# Windows runtime setup for final sandbox acceptance

The repository already contains the Docker SDK and a Docker-only runner. The remaining runtime gate is a working Docker Desktop/WSL2 daemon.

1. Install Docker Desktop from the official Docker distribution and enable its WSL2 backend.
2. Restart Docker Desktop and verify `docker version` from PowerShell.
3. From the repository root, synchronize all relevant extras:

```powershell
uv sync --group dev --extra api --extra retrieval --extra execution
```

4. Run the inventory forecast demo with execution enabled:

```powershell
uv run algo-weaver reproduce `
  --input examples/inventory_forecast/algorithm.md `
  --output-dir data/processed/inventory_forecast_exec `
  --registry data/processed/capabilities.sqlite3 `
  --mode mock `
  --execute
```

The expected pre-runtime state is `blocked` when the Docker daemon is absent. A real runtime acceptance requires `execution_result.json` with `status="passed"`; only then can an independent report be considered for verified promotion.
