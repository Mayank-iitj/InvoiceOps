# 11 — Demo Pitch and Script

## 1. Positioning statement

**InvoiceOps turns invoice exceptions from scattered email-and-spreadsheet work into a shared, evidence-backed workflow where people and AI agents resolve the case together in Switch.**

## 2. 30-second pitch

Accounts-payable work often stalls when an invoice, purchase order and goods-receipt record disagree. AP cannot resolve that alone; procurement knows what arrived, and finance owns the approval. InvoiceOps brings those people and specialist AI agents into one Switch room. Agents extract and reconcile evidence, route the exact discrepancy to the right human, rerun deterministic checks after confirmation, and prepare an auditable payment-ready record only after a finance approver signs off. It never moves money.

## 3. Recommended demo story (2–3 minutes; recommended duration, not an official event limit)

### Scene A — Show the real work (15–20 seconds)

Open `#invoiceops-ap` in Mattermost through Switch. Explain that this is the working room, not a notification mirror. Show AP Clerk, Procurement Owner, Finance Approver and the two agents as participants.

### Scene B — Invoice extraction (20–30 seconds)

AP Clerk posts: `@invoiceops-intake Please extract INV-2026-1042. Use the attached case and report unknown fields honestly.`

Show the agent report with invoice number, vendor, date, PO reference, line items and source evidence. Point out that extracted values are proposals until confirmed.

### Scene C — Find a real exception (25–35 seconds)

AP Clerk posts: `@invoiceops-reconcile Run the three-way match for INV-2026-1042.`

Show deterministic result: invoice quantity 10, PO quantity 10, accepted GRN quantity 8. Exception `QTY_EXCEEDS_RECEIVED`; approval blocked. Explain that the LLM does not decide the number — the backend computes it.

### Scene D — People and agents collaborate (25–35 seconds)

Reconciliation Agent tags Procurement Owner with the specific question. Procurement confirms that only eight units were accepted and that the supplier must correct the invoice (or provides a second GRN if one exists). AP Clerk records the verified evidence and asks for a rerun.

### Scene E — Re-run and approve (25–35 seconds)

Show the corrected fixture / receipt evidence, new match run and `PASS`. Finance Approver reviews the evidence and approves. Show that an agent cannot approve (optional short test).

### Scene F — Tangible completion (15–20 seconds)

Show the persisted payment-ready record and audit timeline. Say clearly: `The invoice is now ready for the downstream payment process. InvoiceOps has not sent money.`

## 4. Required screenshots/video evidence

- Switch room with humans and agents visible.
- Intake agent extraction with source evidence.
- Match agent's exception and human handoff.
- Human response in the same room/thread.
- Finance approval.
- Final payment-ready record and audit event.
- Thin workbench invoice comparison.

## 5. Suggested live room messages

```text
@invoiceops-intake Extract INV-2026-1042. Return the fields, source page/line evidence, confidence and any unknown values. Do not infer missing fields.

@invoiceops-reconcile Run the three-way match for INV-2026-1042 using the current PO and accepted GRN records. Report each check and route every blocking exception to its human owner. Do not approve or create payment-ready records.

@invoiceops-reconcile Re-run INV-2026-1042 after the procurement confirmation has been recorded. Compare the latest result with the prior match run.
```

## 6. What to emphasize to judges

- Switch is essential because coordination, task routing and shared context happen in its room.
- The people are not decorative: Procurement supplies operational facts; Finance owns the approval.
- Agents have different responsibilities and constrained tools.
- Financial logic is deterministic and reproducible.
- The finished result is a database record with an audit trail, not only a chat response.
- The product never claims a payment was made.

## 7. Avoid saying

- “We automate all accounts payable.”
- “We save 80% of finance time” unless measured in a real pilot.
- “The agent verifies legal GST compliance.”
- “Payment completed” when only a ready record exists.
- “Production-ready” if only synthetic fixtures were tested.
