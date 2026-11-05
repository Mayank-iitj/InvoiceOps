import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database import SessionLocal
from backend.app.services.seed_service import seed_database
from backend.app.services.telegram_service import telegram_gateway, _save_subscriber, _load_subscribers

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    from backend.app.database import engine, Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db, run_initial_match=True)
    db.close()
    yield

def test_telegram_status_endpoint():
    resp = client.get("/api/v1/telegram/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["bot_username"] == "@switch_devops_bot"
    assert data["gateway_enabled"] is True
    assert "status" in data

@patch.object(telegram_gateway, "send_message", new_callable=AsyncMock)
def test_telegram_webhook_start_command(mock_send):
    mock_send.return_value = True
    payload = {
        "update_id": 1001,
        "message": {
            "message_id": 1,
            "from": {"id": 123456, "first_name": "Test", "last_name": "User", "username": "testuser"},
            "chat": {"id": 123456, "type": "private"},
            "text": "/start"
        }
    }
    resp = client.post("/api/v1/telegram/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
    assert mock_send.called
    sent_text = mock_send.call_args[0][1]
    assert "Welcome to InvoiceOps" in sent_text
    assert "@switch_devops_bot" in sent_text

@patch.object(telegram_gateway, "send_message", new_callable=AsyncMock)
def test_telegram_webhook_invoices_command(mock_send):
    mock_send.return_value = True
    payload = {
        "update_id": 1002,
        "message": {
            "message_id": 2,
            "from": {"id": 123456, "first_name": "Test"},
            "chat": {"id": 123456, "type": "private"},
            "text": "/invoices"
        }
    }
    resp = client.post("/api/v1/telegram/webhook", json=payload)
    assert resp.status_code == 200
    assert mock_send.called
    sent_text = mock_send.call_args[0][1]
    assert "INV-2026-1041" in sent_text

@patch.object(telegram_gateway, "send_message", new_callable=AsyncMock)
def test_telegram_webhook_reconcile_command(mock_send):
    mock_send.return_value = True
    payload = {
        "update_id": 1003,
        "message": {
            "message_id": 3,
            "from": {"id": 123456, "first_name": "Test"},
            "chat": {"id": 123456, "type": "private"},
            "text": "/reconcile INV-2026-1041"
        }
    }
    resp = client.post("/api/v1/telegram/webhook", json=payload)
    assert resp.status_code == 200
    assert mock_send.called
    sent_text = mock_send.call_args[0][1]
    assert "3-Way Reconciliation" in sent_text

@patch.object(telegram_gateway, "send_message", new_callable=AsyncMock)
def test_telegram_webhook_simulate_command(mock_send):
    mock_send.return_value = True
    payload = {
        "update_id": 1004,
        "message": {
            "message_id": 4,
            "from": {"id": 123456, "first_name": "Test"},
            "chat": {"id": 123456, "type": "private"},
            "text": "/simulate"
        }
    }
    resp = client.post("/api/v1/telegram/webhook", json=payload)
    assert resp.status_code == 200
    assert mock_send.called
    sent_text = mock_send.call_args[0][1]
    assert "Switch Collaborative Scenario Completed" in sent_text

@patch.object(telegram_gateway, "send_message", new_callable=AsyncMock)
def test_telegram_broadcast_endpoint(mock_send):
    mock_send.return_value = True
    _save_subscriber(998877)
    
    resp = client.post("/api/v1/telegram/broadcast", json={
        "message": "🚨 Critical AP exception detected on INV-2026-1042"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "broadcast_sent"
    assert data["subscribers_count"] >= 1

