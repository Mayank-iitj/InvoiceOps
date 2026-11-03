# 06 — Data Model and Matching Rules

## 1. Core entities

- Vendor: supplier master data (demo fields only; no bank account fields).
- PurchaseOrder + PurchaseOrderLine: agreed quantities and prices.
- GoodsReceipt + GoodsReceiptLine: quantities accepted by warehouse/procurement.
- Invoice + InvoiceLine: supplier-submitted invoice.
- Document: original evidence file metadata and hash.
- Extraction: versioned structured data proposal with provenance.
- MatchRun + MatchCheck: deterministic matching outcome.
- Exception + ResolutionProposal: discrepancy and proposed next step.
- Approval: human finance decision.
- PaymentReadyRecord: non-payment downstream handoff.
- AuditEvent: append-only event record.

## 2. Normalized matching keys

- Vendor: stable `vendor_id`, not free-text supplier name alone.
- Invoice number: Unicode normalize, trim, uppercase, and remove whitespace, hyphens and slashes for the demo key (so `NSC/1041/26` and `NSC 1041-26` collide); preserve all other characters unless explicitly tested.
- Document duplicate: SHA-256 exact content hash.
- PO line: explicit PO line ID or SKU mapping confirmed by a person; no autonomous fuzzy mapping.

## 3. Default demo matching policy

All values are configurable and must be displayed in `Settings > Matching policy`. These defaults are only for the synthetic dataset:

- Currency: INR only.
- Quantity tolerance: 0 units.
- Unit-price relative tolerance: 0.50%.
- Absolute price tolerance: ₹1.00 per unit (100 paise); apply the stricter documented rule chosen by the project and test it.
- Tax arithmetic: recompute component totals to the invoice total with currency rounding; this is arithmetic consistency, not GST compliance.
- Missing PO or GRN: `unknown`, blocking.
- Duplicate key: same vendor + normalized invoice number OR exact document checksum.
- Partial receipts: sum accepted GRN quantities across all linked receipts for the PO line.

Recommended deterministic comparison:

`price_delta = abs(invoice_unit_price - po_unit_price)`  
`price_allowed = max(po_unit_price * relative_tolerance, absolute_tolerance)`

Pass only when `price_delta <= price_allowed`. For quantities, invoice quantity must not exceed accepted GRN quantity unless an explicitly configured overbilling policy is approved by a human. The MVP should use zero quantity tolerance.

## 4. Match output schema

Each check should contain:

```json
{
  "code": "QTY_EXCEEDS_RECEIVED",
  "status": "fail",
  "severity": "blocking",
  "message": "Invoice quantity exceeds accepted received quantity.",
  "expected": "8",
  "actual": "10",
  "source_refs": ["PO-2026-0082/line-1", "GRN-2026-0041/line-1", "INV-2026-1042/page-1"],
  "policy_version": "demo-policy-1.0"
}
```

## 5. Overall match status

- `PASS`: all mandatory checks pass.
- `BLOCKED`: at least one mandatory check fails or a duplicate is confirmed.
- `NEEDS_HUMAN`: one or more mandatory checks are unknown or require factual confirmation.

Approval requires `PASS`, no open blocking exceptions, and current source versions.

## 6. Audit event fields

`event_id`, `occurred_at`, `actor_id`, `actor_type`, `action`, `invoice_id`, `entity_type`, `entity_id`, `before_state`, `after_state`, `reason`, `source_refs`, `request_id`, `idempotency_key_hash`.

Do not store secrets or full document contents in audit event payloads.
