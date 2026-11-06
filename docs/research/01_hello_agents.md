# 01 Hello Agents

- 官方仓库：https://github.com/datawhalechina/hello-agents
- 研究 SHA：`36f583c233ea5cee4537ef93455702b55053af18`（公开 HEAD，2026-11-06 查询）
- 许可证/引入边界：本项目只记录设计，不复制教程代码；若复用代码需按仓库 LICENSE 单独核验。

## 解决的问题

Hello Agents 是从零构建智能体的系统教程，覆盖经典 Agent Loop、框架实践、记忆与检索、上下文工程、多智能体和评估。对 AlgoWeaver 的价值在于把“模型生成文本”拆成可观察的推理、行动、观察、反思与记忆步骤。

## 核心架构与代码位置

官方第七章给出的框架目录是：

- `hello_agents/core/agent.py`：Agent 基类和运行入口。
- `hello_agents/core/llm.py`：统一 LLM 接口。
- `hello_agents/core/message.py`、`config.py`、`exceptions.py`：消息、配置和错误边界。
- `hello_agents/agents/react_agent.py`：ReAct Agent。
- `hello_agents/agents/plan_solve_agent.py`：Plan-and-Solve Agent。
- `hello_agents/agents/reflection_agent.py`：Reflection Agent。
- `hello_agents/tools/`：工具注册和执行。

第四章原文路径为 `docs/chapter4/第四章 智能体经典范式构建.md`，第七章为 `docs/chapter7/第七章 构建你的Agent框架.md`。

## 关键原理与执行流程

1. **ReAct**：模型输出 Thought/Action；工具执行得到 Observation；Observation 回写上下文，循环到 Final Answer。适合需要外部证据、动态决策和反馈的任务。
2. **Plan-and-Solve**：先生成完整子任务计划，再逐步执行。适合结构已知、希望降低执行漂移的长任务。
3. **Reflection**：先产生结果，再让评估器检查缺陷，必要时生成改进结果。真正可用的反思应绑定外部执行结果、测试失败或证据缺失，而不是重复“你觉得好吗”。
4. **Memory/RAG**：把对话、工具结果和长期知识分层存储；检索结果要带来源，避免把模型猜测写成事实。
5. **Context Engineering**：控制历史、工具说明、证据和当前任务的组合，减少无关上下文。
6. **Evaluation**：从任务成功率、工具正确率、事实性、成本、延迟和失败恢复等维度评估 Agent，而不是只看最终文本。

## AlgoWeaver 采用与拒绝

采用：Plan-and-Solve 生成算法复刻计划；ReAct 执行检索、文件操作和测试；Reflection 由测试/静态检查结果驱动，输入必须包括错误日志和失败测试；Memory 保存能力卡片、验证报告和失败案例。

不直接采用：教学用的自然语言正则解析。生产模块使用 Pydantic 结构化输出和显式状态校验；不把自我评价当成验证证据。

## 可改进点

对 AlgoWeaver 增加 `Evidence -> Action -> Observation -> Verification` 事件类型，规定只有独立验证器才能把能力状态从 `Pending` 改为 `Verified`。为每一轮反思记录输入证据、修改文件和测试差异，支持复盘。
