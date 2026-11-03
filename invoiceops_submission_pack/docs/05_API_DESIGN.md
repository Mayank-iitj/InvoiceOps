# 05 — API Design

## 1. API conventions

Base path: `/api/v1`  
Format: JSON, except multipart document upload.  
Auth: `Authorization: Bearer <token>`.  
Money: decimal strings with explicit ISO currency.  
Time: UTC ISO-8601 timestamps.  
IDs: opaque UUIDs except human-readable invoice/vendor/PO references.

Each response includes `X-Request-ID`. Mutating calls accept `Idempotency-Key`; it is mandatory for approval and finalization. Use `If-Match` or `expected_version` when acting on a previously viewed invoice to avoid stale approvals.

## 2. Actor roles and scopes

| Actor | Allowed scopes | Forbidden |
|---|---|---|
| `ap_clerk` | invoice read/create, upload, confirm extraction, run match, attach human evidence, request approval | approve/reject, create payment-ready |
| `procurement_owner` | read PO/receipt context, submit receipt confirmation/evidence, resolve assigned PO/GRN exception | approve invoice |
| `finance_approver` | read case/evidence, approve/reject, create payment-ready record after approval | edit extracted invoice fields silently |
| `invoice_intake_agent` | read assigned case/document text, submit extraction proposal | resolve exceptions, approve, finalize |
| `invoice_match_agent` | read case/PO/GRN, run match, create routing/proposal note | approve, change master data, finalize |
| `ap_admin` | configuration, exception override with justification, user/role setup | no unlogged mutations |

Agent identities must not be mapped to `finance_approver` or `ap_admin`.

## 3. Resource model

- `Invoice`: business case and status.
- `Document`: uploaded source artifact and checksum.
- `Extraction`: proposed structured fields and evidence.
- `MatchRun`: immutable result tied to data versions and policy version.
- `Exception`: blocking or informational discrepancy.
- `ResolutionProposal`: proposed action, evidence and responsible human; not a final decision.
- `Approval`: human approval/rejection record.
- `PaymentReadyRecord`: non-payment downstream-ready output.
- `AuditEvent`: append-only history.

## 4. Endpoint catalogue

| Method | Path | Purpose | Scope |
|---|---|---|---|
| GET | `/health` | Health probe | public |
| GET | `/invoices` | Search/filter cases | `invoice:read` |
| POST | `/invoices` | Create invoice case | `invoice:create` |
| GET | `/invoices/{id}` | Read case and current state | `invoice:read` |
| POST | `/invoices/{id}/documents` | Upload evidence | `document:write` |
| GET | `/documents/{id}` | Read safe metadata/text | `document:read` |
| POST | `/invoices/{id}/extractions` | Submit agent extraction proposal | `extraction:write` |
| POST | `/invoices/{id}/extractions/{extractionId}/confirm` | Human confirm/correct extraction | `extraction:confirm` |
| POST | `/invoices/{id}/match-runs` | Run deterministic match | `match:run` |
| GET | `/invoices/{id}/match-runs/latest` | Get latest match result | `invoice:read` |
| POST | `/invoices/{id}/exceptions/{exceptionId}/evidence` | Attach human evidence | `exception:evidence` |
| POST | `/invoices/{id}/exceptions/{exceptionId}/proposals` | Create agent/human resolution proposal | `exception:propose` |
| POST | `/invoices/{id}/approvals` | Finance approve/reject | `approval:decide` |
| POST | `/invoices/{id}/payment-ready-records` | Create downstream-ready record | `payment_ready:create` |
| GET | `/payment-ready-records` | List approved ready records | `payment_ready:read` |
| GET | `/invoices/{id}/audit-events` | Case audit history | `audit:read` |

## 5. Error envelope

```json
{
  "error": {
    "code": "APPROVAL_BLOCKED",
    "message": "Invoice has unresolved blocking exceptions.",
    "details": [{"exception_code": "QTY_EXCEEDS_RECEIVED", "status": "open"}]
  },
  "request_id": "req_01..."
}
```

Common HTTP statuses: 400 invalid body, 401 missing/invalid token, 403 role/scope denied, 404 resource not found, 409 invalid state/stale version/idempotency conflict, 413 upload too large, 422 domain validation failed, 429 rate limit, 500 unexpected server failure.

## 6. Critical API behavior

### Create and upload

`POST /invoices` creates a `draft`. Uploading a valid invoice document transitions it to `received`. Duplicate pre-check runs using vendor ID + normalized invoice number and document checksum. Store the submitted case, then create `duplicate_blocked` / `DUPLICATE_INVOICE` so the suspected duplicate remains auditable; do not rely on a database uniqueness constraint that silently rejects the evidence.

### Extraction proposal

The agent submits values, confidence and source evidence. The server validates types and arithmetic but does not treat model confidence as proof. Mandatory-field confidence below configured threshold moves to `needs_review`. Human confirmation creates a new immutable extraction version.

### Match run

The backend runs all rules deterministically and persists a new immutable `MatchRun`. The run includes `invoice_version`, `po_version`, `grn_version` and `policy_version`. A change to any input invalidates approval eligibility until a fresh match is run.

### Approval

The API must verify actor role server-side. It must reject agent actors even if an agent sends a crafted request. Approval is not allowed when current match status is not `PASS`, any blocking exception is open, or the match input versions are stale.

### Payment-ready record

The endpoint creates a record for downstream payment processing, not an actual transfer. No bank/payment provider SDK, payment credential or transfer endpoint is part of the MVP. It is not enough for the UI to hide a button; the backend must enforce this rule.

## 7. Switch integration boundary

The InvoiceOps API is **not** the Switch API. Agents join the Switch room through Switch Console or a custom client that follows Switch's current agent protocol. They then call the InvoiceOps API/CLI using InvoiceOps service credentials. Current Switch docs describe agent WebSocket connections and HTTP operations, bearer agent API keys, and `POST /agents/{agent_id}/ops/{operation}` for Switch operations. Do not point an InvoiceOps token at Switch endpoints or treat a Switch registration token as an agent API key.
