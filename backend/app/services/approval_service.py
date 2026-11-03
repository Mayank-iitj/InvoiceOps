import hashlib
import json
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.all_models import (
    Invoice,
    Approval,
    MatchRun,
    ExceptionRecord,
    PaymentReadyRecord,
    IdempotencyRecord,
    gen_uuid,
    utcnow_iso,
)
from backend.app.services.audit_service import log_audit_event

def hash_idempotency_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()

def process_approval_decision(
    db: Session,
    invoice_id: str,
    decision: str, # "approved" or "rejected"
    comment: str,
    match_run_id: str,
    approver_id: str,
    approver_role: str,
    idempotency_key: str,
    expected_invoice_version: Optional[int] = None,
    request_id: Optional[str] = None,
) -> Tuple[Approval, bool]:
    """
    Executes atomic, transactional approval or rejection.
    Returns (Approval, is_duplicate_request)
    """
    key_hash = hash_idempotency_key(idempotency_key)

    # 1. Check idempotency: if approval with this key exists, return it
    existing_approval = db.query(Approval).filter(Approval.idempotency_key_hash == key_hash).first()
    if existing_approval:
        if existing_approval.invoice_id != invoice_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"code": "IDEMPOTENCY_CONFLICT", "message": "Idempotency key was used for a different invoice."}}
            )
        return existing_approval, True

    # 2. Strict Role Check: ONLY human finance_approver can approve or reject
    if approver_role != "finance_approver" and approver_role != "ap_admin":
        # Log unauthorized attempt in audit table
        log_audit_event(
            db=db,
            actor_id=approver_id,
            actor_type="agent" if "agent" in approver_role else "human",
            action="APPROVAL_DENIED",
            entity_type="Invoice",
            entity_id=invoice_id,
            invoice_id=invoice_id,
            reason=f"Forbidden role '{approver_role}' attempted financial decision.",
            request_id=request_id,
            idempotency_key_hash=key_hash,
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "ROLE_FORBIDDEN", "message": f"Actor role '{approver_role}' cannot approve invoices. Human finance_approver required."}}
        )

    # 3. Read invoice
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "INVOICE_NOT_FOUND", "message": f"Invoice {invoice_id} not found."}}
        )

    # 4. Version check if specified
    if expected_invoice_version is not None and invoice.version != expected_invoice_version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "STALE_VERSION", "message": f"Invoice version {invoice.version} differs from expected version {expected_invoice_version}."}}
        )

    # 5. Validate Match Run
    match_run = db.query(MatchRun).filter(MatchRun.id == match_run_id).first()
    if not match_run or match_run.invoice_id != invoice_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_MATCH_RUN", "message": f"Match run {match_run_id} is invalid for invoice {invoice_id}."}}
        )

    # Verify that match run is not stale
    if match_run.invoice_version != invoice.version:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "STALE_MATCH_RUN", "message": f"Match run version {match_run.invoice_version} is stale. Current invoice version is {invoice.version}. Re-run matching first."}}
        )

    # If approving: verify that match run is PASS and no blocking exceptions exist
    if decision == "approved":
        if match_run.overall_status != "PASS":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"code": "MATCH_NOT_PASSED", "message": f"Cannot approve invoice: latest match run status is '{match_run.overall_status}', not 'PASS'."}}
            )

        open_blocking_exceptions = db.query(ExceptionRecord).filter(
            ExceptionRecord.invoice_id == invoice_id,
            ExceptionRecord.status == "open",
            ExceptionRecord.severity == "blocking",
        ).all()

        if open_blocking_exceptions:
            details = [{"code": e.code, "description": e.description} for e in open_blocking_exceptions]
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"code": "APPROVAL_BLOCKED", "message": "Invoice has unresolved blocking exceptions.", "details": details}}
            )

    before_state = invoice.status
    after_state = "approved" if decision == "approved" else "rejected"

    approval = Approval(
        id=gen_uuid(),
        invoice_id=invoice_id,
        match_run_id=match_run_id,
        decision=decision,
        comment=comment,
        approver_id=approver_id,
        approver_role=approver_role,
        idempotency_key_hash=key_hash,
        created_at=utcnow_iso(),
    )
    db.add(approval)

    invoice.status = after_state
    invoice.version += 1
    invoice.updated_at = utcnow_iso()

    log_audit_event(
        db=db,
        actor_id=approver_id,
        actor_type="human",
        action=f"INVOICE_{decision.upper()}",
        entity_type="Invoice",
        entity_id=invoice_id,
        invoice_id=invoice_id,
        before_state=before_state,
        after_state=after_state,
        reason=comment,
        source_refs=[f"match_run/{match_run_id}", f"approval/{approval.id}"],
        request_id=request_id,
        idempotency_key_hash=key_hash,
    )

    db.commit()
    db.refresh(approval)
    return approval, False


def create_payment_ready_record(
    db: Session,
    invoice_id: str,
    approval_id: str,
    actor_id: str,
    actor_role: str,
    idempotency_key: str,
    request_id: Optional[str] = None,
) -> PaymentReadyRecord:
    key_hash = hash_idempotency_key(idempotency_key)

    existing_record = db.query(PaymentReadyRecord).filter(
        PaymentReadyRecord.invoice_id == invoice_id
    ).first()
    if existing_record:
        return existing_record

    # Strict role check
    if actor_role != "finance_approver" and actor_role != "ap_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "ROLE_FORBIDDEN", "message": f"Actor role '{actor_role}' cannot create payment-ready record."}}
        )

    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "INVOICE_NOT_FOUND", "message": f"Invoice {invoice_id} not found."}}
        )

    approval = db.query(Approval).filter(Approval.id == approval_id, Approval.invoice_id == invoice_id).first()
    if not approval or approval.decision != "approved":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "INVOICE_NOT_APPROVED", "message": "Cannot create payment-ready record for an unapproved invoice."}}
        )

    before_state = invoice.status
    record = PaymentReadyRecord(
        id=gen_uuid(),
        invoice_id=invoice_id,
        approval_id=approval_id,
        approved_amount=invoice.invoice_total,
        currency=invoice.currency,
        status="ready_for_downstream_payment",
        created_at=utcnow_iso(),
        created_by=actor_id,
    )
    db.add(record)

    invoice.status = "payment_ready"
    invoice.version += 1
    invoice.updated_at = utcnow_iso()

    log_audit_event(
        db=db,
        actor_id=actor_id,
        actor_type="human",
        action="PAYMENT_READY_RECORD_CREATED",
        entity_type="PaymentReadyRecord",
        entity_id=record.id,
        invoice_id=invoice_id,
        before_state=before_state,
        after_state="payment_ready",
        reason="Invoice approved; downstream payment-ready record generated without initiating payment.",
        source_refs=[f"approval/{approval.id}"],
        request_id=request_id,
        idempotency_key_hash=key_hash,
    )

    db.commit()
    db.refresh(record)
    return record

