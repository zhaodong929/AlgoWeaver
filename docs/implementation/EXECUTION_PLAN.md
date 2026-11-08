# AlgoWeaver Execution Plan

Updated: 2026-11-08 (Asia/Shanghai)

## Current milestone

**Phase 8/9: delivery hardening.** The current deliverable is the inventory-demand
forecasting scenario with CLI, FastAPI, Streamlit, optional live Bailian providers,
Qdrant memory/server modes, isolated execution, bounded repair and verified-only
reuse. The authoritative gaps and their execution order are in
`DELIVERY_GAP_LIST.md`; the next work starts with persistent-Qdrant smoke testing,
the main scenario report, browser acceptance and production boundary checks.

## Milestones

| ID | Milestone | Exit evidence | Status |
|---|---|---|---|
| M0 | Revalidate baseline and project controls | `pytest`, Ruff, Mypy, GPU/uv/Git record | DONE |
| M1 | Multi-source ingestion and provenance | Supported text formats plus lazy Docling adapter, hash, metadata, unsupported/failed boundary tests | IN_PROGRESS |
| M2 | Python AST code parsing | Function/class/import schema, syntax-error behavior, tests | DONE |
| M3 | Evidence-aware extraction | Mock/LLM extraction maps claims to application-controlled source locations and hashes | DONE |
| M4 | Local retrieval baseline | Chunking, deterministic lexical ranking, metadata filters, provenance hits and tests | DONE |
| M5 | Reproduction plan and generated artifacts | Structured plan, evidence IDs, deterministic template, Mock and Pydantic-validated LLM artifact boundary | IN_PROGRESS |
| M6 | Safe validation and bounded repair | Static checks, Docker-only policy boundary, bounded repair orchestration and retry limit | IN_PROGRESS |
| M7 | Capability registry and reuse | SQLite versions, verified-only promotion and name search | IN_PROGRESS |
| M8 | API/demo integration | CLI `reproduce` writes plan, artifacts and static validation reports | IN_PROGRESS |
| M9 | Final acceptance | Requirement matrix audit, security/performance checks, final demo | NOT_STARTED |
| M10 | Delivery gap audit | Updated matrix, primary scenario evidence and actionable backlog | IN_PROGRESS |
| M11 | Production retrieval and UI acceptance | Persistent Qdrant smoke test, automated UI interaction, HTTPS/auth/rate-limit check | IN_PROGRESS |
| M12 | Extended failure repair and cross-scenario validation | Live import/dependency/timeout repair evidence and second public dataset | NOT_STARTED |

## Working rules

- Work only on feature branches; never force-push or merge `main` without explicit confirmation.
- At each milestone run focused tests first, then the full suite and static checks.
- Update `phase_status.md`, `build_log.md`, `known_issues.md`, and the relevant ADR before the milestone commit.
- If an optional dependency is unavailable, implement an explicit boundary or Mock path and continue with independent work.
