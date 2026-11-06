# 03 smolagents

- 官方仓库：https://github.com/huggingface/smolagents
- 研究 SHA：`96f33faaf028479119ec8d34507b47694cf14e34`
- 核心文件：`src/smolagents/agents.py`、`src/smolagents/tools.py`、`src/smolagents/` 下的 Python Executor 与模型适配器。

## 解决的问题

smolagents 提供轻量的多步 Agent Loop，把工具描述、模型调用、动作解析、执行结果和记忆封装为少量可组合类。它同时支持结构化工具调用和生成 Python 代码两种动作表示。

## 关键类与接口

- `MultiStepAgent`：ReAct 循环基类，维护 System/Task/Action/Planning 步骤，支持 `max_steps`、回调和 managed agents。
- `ToolCallingAgent`：模型输出 JSON 工具调用；动作边界清晰，便于校验、审计和限制权限。
- `CodeAgent`：模型输出 Python 代码片段；通过 `PythonExecutor` 执行，可配置 `additional_authorized_imports`、`executor_type`、最大输出长度和自定义执行器。
- `Tool`/`BaseTool`：以名称、描述、输入 schema、输出类型和 `forward` 方法暴露工具；工具描述会注入系统提示。
- `PythonInterpreterTool`：供 ToolCallingAgent 显式调用的解释执行工具。
- `AGENT_REGISTRY`：反序列化时只允许登记过的 Agent 类，避免任意动态导入。

## 运行流程

1. Agent 将任务和历史记忆写入消息。
2. 模型生成 JSON 或代码动作。
3. 解析器把动作映射到工具/执行器。
4. 执行结果作为 observation 写回 `ActionStep`。
5. 回调记录、评估或修改步骤；达到 `final_answer` 或 `max_steps` 时结束。
6. 可周期性插入 planning step，重新组织剩余工作。

## 选择建议

算法复刻的“检索、读取文件、运行测试、读取日志”适合 ToolCallingAgent，因为工具参数需严格校验，且不应让模型任意生成文件系统代码。需要组合数组运算、临时数据处理或生成测试输入时，CodeAgent 更有表达力，但必须在独立沙箱中执行，禁止继承宿主凭证和网络权限。

## AlgoWeaver 采用与拒绝

采用工具描述中明确输入/输出类型、显式 `max_steps`、错误作为 observation、白名单反序列化和可替换执行器。先实现本地 `ToolCallingAgent` 风格的轻量接口，避免把完整 smolagents 作为运行时依赖。

不直接采用本地解释器执行不可信代码；AlgoWeaver 的代码验证走 Docker/隔离运行时。CodeAgent 生成的代码必须先经过静态检查和策略检查，再送入沙箱。

## 进一步改进

将每一次工具调用转为统一事件：工具名、参数摘要、输入证据、执行耗时、退出码和输出截断策略。对代码执行增加资源配额、超时、网络策略、只读输入挂载和敏感变量清洗。
