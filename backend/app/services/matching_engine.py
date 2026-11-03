import re
import json
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.config import settings
from backend.app.models.all_models import (
    Invoice,
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceipt,
    GoodsReceiptLine,
    MatchRun,
    ExceptionRecord,
    Document,
    Extraction,
    gen_uuid,
    utcnow_iso,
)

def normalize_invoice_number(raw: str) -> str:
    """
    Unicode normalize, trim, uppercase, and remove whitespace, hyphens and slashes.
    e.g. 'NSC/1041/26' and 'NSC 1041-26' both become 'NSC104126'
    """
    if not raw:
        return ""
    norm = unicodedata.normalize("NFKC", raw.strip().upper())
    return re.sub(r"[\s\-\/\\]+", "", norm)

def to_decimal(val: Any) -> Decimal:
    if val is None or val == "":
        return Decimal("0.00")
    try:
        return Decimal(str(val).strip())
    except (InvalidOperation, ValueError):
        return Decimal("0.00")

def run_three_way_match(
    db: Session,
    invoice_id: str,
    executed_by: str = "system",
    policy_version: Optional[str] = None,
) -> Tuple[MatchRun, List[ExceptionRecord]]:
    policy_ver = policy_version or settings.POLICY_VERSION

    invoice: Optional[Invoice] = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")

    checks: List[Dict[str, Any]] = []
    blocking_exceptions_to_create: List[Dict[str, Any]] = []

    # 1. DUPLICATE CHECK
    # Check if a prior invoice already exists with same vendor_id and normalized_invoice_number
    normalized_num = normalize_invoice_number(invoice.invoice_number)
    duplicate_query = db.query(Invoice).filter(
        Invoice.id != invoice.id,
        Invoice.vendor_id == invoice.vendor_id,
        Invoice.normalized_invoice_number == normalized_num,
        (Invoice.created_at < invoice.created_at) | ((Invoice.created_at == invoice.created_at) & (Invoice.id < invoice.id)),
    ).first()

    # Also check document SHA-256 collisions with earlier documents
    doc_duplicate = None
    invoice_doc = db.query(Document).filter(Document.invoice_id == invoice.id).first()
    if invoice_doc and invoice_doc.sha256:
        doc_duplicate = db.query(Document).join(Invoice, Document.invoice_id == Invoice.id).filter(
            Document.invoice_id != invoice.id,
            Document.sha256 == invoice_doc.sha256,
            (Invoice.created_at < invoice.created_at) | ((Invoice.created_at == invoice.created_at) & (Invoice.id < invoice.id)),
        ).first()

    if duplicate_query or doc_duplicate:
        dup_target = duplicate_query.id if duplicate_query else (doc_duplicate.invoice_id if doc_duplicate else "unknown")
        checks.append({
            "code": "DUPLICATE_INVOICE",
            "status": "fail",
            "severity": "blocking",
            "message": f"Duplicate invoice detected. Matches existing invoice '{dup_target}'.",
            "expected": "unique vendor + invoice number and content hash",
            "actual": f"Collides with invoice {dup_target}",
            "source_refs": [f"invoice/{invoice.id}", f"invoice/{dup_target}"],
        })
        blocking_exceptions_to_create.append({
            "code": "DUPLICATE_INVOICE",
            "severity": "blocking",
            "owner_role": "ap_lead",
            "description": f"Invoice collides with existing case {dup_target} on normalized number or content hash.",
            "expected_value": "unique",
            "actual_value": f"duplicate of {dup_target}",
            "source_refs": [f"invoice/{invoice.id}", f"invoice/{dup_target}"],
        })
    else:
        checks.append({
            "code": "DUPLICATE_INVOICE",
            "status": "pass",
            "severity": "blocking",
            "message": "No duplicate vendor invoice or document checksum found.",
            "expected": "unique",
            "actual": "unique",
            "source_refs": [f"invoice/{invoice.id}"],
        })

    # 2. PURCHASE ORDER EXISTENCE & VENDOR CHECK
    po: Optional[PurchaseOrder] = None
    if invoice.purchase_order_id:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == invoice.purchase_order_id).first()

    if not invoice.purchase_order_id or not po:
        checks.append({
            "code": "PO_NOT_FOUND",
            "status": "fail",
            "severity": "blocking",
            "message": f"Purchase order '{invoice.purchase_order_id}' not found in supplier records.",
            "expected": "valid active PO",
            "actual": str(invoice.purchase_order_id),
            "source_refs": [f"invoice/{invoice.id}"],
        })
        blocking_exceptions_to_create.append({
            "code": "PO_NOT_FOUND",
            "severity": "blocking",
            "owner_role": "procurement_owner",
            "description": f"Referenced PO '{invoice.purchase_order_id}' could not be resolved.",
            "expected_value": "resolved PO",
            "actual_value": str(invoice.purchase_order_id),
            "source_refs": [f"invoice/{invoice.id}"],
        })
    else:
        checks.append({
            "code": "PO_NOT_FOUND",
            "status": "pass",
            "severity": "blocking",
            "message": f"Purchase order '{po.id}' resolved successfully.",
            "expected": str(po.id),
            "actual": str(po.id),
            "source_refs": [f"po/{po.id}"],
        })

        # Vendor match check
        if invoice.vendor_id != po.vendor_id:
            checks.append({
                "code": "VENDOR_MISMATCH",
                "status": "fail",
                "severity": "blocking",
                "message": f"Invoice vendor '{invoice.vendor_id}' does not match PO vendor '{po.vendor_id}'.",
                "expected": po.vendor_id,
                "actual": invoice.vendor_id,
                "source_refs": [f"invoice/{invoice.id}", f"po/{po.id}"],
            })
            blocking_exceptions_to_create.append({
                "code": "VENDOR_MISMATCH",
                "severity": "blocking",
                "owner_role": "procurement_owner",
                "description": f"Vendor mismatch between invoice ({invoice.vendor_id}) and PO ({po.vendor_id}).",
                "expected_value": po.vendor_id,
                "actual_value": invoice.vendor_id,
                "source_refs": [f"invoice/{invoice.id}", f"po/{po.id}"],
            })
        else:
            checks.append({
                "code": "VENDOR_MISMATCH",
                "status": "pass",
                "severity": "blocking",
                "message": f"Vendor '{invoice.vendor_id}' matches purchase order vendor.",
                "expected": po.vendor_id,
                "actual": invoice.vendor_id,
                "source_refs": [f"invoice/{invoice.id}", f"po/{po.id}"],
            })

        # Currency match check
        if invoice.currency != po.currency:
            checks.append({
                "code": "CURRENCY_MISMATCH",
                "status": "fail",
                "severity": "blocking",
                "message": f"Invoice currency '{invoice.currency}' does not match PO currency '{po.currency}'.",
                "expected": po.currency,
                "actual": invoice.currency,
                "source_refs": [f"invoice/{invoice.id}", f"po/{po.id}"],
            })
            blocking_exceptions_to_create.append({
                "code": "CURRENCY_MISMATCH",
                "severity": "blocking",
                "owner_role": "finance_approver",
                "description": f"Currency discrepancy: invoice ({invoice.currency}) vs PO ({po.currency}).",
                "expected_value": po.currency,
                "actual_value": invoice.currency,
                "source_refs": [f"invoice/{invoice.id}", f"po/{po.id}"],
            })
        else:
            checks.append({
                "code": "CURRENCY_MISMATCH",
                "status": "pass",
                "severity": "blocking",
                "message": f"Currency '{invoice.currency}' agrees across records.",
                "expected": po.currency,
                "actual": invoice.currency,
                "source_refs": [f"invoice/{invoice.id}", f"po/{po.id}"],
            })

    # 3. GOODS RECEIPT AND LINE LEVEL MATCHING
    # Gather GRNs for PO
    grn_version_str = "none"
    if po:
        grns = db.query(GoodsReceipt).filter(
            GoodsReceipt.purchase_order_id == po.id,
            GoodsReceipt.status == "accepted"
        ).all()
        if not grns:
            checks.append({
                "code": "GRN_MISSING",
                "status": "unknown",
                "severity": "blocking",
                "message": f"No accepted goods receipt found for purchase order '{po.id}'.",
                "expected": ">= 1 accepted GRN",
                "actual": "0 accepted GRNs",
                "source_refs": [f"po/{po.id}"],
            })
            blocking_exceptions_to_create.append({
                "code": "GRN_MISSING",
                "severity": "blocking",
                "owner_role": "procurement_owner",
                "description": f"Warehouse goods receipt record missing for PO '{po.id}'.",
                "expected_value": "accepted receipt",
                "actual_value": "none",
                "source_refs": [f"po/{po.id}"],
            })
        else:
            checks.append({
                "code": "GRN_MISSING",
                "status": "pass",
                "severity": "blocking",
                "message": f"Found {len(grns)} accepted goods receipt(s) for PO '{po.id}'.",
                "expected": ">= 1 accepted GRN",
                "actual": f"{len(grns)} accepted GRN(s)",
                "source_refs": [f"grn/{g.id}" for g in grns],
            })
            grn_version_str = ":".join(f"{g.id}-v{g.version}" for g in sorted(grns, key=lambda x: x.id))

        # Check line items
        po_lines_by_sku: Dict[str, PurchaseOrderLine] = {}
        po_lines_by_desc: Dict[str, PurchaseOrderLine] = {}
        for pol in po.lines:
            if pol.sku:
                po_lines_by_sku[pol.sku.strip().upper()] = pol
            po_lines_by_desc[pol.description.strip().lower()] = pol

        # Map each invoice line to PO line and compare
        for inv_line in invoice.lines:
            matched_pol: Optional[PurchaseOrderLine] = None
            if inv_line.sku and inv_line.sku.strip().upper() in po_lines_by_sku:
                matched_pol = po_lines_by_sku[inv_line.sku.strip().upper()]
            elif inv_line.description.strip().lower() in po_lines_by_desc:
                matched_pol = po_lines_by_desc[inv_line.description.strip().lower()]
            elif len(po.lines) == 1:
                # If single line PO, match directly
                matched_pol = po.lines[0]

            line_ref = f"inv_line/{inv_line.line_number}"

            if not matched_pol:
                checks.append({
                    "code": "PO_LINE_NOT_MATCHED",
                    "status": "fail",
                    "severity": "blocking",
                    "message": f"Line {inv_line.line_number} ('{inv_line.description}') could not be mapped to any PO line.",
                    "expected": "mapped PO line",
                    "actual": inv_line.sku or inv_line.description,
                    "source_refs": [line_ref],
                })
                blocking_exceptions_to_create.append({
                    "code": "PO_LINE_NOT_MATCHED",
                    "severity": "blocking",
                    "owner_role": "procurement_owner",
                    "description": f"Invoice line {inv_line.line_number} has no corresponding PO line item.",
                    "expected_value": "PO line match",
                    "actual_value": inv_line.sku or inv_line.description,
                    "source_refs": [line_ref],
                })
                continue

            po_line_ref = f"po/{po.id}/line/{matched_pol.line_number}"

            # Calculate total accepted quantity across all GRNs for this PO line
            total_accepted_qty = Decimal("0")
            grn_refs: List[str] = []
            for grn in grns:
                for grn_line in grn.lines:
                    if grn_line.po_line_id == matched_pol.id or grn_line.po_line_id == matched_pol.sku:
                        total_accepted_qty += to_decimal(grn_line.accepted_qty)
                        grn_refs.append(f"grn/{grn.id}")

            inv_qty = to_decimal(inv_line.quantity)

            # Check quantity
            if inv_qty > total_accepted_qty:
                checks.append({
                    "code": "QTY_EXCEEDS_RECEIVED",
                    "status": "fail",
                    "severity": "blocking",
                    "message": f"Invoice quantity ({inv_qty}) exceeds accepted received quantity ({total_accepted_qty}).",
                    "expected": str(total_accepted_qty),
                    "actual": str(inv_qty),
                    "source_refs": [line_ref, po_line_ref] + grn_refs,
                })
                blocking_exceptions_to_create.append({
                    "code": "QTY_EXCEEDS_RECEIVED",
                    "severity": "blocking",
                    "owner_role": "procurement_owner",
                    "description": f"Invoice line {inv_line.line_number} billed {inv_qty} units, but warehouse accepted only {total_accepted_qty} units.",
                    "expected_value": str(total_accepted_qty),
                    "actual_value": str(inv_qty),
                    "source_refs": [line_ref, po_line_ref] + grn_refs,
                })
            else:
                checks.append({
                    "code": "QTY_EXCEEDS_RECEIVED",
                    "status": "pass",
                    "severity": "blocking",
                    "message": f"Invoice quantity ({inv_qty}) is within accepted receipt quantity ({total_accepted_qty}).",
                    "expected": str(total_accepted_qty),
                    "actual": str(inv_qty),
                    "source_refs": [line_ref, po_line_ref] + grn_refs,
                })

            # Check unit price tolerance
            inv_unit_price = to_decimal(inv_line.unit_price)
            po_unit_price = to_decimal(matched_pol.unit_price)

            price_delta = abs(inv_unit_price - po_unit_price)
            # relative tolerance: 0.5% (0.005)
            rel_tolerance = po_unit_price * (settings.PRICE_VARIANCE_PERCENT / Decimal("100"))
            abs_tolerance = settings.PRICE_VARIANCE_ABSOLUTE # 1.00 INR
            allowed_delta = max(rel_tolerance, abs_tolerance)

            if price_delta > allowed_delta:
                checks.append({
                    "code": "PRICE_VARIANCE",
                    "status": "fail",
                    "severity": "blocking",
                    "message": f"Unit price ₹{inv_unit_price} exceeds PO price ₹{po_unit_price} by ₹{price_delta} (tolerance is ₹{allowed_delta:.2f}).",
                    "expected": str(po_unit_price),
                    "actual": str(inv_unit_price),
                    "source_refs": [line_ref, po_line_ref],
                })
                blocking_exceptions_to_create.append({
                    "code": "PRICE_VARIANCE",
                    "severity": "blocking",
                    "owner_role": "procurement_owner",
                    "description": f"Invoice line {inv_line.line_number} unit price ₹{inv_unit_price} exceeds PO price ₹{po_unit_price} beyond allowable tolerance.",
                    "expected_value": str(po_unit_price),
                    "actual_value": str(inv_unit_price),
                    "source_refs": [line_ref, po_line_ref],
                })
            else:
                checks.append({
                    "code": "PRICE_VARIANCE",
                    "status": "pass",
                    "severity": "blocking",
                    "message": f"Unit price ₹{inv_unit_price} matches PO unit price ₹{po_unit_price} within tolerance.",
                    "expected": str(po_unit_price),
                    "actual": str(inv_unit_price),
                    "source_refs": [line_ref, po_line_ref],
                })

    # 4. ARITHMETIC CONSISTENCY CHECKS
    # Line math: quantity * unit_price == net_amount
    for line in invoice.lines:
        line_ref = f"inv_line/{line.line_number}"
        qty = to_decimal(line.quantity)
        price = to_decimal(line.unit_price)
        calc_net = (qty * price).quantize(Decimal("0.01"))
        stated_net = to_decimal(line.net_amount) if line.net_amount else calc_net

        if abs(calc_net - stated_net) > Decimal("0.01"):
            checks.append({
                "code": "LINE_TOTAL_MISMATCH",
                "status": "fail",
                "severity": "blocking",
                "message": f"Line {line.line_number} calculation mismatch: {qty} * {price} = {calc_net}, but line net is {stated_net}.",
                "expected": str(calc_net),
                "actual": str(stated_net),
                "source_refs": [line_ref],
            })
            blocking_exceptions_to_create.append({
                "code": "LINE_TOTAL_MISMATCH",
                "severity": "blocking",
                "owner_role": "ap_clerk",
                "description": f"Invoice line {line.line_number} arithmetic mismatch between quantity, unit price and net amount.",
                "expected_value": str(calc_net),
                "actual_value": str(stated_net),
                "source_refs": [line_ref],
            })
        else:
            checks.append({
                "code": "LINE_TOTAL_MISMATCH",
                "status": "pass",
                "severity": "blocking",
                "message": f"Line {line.line_number} arithmetic is consistent ({qty} * {price} = {stated_net}).",
                "expected": str(calc_net),
                "actual": str(stated_net),
                "source_refs": [line_ref],
            })

    # Invoice total consistency: sum(lines net + tax) == invoice_total
    recomputed_subtotal = Decimal("0.00")
    recomputed_tax = Decimal("0.00")
    for line in invoice.lines:
        recomputed_subtotal += to_decimal(line.net_amount)
        if line.tax_amount:
            recomputed_tax += to_decimal(line.tax_amount)

    stated_total = to_decimal(invoice.invoice_total)
    expected_total = recomputed_subtotal + recomputed_tax

    if invoice.lines and abs(expected_total - stated_total) > Decimal("0.05"):
        checks.append({
            "code": "INVOICE_TOTAL_MISMATCH",
            "status": "fail",
            "severity": "blocking",
            "message": f"Invoice total ₹{stated_total} differs from sum of lines (subtotal ₹{recomputed_subtotal} + tax ₹{recomputed_tax} = ₹{expected_total}).",
            "expected": str(expected_total),
            "actual": str(stated_total),
            "source_refs": [f"invoice/{invoice.id}"],
        })
        blocking_exceptions_to_create.append({
            "code": "INVOICE_TOTAL_MISMATCH",
            "severity": "blocking",
            "owner_role": "ap_clerk",
            "description": f"Invoice total mismatch: stated total {stated_total} vs recomputed total {expected_total}.",
            "expected_value": str(expected_total),
            "actual_value": str(stated_total),
            "source_refs": [f"invoice/{invoice.id}"],
        })
    else:
        checks.append({
            "code": "INVOICE_TOTAL_MISMATCH",
            "status": "pass",
            "severity": "blocking",
            "message": f"Invoice total ₹{stated_total} equals sum of subtotal and tax.",
            "expected": str(expected_total if invoice.lines else stated_total),
            "actual": str(stated_total),
            "source_refs": [f"invoice/{invoice.id}"],
        })

    # 5. EXTRACTION CONFIDENCE CHECK
    latest_extraction = db.query(Extraction).filter(Extraction.invoice_id == invoice.id).order_by(Extraction.version.desc()).first()
    if latest_extraction and not latest_extraction.confirmed_by:
        try:
            payload = json.loads(latest_extraction.payload_json)
            fields = payload.get("fields", [])
            low_conf_fields = [
                f.get("field") for f in fields
                if f.get("confidence", 1.0) < settings.EXTRACTION_CONFIDENCE_THRESHOLD
            ]
            if low_conf_fields:
                checks.append({
                    "code": "LOW_EXTRACTION_CONFIDENCE",
                    "status": "unknown",
                    "severity": "blocking",
                    "message": f"Fields require human confirmation due to low extraction confidence: {', '.join(low_conf_fields)}",
                    "expected": f">= {settings.EXTRACTION_CONFIDENCE_THRESHOLD}",
                    "actual": "below threshold",
                    "source_refs": [f"extraction/{latest_extraction.id}"],
                })
                blocking_exceptions_to_create.append({
                    "code": "LOW_EXTRACTION_CONFIDENCE",
                    "severity": "blocking",
                    "owner_role": "ap_clerk",
                    "description": f"Low extraction confidence on critical fields: {', '.join(low_conf_fields)}.",
                    "expected_value": "human confirmed",
                    "actual_value": "unreviewed proposal",
                    "source_refs": [f"extraction/{latest_extraction.id}"],
                })
        except Exception:
            pass

    # DETERMINE OVERALL STATUS
    # Status:
    # PASS: all mandatory checks pass.
    # BLOCKED: at least one check fails.
    # NEEDS_HUMAN: at least one check is unknown and no check fails.
    has_fail = any(c["status"] == "fail" for c in checks)
    has_unknown = any(c["status"] == "unknown" for c in checks)

    if has_fail:
        overall_status = "BLOCKED"
    elif has_unknown:
        overall_status = "NEEDS_HUMAN"
    else:
        overall_status = "PASS"

    # PERSIST MATCH RUN
    match_run = MatchRun(
        id=gen_uuid(),
        invoice_id=invoice.id,
        invoice_version=invoice.version,
        po_version=po.version if po else None,
        grn_version_fingerprint=grn_version_str,
        policy_version=policy_ver,
        overall_status=overall_status,
        checks_json=json.dumps(checks),
        executed_by=executed_by,
        created_at=utcnow_iso(),
    )
    db.add(match_run)
    db.flush()

    # MANAGE EXCEPTIONS
    # Close old open exceptions for checks that are now passing
    existing_exceptions = db.query(ExceptionRecord).filter(
        ExceptionRecord.invoice_id == invoice.id,
        ExceptionRecord.status == "open",
    ).all()

    created_exceptions: List[ExceptionRecord] = []
    # If duplicate_invoice was flagged, update invoice status to duplicate_blocked
    is_duplicate = any(e["code"] == "DUPLICATE_INVOICE" for e in blocking_exceptions_to_create)

    for exc_data in blocking_exceptions_to_create:
        # Check if already open
        already_open = next((e for e in existing_exceptions if e.code == exc_data["code"] and e.status == "open"), None)
        if not already_open:
            new_exc = ExceptionRecord(
                id=gen_uuid(),
                invoice_id=invoice.id,
                match_run_id=match_run.id,
                code=exc_data["code"],
                severity=exc_data["severity"],
                status="open",
                owner_role=exc_data["owner_role"],
                description=exc_data["description"],
                expected_value=exc_data["expected_value"],
                actual_value=exc_data["actual_value"],
                source_refs_json=json.dumps(exc_data["source_refs"]),
                created_at=utcnow_iso(),
            )
            db.add(new_exc)
            created_exceptions.append(new_exc)
        else:
            # Update match run id
            already_open.match_run_id = match_run.id
            created_exceptions.append(already_open)

    # Auto-resolve existing exceptions if their check now passes
    active_codes = {e["code"] for e in blocking_exceptions_to_create}
    for old_exc in existing_exceptions:
        if old_exc.code not in active_codes:
            old_exc.status = "resolved"
            old_exc.resolved_at = utcnow_iso()
            old_exc.resolved_by = executed_by

    # UPDATE INVOICE STATE ACCORDING TO STATE MACHINE
    if is_duplicate:
        invoice.status = "duplicate_blocked"
    elif overall_status == "PASS":
        invoice.status = "ready_for_approval"
    elif overall_status == "BLOCKED":
        invoice.status = "exception_open"
    elif overall_status == "NEEDS_HUMAN":
        invoice.status = "awaiting_human"

    invoice.updated_at = utcnow_iso()
    db.flush()

    return match_run, created_exceptions
