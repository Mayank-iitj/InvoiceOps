# InvoiceOps

Collaborative AP invoice exception resolution using Switch, people and AI agents.

## Demo boundary

InvoiceOps extracts and reconciles supplier invoices against purchase orders and goods-receipt records, coordinates human exception resolution in a Switch room, and creates an auditable payment-ready record after human finance approval. **It does not initiate payments.** All included records are synthetic.

## Architecture

[Insert the architecture diagram from `docs/03_SYSTEM_DESIGN.md`]

## Prerequisites

[Insert tested versions of Python, Node, Docker and Switch Console.]

## Quick start

[Insert only commands verified against the current repository.]

## Switch setup

1. Install Switch Console and start local Switch.
2. Open bundled Mattermost.
3. Create `#invoiceops-ap` using `switch/invoiceops-room.template.yaml` as the blueprint.
4. Add agents with instructions in `agents/`.
5. Configure restricted InvoiceOps API/CLI access for each agent.
6. Verify a real mention/response and a human handoff.

## Demo cases

- `INV-2026-1041`: synthetic fully matched invoice; finance approval creates a payment-ready record.
- `INV-2026-1042`: synthetic quantity mismatch; invoice qty 10 vs accepted GRN qty 8; blocks approval until further evidence/correction.

## Tests

[Insert verified test command and actual outcome.]

## Safety and limitations

- No bank integration, transfer, supplier email sending or vendor bank-data update.
- Finance approval is human-only and enforced in the backend.
- OCR/model extraction is a proposal; matching and arithmetic are deterministic.
- Synthetic data only; not a production accounting system or tax/legal compliance product.

## How Switch is used

[Explain which actions occur in the Switch room, agent responsibilities, human roles, room instructions and how the workflow would fail without Switch. Include screenshots/video.]
