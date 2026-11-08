# AlgoWeaver MVP acceptance matrix

Audit date: 2026-11-08 (Asia/Shanghai)

`DONE` means the stated scope has direct code, test and runtime evidence. `PARTIAL`
means a usable path exists but the full requested scope still needs evidence.
`BLOCKED` means an external environment condition prevents the required integration.

| Must-have | Current evidence | Status | Remaining acceptance gap |
|---|---|---|---|
| Multi-source documents and historical code | `SourceIngestor` handles text/Markdown/Python/CSV/JSON/YAML; Docling and stdlib fallbacks cover office/PDF boundaries; `PythonCodeParser` indexes imports/classes/functions. | PARTIAL | Complex PDF/Office layout and repository-scale parsing remain unverified. |
| Algorithm knowledge extraction | `CapabilityExtractor`, Mock and LiteLLM adapters, Pydantic capability cards, missing-information handling and source evidence. Live Qwen extraction was run through the configured Bailian endpoint. | PARTIAL | More real business documents and conflict/uncertainty evaluation. |
| Standard capability cards | `AlgorithmCapability`, `EvidenceRef`, draft/needs_review/verified states and SQLite registry payloads. | DONE for schema and reviewed-card promotion | Automated confidence scoring remains open. |
| Evidence-linked RAG retrieval | Lexical retrieval plus real `qwen3.7-text-embedding-flash` vectors, Qdrant memory/local/server adapters and `qwen3-rerank`; provenance fields survive fusion. Local persistence was reopened across client instances. | PARTIAL | Docker Qdrant server smoke test and Recall@k/MRR report; Docker Hub image pull currently times out. |
| Multi-model reproduction Agent | LangGraph retrieve→plan→generate→validate graph; Qwen primary model and DeepSeek code model live JSON/code-generation boundaries were exercised. | PARTIAL | A real-provider generated artifact still needs a complete independent promotion run. |
| Code generation and dependency analysis | Template, Mock and Pydantic-validated LLM generators produce hashed Python/pytest artifacts; AST dependency reports are emitted. | PARTIAL | Dependency installation policy and generated-test coverage gate. |
| Isolated code execution | WSL2 Docker `python:3.12-slim`, network disabled, read-only workspace, resource limits and runtime reports. Inventory tests and metrics passed. | DONE for reviewed inventory path | Production runner deployment remains separate from the public API container. |
| Automated tests, error analysis and repair | Static/runtime/metric validation; bounded repair; live DeepSeek repair passed for import error, missing pandas dependency and timeout, plus controlled regression tests. | PARTIAL | Broader dependency classes, multi-attempt repair and failure-memory write-back. |
| Capability versioning and persistence | SQLite immutable versions, verified-only promotion, metric-aware gates, CLI/API persistence and verified reuse. Inventory version 2 was promoted and reused. | DONE for reviewed inventory path | Semantic version comparison and similarity reuse. |
| Historical capability retrieval and reuse | Registry search, CLI `reuse`, API `reuse_query`/`auto_reuse`, and retrieval evidence are implemented and tested. | PARTIAL | Semantic similarity reuse beyond deterministic name matching. |
| CLI/API/UI | Typer CLI, FastAPI `/health`/`/extract`/`/metrics`/`/reproduce`, Streamlit AppTest, live FastAPI smoke and Streamlit health/root HTTP checks. | PARTIAL | Browser manual acceptance record and hosted deployment. |
| Production security boundary | API-key middleware, 401/429 tests, rolling rate limit, Caddy HTTPS configuration and production Compose bundle. | PARTIAL | Actual DNS/certificate deployment and gateway-level multi-replica rate limiting. |
| Complete end-to-end demo | Inventory document + CSV → reviewed capability → generated code/tests → WSL sandbox → MAE/RMSE → verified registry → `reuse-query` revalidation. Report: `docs/reports/test_reports/2026-11-08-inventory-delivery.md`. | DONE for reviewed inventory path | Live LLM generation and full browser path should be demonstrated together. |
| Open-license second scenario | UCI AI4I 2020 Predictive Maintenance Dataset, DOI `10.24432/C5HS5C`, CC BY 4.0, with attribution, transparent rule baseline and tests. | DONE as standalone scenario | Connect the scenario to generic Agent/API metric adapters. |

## Verification evidence

- `uv run --no-sync pytest -q`: **129 passed**.
- `uv run --no-sync ruff check src tests examples`: passed.
- `uv run --no-sync mypy src`: passed for 46 source files.
- Inventory WSL2 report: execution passed, MAE `0.8888888888888881`, RMSE
  `1.3608276348795427`, verified promotion and verified reuse.
- Live repair report: `docs/reports/test_reports/2026-11-08-live-repair-scenarios.md`.
- Local Qdrant persistence test: collection reopened in a second client and the
  provenance chunk remained searchable.
- Streamlit runtime: `/_stcore/health` HTTP 200 and root page HTTP 200; AppTest
  exercises the form and result panels.
- GitHub Actions runs #89 and #90 passed on Python 3.12 and 3.13. The latest
  documentation/repair/Qdrant commits are pushed to `feat/api-capability-reuse`.

## Acceptance conclusion

The reviewed inventory scenario is a runnable, reproducible MVP demonstration with
isolated execution, metrics, verified persistence and reuse. The remaining MVP gate is
the Docker Qdrant service smoke test and actual hosted HTTPS deployment; both have
configuration and evidence procedures, but are not claimed as completed while the
current registry network and deployment DNS are unavailable.
