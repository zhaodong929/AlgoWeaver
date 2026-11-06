# ADR-001：Agent 编排采用 LangGraph 兼容状态流

- 状态：Accepted for the planned workflow
- 日期：2026-11-06

## Context

复刻任务需要状态、条件路由、循环修复、检查点和可恢复线程。

## Decision

使用 LangGraph 作为可选编排依赖；领域状态由项目内 TypedDict/Pydantic 定义。核心 CLI 在 LangGraph 缺失时保留一个最小离线运行器，避免 mock 演示被可选依赖阻断。

## Consequences

可使用 checkpoint/HITL/streaming；需要固定版本并为图节点编写集成测试。离线 fallback 不提供持久化能力。
