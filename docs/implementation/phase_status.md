# 阶段状态（2026-11-06）

状态枚举：`DONE`、`IN_PROGRESS`、`BLOCKED`、`NOT_STARTED`。

| Phase | 状态 | 当前证据 | 下一步 |
|---|---|---|---|
| Phase 0 基线、环境、依赖、Git | DONE | `docs/architecture/v0.1.0_audit.md`；14 passed/2 skipped；Ruff/Mypy 通过；feature branch 已推送 | 仅在环境变化时复核 |
| Phase 1 多格式文档解析与来源追踪 | IN_PROGRESS | `SourceIngestor` 支持 text/Markdown/Python/CSV/JSON/YAML，含 SHA-256 和 unsupported 边界 | 完善可选格式适配边界与统一 metadata |
| Phase 2 历史代码结构化解析 | DONE | `PythonCodeParser`、`PythonSourceFile`、19 passed/2 skipped，提交 `f0c794e` | 接入检索和证据定位 |
| Phase 3 真实 LLM 抽取与证据校验 | IN_PROGRESS | Mock/LiteLLM 抽取切片已存在；真实 provider 未调用 | 将 source location 细化到 chunk/行号 |
| Phase 4 RAG、混合检索、检索评估 | NOT_STARTED | 只有研究笔记和 ADR | 先实现本地 lexical retrieval 接口 |
| Phase 5 LangGraph 算法复刻 Agent | NOT_STARTED | 只有 extraction graph | 定义 reproduction plan 与 artifact 状态 |
| Phase 6 Docker 沙箱、自动测试、错误修复 | IN_PROGRESS | `ValidationService` 已提供静态/契约报告；尚无沙箱和运行时测试 | 接入隔离 runner、超时和资源限制 |
| Phase 7 持久化、版本管理、复用 | NOT_STARTED | 当前只写 JSON 文件 | 设计 verified-only promotion 和版本 schema |
| Phase 8 API、展示界面、端到端集成 | NOT_STARTED | 只有 CLI 抽取 | 选择 CLI-first，再补 API/UI |
| Phase 9 最终验收、性能、文档、Demo | NOT_STARTED | 无完整闭环证据 | 汇总需求矩阵并运行完整验收 |

## 当前 Git 证据

- Branch: `feat/initial-audit-and-ingestion`
- Remote tracking: `origin/feat/initial-audit-and-ingestion`
- Baseline commit: `04d74ac`; latest code milestone: `f0c794e`
- `ALGO_WEAVER_GOAL.md`、执行计划和本状态文件属于当前继续开发的未提交工作，待本轮文档与代码变更一起形成新的 feature commit。
