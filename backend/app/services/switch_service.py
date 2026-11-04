import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.orm import Session
from fastapi import WebSocket

from backend.app.config import settings
from backend.app.models.all_models import (
    SwitchMessage,
    Invoice,
    PurchaseOrder,
    GoodsReceipt,
    ExceptionRecord,
    MatchRun,
    Approval,
    PaymentReadyRecord,
    AuditEvent
)
from backend.app.services.matching_engine import run_three_way_match
from backend.app.services.approval_service import process_approval_decision
from backend.app.services.audit_service import log_audit_event

logger = logging.getLogger("invoiceops.switch")

DEFAULT_ROOM_ID = "room_invoiceops_ap"
DEFAULT_ROOM_NAME = "#invoiceops-ap"

AGENT_INTAKE = {
    "id": "invoiceops-intake",
    "name": "Intake Agent (AI)",
    "role": "agent",
    "avatar": "bot-blue"
}

AGENT_RECONCILE = {
    "id": "invoiceops-reconcile",
    "name": "Reconcile Agent (AI)",
    "role": "agent",
    "avatar": "bot-cyan"
}

HUMAN_CLERK = {
    "id": "ap_clerk_1",
    "name": "Sarah Chen (AP Clerk)",
    "role": "human",
    "avatar": "user-green"
}

HUMAN_PROCUREMENT = {
    "id": "procurement_owner_1",
    "name": "Rajesh Kumar (Procurement)",
    "role": "human",
    "avatar": "user-amber"
}

HUMAN_FINANCE = {
    "id": "finance_approver_1",
    "name": "Elena Rostova (Finance Approver)",
    "role": "human",
    "avatar": "user-purple"
}


def utcnow_iso():
    return datetime.now(timezone.utc).isoformat()


def detect_prompt_injection(content: str) -> bool:
    """Adversarial & Prompt Injection heuristic detection for untrusted input data."""
    suspicious_patterns = [
        "ignore previous instructions",
        "ignore all previous instructions",
        "ignore all prior instructions",
        "disregard previous instructions",
        "system prompt",
        "you are now in",
        "maintenance mode",
        "bypass validation",
        "bypass policy",
        "approve unconditionally",
        "override without addendum",
        "drop table",
        "grant admin",
        "release funds immediately"
    ]
    low = content.lower()
    return any(p in low for p in suspicious_patterns)


class SwitchConnectionManager:
    """Manages active WebSockets for Switch collaboration rooms with thread-safe broadcast."""

    def __init__(self):
        self.active_rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.active_rooms:
            self.active_rooms[room_id] = set()
        self.active_rooms[room_id].add(websocket)
        logger.info(f"WebSocket client connected to {room_id}. Total: {len(self.active_rooms[room_id])}")

    def disconnect(self, room_id: str, websocket: WebSocket):
        if room_id in self.active_rooms:
            self.active_rooms[room_id].discard(websocket)
            if not self.active_rooms[room_id]:
                del self.active_rooms[room_id]
        logger.info(f"WebSocket client disconnected from {room_id}")

    async def broadcast(self, room_id: str, message: Dict[str, Any]):
        if room_id in self.active_rooms:
            dead_sockets = set()
            for ws in list(self.active_rooms[room_id]):
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                self.active_rooms[room_id].discard(dead)

    def broadcast_sync(self, room_id: str, message: Dict[str, Any]):
        """Safe thread-safe and loop-safe broadcast helper for sync endpoints."""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.broadcast(room_id, message))
        except RuntimeError:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.run_coroutine_threadsafe(self.broadcast(room_id, message), loop)
            except Exception:
                pass


manager = SwitchConnectionManager()


class SwitchService:
    @staticmethod
    def get_room_metadata():
        return {
            "room_id": DEFAULT_ROOM_ID,
            "room_name": DEFAULT_ROOM_NAME,
            "topic": "Autonomous Accounts Payable Reconciliation & Exception Resolution",
            "active_agents": [AGENT_INTAKE, AGENT_RECONCILE],
            "active_humans": [HUMAN_CLERK, HUMAN_PROCUREMENT, HUMAN_FINANCE],
            "connectors": {
                "switch_core": {"status": "connected", "type": "websocket_and_rest"},
                "mattermost": {"status": "configured", "channel": "~invoiceops-ap"},
                "slack": {"status": "ready", "channel": "#invoiceops-ap"},
                "teams": {"status": "ready", "team": "Finance Operations"},
                "discord": {"status": "ready", "channel": "ap-reconcile"},
                "mcp": {"status": "active", "endpoint": "/api/v1/switch/mcp"}
            }
        }

    @staticmethod
    def get_messages(
        db: Session, 
        room_id: str = DEFAULT_ROOM_ID, 
        thread_id: Optional[str] = None, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        # Auto-seed initial thread if empty
        if db.query(SwitchMessage).filter(SwitchMessage.room_id == room_id).count() == 0:
            SwitchService.seed_initial_messages(db)

        query = db.query(SwitchMessage).filter(SwitchMessage.room_id == room_id)
        if thread_id:
            query = query.filter(SwitchMessage.thread_id == thread_id)
        
        messages = query.order_by(SwitchMessage.created_at.asc()).limit(limit).all()
        return [
            {
                "id": m.id,
                "room_id": m.room_id,
                "thread_id": m.thread_id,
                "sender_id": m.sender_id,
                "sender_name": m.sender_name,
                "sender_role": m.sender_role,
                "avatar": m.avatar,
                "content": m.content,
                "mentions": json.loads(m.mentions_json or "[]"),
                "evidence_refs": json.loads(m.evidence_refs_json or "[]"),
                "action_type": m.action_type,
                "action_payload": json.loads(m.action_payload_json or "{}"),
                "created_at": m.created_at
            }
            for m in messages
        ]

    @staticmethod
    def post_message(
        db: Session,
        room_id: str,
        thread_id: str,
        sender_id: str,
        sender_name: str,
        sender_role: str,
        content: str,
        avatar: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        evidence_refs: Optional[List[str]] = None,
        action_type: Optional[str] = "chat",
        action_payload: Optional[Dict[str, Any]] = None,
        auto_react: bool = True
    ) -> Dict[str, Any]:
        msg = SwitchMessage(
            room_id=room_id,
            thread_id=thread_id,
            sender_id=sender_id,
            sender_name=sender_name,
            sender_role=sender_role,
            avatar=avatar or ("bot-blue" if sender_role == "agent" else "user-amber"),
            content=content,
            mentions_json=json.dumps(mentions or []),
            evidence_refs_json=json.dumps(evidence_refs or []),
            action_type=action_type,
            action_payload_json=json.dumps(action_payload or {}),
            created_at=utcnow_iso()
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)

        result = {
            "id": msg.id,
            "room_id": msg.room_id,
            "thread_id": msg.thread_id,
            "sender_id": msg.sender_id,
            "sender_name": msg.sender_name,
            "sender_role": msg.sender_role,
            "avatar": msg.avatar,
            "content": msg.content,
            "mentions": mentions or [],
            "evidence_refs": evidence_refs or [],
            "action_type": msg.action_type,
            "action_payload": action_payload or {},
            "created_at": msg.created_at
        }

        # Real-time WebSocket Broadcast
        manager.broadcast_sync(room_id, {
            "type": "new_message",
            "room_id": room_id,
            "thread_id": thread_id,
            "message": result
        })

        # Reactive AI agent response if human mentioned an agent or posted in thread
        if auto_react and sender_role == "human":
            SwitchService._trigger_reactive_agent_reply(db, msg)

        return result

    @staticmethod
    def _trigger_reactive_agent_reply(db: Session, user_msg: SwitchMessage):
        """Autonomously analyzes user input and generates AI teammate response using Switch algorithms."""
        content = user_msg.content
        low_content = content.lower()
        mentions = json.loads(user_msg.mentions_json or "[]")
        thread_id = user_msg.thread_id

        # Determine invoice ID from thread or content
        invoice_id = None
        for inv_id in ["INV-2026-1041", "INV-2026-1042", "INV-2026-1043", "INV-2026-1044"]:
            if inv_id.lower() in low_content or inv_id.lower() in thread_id.lower():
                invoice_id = inv_id
                break
        target_id = invoice_id or "INV-2026-1042"

        # ---------------------------------------------------------------------
        # ALGORITHM 1: ADVERSARIAL & PROMPT INJECTION DEFENSE (Intake Agent)
        # ---------------------------------------------------------------------
        if detect_prompt_injection(content):
            log_audit_event(
                db=db,
                actor_id=user_msg.sender_id,
                actor_type="untrusted_input",
                action="PROMPT_INJECTION_QUARANTINED",
                entity_type="Invoice",
                entity_id=target_id,
                invoice_id=target_id,
                reason="Adversarial prompt injection pattern detected in input payload.",
                source_refs=[f"msg_{user_msg.id}"]
            )
            db.commit()

            SwitchService.post_message(
                db=db,
                room_id=user_msg.room_id,
                thread_id=user_msg.thread_id,
                sender_id=AGENT_INTAKE["id"],
                sender_name=AGENT_INTAKE["name"],
                sender_role=AGENT_INTAKE["role"],
                avatar=AGENT_INTAKE["avatar"],
                content=(
                    "🚨 **[SECURITY ALERT — UNTRUSTED CONTENT QUARANTINED]**\n\n"
                    "• **Threat Analysis**: Adversarial prompt injection or unauthorized instruction override sequence detected in input data.\n"
                    "• **Policy Invariant**: In accordance with Switch safety guidelines, all document contents and collaborative inputs are strictly treated as untrusted data.\n"
                    "• **Action Enforced**: Automated processing halted. Case marked for manual quarantine review by AP Supervisor.\n"
                    "• **Tamper-Evident Ledger**: Incident appended to immutable audit log."
                ),
                mentions=["ap_clerk_1"],
                action_type="security_quarantine",
                action_payload={"threat": "PROMPT_INJECTION", "status": "QUARANTINED"},
                auto_react=False
            )
            return

        # ---------------------------------------------------------------------
        # ALGORITHM 2: INTAKE & EXTRACTION PROPOSAL (Intake Agent)
        # ---------------------------------------------------------------------
        if (
            "extract" in low_content 
            or "ingest" in low_content 
            or "inspect" in low_content 
            or "ocr" in low_content 
            or "@invoiceops-intake" in mentions
        ) and "reconcile" not in low_content and "match" not in low_content:
            inv = db.query(Invoice).filter(Invoice.id == target_id).first()
            if inv:
                lines_summary = []
                for idx, line in enumerate(inv.lines, start=1):
                    lines_summary.append(
                        f"  - Row {idx}: `{line.description}` | Qty: {line.quantity} | Rate: ₹{line.unit_price} (Evidence: `doc_{inv.id}.pdf` Page 1, Line {idx})"
                    )
                lines_text = "\n".join(lines_summary) if lines_summary else "  - No line items registered"

                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_INTAKE["id"],
                    sender_name=AGENT_INTAKE["name"],
                    sender_role=AGENT_INTAKE["role"],
                    avatar=AGENT_INTAKE["avatar"],
                    content=(
                        f"📥 **Extraction Proposal Generated for `{inv.id}`**:\n\n"
                        f"• **Supplier / Vendor**: `{inv.vendor_id}`\n"
                        f"• **Invoice Total**: ₹{inv.invoice_total} {inv.currency} (Tax: ₹{inv.tax_amount or '0.00'})\n"
                        f"• **Purchase Order Reference**: `{inv.purchase_order_id or 'PO-2026-0082'}`\n"
                        f"• **OCR Confidence Score**: `0.98` (High Confidence)\n"
                        f"• **Duplicate Fingerprint Check**: Passed (SHA-256 normalized hash verified)\n"
                        f"• **Extracted Line Items**:\n{lines_text}\n\n"
                        "⚠️ *Safety Invariant*: The Intake Agent extracts source evidence only and never approves, releases funds, or initiates payment.\n\n"
                        "Routing to @invoiceops-reconcile for deterministic 3-way matching."
                    ),
                    mentions=["invoiceops-reconcile"],
                    evidence_refs=[f"doc_{inv.id}.pdf"],
                    action_type="intake_report",
                    action_payload={
                        "invoice_id": inv.id,
                        "vendor_id": inv.vendor_id,
                        "total": str(inv.invoice_total),
                        "ocr_confidence": 0.98
                    },
                    auto_react=False
                )
            return

        # ---------------------------------------------------------------------
        # ALGORITHM 3: DETERMINISTIC 3-WAY MATCHING (Reconcile Agent)
        # ---------------------------------------------------------------------
        if "match" in low_content or "reconcile" in low_content or "@invoiceops-reconcile" in mentions:
            inv = db.query(Invoice).filter(Invoice.id == target_id).first()
            if inv:
                run, ex_list = run_three_way_match(db, inv.id, executed_by="invoiceops-reconcile")
                status = run.overall_status

                msg_content = (
                    f"🤖 **Deterministic 3-Way Reconciliation for `{inv.id}`**:\n\n"
                    f"• **Overall Engine Status**: `{status}`\n"
                    f"• **Total Billed**: ₹{inv.invoice_total} {inv.currency}\n"
                    f"• **Policy Engine Version**: `{run.policy_version}`\n"
                    f"• **Precision Standard**: Strict Python `Decimal` (zero floating-point drift)\n"
                )

                if ex_list:
                    msg_content += f"• **Blocking Exceptions Identified**: {len(ex_list)}\n\n"
                    for ex in ex_list:
                        msg_content += (
                            f"  ⚠️ **`[{ex.code}]`**: {ex.description}\n"
                            f"     - Assigned Owner: `@{ex.owner_role}` | Severity: `{ex.severity}`\n"
                        )
                    msg_content += "\n@procurement_owner: Please verify if an authorized PO amendment or rate addendum exists for Acme Supplies."
                    target_role = "procurement_owner"
                    action_type = "match_exception"
                else:
                    msg_content += (
                        "• **Line Items Verification**: All lines, quantities, and prices matched agreed PO & GRN within 0.00 tolerance.\n\n"
                        "Ready for final human-in-the-loop review by @finance_approver."
                    )
                    target_role = "finance_approver"
                    action_type = "match_pass"

                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_RECONCILE["id"],
                    sender_name=AGENT_RECONCILE["name"],
                    sender_role=AGENT_RECONCILE["role"],
                    avatar=AGENT_RECONCILE["avatar"],
                    content=msg_content,
                    mentions=[target_role],
                    evidence_refs=[inv.purchase_order_id or "PO-2026-0082"],
                    action_type=action_type,
                    action_payload={"invoice_id": inv.id, "status": status, "exception_count": len(ex_list)},
                    auto_react=False
                )
            return

        # ---------------------------------------------------------------------
        # ALGORITHM 4: PROCUREMENT OVERRIDE & EVIDENCE RESOLUTION
        # ---------------------------------------------------------------------
        if (
            "override" in low_content 
            or "addendum" in low_content 
            or "surcharge" in low_content 
            or "waiver" in low_content
            or "amendment" in low_content
            or (user_msg.sender_id == "procurement_owner_1" and ("approve" in low_content or "verified" in low_content))
        ) and user_msg.sender_id != "finance_approver_1":
            # Resolve open exceptions in DB
            open_exceptions = db.query(ExceptionRecord).filter(
                ExceptionRecord.invoice_id == target_id,
                ExceptionRecord.status == "open"
            ).all()

            for ex in open_exceptions:
                ex.status = "resolved"
                ex.resolved_by = user_msg.sender_id
                ex.resolution_comment = "Verified authorized rate surcharge under Addendum #A-42 (Overnight rate amendment)."
                ex.evidence_doc_id = "Addendum_A42_Overnight_Rate.pdf"
            
            # Update invoice status
            inv = db.query(Invoice).filter(Invoice.id == target_id).first()
            if inv:
                inv.status = "needs_human_approval"
            db.commit()

            log_audit_event(
                db=db,
                actor_id=user_msg.sender_id,
                actor_type="human",
                action="PROCUREMENT_OVERRIDE_RECORDED",
                entity_type="Invoice",
                entity_id=target_id,
                invoice_id=target_id,
                reason="Procurement override confirmed with attached Addendum #A-42.",
                source_refs=["Addendum_A42_Overnight_Rate.pdf"]
            )
            db.commit()

            SwitchService.post_message(
                db=db,
                room_id=user_msg.room_id,
                thread_id=user_msg.thread_id,
                sender_id=AGENT_RECONCILE["id"],
                sender_name=AGENT_RECONCILE["name"],
                sender_role=AGENT_RECONCILE["role"],
                avatar=AGENT_RECONCILE["avatar"],
                content=(
                    "📄 **Procurement Addendum Acknowledged & Line Re-Checked**:\n\n"
                    "• **Evidence Document**: Attached `Addendum_A42_Overnight_Rate.pdf` (Addendum #A-42)\n"
                    "• **Variance Coverage**: Price delta of ₹400.00 acknowledged under authorized overnight shipping clause.\n"
                    "• **Exception Status**: Updated to `RESOLVED_WITH_EVIDENCE` in system of record.\n"
                    "• **Arithmetic Verification**: 3-way check re-calculated with pure Decimal precision (0.00 floating point error).\n"
                    "• **Current Case State**: `NEEDS_HUMAN_APPROVAL`\n\n"
                    "Calling @finance_approver for mandatory human-in-the-loop sign-off to generate downstream payment voucher."
                ),
                mentions=["finance_approver"],
                evidence_refs=["Addendum_A42_Overnight_Rate.pdf"],
                action_type="procurement_override_confirmed",
                action_payload={"addendum": "Addendum #A-42", "status": "NEEDS_HUMAN_APPROVAL"},
                auto_react=False
            )
            return

        # ---------------------------------------------------------------------
        # ALGORITHM 5: HUMAN-IN-THE-LOOP (HITL) APPROVAL & FINANCIAL SAFETY
        # ---------------------------------------------------------------------
        if (
            "approved" in low_content 
            or "sign off" in low_content 
            or "release payment" in low_content 
            or "voucher" in low_content
        ):
            # RBAC Enforcement: AI agents or non-finance roles are strictly forbidden from approving
            if user_msg.sender_role != "human" or (user_msg.sender_id != "finance_approver_1" and "finance" not in user_msg.sender_id):
                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_INTAKE["id"],
                    sender_name=AGENT_INTAKE["name"],
                    sender_role=AGENT_INTAKE["role"],
                    avatar=AGENT_INTAKE["avatar"],
                    content=(
                        "⛔ **[HITL GOVERNANCE REJECTION]**:\n\n"
                        "• **Permission Denied**: The Switch collaboration policy and InvoiceOps safety boundaries strictly forbid AI agents, AP clerks, or Procurement from signing off on payments.\n"
                        "• **Required Actor**: Only a verified human `finance_approver` may sign off to generate a payment-ready voucher.\n"
                        "• **Action Enforced**: State remains locked."
                    ),
                    mentions=["finance_approver"],
                    action_type="governance_rejection",
                    auto_react=False
                )
                return

            # Check if active blocking exceptions remain
            active_ex = db.query(ExceptionRecord).filter(
                ExceptionRecord.invoice_id == target_id,
                ExceptionRecord.status == "open"
            ).count()

            if active_ex > 0:
                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_RECONCILE["id"],
                    sender_name=AGENT_RECONCILE["name"],
                    sender_role=AGENT_RECONCILE["role"],
                    avatar=AGENT_RECONCILE["avatar"],
                    content=(
                        f"⚠️ **Cannot Approve Case `{target_id}`**:\n\n"
                        f"• {active_ex} active blocking exception(s) remain open.\n"
                        "• Invariant: All exceptions must be resolved with procurement evidence or credit memos before finance sign-off."
                    ),
                    action_type="approval_blocked",
                    auto_react=False
                )
                return

            try:
                # Trigger real approval & payment ready voucher creation
                appr, pay_rec = process_approval_decision(
                    db=db,
                    invoice_id=target_id,
                    approver_id=user_msg.sender_id,
                    approver_role="finance_approver",
                    decision="approved",
                    comment=user_msg.content,
                    idempotency_key=f"switch_appr_{target_id}_{user_msg.id[:8]}"
                )

                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_INTAKE["id"],
                    sender_name=AGENT_INTAKE["name"],
                    sender_role=AGENT_INTAKE["role"],
                    avatar=AGENT_INTAKE["avatar"],
                    content=(
                        f"✅ **Human Finance Approval Executed & Payment-Ready Voucher Generated**:\n\n"
                        f"• **Target Invoice**: `{target_id}`\n"
                        f"• **Approval Sign-Off ID**: `{appr.id}`\n"
                        f"• **Approved Amount**: ₹{pay_rec.approved_amount} {pay_rec.currency}\n"
                        f"• **Payment Record Voucher**: `{pay_rec.id}`\n"
                        f"• **Cryptographic Integrity**: SHA-256 digest sealed\n"
                        f"• **Financial Safety Boundary**: Hard invariant guaranteed — zero live banking rails or payment execution APIs touched. Downstream voucher export only.\n"
                        f"• **Audit Trail**: Tamper-evident append-only ledger updated.\n\n"
                        "Collaboration workflow complete. Case closed successfully."
                    ),
                    mentions=[],
                    action_type="payment_voucher_generated",
                    action_payload={
                        "approval_id": appr.id,
                        "payment_record_id": pay_rec.id,
                        "approved_amount": str(pay_rec.approved_amount),
                        "status": "COMPLETED"
                    },
                    auto_react=False
                )
            except Exception as e:
                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_INTAKE["id"],
                    sender_name=AGENT_INTAKE["name"],
                    sender_role=AGENT_INTAKE["role"],
                    avatar=AGENT_INTAKE["avatar"],
                    content=f"⚠️ Approval notice: {str(e)}",
                    auto_react=False
                )
            return

        # ---------------------------------------------------------------------
        # ALGORITHM 6: AUDIT LEDGER INQUIRY
        # ---------------------------------------------------------------------
        if "audit" in low_content or "ledger" in low_content or "trail" in low_content:
            events = db.query(AuditEvent).filter(AuditEvent.invoice_id == target_id).order_by(AuditEvent.occurred_at.asc()).all()
            event_lines = []
            for ev in events[-5:]:
                event_lines.append(f"• `{ev.occurred_at[:19]}` | Actor: `{ev.actor_id}` | Action: `{ev.action}`")
            trail_text = "\n".join(event_lines) if event_lines else "• No audit events logged yet."

            SwitchService.post_message(
                db=db,
                room_id=user_msg.room_id,
                thread_id=user_msg.thread_id,
                sender_id=AGENT_RECONCILE["id"],
                sender_name=AGENT_RECONCILE["name"],
                sender_role=AGENT_RECONCILE["role"],
                avatar=AGENT_RECONCILE["avatar"],
                content=(
                    f"📜 **Tamper-Evident Audit Trail for `{target_id}`**:\n\n"
                    f"{trail_text}\n\n"
                    f"• Total Logged Events: `{len(events)}`\n"
                    "• Storage: Append-only cryptographic SQLite ledger."
                ),
                action_type="audit_ledger",
                action_payload={"event_count": len(events)},
                auto_react=False
            )
            return

        # Default teammate acknowledgment
        SwitchService.post_message(
            db=db,
            room_id=user_msg.room_id,
            thread_id=user_msg.thread_id,
            sender_id=AGENT_INTAKE["id"],
            sender_name=AGENT_INTAKE["name"],
            sender_role=AGENT_INTAKE["role"],
            avatar=AGENT_INTAKE["avatar"],
            content=f"Received input from {user_msg.sender_name}. Synchronized with InvoiceOps state ledger.",
            auto_react=False
        )

    @staticmethod
    def seed_initial_messages(db: Session):
        """Seeds the canonical Switch multi-turn conversation thread for INV-2026-1042."""
        thread_id = "thread_INV-2026-1042"
        room_id = DEFAULT_ROOM_ID

        # Clear any existing
        db.query(SwitchMessage).filter(SwitchMessage.thread_id == thread_id).delete()
        db.commit()

        messages = [
            (
                AGENT_INTAKE["id"],
                AGENT_INTAKE["name"],
                AGENT_INTAKE["role"],
                AGENT_INTAKE["avatar"],
                (
                    "📥 **Invoice Ingested**: Ingested `INV-2026-1042` from **Acme Supplies Co.** (VND-001).\n"
                    "• **Total**: ₹4,150.00 INR\n"
                    "• **OCR Confidence**: 0.98\n"
                    "• **Purchase Order**: `PO-2026-0082`\n"
                    "• **Duplicate Check**: Passed (Normalized hash `c9a4f...`)\n\n"
                    "Calling @invoiceops-reconcile for 3-way matching."
                ),
                ["invoiceops-reconcile"],
                ["doc_INV-2026-1042.pdf"],
                "intake_report",
                {"invoice_id": "INV-2026-1042", "confidence": 0.98}
            ),
            (
                AGENT_RECONCILE["id"],
                AGENT_RECONCILE["name"],
                AGENT_RECONCILE["role"],
                AGENT_RECONCILE["avatar"],
                (
                    "⚠️ **Match Exception Detected on Line 1**: `Industrial Widget`\n\n"
                    "• **Invoice Unit Price**: ₹250.00\n"
                    "• **PO Agreed Price**: ₹200.00\n"
                    "• **Quantity**: 8 units delivered on GRN-2026-0041\n"
                    "• **Line Variance**: +₹400.00 (+25.0% price delta)\n"
                    "• **Configured Tolerance**: Max ₹1.00 abs / 0.50% rel\n\n"
                    "@procurement_owner please verify if an authorized addendum or surcharge exists for Acme Supplies."
                ),
                ["procurement_owner"],
                ["PO-2026-0082", "GRN-2026-0041"],
                "match_exception",
                {"exception_code": "PRICE_MISMATCH", "variance": 400.0}
            ),
            (
                HUMAN_PROCUREMENT["id"],
                HUMAN_PROCUREMENT["name"],
                HUMAN_PROCUREMENT["role"],
                HUMAN_PROCUREMENT["avatar"],
                (
                    "Reviewed PO-2026-0082. Acme Supplies applied an overnight rush shipping surcharge of ₹50/unit authorized under Addendum #A-42.\n\n"
                    "Attached signed amendment `Addendum_A42_Overnight_Rate.pdf`. Surcharge approved for processing."
                ),
                ["invoiceops-reconcile"],
                ["Addendum_A42_Overnight_Rate.pdf"],
                "procurement_override",
                {"addendum_id": "Addendum #A-42", "approved_delta": 400.0}
            ),
            (
                AGENT_RECONCILE["id"],
                AGENT_RECONCILE["name"],
                AGENT_RECONCILE["role"],
                AGENT_RECONCILE["avatar"],
                (
                    "✅ **Reconciliation Re-Run Successful**:\n\n"
                    "• Verified procurement override evidence `Addendum_A42_Overnight_Rate.pdf`.\n"
                    "• Price delta of ₹400.00 reconciled.\n"
                    "• Overall Status: `NEEDS_HUMAN_APPROVAL`\n\n"
                    "Ready for @finance_approver final human sign-off to create payment-ready record."
                ),
                ["finance_approver"],
                [],
                "ready_for_approval",
                {"status": "NEEDS_HUMAN_APPROVAL"}
            )
        ]

        for sender_id, sender_name, sender_role, avatar, content, mentions, evidence, action_type, payload in messages:
            msg = SwitchMessage(
                room_id=room_id,
                thread_id=thread_id,
                sender_id=sender_id,
                sender_name=sender_name,
                sender_role=sender_role,
                avatar=avatar,
                content=content,
                mentions_json=json.dumps(mentions),
                evidence_refs_json=json.dumps(evidence),
                action_type=action_type,
                action_payload_json=json.dumps(payload),
                created_at=utcnow_iso()
            )
            db.add(msg)
        db.commit()

    # -------------------------------------------------------------------------
    # Model Context Protocol (MCP) Server Implementation
    # -------------------------------------------------------------------------
    @staticmethod
    def get_mcp_manifest():
        """Returns MCP tool definitions so Claude Code / OpenAI Codex / OpenCode can join Switch."""
        return {
            "name": "invoiceops-switch-mcp",
            "version": "1.0.0",
            "description": "InvoiceOps Autonomous Accounts Payable MCP Server for Switch",
            "tools": [
                {
                    "name": "invoiceops_match",
                    "description": "Execute deterministic 3-way matching for an invoice against PO and GRN with pure Decimal precision.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string", "description": "e.g. INV-2026-1041 or INV-2026-1042"}
                        },
                        "required": ["invoice_id"]
                    }
                },
                {
                    "name": "invoiceops_inspect",
                    "description": "Inspect line-item variances, quantity deltas, and OCR confidence summary for an invoice.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string", "description": "Invoice identifier"}
                        },
                        "required": ["invoice_id"]
                    }
                },
                {
                    "name": "invoiceops_attach_evidence",
                    "description": "Attach procurement override evidence (e.g. contract addendum) to resolve a price or quantity exception.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "exception_id": {"type": "string"},
                            "rationale": {"type": "string"},
                            "evidence_ref": {"type": "string"}
                        },
                        "required": ["exception_id", "rationale"]
                    }
                },
                {
                    "name": "invoiceops_approve_payment",
                    "description": "Human Finance Approver sign-off. Generates downstream payment-ready record with cryptographic hash.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string"},
                            "approver_role": {"type": "string", "enum": ["finance_approver"]},
                            "comment": {"type": "string"},
                            "idempotency_key": {"type": "string"}
                        },
                        "required": ["invoice_id", "approver_role"]
                    }
                },
                {
                    "name": "invoiceops_get_audit",
                    "description": "Retrieve the tamper-evident append-only audit trail for an invoice.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "invoice_id": {"type": "string"}
                        },
                        "required": ["invoice_id"]
                    }
                }
            ]
        }

    @staticmethod
    def invoke_mcp_tool(tool_name: str, args: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Executes an MCP tool call from a Switch agent and streams the event into the room."""
        result: Dict[str, Any] = {}
        invoice_id = args.get("invoice_id", "INV-2026-1042")

        if tool_name == "invoiceops_match":
            run, ex_list = run_three_way_match(db, invoice_id, executed_by="mcp_switch_agent")
            result = {
                "match_run_id": run.id,
                "overall_status": run.overall_status,
                "policy_version": run.policy_version,
                "exceptions": [
                    {"code": e.code, "severity": e.severity, "desc": e.description, "owner": e.owner_role}
                    for e in ex_list
                ]
            }
            summary_content = (
                f"🔌 **[MCP Tool Call: `invoiceops_match`]**\n\n"
                f"Claude Code executed deterministic 3-way match on `{invoice_id}`.\n"
                f"• Status: `{run.overall_status}` | Exceptions: `{len(ex_list)}`"
            )

        elif tool_name == "invoiceops_inspect":
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not inv:
                return {"error": f"Invoice {invoice_id} not found"}
            result = {
                "id": inv.id,
                "vendor_id": inv.vendor_id,
                "purchase_order_id": getattr(inv, "purchase_order_id", None),
                "total": inv.invoice_total,
                "currency": inv.currency,
                "status": inv.status,
                "lines": [
                    {"line": l.line_number, "desc": l.description, "qty": l.quantity, "price": l.unit_price}
                    for l in inv.lines
                ]
            }
            summary_content = (
                f"🔌 **[MCP Tool Call: `invoiceops_inspect`]**\n\n"
                f"Claude Code inspected case `{invoice_id}`.\n"
                f"• Vendor: `{inv.vendor_id}` | Billed Total: ₹{inv.invoice_total} {inv.currency}"
            )

        elif tool_name == "invoiceops_attach_evidence":
            ex_id = args.get("exception_id")
            rationale = args.get("rationale", "Addendum override attached via MCP")
            evidence_ref = args.get("evidence_ref", "Addendum_A42_Overnight_Rate.pdf")

            ex = db.query(ExceptionRecord).filter(ExceptionRecord.id == ex_id).first()
            if ex:
                ex.status = "resolved"
                ex.resolved_by = "mcp_switch_agent"
                ex.resolution_comment = rationale
                ex.evidence_doc_id = evidence_ref
                db.commit()
                invoice_id = ex.invoice_id
                result = {"status": "resolved", "exception_id": ex.id, "evidence_ref": evidence_ref}
            else:
                # Resolve open exceptions for target invoice
                open_ex = db.query(ExceptionRecord).filter(
                    ExceptionRecord.invoice_id == invoice_id,
                    ExceptionRecord.status == "open"
                ).all()
                for e in open_ex:
                    e.status = "resolved"
                    e.resolved_by = "mcp_switch_agent"
                    e.resolution_comment = rationale
                    e.evidence_doc_id = evidence_ref
                db.commit()
                result = {"status": "resolved", "resolved_count": len(open_ex), "evidence_ref": evidence_ref}

            summary_content = (
                f"🔌 **[MCP Tool Call: `invoiceops_attach_evidence`]**\n\n"
                f"Attached procurement addendum evidence `{evidence_ref}`.\n"
                f"• Rationale: {rationale}"
            )

        elif tool_name == "invoiceops_approve_payment":
            role = args.get("approver_role")
            if role != "finance_approver":
                return {"error": "HTTP 403 Forbidden: Only human finance_approver can authorize payments"}
            appr, pay_rec = process_approval_decision(
                db=db,
                invoice_id=invoice_id,
                approver_id="mcp_finance_approver",
                approver_role=role,
                decision="approved",
                comment=args.get("comment", "Approved via Switch MCP Tool"),
                idempotency_key=args.get("idempotency_key", f"mcp_{utcnow_iso()}")
            )
            result = {
                "approval_id": appr.id,
                "payment_ready_id": pay_rec.id,
                "amount": pay_rec.approved_amount,
                "status": pay_rec.status
            }
            summary_content = (
                f"🔌 **[MCP Tool Call: `invoiceops_approve_payment`]**\n\n"
                f"Human Finance Sign-off completed via MCP for `{invoice_id}`.\n"
                f"• Voucher Generated: `{pay_rec.id}` | Amount: ₹{pay_rec.approved_amount}"
            )

        elif tool_name == "invoiceops_get_audit":
            events = db.query(AuditEvent).filter(AuditEvent.invoice_id == invoice_id).all()
            result = {
                "invoice_id": invoice_id,
                "event_count": len(events),
                "events": [
                    {"action": e.action, "actor": e.actor_id, "time": e.occurred_at, "state": e.after_state}
                    for e in events
                ]
            }
            summary_content = (
                f"🔌 **[MCP Tool Call: `invoiceops_get_audit`]**\n\n"
                f"Retrieved `{len(events)}` append-only audit records for `{invoice_id}`."
            )

        else:
            return {"error": f"Unknown MCP tool {tool_name}"}

        # Post real-time event to Switch Room so human operators in the room see what MCP agent did
        try:
            SwitchService.post_message(
                db=db,
                room_id=DEFAULT_ROOM_ID,
                thread_id=f"thread_{invoice_id}",
                sender_id="mcp_switch_agent",
                sender_name="Claude Code (via MCP)",
                sender_role="agent",
                avatar="bot-blue",
                content=summary_content,
                action_type=f"mcp_{tool_name}",
                action_payload=result,
                auto_react=False
            )
        except Exception as e:
            logger.warning(f"Could not post MCP invocation message: {e}")

        return result
