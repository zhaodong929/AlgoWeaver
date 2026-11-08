# AlgoWeaver — Autonomous Engineering Goal

你现在是 AlgoWeaver 项目的首席 AI Agent 架构师、资深 Python 工程师、技术负责人和测试负责人。

你的唯一长期目标是：

**基于现有 AlgoWeaver v0.1.0，完成一个满足浙江大学博士考核要求的、真正可运行的算法能力智能体系统（Algorithm Intelligence & Reproduction Agent）。**

这不是一个单次代码生成任务，而是一个需要持续研究、设计、实现、测试、修复和迭代的长期工程任务。

请将项目根目录中的以下文件作为最高优先级的项目依据：

- AGENTS.md
- docs/PROJECT_MASTER_PLAN.md
- docs/requirements/source_requirements.md
- docs/requirements/requirements_matrix.md
- docs/research/
- docs/architecture/
- docs/architecture/decisions/
- docs/implementation/

如果部分文件尚不存在，先检查现有项目，不要假设它们已经完成。

## 一、项目基线

GitHub：

[https://github.com/zhaodong929/AlgoWeaver](https://github.com/zhaodong929/AlgoWeaver)

已知第一轮分支：

feat/initial-audit-and-ingestion

已知第一轮提交：

04d74ac

已完成第一轮工程审计、需求整理、六个开源项目研究、基础架构、六个 ADR，以及文本、Markdown、Python、CSV、JSON、YAML 接入和 Mock 能力抽取。

第一轮测试报告为 14 passed、2 skipped，Ruff 和 Mypy 通过。

以上是已知基线，必须重新核验实际代码、Git 状态和测试结果。

不得推翻现有工程，不得丢失已有成果。

## 二、最终功能目标

围绕真实考核需求，完成以下系统能力：

1. 多源文档及历史代码接入。
2. 算法知识自动抽取。
3. 标准化算法能力卡片。
4. 带有原始证据和来源定位的 RAG 知识检索。
5. 多模型兼容的算法复刻 Agent。
6. 自动代码生成与依赖分析。
7. 安全隔离的代码执行环境。
8. 自动测试、错误分析和有限次数修复。
9. 算法能力版本管理和持久化。
10. 历史算法能力检索与复用。
11. 完整端到端 Demo 和可复现运行文档。

## 三、技术原则

优先研究和采用：

- LangGraph：主要 Agent 工作流。
- LiteLLM：多模型适配。
- Pydantic：结构化能力表示。
- Docling：多格式文档解析。
- Python AST / Tree-sitter：代码结构化解析。
- Qdrant / Hybrid Search：知识检索。
- Embedding / Reranker：语义检索与重排。
- Docker：代码执行沙箱。
- pytest / Hypothesis：自动验证。
- SQLite / PostgreSQL：结构化持久化。
- FastAPI / Streamlit：系统展示。

这些是候选方案，不是强制技术清单。应结合已有 ADR、实际需求、兼容性和成本作出选择。

避免无必要的框架堆叠、重复实现和大规模重构。

## 四、持续自主执行规则

不要把项目拆成需要我每次重新发送提示词的独立任务。

你需要自主完成以下循环：

1. 读取当前项目状态。
2. 识别最高优先级的未完成需求。
3. 研究必要的官方文档和源码。
4. 制定具体实现方案。
5. 修改代码。
6. 运行测试。
7. 根据错误修复代码。
8. 更新文档和进度。
9. 完成当前里程碑后自动进入下一个里程碑。

**每个里程碑通过后，直接继续下一个可执行任务，不要等待我回复“继续”。**

如果某个模块遇到阻塞，先完成其他不依赖该模块的工作，不要因此停止整个项目。

只有遇到必须由我提供的 API Key、不可绕过的权限审批、破坏性操作、付费资源或无法自行确定的重大产品决策时，才暂停并明确说明原因。

对于一般技术选择，优先采用简单、安全、兼容的方案，记录 ADR 后继续执行。

## 五、开发路线

请根据需求矩阵和实际依赖关系动态安排：

Phase 0：工程基线、环境、依赖和 Git 核验。

Phase 1：多格式文档解析与来源追踪。

Phase 2：历史代码结构化解析。

Phase 3：真实 LLM 算法能力抽取和证据校验。

Phase 4：RAG、混合检索和检索评估。

Phase 5：LangGraph 算法复刻 Agent。

Phase 6：Docker 安全沙箱、自动测试和错误修复。

Phase 7：算法能力持久化、版本管理和复用。

Phase 8：API、展示界面和端到端集成。

Phase 9：完整需求验收、性能评估、文档和最终 Demo。

允许调整顺序，但必须说明依赖关系和理由。

不要只完成计划或架构图。完成必要设计后必须继续实际编码。

## 六、持续进度管理

请建立或维护：

- docs/implementation/EXECUTION_PLAN.md
- docs/implementation/phase_status.md
- docs/implementation/build_log.md
- docs/implementation/known_issues.md

EXECUTION_PLAN.md 是长期执行计划。

phase_status.md 是唯一的开发状态记录，逐项标记 DONE、IN_PROGRESS、BLOCKED、NOT_STARTED。

build_log.md 记录每次实现、测试和修复。

known_issues.md 记录技术债务和待解决问题。

每次上下文压缩或恢复工作时，先读取这些文件，避免重复开发。

每完成一个里程碑：

- 更新任务状态。
- 保存技术决策。
- 记录实际测试命令及结果。
- 记录 Git Commit。
- 自动继续下一个可执行里程碑。

## 七、Git 安全规则

优先在独立 feature 分支开发。

允许创建分支、提交代码、推送功能分支。

禁止：

- git push --force。
- 删除远程分支。
- 覆盖 main。
- 重写已有提交历史。
- 未经确认合并 main。
- 删除用户未提交的修改。
- 提交 .env、API Key、模型权重和敏感数据。

开始前必须检查 git status、branch、log 和 remote。

如果当前状态与 04d74ac 不一致，先分析差异，不允许强制回退。

## 八、安全和环境约束

- 使用 Python 3.12 和 uv，优先保持现有依赖兼容。
- 检查本地 NVIDIA GPU 和 CUDA 环境。
- 不要未经确认下载大型模型权重。
- 不要将密钥传入不可信代码执行环境。
- 不允许在宿主机直接执行未经验证的生成代码。
- 沙箱必须有超时、资源和文件访问限制。
- 不允许无限自动修复循环。
- API 缺失时使用 Mock 完成其他可独立开发的功能。
- 不要虚构真实模型测试或集成测试结果。

## 九、最终验收标准

只有满足以下条件，才能宣布 AlgoWeaver MVP 完成：

1. 所有 Must-have 需求均有对应实现。
2. 所有功能都有可追踪的代码和测试。
3. 多源资料能够解析和建立来源关联。
4. 算法能力能够结构化抽取。
5. RAG 能够检索历史算法知识和代码。
6. Agent 能够完成算法复刻。
7. 生成代码在隔离环境执行。
8. 测试失败能够触发有限次数自动修复。
9. 验证通过的能力可以保存和再次复用。
10. 至少完成一个完整端到端演示。
11. 测试、静态检查和安全检查有真实记录。
12. README 和运行文档可以指导他人复现。

不允许将未实现、未测试或 Mock 的功能标记为真实完成。

## 十、执行要求

现在开始执行这个长期目标。

先核验项目基线，建立完整执行计划，然后立即开始第一个可执行的开发里程碑。

**不要在生成 EXECUTION_PLAN.md 后停止。不要在完成一个模块后等待我发送下一条指令。持续推进整个项目，直到所有验收条件满足，或出现必须由我处理的明确阻塞。**

最终交付完整源代码、测试报告、技术文档、GitHub 功能分支和可运行 Demo。

## 十一、笔试要求对照后的交付目标（v2）

本节是对 `docs/requirements/source_requirements.md` 笔试原文的可执行重述。
它不把“有接口”当作“完成”：每项目标都必须有代码位置、测试命令和可展示证据。

### 主验收场景

AlgoWeaver 以**库存需求预测**作为主行业场景。输入是按日期排列的商品日销量，
基线算法是固定窗口移动平均，输出滑动预测序列和下一周期补货基线，指标为逐元素
参考实现、MAE、RMSE、运行时间以及空序列/非法窗口/窗口过长等边界行为。
材料位于 `examples/inventory_forecast/`，包括业务说明、人工审核能力卡片和
`sales_history.csv`。该场景已经有模板生成、隔离执行、指标评估、能力持久化和
verified-only 复用证据，是当前可交付 Demo。真实 LLM 生成与修复另有明确标记，
不会被模板结果冒充。

### 必须交付的闭环

1. 输入业务文档、历史代码、实验记录和测试报告，并保存来源、哈希、位置和解析状态。
2. 抽取算法名称、原理、输入输出、预处理、步骤、参数、约束、指标、失败案例和依赖，
   形成 Pydantic 能力卡片；原始证据、模型推断、待确认和已验证信息必须分开。
3. 以词法检索为离线基线，以 `qwen3.7-text-embedding-flash`、Qdrant 和
   `qwen3-rerank` 形成可选的混合检索路径，并返回可定位证据。
4. 由 Agent 完成理解、检索、规划、代码/测试生成、依赖分析和结构化输出校验。
5. 生成代码只能在 Docker/WSL 隔离环境中执行，执行失败、导入错误、依赖错误和超时
   必须进入有最大次数的修复循环。
6. 统一输出功能、指标、稳定性、接口和安全检查结果；只有独立验证通过的能力才能
   写入 `verified`，并能按版本检索和复用。
7. 通过 CLI、FastAPI 和 Streamlit 提交任务并查看证据、计划、代码、执行结果、修复过程
   和能力卡片；线上部署必须有 API key、HTTPS 和限流配置。

### 连续执行规则

后续 Codex 运行必须先读取本文件、`requirements_matrix.md` 和
`DELIVERY_GAP_LIST.md`，选择优先级最高且未完成的一项，完成实现、测试、文档和
Git 记录后继续下一项。不得以“接口存在”“测试被跳过”或“Mock 返回成功”作为真实
完成依据。所有剩余事项以 `DELIVERY_GAP_LIST.md` 为唯一可执行清单；完成一项后更新
矩阵状态和证据链接。
