import os
import csv
import logging
from decimal import Decimal
from typing import Dict, Any, List
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
    DeliveryChallan,
    PriceListItem,
    VendorHistory,
    RoomRule,
    BenchmarkRole,
    ScriptedHumanReply,
    BenchmarkAnswerKey,
    Document,
    utcnow_iso
)
from backend.app.services.matching_engine import normalize_invoice_number, run_three_way_match
from backend.app.services.audit_service import log_audit_event

logger = logging.getLogger("invoiceops.ap_data")

def find_ap_data_dir() -> str:
    possible_paths = [
        "data/ap-data",
        "../data/ap-data",
        "../../data/ap-data",
        "fixtures/ap-data",
        "C:/Users/MS/Downloads/files (1)/ap-data/ap-data"
    ]
    for p in possible_paths:
        if os.path.exists(p) and os.path.isdir(p):
            return os.path.abspath(p)
    return os.path.abspath("data/ap-data")


def find_answer_key_path() -> str:
    possible_paths = [
        "data/answer_key.csv",
        "../data/answer_key.csv",
        "../../data/answer_key.csv",
        "fixtures/answer_key.csv",
        "C:/Users/MS/Downloads/files (1)/answer_key.csv"
    ]
    for p in possible_paths:
        if os.path.exists(p) and os.path.isfile(p):
            return os.path.abspath(p)
    return os.path.abspath("data/answer_key.csv")


def feed_ap_data(db: Session, run_matches: bool = True) -> Dict[str, int]:
    """
    Ingests the official AP exception benchmark dataset (vendors, po_lines, goods_receipts,
    delivery_challans, invoice_headers, invoice_lines, price_list, roles, room_rules,
    scripted_human_replies, vendor_history, and answer_key) into InvoiceOps SQLite database.
    """
    Base.metadata.create_all(bind=engine)
    data_dir = find_ap_data_dir()
    answer_key_file = find_answer_key_path()

    logger.info(f"Feeding AP data from {data_dir}...")
    counts = {
        "vendors": 0,
        "purchase_orders": 0,
        "po_lines": 0,
        "goods_receipts": 0,
        "delivery_challans": 0,
        "price_list": 0,
        "invoices": 0,
        "invoice_lines": 0,
        "vendor_history": 0,
        "roles": 0,
        "room_rules": 0,
        "scripted_replies": 0,
        "answer_keys": 0
    }

    # 1. Vendors
    v_path = os.path.join(data_dir, "vendors.csv")
    if os.path.exists(v_path):
        with open(v_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row["vendor_id"].strip()
                v = db.query(Vendor).filter(Vendor.id == vid).first()
                if not v:
                    v = Vendor(
                        id=vid,
                        legal_name=row.get("vendor_name", vid),
                        display_name=row.get("vendor_name", vid),
                        currency="INR",
                        is_active=1
                    )
                    db.add(v)
                    counts["vendors"] += 1
        db.flush()

    # 2. PO Lines & Purchase Orders
    po_path = os.path.join(data_dir, "po_lines.csv")
    if os.path.exists(po_path):
        with open(po_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                po_id = row["po_id"].strip()
                po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
                if not po:
                    po = PurchaseOrder(
                        id=po_id,
                        vendor_id=row["vendor_id"].strip(),
                        currency="INR",
                        status="open",
                        created_at=row.get("po_date", utcnow_iso())
                    )
                    db.add(po)
                    db.flush()
                    counts["purchase_orders"] += 1

                line_no = int(row["line_no"])
                pol_id = f"{po_id}-{line_no}"
                pol = db.query(PurchaseOrderLine).filter(PurchaseOrderLine.id == pol_id).first()
                if not pol:
                    pol = PurchaseOrderLine(
                        id=pol_id,
                        purchase_order_id=po_id,
                        line_number=line_no,
                        sku=row.get("sku", "").strip(),
                        description=row.get("description", "").strip(),
                        ordered_qty=str(Decimal(row.get("qty_ordered", "0"))),
                        unit_price=str(Decimal(row.get("unit_price_inr", "0.00"))),
                        uom=row.get("uom", "EA").strip()
                    )
                    db.add(pol)
                    counts["po_lines"] += 1
        db.flush()

    # 3. Goods Receipts
    grn_path = os.path.join(data_dir, "goods_receipts.csv")
    if os.path.exists(grn_path):
        with open(grn_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                grn_id = row["grn_id"].strip()
                po_id = row["po_id"].strip()
                grn = db.query(GoodsReceipt).filter(GoodsReceipt.id == grn_id).first()
                if not grn:
                    grn = GoodsReceipt(
                        id=grn_id,
                        purchase_order_id=po_id,
                        status="accepted",
                        received_at=row.get("receipt_date", utcnow_iso())
                    )
                    db.add(grn)
                    db.flush()
                    counts["goods_receipts"] += 1

                line_no = int(row["line_no"])
                grnl_id = f"{grn_id}-{line_no}"
                pol_id = f"{po_id}-{line_no}"
                grnl = db.query(GoodsReceiptLine).filter(GoodsReceiptLine.id == grnl_id).first()
                if not grnl:
                    grnl = GoodsReceiptLine(
                        id=grnl_id,
                        goods_receipt_id=grn_id,
                        po_line_id=pol_id,
                        accepted_qty=str(Decimal(row.get("qty_received", "0"))),
                        rejected_qty="0"
                    )
                    db.add(grnl)
        db.flush()

    # 4. Delivery Challans
    dc_path = os.path.join(data_dir, "delivery_challans.csv")
    if os.path.exists(dc_path):
        with open(dc_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row["challan_no"].strip()
                dc = db.query(DeliveryChallan).filter(DeliveryChallan.id == cid).first()
                if not dc:
                    dc = DeliveryChallan(
                        id=cid,
                        po_id=row["po_id"].strip(),
                        vendor_id=row["vendor_id"].strip(),
                        sku=row["sku"].strip(),
                        uom=row["uom"].strip(),
                        qty_dispatched=str(Decimal(row.get("qty_dispatched", "0"))),
                        dispatch_date=row.get("dispatch_date", "")
                    )
                    db.add(dc)
                    counts["delivery_challans"] += 1
        db.flush()

    # 5. Price List
    pl_path = os.path.join(data_dir, "price_list.csv")
    if os.path.exists(pl_path):
        with open(pl_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row["vendor_id"].strip()
                sku = row["sku"].strip()
                eff = row.get("effective_from", "")
                existing = db.query(PriceListItem).filter(
                    PriceListItem.vendor_id == vid,
                    PriceListItem.sku == sku,
                    PriceListItem.effective_from == eff
                ).first()
                if not existing:
                    item = PriceListItem(
                        vendor_id=vid,
                        sku=sku,
                        description=row.get("description", "").strip(),
                        uom=row.get("uom", "").strip(),
                        unit_price_inr=str(Decimal(row.get("unit_price_inr", "0.00"))),
                        effective_from=eff,
                        effective_to=row.get("effective_to", "") or None,
                        note=row.get("note", "") or None
                    )
                    db.add(item)
                    counts["price_list"] += 1
        db.flush()

    # 6. Invoices (Headers & Lines)
    inv_h_path = os.path.join(data_dir, "invoice_headers.csv")
    new_invoices = []
    if os.path.exists(inv_h_path):
        with open(inv_h_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                inv_id = row["invoice_id"].strip()
                inv = db.query(Invoice).filter(Invoice.id == inv_id).first()
                if not inv:
                    subtotal = Decimal(row.get("subtotal_inr", "0.00"))
                    gst = Decimal(row.get("gst_inr", "0.00"))
                    total = Decimal(row.get("total_inr", "0.00"))
                    status = row.get("status", "pending_match").strip()

                    inv = Invoice(
                        id=inv_id,
                        vendor_id=row["vendor_id"].strip(),
                        invoice_number=row["invoice_no"].strip(),
                        normalized_invoice_number=normalize_invoice_number(row["invoice_no"].strip()),
                        invoice_date=row.get("invoice_date", ""),
                        purchase_order_id=row.get("po_id", "").strip() or None,
                        currency="INR",
                        subtotal=str(subtotal),
                        tax_total=str(gst),
                        invoice_total=str(total),
                        status=status,
                        created_by="ap_data_feed"
                    )
                    db.add(inv)
                    db.flush()
                    counts["invoices"] += 1
                    if status != "paid":
                        new_invoices.append(inv_id)
        db.flush()

    # Invoice Lines
    inv_l_path = os.path.join(data_dir, "invoice_lines.csv")
    if os.path.exists(inv_l_path):
        with open(inv_l_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                inv_id = row["invoice_id"].strip()
                line_no = int(row["line_no"])
                inl_id = f"{inv_id}-{line_no}"
                inl = db.query(InvoiceLine).filter(InvoiceLine.id == inl_id).first()
                if not inl:
                    qty = Decimal(row.get("qty_invoiced", "0"))
                    rate = Decimal(row.get("unit_price_inr", "0.00"))
                    net = Decimal(row.get("line_amount_inr", "0.00"))
                    tax_rate = Decimal("0.18")
                    tax = net * tax_rate
                    gross = net + tax

                    inl = InvoiceLine(
                        id=inl_id,
                        invoice_id=inv_id,
                        line_number=line_no,
                        sku=row.get("sku", "").strip() or None,
                        description=row.get("description", "").strip(),
                        uom=row.get("uom", "EA").strip(),
                        quantity=str(qty),
                        unit_price=str(rate),
                        net_amount=str(net),
                        tax_rate=str(tax_rate),
                        tax_amount=str(tax),
                        gross_amount=str(gross),
                        source_page=1,
                        confidence="0.98"
                    )
                    db.add(inl)
                    counts["invoice_lines"] += 1
        db.flush()

    # 7. Vendor History
    vh_path = os.path.join(data_dir, "vendor_history.csv")
    if os.path.exists(vh_path):
        with open(vh_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                hid = row["history_id"].strip()
                vh = db.query(VendorHistory).filter(VendorHistory.id == hid).first()
                if not vh:
                    vh = VendorHistory(
                        id=hid,
                        vendor_id=row["vendor_id"].strip(),
                        date=row.get("date", ""),
                        issue_type=row.get("issue_type", ""),
                        amount_inr=str(Decimal(row.get("amount_inr", "0.00"))),
                        resolution=row.get("resolution", ""),
                        resolved_by=row.get("resolved_by", "")
                    )
                    db.add(vh)
                    counts["vendor_history"] += 1
        db.flush()

    # 8. Room Rules
    rr_path = os.path.join(data_dir, "room_rules.csv")
    if os.path.exists(rr_path):
        with open(rr_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rid = row["rule_id"].strip()
                rr = db.query(RoomRule).filter(RoomRule.id == rid).first()
                if not rr:
                    rr = RoomRule(
                        id=rid,
                        name=row.get("name", "").strip(),
                        text=row.get("text", "").strip()
                    )
                    db.add(rr)
                    counts["room_rules"] += 1
        db.flush()

    # 9. Roles
    r_path = os.path.join(data_dir, "roles.csv")
    if os.path.exists(r_path):
        with open(r_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                role_id = row["role"].strip()
                r = db.query(BenchmarkRole).filter(BenchmarkRole.id == role_id).first()
                if not r:
                    r = BenchmarkRole(
                        id=role_id,
                        person=row.get("person", "").strip(),
                        chat_username=row.get("chat_username", "").strip() or None,
                        authority=row.get("authority", "").strip()
                    )
                    db.add(r)
                    counts["roles"] += 1
        db.flush()

    # 10. Scripted Human Replies
    shr_path = os.path.join(data_dir, "scripted_human_replies.csv")
    if os.path.exists(shr_path):
        with open(shr_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                inv_id = row["invoice_id"].strip()
                role = row["role"].strip()
                q = row["question"].strip()
                existing = db.query(ScriptedHumanReply).filter(
                    ScriptedHumanReply.invoice_id == inv_id,
                    ScriptedHumanReply.role == role,
                    ScriptedHumanReply.question == q
                ).first()
                if not existing:
                    shr = ScriptedHumanReply(
                        invoice_id=inv_id,
                        role=role,
                        question=q,
                        scripted_reply=row.get("scripted_reply", "").strip()
                    )
                    db.add(shr)
                    counts["scripted_replies"] += 1
        db.flush()

    # 11. Answer Key
    if os.path.exists(answer_key_file):
        with open(answer_key_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sc = row["scenario"].strip()
                inv_id = row["invoice_id"].strip()
                existing = db.query(BenchmarkAnswerKey).filter(
                    BenchmarkAnswerKey.scenario == sc,
                    BenchmarkAnswerKey.invoice_id == inv_id
                ).first()
                if not existing:
                    ak = BenchmarkAnswerKey(
                        scenario=sc,
                        invoice_id=inv_id,
                        invoice_no=row.get("invoice_no", "").strip(),
                        expected_route=row.get("expected_route", "").strip(),
                        expected_cause=row.get("expected_cause", "").strip() or None,
                        expected_resolution=row.get("expected_resolution", "").strip() or None,
                        deciding_role=row.get("deciding_role", "").strip() or None,
                        disputed_amount_inr_pre_gst=row.get("disputed_amount_inr_pre_gst", "").strip() or None,
                        max_human_questions=int(row["max_human_questions"]) if row.get("max_human_questions") else 0,
                        key_evidence=row.get("key_evidence", "").strip() or None,
                        trap=row.get("trap", "").strip() or None
                    )
                    db.add(ak)
                    counts["answer_keys"] += 1
        db.flush()

    db.commit()

    # 12. Run initial matching on pending invoices if requested
    if run_matches:
        for inv_id in new_invoices:
            try:
                run_three_way_match(db, inv_id, executed_by="ap_benchmark_seeder")
            except Exception as e:
                logger.warning(f"Initial match error on {inv_id}: {e}")

    logger.info(f"AP data feed complete: {counts}")
    return counts
