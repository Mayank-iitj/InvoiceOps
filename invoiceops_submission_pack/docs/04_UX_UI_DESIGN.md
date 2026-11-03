# 04 — UX / UI Design Specification

## 1. UX strategy

The workbench is an **evidence viewer and operational control surface**, not another chat application. Switch/Mattermost remains the shared workspace for messages, agent handoffs and human coordination. The web app answers three questions quickly:

1. What needs attention?
2. What evidence supports the match result?
3. What action is the current human role allowed to take?

## 2. Design direction

- Visual tone: restrained enterprise operations, clear status, high information density without visual noise.
- Primary canvas: warm near-white `#F7F9F8`; cards `#FFFFFF`; ink `#172622`; muted text `#64736E`.
- Primary accent: deep teal `#146B5A`; action accent `#1D806D`.
- Semantic states: success `#23845D`; warning `#B7791F`; danger `#B54747`; info `#3972A8`.
- Typography: Inter or system UI; tabular numerals for money and IDs.
- Radius: 8–12 px. Borders before shadows. Use one main accent and reserve semantic colors for actual states.
- Accessibility: WCAG AA contrast target, keyboard navigation, visible focus rings, semantic tables, non-color state labels.

## 3. Information architecture

- `/inbox` — AP queue and operational summary.
- `/invoices/:invoiceId` — case details, source documents, three-way match and audit timeline.
- `/approvals` — finance approval queue.
- `/vendors` — simple vendor lookup for demo.
- `/settings/policy` — visible demo tolerance policy (read-only or admin-only).
- External deep link — open the relevant Switch room; do not embed a duplicate chat interface.

## 4. Screen 1 — AP Inbox

Top bar: InvoiceOps logo, environment badge (`DEMO`), current user/role, Switch room link.

Summary tiles:
- Needs extraction review
- Open exceptions
- Awaiting human input
- Ready for finance approval
- Payment-ready (not paid)

Queue columns:
- Invoice / vendor
- PO reference
- Invoice date
- Total (INR)
- State
- Age
- Current owner
- Last activity

Filters: state, vendor, assigned role, duplicate-only. Search by invoice number/vendor/PO. Default sort: blocking exceptions then oldest first.

Empty state: explain there are no cases and offer `Load demo cases` or `Create invoice`.

## 5. Screen 2 — Invoice Detail

Header: invoice number, vendor, current state, total, PO link, document count and `Open in Switch` action.

Three-column layout (responsive to stacked sections on mobile):

- **Left — Source evidence:** invoice PDF/image preview, extracted header fields, confidence/evidence markers and document checksum.
- **Center — Three-way comparison:** Invoice vs PO vs GRN table. Show each line with ordered qty, accepted qty, invoice qty, PO unit price, invoice unit price, delta and status. Use `Unknown` rather than blank for missing evidence.
- **Right — Workflow & audit:** owner, current blocker, last match run, approval status and timestamped audit timeline. Include a prominent `Open #invoiceops-ap` link rather than chat transcript duplication.

Primary actions depend on role and state:
- AP Clerk: upload supporting document, confirm extraction, rerun match, request human review.
- Procurement Owner: provide receipt/PO confirmation through the Switch room and attach source record via the workbench.
- Finance Approver: review evidence, approve or reject with mandatory comment.
- Agents: no approval control is rendered for agent identities.

## 6. Screen 3 — Finance Approval Review

Layout:
- Summary strip with invoice, vendor, amount and PO.
- All match checks visible; every blocking exception must be resolved.
- Evidence drawer with source document, PO, GRN and human confirmation references.
- Latest match run ID and data version hash.
- Approval decision controls: `Approve for payment-ready` and `Reject`, both requiring a written reason/comment.
- Confirmation modal clearly says: `This creates a payment-ready record. It does not send money.`

Disable approval if any mandatory check is fail/unknown, a duplicate is unresolved or source versions changed since the last match.

## 7. Screen 4 — Payment-ready Records

Table columns: record ID, invoice, vendor, approved amount, approved by, approved at, status `Ready for downstream payment`, export status. Include an explicit banner: `No payment has been initiated by InvoiceOps.`

## 8. Interaction and content rules

- Always show amount and currency together (`₹1,20,000.00 INR`).
- Don't show a green pass icon without text `Pass`.
- Show a short explanation plus evidence link for every exception.
- Never describe an AI extraction as verified; label it `Agent-extracted` until source validation is complete.
- Show confidence as a supporting signal, not as a substitute for human review.
- Use exact state names in timeline and API output.
- Provide a concise reason when an action is disabled.

## 9. Wireframe — Invoice detail

```text
┌────────────────────────────────────────────────────────────────────────────┐
│ InvoiceOps     DEMO                         #invoiceops-ap  User: AP Clerk │
├────────────────────────────────────────────────────────────────────────────┤
│ INV-2026-1042  Northstar Components          EXCEPTION OPEN     ₹1,41,600 │
│ PO-2026-0082   [Open source invoice] [Open in Switch]                       │
├──────────────────────┬──────────────────────────────┬──────────────────────┤
│ SOURCE EVIDENCE      │ THREE-WAY MATCH               │ WORKFLOW             │
│                      │                              │                      │
│ Invoice PDF          │ Line / SKU                    │ Current owner        │
│ page 1               │ Invoice | PO | GRN            │ Procurement          │
│                      │ Qty 10   | 10 | 8              │                      │
│ Invoice number       │ Price 12k | 12k | n/a          │ QTY_EXCEEDS_RECEIVED │
│ Vendor               │ Result: BLOCKED               │                      │
│ Date                 │                              │ Audit timeline       │
│ Total                │ Evidence refs: PO, GRN, PDF   │                      │
│ Extraction confidence│                              │ [Open Switch thread]  │
│                      │                              │                      │
├──────────────────────┴──────────────────────────────┴──────────────────────┤
│ Approval unavailable: accepted GRN quantity is below invoice quantity.    │
└────────────────────────────────────────────────────────────────────────────┘
```

## 10. Responsive behavior

- Desktop: three-column invoice detail and full table.
- Tablet: evidence and comparison stacked; workflow rail collapses to a compact summary.
- Mobile: single column, sticky state/action header; wide match table horizontally scrollable with accessible row labels.

## 11. UX acceptance checklist

- [ ] An AP Clerk identifies the top blocking case within 10 seconds.
- [ ] A judge can find the evidence behind a mismatch without leaving the case.
- [ ] The UI clearly distinguishes agent suggestion from human-confirmed fact.
- [ ] A finance approver understands that approval creates a payment-ready record, not a bank transfer.
- [ ] An agent cannot see or invoke an approval control.
- [ ] Switch is one click away and remains the place for conversation/handoff.
