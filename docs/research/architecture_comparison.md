# 横向比较

| 维度 | Hello Agents | LangGraph 101 | smolagents | SWE-agent | LlamaIndex | OpenHands SDK |
|---|---|---|---|---|---|---|
| 主要问题 | Agent 原理教学 | 有状态工作流 | 轻量多步 Agent | 软件工程 Agent | 数据/检索管线 | 生产软件 Agent 运行时 |
| 核心单位 | Agent Loop | StateGraph 节点/边 | MultiStepAgent/Tool | ACI 工具 | Document/Node/Pipeline | Event/Workspace/Session |
| 反馈来源 | 工具 Observation | 节点输出/条件边 | 工具结果/异常 | lint、测试、命令输出 | 检索节点和元数据 | Workspace Observation/Event |
| 持久化 | 教学级 Memory | Checkpointer/Store | Agent memory | 轨迹/日志 | docstore/cache/vector store | 会话事件/工作区 |
| 安全边界 | 未重点实现 | 中间件/HITL | Executor 可替换 | 受控 ACI | 数据访问抽象 | Sandbox/Policy/Workspace |
| 适合 AlgoWeaver 的部分 | 范式选择、反思原则 | 主流程编排和恢复 | 工具接口与动作表示 | 代码探索、编辑、测试闭环 | 解析、切分、索引、检索 | 隔离执行和事件审计 |
| 不宜直接引入 | 教学代码 | 全部 Deep Agents | 不受控本地执行 | 特化的 SWE CLI | 全量运行时依赖 | 全套服务端部署 |

## 结论

AlgoWeaver 需要组合设计：LangGraph 负责主状态机和恢复；项目内 Pydantic 协议负责能力对象；LlamaIndex 的摄取/缓存思想指导 RAG；SWE-agent 的 ACI 指导代码复刻；OpenHands 的 Workspace/事件/沙箱指导安全执行；Hello Agents 和 smolagents 指导 Agent Loop、结构化工具调用和测试反馈反思。
