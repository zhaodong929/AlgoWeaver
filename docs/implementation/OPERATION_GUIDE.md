# AlgoWeaver 操作指南

更新时间：2026-11-08（Asia/Shanghai）

本文面向导师验收、答辩演示和 Windows 本地复现。主场景是库存需求预测：系统从算法说明和历史销量资料开始，完成能力抽取、证据检索、复刻计划、代码生成、隔离执行、MAE/RMSE 评估、能力注册和后续复用。

## 1. 获取正确版本

当前可交付提交为 `b0b22fe`。GitHub 默认分支 `feat/initial-audit-and-ingestion` 已从旧提交 `339a020` 普通快进到该提交；也可以直接使用功能分支 `feat/api-capability-reuse`。

```powershell
git clone -b feat/initial-audit-and-ingestion https://github.com/zhaodong929/AlgoWeaver.git
cd AlgoWeaver
git rev-parse --short HEAD
```

预期提交为 `b0b22fe` 或其后续提交。若需要查看完整开发历史：

```powershell
git branch -a
git log --oneline --decorate -12
```

## 2. 安装环境

要求：Windows 10/11、Python 3.12 或 3.13、uv、Git。WSL2 和 Docker 用于真实隔离执行与持久化 Qdrant；只做 mock 演示时可以不启动它们。

```powershell
uv sync --group dev --extra api --extra retrieval --extra execution --extra ui
uv run pytest -q
uv run ruff check src tests
uv run mypy src
```

当前基线结果：pytest 139 passed，Ruff 通过，Mypy 通过。

## 3. 五分钟离线演示

离线演示使用 Mock 模型、内存检索和模板生成，不消耗百炼额度，也不需要 API Key。若当前目录存在 `.env`，下面的环境变量会在本次 PowerShell 会话中覆盖其真实 provider 设置。

窗口一启动 FastAPI：

```powershell
$env:ALGOWEAVER_LLM_MODE = "mock"
$env:ALGOWEAVER_EMBEDDING_MODE = "mock"
$env:ALGOWEAVER_RERANKER_MODE = "mock"
$env:ALGOWEAVER_QDRANT_MODE = "memory"
uv run uvicorn algo_weaver.api:create_app --factory --host 127.0.0.1 --port 8000
```

窗口二启动 Streamlit：

```powershell
$env:ALGOWEAVER_UI_API_BASE = "http://127.0.0.1:8000"
uv run streamlit run src/algo_weaver/ui.py --server.port 8501
```

浏览器打开 `http://127.0.0.1:8501`，保持左侧的 `mock + template`，点击“运行 AlgoWeaver”。结果页应出现：能力摘要、检索证据、复刻计划、代码与测试、验证报告和能力资产六个面板。

## 4. API 验收

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health

$body = '{"task":"inventory_demand","actual":[10,12,14],"predicted":[11,11,15],"max_mae":1.0,"max_rmse":1.0}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/metrics `
  -ContentType 'application/json' -Body $body
```

`/health` 应返回 200；`/metrics` 应返回 `overall_status: passed`，MAE 和 RMSE 均不超过阈值。

也可以直接提交复刻请求：

```powershell
$payload = @{
  source_text = "Use a moving average over historical daily sales. Inputs: sales and window."
  source_id = "advisor-smoke"
  mode = "mock"
  generation_mode = "template"
  execute = $false
  backend = "docker"
  repair = $false
  additional_sources = @()
} | ConvertTo-Json -Depth 6
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/reproduce `
  -ContentType 'application/json' -Body $payload
```

## 5. 真实百炼模型

真实调用通过 OpenAI-compatible endpoint 和 LiteLLM 适配。密钥只放在本机 `.env`、部署平台 Secrets 或服务器环境中，不提交 GitHub。

```dotenv
ALGOWEAVER_LLM_MODE=litellm
ALGOWEAVER_LLM_MODEL=dashscope/qwen3.8-max-0902
ALGOWEAVER_CODE_LLM_MODEL=dashscope/deepseek-v4.1-flash-1017
ALGOWEAVER_LLM_API_KEY=<provider-key>
ALGOWEAVER_LLM_API_BASE=https://<workspace-id>.cn-beijing.maas.aliyuncs.com/compatible-mode/v1

ALGOWEAVER_EMBEDDING_MODE=dashscope
ALGOWEAVER_EMBEDDING_MODEL=qwen3.7-text-embedding-flash
ALGOWEAVER_EMBEDDING_API_KEY=<provider-key>
ALGOWEAVER_EMBEDDING_API_BASE=https://<workspace-id>.cn-beijing.maas.aliyuncs.com/api/v1

ALGOWEAVER_RERANKER_MODE=dashscope
ALGOWEAVER_RERANKER_MODEL=qwen3-rerank
ALGOWEAVER_RERANKER_API_KEY=<provider-key>
ALGOWEAVER_RERANKER_API_BASE=https://<workspace-id>.cn-beijing.maas.aliyuncs.com/api/v1
```

主 Agent 使用 Qwen，代码生成和修复使用 DeepSeek，向量检索使用 `qwen3.7-text-embedding-flash`，重排使用 `qwen3-rerank`。真实 API 测试受网络、TLS、额度和 provider 状态影响；出现网络错误时，先切回第 3 节的 mock 验收，不把网络失败归因于生成算法。

## 6. 库存预测真实隔离执行

主场景材料位于 `examples/inventory_forecast/`。无需真实 LLM 即可复现已审核能力卡片的隔离执行：

```powershell
$env:ALGOWEAVER_LLM_MODE = "mock"
$env:ALGOWEAVER_EMBEDDING_MODE = "mock"
$env:ALGOWEAVER_RERANKER_MODE = "mock"
$env:ALGOWEAVER_QDRANT_MODE = "memory"

uv run algo-weaver reproduce `
  --input examples/inventory_forecast/algorithm.md `
  --output-dir data/processed/acceptance_inventory `
  --capability-file examples/inventory_forecast/reviewed_capability.json `
  --registry data/processed/acceptance_inventory/capabilities.sqlite3 `
  --metrics-file examples/inventory_forecast/sales_history.csv `
  --max-mae 2.0 `
  --max-rmse 3.0 `
  --execute `
  --backend wsl `
  --mode mock `
  --generation-mode template
```

预期：沙箱状态 `passed`，MAE `0.8888888888888881`，RMSE `1.3608276348795427`，能力状态 `verified`。生成的 `execution_result.json`、`metric_report.json`、`registry_record.json` 和代码产物用于验收留档。

## 7. 持久化 Qdrant

在 WSL2/Docker 中启动服务：

```powershell
docker compose -f deploy/qdrant/docker-compose.yml up -d
docker compose -f deploy/qdrant/docker-compose.yml ps
```

Windows 访问 WSL Docker 时，如果 `127.0.0.1:6333` 不稳定，获取 WSL IP：

```powershell
wsl.exe -e sh -lc "hostname -I"
```

然后配置：

```powershell
$env:ALGOWEAVER_QDRANT_MODE = "server"
$env:ALGOWEAVER_QDRANT_URL = "http://<wsl-ip>:6333"
```

Qdrant 使用命名卷 `qdrant_storage`。已有验收证明：写入资料、重启 Qdrant 容器后仍能检索，真实 embedding 与 reranker 的四条 smoke query Recall@2/MRR 均为 1.0。
如果 Windows 通过本机代理访问 WSL IP，请把该 IP 加入 `NO_PROXY`/`no_proxy`；当前环境中 WSL 内部 `curl http://127.0.0.1:6333/readyz` 稳定返回 200，而 Windows 到 WSL 的 NAT 转发可能受代理影响。可靠的持久化验收命令是：

```powershell
wsl.exe -d Ubuntu-24.04 -- bash -lc "curl -fsS http://127.0.0.1:6333/readyz; curl -fsS http://127.0.0.1:6333/collections"
```

## 8. API Key、限流和 HTTPS

本地 API Key 模式：

```powershell
$env:ALGOWEAVER_API_AUTH_MODE = "api_key"
$env:ALGOWEAVER_API_KEY = "<long-random-secret>"
```

Streamlit 左侧 API Key 输入框会通过 `X-API-Key` 请求头发送。已有真实 smoke：无 Key 返回 401，合法 Key 返回 200，超过进程限额返回 429。

临时给导师展示时，只暴露 Streamlit：

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

长期公网服务需要域名、服务器、80/443 入站和 Caddy ACME。生产 Compose 位于 `deploy/production/`，完整步骤见 `docs/deployment/github_mentor_guide.md`。

第二场景的通用指标接口：

```powershell
$body = '{"task":"predictive_maintenance","actual":[1,0,1,0],"predicted":[1,0,0,0],"min_precision":0.9,"min_recall":0.5}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/metrics/classification `
  -ContentType 'application/json' -Body $body
```

完整 10,000 行 AI4I 结果和透明规则的低召回限制见 `docs/reports/test_reports/2026-11-08-ai4i-api-metrics.md`。

能力版本比较：

```powershell
uv run algo-weaver diff --capability-id <capability-id> --from-version 1 --to-version 2 `
  --registry data/processed/capabilities.sqlite3
```

## 9. 导师五分钟验收清单

1. 打开 Streamlit 页面，确认品牌、任务工作台和六阶段流程条正常。
2. 使用默认库存预测文本运行 `mock + template`。
3. 在“检索证据”查看来源、hash、行号和命中片段。
4. 在“复刻计划”和“代码与测试”查看计划、代码、测试和依赖分析。
5. 上传 `examples/inventory_forecast/sales_history.csv`，确认追加来源进入结果。
6. 使用第 6 节命令执行 WSL/Docker，检查测试、MAE/RMSE 和 verified 注册表。
7. 切换“执行记录”“能力资产”“系统设置”，确认页面导航可用。
8. 查看 GitHub Actions，确认 Python 3.12/3.13 两个矩阵作业均为绿色。

## 10. 常见问题

- 页面无法连接 API：检查 FastAPI 进程和左侧 API 地址。
- 401：API 开启了 Key 模式，填写与后端完全相同的 Key。
- 429：触发了单进程限流，等待窗口结束或调整本地开发配置。
- 真实 provider TLS/额度失败：先记录为外部 API 环境问题，切回 mock；不要把它标记为算法生成失败。
- WSL `localhost` 不稳定：使用 `hostname -I` 得到的 WSL IP。
- ACME 失败：检查 DNS、80/443 和服务器公网可达性；一次性演示使用 Quick Tunnel。
