from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.auth import require_roles, Actor
from backend.app.models.all_models import PaymentReadyRecord, Invoice
from backend.app.schemas.schemas import PaymentReadyCreate, PaymentReadyRecordResponse
from backend.app.services.approval_service import create_payment_ready_record

router = APIRouter()

@router.post(
    "/invoices/{invoiceId}/payment-ready-records",
    response_model=PaymentReadyRecordResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["PaymentReady"],
)
def create_payment_ready_handler(
    invoiceId: str,
    payload: PaymentReadyCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    actor: Actor = Depends(require_roles(["finance_approver", "ap_admin"])),
    db: Session = Depends(get_db),
):
    record = create_payment_ready_record(
        db=db,
        invoice_id=invoiceId,
        approval_id=payload.approval_id,
        actor_id=actor.id,
        actor_role=actor.role,
        idempotency_key=idempotency_key,
        request_id=x_request_id,
    )

    return PaymentReadyRecordResponse(
        payment_ready_record_id=record.id,
        invoice_id=record.invoice_id,
        approval_id=record.approval_id,
        approved_amount=record.approved_amount,
        currency=record.currency,
        status=record.status,
        created_at=record.created_at,
        payment_executed=False,
    )


@router.get(
    "/payment-ready-records",
    tags=["PaymentReady"],
)
def list_payment_ready_records(
    db: Session = Depends(get_db),
):
    records = db.query(PaymentReadyRecord).order_by(PaymentReadyRecord.created_at.desc()).all()
    items = []
    for r in records:
        inv = db.query(Invoice).filter(Invoice.id == r.invoice_id).first()
        items.append({
            "payment_ready_record_id": r.id,
            "invoice_id": r.invoice_id,
            "invoice_number": inv.invoice_number if inv else "Unknown",
            "vendor_id": inv.vendor_id if inv else "Unknown",
            "approval_id": r.approval_id,
            "approved_amount": r.approved_amount,
            "currency": r.currency,
            "status": r.status,
            "created_at": r.created_at,
            "created_by": r.created_by,
            "payment_executed": False,
        })
    return {"items": items}

