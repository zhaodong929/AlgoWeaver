# 阶段状态（2026-11-07）

状态枚举：`DONE`、`IN_PROGRESS`、`BLOCKED`、`NOT_STARTED`。

| Phase | 状态 | 当前证据 | 下一步 |
|---|---|---|---|
| Phase 0 基线、环境、依赖、Git | DONE | `uv.lock` 已生成；`uv sync --group dev --extra api --extra retrieval --extra execution` 成功；Windows 本地 106 passed/0 skipped，Linux 等价环境 105 passed/1 个平台专用 skip；Ruff/Mypy 通过；CI #78 的 Python 3.12/3.13 均通过 | 仅在环境变化时复核 |
| Phase 1 多格式文档解析与来源追踪 | IN_PROGRESS | `SourceIngestor` 支持 text/Markdown/Python/CSV/JSON/YAML；DOCX/PPTX/XLSX 有 Docling 优先和 stdlib fallback；`ingest_paths()` 保留混合来源的独立状态；PDF 仍需 Docling | 验证 PDF/复杂 Office 样例并保留来源布局 |
| Phase 2 历史代码结构化解析 | DONE | `PythonCodeParser`、`PythonSourceFile`、19 passed/2 skipped，提交 `f0c794e` | 接入检索和证据定位 |
| Phase 3 真实 LLM 抽取与证据校验 | IN_PROGRESS | `EvidenceRef` 已支持应用控制的行号和 SHA-256；真实 provider 未调用 | 用真实 provider 做一次可复现抽取并评估证据覆盖率 |
| Phase 4 RAG、混合检索、检索评估 | IN_PROGRESS | lexical retrieval、Recall@k/MRR/provenance coverage、score fusion 和 Qdrant in-memory vector adapter 已测试；graph/API 已聚合多源 chunks；embedding/reranker 未验证 | 接入真实 embedding/vector adapter并建立评估集 |
| Phase 5 LangGraph 算法复刻 Agent | IN_PROGRESS | `build_reproduction_graph()` 已实现 retrieve→plan→generate→validate，并支持注入 workspace/runner 的 artifact 写入与执行节点；生成节点支持 `ArtifactGenerator`，模板、Mock 和 Pydantic 校验的 LLM JSON 边界均有测试；真实 graph run 已完成 retrieve→plan→generate→write→execute→validate | 用真实 provider 完成一次可复现 planning/code generation 运行 |
| Phase 6 Docker 沙箱、自动测试、错误修复 | IN_PROGRESS | 图工作流可将 failed/timeout execution 条件路由到有界 `BoundedRepairLoop`；`LLMRepairer` 通过 Pydantic 校验 patch、限制已有 artifact 和 workspace、更新 hash，并已接入 CLI/API `repair_mode=llm`；人工审核库存能力通过 WSL2 Docker graph run，execution/runtime report 均为 passed | 用真实 provider 做一次修复反馈闭环并补充指标策略 |
| Phase 7 持久化、版本管理、复用 | IN_PROGRESS | `CapabilityRegistry` + CLI `reuse` + `reproduce --reuse-query` + API `reuse_query`/`auto_reuse` 只选择 verified capability 并返回版本信息；API `persist=true` 使用 configured SQLite 并复用 runtime/metric promotion gate；reviewed capability 已由 WSL runtime 晋升 verified | 连接语义检索结果、版本比较和相似度复用 workflow |
| Phase 8 API、展示界面、端到端集成 | IN_PROGRESS | FastAPI `/metrics` 和 `/reproduce` 已覆盖阈值评估、显式 sandbox、repair/repair_mode、persist、additional_sources、generation_mode、受限 sandbox metrics、verified reuse；18 个 API 测试通过；真实 WSL2 `/reproduce` 指标运行已通过；UI 未实现 | 接入指标与执行结果可视化 |
| Phase 9 最终验收、性能、文档、Demo | IN_PROGRESS | WSL sandbox runtime 和 reviewed capability verified promotion 已有真实证据；结构化生成/修复/API 指标、metric-aware promotion 和 verified reuse 边界已有 106 项本地测试；CI #77 的两个 Python 矩阵任务通过；`docs/reports/acceptance_matrix.md` 已逐项审计当前 Must-have | 补齐真实 provider 和语义相似度复用 |

## 当前 Git 证据

- Branch: `feat/api-capability-reuse`
- Remote tracking: pending push for this milestone
- Baseline commit: `04d74ac`; latest code milestone: `23b5470` (GPU/Docker audit; CI #78 verified)
- Latest feature commits: `f0c794e` (AST parser), `474dcb0` (document adapter boundaries/validation), `594e587` (retrieval), `0063c4c` (evidence/reproduction), `7a28841` (registry/sandbox), `aefb424` (repair), `19de267` (CLI demo), `3356695` (workflow/dependency analysis), `e7d061a` (API/lock/retrieval evaluation), `ebd8cbd` (Qdrant contract), `d81f30c` (verified-only reuse), `07394dc` (stdlib Office fallback), `2414981` (PDF fallback), `3bf54f2` (runtime promotion gate), `8ca8bf3` (runtime status update), `acf4329` (CI optional extras), `9b5b4cf` (WSL Docker runtime), `0669731` (executable reproduction graph), `cbc503b` (API sandbox execution), `ac79669` (API registry write-back), `118cd92` (API metrics), `c5dc718` (README refresh), `5db6d94` (multi-source reproduction inputs), `d76637c` (structured code generation boundary), `a7fb5c7` (CI WSL platform gate), `7967c2c`/`6a69261`/`057078b` (CI failure diagnostics), `7ce30f3`/`fdedf02`/`9ed4af0` (cross-platform CLI guard tests), `1c20d1c` (structured LLM repair boundary), `5532c16` (API sandbox metrics collection)
