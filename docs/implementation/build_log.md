# Build log

## 2026-11-06 — baseline and execution controls

- Re-read `AGENTS.md`, `ALGO_WEAVER_GOAL.md`, requirements matrix, architecture and ADRs.
- Revalidated environment: Python 3.13.9; NVIDIA GeForce RTX 5070 Laptop GPU, 8151 MiB, driver 573.22; `uv` unavailable.
- Revalidated source tree and Git: branch `feat/initial-audit-and-ingestion`, origin synchronized at `04d74ac` before this continuation; no `main` merge.
- Ran `PYTHONPATH=src pytest -q`: 14 passed, 2 skipped because LangGraph is not installed.
- Ran `ruff check src tests`: passed.
- Ran `mypy src`: passed for 17 source files.
- Created `docs/PROJECT_MASTER_PLAN.md`, `EXECUTION_PLAN.md`, and this log; opened M1/M2 implementation work.

## 2026-11-06 — ingestion, AST indexing and validation baseline

- Extended `SourceIngestor` with lazy Docling boundaries for PDF, DOCX, PPTX and XLSX. Missing optional dependency returns `unsupported`; parser failures return `failed`.
- Added `PythonCodeParser` using stdlib `ast`; it extracts imports, classes, methods, functions, decorators, arguments, return annotations, docstrings, line ranges and SHA-256 without executing source. Commit: `f0c794e`.
- Added `ValidationService` and `ValidationReport` for deterministic capability contracts and Python AST/entrypoint checks. Runtime metrics, dependency checks and sandbox execution remain pending.
- Focused and full validation after the code parser: `pytest -q` -> 19 passed, 2 skipped; Ruff passed; Mypy passed for 19 source files.
- Committed and pushed the combined document adapter, validation and execution-control documentation change as `474dcb0`.
- Opened M4 local retrieval baseline: deterministic lexical ranking first, with a later Qdrant/embedding adapter behind the same interface.

## 2026-11-06 — local retrieval baseline

- Added `EvidenceChunk` and `RetrievalHit` schemas with source ID, path, line range, format and copied metadata.
- Added `SourceChunker` and `LocalLexicalRetriever` with deterministic token overlap ranking, source-type/metadata filters and provenance-preserving hits.
- Full validation: `pytest -q` -> 27 passed, 2 skipped; Ruff passed; Mypy passed for 23 source files.
- Qdrant, dense embeddings, reranking and retrieval metrics remain open work; no semantic retrieval claim is made.

## 2026-11-06 — evidence and reproduction baseline

- Extended `EvidenceRef` and `CapabilityExtractor` with application-controlled line ranges and content hashes; model-supplied evidence remains rejected by the draft schema.
- Added deterministic `ReproductionPlanner` and `TemplateArtifactWriter` for evidence-linked plans and moving-average Python/pytest artifacts. Artifacts are explicitly `unverified` and are never executed during generation.
- Reproduction module commit: `37def95`; evidence changes are pending the next combined commit.
- Focused/full validation after these changes: `pytest -q` -> 33 passed, 2 skipped; Ruff and Mypy passed.

## 2026-11-07 — capability persistence baseline

- Added `CapabilityRegistry` backed by stdlib SQLite, with immutable integer versions, latest/search queries and verified-only promotion guarded by a passing `ValidationReport`.
- Added `CapabilityVersion` schema and registry tests for versioning, promotion rejection and invalid queries.
- Focused registry validation: 3 passed; full-suite validation remains required before commit.

## 2026-11-07 — Docker sandbox boundary

- Added `ExecutionPolicy`, `ExecutionResult` and `DockerSandboxRunner`.
- The runner lazy-loads the Docker SDK, disables network by default, mounts the workspace read-only by default, applies timeout/memory/CPU/PID/output limits, clears environment variables and returns `blocked` when Docker is unavailable.
- There is no host subprocess fallback. Tests use a fake Docker client to inspect policy translation; real Docker daemon execution remains unverified.
- Full validation: `pytest -q` -> 39 passed, 2 skipped; Ruff passed; Mypy passed for 29 source files.

## 2026-11-07 — bounded repair orchestration

- Added `BoundedRepairLoop` and repair result schemas. The loop consumes sandbox observations, calls an injected repair action, reruns through an injected executor, and stops on pass, blocked, callback failure or the configured attempt limit.
- It never executes commands or edits files directly; generated code remains behind the Docker runner boundary.
- Focused repair validation: 3 passed; full-suite validation and commit are pending.

## 2026-11-07 — CLI reproduction demo

- Added `algo-weaver reproduce`, which ingests a source, extracts a capability, retrieves provenance chunks, builds a reproduction plan, writes deterministic artifacts and emits static validation reports.
- The command was run against `examples/moving_average/algorithm.md` in Mock mode. It wrote `algorithm.py`, `test_algorithm.py`, `reproduction_bundle.json` and `validation_reports.json` and printed `unverified`.
- No generated code was executed by this CLI path; Docker sandbox execution remains the promotion gate.
- Full validation after CLI integration: `pytest -q` -> 43 passed, 2 skipped; Ruff and Mypy passed.

## 2026-11-07 — sandbox and registry CLI wiring

- `reproduce` now accepts `--execute` and `--registry`. It writes the draft capability to SQLite and records `execution_result.json` when Docker execution is requested.
- A real run in the current environment returned `status=blocked` with `Docker unavailable: No module named 'docker'`; the persisted capability remained `needs_review` and no `verified` promotion occurred.

## Evidence policy

Every later entry must record the changed module, test command, result, unresolved issue, and Git commit. Claims remain `NOT_STARTED`, `IN_PROGRESS` or `BLOCKED` until those fields have evidence.
