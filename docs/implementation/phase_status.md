# 阶段状态（2026-11-08）

状态枚举：`DONE`、`IN_PROGRESS`、`BLOCKED`、`NOT_STARTED`。

| Phase | 状态 | 当前证据 | 下一步 |
|---|---|---|---|
| Phase 0 基线、环境、依赖、Git | DONE | `uv.lock` 已生成；`uv sync --group dev --extra api --extra retrieval --extra execution` 成功；Windows 本地 106 passed/0 skipped，Linux 等价环境 105 passed/1 个平台专用 skip；Ruff/Mypy 通过；CI #79 的 Python 3.12/3.13 均通过 | 仅在环境变化时复核 |
| Phase 1 多格式文档解析与来源追踪 | IN_PROGRESS | `SourceIngestor` 支持 text/Markdown/Python/CSV/JSON/YAML；DOCX/PPTX/XLSX 有 Docling 优先和 stdlib fallback；`ingest_paths()` 保留混合来源的独立状态；PDF 仍需 Docling | 验证 PDF/复杂 Office 样例并保留来源布局 |
| Phase 2 历史代码结构化解析 | DONE | `PythonCodeParser`、`PythonSourceFile`、19 passed/2 skipped，提交 `f0c794e` | 接入检索和证据定位 |
| Phase 3 真实 LLM 抽取与证据校验 | DONE for live provider boundary | `qwen3.8-max-0902` 通过百炼 workspace OpenAI-compatible API 完成 JSON smoke test、CLI 抽取和 FastAPI `/reproduce`；`deepseek-v4.1-flash-1017` 通过同一 API 完成 JSON smoke test 和代码生成；证据仍由应用侧控制 | 继续评估真实业务资料的抽取覆盖率 |
| Phase 4 RAG、混合检索、检索评估 | DONE for persistent service boundary; IN_PROGRESS for evaluation breadth | `HybridRetriever` 已接入 LangGraph、CLI 和 FastAPI；真实 embedding、Qdrant 1.20.0 server 命名卷重启持久化、词法融合和 rerank 均已通过 | 扩充 Recall@k/MRR 评估集，补充复杂文档检索样本 |
| Phase 5 LangGraph 算法复刻 Agent | DONE for live generation/repair boundary; PARTIAL for promotion | `build_reproduction_graph()` 已实现 retrieve→plan→generate→validate；Qwen/DeepSeek live bundle 在 WSL2 Docker 中先暴露 pytest 依赖失败，再由 DeepSeek 修复并通过 8 个测试 | 完成 live bundle 的指标门禁和 verified promotion |
| Phase 6 Docker 沙箱、自动测试、错误修复 | DONE for controlled and representative live coverage; PARTIAL for breadth | 图工作流可将 failed/timeout execution 条件路由到有界 `BoundedRepairLoop`；真实 DeepSeek 已分别修复导入错误、缺少 pandas 依赖和超时循环 | 增加多轮修复、失败经验回写和更多依赖类别 |
| Phase 7 持久化、版本管理、复用 | IN_PROGRESS | `CapabilityRegistry` + CLI `reuse` + `reproduce --reuse-query` + API `reuse_query`/`auto_reuse` 只选择 verified capability 并返回版本信息；API `persist=true` 使用 configured SQLite 并复用 runtime/metric promotion gate；reviewed capability 已由 WSL runtime 晋升 verified | 连接语义检索结果、版本比较和相似度复用 workflow |
| Phase 8 API、展示界面、端到端集成 | IN_PROGRESS | FastAPI `/metrics`/`/reproduce` 已覆盖阈值评估、显式 sandbox、repair/repair_mode、persist、additional_sources、generation_mode、受限 sandbox metrics、verified reuse；FastAPI runtime smoke 返回 200；Streamlit 已通过 AppTest、`/_stcore/health` 和根页面 HTTP 200；API 已增加 API-key、进程级限流和 HTTPS 反向代理部署说明 | 完成浏览器人工验收、HTTPS 实例和多副本网关限流配置 |
| Phase 9 最终验收、性能、文档、Demo | IN_PROGRESS | WSL sandbox runtime、MAE/RMSE 指标、reviewed capability verified promotion 和 verified reuse 已有真实证据；库存报告保存于 `docs/reports/test_reports/2026-11-08-inventory-delivery.md`；AI4I 第二场景已加入；生产 Compose/Caddy bundle 已加入；本轮全量本地测试 129 passed | 完成 Docker Qdrant service smoke test 和真实 DNS/HTTPS 部署证据 |

## 当前 Git 证据

- Branch: `feat/api-capability-reuse`
- Remote tracking: clean and synchronized after `084894f`
- Baseline commit: `04d74ac`; latest code milestone: `23b5470` (GPU/Docker audit; CI #79 verified)
- Latest feature commits include `084894f` (scenario performance report), `ad58fbc` (live LLM reproduction/repair), `e8e2c6f` (acceptance matrix), `7c4d319` (production HTTPS bundle), `9fa012a` (local persistent Qdrant), `8ac0ffd` (live repair evidence), `dcb64da` (open-license second scenario), `fa17dea` (delivery audit evidence), `16919d0` (provider-default test isolation), `b17206f` (production boundaries), `3705a66`/`47d3dfb` (hybrid retrieval and Streamlit), plus the earlier implementation milestones listed above.
