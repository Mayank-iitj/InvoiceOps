from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from backend.app.database import get_db
from backend.app.services.telegram_service import telegram_gateway, _load_subscribers
from backend.app.config import settings

router = APIRouter(prefix="/telegram", tags=["Telegram Chat Gateway"])


class BroadcastRequest(BaseModel):
    message: str = Field(..., description="Message text to broadcast to Telegram subscribers")
    parse_mode: Optional[str] = Field("Markdown", description="Formatting mode: Markdown or None")


class SendMessageRequest(BaseModel):
    chat_id: int | str = Field(..., description="Target Telegram chat ID")
    message: str = Field(..., description="Message text to send")
    parse_mode: Optional[str] = Field("Markdown", description="Formatting mode: Markdown or None")


@router.get("/status")
async def get_telegram_status():
    """Returns connectivity and configuration status for the Telegram Chat Gateway."""
    configured = telegram_gateway.is_configured()
    bot_info = await telegram_gateway.get_me() if configured else {}
    subscribers = _load_subscribers()

    return {
        "status": "connected" if configured and "id" in bot_info else ("configured" if configured else "disabled"),
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
        "polling_active": telegram_gateway._is_running,
        "subscribers_count": len(subscribers),
        "bot_details": bot_info,
        "gateway_enabled": settings.TELEGRAM_GATEWAY_ENABLED
    }


@router.post("/webhook")
async def telegram_webhook(
    update: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Inbound webhook receiver from Telegram Bot API.
    Can be used in production when webhook mode is set instead of long polling.
    """
    if not telegram_gateway.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram Gateway is not configured."
        )

    await telegram_gateway.handle_update(update, db)
    return {"status": "ok"}


@router.post("/broadcast")
async def broadcast_to_subscribers(
    req: BroadcastRequest
):
    """Broadcasts a notification message to all subscribed Telegram users."""
    if not telegram_gateway.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram Gateway is not configured."
        )

    subscribers = _load_subscribers()
    if not subscribers:
        return {"status": "no_subscribers", "delivered_count": 0}

    await telegram_gateway.broadcast_notification(req.message, parse_mode=req.parse_mode)
    return {
        "status": "broadcast_sent",
        "subscribers_count": len(subscribers),
        "message": req.message
    }


@router.post("/send")
async def send_direct_message(
    req: SendMessageRequest
):
    """Sends a direct message to a specific Telegram chat ID."""
    if not telegram_gateway.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram Gateway is not configured."
        )

    success = await telegram_gateway.send_message(req.chat_id, req.message, parse_mode=req.parse_mode)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to deliver message to Telegram chat {req.chat_id}."
        )

    return {"status": "delivered", "chat_id": req.chat_id}

