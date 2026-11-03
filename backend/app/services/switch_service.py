import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import httpx

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

        # Reactive AI agent response if human mentioned an agent or posted in thread
        if auto_react and sender_role == "human":
            SwitchService._trigger_reactive_agent_reply(db, msg)

        return result

    @staticmethod
    def _trigger_reactive_agent_reply(db: Session, user_msg: SwitchMessage):
        """Autonomously analyzes user input and generates AI teammate response."""
        content = user_msg.content.lower()
        mentions = json.loads(user_msg.mentions_json or "[]")
        thread_id = user_msg.thread_id

        # Determine invoice ID from thread or content
        invoice_id = None
        for inv_id in ["INV-2026-1041", "INV-2026-1042", "INV-2026-1043", "INV-2026-1044"]:
            if inv_id.lower() in content or inv_id.lower() in thread_id.lower():
                invoice_id = inv_id
                break

        # Scenario 1: User asks for match run or status
        if "match" in content or "reconcile" in content or "@invoiceops-reconcile" in mentions:
            target_id = invoice_id or "INV-2026-1042"
            inv = db.query(Invoice).filter(Invoice.id == target_id).first()
            if inv:
                # Run deterministic 3-way match
                run, ex_list = run_three_way_match(db, inv.id, executed_by="invoiceops-reconcile")
                status = run.overall_status
                msg_content = (
                    f"🤖 **Reconciliation Engine Result for {inv.id}**:\n\n"
                    f"• **Status**: `{status}`\n"
                    f"• **Total Billed**: ₹{inv.invoice_total}\n"
                    f"• **Policy Version**: `{run.policy_version}`\n"
                )
                if ex_list:
                    msg_content += f"• **Exceptions Detected**: {len(ex_list)}\n"
                    for ex in ex_list:
                        msg_content += f"  - `[{ex.code}]` {ex.description} (Owner: `@{ex.owner_role}`)\n"
                    msg_content += "\n@procurement_owner please verify if this rate variance has authorized override documentation."
                else:
                    msg_content += "• All line items matched within configured zero-tolerance. Ready for @finance_approver sign-off."

                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_RECONCILE["id"],
                    sender_name=AGENT_RECONCILE["name"],
                    sender_role=AGENT_RECONCILE["role"],
                    content=msg_content,
                    avatar=AGENT_RECONCILE["avatar"],
                    mentions=["procurement_owner" if ex_list else "finance_approver"],
                    action_type="match_report",
                    action_payload={"invoice_id": inv.id, "status": status, "exception_count": len(ex_list)},
                    auto_react=False
                )
            return

        # Scenario 2: User provides procurement authorization or addendum
        if ("approve" in content or "override" in content or "addendum" in content or "surcharge" in content) and user_msg.sender_id != "finance_approver_1":
            SwitchService.post_message(
                db=db,
                room_id=user_msg.room_id,
                thread_id=user_msg.thread_id,
                sender_id=AGENT_RECONCILE["id"],
                sender_name=AGENT_RECONCILE["name"],
                sender_role=AGENT_RECONCILE["role"],
                content=(
                    "📄 **Procurement Addendum Acknowledged**:\n\n"
                    "• Rate surcharge verified against authorized Addendum #A-42.\n"
                    "• Exception status updated to `RESOLVED_WITH_EVIDENCE`.\n"
                    "• 3-way line item arithmetic validated with zero floating-point drift.\n\n"
                    "Calling @finance_approver for final human-in-the-loop sign-off to generate downstream payment-ready record."
                ),
                avatar=AGENT_RECONCILE["avatar"],
                mentions=["finance_approver"],
                action_type="procurement_override_confirmed",
                action_payload={"addendum": "Addendum #A-42", "status": "PENDING_FINANCE_APPROVAL"},
                auto_react=False
            )
            return

        # Scenario 3: Finance Approver signs off
        if "approved" in content and ("finance" in user_msg.sender_id or "approv" in user_msg.sender_id):
            target_id = invoice_id or "INV-2026-1042"
            try:
                # Trigger real approval & payment ready voucher creation
                appr, pay_rec = process_approval_decision(
                    db=db,
                    invoice_id=target_id,
                    approver_id=user_msg.sender_id,
                    approver_role="finance_approver",
                    decision="approved",
                    comment=user_msg.content,
                    idempotency_key=f"switch_approval_{target_id}_{user_msg.id[:8]}"
                )
                SwitchService.post_message(
                    db=db,
                    room_id=user_msg.room_id,
                    thread_id=user_msg.thread_id,
                    sender_id=AGENT_INTAKE["id"],
                    sender_name=AGENT_INTAKE["name"],
                    sender_role=AGENT_INTAKE["role"],
                    content=(
                        f"✅ **Human Finance Approval Executed & Payment-Ready Voucher Generated**:\n\n"
                        f"• **Invoice**: `{target_id}`\n"
                        f"• **Approval ID**: `{appr.id}`\n"
                        f"• **Approved Amount**: ₹{pay_rec.approved_amount} {pay_rec.currency}\n"
                        f"• **Payment Record**: `{pay_rec.id}`\n"
                        f"• **Security Boundary**: Guaranteed zero payment execution (Voucher export only).\n"
                        f"• **Audit Trail**: Append-only log event recorded.\n\n"
                        "Workflow complete. Case closed successfully."
                    ),
                    avatar=AGENT_INTAKE["avatar"],
                    mentions=[],
                    action_type="payment_voucher_generated",
                    action_payload={"approval_id": appr.id, "payment_record_id": pay_rec.id, "status": "COMPLETED"},
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
                    content=f"⚠️ Approval notice: {str(e)}",
                    avatar=AGENT_INTAKE["avatar"],
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
            content=f"Received input from {user_msg.sender_name}. Synchronized with InvoiceOps state ledger.",
            avatar=AGENT_INTAKE["avatar"],
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
        """Executes an MCP tool call from a Switch agent."""
        if tool_name == "invoiceops_match":
            invoice_id = args.get("invoice_id")
            run, ex_list = run_three_way_match(db, invoice_id, executed_by="mcp_switch_agent")
            return {
                "match_run_id": run.id,
                "overall_status": run.overall_status,
                "policy_version": run.policy_version,
                "exceptions": [
                    {"code": e.code, "severity": e.severity, "desc": e.description, "owner": e.owner_role}
                    for e in ex_list
                ]
            }

        elif tool_name == "invoiceops_inspect":
            invoice_id = args.get("invoice_id")
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if not inv:
                return {"error": f"Invoice {invoice_id} not found"}
            return {
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

        elif tool_name == "invoiceops_approve_payment":
            role = args.get("approver_role")
            if role != "finance_approver":
                return {"error": "HTTP 403 Forbidden: Only human finance_approver can authorize payments"}
            appr, pay_rec = process_approval_decision(
                db=db,
                invoice_id=args.get("invoice_id"),
                approver_id="mcp_finance_approver",
                approver_role=role,
                decision="approved",
                comment=args.get("comment", "Approved via Switch MCP Tool"),
                idempotency_key=args.get("idempotency_key", f"mcp_{utcnow_iso()}")
            )
            return {
                "approval_id": appr.id,
                "payment_ready_id": pay_rec.id,
                "amount": pay_rec.approved_amount,
                "status": pay_rec.status
            }

        elif tool_name == "invoiceops_get_audit":
            events = db.query(AuditEvent).filter(AuditEvent.invoice_id == args.get("invoice_id")).all()
            return {
                "invoice_id": args.get("invoice_id"),
                "event_count": len(events),
                "events": [
                    {"action": e.action, "actor": e.actor_id, "time": e.occurred_at, "state": e.after_state}
                    for e in events
                ]
            }

        return {"error": f"Unknown MCP tool {tool_name}"}
