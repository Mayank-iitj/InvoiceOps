# 15 — Sources and Assumptions

**Research checked:** 3 November 2026. Official pages can change; re-check before final submission.

## Official hackathon references

1. Flip the Switch Hackathon overview, track description, criteria, dates and FAQ: https://www.wemakedevs.org/hackathons/switch
2. Flip the Switch resources: https://www.wemakedevs.org/hackathons/switch/resources
3. Official rules: https://www.wemakedevs.org/hackathons/switch/rules
4. Schedule: https://www.wemakedevs.org/hackathons/switch/schedule

## Official Switch technical references

5. Switch quickstart: https://docs.switchagents.ai/switch-rooms/getting-started
6. Agent protocol: https://docs.switchagents.ai/switch-rooms/internals/agent-protocol
7. Build a payments room: https://docs.switchagents.ai/switch-rooms/building/payments-room
8. Create a room: https://docs.switchagents.ai/switch-rooms/getting-started/create-a-room
9. Add a custom agent: https://docs.switchagents.ai/switch-rooms/getting-started/add-a-second-agent
10. Share context: https://docs.switchagents.ai/switch-rooms/using/shared-context
11. Working safely with agents: https://docs.switchagents.ai/switch-rooms/resources/working-safely-with-agents
12. Identity and access: https://docs.switchagents.ai/switch-rooms/internals/identity-and-access

## Facts confirmed from the event and Switch pages

- Track 01 is Best Business Workflow: practical workflows where people and AI agents get work done.
- Judging emphasizes Use of Switch, Technical execution, Creativity and impact, and Presentation.
- Switch is mandatory and must be central; at least one person and one AI agent must complete a real task together in a team-chat workflow.
- The event page lists 4–7 November 2026, with submissions closing 7 November 2026 at 11:59 PM IST.
- The event page lists Mattermost among supported chat surfaces; the quickstart describes a bundled Mattermost instance for a local server.
- Switch rooms are shared workspaces with messages, instructions, roles, tasks/context and shared materials.
- Current agent protocol documentation describes WebSocket connections and HTTP operations. Older SSE support is deprecated.
- Switch agent registration uses a registration credential once; the returned agent API key is used for the agent's later connection and calls. These credentials are not interchangeable.
- Switch agents inherit the access of their owner; Switch docs warn teams to examine working directories, tools, execution mode and owner access.
- Current docs say there is no separate first-class task protocol; agent handoff can be a message/mention or targeted message.

## InvoiceOps design assumptions (not official requirements)

- AP invoice exception resolution is the selected business problem and target workflow.
- React/Vite/FastAPI/SQLite is the recommended hackathon stack, not a requirement from Switch.
- InvoiceOps endpoint paths and database schema are proposed APIs owned by this project; they are not Switch endpoints.
- Matching thresholds are illustrative demo policy values only; each real company must configure its own rules.
- Synthetic business records are included for testing only.
- The package does not guarantee a win. It is designed to align tightly with the published criteria and make the work reproducible and judgeable.

## Differentiation note

Switch's official docs include a **payments room** example focused on a software engineering team building and operating a payments service (repository grounding, code review, release coordination and deploy authority). InvoiceOps is deliberately a different business workflow: accounts-payable invoice matching against PO/GRN evidence, procurement exception resolution and human finance approval. The MVP does not initiate payments.
