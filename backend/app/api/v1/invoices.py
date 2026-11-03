import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Header, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.database import get_db
from backend.app.auth import require_roles, Actor, get_current_actor
from backend.app.models.all_models import (
    Invoice,
    InvoiceLine,
    Document,
    MatchRun,
    ExceptionRecord,
    Approval,
    PaymentReadyRecord,
    Vendor,
    gen_uuid,
    utcnow_iso,
)
from backend.app.schemas.schemas import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceDetailResponse,
    DocumentResponse,
    MatchRunResponse,
    ExceptionResponse,
    ApprovalResponse,
    PaymentReadyRecordResponse,
)
from backend.app.services.matching_engine import normalize_invoice_number, run_three_way_match
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.get("/invoices", response_model=InvoiceListResponse, tags=["Invoices"])
def list_invoices(
    status_filter: Optional[str] = Query(None, alias="status"),
    q: Optional[str] = Query(None),
    limit: int = Query(25, ge=1, le=100),
    cursor: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Invoice)

    if status_filter:
        query = query.filter(Invoice.status == status_filter)

    if q:
        search_pattern = f"%{q}%".lower()
        query = query.filter(
            or_(
                Invoice.invoice_number.ilike(search_pattern),
                Invoice.id.ilike(search_pattern),
                Invoice.vendor_id.ilike(search_pattern),
                Invoice.purchase_order_id.ilike(search_pattern),
            )
        )

    query = query.order_by(Invoice.created_at.desc())
    invoices = query.limit(limit).all()

    items = [
        InvoiceResponse(
            invoice_id=inv.id,
            status=inv.status,
            version=inv.version,
            invoice_number=inv.invoice_number,
            vendor_id=inv.vendor_id,
            invoice_date=inv.invoice_date,
            currency=inv.currency,
            invoice_total=inv.invoice_total,
            po_id=inv.purchase_order_id,
        )
        for inv in invoices
    ]

    return InvoiceListResponse(items=items, next_cursor=None)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED, tags=["Invoices"])
def create_invoice(
    payload: InvoiceCreate,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    actor: Actor = Depends(require_roles(["ap_clerk", "ap_admin"])),
    db: Session = Depends(get_db),
):
    norm_num = normalize_invoice_number(payload.invoice_number)

    # Check duplicate
    existing_dup = db.query(Invoice).filter(
        Invoice.vendor_id == payload.vendor_id,
        Invoice.normalized_invoice_number == norm_num,
    ).first()

    inv_id = f"INV-{utcnow_iso()[:10].replace('-', '')}-{gen_uuid()[:4].upper()}"

    initial_status = "duplicate_blocked" if existing_dup else "draft"

    invoice = Invoice(
        id=inv_id,
        vendor_id=payload.vendor_id,
        invoice_number=payload.invoice_number,
        normalized_invoice_number=norm_num,
        invoice_date=payload.invoice_date,
        purchase_order_id=payload.po_id,
        currency=payload.currency,
        subtotal=payload.subtotal,
        tax_total=payload.tax_total,
        invoice_total=payload.invoice_total,
        status=initial_status,
        version=1,
        created_by=actor.id,
        created_at=utcnow_iso(),
        updated_at=utcnow_iso(),
    )
    db.add(invoice)
    db.flush()

    if payload.lines:
        for idx, line in enumerate(payload.lines):
            il = InvoiceLine(
                id=gen_uuid(),
                invoice_id=invoice.id,
                line_number=idx + 1,
                sku=line.sku,
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                net_amount=line.net_amount or str(round(float(line.quantity) * float(line.unit_price), 2)),
                tax_rate=line.tax_rate,
                tax_amount=line.tax_amount,
                gross_amount=line.gross_amount,
                source_page=line.source_page,
                source_excerpt=line.source_excerpt,
                confidence=line.confidence or "1.0",
            )
            db.add(il)
        db.flush()

    log_audit_event(
        db=db,
        actor_id=actor.id,
        actor_type=actor.type,
        action="INVOICE_CREATED",
        entity_type="Invoice",
        entity_id=invoice.id,
        invoice_id=invoice.id,
        after_state=invoice.status,
        reason="Invoice case created by AP Clerk.",
        source_refs=[f"invoice/{invoice.id}"],
    )

    db.commit()
    db.refresh(invoice)

    return InvoiceResponse(
        invoice_id=invoice.id,
        status=invoice.status,
        version=invoice.version,
        invoice_number=invoice.invoice_number,
        vendor_id=invoice.vendor_id,
        invoice_date=invoice.invoice_date,
        currency=invoice.currency,
        invoice_total=invoice.invoice_total,
        po_id=invoice.purchase_order_id,
    )


@router.get("/invoices/{invoiceId}", response_model=InvoiceDetailResponse, tags=["Invoices"])
def get_invoice(
    invoiceId: str,
    db: Session = Depends(get_db),
):
    inv = db.query(Invoice).filter(Invoice.id == invoiceId).first()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Invoice '{invoiceId}' not found."}},
        )

    vendor = db.query(Vendor).filter(Vendor.id == inv.vendor_id).first()
    vendor_name = vendor.display_name if vendor else inv.vendor_id

    # Latest match run
    latest_run = (
        db.query(MatchRun)
        .filter(MatchRun.invoice_id == inv.id)
        .order_by(MatchRun.created_at.desc())
        .first()
    )

    latest_run_resp = None
    if latest_run:
        checks_data = json.loads(latest_run.checks_json)
        latest_run_resp = MatchRunResponse(
            match_run_id=latest_run.id,
            invoice_id=latest_run.invoice_id,
            overall_status=latest_run.overall_status,
            invoice_version=latest_run.invoice_version,
            po_version=latest_run.po_version,
            grn_version_fingerprint=latest_run.grn_version_fingerprint,
            policy_version=latest_run.policy_version,
            checks=checks_data,
            executed_by=latest_run.executed_by,
            created_at=latest_run.created_at,
        )

    # Open exceptions
    open_exceptions = (
        db.query(ExceptionRecord)
        .filter(ExceptionRecord.invoice_id == inv.id, ExceptionRecord.status == "open")
        .all()
    )
    open_exc_resp = [
        ExceptionResponse(
            exception_id=e.id,
            invoice_id=e.invoice_id,
            match_run_id=e.match_run_id,
            code=e.code,
            severity=e.severity,
            status=e.status,
            owner_role=e.owner_role,
            description=e.description,
            expected_value=e.expected_value,
            actual_value=e.actual_value,
            source_refs=json.loads(e.source_refs_json or "[]"),
            created_at=e.created_at,
            resolved_at=e.resolved_at,
            resolved_by=e.resolved_by,
        )
        for e in open_exceptions
    ]

    # Documents
    docs = db.query(Document).filter(Document.invoice_id == inv.id).all()
    docs_resp = [
        DocumentResponse(
            document_id=d.id,
            invoice_id=d.invoice_id,
            filename=d.original_filename,
            mime_type=d.mime_type,
            size_bytes=d.size_bytes,
            sha256=d.sha256,
            document_type=d.document_type,
            extraction_status="extracted",
            created_at=d.created_at,
        )
        for d in docs
    ]

    # Approvals
    approvals = db.query(Approval).filter(Approval.invoice_id == inv.id).all()
    approvals_resp = [
        ApprovalResponse(
            approval_id=a.id,
            invoice_id=a.invoice_id,
            decision=a.decision,
            approver_id=a.approver_id,
            created_at=a.created_at,
        )
        for a in approvals
    ]

    # Payment ready record
    payment_ready = db.query(PaymentReadyRecord).filter(PaymentReadyRecord.invoice_id == inv.id).first()
    payment_ready_resp = None
    if payment_ready:
        payment_ready_resp = PaymentReadyRecordResponse(
            payment_ready_record_id=payment_ready.id,
            invoice_id=payment_ready.invoice_id,
            approval_id=payment_ready.approval_id,
            approved_amount=payment_ready.approved_amount,
            currency=payment_ready.currency,
            status=payment_ready.status,
            created_at=payment_ready.created_at,
            payment_executed=False,
        )

    # Lines
    lines_data = [
        {
            "line_number": l.line_number,
            "sku": l.sku,
            "description": l.description,
            "quantity": l.quantity,
            "unit_price": l.unit_price,
            "net_amount": l.net_amount,
            "tax_rate": l.tax_rate,
            "tax_amount": l.tax_amount,
            "gross_amount": l.gross_amount,
            "source_page": l.source_page,
            "source_excerpt": l.source_excerpt,
            "confidence": l.confidence,
        }
        for l in inv.lines
    ]

    return InvoiceDetailResponse(
        invoice_id=inv.id,
        vendor_id=inv.vendor_id,
        vendor_name=vendor_name,
        invoice_number=inv.invoice_number,
        normalized_invoice_number=inv.normalized_invoice_number,
        invoice_date=inv.invoice_date,
        po_id=inv.purchase_order_id,
        currency=inv.currency,
        subtotal=inv.subtotal,
        tax_total=inv.tax_total,
        invoice_total=inv.invoice_total,
        status=inv.status,
        version=inv.version,
        created_by=inv.created_by,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        lines=lines_data,
        documents=docs_resp,
        latest_match_run=latest_run_resp,
        open_exceptions=open_exc_resp,
        approvals=approvals_resp,
        payment_ready_record=payment_ready_resp,
    )

