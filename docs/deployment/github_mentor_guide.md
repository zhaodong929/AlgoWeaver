# GitHub 上线与导师测试指南

本文说明如何把 AlgoWeaver 代码发布到 GitHub，并为导师提供一个可以直接打开的
演示入口。GitHub 保存源代码、文档和 CI 记录；它本身不运行 FastAPI、Streamlit
或 Qdrant。运行环境需要在本机、临时 HTTPS 隧道、托管平台或云服务器上单独提供。

## 1. 推荐的上线路径

| 目标 | 方案 | 需要公网域名和 ACME 证书 | 适用场景 |
| --- | --- | --- | --- |
| 明天即可演示 | 本机 FastAPI + Streamlit + Cloudflare Quick Tunnel | 否，隧道提供临时 HTTPS 地址 | 一次性答辩、导师短期验收 |
| 只托管前端 | Streamlit Community Cloud + 一个可访问的 FastAPI 地址 | 否，平台提供 `streamlit.app` HTTPS | 稳定展示页面，API 另行部署 |
| 长期公网服务 | 云服务器 Docker Compose + Qdrant + Caddy | 是，DNS 指向服务器且 80/443 可达 | 持续运行、多人访问 |

最省时间的路线是第一行。它不会修改 GitHub 代码，也不把 API Key 放进浏览器
或仓库。导师打开临时地址即可操作 Streamlit 页面；页面由服务器端调用本机
FastAPI，因此 API 可以只监听本机。

## 2. GitHub 仓库与 CI

当前仓库的功能分支是 `feat/api-capability-reuse`。发布前先检查工作区，再推送
功能分支；不要强制覆盖 `main`：

```powershell
git status
git branch --show-current
git remote -v
git push origin feat/api-capability-reuse
```

`.github/workflows/ci.yml` 在每次 push 和 pull request 上运行 Python 3.12、3.13
矩阵，步骤顺序为：

1. `uv sync --group dev --extra api --extra retrieval --extra execution --extra ui`
2. `uv run ruff check .`
3. `uv run pytest --junitxml=test-results.xml`
4. `uv run mypy src`

CI 只验证可重复的离线测试，不需要把百炼、Embedding、Reranker 或 API 服务密钥
放入 GitHub。真实模型验收应在部署环境的 Secrets 中配置，并单独记录调用结果。
导师可以在仓库的 **Actions** 页面查看对应分支的绿色 CI 记录，在 **README** 和
`docs/reports/` 查看运行说明及验收报告。

## 3. 最快的本机 HTTPS 演示（推荐）

### 3.1 启动 API

在仓库根目录的第一个 PowerShell 窗口执行：

```powershell
$env:ALGOWEAVER_APP_ENV = "development"
$env:ALGOWEAVER_API_AUTH_MODE = "none"
uv run uvicorn algo_weaver.api:create_app --factory --host 127.0.0.1 --port 8000
```

本地检查：

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

若需要在演示中使用真实模型，将 `ALGOWEAVER_LLM_MODE`、模型名称、
`ALGOWEAVER_LLM_API_KEY`、Embedding 和 Reranker 变量放入本机 `.env` 或当前
PowerShell 会话。`.env` 已被 Git 忽略，不能提交到仓库。

### 3.2 启动 Streamlit

在第二个窗口执行：

```powershell
$env:ALGOWEAVER_UI_API_BASE = "http://127.0.0.1:8000"
uv run streamlit run src/algo_weaver/ui.py `
  --server.address 127.0.0.1 `
  --server.port 8501
```

浏览器先打开 `http://127.0.0.1:8501`，确认页面能完成一次 mock/template
流程后，再启动隧道。

### 3.3 暴露临时 HTTPS 地址

安装 cloudflared（Quick Tunnel 无需登录），在第三个窗口执行：

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

命令会打印一次性的 `https://<随机值>.trycloudflare.com` 地址，把它发给导师。
API 仍然只在 `127.0.0.1:8000` 监听；Cloudflare 进程和两个应用进程必须持续运行。
演示结束后关闭隧道即可。也可以使用 `ngrok http 8501`，但两者都只适合短期演示。

如果要保护本机 API，将 API 改为：

```powershell
$env:ALGOWEAVER_API_AUTH_MODE = "api_key"
$env:ALGOWEAVER_API_KEY = "<随机长密钥>"
```

然后在 Streamlit 侧栏填入同一个密钥。当前页面通过 `X-API-Key` 发送；健康检查
`/health` 保持公开，便于进程和网关探活。

## 4. Streamlit Community Cloud 路线

Streamlit Community Cloud 适合托管展示页面，但它不能访问导师电脑上的
`127.0.0.1`。因此必须先把 FastAPI 部署到一个可访问的 HTTPS 地址（正式云服务、
受保护的 Cloudflare Tunnel 或其他托管 API），再将该地址配置为
`ALGOWEAVER_UI_API_BASE`。

部署时选择 GitHub 仓库、目标分支和入口文件：

```text
src/algo_weaver/ui.py
```

依赖使用项目的 `pyproject.toml`，并启用 `ui`、`api`、`retrieval` 等实际需要的
可选依赖。平台配置项只保存以下变量，不要把值写入代码：

```text
ALGOWEAVER_UI_API_BASE=https://<api-domain>
ALGOWEAVER_UI_API_KEY=<optional-api-key>
```

如果平台的 Secrets 以 TOML 文件提供而不是环境变量，应在部署设置中将这两个值
映射为环境变量，或者使用页面侧栏输入 API 地址和密钥。导师只需要访问平台生成的
`https://<app>.streamlit.app` 地址；FastAPI、Qdrant 和代码执行 runner 仍然属于
后端部署范围。

## 5. 正式 Docker + Qdrant + Caddy 部署

正式服务需要一台可以运行 Docker 的 Linux/WSL2 主机，以及一个指向该主机公网 IP
的 DNS 记录。生产 Compose 文件已经包含：

- `api`：FastAPI，容器内端口 8000，仅被 Caddy 访问；
- `qdrant`：Qdrant 1.20.0，使用命名卷保存索引，不直接发布端口；
- `caddy`：监听 80/443，负责 HTTPS 证书和反向代理。

在服务器执行：

```bash
cd algo-weaver/deploy/production
cp .env.production.example .env.production
# 编辑 .env.production，替换域名、API Key 和模型供应商密钥
docker compose up -d --build
docker compose ps
curl -fsS https://<your-domain>/health
```

DNS 和网络条件：

1. `A`/`AAAA` 记录指向服务器；
2. 入站 TCP 80、443 放行，80 用于 ACME HTTP-01 及重定向；
3. 不把 Qdrant 6333 或 Uvicorn 8000 暴露到公网；
4. 生产 API 开启 `ALGOWEAVER_API_AUTH_MODE=api_key`，并设置非空
   `ALGOWEAVER_API_KEY`；
5. 多副本部署时，在云网关配置共享限流，应用内限流只覆盖单个进程。

Caddy 会在域名和端口满足条件后自动申请并续期 ACME 证书。没有域名或公网服务器
时，不要声称已完成正式 HTTPS 部署；使用第三节的临时隧道即可完成导师演示。

生产环境的 `api` 容器不挂载宿主机 Docker socket。生成代码的执行必须交给单独的
WSL2/Docker runner，并设置超时、CPU、内存、文件和网络限制；不能因为部署方便而
让公网 API 获得宿主机 Docker 权限。

## 6. Secrets 与端口清单

| 变量或端口 | 用途 | 是否可提交 Git |
| --- | --- | --- |
| `ALGOWEAVER_LLM_API_KEY` | 主 Agent 和代码模型供应商密钥 | 否 |
| `ALGOWEAVER_EMBEDDING_API_KEY` | 向量模型密钥 | 否 |
| `ALGOWEAVER_RERANKER_API_KEY` | 重排模型密钥 | 否 |
| `ALGOWEAVER_API_KEY` | FastAPI 客户端认证密钥 | 否 |
| `8000` | FastAPI 内部监听端口 | 不直接公网开放 |
| `8501` | Streamlit 页面 | 仅通过隧道或平台域名提供 |
| `6333` | Qdrant HTTP API | 仅 Docker/本机内部 |
| `80/443` | Caddy 公网入口 | 仅生产服务器 |

不要提交 `.env`、`.env.production`、模型权重、Qdrant storage 或真实业务原始数据。
如果密钥曾经出现在聊天、截图或日志中，应在百炼平台轮换后再部署。

## 7. 导师五分钟验收脚本

1. 打开临时隧道或 Streamlit Cloud 地址，确认页面标题和状态信息正常；
2. 保持默认 `mock + template`，提交库存需求预测示例；
3. 查看能力卡片、检索证据、复刻计划、生成代码和验证报告；
4. 上传 `examples/inventory_forecast/sales_history.csv`，再次运行并检查来源关联；
5. 在本机或受控 runner 中勾选执行，确认超时、失败反馈和有限修复记录；
6. 查看 `reports` 中的 MAE/RMSE、执行状态和能力持久化结果；
7. 如配置了真实百炼模型，再切换 `litellm`，检查模型调用和失败边界，不把真实
   API 调用结果误当成离线 CI 结果。

最小 API 检查：

```powershell
curl.exe -fsS http://127.0.0.1:8000/health
curl.exe -X POST http://127.0.0.1:8000/metrics `
  -H "Content-Type: application/json" `
  -d '{"task":"inventory_demand","actual":[10,12,14],"predicted":[11,11,15],"max_mae":1.0,"max_rmse":1.0}'
```

## 8. 常见故障

- 页面提示连接 `127.0.0.1:8000` 失败：API 进程未启动，或 Streamlit 的
  `ALGOWEAVER_UI_API_BASE` 指向了错误地址。
- 返回 401：API 开启了 `api_key`，在侧栏填入与后端完全相同的密钥。
- 返回 429：触发了单进程限流；等待窗口结束，或在受控演示环境调整限额。
- 检索为空：先使用 mock/lexical 路径确认流程，再检查 Qdrant URL、Embedding
  模型、API Key 和集合初始化。
- 执行失败：确认 runner 已安装并运行；生产 API 容器不会直接访问宿主 Docker。
- ACME 失败：检查 DNS、80/443 防火墙、域名是否解析到当前服务器；临时演示改用
  Quick Tunnel，不要关闭认证或把 Qdrant 暴露到公网。

相关配置与接口实现见 [`docs/architecture/deployment.md`](../architecture/deployment.md)、
[`deploy/production/docker-compose.yml`](../../deploy/production/docker-compose.yml) 和
[`deploy/production/.env.production.example`](../../deploy/production/.env.production.example)。

官方操作文档：

- [Cloudflare Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
- [Streamlit Community Cloud 部署](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)
- [Streamlit Community Cloud Secrets](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [ngrok HTTP/S endpoints](https://ngrok.com/docs/gateway/endpoints/http)
