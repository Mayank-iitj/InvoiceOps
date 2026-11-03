# 01 — Product Requirements Document (PRD)

**Product:** InvoiceOps  
**Release:** Hackathon MVP 1.0  
**Track:** Best Business Workflow  
**Owner:** Project team  
**Status:** Ready for implementation

## 1. Executive summary

InvoiceOps is a collaborative accounts-payable (AP) exception-resolution workflow. It coordinates AP, procurement and finance employees with specialist AI agents in a Switch room. The system extracts invoice fields, compares the invoice with its purchase order (PO) and goods-receipt note (GRN), detects duplicates and mismatches, routes unresolved questions to the right person, records human decisions and produces a payment-ready record after approval.

InvoiceOps is not a payment processor. It does not initiate bank transfers, approve invoices autonomously or claim to perform legal/tax compliance. Its output is an evidence-backed, auditable AP decision and a record ready for a downstream payment system.

## 2. Problem statement

In small and mid-sized businesses, invoice handling frequently crosses separate roles and records. An AP employee may have an invoice but not know whether the goods were received. Procurement may know the PO amendment but not see the invoice. Finance may receive a request with no clear evidence trail. The result is manual back-and-forth, duplicated checks, delayed approvals and accidental payment risk.

The core problem is not PDF extraction alone. It is **coordination across people, records and decisions**. InvoiceOps makes that coordination explicit in a shared Switch room and uses deterministic software for financial checks.

## 3. Target users and jobs-to-be-done

| Persona | Job to be done | Needs |
|---|---|---|
| AP Clerk | Process supplier invoices consistently | Intake, evidence, queue, clear exception reasons and audit trail |
| Procurement Owner | Confirm PO terms, receipt quantity or delivery discrepancy | Focused question, linked PO/GRN evidence, reply in same room |
| Finance Approver | Decide whether a reconciled payable can move forward | Trusted comparison, exception status, supporting evidence and approval history |
| AP Operations Lead | Monitor throughput and bottlenecks | Queue states, ageing, exceptions and measurable processing time |
| Invoice Intake Agent | Extract candidate data from invoice documents | Restricted document access, structured schema and confidence/evidence capture |
| Reconciliation Agent | Run/interpret deterministic matching and coordinate exceptions | Read-only source records, match tool and permission to request human input |

## 4. Product principles

1. **People own consequential decisions.** No agent may approve, reject, release or pay an invoice.
2. **Evidence before assertions.** Each extracted value and match result must point to a document/source record or be marked unknown.
3. **Deterministic financial logic.** Amounts, quantities, duplicate detection, thresholds and state transitions are computed in application code.
4. **Switch is the work room.** Human/agent collaboration and handoffs occur in Switch; the web app is the thin evidence workbench.
5. **Fail closed.** Missing or ambiguous records produce a hold/exception, not an assumed pass.
6. **Reproducible demo.** Synthetic fixtures and local setup must work without real accounting, banking or vendor credentials.

## 5. Goals and non-goals

### Goals

- Process a seeded invoice end-to-end with a person and at least one AI agent in Switch.
- Demonstrate at least two distinct agent responsibilities.
- Detect quantity/price discrepancies by matching invoice, PO and GRN.
- Detect exact and normalized duplicate invoices.
- Route operational exceptions to a named human role.
- Require human finance approval before a payment-ready record is created.
- Persist case status, evidence, decision and audit events.
- Provide a reproducible local demo with expected test outcomes.

### Non-goals

- Sending money or connecting to banks/payment rails.
- Replacing an ERP, accounting package or procurement suite.
- Legal/tax advice or a complete GST compliance assessment.
- Automatically sending supplier emails or changing vendor banking information.
- Multi-company SaaS tenancy in the hackathon MVP.
- Arbitrary agent access to source documents, shell, database or financial credentials.

## 6. Primary workflow

1. AP Clerk creates an invoice case and attaches the invoice document.
2. AP Clerk posts `@invoiceops-intake Please extract INV-...` in `#invoiceops-ap`.
3. Intake Agent extracts candidate fields and line items, associates each with page/line evidence and reports low-confidence fields.
4. Reconciliation Agent invokes deterministic three-way matching against PO and GRN records.
5. If matched, agent posts a concise match summary and requests finance review.
6. If an exception exists, agent names the exception, posts the exact discrepancy and tags the responsible human (for example, Procurement Owner).
7. Human adds a verified fact or uploads/links the missing record; the AP Clerk records the confirmation in InvoiceOps.
8. Reconciliation Agent reruns matching and reports the before/after result.
9. Finance Approver reviews evidence and approves or rejects in the controlled approval action; the decision is also summarized in the Switch thread.
10. Backend creates `payment_ready` only after all guards pass. It creates no bank transaction.

## 7. Functional requirements

Priority legend: **P0** required for judging demo; **P1** valuable if time permits; **P2** post-hackathon.

| ID | Requirement | Priority | Acceptance evidence |
|---|---|---:|---|
| FR-01 | Create an invoice case with vendor, invoice number, date, currency, amount and PO reference | P0 | Case appears in queue and DB |
| FR-02 | Attach a PDF/image or load a seeded document record | P0 | Document linked to case; checksum retained |
| FR-03 | Extract header and line-item fields to a typed schema | P0 | Structured extraction plus source evidence and confidence |
| FR-04 | Compare invoice lines against PO lines and accepted GRN quantities | P0 | Deterministic match report with pass/fail/unknown per check |
| FR-05 | Detect duplicate invoice using vendor + normalized invoice number and document hash | P0 | Duplicate case is blocked from approval |
| FR-06 | Create named exceptions for missing GRN, quantity mismatch, price mismatch, tax arithmetic mismatch and duplicate | P0 | Exception visible in API/UI and Switch summary |
| FR-07 | Route exception to a human owner through Switch | P0 | Human reply appears in same room/thread |
| FR-08 | Store human evidence/confirmation and rerun matching | P0 | Before/after report and audit event |
| FR-09 | Require an authorized human approver | P0 | Agent identity receives 403 for approval |
| FR-10 | Create payment-ready record only after checks and approval pass | P0 | DB row created; no payment provider call exists |
| FR-11 | Append audit events for state-changing operations | P0 | Case timeline shows actor/action/time/result |
| FR-12 | Show AP work queue and case detail | P0 | Working thin web UI |
| FR-13 | Export a payment-ready CSV for downstream review | P1 | Export contains approved rows only |
| FR-14 | Track time from intake to resolution | P1 | Derived elapsed time per case |
| FR-15 | Add a second room for supplier follow-up | P2 | Not required for MVP |

## 8. Non-functional requirements

| Area | Requirement |
|---|---|
| Reliability | No partial approval state; use DB transactions for approval/finalization |
| Safety | No autonomous approval, vendor-master changes, bank changes or payments |
| Security | Role-scoped API keys/JWT; least privilege; redact secrets; no agent admin token |
| Auditability | Append-only event records for extraction, match, human response, approval and finalization |
| Performance | Seeded case list <1 second locally; match computation <2 seconds for typical demo dataset |
| Usability | A reviewer can understand why a case is held within 30 seconds |
| Reproducibility | One documented local startup command after dependencies are installed |
| Accessibility | Keyboard-accessible controls, visible focus, semantic labels, WCAG AA contrast target |
| Portability | SQLite for demo; avoid SQLite-only semantics in domain/business layer |

## 9. State model and business outcomes

- `draft`: invoice case created, required data incomplete.
- `received`: source document attached and case ready for extraction.
- `extracting`: extraction job in progress.
- `needs_review`: mandatory extracted field has low confidence or conflicting values.
- `reconciling`: match engine running.
- `exception_open`: one or more blocking exceptions exist.
- `awaiting_human`: a named business fact or evidence is needed.
- `ready_for_approval`: no blocking exceptions; all required checks passed.
- `approved`: authorized finance approver approved the case.
- `payment_ready`: downstream-ready record created; no payment executed.
- `rejected`: finance approver rejected the case.
- `vendor_correction_required`: invoice must be corrected by supplier before processing.
- `duplicate_blocked`: duplicate rule prevented processing.

No transition may jump from `received`, `exception_open` or `ready_for_approval` directly to `payment_ready` without the required extraction, match and approval checks.

## 10. Success metrics

Do not invent impact claims. Measure these on the included synthetic test set and report the dataset size:

- Extraction field accuracy = correctly extracted required fields / fields reviewed.
- Three-way match accuracy = correct fixture outcomes / total fixtures.
- Duplicate recall and precision on labeled duplicate/non-duplicate fixtures.
- Exception routing correctness = correctly routed exceptions / routed exceptions.
- Human handoff count per case and time from case creation to resolution.
- Approval control test: zero agent-identity approvals accepted.
- Reproducibility: clean clone-to-demo success rate across at least two test runs.

The demo may show measured results only after running the tests. Avoid claiming company-wide savings based on synthetic records.

## 11. MVP acceptance criteria

The MVP is accepted when:

- [ ] A judge can start the app using the README.
- [ ] Switch room includes at least one human and two distinct agents.
- [ ] Intake agent extracts an invoice case and identifies uncertainty honestly.
- [ ] Matching agent runs deterministic invoice/PO/GRN checks.
- [ ] Quantity mismatch is routed to Procurement and remains blocked until a human response is recorded.
- [ ] Duplicate invoice is blocked.
- [ ] Finance Approver can approve a fully reconciled case.
- [ ] Agent approval attempt is denied and audited.
- [ ] A payment-ready record is persisted only after approval.
- [ ] The final record and audit trail can be shown on screen.
- [ ] No real money movement, email sending or external financial credential is required.
