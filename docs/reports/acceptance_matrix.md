# AlgoWeaver MVP acceptance matrix

Audit date: 2026-11-07 (Asia/Shanghai)

This is an evidence audit of the current worktree. `DONE` means the stated scope has direct code and test evidence. `PARTIAL` means a narrower baseline exists but the requirement's full acceptance scope is not met. `BLOCKED` means the implementation boundary is present but the current environment cannot execute the required integration.

| Must-have | Current evidence | Status | Remaining acceptance gap |
|---|---|---|---|
| Multi-source documents and historical code | `SourceIngestor` handles text/Markdown/Python/CSV/JSON/YAML; lazy Docling paths cover PDF/DOCX/PPTX/XLSX; `PythonCodeParser` indexes imports/classes/functions. | PARTIAL | Docling is not installed, so real office/PDF parsing is unverified; no repository-scale Tree-sitter path. |
| Algorithm knowledge extraction | `CapabilityExtractor`, Mock model, LiteLLM adapter, Pydantic `AlgorithmDraft`/`AlgorithmCapability`, missing-information handling. | PARTIAL | No real provider call has been executed in this environment; extraction remains a draft/review workflow. |
| Standard capability cards | `AlgorithmCapability`, `EvidenceRef`, explicit `draft`/`needs_review`/`verified` statuses, JSON output and registry payloads. | DONE for schema baseline | Full verified promotion still depends on an independent runtime report. |
| Evidence-linked RAG retrieval | `SourceChunker`, `EvidenceChunk`, `LocalLexicalRetriever`, `RetrievalEvaluator` and local in-memory `QdrantVectorRetriever` preserve line/path/source metadata; Recall@k, MRR and provenance coverage are tested. | PARTIAL | No embedding model, remote Qdrant service or reranker quality evaluation is configured. |
| Multi-model reproduction Agent | `ChatModel`/LiteLLM abstraction, `ReproductionPlanner`, `build_reproduction_graph()` and offline fallback. | PARTIAL | LangGraph is absent and real LLM planning/code generation is unverified; the current writer is deterministic template generation. |
| Code generation and dependency analysis | `TemplateArtifactWriter` produces moving-average Python/pytest artifacts; `PythonDependencyAnalyzer` emits static import reports. | PARTIAL | General algorithm generation, dependency resolution and workspace management are not implemented. |
| Isolated code execution | `ExecutionPolicy`, `ExecutionResult`, Docker-only `DockerSandboxRunner`; tests verify network, memory, CPU, PID, output and read-only policy translation; Docker SDK import and CLI path are verified. | BLOCKED for runtime | Docker CLI/daemon/pipe is unavailable; no real container execution has been observed. |
| Automated tests, error analysis and repair | `ValidationService` performs AST/contract checks; `BoundedRepairLoop` limits retries and preserves external observations. | PARTIAL | Generated pytest has not run in a sandbox; no LLM edit/repair callback or metric/performance evaluation is integrated. |
| Capability versioning and persistence | SQLite `CapabilityRegistry`, immutable versions, search and passing-report-only promotion; registry tests pass. | PARTIAL | No verified runtime report has been produced to exercise a real promotion from the CLI. |
| Historical capability retrieval and reuse | Lexical retrieval and registry name search are independently tested; `search_reusable()` filters to verified versions. | PARTIAL | Retrieval results are not yet fed into a reusable verified-capability selection workflow. |
| Complete end-to-end demo | `algo-weaver reproduce` writes bundle, dependency report and validation reports; optional FastAPI `/reproduce` returns the same evidence; Mock inventory example succeeds and marks artifacts `unverified`. | PARTIAL | The execution/promotion portion is blocked by unavailable Docker, so the full verified loop is not demonstrated. |

## Verification evidence

- `uv run pytest -q`: 55 passed, 0 skipped after installing the declared LangGraph, API and retrieval dependencies.
- `uv run ruff check src tests`: passed.
- `uv run mypy src`: passed for 36 source files.
- Mock CLI reproduction run created `algorithm.py`, `test_algorithm.py`, `reproduction_bundle.json`, `dependency_report.json` and `validation_reports.json`.
- CLI `--execute` run recorded `status=blocked` because the Docker daemon/pipe was unavailable; no capability was promoted to `verified`.
- FastAPI tests cover `/health`, `/extract` and `/reproduce`; the API does not execute generated code.
- Git branch `feat/initial-audit-and-ingestion` is synchronized with `origin`; `main` has not been merged.

## Acceptance conclusion

The current project is a well-tested partial MVP baseline. The full MVP acceptance gate is not yet satisfied because real isolated execution, runtime validation, automatic repair, real-provider extraction and verified reuse lack direct evidence.
