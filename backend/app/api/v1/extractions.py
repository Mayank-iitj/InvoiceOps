from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.auth import require_roles, Actor
from backend.app.schemas.schemas import (
    ExtractionProposal,
    ExtractionConfirmation,
    ExtractionResponse,
)
from backend.app.services.extraction_service import (
    create_extraction_proposal,
    confirm_extraction,
)
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.post(
    "/invoices/{invoiceId}/extractions",
    response_model=ExtractionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Extraction"],
)
def submit_extraction_proposal(
    invoiceId: str,
    proposal: ExtractionProposal,
    actor: Actor = Depends(require_roles(["invoice_intake_agent", "ap_clerk", "ap_admin"])),
    db: Session = Depends(get_db),
):
    try:
        fields_data = [f.model_dump() for f in proposal.fields]
        lines_data = [l.model_dump() for l in proposal.lines]

        extraction = create_extraction_proposal(
            db=db,
            invoice_id=invoiceId,
            extractor_actor_id=actor.id,
            document_id=proposal.document_id,
            fields=fields_data,
            lines=lines_data,
        )

        log_audit_event(
            db=db,
            actor_id=actor.id,
            actor_type=actor.type,
            action="EXTRACTION_PROPOSED",
            entity_type="Extraction",
            entity_id=extraction.id,
            invoice_id=invoiceId,
            after_state=extraction.status,
            reason=f"Extraction proposal submitted with {len(fields_data)} fields and {len(lines_data)} line items.",
            source_refs=[f"document/{proposal.document_id}", f"extraction/{extraction.id}"],
        )

        db.commit()

        requires_review = extraction.status == "needs_review"
        return ExtractionResponse(
            extraction_id=extraction.id,
            invoice_id=invoiceId,
            status=extraction.status,
            requires_human_review=requires_review,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )


@router.post(
    "/invoices/{invoiceId}/extractions/{extractionId}/confirm",
    response_model=ExtractionResponse,
    tags=["Extraction"],
)
def confirm_extraction_handler(
    invoiceId: str,
    extractionId: str,
    confirmation: ExtractionConfirmation,
    actor: Actor = Depends(require_roles(["ap_clerk", "ap_admin"])),
    db: Session = Depends(get_db),
):
    try:
        extraction = confirm_extraction(
            db=db,
            invoice_id=invoiceId,
            extraction_id=extractionId,
            confirmed_by=actor.id,
            confirmed=confirmation.confirmed,
            comment=confirmation.comment,
            corrected_fields=confirmation.corrected_fields,
        )

        log_audit_event(
            db=db,
            actor_id=actor.id,
            actor_type="human",
            action="EXTRACTION_CONFIRMED" if confirmation.confirmed else "EXTRACTION_REJECTED",
            entity_type="Extraction",
            entity_id=extraction.id,
            invoice_id=invoiceId,
            after_state=extraction.status,
            reason=confirmation.comment,
            source_refs=[f"extraction/{extraction.id}"],
        )

        db.commit()

        return ExtractionResponse(
            extraction_id=extraction.id,
            invoice_id=invoiceId,
            status=extraction.status,
            requires_human_review=False,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )

