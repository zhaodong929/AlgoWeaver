# AlgoWeaver 可交付差距清单

更新时间：2026-11-08（Asia/Shanghai）

状态含义：`DONE` 有代码、测试和可复现证据；`PARTIAL` 有可运行路径但仍缺少题目
要求的一部分证据；`TODO` 尚未完成；`BLOCKED` 需要外部权限、资源或用户决策。

## 当前可交付物

主场景是库存需求预测（固定窗口移动平均），材料在
`examples/inventory_forecast/`。当前仓库已有：

- CLI、FastAPI、Streamlit 三种入口；
- Mock 和百炼兼容的真实 LLM 边界；主模型 `qwen3.8-max-0902`，代码模型
  `deepseek-v4.1-flash-1017`；
- `qwen3.7-text-embedding-flash` 向量、Qdrant 内存/本地持久化/服务模式、`qwen3-rerank` 重排；
- LangGraph 检索→规划→生成→验证图；
- Docker/WSL 隔离执行、指标报告、有限修复和 SQLite 能力版本库；
- 第二个开放许可场景：UCI AI4I 2020 预测性维护，位于
  `examples/predictive_maintenance/`，包含归属说明、10,000 行 CSV、算法、测试和能力卡片；
- `uv run pytest -q` 当前 130 passed，Ruff 和 Mypy 的 CI 检查已配置。

## 需求到实现对照

| ID | 笔试要求 | 当前状态 | 下一步验收证据 |
|---|---|---|---|
| G-01 | LLM 理解、抽取、生成或修复 | PARTIAL | 真实模型抽取/生成已验收；补充多份真实业务资料和真实多轮修复报告 |
| G-02 | 具体行业场景及数据 | DONE（两个场景） | 将 AI4I 场景接入通用 Agent/API 指标接口 |
| G-03 | 能力知识库/知识图谱 schema | PARTIAL | Pydantic+SQLite 和 JSON-LD 导出已实现；补充图谱可视化和版本 diff |
| G-04 | 自然语言到可运行代码 | PARTIAL | 真实 LLM bundle 已在隔离环境执行；首次 pytest 依赖失败后由 DeepSeek 修复并通过 8 个测试；继续完成 live bundle 的指标门禁和 verified promotion |
| G-05 | 统一功能/指标/稳定性/接口验证 | PARTIAL | 现有静态、运行、MAE/RMSE；补充性能预算、接口契约和安全扫描报告 |
| G-06 | CLI/API/UI | PARTIAL | 三入口、AppTest 和 HTTP smoke 已实现；补充浏览器人工验收记录和线上部署演示 |
| G-07a | 理解用户输入 | DONE（边界） | 增加缺失字段、冲突证据和低置信度抽取样本 |
| G-07b | 检索文档/代码/图谱 | PARTIAL | Docker server persistence and real hybrid retrieval smoke 已通过；继续补充 Recall@k/MRR 评估集 |
| G-07c | 规划方案 | PARTIAL | 规则规划稳定；补充真实 LLM 规划质量评估和候选方案比较 |
| G-07d | 生成代码和测试 | PARTIAL | 补充依赖安装策略、生成测试覆盖率和失败产物归档 |
| G-07e | 自动执行和指标 | PARTIAL | 主场景已通过；补充超时、资源限制、网络策略和第二指标任务 |
| G-07f | 错误分析和有限修复 | PARTIAL | 三类真实 DeepSeek repair 各完成一次；继续补充多轮修复和失败经验回写 |
| G-07g | 验证结果回写和复用 | PARTIAL | SQLite verified gate 已有；补充语义相似复用、版本 diff 和失败经验回写 |
| G-08 | Git、文档、依赖、测试和示例 | PARTIAL | feature 分支和 README 已有；补齐发布清单、Windows/Docker 复现记录 |
| G-09 | 进阶：多轮修复/比较/可视化/插件 | PARTIAL | 多轮修复和 UI 有基础；候选比较、图谱可视化、插件注册尚未完成 |
| G-10 | 加分：图搜索、多 Agent、仓库抽取、安全和性能 | PARTIAL | AST、沙箱、失败反馈已有；图搜索、多 Agent、仓库级抽取、性能分析待做 |

## 下一步执行顺序

1. **P0-1 持久化检索验收**：已完成 WSL Docker Qdrant 1.20.0、命名卷、`/readyz`、
   Windows server-mode 写入/重启/检索，以及真实 embedding+reranker hybrid smoke；
   后续只需扩充 Recall@k/MRR 评估集。
2. **P0-2 主场景交付报告**：已完成 `sales_history.csv` 从材料接入到 verified
   复用的报告；后续只补充现场截图和发布打包记录。
3. **P0-3 Streamlit 浏览器验收**：启动 FastAPI+Streamlit，执行上传、运行、查看证据、
   查看代码/报告、失败修复和复用操作；自动 AppTest 和 HTTP smoke 已完成，仍需浏览器人工记录。
4. **P0-4 安全部署验收**：API key、应用限流、401/429 和 `/health` 已完成真实
   Uvicorn smoke；Caddy internal TLS 已完成本地 HTTPS smoke；仍需真实 DNS/ACME 证书和多副本网关验收。
5. **P1-1 真实失败修复扩展**：导入错误、缺少依赖、超时各已完成一次真实修复；
   继续验证多轮修复并保存失败经验。
6. **P1-2 能力资产增强**：JSON-LD 导出已实现（`algo-weaver export-graph`）；继续加入
   版本 diff、失败经验和语义相似复用。
7. **P1-3 第二公开场景**：已加入 UCI AI4I 2020 Predictive Maintenance Dataset
   （CC BY 4.0，DOI `10.24432/C5HS5C`）和透明规则基线，复用了相同的能力卡片和
   测试结构；下一步把该场景接入通用 Agent/API 指标接口并保留授权来源。
8. **P2-1 展示增强**：候选算法比较、图谱可视化、资源消耗和性能报告、插件式指标。

任何真实 API、Docker、浏览器或公开数据未运行的项目，必须在报告中标为
`PARTIAL`，不能提前宣布 MVP 完成。
