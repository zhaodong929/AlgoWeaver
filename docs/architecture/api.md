# Optional API surface

`algo_weaver.api.create_app()` creates a FastAPI application when the `api` extra is installed. The endpoints are thin adapters over existing services:

- `GET /health` reports the configured mode.
- `POST /extract` accepts source text and returns an evidence-linked capability card.
- `POST /metrics` evaluates actual and predicted numeric sequences with MAE/RMSE and optional thresholds.
- `POST /reproduce` returns source records, multi-source retrieval hits, a reproduction plan, artifacts, validation reports and a dependency report. The primary `source_text` can be accompanied by `additional_sources` entries for historical code, experiment notes or test reports. Set `generation_mode` to `template`, `mock` or `llm`; the latter requires `mode="litellm"` and a configured provider. Set `execute=true` to write the artifacts to a temporary workspace and run the generated test command through the configured Docker/WSL sandbox. Set `repair=true` to enable bounded repair; the default `repair_mode="template"` restores the reviewed bundle, while `repair_mode="llm"` requires `mode="litellm"` and validates a model-proposed `RepairPatch`. Set `persist=true` to save the capability in the configured SQLite registry.

Execution is opt-in and the runner boundary is injectable for tests. Persistence uses `ALGOWEAVER_REGISTRY_PATH` (default `data/processed/capabilities.sqlite3`); a capability is promoted only when the returned runtime report is independently `passed`. The module does not create a global FastAPI app at import time, so the core package remains usable without the optional API dependency.
