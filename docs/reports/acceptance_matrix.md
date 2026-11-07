# AlgoWeaver MVP acceptance matrix

Audit date: 2026-11-07 (Asia/Shanghai)

This is an evidence audit of the current worktree. `DONE` means the stated scope has direct code and test evidence. `PARTIAL` means a narrower baseline exists but the requirement's full acceptance scope is not met. `BLOCKED` means the implementation boundary is present but the current environment cannot execute the required integration.

| Must-have | Current evidence | Status | Remaining acceptance gap |
|---|---|---|---|
| Multi-source documents and historical code | `SourceIngestor` handles text/Markdown/Python/CSV/JSON/YAML; lazy Docling paths cover PDF/DOCX/PPTX/XLSX; stdlib ZIP/XML and basic PDF literal-text fallbacks cover simple office/PDF text; `PythonCodeParser` indexes imports/classes/functions. | PARTIAL | Complex PDF/Office layout remains unverified without Docling; no repository-scale Tree-sitter path. |
| Algorithm knowledge extraction | `CapabilityExtractor`, Mock model, LiteLLM adapter, Pydantic `AlgorithmDraft`/`AlgorithmCapability`, missing-information handling. | PARTIAL | No real provider call has been executed in this environment; extraction remains a draft/review workflow. |
| Standard capability cards | `AlgorithmCapability`, `EvidenceRef`, explicit `draft`/`needs_review`/`verified` statuses, JSON output and registry payloads. | DONE for schema baseline | Real LLM extraction remains unverified; reviewed-card promotion is demonstrated. |
| Evidence-linked RAG retrieval | `SourceChunker`, `EvidenceChunk`, `LocalLexicalRetriever`, `RetrievalEvaluator` and local in-memory `QdrantVectorRetriever` preserve line/path/source metadata; Recall@k, MRR and provenance coverage are tested. | PARTIAL | No embedding model, remote Qdrant service or reranker quality evaluation is configured. |
| Multi-model reproduction Agent | `ChatModel`/LiteLLM abstraction, installed LangGraph graph, `ReproductionPlanner`, executable graph boundary, and offline fallback. | PARTIAL | Real LLM planning/code generation is unverified; the current writer is deterministic template generation. |
| Code generation and dependency analysis | `TemplateArtifactWriter` produces moving-average Python/pytest artifacts; `PythonDependencyAnalyzer` emits static import reports. | PARTIAL | General algorithm generation, dependency resolution and workspace management are not implemented. |
| Isolated code execution | `ExecutionPolicy`, `ExecutionResult`, Docker SDK runner and WSL2 `WslDockerSandboxRunner`; inventory forecast unittest passed inside `python:3.12-slim` with network disabled and read-only workspace. | PARTIAL | Windows Docker pipe is optional; final capability promotion requires a complete draft from a real provider. |
| Automated tests, error analysis and repair | `ValidationService` performs AST/contract/runtime report checks; generated unittest passed in WSL Docker; WSL integration test demonstrates fail → bounded template repair → pass; LangGraph conditional routing now returns execution and repair loop state; `--metrics-file` collects container predictions and writes thresholded MAE/RMSE. | PARTIAL | No LLM edit/repair callback or multi-metric domain policy is integrated. |
| Capability versioning and persistence | SQLite `CapabilityRegistry`, immutable versions, search and passing-report-only promotion; WSL CLI run promoted the human-reviewed inventory card to `verified`. | PARTIAL | Real-provider extraction and automated reuse workflow remain open. |
| Historical capability retrieval and reuse | Lexical retrieval and registry name search are independently tested; `search_reusable()` and CLI `reuse` filter to verified versions; `reproduce --reuse-query` selects a verified card and revalidates it in WSL Docker. | PARTIAL | Retrieval hits are not yet automatically selected into a new reproduction plan. |
| Complete end-to-end demo | `algo-weaver reproduce --capability-file ... --backend wsl --execute` promoted a card to `verified`; `--reuse-query` then selected and revalidated that verified card in WSL Docker. | PARTIAL | The verified path is human-reviewed; real-provider extraction and LLM repair are not demonstrated. |

## Verification evidence

- `uv run pytest -q`: 76 passed, 0 skipped after installing the declared LangGraph, API, retrieval and execution dependencies.
- `uv run ruff check src tests`: passed.
- `uv run mypy src`: passed for 39 source files.
- Mock CLI reproduction run created `algorithm.py`, `test_algorithm.py`, `reproduction_bundle.json`, `dependency_report.json` and `validation_reports.json`.
- WSL CLI `--backend wsl --execute` recorded `status=passed` for the generated unittest. The reviewed-capability run promoted `cap_inventory_forecast_reviewed` to `verified`, and `--reuse-query` revalidated that verified card; the Mock extraction run remained `needs_review`.
- FastAPI tests cover `/health`, `/extract` and `/reproduce`; the API still does not execute generated code, while the LangGraph execution boundary is covered with injected fake runners.
- Git branch `feat/initial-audit-and-ingestion` is synchronized with `origin`; `main` has not been merged.

## Acceptance conclusion

The current project is a well-tested partial MVP baseline. Real isolated execution is now directly verified through WSL2 Docker; the full MVP gate remains open because real-provider extraction, LLM-driven repair, runtime metric evaluation and verified capability reuse lack direct evidence.
