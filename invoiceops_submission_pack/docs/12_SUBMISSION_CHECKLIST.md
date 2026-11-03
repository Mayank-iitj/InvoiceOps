# 12 — Submission Checklist

## A. Track fit

- [ ] Submit under **Track 01 — Best Business Workflow**.
- [ ] State the business problem, the people involved and the real task completed.
- [ ] Explain how Switch connects the human team and agents.
- [ ] Show a full task lifecycle, not a chatbot-only interaction.

## B. Switch proof (highest weight)

- [ ] At least one human and one AI agent visibly collaborate in a Switch room; recommended demo has three human roles and two agents.
- [ ] Switch is central to the workflow; agents receive work and post evidence in the shared room.
- [ ] Room instructions and shared context are configured.
- [ ] Agent roles are distinct and documented.
- [ ] README explains Switch setup, room configuration, agent names, agent permissions and how to replay the workflow.
- [ ] Show at least one explicit human handoff and one human approval.
- [ ] Do not present an app-side chat replica as Switch usage.

## C. Technical execution

- [ ] Public repository is accessible.
- [ ] `.env.example` contains placeholders only.
- [ ] Dependency lockfiles committed.
- [ ] Seed/reset commands work.
- [ ] Clean clone-to-run smoke test completed.
- [ ] Unit/integration/authorization tests pass.
- [ ] OpenAPI and DB schema match implementation.
- [ ] No hardcoded secrets, real financial data or production credentials.
- [ ] Failure paths are visible and do not silently claim success.

## D. Business impact and differentiation

- [ ] Explain that this is AP invoice exception resolution, not payment initiation or an engineering payments-room clone.
- [ ] Show invoice/PO/GRN mismatch with a measurable discrepancy.
- [ ] Show procurement and finance responsibilities.
- [ ] Show duplicate detection or second exception case.
- [ ] Explain why a chat-only generic agent is insufficient: the workflow needs deterministic data checks, assigned human owners, guarded approval and persisted outcomes.

## E. Presentation

- [ ] Demo starts with the problem and ends with a persisted output.
- [ ] Switch room shown on screen throughout the core workflow.
- [ ] Demo data labeled synthetic.
- [ ] Narration says what is deterministic and what is model-assisted.
- [ ] Final screen shows audit trail and explicit no-payment boundary.
- [ ] README includes architecture diagram, run commands, sample commands, screenshots/video link and limitations.
- [ ] Submit before the official deadline: 7 November 2026, 11:59 PM IST.

## F. Final release gate

Do not submit until these six things are true:

1. The project runs from a clean checkout.
2. Switch room contains the agents and human participants.
3. A mismatch is found, routed to a human, and resolved with evidence.
4. A finance human can approve a clean case.
5. An agent cannot approve or create a payment-ready record.
6. The final output persists and is visible in the audit log.
