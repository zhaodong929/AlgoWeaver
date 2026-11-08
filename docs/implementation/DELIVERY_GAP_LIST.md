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
- `qwen3.7-text-embedding-flash` 向量、Qdrant 内存/服务模式、`qwen3-rerank` 重排；
- LangGraph 检索→规划→生成→验证图；
- Docker/WSL 隔离执行、指标报告、有限修复和 SQLite 能力版本库；
- `uv run pytest -q` 当前 125 passed，Ruff 和 Mypy 的 CI 检查已配置。

## 需求到实现对照

| ID | 笔试要求 | 当前状态 | 下一步验收证据 |
|---|---|---|---|
| G-01 | LLM 理解、抽取、生成或修复 | PARTIAL | 真实模型抽取/生成已验收；补充多份真实业务资料和真实多轮修复报告 |
| G-02 | 具体行业场景及数据 | DONE（主场景） | 运行 inventory demo，保存 MAE/RMSE/运行时间报告；增加公开第二场景 |
| G-03 | 能力知识库/知识图谱 schema | PARTIAL | Pydantic+SQLite 已有；补充能力、证据、依赖、验证历史的图导出/可视化 |
| G-04 | 自然语言到可运行代码 | PARTIAL | 模板、Mock、真实 LLM bundle 均可生成；补充真实 LLM 产物的隔离执行验收 |
| G-05 | 统一功能/指标/稳定性/接口验证 | PARTIAL | 现有静态、运行、MAE/RMSE；补充性能预算、接口契约和安全扫描报告 |
| G-06 | CLI/API/UI | PARTIAL | 三入口已实现；补充 Streamlit 浏览器人工验收记录和线上部署演示 |
| G-07a | 理解用户输入 | DONE（边界） | 增加缺失字段、冲突证据和低置信度抽取样本 |
| G-07b | 检索文档/代码/图谱 | PARTIAL | 词法+向量+重排已接入；运行持久化 Qdrant smoke test 并记录 Recall@k/MRR |
| G-07c | 规划方案 | PARTIAL | 规则规划稳定；补充真实 LLM 规划质量评估和候选方案比较 |
| G-07d | 生成代码和测试 | PARTIAL | 补充依赖安装策略、生成测试覆盖率和失败产物归档 |
| G-07e | 自动执行和指标 | PARTIAL | 主场景已通过；补充超时、资源限制、网络策略和第二指标任务 |
| G-07f | 错误分析和有限修复 | PARTIAL | 已覆盖导入/依赖/超时受控测试，真实模型仅有一个失败案例；补充三类 live repair 证据 |
| G-07g | 验证结果回写和复用 | PARTIAL | SQLite verified gate 已有；补充语义相似复用、版本 diff 和失败经验回写 |
| G-08 | Git、文档、依赖、测试和示例 | PARTIAL | feature 分支和 README 已有；补齐发布清单、Windows/Docker 复现记录 |
| G-09 | 进阶：多轮修复/比较/可视化/插件 | PARTIAL | 多轮修复和 UI 有基础；候选比较、图谱可视化、插件注册尚未完成 |
| G-10 | 加分：图搜索、多 Agent、仓库抽取、安全和性能 | PARTIAL | AST、沙箱、失败反馈已有；图搜索、多 Agent、仓库级抽取、性能分析待做 |

## 下一步执行顺序

1. **P0-1 持久化检索验收**：启动 `deploy/qdrant/docker-compose.yml`，运行 `/readyz`、
   API/CLI server-mode smoke test，并记录真实 collection 数据持久化。
2. **P0-2 主场景交付报告**：用 `sales_history.csv` 完成一次从材料接入到 verified
   复用的报告，包含代码、测试、MAE/RMSE、耗时和来源证据。
3. **P0-3 Streamlit 浏览器验收**：启动 FastAPI+Streamlit，执行上传、运行、查看证据、
   查看代码/报告、失败修复和复用操作，保存截图或录屏及复现步骤。
4. **P0-4 安全部署验收**：启用 API key、HTTPS 反向代理和网关限流，验证 401/429、
   `/health` 探针及敏感配置不进入沙箱。
5. **P1-1 真实失败修复扩展**：用真实代码模型分别验证导入错误、缺少依赖、超时，
   每类最多 2 次修复并保留初始/最终日志；不能用 Mock 结果替代。
6. **P1-2 能力资产增强**：导出 GraphML/JSON-LD 或等价图结构，加入版本 diff、失败
   经验和语义相似复用。
7. **P1-3 第二公开场景**：优先采用 UCI/开放许可的异常检测或文本分类数据，复用同一
   Agent/验证接口，形成跨场景证据。
8. **P2-1 展示增强**：候选算法比较、图谱可视化、资源消耗和性能报告、插件式指标。

任何真实 API、Docker、浏览器或公开数据未运行的项目，必须在报告中标为
`PARTIAL`，不能提前宣布 MVP 完成。
