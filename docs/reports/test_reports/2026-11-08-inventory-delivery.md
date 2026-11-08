# Inventory demand forecasting delivery report

**Date:** 2026-11-08 (Asia/Shanghai)  
**Branch:** `feat/api-capability-reuse`  
**Scenario:** inventory demand forecasting with a fixed-window moving average  
**Evidence policy:** template generation and reviewed capability inputs are labelled explicitly; no Mock result is presented as a live LLM result.

## Reproduction path

The run used the following project materials:

- `examples/inventory_forecast/algorithm.md` — business description and acceptance rules;
- `examples/inventory_forecast/sales_history.csv` — five daily sales observations;
- `examples/inventory_forecast/reviewed_capability.json` — human-reviewed capability card.

The command below ingested the document and CSV, generated `algorithm.py` and
`test_algorithm.py`, executed the tests inside the WSL2 Docker boundary using
`python:3.12-slim`, and evaluated the moving-average output.

```powershell
uv run --no-sync algo-weaver reproduce `
  --input examples/inventory_forecast/algorithm.md `
  --additional-input examples/inventory_forecast/sales_history.csv `
  --output-dir data/processed/final_demo_reviewed `
  --mode mock --generation-mode template `
  --backend wsl --execute `
  --metrics-file examples/inventory_forecast/sales_history.csv `
  --metrics-window 3 --max-mae 3 --max-rmse 3 `
  --capability-file examples/inventory_forecast/reviewed_capability.json `
  --registry data/processed/final_demo_registry.sqlite3
```

Observed result:

- ingestion: 1 additional source ingested, 0 unsupported, 0 failed;
- sandbox execution: `passed`, image `python:3.12-slim`, 2 generated unit tests passed;
- metric execution: `passed`, three predictions returned;
- MAE: `0.8888888888888881`, threshold `3.0`, passed;
- RMSE: `1.3608276348795427`, threshold `3.0`, passed;
- registry: capability version 2 promoted from `draft` to `verified`;
- sandbox duration: `0.775` seconds;
- generated artifacts: `algorithm.py`, `test_algorithm.py`, dependency report and validation reports.

## Verified reuse

The verified card was then reused through the registry:

```powershell
uv run --no-sync algo-weaver reproduce `
  --input examples/inventory_forecast/algorithm.md `
  --output-dir data/processed/final_demo_reuse `
  --mode mock --generation-mode template --backend wsl --execute `
  --reuse-query "库存需求移动平均预测" `
  --registry data/processed/final_demo_registry.sqlite3
```

The command selected verified capability version 2, executed the generated tests in
the isolated runner, promoted the passing result, and wrote a new verified registry
version. This demonstrates persistence and reuse of the reviewed capability card.

## Scope and remaining evidence

This report is a real WSL2 sandbox and SQLite registry acceptance run. Generation is
the reviewed deterministic template path; the separate live LLM generation/repair
evidence is recorded in `2026-11-08-live-llm-reproduction.md`. Persistent Qdrant
service validation is recorded separately in `2026-11-08-qdrant-persistence.md`.
