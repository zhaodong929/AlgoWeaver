# AlgoWeaver 项目交付评估

## 项目定位

AlgoWeaver 是一个算法能力工厂原型，目标是将业务资料转化为结构化能力资产，再通过可验证的代码生成流程形成可复用算法。

## 已实现功能

1. 能力抽取与 Pydantic schema 校验。
2. 来源追踪、词法检索和可选向量检索。
3. LangGraph 规划、代码生成、验证和有限修复流程。
4. 库存预测、异常检测、预测性维护示例。
5. FastAPI、Typer 和 Streamlit 三种使用入口。
6. SQLite 能力版本库、verified gate、JSON-LD 导出。
7. 库存预测候选算法比较和 MAE/RMSE 报告。
8. 结构化修复经验保存与查询。

## 质量证据

- pytest：146 passed，1 skipped（WSL 集成环境不可用时跳过）。
- Ruff：通过。
- Mypy：通过。
- API：包含健康检查、能力抽取、指标评估、候选比较和复刻接口。
- UI：包含任务工作台、执行记录、能力资产、系统设置和候选比较入口。

## 运行方式

```powershell
uv sync --group dev --extra api --extra retrieval --extra execution --extra ui
uv run pytest -q
uv run streamlit run src/algo_weaver/ui.py --server.headless true --server.port 8512
```

## 技术方案

系统使用 Pydantic 约束结构化数据，使用 LangGraph 编排流程，使用 SQLite 保存能力版本和验证状态，使用 FastAPI、Typer 和 Streamlit 提供不同交互入口。生成代码只有在独立验证通过后才能进入 verified 状态。

## 交付边界

当前版本适合作为可运行原型和演示项目。复杂文档解析、图谱可视化、插件化扩展、多轮修复、性能预算和正式公网部署仍属于后续增强方向。
