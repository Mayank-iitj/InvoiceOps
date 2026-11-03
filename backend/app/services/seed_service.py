import os
import json
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.database import engine, Base
from backend.app.models.all_models import (
    Vendor,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    Invoice,
    InvoiceLine,
    Document,
    MatchRun,
    ExceptionRecord,
    Approval,
    PaymentReadyRecord,
    AuditEvent,
    IdempotencyRecord,
    Extraction,
    ResolutionProposal,
    gen_uuid,
    utcnow_iso,
)
from backend.app.services.matching_engine import normalize_invoice_number, run_three_way_match
from backend.app.services.audit_service import log_audit_event

def find_fixtures_dir() -> str:
    possible_paths = [
        "invoiceops_submission_pack/fixtures",
        "../invoiceops_submission_pack/fixtures",
        "fixtures",
        "../../invoiceops_submission_pack/fixtures",
    ]
    for p in possible_paths:
        if os.path.exists(p) and os.path.isdir(p):
            return p
    return "invoiceops_submission_pack/fixtures"

def reset_database():
    """Drops and recreates all database tables."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_database(db: Session, run_initial_match: bool = True) -> dict:
    """Populates database with synthetic demo fixtures."""
    Base.metadata.create_all(bind=engine)
    fixtures_dir = find_fixtures_dir()

    # 1. Vendor
    vendor_file = os.path.join(fixtures_dir, "vendor.json")
    if os.path.exists(vendor_file):
        with open(vendor_file, "r") as f:
            v_data = json.load(f)
            v = db.query(Vendor).filter(Vendor.id == v_data["vendor_id"]).first()
            if not v:
                v = Vendor(
                    id=v_data["vendor_id"],
                    legal_name=v_data.get("legal_name", "Northstar Components Pvt Ltd"),
                    display_name=v_data.get("display_name", "Northstar Components"),
                    currency=v_data.get("currency", "INR"),
                    is_active=1 if v_data.get("is_active", True) else 0,
                    version=1,
                    created_at=utcnow_iso(),
                    updated_at=utcnow_iso(),
                )
                db.add(v)
                db.flush()

    # 2. Purchase Order
    po_file = os.path.join(fixtures_dir, "purchase_order.json")
    if os.path.exists(po_file):
        with open(po_file, "r") as f:
            po_data = json.load(f)
            po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_data["po_id"]).first()
            if not po:
                po = PurchaseOrder(
                    id=po_data["po_id"],
                    vendor_id=po_data["vendor_id"],
                    currency=po_data.get("currency", "INR"),
                    status=po_data.get("status", "open"),
                    version=1,
                    created_at=utcnow_iso(),
                    updated_at=utcnow_iso(),
                )
                db.add(po)
                db.flush()

                for idx, line in enumerate(po_data.get("lines", [])):
                    pol = PurchaseOrderLine(
                        id=line.get("po_line_id", f"POL-{idx+1}"),
                        purchase_order_id=po.id,
                        line_number=idx + 1,
                        sku=line.get("sku"),
                        description=line.get("description", "Item"),
                        ordered_qty=str(line.get("ordered_qty", "0")),
                        unit_price=str(line.get("unit_price", "0.00")),
                        uom=line.get("uom", "each"),
                    )
                    db.add(pol)
                db.flush()

    # 3. Goods Receipts
    grn_file = os.path.join(fixtures_dir, "goods_receipts.json")
    if os.path.exists(grn_file):
        with open(grn_file, "r") as f:
            grns_data = json.load(f)
            for g_data in grns_data:
                grn = db.query(GoodsReceipt).filter(GoodsReceipt.id == g_data["grn_id"]).first()
                if not grn:
                    grn = GoodsReceipt(
                        id=g_data["grn_id"],
                        purchase_order_id=g_data["po_id"],
                        status=g_data.get("status", "accepted"),
                        received_at=g_data.get("received_at", utcnow_iso()),
                        version=1,
                        created_at=utcnow_iso(),
                    )
                    db.add(grn)
                    db.flush()

                    for gl in g_data.get("lines", []):
                        grnl = GoodsReceiptLine(
                            id=gen_uuid(),
                            goods_receipt_id=grn.id,
                            po_line_id=gl.get("po_line_id"),
                            accepted_qty=str(gl.get("accepted_qty", "0")),
                            rejected_qty=str(gl.get("rejected_qty", "0")),
                        )
                        db.add(grnl)
                    db.flush()

    # 4. Invoices
    invoice_fixtures = [
        "invoice_valid.json",
        "invoice_quantity_mismatch.json",
        "invoice_duplicate.json",
        "invoice_price_mismatch.json",
    ]

    seeded_invoices = []
    for inv_file_name in invoice_fixtures:
        inv_path = os.path.join(fixtures_dir, inv_file_name)
        if not os.path.exists(inv_path):
            continue
        with open(inv_path, "r") as f:
            inv_data = json.load(f)
            inv_id = inv_data["invoice_id"]
            existing = db.query(Invoice).filter(Invoice.id == inv_id).first()
            if not existing:
                inv = Invoice(
                    id=inv_id,
                    vendor_id=inv_data["vendor_id"],
                    invoice_number=inv_data["invoice_number"],
                    normalized_invoice_number=normalize_invoice_number(inv_data["invoice_number"]),
                    invoice_date=inv_data.get("invoice_date", "2026-10-27"),
                    purchase_order_id=inv_data.get("po_id"),
                    currency=inv_data.get("currency", "INR"),
                    subtotal=str(inv_data.get("subtotal", "0.00")),
                    tax_total=str(inv_data.get("tax_total", "0.00")),
                    invoice_total=str(inv_data.get("invoice_total", "0.00")),
                    status="received",
                    version=1,
                    created_by="system_seeder",
                    created_at=utcnow_iso(),
                    updated_at=utcnow_iso(),
                )
                db.add(inv)
                db.flush()

                # Add lines
                for idx, line in enumerate(inv_data.get("lines", [])):
                    il = InvoiceLine(
                        id=gen_uuid(),
                        invoice_id=inv.id,
                        line_number=idx + 1,
                        sku=line.get("sku"),
                        description=line.get("description", "Item"),
                        quantity=str(line.get("quantity", "0")),
                        unit_price=str(line.get("unit_price", "0.00")),
                        net_amount=str(line.get("net_amount", "0.00")),
                        tax_rate=str(line.get("tax_rate", "18.00")),
                        tax_amount=str(line.get("tax_amount", "0.00")),
                        gross_amount=str(line.get("gross_amount", "0.00")),
                        confidence="0.98",
                    )
                    db.add(il)
                db.flush()

                # Add mock document record
                doc = Document(
                    id=gen_uuid(),
                    invoice_id=inv.id,
                    original_filename=f"{inv.invoice_number.replace('/', '_')}.pdf",
                    storage_path=f"data/uploads/{inv.id}.pdf",
                    mime_type="application/pdf",
                    size_bytes=1024 * 45,
                    sha256=f"hash_synthetic_{inv.id.lower()}",
                    document_type="supplier_invoice",
                    created_by="system_seeder",
                    created_at=utcnow_iso(),
                )
                db.add(doc)
                db.flush()

                log_audit_event(
                    db=db,
                    actor_id="system_seeder",
                    actor_type="system",
                    action="INVOICE_CREATED",
                    entity_type="Invoice",
                    entity_id=inv.id,
                    invoice_id=inv.id,
                    after_state="received",
                    reason="Synthetic demo case seeded",
                )
                seeded_invoices.append(inv.id)

    db.commit()

    # Run match on seeded invoices if requested
    if run_initial_match:
        for i_id in seeded_invoices:
            try:
                run_three_way_match(db, i_id, executed_by="system_seeder")
                db.commit()
            except Exception as e:
                db.rollback()

    return {
        "status": "success",
        "vendor": "VND-001",
        "po": "PO-2026-0082",
        "grn": "GRN-2026-0041",
        "invoices_seeded": seeded_invoices,
    }
