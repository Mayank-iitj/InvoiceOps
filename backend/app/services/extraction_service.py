import os
import json
import hashlib
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from backend.app.config import settings
from backend.app.models.all_models import (
    Invoice,
    InvoiceLine,
    Document,
    Extraction,
    gen_uuid,
    utcnow_iso,
)

def compute_sha256(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

def extract_text_from_pdf(file_path: str) -> str:
    """Extracts text from PDF using pymupdf (fitz) or pypdf fallback."""
    text = ""
    try:
        import fitz
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except Exception:
        pass

    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text
    except Exception:
        pass

    # Plain text / fallback
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def create_extraction_proposal(
    db: Session,
    invoice_id: str,
    extractor_actor_id: str,
    document_id: str,
    fields: List[Dict[str, Any]],
    lines: List[Dict[str, Any]],
) -> Extraction:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")

    # Determine if any critical field has confidence below threshold
    requires_human_review = False
    for f in fields:
        conf = float(f.get("confidence", 1.0))
        if conf < settings.EXTRACTION_CONFIDENCE_THRESHOLD:
            requires_human_review = True
            break

    payload = {
        "document_id": document_id,
        "fields": fields,
        "lines": lines,
    }

    # Count existing extractions to determine version
    prev_count = db.query(Extraction).filter(Extraction.invoice_id == invoice_id).count()

    status = "needs_review" if requires_human_review else "proposed"

    extraction = Extraction(
        id=gen_uuid(),
        invoice_id=invoice_id,
        document_id=document_id,
        extractor_actor_id=extractor_actor_id,
        status=status,
        payload_json=json.dumps(payload),
        confidence_summary=f"Requires human review: {requires_human_review}",
        version=prev_count + 1,
        created_at=utcnow_iso(),
    )
    db.add(extraction)

    if requires_human_review:
        invoice.status = "needs_review"
    else:
        invoice.status = "reconciling"
    invoice.version += 1
    invoice.updated_at = utcnow_iso()

    db.flush()
    return extraction

def confirm_extraction(
    db: Session,
    invoice_id: str,
    extraction_id: str,
    confirmed_by: str,
    confirmed: bool,
    comment: str,
    corrected_fields: Optional[Dict[str, Any]] = None,
) -> Extraction:
    extraction = db.query(Extraction).filter(
        Extraction.id == extraction_id,
        Extraction.invoice_id == invoice_id,
    ).first()
    if not extraction:
        raise ValueError(f"Extraction {extraction_id} not found")

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")

    extraction.confirmed_by = confirmed_by
    extraction.confirmed_at = utcnow_iso()
    extraction.status = "confirmed" if confirmed else "rejected"

    # If corrected fields provided, apply to invoice and lines
    if corrected_fields:
        if "invoice_number" in corrected_fields:
            invoice.invoice_number = corrected_fields["invoice_number"]
            from backend.app.services.matching_engine import normalize_invoice_number
            invoice.normalized_invoice_number = normalize_invoice_number(corrected_fields["invoice_number"])
        if "invoice_total" in corrected_fields:
            invoice.invoice_total = str(corrected_fields["invoice_total"])
        if "po_id" in corrected_fields:
            invoice.purchase_order_id = corrected_fields["po_id"]

    invoice.version += 1
    invoice.status = "reconciling"
    invoice.updated_at = utcnow_iso()

    db.flush()
    return extraction

