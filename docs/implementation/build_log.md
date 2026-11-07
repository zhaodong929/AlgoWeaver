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

## 2026-11-07 — static dependency analysis

- Added `PythonDependencyAnalyzer` and `DependencyReport` for AST-only import inventory; generated code is never imported or executed.
- `reproduce` now writes `dependency_report.json` beside the generated artifacts and validation reports.

## 2026-11-07 — reproduction workflow state

- Added `build_reproduction_graph()` with `retrieve -> plan -> generate -> validate` nodes and an optional LangGraph backend plus offline fallback.
- Added AST-only `PythonDependencyAnalyzer`; the CLI now emits `dependency_report.json` for generated Python artifacts.
- Focused validation: graph, dependency and CLI tests passed; Ruff/Mypy passed for 34 source files.
- Full validation after workflow/dependency changes: `pytest -q` -> 46 passed, 2 skipped; Ruff and Mypy passed.
- Committed and pushed workflow/dependency analysis as `3356695`; feature branch remains synchronized with origin.

## 2026-11-07 — API, retrieval evaluation and acceptance audit

- Added optional FastAPI endpoints `/health`, `/extract` and `/reproduce`; they reuse existing services, default to Mock and never execute generated code.
- Added deterministic retrieval `Recall@k`, MRR and provenance coverage evaluation plus explicit score fusion for externally supplied dense scores. No embedding model is claimed as verified.
- Added an inventory demand forecasting example and a Must-have acceptance audit at `docs/reports/acceptance_matrix.md`.
- Full validation after these changes: `pytest -q` -> 51 passed, 2 skipped; Ruff and Mypy passed for 35 source files.

## 2026-11-07 — uv lock and optional dependency verification

- Installed lightweight engineering dependencies `uv`, LangGraph, Docker SDK and Qdrant client; no model weights were downloaded.
- Generated `uv.lock` with `uv lock` and created the project environment with `uv sync --group dev`.
- Installed the API extra with `uv sync --group dev --extra api`.
- Re-ran the authoritative commands: `uv run pytest -q` -> 53 passed, 0 skipped; `uv run ruff check src tests` passed; `uv run mypy src` passed for 35 source files.
- The Docker CLI/daemon and Docling remain unavailable, so real sandbox and office-document integration are still unverified.

## 2026-11-07 — Qdrant vector contract

- Added optional `QdrantVectorRetriever` over `EvidenceChunk`/`RetrievalHit`, using Qdrant's local in-memory client and externally supplied synthetic vectors.
- Installed the retrieval extra with `uv sync --group dev --extra api --extra retrieval`.
- Full validation: `uv run pytest -q` -> 54 passed, 0 skipped; Ruff and Mypy passed for 36 source files.
- This validates the vector-store/provenance contract only; no embedding model or remote vector service was used.

## 2026-11-07 — verified-only reuse search

- Extended `CapabilityRegistry` with `search_reusable()`, which returns only versions whose status is `verified`.
- Added regression coverage proving draft/partial records are not eligible for reuse until a passing independent report promotes them.

## 2026-11-07 — inventory scenario routing fix

- The first inventory forecast Demo exposed that the Chinese `移动平均` title selected the generic placeholder template.
- Updated deterministic template routing to recognize the Chinese algorithm name and added a regression test; the domain demo now generates the moving-average implementation.
- Full validation after the routing fix: `uv run pytest -q` -> 55 passed, 0 skipped.

## 2026-11-07 — Docker SDK verification

- Installed the `execution` extra with `uv sync --group dev --extra api --extra retrieval --extra execution`.
- Re-ran the inventory forecast demo with `--execute`; the runner reached the Docker SDK but returned `blocked` because the Docker daemon/pipe is unavailable. No host execution occurred.

## 2026-11-07 — stdlib Office fallback

- Added dependency-free DOCX/PPTX/XLSX ZIP/XML text fallbacks used only when Docling is unavailable; PDF remains explicitly unsupported without Docling.
- Added synthetic DOCX/PPTX/XLSX fixtures. Focused ingestion validation: 9 passed; Ruff/Mypy passed.
- Full validation after the Office fallback commit: `uv run pytest -q` -> 58 passed, 0 skipped; Ruff and Mypy passed.

## 2026-11-07 — basic PDF literal-text fallback

- Added a constrained stdlib PDF fallback for simple `BT ... (text) Tj ... ET` literal text operators when Docling is unavailable.
- Complex layout, compressed streams, OCR and table extraction remain explicitly outside this fallback.
- Focused ingestion validation: 10 passed; Ruff and Mypy passed.
- Full validation after the PDF fallback: `uv run pytest -q` -> 59 passed, 0 skipped.

## 2026-11-07 — runtime validation report and promotion gate

- Added `ValidationService.build_runtime_report()` to combine capability, artifact and Docker execution evidence.
- `reproduce --execute` now writes the runtime report and can promote a capability only when the report is fully passing; the current Docker-blocked run remained `unverified`.
- Focused validation: CLI and validation tests passed; Ruff and Mypy passed.

## 2026-11-07 — continuation audit

- Revalidated clean feature branch, remote synchronization, and current evidence files.
- Authoritative checks: `uv run pytest -q` -> 61 passed, 0 skipped; Ruff passed; Mypy passed for 36 source files.
- Remaining blocker is unchanged: Docker daemon/pipe unavailable; no host execution fallback is permitted.

## 2026-11-07 — WSL Docker runtime verified

- Located the existing D-drive WSL distribution at `D:\WSL\Ubuntu-24.04` and started its systemd Docker Engine.
- Installed Ubuntu `docker.io`, added user `zd929` to the `docker` group, pulled `python:3.12-slim`, and added `WslDockerSandboxRunner`.
- Ran the inventory forecast demo with `--backend wsl --execute`: the generated unittest ran inside the container and returned `status="passed"` with network disabled and a read-only workspace.
- The capability stayed `needs_review` because Mock extraction is intentionally not eligible for verified promotion.
- Full validation after WSL backend changes: `uv run pytest -q` -> 62 passed, 0 skipped; Ruff and Mypy passed.
- Acceptance status changed from Docker-runtime blocked to runtime verified/Mock-promotion pending.

## 2026-11-07 — human-reviewed verified capability demo

- Added `--capability-file` to `reproduce` for an explicit human-reviewed capability card path.
- Ran `examples/inventory_forecast/reviewed_capability.json` with `--backend wsl --execute --registry`.
- The generated unittest passed inside Docker, runtime validation passed, and SQLite registry promotion returned `status="verified"` for `cap_inventory_forecast_reviewed`.
- This is a verified human-reviewed path; it does not claim real LLM extraction.
- Full validation after this change: `uv run pytest -q` -> 63 passed, 0 skipped; Ruff and Mypy passed.

## 2026-11-07 — verified reuse CLI and runtime duration metric

- Added `sandbox.duration` to runtime reports with measured wall time.
- Added `algo-weaver reuse <query>`; it returns only registry records with `status="verified"`.
- CLI reuse regression proves draft records are excluded and promoted records are returned.
- Full validation after this change: `uv run pytest -q` -> 64 passed, 0 skipped; Ruff and Mypy passed.

## 2026-11-07 — bounded offline repair path

- Added `TemplateRepairer`, which restores only reviewed bundle artifacts after a failed or timed-out execution and rejects path escapes.
- Wired `--repair` into the CLI's bounded repair loop; blocked execution remains unrepaired.
- Added repair regression tests; full validation: `uv run pytest -q` -> 66 passed, 0 skipped; Ruff and Mypy passed.

## 2026-11-07 — CI optional-extra coverage

- Updated GitHub Actions to install API, retrieval and execution extras on both Python 3.12 and 3.13 matrix jobs.
- CI now runs Ruff, the full pytest suite and Mypy, matching the local reproducible validation scope.

## 2026-11-07 — deterministic domain metrics

- Added `RegressionMetricEvaluator` with MAE/RMSE and explicit threshold status for inventory demand evaluation.
- Added schema, service, tests and architecture documentation; automatic collection from sandbox prediction files remains future integration work.

## Evidence policy

Every later entry must record the changed module, test command, result, unresolved issue, and Git commit. Claims remain `NOT_STARTED`, `IN_PROGRESS` or `BLOCKED` until those fields have evidence.
