# InvoiceOps Tool Contract for Switch Agents

These are proposed InvoiceOps CLI commands backed by the API in `schemas/openapi.yaml`. Implement the CLI or equivalent MCP tools; these names are not native Switch operations.

| Tool | Intake Agent | Reconciliation Agent | Human |
|---|---:|---:|---:|
| `invoiceops case show <id>` | Yes | Yes | Yes |
| `invoiceops document get-text <document_id>` | Yes | Yes | Yes |
| `invoiceops extraction propose <case_id> --json <file>` | Yes | No | AP Clerk can correct/confirm |
| `invoiceops match run <case_id>` | No | Yes | AP Clerk can trigger |
| `invoiceops match latest <case_id>` | Yes | Yes | Yes |
| `invoiceops exception list <case_id>` | Yes | Yes | Yes |
| `invoiceops exception proposal create ...` | No | Yes | Yes |
| `invoiceops evidence attach ...` | No | No | AP/Procurement |
| `invoiceops approval decide ...` | No | No | Finance Approver only |
| `invoiceops payment-ready create ...` | No | No | Finance Approver/service only after approval |

The server must enforce these permissions even if an agent calls an endpoint directly.
