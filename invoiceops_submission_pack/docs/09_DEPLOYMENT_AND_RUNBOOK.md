# 09 — Deployment and Runbook

## 1. Local demo target

A judge should be able to run InvoiceOps on a laptop with a single local database and synthetic records. Switch is installed and run separately using the official Switch Console quickstart and bundled Mattermost path.

## 2. Prerequisites

- Git
- Python 3.12+
- Node.js LTS and npm/pnpm
- Docker Desktop or compatible runtime for Switch Console's local server
- Switch Console and one supported agent provider configured

Current Switch quickstart notes: local Switch runs its server in Docker and includes Mattermost; Switch does not include an agent/model, so the builder supplies an agent and provider credentials. Confirm the latest platform support for your OS before the demo.

## 3. Suggested repository commands

The implementation team should provide these commands and keep README aligned with actual scripts:

```bash
# clone
 git clone <PUBLIC_REPOSITORY_URL>
 cd invoiceops

# backend
 python -m venv .venv
 # Windows PowerShell: .venv\\Scripts\\Activate.ps1
 # macOS/Linux: source .venv/bin/activate
 pip install -e ".[dev]"
 cp .env.example .env
 python -m invoiceops.db seed
 uvicorn invoiceops.main:app --reload --port 8000

# frontend (second terminal)
 cd frontend
 npm ci
 npm run dev
```

Do not publish this runbook until the commands match the real repository.

## 4. Switch setup

1. Install the current Switch Console release from the official resources page.
2. Start Docker and choose the local Switch server path.
3. Sign into the bundled Mattermost instance.
4. Configure the chosen AI agent provider; do not store its credential in the repository.
5. Create the `invoiceops-ap` room using the provided template blueprint and add the AP Clerk, Procurement Owner and Finance Approver demo users.
6. Add `invoiceops-intake` and `invoiceops-reconcile` agents with the instructions in `agents/`.
7. Give each agent only the InvoiceOps CLI/API capability required by its role.
8. Attach the invoice-processing runbook and demo matching policy as room materials where the current Switch UI supports it.
9. Test that both agents can read the room context and reply to explicit mentions.
10. Record a short test conversation before the actual demo.

## 5. Seed data and reset

Provide:

```bash
python -m invoiceops.db reset-demo
python -m invoiceops.db seed
python -m invoiceops.db status
```

Reset must operate only on the local demo database and synthetic fixture directory. It must not target a remote/prod database.

## 6. Health and diagnostics

- `GET /api/v1/health` returns `{ "status": "ok", "version": "..." }`.
- `GET /api/v1/invoices` should show seeded cases.
- Check API logs for request ID and actor ID, not file contents.
- If Switch agent is silent, verify the room mention uses the exact agent name and the agent is connected. Confirm the Switch Console/provider session is running.
- If agent tool call fails, run the corresponding InvoiceOps CLI command manually and preserve the failure in the demo; do not claim a successful agent action.

## 7. Demo day checklist

- [ ] Laptop power and network.
- [ ] API and frontend start cleanly.
- [ ] Switch server is running and Mattermost room is accessible.
- [ ] Agent providers are signed in and agents respond.
- [ ] DB seeded and exact fixture IDs checked.
- [ ] No real credentials or production records visible.
- [ ] Two test runs completed before recording.
- [ ] Backup screen recording available in case live provider latency occurs.
