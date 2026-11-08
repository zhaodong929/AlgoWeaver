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

## 2026-11-07 — verified capability reuse in reproduction

- Added `--reuse-query` to `reproduce`; it selects only verified registry records and rejects missing matches.
- Revalidated the reviewed inventory capability through WSL Docker using `--reuse-query`; execution passed and the existing verified status was preserved.
- Fixed runtime report handling for already-verified capabilities.

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

## 2026-11-07 — sandbox hardening

- Extended both Docker execution backends with read-only root filesystems, dropped capabilities, `no-new-privileges` and a bounded noexec `/tmp` tmpfs.
- Re-ran the reviewed inventory capability through WSL Docker after the hardening change; execution passed and registry promotion remained verified.

## 2026-11-07 — WSL repair integration evidence

- Added a WSL integration test that corrupts `algorithm.py`, observes a failing container unittest, applies `TemplateRepairer` through `BoundedRepairLoop`, and reruns successfully.
- Integration test passed in the configured WSL Docker environment; full suite reached 69 passed, 0 skipped.

## 2026-11-07 — sandbox metric collection

- Added `--metrics-file` to execute the generated moving-average prediction inside WSL Docker and compute MAE/RMSE from the inventory sales CSV.
- Verified output: `metric_report.json` with 3 samples, MAE `0.888888...` and RMSE `1.360827...`.
- With `--max-mae 1.0 --max-rmse 1.5`, the same report returned `overall_status="passed"`.

## 2026-11-07 — LiteLLM provider contract test

- Added a mocked provider-call test for `LiteLLMChatModel`, verifying model name, API base, temperature, timeout and JSON extraction without network access.

## 2026-11-07 — Windows WSL subprocess encoding fix

- Full pytest exposed GBK decoding warnings from WSL subprocess reader threads on Windows.
- `WslDockerSandboxRunner` now forces UTF-8 with replacement decoding; WSL integration and full suite pass without the prior thread warnings.

## 2026-11-07 — CI #48 cross-platform sandbox test fix

- Root cause: both Python 3.12 and 3.13 CI jobs failed in `tests/test_sandbox.py::test_wsl_runner_translates_policy_without_host_execution` because Ubuntu's `tmp_path` is POSIX (`/tmp/...`), while `_windows_to_wsl_path` intentionally requires a Windows drive path.
- The test now verifies Windows-drive translation with `PureWindowsPath` and stubs only the platform boundary when exercising the WSL command policy, preserving the production contract and all CI checks.
- Validation: `uv sync --group dev --extra api --extra retrieval --extra execution`; `uv run ruff check .`; `uv run pytest` -> 73 passed; `uv run mypy src` -> 39 source files, no issues.
- Unresolved: GitHub Actions verification requires the post-push run to complete. The public API exposed step statuses, while the logs endpoint required admin authentication; the authenticated browser log for CI #48 confirmed the failure above.
- Git commit: `3531d55` (`test: make WSL path test platform independent`).

## 2026-11-07 — executable reproduction graph

- Extended `build_reproduction_graph()` with optional artifact writing, injected sandbox execution, conditional failed/timeout routing and bounded repair. The default graph remains static and does not execute generated code.
- Added graph state for artifact paths, `ExecutionResult`, `RepairLoopResult` and runtime validation reports. The validation path now checks the generated moving-average entrypoint consistently with the CLI.
- Tests cover execution success, one-attempt repair success and repair-budget exhaustion using fake runners; no host or Docker execution occurs in these tests.
- Validation: `uv run pytest tests/test_reproduction_graph.py -q` -> 4 passed; full `uv run pytest` -> 76 passed; `uv run ruff check .` passed; `uv run mypy src` passed for 39 source files.
- Unresolved: real-provider planning/code generation and LLM repair remain unverified; API execution/write-back is the next milestone.
- Git commit: `0669731` (`feat: integrate execution and repair into reproduction graph`).

## 2026-11-07 — API sandbox execution integration

- Extended `POST /reproduce` with explicit `execute`, `backend`, `repair` and bounded `max_repair_attempts` fields. The endpoint now delegates to the executable reproduction graph and returns sandbox/repair observations without promoting a capability.
- Production requests use the existing Docker or WSL runner; tests inject a runner so CI never executes generated code or requires a daemon. Default requests remain static and return unverified artifacts.
- Validation: API-focused tests -> 5 passed; full `uv run pytest` -> 78 passed; `uv run ruff check .` passed; `uv run mypy src` passed for 39 source files.
- Unresolved: API registry write-back, metrics request handling and UI remain future work; real-provider and LLM repair paths are still unverified.
- Git commit: `cbc503b` (`feat: expose sandbox execution through API`).

## 2026-11-07 — API registry write-back

- Added `ALGOWEAVER_REGISTRY_PATH` configuration and `persist=true` on `/reproduce`. API persistence appends an immutable capability version and reuses `CapabilityRegistry.promote_verified()` only when an independently passing runtime report is present.
- Mock/needs_review capabilities remain pending even when an injected execution runner passes; the API test verifies no false promotion.
- Validation: API-focused tests -> 6 passed; full `uv run pytest` -> 79 passed; `uv run ruff check .` passed; `uv run mypy src` passed for 39 source files.
- Unresolved: API metrics request handling and UI remain future work; real-provider and LLM repair paths are still unverified.
- Git commit: `ac79669` (`feat: persist API capabilities through registry gate`).

## 2026-11-07 — LangGraph WSL runtime acceptance

- Ran the reviewed inventory capability through the new executable graph with `WslDockerSandboxRunner`, a temporary workspace, `python -m unittest discover -v`, `TemplateRepairer`, and one repair attempt budget.
- Observed `execution=passed`, `runtime_report=passed`, no repair required, and both generated artifact paths recorded in graph state. This is real WSL2 Docker execution, not a fake runner test.
- The graph itself does not promote registry state; promotion remains behind the existing independent `CapabilityRegistry` gate in CLI/API workflows.
- Validation command: `uv run python -` with the reviewed capability and `examples/inventory_forecast/algorithm.md`; command completed successfully.
- Unresolved: metrics collection is still CLI-specific, and real-provider extraction/LLM repair remain unverified.

## 2026-11-07 — API regression metrics

- Added `POST /metrics` with Pydantic input validation, deterministic MAE/RMSE evaluation and optional threshold status. Mismatched sequences return HTTP 400; threshold failures remain explicit `overall_status="failed"`.
- Validation: API-focused tests -> 9 passed; full `uv run pytest` -> 82 passed; `uv run ruff check .` passed; `uv run mypy src` passed for 39 source files.
- Unresolved: `/metrics` evaluates supplied predictions; automatic extraction of predictions from sandbox stdout and UI visualization remain future work.
- Git commit: `118cd92` (`feat: expose regression metrics through API`).

## 2026-11-07 — README acceptance refresh

- Updated the Windows/Linux runbook and acceptance checklist to match the current 82-test baseline, CI #55, executable LangGraph/WSL path, API execution/persistence/metrics flags and explicit unverified boundaries.
- Git commit: `d30f250` (`docs: refresh MVP runbook and acceptance status`).

## 2026-11-07 — multi-source ingestion and retrieval

- Added `IngestionBatch` and `SourceIngestor.ingest_paths()` so mixed Markdown/Python/CSV/unsupported/missing sources retain independent provenance and status.
- Extended the reproduction graph to aggregate chunks from `sources`; FastAPI `/reproduce` accepts `additional_sources`, and CLI `reproduce` accepts repeated `--additional-input` values. Retrieval hits preserve source IDs and locations across the mixed set.
- Validation: full `uv run pytest` -> 85 passed; `uv run ruff check .` passed; `uv run mypy src` passed for 39 source files. Focused ingestion, graph and API tests cover mixed source success, unsupported/failed isolation and provenance hits.
- Unresolved: complex document layout, semantic embeddings/reranking and repository-scale ingestion remain open.
- Git commit: `5db6d94` (`feat: support multi-source reproduction inputs`).

## 2026-11-07 — structured code generation boundary

- Added `GeneratedCodeDraft` with strict Pydantic validation and a provider-neutral `ArtifactGenerator` protocol.
- Added deterministic `MockCodeGenerator` and provider-backed `LLMCodeGenerator`; the latter sends the evidence-linked plan to `ChatModel.complete_json`, merges model-declared dependencies into the plan and labels artifacts `llm` while keeping them `unverified`.
- Wired `generation_mode=template|mock|llm` into the reproduction graph, CLI and FastAPI. The LLM mode requires explicit `litellm` provider configuration so a mock extraction response cannot be mistaken for generated code.
- Focused validation: `uv run pytest tests/test_code_generation.py tests/test_reproduction_graph.py tests/test_api.py tests/test_cli.py -q` -> 29 passed.
- Full validation: `uv run pytest -q` -> 94 passed, 0 skipped; `uv run ruff check .` passed; `uv run mypy src` passed for 40 source files.
- Unresolved: no live provider call was made without credentials; generated LLM artifacts still require static checks and isolated runtime acceptance before promotion, and LLM repair remains open.
- Git commit: `d76637c` (`feat: add structured code generation modes`).

## 2026-11-07 — CI #58 WSL platform diagnosis and fix

- CI #58 failed in the `Test` step on both Python 3.12 and 3.13; dependency installation and Ruff completed successfully.
- Root cause: `tests/test_wsl_repair_integration.py` treated the presence of `wsl.exe` as sufficient on every host. The Ubuntu runner exposed a compatibility command, so the Windows-only integration test used a POSIX `/tmp` path and `WslDockerSandboxRunner` correctly rejected it.
- Changed the existing skip boundary to require both `sys.platform == "win32"` and an available `wsl.exe`. The WSL integration test remains active on Windows and is still a real runtime test there.
- Linux CI-equivalent validation in an isolated environment: 93 passed, 1 platform-appropriate skip; Ruff and Mypy passed. Windows validation in an isolated environment: 94 passed; Ruff and Mypy passed.
- No tests were deleted, and no quality check was disabled. The next GitHub Actions run is the acceptance gate for this fix.
- Git commit: `a7fb5c7` (`fix: gate WSL integration by host platform`).

## 2026-11-07 — CI #59–#65 CLI output parity and final verification

- CI #59–#64 exposed a second cross-platform failure after the WSL gate: `test_reproduce_command_requires_litellm_for_llm_generation` depended on Click's rendered output stream and ANSI layout. Linux and Windows runners reported the same command error through different captured streams.
- Added failure annotations to `.github/workflows/ci.yml` so the first failing pytest case is visible through the public Checks API even when job logs require authentication. The workflow still runs the same full pytest command and preserves its exit status.
- The CLI test now verifies the Typer boundary with a direct `BadParameter` assertion and treats the rendered invocation as an exit-code check. No production validation was weakened.
- Focused validation: `uv run pytest tests/test_cli.py -q` -> 8 passed in both Windows and Linux/Python 3.13 isolated environments.
- Final local validation: Windows isolated environment `uv run pytest -q` -> 94 passed; Ruff passed; Mypy passed for 40 source files. Linux/Python 3.13 with all CI extras -> 93 passed, 1 Windows-only WSL skip.
- GitHub Actions run #65 passed on Python 3.12 and 3.13.
- Git commits: `7967c2c`, `6a69261`, `7ce30f3`, `fdedf02`, `057078b`, `9ed4af0`.

## 2026-11-08 — structured LLM repair boundary

- Added `RepairPatch` with strict Pydantic fields for an existing artifact path, replacement source and rationale.
- Added `LLMRepairer`, which sends the plan, artifact contents and external `ExecutionResult` to `ChatModel.complete_json`, rejects unknown/path-escaping targets, writes only inside the sandbox workspace, refreshes the artifact SHA-256 and never executes source on the host.
- Integrated `repair_mode=template|llm` into the reproduction graph, CLI and FastAPI. LLM repair requires `repair=true` and `mode=litellm`; template repair remains the offline default. The graph returns the mutated bundle so validation observes the applied patch.
- Focused validation: `uv run pytest tests/test_llm_repair.py tests/test_reproduction_graph.py tests/test_api.py tests/test_cli.py -q` -> 32 passed; Ruff passed; Mypy passed for 41 source files.
- Full Windows validation: `uv run pytest -q` -> 100 passed, 0 skipped; Ruff passed; Mypy passed for 41 source files. Linux/Python 3.13 with all CI extras -> 99 passed, 1 Windows-only WSL skip; Ruff and Mypy passed.
- Unresolved: no live provider repair call was made without credentials; API-side automatic metric collection remains a separate milestone.
- Git commit: `1c20d1c` (`feat: add structured LLM repair boundary`).

## 2026-11-08 — API sandbox metrics collection

- Added `SandboxMetricsRequest` to `/reproduce` with a fixed `inventory_demand` task, actual samples, moving-average window and MAE/RMSE thresholds. Metrics require `execute=true` and reject windows larger than the supplied samples.
- The endpoint writes a JSON input inside the temporary workspace and runs a fixed `python -c` moving-average evaluation command through the same Docker/WSL boundary. It returns `metric_execution` plus a thresholded `metric_report`; arbitrary user commands are not accepted.
- Added an injectable metric runner for API tests without weakening the production sandbox path.
- Focused validation: API tests -> 15 passed. Full Windows validation: `uv run pytest -q` -> 102 passed, 0 skipped; Ruff passed; Mypy passed for 41 source files.
- Linux/Python 3.13 CI-equivalent validation with all extras: 101 passed, 1 Windows-only WSL skip; Ruff and Mypy passed. GitHub Actions #68 passed on Python 3.12 and 3.13.
- Real API evidence: `/reproduce` on WSL2 returned HTTP 200 with `execution=passed`, `metric_execution=passed`, MAE `1.0`, RMSE `1.0`, and `overall_status="passed"` for four inventory samples with window 2.
- Unresolved: support for other task types and automatic registry promotion by metrics remain open.
- Git commit: `5532c16` (`feat: collect metrics in API sandbox`).

## 2026-11-08 — metric-aware capability promotion

- API persistence now requires the runtime report to pass and, when `metrics` is requested, the sandbox metric report to have `overall_status="passed"` before calling `promote_verified()`.
- Added a regression test proving a failed metric keeps the registry record at `needs_review` even when the test runner itself passes.
- Validation: API tests -> 16 passed; full Windows suite -> 103 passed, 0 skipped; Linux/Python 3.13 with all CI extras -> 102 passed, 1 Windows-only WSL skip; Ruff and Mypy passed for 41 source files.
- Git commit: `7523f4b` (`feat: gate registry promotion on metric pass`).

## 2026-11-08 — API verified capability reuse

- Added `reuse_query` to `/reproduce`. The endpoint searches the configured SQLite registry with `search_reusable()`, refuses missing matches with HTTP 404, skips fresh extraction and returns the selected `reused_record` version.
- Added API tests for verified reuse and missing-match rejection; unverified records remain ineligible by the existing registry query contract.
- Validation: API tests -> 18 passed; full Windows validation -> 105 passed, 0 skipped; Linux/Python 3.13 with all CI extras -> 104 passed, 1 Windows-only WSL skip; Ruff and Mypy passed for 41 source files. GitHub Actions #72 passed on Python 3.12 and 3.13.
- Unresolved: semantic retrieval-driven reuse without an explicit query remains open.
- Git commit: `152dce4` (`feat: reuse verified capabilities in API`).

## 2026-11-08 — automatic verified reuse by extracted name

- Added `auto_reuse=true` to `/reproduce`. After extraction, the API performs a verified-only registry name match; a hit replaces the draft capability and returns its `reused_record`. Explicit `reuse_query` and `auto_reuse` are mutually exclusive.
- Added regression coverage for automatic name matching and the existing explicit reuse/missing-match paths.
- Validation: API tests -> 19 passed; full Windows validation -> 106 passed, 0 skipped; Linux/Python 3.13 with all CI extras -> 104 passed, 1 Windows-only WSL skip; Ruff and Mypy passed for 41 source files. GitHub Actions #74 passed on Python 3.12 and 3.13.
- Unresolved: semantic embedding/reranker-based reuse remains open.
- Git commit: `f42e604` (`feat: add automatic verified reuse by name`).

## 2026-11-08 — GPU and Docker runtime audit

- Windows and WSL2 report an NVIDIA GeForce RTX 5070 Laptop GPU with 8,151 MiB VRAM, driver 573.22 and CUDA 12.8; WSL Docker Engine 29.1.3 is available.
- A CUDA container smoke test was not completed because the image pull ended with a registry network EOF; no model weights or CUDA/PyTorch wheels were downloaded.
- Linux/Python 3.13 with all CI extras: 105 passed, 1 Windows-only WSL skip; Ruff and Mypy passed. GitHub Actions run #79 passed on Python 3.12 and 3.13 after the documentation-only audit.
- Git commit: `23b5470` (`docs: record GPU and Docker runtime audit`).

## Evidence policy

Every later entry must record the changed module, test command, result, unresolved issue, and Git commit. Claims remain `NOT_STARTED`, `IN_PROGRESS` or `BLOCKED` until those fields have evidence.

## 2026-11-08 — live Bailian providers and model routing

- Configured the local ignored `.env` for the user's Bailian workspace without adding any secret to tracked files. The primary model is `dashscope/qwen3.8-max-0902`; `ALGOWEAVER_CODE_LLM_MODEL` routes generation and LLM repair to `dashscope/deepseek-v4.1-flash-1017`.
- Added provider-neutral `EmbeddingProvider` and `RerankerProvider` boundaries with deterministic mocks and explicit DashScope implementations. `qwen3.7-text-embedding-flash` returned two 1024-dimensional vectors. `qwen3-rerank` returned ordered relevance scores through the workspace OpenAI-compatible rerank endpoint.
- The requested `text-embedding-v4` endpoint returned HTTP 403 `insufficient_quota` because its free quota is exhausted in the current workspace; the enabled `qwen3.7-text-embedding-flash` remains the active fallback.
- Fixed the reranker request format to use `/compatible-api/v1/reranks`; the DashScope `/api/v1/services/rank/...` route returned the official `url error` for this workspace/model combination.
- Fixed LangGraph plan-error routing so an incomplete capability returns a controlled API error instead of reaching the generation node with a missing plan.
- Live evidence: qwen JSON smoke test passed; DeepSeek JSON smoke test passed; CLI live extraction passed; CLI routed reproduction produced `algorithm.py` and `test_algorithm.py`; FastAPI `/reproduce` returned 200 with a ready plan and two LLM artifacts for a complete inventory description.
- Validation: `uv run --no-sync pytest -q` -> 114 passed; Ruff passed; Mypy passed for 44 source files. Retrieval provider focus -> 13 passed.
- Security: the API key was supplied in chat and must be revoked and regenerated before deployment. The local `.env` is ignored and must never be committed.
- Git commit: `974c528` (`feat: connect Bailian model and retrieval providers`).

## 2026-11-08 — live repair loop, hybrid retrieval and Streamlit UI

- Configured the Bailian workspace models as user-level Windows environment variables, outside the repository. The active roles are `qwen3.8-max-0902`, `deepseek-v4.1-flash-1017`, `qwen3.7-text-embedding-flash`, and `qwen3-rerank`.
- Added `HybridRetriever` and connected it to LangGraph, CLI and FastAPI. It performs lexical retrieval, Qdrant in-memory dense retrieval, weighted score fusion and optional reranking, while preserving the lexical fallback.
- Real hybrid evidence: qwen3.7-text-embedding-flash returned 1024-dimensional vectors; qwen3-rerank returned scores 0.8559 and 0.2150 for inventory versus image-classification candidates.
- Completed a real failed-code repair loop: an intentionally broken moving-average artifact failed in the WSL2 Docker sandbox, `deepseek-v4.1-flash-1017` proposed and applied a patch, and the bounded one-attempt loop ended with `final=passed`.
- Added a Streamlit dashboard with file upload, mode selection, API execution, evidence, plan, artifact, runtime and report panels. `streamlit run src/algo_weaver/ui.py --server.headless true --server.port 8505` started successfully and `/_stcore/health` returned HTTP 200.
- Added the optional `ui` dependency group and `algo-weaver-ui` entry point. Full validation: 117 passed, Ruff passed, Mypy passed for 46 source files.
- Git commit: `47d3dfb` (`feat: add hybrid retrieval and Streamlit dashboard`).

## 2026-11-08 — delivery gap audit and production boundaries

- Added `DELIVERY_GAP_LIST.md` as the executable backlog derived directly from the
 笔试 requirements. It names the inventory-demand forecasting scenario, records the
  existing CSV/doc/card evidence, and separates `DONE`, `PARTIAL`, `TODO` and `BLOCKED`.
- Updated `requirements_matrix.md`, `EXECUTION_PLAN.md` and `phase_status.md` with the
  latest implementation evidence and the next P0/P1/P2 milestones.
- Added persistent Qdrant configuration (`ALGOWEAVER_QDRANT_MODE=server`), a Docker
  Compose service with a storage volume and healthcheck, and wiring through CLI,
  FastAPI and LangGraph. Memory mode remains the offline default.
- Added production API boundary controls: API-key authentication, per-process rolling
  rate limiting with `Retry-After`, public `/health` for probes, and HTTPS reverse-proxy
  deployment instructions in `docs/architecture/deployment.md`.
- Added Streamlit AppTest coverage for page rendering and request submission, and
  controlled repair coverage for import errors, missing dependencies and timeouts.
- Validation after the fixes: `uv run --no-sync pytest -q` -> **125 passed**;
  focused provider/UI tests -> **9 passed**. Qdrant persistence configuration tests
  passed; a real Qdrant Docker smoke test remains pending because Docker is not exposed
  in the current PowerShell session.
- No API key, `.env`, Qdrant storage volume or model weights were added to Git.
- Git commits: `b17206f` (`feat: harden delivery and production boundaries`) and
  `16919d0` (`test: isolate provider defaults`).

## 2026-11-08 — P0-2 inventory scenario delivery evidence

- Ran the reviewed inventory capability through ingestion of `algorithm.md` and
  `sales_history.csv`, deterministic artifact generation, WSL2 Docker execution and
  sandbox metric evaluation.
- Observed `execution=passed`, two generated unit tests passing in `python:3.12-slim`,
  MAE `0.8888888888888881`, RMSE `1.3608276348795427`, both under threshold `3.0`,
  and registry promotion to `verified`.
- Re-ran the same workflow with `--reuse-query "库存需求移动平均预测"`; verified
  capability version 2 was selected and revalidated in the isolated runner.
- Saved the evidence and exact commands in
  `docs/reports/test_reports/2026-11-08-inventory-delivery.md`.
- P0-1 Qdrant attempt: WSL Docker Engine 29.1.3 is available, but the Qdrant image
  pull timed out at Docker Hub. No service-success claim was recorded.
- Added `ALGOWEAVER_QDRANT_MODE=local` with an on-disk Qdrant client path for Windows
  development. The persistence test reopened the same collection in a second client
  and retrieved the previously stored provenance chunk (`3 passed` in the focused
  Qdrant test file). This is local persistence evidence; Docker service validation
  remains a separate open item.

## 2026-11-08 — open-license second scenario

- Added `examples/predictive_maintenance/` using the UCI AI4I 2020 Predictive
  Maintenance Dataset (DOI `10.24432/C5HS5C`, CC BY 4.0) with attribution metadata,
  a transparent torque/tool-wear rule baseline, a reviewed capability card and
  deterministic precision/recall checks.
- The checked-in CSV has 10,000 rows. The baseline produced 2 high-risk rows with
  precision `1.0` and a deliberately low recall; this is documented as a baseline,
  not a production model.
- Validation: scenario tests -> `3 passed`; full suite and static checks remain the
  authoritative project gate.

## 2026-11-08 — API and Streamlit runtime smoke

- Started FastAPI on `127.0.0.1:8010`; `GET /health` returned HTTP 200 and
  `POST /metrics` returned HTTP 200 with deterministic MAE/RMSE output.
- Started Streamlit on `127.0.0.1:8510`; `/_stcore/health` returned HTTP 200 and
  the root page returned HTTP 200 with 7,863 bytes of HTML. Automated AppTest also
  exercises the default form and request-result panels.
- The full project suite after the AI4I scenario and CLI metric gate is **128 passed**;
  Ruff and Mypy remain clean.
- GitHub Actions CI runs #89 (`a466b89`) and #90 (`ec24374`) both completed
  successfully on Python 3.12 and 3.13. The only annotations are upstream runner
  deprecation/migration notices.

## 2026-11-08 — live repair coverage for three failure classes

- Ran `LLMRepairer` with the configured `deepseek-v4.1-flash-1017` model against
  intentionally broken artifacts in temporary WSL2 Docker workspaces.
- Import error (`missing_helpers`), missing dependency (`pandas`) and timeout
  (infinite loop) each entered the bounded one-attempt loop and ended with a passing
  generated unittest suite.
- Full evidence, hashes and the execution boundary are recorded in
  `docs/reports/test_reports/2026-11-08-live-repair-scenarios.md`.
