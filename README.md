<div align="center">

# ⚡ InvoiceOps

### **Deterministic Autonomous AP Exception Resolution & 3-Way Matching Engine**

*Autonomous multi-agent collaboration meets deterministic financial safety. Human AP specialists, procurement leads, finance approvers, and specialized AI agents resolve discrepancies in real time to produce immutable, audit-ready payment records.*

<br/>

[![Python 3.12+](https://img.shields.io/badge/python-3.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Docker Ready](https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![Tests Passing](https://img.shields.io/badge/Tests-18%2F18%20Passing-success?style=for-the-badge&logo=pytest&logoColor=white)](backend/tests/test_scenarios.py)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg?style=for-the-badge)](LICENSE)

<br/>

[**Live Studio App**](http://localhost:8000) • [**Interactive API Docs**](http://localhost:8000/docs) • [**Switch MCP Manifest**](http://localhost:8000/api/v1/switch/mcp) • [**Health Probe**](http://localhost:8000/health)

</div>

---

## 🧭 Executive Summary

Every year, enterprise finance departments waste hundreds of thousands of hours resolving accounts payable exceptions—rate discrepancies, missing goods receipts, duplicate billings, and unauthorized surcharges. Traditional AP software either traps exceptions in static queues or attempts opaque LLM automation that hallucinations can compromise.

**InvoiceOps pioneers a dual-engine architecture:**
1. **Deterministic Python Core**: Strict 3-way matching engine using Python's pure `Decimal` arithmetic—ensuring zero binary floating-point rounding errors and 100% reproducible reconciliation.
2. **Collaborative Autonomous Multi-Agent Layer**: Native integration with `sandbox-quantum/switch` multi-agent rooms (`#invoiceops-ap`) where specialized intake and reconciliation agents collaborate with humans, gather evidence, and solve blocking exceptions in real time.

> [!IMPORTANT]
> **Strict Financial Safety & Non-Payment Boundary**  
> InvoiceOps reconciles documents, coordinates dispute resolution, and produces cryptographically verifiable **Payment-Ready Records**. **InvoiceOps never connects to live banking rails, executes wire transfers, or holds supplier disbursement credentials.** Money movement remains strictly downstream in enterprise ERPs (SAP, NetSuite, Oracle) or corporate treasury systems.

---

## ✨ Key Highlights & Features

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│  INVOICEOPS CORE PILLARS                                                                         │
├──────────────────────────┬──────────────────────────┬────────────────────────────────────────────┤
│ 🛡️ 100% Pure Decimal     │ 🤖 Switch Multi-Agent    │ 🔒 Consequential Role Gate                 │
│ Zero floating-point drift│ Real-time threaded room  │ Strict 403 on clerk/agent approvals;       │
│ evaluated to exact paise │ with reactive AI agents  │ only human Finance Approvers sign off      │
├──────────────────────────┼──────────────────────────┼────────────────────────────────────────────┤
│ 📜 Cryptographic Audit   │ 🔌 Native MCP Server     │ 🎨 Apple & Supaste Aesthetic               │
│ SHA-256 immutable hashes │ 5 Model Context Protocol │ Dynamic Island notch nav, ambient glow,    │
│ for every state change   │ tools for Claude & Codex │ high-density tables & tabular numbers      │
└──────────────────────────┴──────────────────────────┴────────────────────────────────────────────┘
```

- **Dynamic Island Notch Top Navigation**: Integrated top bar featuring smooth concave fillets, role switcher, database reset controls, and one-click Switch console drawer.
- **Interactive Three-Way Reconciliation Grid**: Live side-by-side comparison of **Invoice Lines ↔ Purchase Order ↔ Warehouse Goods Receipts (GRN)**.
- **One-Click Ingestion & Scenario Simulator**: Ingest custom invoices via drag-and-drop or run one-click stress-test templates:
  - *Clean Match* (`INV-2026-1041`): Perfect 3-way match ready for instant finance approval.
  - *Quantity Surcharge* (`INV-2026-1042`): Billed 10 units vs 8 accepted at warehouse.
  - *Duplicate Invoice Block* (`INV-2026-1043`): Identical normalized number & hash detection.
  - *Price Mismatch* (`INV-2026-1044`): Rate variance exceeding configured tolerance threshold.
  - *Prompt Injection Defense*: Malicious PDF instructions isolated and suppressed.
- **Immutable Governance Log**: Searchable, filterable audit trail tracking all actions, before/after states, actor identities, and cryptographic source references with JSON/CSV export.
- **Model Context Protocol (MCP) Server**: Exposes 5 production tools for external LLM clients (`Claude Code`, `Codex`, `Cursor`).

---

## 🏛️ System Architecture

### Multi-Agent Flow & Component Topology

```mermaid
flowchart TB
  subgraph ClientLayer["Frontend Studio (React 18 + TypeScript + Vite)"]
    direction TB
    NAV["Dynamic Island Notch Nav\n(Role Selector & Live Status)"]
    LP["Landing Page & Hero Shelf"]
    IB["AP Invoices Inbox & Ingestion Modal"]
    DT["3-Way Match Reconciler & Evidence Drawer"]
    PR["Payment-Ready Registry & CSV Export"]
    AL["Immutable Audit Log & Event Inspector"]
  end

  subgraph SwitchLayer["Switch Multi-Agent Network (#invoiceops-ap)"]
    direction LR
    ROOM["Threaded Room: #invoiceops-ap"]
    INTAKE["@invoiceops-intake\n(OCR & Proposal Agent)"]
    RECON["@invoiceops-reconcile\n(Math Verification Agent)"]
    HUMAN["Human AP / Procurement Owner"]
    ROOM <--> INTAKE
    ROOM <--> RECON
    ROOM <--> HUMAN
  end

  subgraph BackendCore["InvoiceOps Deterministic Engine (FastAPI + SQLAlchemy)"]
    direction TB
    ROUTER["FastAPI REST Router\n(/api/v1)"]
    AUTH["Role-Based Guardrail Engine\n(403 Enforcement)"]
    MATH["Decimal 3-Way Matcher\n(Zero Float Drift)"]
    MCP["Model Context Protocol Server\n(5 Native Tools)"]
    SAFE["Document Vault\n(SHA-256 Digesting)"]
  end

  subgraph StorageLayer["Data & Compliance Layer"]
    DB[(SQLite / PostgreSQL Engine)]
    AUDIT[(Append-Only Audit Trail)]
    EXPORT[(Downstream ERP Payment Vouchers)]
  end

  ClientLayer <-->|REST API + Idempotency Keys| ROUTER
  SwitchLayer <-->|Webhooks & MCP Invocations| MCP
  ROUTER --> AUTH
  AUTH --> MATH
  MATH --> SAFE
  SAFE --> DB
  SAFE --> AUDIT
  AUTH --> EXPORT
```

---

## 🔄 End-to-End Resolution Lifecycle

The following sequence details how an exception is ingested, detected, routed to Switch agents, verified with evidence, and signed off by finance:

```mermaid
sequenceDiagram
  autonumber
  actor AP as AP Specialist
  participant UI as InvoiceOps Studio
  participant Core as Backend Matching Engine
  participant Switch as Switch Room (#invoiceops-ap)
  actor PO as Procurement Owner
  actor FA as Finance Approver

  AP->>UI: Ingests Invoice (e.g. INV-2026-1042)
  UI->>Core: POST /api/v1/invoices + SHA-256 Hashing
  Core->>Core: Run Deterministic 3-Way Match (Decimal Engine)
  Core-->>UI: Match Status: FAILED (QTY_EXCEEDS_RECEIVED)
  Core->>Switch: Post Exception Alert to #invoiceops-ap
  Switch->>PO: @procurement_owner discrepancy on Line 1 (10 billed vs 8 GRN)
  PO->>Switch: "Inspected physical bay: 2 units accepted under GRN-2026-9042"
  PO->>UI: Attach Verified GRN Evidence & Comment
  UI->>Core: POST /exceptions/{id}/evidence
  Core->>Core: Re-run 3-Way Match Engine
  Core-->>UI: Match Status: PASS (Ready for Approval)
  Note over FA,Core: Role-Based Gate: Only finance_approver can sign off
  FA->>UI: Reviews line audit & clicks "Approve Invoice"
  UI->>Core: POST /approvals (Role: finance_approver)
  Core->>Core: Verify Idempotency & Freshness
  Core->>Core: Generate Payment-Ready Record Voucher
  Core-->>Switch: Broadcast: "INV-2026-1042 approved. Voucher PR-2026-0042 generated."
  Core-->>UI: Display Payment-Ready Voucher (Exportable to CSV)
```

---

## 🛠️ Model Context Protocol (MCP) Server

InvoiceOps exposes a native Model Context Protocol (MCP) endpoint under `/api/v1/switch/mcp` allowing autonomous agents (e.g., Claude Code, Cursor, Codex) to inspect and reconcile invoices deterministically:

```bash
# Query the live MCP Tool Manifest
curl -s http://localhost:8000/api/v1/switch/mcp | jq .
```

### Available MCP Tools

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `invoiceops_match` | `invoice_id` | Executes deterministic 3-way match using Decimal domain logic. |
| `invoiceops_inspect` | `invoice_id` | Retrieves full case facts, discrepancies, and tolerance checks. |
| `invoiceops_attach_evidence` | `invoice_id`, `exception_id`, `source_type`, `source_ref`, `comment` | Attaches verified external evidence to clear a discrepancy. |
| `invoiceops_approve_payment` | `invoice_id`, `decision`, `comment`, `approver_role` | Consequential finance approval. Rejects non-finance roles with 403. |
| `invoiceops_get_audit` | `invoice_id` | Fetches immutable cryptographic event log for compliance check. |

#### Example: Invoking an MCP Tool via REST
```bash
curl -X POST http://localhost:8000/api/v1/switch/mcp/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "invoiceops_match",
    "arguments": { "invoice_id": "INV-2026-1041" }
  }'
```

---

## 🚀 Quick Start & Deployment Guide

InvoiceOps is engineered to boot seamlessly across any development or production environment in seconds.

### Option 1: Docker Compose (Production Recommendation)
Runs the entire web application, deterministic backend, and Switch mock gateway on an isolated bridge network:

```bash
# Clone the repository
git clone https://github.com/your-org/invoiceops.git
cd invoiceops

# Build and start services
docker compose up --build
```
- 🌐 **Web Studio UI**: [http://localhost:8000](http://localhost:8000)
- 📚 **OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 🩺 **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

### Option 2: Standalone Docker Container
```bash
docker build -t invoiceops:latest .
docker run -p 8000:8000 -e PORT=8000 invoiceops:latest
```

---

### Option 3: Local One-Click Scripts

#### Windows
Double-click `start.bat` or run:
```powershell
.\start.ps1
```

#### macOS / Linux
```bash
chmod +x start.sh
./start.sh
```

#### Native Python
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch production server
python run_app.py
```

---

### Option 4: 1-Click Cloud Platform Deployments

InvoiceOps includes ready-to-deploy configuration manifests for leading cloud providers:

| Cloud Platform | Config Manifest | Deployment Flow |
| :--- | :--- | :--- |
| **Render** | [`render.yaml`](render.yaml) | New &rarr; Blueprint &rarr; Select Repo &rarr; Auto Deploy |
| **Railway** | [`railway.json`](railway.json) | New Project &rarr; Deploy from GitHub Repo (Auto-detected) |
| **Fly.io** | [`fly.toml`](fly.toml) | `fly launch` followed by `fly deploy` |
| **Heroku / Dokku**| [`Procfile`](Procfile) | Uses standard web worker with dynamic `$PORT` |
| **Kubernetes** | [`deploy/k8s/deployment.yaml`](deploy/k8s/deployment.yaml) | `kubectl apply -f deploy/k8s/deployment.yaml` |

---

## 🧪 Comprehensive Verification & Test Suite

All 18 mission-critical test scenarios are automated and verified via pytest:

```bash
python -m pytest backend/tests/test_scenarios.py -v
```

### Verified Test Run (18/18 Passing)
```text
============================= test session starts =============================
platform win32 -- Python 3.14.10, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Users\MS\Downloads\InvoiceOps_Submission_Documentation_Pack

backend/tests/test_scenarios.py::test_t01_valid_invoice_passes_and_ready_for_approval PASSED [  5%]
backend/tests/test_scenarios.py::test_t02_quantity_mismatch_blocks_approval PASSED [ 11%]
backend/tests/test_scenarios.py::test_t03_price_variance_blocks_and_routes_to_procurement PASSED [ 16%]
backend/tests/test_scenarios.py::test_t04_po_not_found PASSED            [ 22%]
backend/tests/test_scenarios.py::test_t05_grn_missing PASSED             [ 27%]
backend/tests/test_scenarios.py::test_t06_duplicate_vendor_and_normalized_number PASSED [ 33%]
backend/tests/test_scenarios.py::test_t07_duplicate_document_hash PASSED [ 38%]
backend/tests/test_scenarios.py::test_t08_low_confidence_requires_human_review PASSED [ 44%]
backend/tests/test_scenarios.py::test_t09_malformed_currency_rejected PASSED [ 50%]
backend/tests/test_scenarios.py::test_t10_agent_attempt_approval_denied_with_403 PASSED [ 55%]
backend/tests/test_scenarios.py::test_t11_ap_clerk_attempt_approval_denied_with_403 PASSED [ 61%]
backend/tests/test_scenarios.py::test_t12_finance_approval_stale_match_denied_with_409 PASSED [ 66%]
backend/tests/test_scenarios.py::test_t13_approval_repeated_with_same_idempotency_key PASSED [ 72%]
backend/tests/test_scenarios.py::test_t14_invoice_contains_prompt_injection_text PASSED [ 77%]
backend/tests/test_scenarios.py::test_t15_file_exceeds_max_size_returns_413 PASSED [ 83%]
backend/tests/test_scenarios.py::test_t16_resolved_exception_and_rematch_passes PASSED [ 88%]
backend/tests/test_scenarios.py::test_t17_switch_room_message_and_reactive_agent_reply PASSED [ 94%]
backend/tests/test_scenarios.py::test_t18_switch_mcp_server_and_tool_invocation PASSED [100%]

======================= 18 passed in 19.73s =======================
```

---

## 🔒 Enterprise Security & Financial Guardrails

1. **Zero Financial Execution**:
   - The application does not contain banking credentials, SWIFT/ACH transmission engines, or live disbursement rails. Approved records yield verifiable vouchers for external corporate treasury systems.
2. **Server-Side Role Guardrails**:
   - Non-human agents (`invoice_intake_agent`, `invoice_match_agent`) and AP Clerks are forbidden from approving payments. Requests attempting unauthorized sign-offs immediately return `HTTP 403 Forbidden`.
3. **Idempotency Protection**:
   - Every financial approval and voucher creation requires an `Idempotency-Key` header, preventing duplicate payments caused by network retries.
4. **Stale Match Protection**:
   - If an invoice, line item, or goods receipt changes after reconciliation, the approval endpoint returns `HTTP 409 Conflict` until a fresh match run is performed.
5. **Prompt Injection Armor**:
   - Documents and invoice text are parsed strictly as untrusted data inputs. Instructions embedded inside PDF streams are never executed by backend services.
6. **Append-Only Audit Ledger**:
   - All state transitions, approvals, evidence uploads, and matches are recorded in an immutable, cryptographically verifiable audit log.

---

## 👥 Built for Enterprise Personas

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│ 👩‍💼 AP Specialists               │ 📦 Procurement Leads            │ 💼 Financial Controllers        │
│ "Eliminate 80% of repetitive    │ "Resolve quantity & rate deltas │ "Enforce ironclad audit trails, │
│ manual data entry and match     │ in-flow without endless email   │ strict Decimal precision, and   │
│ checks in seconds."             │ chains and vendor phone calls." │ zero rogue disbursement risk."  │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 🔍 Internal Auditors            │ 🛠️ IT & ERP Engineers           │ 🛡️ Security Officers           │
│ "Inspect cryptographic SHA-256  │ "Deploy in 60s with Docker, K8s │ "Total prompt injection defense │
│ logs and immutable state        │ or native cloud templates;      │ with strictly isolated document │
│ transitions on demand."         │ integrate via clean REST & MCP."│ parsing sandboxes."             │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
├── .dockerignore                     # Docker build exclusions
├── .env.example                      # Production environment template
├── docker-compose.yml                # Production multi-container composition
├── Dockerfile                        # Multi-stage production container build
├── fly.toml                          # Fly.io deployment manifest
├── Procfile                          # Heroku/Render process declaration
├── railway.json                      # Railway platform configuration
├── render.yaml                       # Render 1-click blueprint
├── requirements.txt                  # Python dependencies
├── run_app.py                        # Single-command server & SPA runner
├── start.bat / start.ps1 / start.sh  # Cross-platform one-click launch scripts
├── SWITCH_INTEGRATION_GUIDE.md       # Multi-agent collaboration documentation
│
├── backend/                          # FastAPI Backend Engine
│   ├── app/
│   │   ├── api/v1/                   # REST API & Switch Endpoints
│   │   │   ├── approvals.py          # Consequential finance sign-offs
│   │   │   ├── audit.py              # Cryptographic governance audit stream
│   │   │   ├── exceptions.py         # Exception management & evidence attachment
│   │   │   ├── invoices.py           # Ingestion, cases, & PDF parsing
│   │   │   ├── matching.py           # 3-way reconciliation triggers
│   │   │   ├── payment_ready.py      # Downstream voucher generation
│   │   │   └── switch_rooms.py       # Switch collaboration rooms & MCP server
│   │   ├── models/                   # SQLAlchemy declarative models
│   │   ├── schemas/                  # Pydantic v2 validation schemas
│   │   └── services/
│   │       ├── matching_engine.py    # Deterministic Decimal matching logic
│   │       └── switch_service.py     # Reactive agents, rooms, & MCP tools
│   └── tests/                        # 18 automated integration test scenarios
│
├── frontend/                         # React 18 + TypeScript + Vite Studio
│   ├── src/
│   │   ├── components/               # Navbar, Ingest Modal, Switch Room, Evidence
│   │   ├── pages/                    # LandingPage, InboxPage, Detail, Audit, Vendors
│   │   └── services/                 # API client & Switch integration
│   └── dist/                         # Pre-compiled production bundle
│
└── fixtures/                         # Synthetic business domain fixtures
```

---

<div align="center">

**InvoiceOps** — *Where Autonomous Agents Meet Deterministic Financial Safety.*

Made with precision for high-trust enterprise accounts payable.

</div>
