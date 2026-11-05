# InvoiceOps & Switch Integration Guide

> **Production Deployment & Architecture Guide for Switch Collaboration Rooms**  
> *Autonomous Accounts Payable Exception Resolution with Human-in-the-Loop Safeguards*

---

## 1. Executive Overview

**InvoiceOps** embeds autonomous finance workflows directly into the [Switch](https://github.com/sandbox-quantum/switch) multi-agent operating system. Rather than forcing accounting and procurement teams into another isolated dashboard, InvoiceOps turns chat channels (**Slack, Microsoft Teams, Discord, Telegram, and Mattermost**) into shared collaboration rooms where AI teammates and humans work together with shared context.

### The 4-Level Switch Capability Ladder

| Level | Switch Standard | InvoiceOps Implementation |
|---|---|---|
| **Level 1** | Everyday agents move into your messaging app | `invoiceops-intake` and `invoiceops-reconcile` join `#invoiceops-ap` in Slack/Mattermost. |
| **Level 2** | Encoding how work runs | Automated invoice ingestion triggers OCR parsing, line-item extraction, and normalized vendor duplicate hashing. |
| **Level 3** | Team runs on Switch | Multi-turn exception triage: when a price delta occurs on `INV-2026-1042`, the reconcile agent flags it, mentions `@procurement_owner`, accepts authorized Addendum #A-42 evidence, re-runs matching, and hands off to `@finance_approver`. |
| **Level 4** | Company runs on Switch | Complete AP department automation across ERPs (SAP, NetSuite, QuickBooks) with **guaranteed zero payment rails** and append-only audit ledgers. |

---

## 2. Switch Room Architecture

### Room: `#invoiceops-ap` (`room_invoiceops_ap`)

- **Topic**: `Autonomous Accounts Payable 3-Way Reconciliation & Discrepancy Resolution`
- **Active AI Agents**:
  1. **`invoiceops-intake`**: Ingests vendor invoices (PDF/XML/EDI), validates vendor profile, normalizes invoice numbers, flags duplicate submissions, and announces new arrivals in the thread.
  2. **`invoiceops-reconcile`**: Executes deterministic Python 3-way matching with `Decimal` arithmetic against Purchase Orders and Goods Receipt Notes. Enforces zero tolerance on quantity and ₹1.00 / 0.50% tolerance on price.
- **Human Operators**:
  1. **`@ap_clerk`**: Reviews triage notifications and extractions.
  2. **`@procurement_owner`**: Authorizes commercial variances, expediting surcharges, and attaches addendum evidence.
  3. **`@finance_approver`**: Exclusive human sign-off authority. Generates cryptographic payment-ready voucher records (AI agents and clerks receive strict HTTP 403 Forbidden).

---

## 3. Native Model Context Protocol (MCP) Server

InvoiceOps natively serves an MCP server so external Switch agents (**Claude Code**, **OpenAI Codex CLI**, **OpenCode**) can join the workflow and execute tools directly.

### Connect Your Agent over MCP

#### Claude Code
```bash
claude mcp add invoiceops http://localhost:8000/api/v1/switch/mcp
```

#### OpenAI Codex CLI
```bash
codex mcp add invoiceops --url http://localhost:8000/api/v1/switch/mcp
```

#### OpenCode
```bash
opencode mcp add
# Provide URL: http://localhost:8000/api/v1/switch/mcp
```

### Exported MCP Tools

| Tool Name | Description | Parameters |
|---|---|---|
| `invoiceops_match` | Executes deterministic 3-way line check | `invoice_id` (e.g. `INV-2026-1042`) |
| `invoiceops_inspect` | Returns line variances, PO comparisons, and OCR scores | `invoice_id` |
| `invoiceops_attach_evidence` | Attaches signed contract addendums to resolve exceptions | `exception_id`, `rationale`, `evidence_ref` |
| `invoiceops_approve_payment` | Human Finance Approver sign-off for payment voucher | `invoice_id`, `approver_role`, `idempotency_key` |
| `invoiceops_get_audit` | Returns tamper-evident append-only audit event trail | `invoice_id` |

---

## 4. REST & Webhook API Endpoints

All Switch endpoints are exposed under `/api/v1/switch`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/switch/rooms` | Lists active Switch rooms and connected agents |
| `GET` | `/api/v1/switch/status` | Reports connectivity across Switch Core, Mattermost, Slack, Teams |
| `GET` | `/api/v1/switch/rooms/{room_id}/messages` | Fetches threaded room messages |
| `POST` | `/api/v1/switch/rooms/{room_id}/messages` | Posts message; triggers reactive AI teammate responses |
| `POST` | `/api/v1/switch/rooms/{room_id}/simulate-workflow` | Executes automated 6-step judge verification scenario |
| `POST` | `/api/v1/switch/rooms/{room_id}/reset` | Resets thread back to clean initial demo state |
| `POST` | `/api/v1/switch/webhook` | Inbound webhook receiver for Switch Gateway and chat bridges |
| `GET` | `/api/v1/switch/mcp` | Serves MCP server manifest |
| `POST` | `/api/v1/switch/mcp/invoke` | Invokes an InvoiceOps tool over MCP |

---

## 5. Telegram Chat Gateway (@switch_devops_bot)

InvoiceOps features a production-ready **Telegram Chat Gateway** bridging mobile/desktop messaging directly into the `#invoiceops-ap` Switch room.

### Gateway Details
- **Bot Handle**: [`@switch_devops_bot`](https://t.me/switch_devops_bot)
- **Token Configuration**: Set via `TELEGRAM_BOT_TOKEN` in `.env`
- **Supported Modes**: Asynchronous long polling (built into FastAPI lifespan) or webhook (`/api/v1/telegram/webhook`)
- **CLI Commands**:
  ```bash
  # Check live connectivity
  python backend/cli.py telegram status

  # Run standalone polling worker
  python backend/cli.py telegram poll
  ```

### Interactive Telegram Commands

| Command | Action |
|---|---|
| `/start` | Onboarding guide, AI teammate roles, and available commands |
| `/status` | Real-time system health, connector status, and ledger counts |
| `/invoices` | List loaded invoice cases, vendor IDs, amounts, and statuses |
| `/inspect <id>` | Trigger Intake Agent OCR parsing & line-item candidate extraction |
| `/reconcile <id>` | Execute deterministic 3-way reconciliation (PO vs GRN vs Invoice) |
| `/override <id>` | Apply Procurement Addendum #A-42 (rate delta authorized) |
| `/approve <id>` | Human Finance Approver sign-off; generates sealed payment voucher |
| `/simulate` | Run automated 6-step collaborative judge triage scenario |
| `/audit <id>` | Inspect cryptographic append-only tamper-evident audit ledger |
| _Natural Language_ | Any freeform query is routed directly to the `#invoiceops-ap` room thread |

### Real-Time Push Notifications
When critical AP events occur anywhere across the platform (such as newly flagged 3-way match exceptions, prompt injection attempts quarantined, or authorized payment vouchers sealed), the gateway automatically broadcasts push alerts to all subscribed Telegram chats in real time.

---

## 5. Deployment Options

### Option A: Local Run (Instant)
```bash
python run_app.py
# Or on Windows: double click start.bat
```
Visit: `http://localhost:8000`

### Option B: Docker Compose (Full Stack)
```bash
docker compose up -d
```
Starts:
- `invoiceops-app` (FastAPI + React Workbench) on port `8000`
- `switch-bridge` (Switch Gateway Mock / Event Relay) on port `8080`

Verify health:
```bash
curl -f http://localhost:8000/health
curl -f http://localhost:8000/api/v1/switch/status
```

### Option C: Kubernetes (Enterprise)
```bash
kubectl apply -f deploy/k8s/deployment.yaml
```

---

## 6. Judge Verification Walkthrough

To verify the collaborative multi-agent workflow in under 60 seconds:

1. Open `http://localhost:8000` in your browser.
2. Click **"Switch Room"** in the top navigation bar.
3. Observe the `#invoiceops-ap` active thread for `INV-2026-1042`:
   - **Step 1**: `invoiceops-intake` extracted the invoice from Acme Supplies.
   - **Step 2**: `invoiceops-reconcile` detected the +₹400 line-item price mismatch and mentioned `@procurement_owner`.
   - **Step 3**: `procurement_owner` uploaded `Addendum_A42_Overnight_Rate.pdf` authorizing the surcharge.
   - **Step 4**: `invoiceops-reconcile` verified the override and tagged `@finance_approver`.
4. Click **"Run Judge Demo"** to see `finance_approver` approve the invoice, generating downstream payment-ready record `PR-INV-2026-1042` with zero payment execution capability.
5. Click **"MCP / Connectors"** to view live tool manifests and CLI commands for Claude Code and OpenAI Codex.

