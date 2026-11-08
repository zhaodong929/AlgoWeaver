# Scenario performance report

**Date:** 2026-11-08 (Asia/Shanghai)

## Inventory moving average

The WSL2 Docker acceptance run processed five sales observations with window 3.
The sandbox execution duration was `0.775` seconds and the metric command duration
was `0.624` seconds. MAE was `0.8888888888888881` and RMSE was
`1.3608276348795427`, both below threshold `3.0`.

## UCI AI4I rule baseline

The dependency-free predictive-maintenance baseline processed all 10,000 rows from
`examples/predictive_maintenance/ai4i2020.csv` in `0.005131300` seconds in the
local Python 3.13 process. It flagged 2 high-risk rows, with precision `1.0` and
recall `0.0058997050147492625`. The low recall is expected from the intentionally
conservative transparent rule and is recorded as a limitation, not a quality claim.
