# InvoiceOps — Flip the Switch Hackathon Submission Pack

**Track:** Best Business Workflow (Track 01)  
**Product:** InvoiceOps — collaborative accounts-payable exception resolution  
**Document status:** Build-ready specification, version 1.0  
**Prepared:** 3 November 2026  
**Hackathon window:** 4–7 November 2026 (IST)

> **Core promise:** A person and AI agents, collaborating in a Switch room, take a supplier invoice from receipt through evidence-backed reconciliation and an explicitly approved payment-ready record.

## Read this first

This package is an implementation specification, not a claim that the product has already been built or deployed. It deliberately separates:

- **Confirmed Switch facts:** derived from the official hackathon page and current Switch documentation linked in `docs/15_SOURCES_AND_ASSUMPTIONS.md`.
- **InvoiceOps design decisions:** proposed interfaces, database tables, API endpoints, policy rules and UX that must be implemented and tested by the project team.
- **Demo data:** fully synthetic records included under `fixtures/`; never represent them as customer or production data.

## The product in one sentence

InvoiceOps coordinates AP staff, procurement staff, finance approvers and AI agents in one Switch room to verify invoices against purchase orders and goods-receipt records, resolve exceptions and produce an auditable payment-ready record without moving money.

## Why this is Track 01

The user-facing work happens in a team chat room connected by Switch. A human opens and owns a case; agents investigate different parts of it; a human supplies missing operational facts; a finance approver makes the consequential decision; the application persists the outcome. Switch is the collaboration and handoff layer, not a decorative notification channel.

Official judging criteria on the event page:

| Criterion | Weight | Proof to show |
|---|---:|---|
| Use of Switch | 30% | Shared room, human/agent handoffs, room instructions/context and task completion through chat |
| Technical execution | 25% | Reproducible clone-and-run setup, deterministic matching, persisted records, tests and safe state transitions |
| Creativity and impact | 25% | Real AP exception workflow with procurement/finance handoffs, not a generic chatbot |
| Presentation | 20% | Clear README, short demo, visible Switch usage and tangible output |

## Strict MVP boundary

**Build:** invoice intake, document extraction, three-way match, duplicate detection, exception routing, human confirmation, approval, payment-ready record, audit trail, one Switch room and two distinct agents.

**Do not build:** bank connectivity, payment initiation, full ERP, real email sending, GST/legal compliance engine, vendor portal, multi-tenant enterprise admin, autonomous financial approval, or a custom chat application.

## Package map

| File | Purpose |
|---|---|
| `docs/01_PRD.md` | Problem, personas, requirements, scope, user stories and acceptance criteria |
| `docs/02_TRD.md` | Stack, implementation constraints, runtime and operational requirements |
| `docs/03_SYSTEM_DESIGN.md` | Architecture, workflows, state machine, sequence and data flows |
| `docs/04_UX_UI_DESIGN.md` | Design system, information architecture, screens and interactions |
| `docs/05_API_DESIGN.md` | API conventions, resources, permissions and endpoint behavior |
| `docs/05A_API_EXAMPLES.md` | Example API requests and responses |
| `schemas/openapi.yaml` | OpenAPI 3.1 contract for the InvoiceOps backend |
| `schemas/schema.sql` | Proposed relational schema (SQLite-compatible baseline) |
| `docs/06_DATA_AND_MATCHING_RULES.md` | Data dictionary, matching logic, tolerances and state invariants |
| `switch/invoiceops-room.template.yaml` | Switch room/agent template blueprint based on the event's published format |
| `agents/*.md` | Role-specific agent system instructions |
| `docs/07_SECURITY_PRIVACY_AND_GUARDRAILS.md` | Threat model, access controls, prompt-injection and financial safety controls |
| `docs/08_TEST_AND_EVALUATION_PLAN.md` | Functional, security, integration and evaluation tests |
| `docs/09_DEPLOYMENT_AND_RUNBOOK.md` | Local demo setup, configuration and operations runbook |
| `docs/10_BUILD_PLAN.md` | Four-day implementation plan and critical path |
| `docs/11_DEMO_PITCH_AND_SCRIPT.md` | Story, spoken demo and proof points |
| `docs/12_SUBMISSION_CHECKLIST.md` | Final judging and release checklist |
| `docs/13_CODING_AGENT_MASTER_PROMPT.md` | Master prompt to implement the documented MVP |
| `docs/14_RISK_REGISTER.md` | Delivery, product and technical risks |
| `docs/15_SOURCES_AND_ASSUMPTIONS.md` | Official references and facts/assumptions ledger |
| `docs/16_PROBLEM_VALIDATION_AND_BUSINESS_CASE.md` | Validation hypotheses, interview guide and ROI measurement formula |
| `fixtures/` | Synthetic business records and expected outcomes |
| `implementation_prompts/` | Focused coding prompts by workstream |

## Recommended implementation stack

- Frontend: React + TypeScript + Vite + Tailwind CSS + shadcn/ui (or equivalent accessible component primitives).
- Backend: Python 3.12+ + FastAPI + Pydantic v2 + SQLAlchemy 2.
- Database: SQLite for zero-friction judging/demo; keep SQL portable and provide PostgreSQL migration path.
- Document extraction: PyMuPDF for text-based PDFs; optional OCR adapter for images/scans. Always preserve extracted values as untrusted proposals until validated.
- Matching: deterministic Python domain service; no LLM arithmetic or eligibility decisions.
- Agent access: narrow InvoiceOps API/CLI tools; standard agents onboarded via Switch Console for the MVP. A custom Switch agent client is optional, not required.
- Collaboration: Switch + bundled Mattermost for the demo; a single `#invoiceops-ap` room.

## First implementation decision

Use the bundled Mattermost server through Switch for the demo. Build the workbench only as a thin evidence/status interface; do not rebuild the chat UI. The main workflow must remain in the Switch room.

## Definition of “done”

A judge can clone the public repository, start the app and seeded database, open the Switch room, trigger one valid invoice and one exception case, observe two agents and a human perform the work, approve one case, see a persisted payment-ready record, and inspect the audit trail — without providing real banking credentials or customer data.
