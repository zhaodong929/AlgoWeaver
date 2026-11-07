# Domain metric evaluation

`RegressionMetricEvaluator` computes deterministic MAE and RMSE for configured actual/predicted sequences. Optional thresholds produce an explicit `passed`/`failed`/`unscored` report. The evaluator is independent of model providers and can be called after a sandbox-generated prediction file is collected.
