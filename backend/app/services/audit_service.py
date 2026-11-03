import json
from typing import Optional, List, Any
from sqlalchemy.orm import Session
from backend.app.models.all_models import AuditEvent, gen_uuid, utcnow_iso

def log_audit_event(
    db: Session,
    actor_id: str,
    actor_type: str,
    action: str,
    entity_type: str,
    entity_id: str,
    invoice_id: Optional[str] = None,
    before_state: Optional[str] = None,
    after_state: Optional[str] = None,
    reason: Optional[str] = None,
    source_refs: Optional[List[str]] = None,
    request_id: Optional[str] = None,
    idempotency_key_hash: Optional[str] = None,
) -> AuditEvent:
    event = AuditEvent(
        id=gen_uuid(),
        occurred_at=utcnow_iso(),
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        invoice_id=invoice_id,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
        reason=reason,
        source_refs_json=json.dumps(source_refs or []),
        request_id=request_id,
        idempotency_key_hash=idempotency_key_hash,
    )
    db.add(event)
    return event

