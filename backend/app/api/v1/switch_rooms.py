from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.switch_service import SwitchService, DEFAULT_ROOM_ID

router = APIRouter(prefix="/switch", tags=["Switch Collaboration Room"])


class PostMessageRequest(BaseModel):
    content: str
    thread_id: str = "thread_INV-2026-1042"
    sender_id: str = "ap_clerk_1"
    sender_name: str = "Sarah Chen (AP Clerk)"
    sender_role: str = "human"
    avatar: Optional[str] = "user-amber"
    mentions: Optional[List[str]] = Field(default_factory=list)
    evidence_refs: Optional[List[str]] = Field(default_factory=list)
    action_type: Optional[str] = "chat"
    action_payload: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MCPInvokeRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class WebhookPayload(BaseModel):
    event: str
    room_id: Optional[str] = DEFAULT_ROOM_ID
    thread_id: Optional[str] = "thread_INV-2026-1042"
    sender: Optional[Dict[str, str]] = None
    content: str
    mentions: Optional[List[str]] = None


@router.get("/rooms")
def get_rooms():
    """Returns the list of active Switch collaboration rooms and connected agents."""
    return [SwitchService.get_room_metadata()]


@router.get("/status")
def get_switch_status():
    """Returns connectivity and integration status across Switch Core, MCP, and Chat platforms."""
    return SwitchService.get_room_metadata()


@router.get("/rooms/{room_id}/messages")
def get_room_messages(
    room_id: str,
    thread_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve all messages in the Switch room or thread."""
    return SwitchService.get_messages(db=db, room_id=room_id, thread_id=thread_id, limit=limit)


@router.post("/rooms/{room_id}/messages")
def post_room_message(
    room_id: str,
    req: PostMessageRequest,
    db: Session = Depends(get_db)
):
    """Post a message into a Switch room thread, triggering reactive agent teammate actions."""
    msg = SwitchService.post_message(
        db=db,
        room_id=room_id,
        thread_id=req.thread_id,
        sender_id=req.sender_id,
        sender_name=req.sender_name,
        sender_role=req.sender_role,
        content=req.content,
        avatar=req.avatar,
        mentions=req.mentions,
        evidence_refs=req.evidence_refs,
        action_type=req.action_type,
        action_payload=req.action_payload,
        auto_react=True
    )
    return msg


@router.post("/rooms/{room_id}/simulate-workflow")
def simulate_workflow(
    room_id: str,
    invoice_id: str = Query("INV-2026-1042"),
    db: Session = Depends(get_db)
):
    """
    Executes the complete end-to-end collaborative exception resolution scenario for judges:
    1. Intake extraction
    2. 3-Way Reconcile price mismatch detection
    3. Procurement owner override with Addendum #A-42 evidence
    4. Re-check & tolerance clearance
    5. Human finance approval
    6. Payment-ready record generation
    """
    thread_id = f"thread_{invoice_id}"
    SwitchService.seed_initial_messages(db)
    
    # Execute step 5: Finance approval in thread
    appr_msg = SwitchService.post_message(
        db=db,
        room_id=room_id,
        thread_id=thread_id,
        sender_id="finance_approver_1",
        sender_name="Elena Rostova (Finance Approver)",
        sender_role="human",
        content="Exception reviewed against authorized procurement addendum #A-42. Surcharge approved for payment voucher generation.",
        avatar="user-purple",
        mentions=[],
        action_type="finance_approval",
        auto_react=True
    )
    
    messages = SwitchService.get_messages(db=db, room_id=room_id, thread_id=thread_id)
    return {
        "status": "workflow_completed",
        "thread_id": thread_id,
        "message_count": len(messages),
        "messages": messages
    }


@router.post("/rooms/{room_id}/reset")
def reset_room(
    room_id: str,
    db: Session = Depends(get_db)
):
    """Resets the Switch room thread back to clean initial demo state."""
    SwitchService.seed_initial_messages(db)
    return {"status": "room_reset_successful", "room_id": room_id}


@router.post("/webhook")
def inbound_switch_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db)
):
    """
    Inbound webhook receiver from Switch Core, Gateway, or Slack/Mattermost.
    Allows external Switch agents to post into InvoiceOps room.
    """
    sender = payload.sender or {"id": "external_switch_agent", "name": "Switch External Agent", "role": "agent"}
    msg = SwitchService.post_message(
        db=db,
        room_id=payload.room_id or DEFAULT_ROOM_ID,
        thread_id=payload.thread_id or "thread_INV-2026-1042",
        sender_id=sender.get("id", "external_agent"),
        sender_name=sender.get("name", "External Teammate"),
        sender_role=sender.get("role", "agent"),
        content=payload.content,
        mentions=payload.mentions or [],
        auto_react=True
    )
    return {"status": "received", "message_id": msg["id"]}


@router.get("/mcp")
def get_mcp_manifest():
    """Serves the Model Context Protocol (MCP) server manifest for Switch agents."""
    return SwitchService.get_mcp_manifest()


@router.post("/mcp/invoke")
def invoke_mcp(
    req: MCPInvokeRequest,
    db: Session = Depends(get_db)
):
    """Invokes an InvoiceOps tool over MCP."""
    return SwitchService.invoke_mcp_tool(req.tool, req.arguments, db)

