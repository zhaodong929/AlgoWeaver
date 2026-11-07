# Windows runtime setup for final sandbox acceptance

The repository contains both a Docker SDK runner and an explicit WSL2 runner. The current verified setup uses the Ubuntu-24.04 distribution at `D:\WSL\Ubuntu-24.04`.

1. Ensure the Ubuntu-24.04 WSL2 distribution is running and Docker Engine is active inside it.
2. Verify with `wsl -d Ubuntu-24.04 -- docker version`.
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
  --backend wsl `
  --execute
```

The verified WSL run produced `execution_result.json` with `status="passed"`. The current Mock capability remains `needs_review`, so it is intentionally not promoted; a complete draft from a real provider is required for the final verified promotion gate.
