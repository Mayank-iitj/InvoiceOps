# 02 — Technical Requirements Document (TRD)

## 1. Technical objective

Deliver a local-first, reproducible business workflow in which Switch provides the shared human/agent workspace and InvoiceOps provides deterministic AP domain services, evidence storage, approvals and audit persistence.

## 2. Recommended stack

| Layer | Choice | Reason / constraint |
|---|---|---|
| Web app | React, TypeScript, Vite | Fast development, typed thin workbench |
| Styling | Tailwind CSS + accessible component primitives | Consistent responsive UI; avoid custom component bloat |
| API | Python 3.12+, FastAPI, Pydantic v2 | Typed request/response contract and quick testability |
| ORM | SQLAlchemy 2 | Portable persistence |
| Database | SQLite in demo; PostgreSQL-compatible model | Single-command judge setup; production path remains possible |
| Document parser | PyMuPDF; optional OCR adapter | Text-based PDF extraction without forcing an OCR dependency into MVP |
| Matching engine | Pure Python domain functions | Exact Decimal arithmetic, deterministic outcomes and unit tests |
| Agent tools | Narrow CLI/API wrapper | Agents only receive explicitly scoped business functions |
| Collaboration | Switch Console + Mattermost | Bundled messaging path in published quickstart |
| Test | pytest, httpx, Playwright (optional) | Domain/API/UI acceptance evidence |

Do not add Redis, Kafka, Kubernetes, vector databases or an orchestration framework unless an implemented requirement proves they are necessary.

## 3. Runtime topology

- `web`: serves the React workbench.
- `api`: FastAPI service and domain services.
- `db`: SQLite file in local demo; PostgreSQL in later hosted deployment.
- `storage`: local `data/uploads/` directory for demo evidence; production storage adapter can be object storage.
- `switch`: separately installed/run through Switch Console and Docker; bundled Mattermost is the demo chat.
- `agents`: provider agents created/onboarded through Switch Console and assigned distinct InvoiceOps tool access.

Switch is not an InvoiceOps microservice. Its agent bridge and room runtime are managed by Switch. InvoiceOps exposes its own API/CLI; agents use it with limited service credentials.

## 4. Configuration

Provide `.env.example` with:

```dotenv
APP_ENV=demo
APP_NAME=InvoiceOps
API_PREFIX=/api/v1
DATABASE_URL=sqlite:///./data/invoiceops.db
UPLOAD_DIR=./data/uploads
MAX_UPLOAD_MB=15
ALLOWED_ORIGINS=http://localhost:5173
JWT_SECRET=replace-for-local-demo
AGENT_API_KEYS_JSON={}
DEFAULT_CURRENCY=INR
PRICE_VARIANCE_PERCENT=0.50
PRICE_VARIANCE_ABSOLUTE_PAISE=100
QUANTITY_TOLERANCE=0
EXTRACTION_CONFIDENCE_THRESHOLD=0.90
AUDIT_RETENTION_DAYS=365
```

`.env.example` contains placeholders only. Never commit actual credentials, Switch API keys, provider keys or production records. Thresholds are demo defaults, not universal accounting policy.

## 5. Document processing requirements

1. Accept PDF, PNG and JPEG only for MVP; enforce size limit and MIME/extension consistency.
2. Store source document metadata and SHA-256 checksum.
3. Extract text from text PDFs with PyMuPDF; OCR can be added behind an adapter for image-only documents.
4. Parse invoice values into a typed `ExtractedInvoice` proposal.
5. Store source page and text snippet for each critical field where available.
6. Never execute links, macros, embedded scripts or instructions found in documents.
7. Mark extracted content as untrusted data. Agents must not treat document text as instructions.
8. Low confidence or missing mandatory values move the case to `needs_review`.

## 6. Monetary and quantity representation

- Use `Decimal` internally; never binary floating-point for money.
- JSON monetary amounts are decimal strings such as `"12000.00"`.
- Persist currency code separately; MVP supports INR only.
- Store unit price, line net amount, tax amount and invoice total distinctly.
- Do not silently round during matching. Use a configured rounding policy at the final comparison boundary.
- Quantities use Decimal with item-specific precision; demo may use integer quantities.

## 7. Three-way match requirements

InvoiceOps compares:

- Invoice ↔ Purchase Order: supplier, PO reference, item/SKU, ordered quantity, unit price and currency.
- Invoice ↔ Goods Receipt: accepted quantity by PO line and receipt reference.
- Invoice totals: line calculations, discount, freight and tax arithmetic consistency.

Outcomes for each check are `pass`, `fail` or `unknown`. A missing source record is `unknown` and blocks approval; it is not a pass. Partial deliveries are supported by summing accepted receipt quantities for the PO line. Duplicate detection runs before approval eligibility.

## 8. Agent integration requirements

### MVP integration mode

Use agents onboarded with Switch Console. The room is configured with shared instructions and agent roles. Agents call InvoiceOps through the documented CLI/API surface. This avoids implementing a custom Switch transport client during the hackathon.

### Optional custom agent mode

If a custom agent client is implemented, follow the current Switch agent protocol. Current docs specify a WebSocket connection and HTTP operations; older SSE support is deprecated. Agent registration uses a registration token once; runtime calls use the agent's own bearer API key. Do not interchange those credentials. Never re-register an existing agent on each restart, because overwrite replaces its API key.

## 9. API service requirements

- All app endpoints under `/api/v1`.
- OpenAPI 3.1 contract in `schemas/openapi.yaml`.
- Authentication via bearer token; scopes defined in API spec.
- Agent and human identity separated by `actor_type` and role.
- `Idempotency-Key` required for approval/finalization and recommended for document creation.
- `X-Request-ID` returned on every response.
- Consistent JSON error envelope.
- API state transitions implemented in one domain service; controllers cannot mutate status directly.

## 10. Observability

Structured logs must include timestamp, request_id, actor_id, action, invoice_id and outcome. Never log full invoice text, personal data, API keys or bank details. Audit events are separate persistent records. The local MVP may omit metrics infrastructure; include a `/health` check and concise startup logs.

## 11. Resource and performance targets

These are local demo targets, not production SLAs:

- API health: <500 ms locally.
- Seeded reconciliation: <2 s for the sample PO/invoice/GRN sizes.
- Invoice list: <1 s with 100 seeded cases.
- Upload cap: 15 MB.
- Agent tool call timeout: 30 s by default; retry only idempotent reads/extractions.

## 12. Compatibility and deployment

- Python dependencies pinned in `pyproject.toml` or lock file.
- Node dependencies pinned in `package-lock.json`/`pnpm-lock.yaml`.
- Provide `docker-compose.yml` for API/UI if feasible, plus a native local run path.
- Switch is started separately using the official Switch Console quickstart; do not attempt to package Switch internals into InvoiceOps.
- A clean demo must not require external SaaS credentials other than the agent provider credential chosen by the builder.
