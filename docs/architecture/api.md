# Optional API surface

`algo_weaver.api.create_app()` creates a FastAPI application when the `api` extra is installed. The endpoints are thin adapters over existing services:

- `GET /health` reports the configured mode.
- `POST /extract` accepts source text and returns an evidence-linked capability card.
- `POST /reproduce` returns retrieval hits, a reproduction plan, artifacts, validation reports and a dependency report. Set `execute=true` to write the artifacts to a temporary workspace and run the generated test command through the configured Docker/WSL sandbox; set `repair=true` to enable the bounded template repair callback.

Execution is opt-in and the runner boundary is injectable for tests. The API does not promote capabilities to `verified`; review and registry write-back remain explicit service/CLI steps. The module does not create a global FastAPI app at import time, so the core package remains usable without the optional API dependency.
