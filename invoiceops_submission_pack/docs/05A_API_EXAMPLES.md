# 05A — API Examples

Examples use local placeholder credentials. Replace values with real demo IDs returned by the API. These commands target InvoiceOps, not Switch.

## 1. Create invoice case

```bash
curl -X POST http://localhost:8000/api/v1/invoices \\
  -H "Authorization: Bearer $AP_CLERK_TOKEN" \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: create-inv-1042-demo-001" \\
  -d '{
    "vendor_id":"VND-001",
    "invoice_number":"NSC/1042/26",
    "invoice_date":"2026-10-29",
    "po_id":"PO-2026-0082",
    "currency":"INR",
    "subtotal":"120000.00",
    "tax_total":"21600.00",
    "invoice_total":"141600.00"
  }'
```

## 2. Submit extraction proposal (agent)

```json
{
  "document_id": "DOC-1042",
  "fields": [
    {"field":"invoice_number","value":"NSC/1042/26","confidence":0.99,"document_id":"DOC-1042","page":1,"excerpt":"Invoice No: NSC/1042/26"},
    {"field":"po_reference","value":"PO-2026-0082","confidence":0.98,"document_id":"DOC-1042","page":1,"excerpt":"PO Ref: PO-2026-0082"},
    {"field":"invoice_total","value":"141600.00","confidence":0.96,"document_id":"DOC-1042","page":1,"excerpt":"Grand Total INR 141,600.00"}
  ],
  "lines": [
    {"sku":"LAPTOP-DOCK-01","description":"USB-C docking station","quantity":"10","unit_price":"12000.00","net_amount":"120000.00","tax_amount":"21600.00","source_page":1,"confidence":0.95}
  ]
}
```

## 3. Run matching

```bash
curl -X POST http://localhost:8000/api/v1/invoices/INV-2026-1042/match-runs \\
  -H "Authorization: Bearer $RECONCILE_AGENT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"policy_version":"demo-policy-1.0"}'
```

Expected synthetic outcome for the included fixture: `BLOCKED` with `QTY_EXCEEDS_RECEIVED`, because invoice quantity is 10 and accepted GRN quantity is 8.

## 4. Attach human evidence

```json
{
  "source_type": "grn",
  "source_ref": "GRN-2026-0042",
  "comment": "Procurement confirmed the second accepted delivery record; source record attached and verified by the AP Clerk."
}
```

The actual case remains blocked until the new evidence is persisted and matching is rerun. A chat message alone is not evidence in the business database.

## 5. Finance approval (human only)

```bash
curl -X POST http://localhost:8000/api/v1/invoices/INV-2026-1041/approvals \\
  -H "Authorization: Bearer $FINANCE_APPROVER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: approve-inv-1041-demo-001" \\
  -d '{
    "decision":"approved",
    "comment":"Reviewed PO, accepted GRN, invoice and latest passing match run.",
    "match_run_id":"MATCH-RUN-ID-FROM-API",
    "expected_invoice_version":1
  }'
```

The same request made with an agent token must return `403` and create no approval record.

## 6. Create payment-ready record

```bash
curl -X POST http://localhost:8000/api/v1/invoices/INV-2026-1041/payment-ready-records \\
  -H "Authorization: Bearer $FINANCE_APPROVER_TOKEN" \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: payready-inv-1041-demo-001" \\
  -d '{"approval_id":"APPROVAL-ID-FROM-API"}'
```

Response must include `payment_executed: false`. This endpoint creates a downstream-ready record only.
