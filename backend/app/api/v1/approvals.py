from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.auth import get_current_actor, Actor
from backend.app.schemas.schemas import ApprovalDecision, ApprovalResponse
from backend.app.services.approval_service import process_approval_decision

router = APIRouter()

@router.post(
    "/invoices/{invoiceId}/approvals",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Approvals"],
)
def submit_approval_decision(
    invoiceId: str,
    decision_body: ApprovalDecision,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
    actor: Actor = Depends(get_current_actor),
    db: Session = Depends(get_db),
):
    # Strict server-side enforcement:
    # If an agent or ap_clerk attempts approval, return 403 Forbidden immediately
    if actor.role in ["invoice_intake_agent", "invoice_match_agent", "ap_clerk", "procurement_owner"]:
        from backend.app.services.audit_service import log_audit_event
        from backend.app.services.approval_service import hash_idempotency_key
        log_audit_event(
            db=db,
            actor_id=actor.id,
            actor_type=actor.type,
            action="APPROVAL_DENIED",
            entity_type="Invoice",
            entity_id=invoiceId,
            invoice_id=invoiceId,
            reason=f"Actor role '{actor.role}' is forbidden from making financial approval decisions.",
            request_id=x_request_id,
            idempotency_key_hash=hash_idempotency_key(idempotency_key),
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN_ROLE",
                    "message": f"Actor role '{actor.role}' cannot approve invoices. Only human 'finance_approver' or 'ap_admin' can make approval decisions.",
                }
            },
        )

    approval, is_duplicate = process_approval_decision(
        db=db,
        invoice_id=invoiceId,
        decision=decision_body.decision,
        comment=decision_body.comment,
        match_run_id=decision_body.match_run_id,
        approver_id=actor.id,
        approver_role=actor.role,
        idempotency_key=idempotency_key,
        expected_invoice_version=decision_body.expected_invoice_version,
        request_id=x_request_id,
    )

    return ApprovalResponse(
        approval_id=approval.id,
        invoice_id=approval.invoice_id,
        decision=approval.decision,
        approver_id=approval.approver_id,
        created_at=approval.created_at,
    )

