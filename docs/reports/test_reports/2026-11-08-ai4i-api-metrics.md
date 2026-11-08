# AI4I 预测性维护 API 指标报告

日期：2026-11-08（Asia/Shanghai）

## 数据与接口

- 数据：`examples/predictive_maintenance/ai4i2020.csv`，UCI AI4I 2020，10,000 行，CC BY 4.0。
- 预测器：项目审核的透明双阈值规则 `flag_high_risk`。
- API：`POST /metrics/classification`。
- 标签：`Machine failure`；预测标签由规则输出的 `is_high_risk` 转换得到。

## 实际结果

```text
HTTP status: 200
sample_count: 10000
accuracy:  0.9663
precision: 1.0000  (threshold 0.90, passed)
recall:    0.0059  (threshold 0.50, failed)
f1:        0.01173
overall_status: failed
```

该结果保留了真实失败信息：透明规则基线虽然精度高，但召回率很低，不能被标记为满足生产级预测性维护指标。API 已能对第二场景执行统一指标检查，后续可在同一接口上替换更强的模型或调节业务阈值。

## 可复现命令

```powershell
uv run --no-sync python -c "import csv,sys; from pathlib import Path; from fastapi.testclient import TestClient; from algo_weaver.api import create_app; sys.path.insert(0,'examples/predictive_maintenance'); from algorithm import flag_high_risk; rows=list(csv.DictReader(Path('examples/predictive_maintenance/ai4i2020.csv').open(encoding='utf-8-sig',newline=''))); preds=flag_high_risk(rows); actual=[int(r['Machine failure']) for r in rows]; predicted=[int(x['is_high_risk']) for x in preds]; r=TestClient(create_app()).post('/metrics/classification',json={'task':'predictive_maintenance','actual':actual,'predicted':predicted,'min_precision':0.9,'min_recall':0.5}); print(r.status_code, r.json())"
```
