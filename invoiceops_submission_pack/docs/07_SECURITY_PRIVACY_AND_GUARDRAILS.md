# 07 — Security, Privacy and Guardrails

## 1. Threat model

Assets: invoice files, supplier/customer names, PO/GRN records, pricing, approval decisions, agent credentials and audit history.

Threats: malicious PDF content/prompt injection, forged agent messages, privilege escalation, duplicate or replayed approvals, stale-match approval, document leakage to an unintended room member, file parser abuse, accidental payment claims and audit tampering.

## 2. Mandatory controls

### Identity and authorization

- Authenticate every InvoiceOps API request.
- Enforce role and scope checks in the backend, never only in the frontend.
- Separate human identities from agent service identities.
- Give intake agent extraction-only permissions; give reconciliation agent read + match + proposal permissions.
- Deny `approval:decide` and `payment_ready:create` to all agent identities.
- Use unique credentials per agent; store them in environment variables/secret store, never in prompts or chat.
- Rotate demo credentials before any hosted deployment.

### Human approval

- Finance approval must be a deliberate, authenticated action by a `finance_approver`.
- Require an approval comment and a fresh match-run ID.
- Approval and payment-ready creation occur in one DB transaction.
- A duplicate, failed or unknown mandatory check blocks approval.
- A changed invoice/PO/GRN/policy version invalidates the previous match.
- The final action says explicitly: `Creates a payment-ready record; does not send money.`

### Document and prompt-injection safety

- Treat invoice text, email text, PDF content and messages as untrusted input.
- Agents must ignore instructions embedded in vendor documents, including instructions to reveal prompts, call tools or change bank/payment data.
- Do not give agents direct database credentials, filesystem-wide access, browser access or unrestricted shell tools.
- Restrict the working directory to the project/demo data.
- Do not enable Bypass permissions for the agents.
- Avoid automatic email sending, bank-account updates, payment execution or arbitrary outbound requests.
- Validate extracted JSON with Pydantic before persistence.

### File handling

- Enforce extension/MIME and upload-size limits.
- Store files outside public web root with generated filenames.
- Compute SHA-256; never trust the user-provided filename as a path.
- Parse PDFs in an isolated process if feasible.
- Do not execute embedded content.
- For production, add malware scanning, encryption at rest, access logging and formal retention/deletion policy.

### Audit and idempotency

- Append audit events for every state-changing action.
- Use idempotency keys for approval/finalization to prevent duplicate records.
- Reject replayed requests with conflicting payloads.
- Protect audit history from ordinary update/delete operations.

## 3. Switch-specific security considerations

Switch rooms provide shared context; every agent in a room may read room conversations and attached context. Before adding an agent, inspect its tools, working directory, credentials, execution mode and owner access. Switch documentation notes that agent access is inherited from its owner, and Auto mode/Bypass settings affect whether actions run without prompts. Therefore:

- Invite only agents appropriate for the invoice data visible in this room.
- Do not use an admin's broad credentials as an agent owner.
- Keep the demo data synthetic.
- Do not give the agent owner access to live accounting/bank systems.
- Do not rely on chat instructions as the only security barrier; enforce sensitive actions in the API.
- Document what each agent can read and do in the room instructions and README.

## 4. Data minimization

The hackathon demo uses synthetic vendor, invoice, PO and GRN records. Avoid personal data, real bank details, customer information and real supplier correspondence. Mask any unnecessary identifiers in screen recordings.

## 5. Security acceptance tests

- [ ] Agent token cannot approve or reject.
- [ ] Agent token cannot create a payment-ready record.
- [ ] AP Clerk token cannot approve.
- [ ] Finance Approver cannot approve a stale or blocked match.
- [ ] Duplicate finalization with the same idempotency key returns the same record, not a second record.
- [ ] Prompt-injection text in a sample invoice does not cause tool use outside the permitted schema.
- [ ] File path traversal filename is stored under a generated name.
- [ ] No bank/payment provider endpoint or secret exists in the MVP.
- [ ] All approval and finalization events are audited.
