# AlgoWeaver Execution Plan

Updated: 2026-11-06 (Asia/Shanghai)

## Current milestone

**Phase 1/3: document adapter boundaries and evidence-aware extraction.** Python AST indexing is complete in `f0c794e`; the next executable work is to connect parsed source locations to extraction evidence, while keeping Docling optional and explicit.

## Milestones

| ID | Milestone | Exit evidence | Status |
|---|---|---|---|
| M0 | Revalidate baseline and project controls | `pytest`, Ruff, Mypy, GPU/uv/Git record | DONE |
| M1 | Multi-source ingestion and provenance | Supported text formats plus lazy Docling adapter, hash, metadata, unsupported/failed boundary tests | IN_PROGRESS |
| M2 | Python AST code parsing | Function/class/import schema, syntax-error behavior, tests | DONE |
| M3 | Evidence-aware extraction | Real/Mock extraction maps claims to source locations | NOT_STARTED |
| M4 | Local retrieval baseline | Chunking, lexical/hybrid retrieval, metadata filters, retrieval tests | NOT_STARTED |
| M5 | Reproduction plan and generated artifacts | Structured plan, code/test files, dependency manifest | NOT_STARTED |
| M6 | Safe validation and bounded repair | Static checks, isolated runner, report schema, retry limit | IN_PROGRESS |
| M7 | Capability registry and reuse | Versioned persistence, verified-only promotion, reuse query | NOT_STARTED |
| M8 | API/demo integration | One end-to-end CLI/API demo and reproducible report | NOT_STARTED |
| M9 | Final acceptance | Requirement matrix audit, security/performance checks, final demo | NOT_STARTED |

## Working rules

- Work only on feature branches; never force-push or merge `main` without explicit confirmation.
- At each milestone run focused tests first, then the full suite and static checks.
- Update `phase_status.md`, `build_log.md`, `known_issues.md`, and the relevant ADR before the milestone commit.
- If an optional dependency is unavailable, implement an explicit boundary or Mock path and continue with independent work.
