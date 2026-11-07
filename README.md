# AlgoWeaver

**Algorithm Intelligence & Reproduction Agent**  
An agentic system for algorithm knowledge extraction, code reproduction, automated verification, and reusable capability accumulation.

> Current milestone: **v0.1.1 — v0.1.0 audit + evidence-linked extraction + multi-source text ingestion**.

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
- CLI command that reads Markdown/text and writes a JSON capability card.
- Pytest coverage for schema validation, extraction, and graph execution.

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
uv sync --group dev

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
```

## 4. Install on Linux/macOS

```bash
cd algo-weaver
uv sync --group dev
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

# Optionally persist the draft and request Docker execution.
# The WSL backend uses the D-drive Ubuntu Docker daemon and records `blocked` only when that daemon is unavailable.
uv run algo-weaver reproduce \
  --input examples/moving_average/algorithm.md \
  --output-dir data/processed/reproduction \
  --registry data/processed/capabilities.sqlite3 \
  --execute \
  --backend wsl \
  --mode mock

# Optional FastAPI surface
uv sync --group dev --extra api
uv run uvicorn algo_weaver.api:create_app --factory --host 127.0.0.1 --port 8000
```

## 5. Enable a real model (LiteLLM)

Edit `.env`:

```dotenv
ALGOWEAVER_LLM_MODE=litellm
ALGOWEAVER_LLM_MODEL=openai/<your-model-name>
ALGOWEAVER_LLM_API_KEY=<your-api-key>
ALGOWEAVER_LLM_API_BASE=
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
- `execution`: Docker SDK; the actual sandbox image and runtime policy will be added in the execution milestone.

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
- [x] `uv run pytest -q` passes in the current environment: 62 passed, 0 skipped.
- [x] The CLI extracts a JSON capability card from the sample Markdown file in mock mode.
- [x] The capability card records source provenance.
- [x] Mock-generated output is never marked `verified`.
- [x] Real provider configuration is loaded from environment variables, not source code.
- [x] Supported text-like sources are normalized and hashed by `SourceIngestor`.

The full requirements traceability matrix is in `docs/requirements/requirements_matrix.md`. The current implementation supports a deterministic moving-average reproduction template, but does not yet claim general code reproduction, sandbox execution, automatic repair or semantic retrieval completion.

The current retrieval baseline is intentionally lexical and local. It returns line-addressable evidence chunks with source IDs, paths and metadata; Qdrant, embeddings and reranking remain later adapters. The primary domain example is inventory demand forecasting with a moving-average baseline in `examples/inventory_forecast/`. The `reproduce` command demonstrates the current CLI-first path and leaves generated artifacts explicitly unverified until sandbox execution passes.

For a human-reviewed capability card, pass `--capability-file examples/inventory_forecast/reviewed_capability.json`; with `--backend wsl --execute --registry ...`, the runtime report can promote the card to `verified`. This path is explicitly human-reviewed and does not claim real LLM extraction.

For the remaining Windows Docker runtime gate, see `docs/implementation/windows_runtime_setup.md`.

## 9. Engineering principles

1. Evidence before claims: extracted fields should be traceable to source material.
2. Draft is not verified: only independent tests and review can promote a capability.
3. Deterministic control where possible: use code for validation, routing, and execution limits; use LLMs for semantic interpretation and generation.
4. Sandbox all generated code: never execute untrusted code directly on the host.
5. Keep provider interfaces replaceable: application services depend on the `ChatModel` protocol, not a specific vendor SDK.
