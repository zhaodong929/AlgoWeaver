# AlgoWeaver MVP acceptance matrix

Audit date: 2026-11-07 (Asia/Shanghai)

This is an evidence audit of the current worktree. `DONE` means the stated scope has direct code and test evidence. `PARTIAL` means a narrower baseline exists but the requirement's full acceptance scope is not met. `BLOCKED` means the implementation boundary is present but the current environment cannot execute the required integration.

| Must-have | Current evidence | Status | Remaining acceptance gap |
|---|---|---|---|
| Multi-source documents and historical code | `SourceIngestor` handles text/Markdown/Python/CSV/JSON/YAML; `ingest_paths()` preserves mixed-source statuses; lazy Docling paths cover PDF/DOCX/PPTX/XLSX; stdlib ZIP/XML and basic PDF literal-text fallbacks cover simple office/PDF text; `PythonCodeParser` indexes imports/classes/functions. | PARTIAL | Complex PDF/Office layout remains unverified without Docling; no repository-scale Tree-sitter path. |
| Algorithm knowledge extraction | `CapabilityExtractor`, Mock model, LiteLLM adapter, Pydantic `AlgorithmDraft`/`AlgorithmCapability`, missing-information handling. | PARTIAL | No real provider call has been executed in this environment; extraction remains a draft/review workflow. |
| Standard capability cards | `AlgorithmCapability`, `EvidenceRef`, explicit `draft`/`needs_review`/`verified` statuses, JSON output and registry payloads. | DONE for schema baseline | Real LLM extraction remains unverified; reviewed-card promotion is demonstrated. |
| Evidence-linked RAG retrieval | `SourceChunker`, `EvidenceChunk`, `LocalLexicalRetriever`, `RetrievalEvaluator` and local in-memory `QdrantVectorRetriever` preserve line/path/source metadata; graph/API aggregate multi-source chunks; Recall@k, MRR and provenance coverage are tested. | PARTIAL | No embedding model, remote Qdrant service or reranker quality evaluation is configured. |
| Multi-model reproduction Agent | `ChatModel`/LiteLLM abstraction, installed LangGraph graph, `ReproductionPlanner`, injectable `ArtifactGenerator`, and offline fallback. | PARTIAL | Real LLM planning/code generation is unverified; the structured generation contract is covered with a fake model. |
| Code generation and dependency analysis | `TemplateArtifactWriter`, `MockCodeGenerator` and Pydantic-validated `LLMCodeGenerator` produce hashed Python/pytest artifacts; `PythonDependencyAnalyzer` emits static import reports. | PARTIAL | A real provider call, dependency installation and general-model runtime acceptance remain unverified. |
| Isolated code execution | `ExecutionPolicy`, `ExecutionResult`, Docker SDK runner and WSL2 `WslDockerSandboxRunner`; inventory forecast unittest passed inside `python:3.12-slim` with network disabled and read-only workspace; the executable LangGraph path also returned passed execution/runtime reports in WSL2. | PARTIAL | Windows Docker pipe is optional; final capability promotion requires a complete draft from a real provider. |
| Automated tests, error analysis and repair | `ValidationService` performs AST/contract/runtime report checks; generated unittest passed in WSL Docker; WSL integration test demonstrates fail → bounded template repair → pass; `LLMRepairer` validates existing-artifact patches, updates hashes and is selectable from CLI/API; LangGraph conditional routing returns execution, updated bundle and repair loop state; CLI `--metrics-file`, API `/metrics` and API `/reproduce.metrics` collect/evaluate predictions with thresholded MAE/RMSE. | PARTIAL | No real provider repair call or multi-metric domain policy is demonstrated. |
| Capability versioning and persistence | SQLite `CapabilityRegistry`, immutable versions, search and passing-report-only promotion; WSL CLI run promoted the human-reviewed inventory card to `verified`; API `persist=true` writes to configured SQLite and requires both a passing runtime report and, when requested, a passing sandbox metric report. | PARTIAL | Real-provider extraction and automated reuse workflow remain open. |
| Historical capability retrieval and reuse | Lexical retrieval and registry name search are independently tested; `search_reusable()` and CLI `reuse` filter to verified versions; `reproduce --reuse-query` and API `reuse_query` select verified cards and feed them into a new plan, with the selected version returned for provenance. | PARTIAL | Retrieval hits are not yet automatically selected into a new reproduction plan without an explicit reuse query. |
| Complete end-to-end demo | `algo-weaver reproduce --capability-file ... --backend wsl --execute` promoted a card to `verified`; `--reuse-query` then selected and revalidated that verified card in WSL Docker; the CLI also produced MAE/RMSE threshold reports; FastAPI `/reproduce?execute=true` exposes the same sandbox boundary and bounded repair result; multi-source CLI/API inputs preserve provenance. | PARTIAL | The verified path is human-reviewed; real-provider extraction and LLM repair are not demonstrated. |

## Verification evidence

- `uv run pytest -q`: 105 passed, 0 skipped after installing the declared LangGraph, API, retrieval and execution dependencies.
- `uv run ruff check src tests`: passed.
- `uv run mypy src`: passed for 41 source files.
- Mock CLI reproduction run created `algorithm.py`, `test_algorithm.py`, `reproduction_bundle.json`, `dependency_report.json` and `validation_reports.json`.
- WSL CLI `--backend wsl --execute` recorded `status=passed` for the generated unittest. The reviewed-capability run promoted `cap_inventory_forecast_reviewed` to `verified`, and `--reuse-query` revalidated that verified card; the Mock extraction run remained `needs_review`.
- FastAPI tests cover `/health`, `/extract`, `/metrics` and `/reproduce`; execution, bounded repair, sandbox metric collection and pending registry persistence are covered with injected fake runners. A real `/reproduce` WSL2 run returned `execution=passed`, `metric_execution=passed`, and thresholded MAE/RMSE `overall_status="passed"` for the inventory moving-average scenario.
- Git branch `feat/api-capability-reuse` contains the current generation, repair, API metrics and verified reuse boundaries; `main` has not been merged.
- GitHub Actions run #72 passed on both Python 3.12 and 3.13 after the WSL platform gate, CLI error-boundary, structured repair, API metrics and verified reuse changes.

## Acceptance conclusion

The current project is a well-tested partial MVP baseline. Real isolated execution and the inventory API metric path are directly verified through WSL2 Docker; the full MVP gate remains open because real-provider extraction, real LLM repair and automated verified capability reuse lack direct evidence.
