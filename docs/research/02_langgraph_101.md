# 02 LangGraph 101

- 官方教程仓库：https://github.com/langchain-ai/langgraph-101
- 研究 SHA：`71e2a14fe0643e8b8878819d76b8b7e4d69f91ca`
- 配套核心源码：https://github.com/langchain-ai/langgraph （查询时公开 HEAD 由上游网页引用；本笔记以 API 文档和 101 仓库为准）

## 解决的问题

LangGraph 用显式状态图编排长时间运行、可恢复、可观测的 Agent。101 目录覆盖模型、工具、记忆、流式输出，201 目录进一步覆盖邮件 Agent、多 Agent、Deep Agents、技能和人工介入。

## 核心抽象与源码位置

- `langgraph.graph.StateGraph`（核心源码 `libs/langgraph/langgraph/graph/state.py`）：节点读取 `State`，返回部分状态更新；可用 reducer 合并并发更新。
- `START`、`END`、普通 Edge 和 Conditional Edge：定义入口、终点和路由。
- `langgraph.checkpoint`：在 super-step 边界保存 `StateSnapshot`；`thread_id` 是恢复和线程隔离的键。
- `notebooks/101/101_langchain_langgraph.ipynb`：基础 Agent、工具、记忆、流式执行。
- `notebooks/101/102_middleware.ipynb`：Middleware、HITL 和 guardrails。
- `notebooks/201/email_agent.ipynb`、`multi_agent.ipynb`、`deepagents.ipynb`：有状态工作流和子图模式。

## 执行流程

1. 以 TypedDict 或 Pydantic 定义状态。
2. 将解析、检索、计划、生成、执行、验证、修复等动作注册成节点。
3. 用 Edge/Conditional Edge 连接节点；验证失败可回到修复节点，超过上限转到失败终点。
4. `compile(checkpointer=...)` 生成可执行图；调用时传 `configurable.thread_id`。
5. 通过 `invoke`、`stream` 或异步 API 运行；每个 super-step 写入检查点，可从中断处恢复。
6. 对写文件、执行代码等副作用设置任务边界或中间件；需要人工批准时调用 interrupt，恢复时提交 `Command(resume=...)`。

## 对 AlgoWeaver 的设计价值

建议使用一张主图管理任务生命周期：`ingest -> extract -> retrieve -> plan -> generate -> execute -> verify -> repair? -> persist`。将每个阶段的输入、证据、产物和状态放在 Pydantic 状态中；修复循环通过条件边限制最大次数。长期能力卡片放在外部数据库，线程检查点只保存当前任务状态。

## 取舍

采用 StateGraph、Conditional Edge、Checkpoint、Thread、Subgraph 和 Streaming；这些直接对应“长任务可恢复”和“博士展示可解释”。暂不引入 Deep Agents 的全部后端/技能层，避免在 v0.1.0 阶段引入不必要的抽象。HITL 只用于高风险写入、网络访问或能力升级审批。

## 风险与改进

检查点只在节点或 super-step 边界生效；副作用必须幂等或放在可恢复任务中。生产部署不能依赖内存 Checkpointer，应使用 PostgreSQL 等持久实现，并保证 UI 能根据 thread_id 恢复待处理的中断。
