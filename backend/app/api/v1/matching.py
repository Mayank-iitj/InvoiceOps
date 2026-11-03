import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.auth import require_roles, Actor
from backend.app.models.all_models import MatchRun, Invoice
from backend.app.schemas.schemas import MatchRunResponse, MatchCheck
from backend.app.services.matching_engine import run_three_way_match
from backend.app.services.audit_service import log_audit_event

router = APIRouter()

@router.post(
    "/invoices/{invoiceId}/match-runs",
    response_model=MatchRunResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Matching"],
)
def execute_match_run(
    invoiceId: str,
    body: Optional[Dict[str, Any]] = Body(default=None),
    actor: Actor = Depends(require_roles(["invoice_match_agent", "ap_clerk", "ap_admin"])),
    db: Session = Depends(get_db),
):
    inv = db.query(Invoice).filter(Invoice.id == invoiceId).first()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Invoice '{invoiceId}' not found."}},
        )

    policy_ver = body.get("policy_version") if body else None

    try:
        match_run, exceptions = run_three_way_match(
            db=db,
            invoice_id=invoiceId,
            executed_by=actor.id,
            policy_version=policy_ver,
        )

        checks_data = json.loads(match_run.checks_json)
        checks_models = [MatchCheck(**c) for c in checks_data]

        log_audit_event(
            db=db,
            actor_id=actor.id,
            actor_type=actor.type,
            action="MATCH_RUN_EXECUTED",
            entity_type="MatchRun",
            entity_id=match_run.id,
            invoice_id=invoiceId,
            after_state=match_run.overall_status,
            reason=f"Three-way match completed with outcome: {match_run.overall_status}. {len(exceptions)} open exception(s).",
            source_refs=[f"match_run/{match_run.id}"],
        )

        db.commit()
        db.refresh(match_run)

        return MatchRunResponse(
            match_run_id=match_run.id,
            invoice_id=match_run.invoice_id,
            overall_status=match_run.overall_status,
            invoice_version=match_run.invoice_version,
            po_version=match_run.po_version,
            grn_version_fingerprint=match_run.grn_version_fingerprint,
            policy_version=match_run.policy_version,
            checks=checks_models,
            executed_by=match_run.executed_by,
            created_at=match_run.created_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": str(e)}},
        )


@router.get(
    "/invoices/{invoiceId}/match-runs/latest",
    response_model=MatchRunResponse,
    tags=["Matching"],
)
def get_latest_match_run(
    invoiceId: str,
    db: Session = Depends(get_db),
):
    inv = db.query(Invoice).filter(Invoice.id == invoiceId).first()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Invoice '{invoiceId}' not found."}},
        )

    latest_run = (
        db.query(MatchRun)
        .filter(MatchRun.invoice_id == invoiceId)
        .order_by(MatchRun.created_at.desc())
        .first()
    )
    if not latest_run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"No match runs found for invoice '{invoiceId}'."}},
        )

    checks_data = json.loads(latest_run.checks_json)
    checks_models = [MatchCheck(**c) for c in checks_data]

    return MatchRunResponse(
        match_run_id=latest_run.id,
        invoice_id=latest_run.invoice_id,
        overall_status=latest_run.overall_status,
        invoice_version=latest_run.invoice_version,
        po_version=latest_run.po_version,
        grn_version_fingerprint=latest_run.grn_version_fingerprint,
        policy_version=latest_run.policy_version,
        checks=checks_models,
        executed_by=latest_run.executed_by,
        created_at=latest_run.created_at,
    )

