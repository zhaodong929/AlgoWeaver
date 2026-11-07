# Optional API surface

`algo_weaver.api.create_app()` creates a FastAPI application when the `api` extra is installed. The endpoints are thin adapters over existing services:

- `GET /health` reports the configured mode.
- `POST /extract` accepts source text and returns an evidence-linked capability card.
- `POST /reproduce` returns retrieval hits, a reproduction plan, unverified artifacts, static validation reports and a dependency report.

The API never executes generated code. Docker execution and verified promotion remain explicit CLI/service steps. The module does not create a global FastAPI app at import time, so the core package remains usable without the optional API dependency.
