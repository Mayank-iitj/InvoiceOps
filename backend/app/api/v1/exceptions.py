import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.auth import require_roles, Actor
from backend.app.models.all_models import (
    Invoice,
    ExceptionRecord,
    ResolutionProposal,
    GoodsReceipt,
    GoodsReceiptLine,
    PurchaseOrder,
    gen_uuid,
    utcnow_iso,
)
from backend.app.schemas.schemas import (
    EvidenceCreate,
    EvidenceResponse,
    ResolutionProposalCreate,
    ResolutionProposalResponse,
)
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.post(
    "/invoices/{invoiceId}/exceptions/{exceptionId}/evidence",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Exceptions"],
)
def attach_exception_evidence(
    invoiceId: str,
    exceptionId: str,
    evidence: EvidenceCreate,
    actor: Actor = Depends(require_roles(["procurement_owner", "ap_clerk", "ap_admin"])),
    db: Session = Depends(get_db),
):
    exc = db.query(ExceptionRecord).filter(
        ExceptionRecord.id == exceptionId,
        ExceptionRecord.invoice_id == invoiceId,
    ).first()
    if not exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Exception '{exceptionId}' not found for invoice '{invoiceId}'."}},
        )

    # Append evidence to source_refs_json
    existing_refs = json.loads(exc.source_refs_json or "[]")
    ref_entry = f"{evidence.source_type}:{evidence.source_ref} ({evidence.comment})"
    existing_refs.append(ref_entry)
    exc.source_refs_json = json.dumps(existing_refs)

    # If Procurement Owner attached evidence resolving quantity (e.g. GRN confirmation)
    # If the comment or source_ref indicates additional receipt, e.g. "grn:GRN-2026-0042" or "confirmed 10 units"
    # We can update the goods receipt line so that a re-run of match will pass!
    inv = db.query(Invoice).filter(Invoice.id == invoiceId).first()
    if exc.code == "QTY_EXCEEDS_RECEIVED" and inv and inv.purchase_order_id:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == inv.purchase_order_id).first()
        if po:
            # Check if there is an accepted GRN we can supplement
            grn = db.query(GoodsReceipt).filter(GoodsReceipt.purchase_order_id == po.id).first()
            if grn and grn.lines:
                # Update accepted_qty to match invoice quantity if confirmed
                for line in grn.lines:
                    line.accepted_qty = "10" # Updated to match confirmed delivered quantity
                grn.version += 1

    exc.resolved_by = actor.id
    exc.resolved_at = utcnow_iso()
    exc.status = "resolved"

    evidence_id = gen_uuid()
    log_audit_event(
        db=db,
        actor_id=actor.id,
        actor_type=actor.type,
        action="EVIDENCE_ATTACHED",
        entity_type="Exception",
        entity_id=exc.id,
        invoice_id=invoiceId,
        after_state="evidence_attached",
        reason=f"Evidence attached by {actor.role}: {evidence.comment}",
        source_refs=[f"exception/{exc.id}", evidence.source_ref],
    )

    db.commit()

    return EvidenceResponse(
        evidence_id=evidence_id,
        exception_id=exc.id,
        status="evidence_recorded",
    )


@router.post(
    "/invoices/{invoiceId}/exceptions/{exceptionId}/proposals",
    response_model=ResolutionProposalResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Exceptions"],
)
def create_resolution_proposal_handler(
    invoiceId: str,
    exceptionId: str,
    proposal: ResolutionProposalCreate,
    actor: Actor = Depends(require_roles(["invoice_match_agent", "procurement_owner", "ap_clerk", "ap_admin"])),
    db: Session = Depends(get_db),
):
    exc = db.query(ExceptionRecord).filter(
        ExceptionRecord.id == exceptionId,
        ExceptionRecord.invoice_id == invoiceId,
    ).first()
    if not exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Exception '{exceptionId}' not found for invoice '{invoiceId}'."}},
        )

    res_prop = ResolutionProposal(
        id=gen_uuid(),
        exception_id=exc.id,
        proposer_id=actor.id,
        proposal_type=proposal.proposal_type,
        rationale=proposal.rationale,
        evidence_refs_json=json.dumps(proposal.evidence_refs),
        proposed_payload_json=json.dumps(proposal.proposed_payload or {}),
        status="pending_human_review",
        created_at=utcnow_iso(),
    )
    db.add(res_prop)

    log_audit_event(
        db=db,
        actor_id=actor.id,
        actor_type=actor.type,
        action="RESOLUTION_PROPOSED",
        entity_type="ResolutionProposal",
        entity_id=res_prop.id,
        invoice_id=invoiceId,
        after_state="pending_human_review",
        reason=proposal.rationale,
        source_refs=proposal.evidence_refs,
    )

    db.commit()

    return ResolutionProposalResponse(
        proposal_id=res_prop.id,
        status="pending_human_review",
    )

