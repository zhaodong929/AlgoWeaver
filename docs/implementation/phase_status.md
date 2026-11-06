# 阶段状态（2026-11-06）

状态枚举：`DONE`、`IN_PROGRESS`、`BLOCKED`、`NOT_STARTED`。

| Phase | 状态 | 当前证据 | 下一步 |
|---|---|---|---|
| Phase 0 基线、环境、依赖、Git | DONE | `docs/architecture/v0.1.0_audit.md`；14 passed/2 skipped；Ruff/Mypy 通过；feature branch 已推送 | 仅在环境变化时复核 |
| Phase 1 多格式文档解析与来源追踪 | IN_PROGRESS | `SourceIngestor` 支持 text/Markdown/Python/CSV/JSON/YAML，PDF/DOCX/PPTX/XLSX 有懒加载 Docling 边界；实际 Docling 解析未在本环境验证 | 安装/验证 documents extra 后完成真实样例 |
| Phase 2 历史代码结构化解析 | DONE | `PythonCodeParser`、`PythonSourceFile`、19 passed/2 skipped，提交 `f0c794e` | 接入检索和证据定位 |
| Phase 3 真实 LLM 抽取与证据校验 | IN_PROGRESS | `EvidenceRef` 已支持应用控制的行号和 SHA-256；真实 provider 未调用 | 用真实 provider 做一次可复现抽取并评估证据覆盖率 |
| Phase 4 RAG、混合检索、检索评估 | IN_PROGRESS | `SourceChunker`/`LocalLexicalRetriever` 已完成，27 passed/2 skipped；Qdrant/embedding/reranker 尚未接入 | 评估 hybrid/vector adapter 和 Recall@k/MRR |
| Phase 5 LangGraph 算法复刻 Agent | IN_PROGRESS | `ReproductionPlanner`、`TemplateArtifactWriter` 已生成 evidence-linked、unverified artifacts；尚无 LangGraph 复刻图 | 接入检索上下文、计划节点和 artifact state |
| Phase 6 Docker 沙箱、自动测试、错误修复 | IN_PROGRESS | `ValidationService` + Docker-only `DockerSandboxRunner` + `BoundedRepairLoop` 已测试；真实 daemon、pytest runtime 和 LLM repair 未验证 | 接入隔离运行报告、故障反馈和有限修复 |
| Phase 7 持久化、版本管理、复用 | IN_PROGRESS | `CapabilityRegistry` 已提供 SQLite 版本追加、name search 和 passing-report promotion；尚未接入完整复用流程 | 连接检索结果、版本比较和 CLI/API |
| Phase 8 API、展示界面、端到端集成 | NOT_STARTED | 只有 CLI 抽取 | 选择 CLI-first，再补 API/UI |
| Phase 9 最终验收、性能、文档、Demo | NOT_STARTED | 无完整闭环证据 | 汇总需求矩阵并运行完整验收 |

## 当前 Git 证据

- Branch: `feat/initial-audit-and-ingestion`
- Remote tracking: `origin/feat/initial-audit-and-ingestion`
- Baseline commit: `04d74ac`; latest code milestone: `f0c794e`
- Latest feature commits: `f0c794e` (AST parser), `474dcb0` (document adapter boundaries, validation, execution controls)
