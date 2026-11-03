# 14 — Risk Register

| Risk | Likelihood | Impact | Mitigation / fallback |
|---|---|---|---|
| Switch/provider agent fails during live demo | Medium | High | Pre-run, keep backup recording, demonstrate truthful CLI/API fallback; never fake an agent response |
| Switch template format differs from assumptions | Medium | Medium | Treat template as blueprint; validate in current Console and adapt using official quickstart |
| LLM extraction hallucinates an amount | Medium | High | Source evidence, schema validation, confidence threshold, human confirmation, deterministic arithmetic |
| Match rules incorrectly accept invoice | Medium | High | Unit tests, fail-closed unknown states, immutable match versions and stale-result guard |
| Agent gets broad permissions from owner account | Medium | High | Separate low-privilege owner/API credential, inspect tool access and working directory, no bypass mode |
| Uploaded document contains prompt injection | Medium | High | Treat as untrusted, restrict tools, do not give network/bank/email capabilities |
| Scope grows into ERP/dashboard build | High | High | Keep only one room, two agents, one workflow, three screens and synthetic fixtures |
| Demo result cannot be reproduced on judge machine | Medium | High | Lock dependencies, seed/reset, clean-clone smoke test, README with exact commands |
| Financial claims misrepresented | Low | High | State no money moved; call record payment-ready only; publish only measured metrics |
| Data or API token leaked in repo/video | Medium | High | `.env.example`, secret scan, screen review and credential rotation |
| SQLite concurrency behavior differs from production | Medium | Medium | Demo is local single-user workflow; document PostgreSQL path and do not claim production readiness |
| OCR not accurate on scan | Medium | Medium | Use text PDF fixtures for primary demo; route low-confidence scan to human review |
