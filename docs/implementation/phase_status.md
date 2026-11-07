# 阶段状态（2026-11-07）

状态枚举：`DONE`、`IN_PROGRESS`、`BLOCKED`、`NOT_STARTED`。

| Phase | 状态 | 当前证据 | 下一步 |
|---|---|---|---|
| Phase 0 基线、环境、依赖、Git | DONE | `uv.lock` 已生成；`uv sync --group dev --extra api --extra retrieval --extra execution` 成功；62 passed/0 skipped；Ruff/Mypy 通过；feature branch 已推送 | 仅在环境变化时复核 |
| Phase 1 多格式文档解析与来源追踪 | IN_PROGRESS | `SourceIngestor` 支持 text/Markdown/Python/CSV/JSON/YAML；DOCX/PPTX/XLSX 有 Docling 优先和 stdlib fallback；PDF 仍需 Docling | 验证 PDF/复杂 Office 样例并保留来源布局 |
| Phase 2 历史代码结构化解析 | DONE | `PythonCodeParser`、`PythonSourceFile`、19 passed/2 skipped，提交 `f0c794e` | 接入检索和证据定位 |
| Phase 3 真实 LLM 抽取与证据校验 | IN_PROGRESS | `EvidenceRef` 已支持应用控制的行号和 SHA-256；真实 provider 未调用 | 用真实 provider 做一次可复现抽取并评估证据覆盖率 |
| Phase 4 RAG、混合检索、检索评估 | IN_PROGRESS | lexical retrieval、Recall@k/MRR/provenance coverage、score fusion 和 Qdrant in-memory vector adapter 已测试；embedding/reranker 未验证 | 接入真实 embedding/vector adapter并建立评估集 |
| Phase 5 LangGraph 算法复刻 Agent | IN_PROGRESS | `ReproductionPlanner`、`TemplateArtifactWriter` 已生成 evidence-linked、unverified artifacts；尚无 LangGraph 复刻图 | 接入检索上下文、计划节点和 artifact state |
| Phase 6 Docker 沙箱、自动测试、错误修复 | IN_PROGRESS | WSL2 Docker runner 已真实执行 inventory unittest；runtime report、`BoundedRepairLoop` 和 offline `TemplateRepairer` 已测试，LLM repair/metrics 未验证 | 接入真实 provider repair 和性能指标 |
| Phase 7 持久化、版本管理、复用 | IN_PROGRESS | `CapabilityRegistry` 已提供 SQLite 版本追加、name search、passing-report promotion、verified-only reuse search 和 CLI reuse query；reviewed capability 已由 WSL runtime 晋升 verified | 连接检索结果、版本比较和自动复用 workflow |
| Phase 8 API、展示界面、端到端集成 | IN_PROGRESS | CLI `reproduce` 和可选 FastAPI `/health`, `/extract`, `/reproduce` 已测试；UI 未实现 | 接入 sandbox result、registry write-back 和可视化输出 |
| Phase 9 最终验收、性能、文档、Demo | IN_PROGRESS | WSL sandbox runtime 和 reviewed capability verified promotion 已有真实证据；`docs/reports/acceptance_matrix.md` 已逐项审计当前 Must-have | 补齐真实 provider、LLM repair 和性能指标 |

## 当前 Git 证据

- Branch: `feat/initial-audit-and-ingestion`
- Remote tracking: `origin/feat/initial-audit-and-ingestion`
- Baseline commit: `04d74ac`; latest code milestone: `86f39b3`
- Latest feature commits: `f0c794e` (AST parser), `474dcb0` (document adapter boundaries/validation), `594e587` (retrieval), `0063c4c` (evidence/reproduction), `7a28841` (registry/sandbox), `aefb424` (repair), `19de267` (CLI demo), `3356695` (workflow/dependency analysis), `e7d061a` (API/lock/retrieval evaluation), `ebd8cbd` (Qdrant contract), `d81f30c` (verified-only reuse), `07394dc` (stdlib Office fallback), `2414981` (PDF fallback), `3bf54f2` (runtime promotion gate), `8ca8bf3` (runtime status update), `acf4329` (CI optional extras), `9b5b4cf` (WSL Docker runtime)
