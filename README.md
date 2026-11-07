# AlgoWeaver

**Algorithm Intelligence & Reproduction Agent**  
An agentic system for algorithm knowledge extraction, code reproduction, automated verification, and reusable capability accumulation.

> Current milestone: **MVP execution baseline — evidence-linked extraction, executable LangGraph workflow, WSL2 sandbox, API and SQLite capability persistence**.

## 1. What is implemented

- Pydantic schemas for algorithm drafts, capability cards, parameters, and evidence references.
- Provider-neutral chat model protocol.
- Deterministic mock model for offline development and tests.
- LiteLLM adapter for multiple model providers and OpenAI-compatible endpoints.
- A minimal LangGraph extraction workflow.
- An offline fallback runner for the extraction workflow when optional LangGraph is not installed.
- Dependency-free ingestion for Markdown, text, Python, CSV, JSON and YAML with SHA-256 provenance.
- Lazy Docling boundaries for PDF, DOCX, PPTX and XLSX; missing optional dependencies are reported explicitly.
- Python AST indexing for imports, classes, methods, functions and source locations without executing code.
- Provenance-preserving local lexical retrieval with source and metadata filters.
- Optional Qdrant in-memory vector adapter with the same provenance contract.
- Deterministic static validation reports for capability contracts and generated Python source.
- SQLite capability versioning with passing-report promotion to `verified`.
- Docker-only execution boundary with explicit `blocked` behavior when the daemon or SDK is unavailable.
- LangGraph reproduction flow with optional artifact writing, sandbox execution, conditional bounded repair and runtime reports.
- Provider-neutral code generation boundary with deterministic `template`, offline `mock` and structured `llm` modes; model output is Pydantic-validated before artifacts are written.
- Bounded repair boundary with reviewed template repair and optional structured LLM patches that can target existing artifacts only.
- CLI and FastAPI surfaces for extraction, reproduction, sandbox execution, repair, registry persistence and MAE/RMSE threshold evaluation.
- WSL2 Docker runtime acceptance for the reviewed inventory forecasting capability.
- Pytest coverage for schema validation, extraction, graph execution, API behavior and safety boundaries.

The mock model is for engineering smoke tests only. Its output is explicitly marked as needing review; it must not be treated as a real algorithm extraction or a verified capability.

## 2. Requirements

- Python 3.12 or 3.13
- `uv` package manager
- Git
- For real model calls: an API key and a LiteLLM-supported model/provider

GPU is not required for this first milestone because model inference is API-based by default. Local GPU inference and embedding/reranking will be added after checking the actual GPU model and VRAM.

## 3. Install on Windows PowerShell

```powershell
# 1. Clone or enter the repository
cd algo-weaver

# 2. Create the virtual environment and install core + development dependencies
uv sync --group dev --extra api --extra retrieval --extra execution

# 3. Create local environment config
Copy-Item .env.example .env

# 4. Run tests
uv run pytest

# 5. Print version
uv run algo-weaver version

# 6. Run the first extraction module in offline mock mode
uv run algo-weaver extract `
  --input examples/moving_average/algorithm.md `
  --output data/processed/moving_average_capability.json `
  --mode mock

# Windows WSL2 runtime demo (after WSL Docker setup)
uv run algo-weaver reproduce `
  --input examples/inventory_forecast/algorithm.md `
  --output-dir data/processed/reproduction `
  --capability-file examples/inventory_forecast/reviewed_capability.json `
  --registry data/processed/capabilities.sqlite3 `
  --execute `
  --backend wsl `
  --mode mock
```

## 4. Install on Linux/macOS

```bash
cd algo-weaver
uv sync --group dev --extra api --extra retrieval --extra execution
cp .env.example .env
uv run pytest
uv run algo-weaver version
uv run algo-weaver extract \
  --input examples/moving_average/algorithm.md \
  --output data/processed/moving_average_capability.json \
  --mode mock

# Build a reproduction bundle and static validation reports (still unverified)
uv run algo-weaver reproduce \
  --input examples/moving_average/algorithm.md \
  --output-dir data/processed/reproduction \
  --mode mock

# Exercise the offline generation boundary while keeping artifacts unverified.
uv run algo-weaver reproduce \
  --input examples/moving_average/algorithm.md \
  --output-dir data/processed/reproduction \
  --generation-mode mock \
  --mode mock

# Add historical code or experiment material to the same retrieval context.
uv run algo-weaver reproduce \
  --input examples/inventory_forecast/algorithm.md \
  --additional-input examples/inventory_forecast/sales_history.csv \
  --output-dir data/processed/reproduction \
  --mode mock

# FastAPI surface
uv run uvicorn algo_weaver.api:create_app --factory --host 127.0.0.1 --port 8000

# API metric evaluation example
curl -X POST http://127.0.0.1:8000/metrics \
  -H "Content-Type: application/json" \
  -d '{"task":"inventory_demand","actual":[10,12,14],"predicted":[11,11,15],"max_mae":1.0,"max_rmse":1.0}'

# API reproduction is static by default. Add execute=true for explicit Docker/WSL execution,
# repair=true for bounded template repair, and persist=true for configured SQLite write-back.
# `additional_sources` accepts historical code, experiment notes or test reports
# and their provenance is preserved in the returned retrieval hits.
```

## 5. Enable a real model (LiteLLM)

Edit `.env`:

```dotenv
ALGOWEAVER_LLM_MODE=litellm
ALGOWEAVER_LLM_MODEL=dashscope/qwen3.8-max-0902
ALGOWEAVER_CODE_LLM_MODEL=dashscope/deepseek-v4.1-flash-1017
ALGOWEAVER_LLM_API_KEY=<your-api-key>
ALGOWEAVER_LLM_API_BASE=https://<workspace-id>.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
ALGOWEAVER_LLM_TEMPERATURE=0.0
```

Examples of LiteLLM model naming patterns (verify the exact model identifier supported by your provider):

```dotenv
# OpenAI
ALGOWEAVER_LLM_MODEL=openai/<model-name>

# DeepSeek
ALGOWEAVER_LLM_MODEL=deepseek/<model-name>

# Qwen / DashScope
ALGOWEAVER_LLM_MODEL=dashscope/<model-name>

# Ollama local endpoint
ALGOWEAVER_LLM_MODEL=ollama/<model-name>
ALGOWEAVER_LLM_API_BASE=http://localhost:11434

# OpenAI-compatible endpoint
ALGOWEAVER_LLM_MODEL=openai/<model-name>
ALGOWEAVER_LLM_API_BASE=https://<provider-compatible-endpoint>/v1
```

Then run:

```bash
uv run algo-weaver extract --input examples/moving_average/algorithm.md --mode litellm
```

`ALGOWEAVER_LLM_MODEL` is used for extraction and planning. When set,
`ALGOWEAVER_CODE_LLM_MODEL` is used for LLM code generation and repair. The
current live Bailian acceptance used `qwen3.8-max-0902` for the primary Agent
and `deepseek-v4.1-flash-1017` for code generation and repair.

Optional semantic retrieval providers are configured separately:

```dotenv
ALGOWEAVER_EMBEDDING_MODE=dashscope
ALGOWEAVER_EMBEDDING_MODEL=qwen3.7-text-embedding-flash
ALGOWEAVER_EMBEDDING_API_KEY=<your-api-key>
ALGOWEAVER_EMBEDDING_API_BASE=https://<workspace-id>.cn-beijing.maas.aliyuncs.com/api/v1
ALGOWEAVER_RERANKER_MODE=dashscope
ALGOWEAVER_RERANKER_MODEL=qwen3-rerank
ALGOWEAVER_RERANKER_API_KEY=<your-api-key>
ALGOWEAVER_RERANKER_API_BASE=https://<workspace-id>.cn-beijing.maas.aliyuncs.com/api/v1
```

The provider boundaries are live-tested, while lexical retrieval remains the
default until dense/hybrid retrieval is explicitly enabled by the workflow.

Do not commit `.env` or API keys. Keep `.env.example` free of secrets.

## 6. Optional dependency groups

Install only when the corresponding milestone starts:

```bash
uv sync --group dev --extra documents
uv sync --group dev --extra code
uv sync --group dev --extra retrieval
uv sync --group dev --extra api
uv sync --group dev --extra observability
uv sync --group dev --extra execution
```

- `documents`: Docling for PDF/DOCX/PPTX/XLSX ingestion.
- `code`: Tree-sitter parsing for syntax-aware code indexing.
- `retrieval`: Qdrant client for hybrid retrieval infrastructure.
- `api`: FastAPI and Uvicorn.
- `observability`: Langfuse and OpenTelemetry.
- `execution`: Docker SDK and the WSL2 Docker runner used by the reviewed runtime demo.

## 7. Project structure

```text
src/algo_weaver/
├── agents/       # LangGraph workflows
├── llm/          # Provider adapters and model factory
├── schemas/      # Pydantic domain schemas
├── services/     # Capability extraction business logic
├── config.py     # Environment-based settings
└── cli.py        # Command-line interface

tests/            # Automated tests
examples/         # Reproducible sample inputs
data/              # Local input/output data (not committed)
docs/              # Architecture and design documents
```

## 8. Current acceptance status

- [x] `uv sync --group dev --extra api --extra retrieval --extra execution` completes.
- [x] `uv run pytest -q` passes in the current environment: 114 passed, 0 skipped.
- [x] GitHub Actions CI passes on Python 3.12 and 3.13 (latest verified run #79 on `feat/api-capability-reuse`).
- [x] The CLI extracts a JSON capability card from the sample Markdown file in mock mode.
- [x] The capability card records source provenance.
- [x] Mock-generated output is never marked `verified`.
- [x] Real Bailian provider calls have been verified for the primary model, code model, embedding model and reranker.
- [x] Real provider configuration is loaded from environment variables, not source code.
- [x] Supported text-like sources are normalized and hashed by `SourceIngestor`.

The full requirements traceability matrix is in `docs/requirements/requirements_matrix.md`. The current implementation supports deterministic moving-average template generation, an offline Mock generation label, Pydantic-validated LLM generation and repair boundaries, a real WSL2 Docker execution path for the reviewed inventory capability, and live Bailian provider boundaries. Use `--generation-mode llm --mode litellm` or `--repair --repair-mode llm --mode litellm` only with a configured provider; live provider checks are recorded separately from offline tests.

The current retrieval baseline is intentionally lexical and local. It returns line-addressable evidence chunks with source IDs, paths and metadata. Injectable DashScope embedding and reranker adapters are available for the next dense/hybrid workflow; the lexical fallback remains the default. The primary domain example is inventory demand forecasting with a moving-average baseline in `examples/inventory_forecast/`. The `reproduce` command demonstrates the current CLI-first path and leaves generated artifacts explicitly unverified until sandbox execution passes.

Multiple local materials can be supplied with repeated `--additional-input` options. The API equivalent is `additional_sources`; both paths preserve each source's ingestion status and provenance in retrieval hits.

The API can reuse a verified registry capability by adding `reuse_query` to `/reproduce`; it returns the selected version in `reused_record` and skips a new capability extraction. Set `auto_reuse=true` to try a verified name match after extraction.

For a human-reviewed capability card, pass `--capability-file examples/inventory_forecast/reviewed_capability.json`; with `--backend wsl --execute --registry ...`, the runtime report can promote the card to `verified`. The same execution/repair boundary is available from FastAPI `/reproduce` with explicit request flags. These paths are explicitly human-reviewed and do not claim real LLM extraction.

Add `--repair` to enable bounded repair after a failed or timed-out sandbox run. The default restores the reviewed template; `--repair-mode llm` uses a configured provider and still requires `--mode litellm`.

Add `--metrics-file examples/inventory_forecast/sales_history.csv` to execute the generated prediction inside WSL Docker and write `metric_report.json` with MAE/RMSE.
Use `--max-mae` and `--max-rmse` to turn those metrics into an explicit pass/fail report.

Use `uv run algo-weaver reuse "库存需求" --registry data/processed/capabilities.sqlite3` to search only verified capability versions.

For the remaining Windows Docker runtime gate, see `docs/implementation/windows_runtime_setup.md`.

## 9. Engineering principles

1. Evidence before claims: extracted fields should be traceable to source material.
2. Draft is not verified: only independent tests and review can promote a capability.
3. Deterministic control where possible: use code for validation, routing, and execution limits; use LLMs for semantic interpretation and generation.
4. Sandbox all generated code: never execute untrusted code directly on the host.
5. Keep provider interfaces replaceable: application services depend on the `ChatModel` protocol, not a specific vendor SDK.
