# AlgoWeaver

AlgoWeaver 是一个面向算法能力复用的 Python 原型系统。它把业务资料、历史代码和验证结果组织成可追溯的算法能力资产，并提供从能力描述到代码生成、验证和复用的工作流。

## 核心能力

- 资料接入：Markdown、文本、Python、CSV、JSON、YAML，以及可选的 Office/PDF 解析适配器。
- 能力抽取：Pydantic 能力卡片，记录输入、输出、步骤、参数、约束、指标、证据和状态。
- 证据检索：词法检索，可选 Qdrant 向量检索与重排，并保留来源定位。
- 方案规划：LangGraph 工作流将检索、规划、生成、验证和修复连接起来。
- 代码生成：模板、Mock 和可替换 LLM provider 三种模式。
- 安全验证：AST 检查、接口契约、单元测试、MAE/RMSE 指标和 Docker/WSL 隔离执行。
- 能力资产：SQLite 版本库、verified gate、JSON-LD 导出和结构化修复经验。
- 候选比较：库存预测支持 moving-average、naive-last、weighted-moving-average，并输出 JSON/Markdown 报告。
- 交互入口：Typer CLI、FastAPI 和 Streamlit 工作台。

## 目录

- `src/algo_weaver/`：核心服务、schema、Agent 图和 API/UI 入口。
- `examples/`：库存需求预测、异常检测和预测性维护示例。
- `tests/`：schema、服务、API、CLI、UI 和安全边界测试。
- `docs/architecture.md`：系统架构和模块说明。
- `docs/requirements/requirements_matrix.md`：需求与实现对应关系。
- `docs/reports/FINAL_DELIVERY_REPORT.md`：公开交付评估报告。
- [`docs/reports/algoweaver_delivery_report.pdf`](docs/reports/algoweaver_delivery_report.pdf)：可直接提交的 PDF 版本。

## 环境配置

需要 Python 3.12+ 和 uv：

```powershell
uv sync --group dev --extra api --extra retrieval --extra execution --extra ui
```

可选 provider 通过环境变量配置。不要把密钥写入仓库；`.env.example` 只包含变量名示例。

## 五分钟离线演示

```powershell
uv run algo-weaver extract examples/inventory_forecast/source.md --source-id inventory-doc
uv run algo-weaver reproduce examples/inventory_forecast/source.md --mode mock --generation-mode template
uv run algo-weaver compare --metrics-file examples/inventory_forecast/sales_history.csv
```

候选比较也可以通过 API 调用：

```powershell
$body = '{"actual":[18,21,20,24,22],"window":3,"selection_metric":"mae"}'
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/compare `
  -ContentType 'application/json' -Body $body
```

启动 API：

```powershell
uv run uvicorn algo_weaver.api:app --factory --host 127.0.0.1 --port 8000
```

启动工作台：

```powershell
uv run streamlit run src/algo_weaver/ui.py --server.headless true --server.port 8512
```

工作台提供任务描述、资料上传、模型/生成模式、候选比较、验证结果和能力资产展示。

## 测试与质量检查

```powershell
uv run pytest -q
uv run ruff check src tests
uv run mypy src --no-incremental
```

当前可复现结果：146 passed，1 skipped（Windows WSL 集成测试在无 WSL 环境下跳过）；Ruff 和 Mypy 通过。

## 技术选择

- Pydantic：约束模型输出和验证状态。
- LangGraph：表达可观察、可测试的算法复刻流程。
- SQLite + JSON-LD：低运维保存版本、证据和失败经验，并支持图数据导出。
- FastAPI、Typer、Streamlit：分别服务自动化调用、命令行复现和现场演示。
- Docker/WSL：为生成代码提供隔离执行边界。

## 当前边界

复杂 PDF/Office 布局、图谱可视化、插件注册、多轮修复、性能预算和正式公网部署仍需要进一步扩展。真实 provider、Docker/WSL 和外部向量服务必须在目标环境中单独复核。
