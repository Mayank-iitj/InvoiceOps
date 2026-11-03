# 10 — Four-Day Build Plan

**Event dates:** 4–7 November 2026 IST.  
**Delivery strategy:** one end-to-end vertical slice first; polish only after it works.

## Day 0 — 3 November (preparation)

- Read current Switch quickstart and confirm local Switch/Mattermost startup on the target machine.
- Create public repo structure and add docs.
- Decide one agent provider that is already available; do not start provider migration.
- Prepare synthetic fixtures and demo script.
- Create GitHub issues/tasks from this plan.

## Day 1 — 4 November: Domain backbone + Switch room

**P0 tasks**
- Create FastAPI app, DB schema, seed command and health endpoint.
- Implement invoice list/detail and case creation.
- Implement document metadata/upload and SHA-256 checksum.
- Implement deterministic duplicate check and three-way match service.
- Start Switch + Mattermost; create `#invoiceops-ap` room.
- Onboard two agents and validate human mention/agent response.

**Exit gate:** one fixture can be loaded, reconciled and reported in Switch by an agent.

## Day 2 — 5 November: Extraction and human handoff

- Implement document text extraction and extraction proposal schema.
- Add source evidence and confidence.
- Implement exceptions and ownership mapping.
- Write agent role prompts and tool/CLI permissions.
- Demonstrate quantity mismatch routed to Procurement.
- Record human confirmation and rerun match.

**Exit gate:** mismatch does not get silently approved; human confirmation changes the deterministic result.

## Day 3 — 6 November: Approval, audit and workbench

- Implement role/scope authorization.
- Implement finance approve/reject flow and stale-match guards.
- Implement payment-ready record creation (no payment execution).
- Implement audit timeline.
- Build inbox, invoice detail and approval review UI.
- Add tests T-01, T-02, T-06, T-10, T-12 and T-13.

**Exit gate:** one valid invoice reaches payment-ready only after human approval; blocked case remains blocked.

## Day 4 — 7 November: Hardening and submission

- Run full scenario matrix and fix critical bugs.
- Verify clean clone-to-run setup.
- Finalize public README, screenshots and demo video.
- Verify Switch is visibly central in video.
- Prepare submission text and submit before 11:59 PM IST.
- Keep buffer for provider/network hiccups; do not add new major features.

## Task priority if time slips

1. Working Switch room + agents + human handoff.
2. Deterministic three-way match + duplicate detection.
3. Finance approval guard + payment-ready record.
4. Audit trail.
5. Clean UI.
6. Optional export, metrics dashboard, OCR for image-only docs.

A complete vertical slice wins over a large incomplete feature list.
