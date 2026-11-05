import sys
import os
import json
import argparse
from typing import Optional

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, engine, Base
from backend.app.models.all_models import (
    Invoice,
    Document,
    MatchRun,
    ExceptionRecord,
    Extraction,
    Approval,
    PaymentReadyRecord,
)
from backend.app.services.seed_service import seed_database, reset_database
from backend.app.services.matching_engine import run_three_way_match
from backend.app.services.extraction_service import create_extraction_proposal, extract_text_from_pdf
from backend.app.services.approval_service import process_approval_decision, create_payment_ready_record

def cmd_seed(args):
    db = SessionLocal()
    try:
        res = seed_database(db, run_initial_match=True)
        print(json.dumps(res, indent=2))
    finally:
        db.close()

def cmd_reset(args):
    reset_database()
    db = SessionLocal()
    try:
        res = seed_database(db, run_initial_match=True)
        print("Database reset and seeded successfully:")
        print(json.dumps(res, indent=2))
    finally:
        db.close()

def cmd_case_show(args):
    db = SessionLocal()
    try:
        inv = db.query(Invoice).filter(Invoice.id == args.id).first()
        if not inv:
            print(f"Error: Invoice '{args.id}' not found.", file=sys.stderr)
            sys.exit(1)

        latest_run = (
            db.query(MatchRun)
            .filter(MatchRun.invoice_id == inv.id)
            .order_by(MatchRun.created_at.desc())
            .first()
        )

        open_exc = (
            db.query(ExceptionRecord)
            .filter(ExceptionRecord.invoice_id == inv.id, ExceptionRecord.status == "open")
            .all()
        )

        out = {
            "invoice_id": inv.id,
            "vendor_id": inv.vendor_id,
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date,
            "po_id": inv.purchase_order_id,
            "currency": inv.currency,
            "invoice_total": inv.invoice_total,
            "status": inv.status,
            "version": inv.version,
            "latest_match_run": {
                "id": latest_run.id if latest_run else None,
                "overall_status": latest_run.overall_status if latest_run else None,
            } if latest_run else None,
            "open_exceptions": [
                {
                    "id": e.id,
                    "code": e.code,
                    "owner_role": e.owner_role,
                    "description": e.description,
                    "expected": e.expected_value,
                    "actual": e.actual_value,
                }
                for e in open_exc
            ],
            "lines_count": len(inv.lines),
        }
        print(json.dumps(out, indent=2))
    finally:
        db.close()

def cmd_doc_get_text(args):
    db = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == args.document_id).first()
        if not doc:
            print(f"Error: Document '{args.document_id}' not found.", file=sys.stderr)
            sys.exit(1)

        text = ""
        if os.path.exists(doc.storage_path):
            text = extract_text_from_pdf(doc.storage_path)

        out = {
            "document_id": doc.id,
            "invoice_id": doc.invoice_id,
            "filename": doc.original_filename,
            "sha256": doc.sha256,
            "size_bytes": doc.size_bytes,
            "text": text,
        }
        print(json.dumps(out, indent=2))
    finally:
        db.close()

def cmd_extraction_propose(args):
    db = SessionLocal()
    try:
        with open(args.json_file, "r") as f:
            data = json.load(f)

        extraction = create_extraction_proposal(
            db=db,
            invoice_id=args.case_id,
            extractor_actor_id=args.actor or "invoiceops-intake",
            document_id=data.get("document_id", "DOC-CLI"),
            fields=data.get("fields", []),
            lines=data.get("lines", []),
        )
        db.commit()
        print(json.dumps({
            "extraction_id": extraction.id,
            "status": extraction.status,
            "requires_human_review": extraction.status == "needs_review",
        }, indent=2))
    finally:
        db.close()

def cmd_match_run(args):
    db = SessionLocal()
    try:
        match_run, exceptions = run_three_way_match(
            db=db,
            invoice_id=args.case_id,
            executed_by=args.actor or "invoiceops-reconcile",
        )
        db.commit()

        checks = json.loads(match_run.checks_json)
        print(json.dumps({
            "match_run_id": match_run.id,
            "invoice_id": match_run.invoice_id,
            "overall_status": match_run.overall_status,
            "checks": checks,
            "open_exceptions_count": len(exceptions),
        }, indent=2))
    finally:
        db.close()

def cmd_match_latest(args):
    db = SessionLocal()
    try:
        run = (
            db.query(MatchRun)
            .filter(MatchRun.invoice_id == args.case_id)
            .order_by(MatchRun.created_at.desc())
            .first()
        )
        if not run:
            print(f"Error: No match runs found for '{args.case_id}'.", file=sys.stderr)
            sys.exit(1)

        checks = json.loads(run.checks_json)
        print(json.dumps({
            "match_run_id": run.id,
            "overall_status": run.overall_status,
            "policy_version": run.policy_version,
            "checks": checks,
            "created_at": run.created_at,
        }, indent=2))
    finally:
        db.close()

def cmd_exception_list(args):
    db = SessionLocal()
    try:
        exceptions = (
            db.query(ExceptionRecord)
            .filter(ExceptionRecord.invoice_id == args.case_id)
            .all()
        )
        out = [
            {
                "id": e.id,
                "code": e.code,
                "severity": e.severity,
                "status": e.status,
                "owner_role": e.owner_role,
                "description": e.description,
                "expected": e.expected_value,
                "actual": e.actual_value,
            }
            for e in exceptions
        ]
        print(json.dumps(out, indent=2))
    finally:
        db.close()

def cmd_telegram_status(args):
    import asyncio
    from backend.app.services.telegram_service import telegram_gateway, _load_subscribers
    from backend.app.config import settings
    configured = telegram_gateway.is_configured()
    bot_info = asyncio.run(telegram_gateway.get_me()) if configured else {}
    subs = _load_subscribers()
    print(json.dumps({
        "status": "connected" if configured and "id" in bot_info else ("configured" if configured else "disabled"),
        "bot_username": settings.TELEGRAM_BOT_USERNAME,
        "polling_active": telegram_gateway._is_running,
        "subscribers_count": len(subs),
        "bot_details": bot_info
    }, indent=2))

def cmd_telegram_poll(args):
    import asyncio
    from backend.app.services.telegram_service import telegram_gateway
    print(f"Starting Telegram Gateway polling for {telegram_gateway.bot_username}...")
    try:
        asyncio.run(telegram_gateway.poll_updates())
    except KeyboardInterrupt:
        print("\nStopping Telegram Gateway polling.")

def cmd_telegram_set_webhook(args):
    import asyncio
    from backend.app.services.telegram_service import telegram_gateway
    url = args.url
    print(f"Setting Telegram webhook to: {url}")
    res = asyncio.run(telegram_gateway.set_webhook(url))
    print(json.dumps(res, indent=2))

def cmd_telegram_delete_webhook(args):
    import asyncio
    from backend.app.services.telegram_service import telegram_gateway
    print("Deleting Telegram webhook...")
    res = asyncio.run(telegram_gateway.delete_webhook())
    print(json.dumps(res, indent=2))

def cmd_telegram_webhook_info(args):
    import asyncio
    from backend.app.services.telegram_service import telegram_gateway
    res = asyncio.run(telegram_gateway.get_webhook_info())
    print(json.dumps(res, indent=2))

def cmd_feed_ap_data(args):
    from backend.app.database import SessionLocal
    from backend.app.services.ap_data_loader import feed_ap_data
    db = SessionLocal()
    try:
        res = feed_ap_data(db, run_matches=True)
        print(json.dumps({"status": "ap_data_fed", "counts": res}, indent=2))
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(prog="invoiceops", description="InvoiceOps CLI tool for AP operations and Switch agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Seed
    p_seed = subparsers.add_parser("seed", help="Seed database with synthetic demo fixtures")
    p_seed.set_defaults(func=cmd_seed)

    # Reset
    p_reset = subparsers.add_parser("reset", help="Drop, recreate and seed database")
    p_reset.set_defaults(func=cmd_reset)

    # Case
    p_case = subparsers.add_parser("case", help="Case management")
    case_subs = p_case.add_subparsers(dest="case_command", required=True)
    p_case_show = case_subs.add_parser("show", help="Show case detail")
    p_case_show.add_argument("id", help="Invoice case ID")
    p_case_show.set_defaults(func=cmd_case_show)

    # Document
    p_doc = subparsers.add_parser("document", help="Document operations")
    doc_subs = p_doc.add_subparsers(dest="doc_command", required=True)
    p_doc_text = doc_subs.add_parser("get-text", help="Extract and read document text")
    p_doc_text.add_argument("document_id", help="Document ID")
    p_doc_text.set_defaults(func=cmd_doc_get_text)

    # Extraction
    p_ext = subparsers.add_parser("extraction", help="Extraction operations")
    ext_subs = p_ext.add_subparsers(dest="ext_command", required=True)
    p_ext_prop = ext_subs.add_parser("propose", help="Propose extraction")
    p_ext_prop.add_argument("case_id", help="Invoice case ID")
    p_ext_prop.add_argument("--json", dest="json_file", required=True, help="Path to extraction JSON file")
    p_ext_prop.add_argument("--actor", default="invoiceops-intake", help="Actor ID")
    p_ext_prop.set_defaults(func=cmd_extraction_propose)

    # Match
    p_match = subparsers.add_parser("match", help="Matching operations")
    match_subs = p_match.add_subparsers(dest="match_command", required=True)
    p_match_run = match_subs.add_parser("run", help="Run 3-way match")
    p_match_run.add_argument("case_id", help="Invoice case ID")
    p_match_run.add_argument("--actor", default="invoiceops-reconcile", help="Actor ID")
    p_match_run.set_defaults(func=cmd_match_run)

    p_match_latest = match_subs.add_parser("latest", help="Show latest match run")
    p_match_latest.add_argument("case_id", help="Invoice case ID")
    p_match_latest.set_defaults(func=cmd_match_latest)

    # Exception
    p_exc = subparsers.add_parser("exception", help="Exception operations")
    exc_subs = p_exc.add_subparsers(dest="exc_command", required=True)
    p_exc_list = exc_subs.add_parser("list", help="List exceptions for case")
    p_exc_list.add_argument("case_id", help="Invoice case ID")
    p_exc_list.set_defaults(func=cmd_exception_list)

    # Telegram Gateway
    p_tg = subparsers.add_parser("telegram", help="Telegram Chat Gateway operations")
    tg_subs = p_tg.add_subparsers(dest="tg_command", required=True)
    p_tg_status = tg_subs.add_parser("status", help="Show Telegram bot connectivity status")
    p_tg_status.set_defaults(func=cmd_telegram_status)
    p_tg_poll = tg_subs.add_parser("poll", help="Run Telegram bot long polling worker")
    p_tg_poll.set_defaults(func=cmd_telegram_poll)
    p_tg_set_wh = tg_subs.add_parser("set-webhook", help="Set Telegram webhook URL")
    p_tg_set_wh.add_argument("url", help="Public HTTPS webhook URL")
    p_tg_set_wh.set_defaults(func=cmd_telegram_set_webhook)
    p_tg_del_wh = tg_subs.add_parser("delete-webhook", help="Delete Telegram webhook")
    p_tg_del_wh.set_defaults(func=cmd_telegram_delete_webhook)
    p_tg_wh_info = tg_subs.add_parser("webhook-info", help="Get Telegram webhook status")
    p_tg_wh_info.set_defaults(func=cmd_telegram_webhook_info)

    # Feed AP Data
    p_feed = subparsers.add_parser("feed-ap-data", help="Ingest official AP exception benchmark dataset")
    p_feed.set_defaults(func=cmd_feed_ap_data)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

