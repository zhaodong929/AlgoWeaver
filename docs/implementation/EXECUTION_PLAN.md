# AlgoWeaver Execution Plan

Updated: 2026-11-08 (Asia/Shanghai)

## Current milestone

**Phase 9: final delivery audit.** The inventory-demand forecasting scenario now has
CLI, FastAPI, Streamlit, live Bailian boundaries, persistent Qdrant service evidence,
isolated execution, bounded repair, verified reuse and JSON-LD graph export. The
remaining work is deployment-specific: public DNS/ACME, manual browser inspection and
broader retrieval/document evaluation. The authoritative list is
`DELIVERY_GAP_LIST.md`.

## Milestones

| ID | Milestone | Exit evidence | Status |
|---|---|---|---|
| M0 | Revalidate baseline and project controls | `pytest`, Ruff, Mypy, GPU/uv/Git record | DONE |
| M1 | Multi-source ingestion and provenance | Supported text formats plus lazy Docling adapter, hash, metadata, unsupported/failed boundary tests | IN_PROGRESS |
| M2 | Python AST code parsing | Function/class/import schema, syntax-error behavior, tests | DONE |
| M3 | Evidence-aware extraction | Mock/LLM extraction maps claims to application-controlled source locations and hashes | DONE |
| M4 | Local retrieval baseline | Chunking, deterministic lexical ranking, metadata filters, provenance hits and tests | DONE |
| M5 | Reproduction plan and generated artifacts | Structured plan, evidence IDs, deterministic template, Mock and live LLM generation boundary | DONE for generation boundary |
| M6 | Safe validation and bounded repair | Static checks, Docker-only policy boundary, bounded repair orchestration and representative live repair | DONE for representative coverage |
| M7 | Capability registry and reuse | SQLite versions, verified-only promotion, JSON-LD export and verified reuse | DONE for reviewed capability path |
| M8 | API/demo integration | CLI, FastAPI and Streamlit runtime/app tests, metrics and security smoke | DONE for local runtime |
| M9 | Final acceptance | Requirement matrix audit, security/performance checks, final demo | IN_PROGRESS |
| M10 | Delivery gap audit | Updated matrix, primary scenario evidence and actionable backlog | DONE |
| M11 | Production retrieval and UI acceptance | Persistent Qdrant smoke test, automated UI interaction, HTTPS/auth/rate-limit check | IN_PROGRESS for public deployment |
| M12 | Extended failure repair and cross-scenario validation | Live import/dependency/timeout repair evidence and second public dataset | DONE for representative coverage |

## Working rules

- Work only on feature branches; never force-push or merge `main` without explicit confirmation.
- At each milestone run focused tests first, then the full suite and static checks.
- Update `phase_status.md`, `build_log.md`, `known_issues.md`, and the relevant ADR before the milestone commit.
- If an optional dependency is unavailable, implement an explicit boundary or Mock path and continue with independent work.
