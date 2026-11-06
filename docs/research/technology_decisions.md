# 技术研究决策输入

本文件记录开源研究对 AlgoWeaver 的设计影响；正式 ADR 位于 `docs/architecture/decisions/`，这里不替代 ADR。

| 领域 | 研究结论 | AlgoWeaver 初步决策 | 原因/边界 |
|---|---|---|---|
| 编排 | LangGraph 提供 StateGraph、条件路由、检查点、线程和中断 | 采用 LangGraph 或兼容的项目内状态协议，优先小范围集成 | 需要长任务恢复；不一次性引入 Deep Agents 全套 |
| Agent 动作 | smolagents 区分 JSON 工具调用和 Python 代码动作 | 默认 ToolCalling；代码执行只进沙箱 | 工具调用易审计，代码动作表达力强但风险高 |
| 代码闭环 | SWE-agent 的 ACI、lint 门禁、分页查看和测试反馈有效 | 实现受限 Workspace/ACI | 减少上下文噪声和宿主机风险 |
| 数据/检索 | LlamaIndex 的 Transformation、Cache、Docstore、Vector Store 可组合 | 先定义自有接口，采用其摄取/去重/缓存思想 | 避免早期依赖膨胀；保留后续 Qdrant 适配空间 |
| 安全执行 | OpenHands 使用事件、Workspace、Sandbox、Policy | 定义 SandboxRunner，默认 Docker/隔离运行时 | 用户代码不得在宿主机执行，凭证不进入沙箱 |
| 范式 | Hello Agents 的 ReAct/Plan-and-Solve/Reflection 各有适用范围 | Plan 统筹、ReAct 执行、外部测试驱动 Reflection | 与算法复刻生命周期一致 |
| 依赖策略 | 六个上游框架各自有较大依赖树 | 不把六套框架全部安装进产品 | 保持 Windows/uv 可复现、调试面可控 |

## 未决事项

- 需要在本地 CUDA/显存核验后决定 Embedding/Reranker 模型。
- 需要根据真实腾讯文档需求决定是否实现 UI、PostgreSQL 和远程沙箱。
- 需要在 Docker 可用性确认后选择本地 Docker runner 或仅提供受限 dry-run。
