import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.config import settings
from backend.app.auth import require_roles, Actor
from backend.app.models.all_models import (
    Invoice,
    Document,
    gen_uuid,
    utcnow_iso,
)
from backend.app.schemas.schemas import DocumentResponse
from backend.app.services.extraction_service import compute_sha256, extract_text_from_pdf
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

MAX_BYTES = settings.MAX_UPLOAD_MB * 1024 * 1024

@router.post(
    "/invoices/{invoiceId}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"],
)
async def upload_document(
    invoiceId: str,
    file: UploadFile = File(...),
    document_type: str = Form("supplier_invoice"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    actor: Actor = Depends(require_roles(["ap_clerk", "ap_admin", "invoice_intake_agent"])),
    db: Session = Depends(get_db),
):
    inv = db.query(Invoice).filter(Invoice.id == invoiceId).first()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Invoice '{invoiceId}' not found."}},
        )

    content = await file.read()
    size = len(content)

    # 1. Size check
    if size > MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail={
                "error": {
                    "code": "PAYLOAD_TOO_LARGE",
                    "message": f"Document exceeds max allowed size of {settings.MAX_UPLOAD_MB} MB.",
                }
            },
        )

    # 2. SHA-256 Checksum
    sha256_hash = compute_sha256(content)

    # Check document checksum duplicate across other invoices
    doc_dup = (
        db.query(Document)
        .filter(Document.sha256 == sha256_hash, Document.invoice_id != inv.id)
        .first()
    )
    if doc_dup:
        inv.status = "duplicate_blocked"

    # Save to disk
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    doc_id = gen_uuid()
    safe_filename = f"{doc_id}_{file.filename}"
    storage_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(storage_path, "wb") as f:
        f.write(content)

    doc = Document(
        id=doc_id,
        invoice_id=inv.id,
        original_filename=file.filename or "uploaded_document",
        storage_path=storage_path,
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=size,
        sha256=sha256_hash,
        document_type=document_type,
        created_by=actor.id,
        created_at=utcnow_iso(),
    )
    db.add(doc)

    if inv.status == "draft":
        inv.status = "received"
    inv.version += 1
    inv.updated_at = utcnow_iso()

    log_audit_event(
        db=db,
        actor_id=actor.id,
        actor_type=actor.type,
        action="DOCUMENT_UPLOADED",
        entity_type="Document",
        entity_id=doc.id,
        invoice_id=inv.id,
        after_state=inv.status,
        reason=f"Attached {document_type} ('{file.filename}'). Checksum: {sha256_hash[:12]}...",
        source_refs=[f"document/{doc.id}"],
    )

    db.commit()
    db.refresh(doc)

    return DocumentResponse(
        document_id=doc.id,
        invoice_id=doc.invoice_id,
        filename=doc.original_filename,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
        sha256=doc.sha256,
        document_type=doc.document_type,
        extraction_status="ready_for_extraction",
        created_at=doc.created_at,
    )


@router.get("/documents/{documentId}", tags=["Documents"])
def get_document(
    documentId: str,
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == documentId).first()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Document '{documentId}' not found."}},
        )

    # Extract text preview
    extracted_text = ""
    if os.path.exists(doc.storage_path):
        extracted_text = extract_text_from_pdf(doc.storage_path)

    return {
        "document_id": doc.id,
        "invoice_id": doc.invoice_id,
        "filename": doc.original_filename,
        "mime_type": doc.mime_type,
        "size_bytes": doc.size_bytes,
        "sha256": doc.sha256,
        "document_type": doc.document_type,
        "created_at": doc.created_at,
        "extracted_text_preview": extracted_text[:1000] if extracted_text else "",
        "full_text": extracted_text,
    }
