# 06 OpenHands Software Agent SDK

- 官方 SDK 仓库：https://github.com/OpenHands/software-agent-sdk
- 研究 SHA：`295b3baf71dfac1be028c5b187134ec3eb495346`（公开 HEAD，2026-11-06 查询）
- 相关核心路径：`openhands-sdk/openhands/sdk/`、`openhands-tools/openhands/tools/`、`openhands-workspace/openhands/workspace/`、`openhands-agent-server/openhands/agent_server/`。

## 解决的问题

OpenHands SDK 把软件 Agent 拆成 Agent、Tools、Workspace、Events、Agent Server 和 Session 生命周期。它强调可组合 Agent、模型无关路由、沙箱执行、事件流和会话恢复，适合作为 AlgoWeaver 代码工作区与安全边界的参考。

## 核心架构

- **Conversation/Agent**：维护一轮会话和 Agent 配置。
- **Events**：用类型化事件表达用户消息、动作、观察、状态更新和错误；事件流可投影成 LLM 消息，也可供 UI/审计消费。
- **Workspace**：抽象本地、Docker、远端或 Kubernetes 工作区；文件操作和命令执行通过 Workspace API。
- **Agent Server**：提供会话/事件 API、健康检查和实时流；客户端可以暂停、恢复和重新连接。
- **Sandbox**：容器/远程工作区执行不可信代码。CPU、内存、镜像、安全上下文、网络出口和持久卷由部署模板/策略控制。
- **Confirmation/Security Policy**：高风险工具调用可等待批准或经过策略检查。

## 执行流程

1. 创建 Conversation，绑定 Agent、Workspace 和模型配置。
2. 用户任务进入事件流。
3. Agent 生成动作事件（读文件、编辑、执行命令等）。
4. Workspace 在隔离环境执行，产出观察/错误事件。
5. Agent 根据观察继续循环；服务器持久化会话事件，客户端可流式展示。
6. 任务结束或暂停时保存状态；恢复时重新连接同一会话和工作区。

## AlgoWeaver 采用与拒绝

采用事件溯源思路，把 `plan/generated/command/test_result/repair/persist` 记录为可重放事件；采用 Workspace 接口隔离算法代码和输入资料，优先 Docker，后续再评估 Kubernetes；采用显式安全策略清洗 API Key、限制文件路径、资源配额和网络出口。

不直接引入完整 OpenHands SDK 作为 v0.1.0 依赖。其部署面和服务端组件较大，当前项目先定义最小 `SandboxRunner`/`Workspace` 协议，后续可提供 OpenHands 适配器。

## 风险与改进

沙箱并不自动保证安全：镜像、挂载、网络和凭证策略必须版本化并测试。每次执行都保存镜像摘要、命令、资源限制和退出码；禁止把宿主 `.env`、数据库密码或模型 Key 挂载给执行进程。暂停/恢复依赖稳定 session ID 和持久事件存储，不能只靠进程内状态。
