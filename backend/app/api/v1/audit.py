import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.all_models import AuditEvent, Invoice
from backend.app.schemas.schemas import AuditEventResponse

router = APIRouter()

@router.get(
    "/invoices/{invoiceId}/audit-events",
    tags=["Audit"],
)
def get_invoice_audit_trail(
    invoiceId: str,
    db: Session = Depends(get_db),
):
    inv = db.query(Invoice).filter(Invoice.id == invoiceId).first()
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": f"Invoice '{invoiceId}' not found."}},
        )

    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.invoice_id == invoiceId)
        .order_by(AuditEvent.occurred_at.asc())
        .all()
    )

    items = []
    for ev in events:
        source_refs = []
        try:
            source_refs = json.loads(ev.source_refs_json or "[]")
        except Exception:
            pass

        items.append({
            "event_id": ev.id,
            "occurred_at": ev.occurred_at,
            "actor_id": ev.actor_id,
            "actor_type": ev.actor_type,
            "action": ev.action,
            "entity_type": ev.entity_type,
            "entity_id": ev.entity_id,
            "before_state": ev.before_state,
            "after_state": ev.after_state,
            "reason": ev.reason,
            "source_refs": source_refs,
            "request_id": ev.request_id,
        })

    return {"items": items}


@router.get(
    "/audit-events",
    tags=["Audit"],
)
def get_global_audit_trail(
    limit: int = 100,
    action: str = None,
    db: Session = Depends(get_db),
):
    query = db.query(AuditEvent)
    if action:
        query = query.filter(AuditEvent.action == action)
    events = query.order_by(AuditEvent.occurred_at.desc()).limit(limit).all()

    items = []
    for ev in events:
        source_refs = []
        try:
            source_refs = json.loads(ev.source_refs_json or "[]")
        except Exception:
            pass

        items.append({
            "event_id": ev.id,
            "invoice_id": ev.invoice_id,
            "occurred_at": ev.occurred_at,
            "actor_id": ev.actor_id,
            "actor_type": ev.actor_type,
            "action": ev.action,
            "entity_type": ev.entity_type,
            "entity_id": ev.entity_id,
            "before_state": ev.before_state,
            "after_state": ev.after_state,
            "reason": ev.reason,
            "source_refs": source_refs,
            "request_id": ev.request_id,
        })

    return {"items": items}


