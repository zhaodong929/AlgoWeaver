# 需求追踪矩阵

来源为 `source_requirements.md` 中用户提供的笔试原文。状态按当前代码证据填写；“规划”不等于已实现。

| ID | 原始要求 | 功能分析 | 技术方案 | 实现模块 | 验收标准 | 测试 | 优先级 | 状态 |
|---|---|---|---|---|---|---|---|---|
| REQ-001 | 使用 LLM 完成理解、抽取、生成或修复 | 需要可替换模型接口 | ChatModel + LiteLLM + Mock | `llm/`, `services/` | 能调用真实/Mock 模型并校验输出 | 模型适配器、抽取测试 | P0 | 部分：抽取已实现，生成/修复未实现 |
| REQ-002 | 选择具体行业场景 | 需要一个可演示任务 | 库存需求预测场景，使用移动平均基线 | `examples/inventory_forecast/` | README 和示例材料说明业务输入、输出与验证指标 | CLI/demo tests | P0 | 部分：行业材料已提供，完整指标评估待实现 |
| REQ-003 | 小型能力知识库/知识图谱 | 表达能力、输入输出、条件、指标、依赖、验证历史 | Pydantic 能力卡片，后续 SQLite/图适配 | `schemas/capability.py` | JSON 能保存并重新校验 | schema 测试 | P0 | 部分：能力卡片已实现 |
| REQ-004 | 自然语言到可运行代码复刻 | 需要计划、检索、生成和文件工作区 | LangGraph 状态流 + 代码生成节点 | `agents/` | 端到端生成并执行示例 | 集成测试 | P0 | 未实现 |
| REQ-005 | 统一验证机制 | 检查功能、指标、稳定性、接口 | Pydantic validation report + AST/static checks；后续 pytest/Hypothesis/sandbox | `schemas/validation.py`, `services/validation.py` | 静态检查能生成通过/失败/跳过报告；运行时指标和隔离执行仍待实现 | `tests/test_validation.py` | P0 | 部分：静态/契约层已实现 |
| REQ-006 | CLI/API/UI | 用户提交能力描述并获取结果 | Typer CLI + optional FastAPI；后续 Streamlit | `cli.py`, `api.py` | CLI 和 API 可输出能力卡片、产物和报告；UI 待实现 | `tests/test_cli.py`, `tests/test_api.py` | P0 | 部分：CLI/API 已实现，UI 待实现 |
| REQ-007 | 理解用户描述 | 抽取结构化字段和缺失信息 | Pydantic + Mock/LLM | `CapabilityExtractor` | 不支持的内容不能伪造 | 抽取边界测试 | P0 | 已实现（抽取阶段） |
| REQ-008 | 检索文档、代码或图谱 | 返回带来源证据的相关知识 | `SourceChunker` + lexical retrieval + Recall@k/MRR/provenance evaluation；后续 hybrid/vector/rerank | `schemas/retrieval.py`, `services/retrieval.py` | 命中结果含来源、行号、metadata、score，评估指标可复现；真实语义检索待实现 | `tests/test_retrieval.py` | P0 | 部分：本地检索与评估已实现 |
| REQ-009 | 规划实现方案 | 输出步骤、依赖和验收策略 | `ReproductionPlanner` 生成结构化计划 | `schemas/reproduction.py`, `services/reproduction.py` | 计划含步骤、验收项和 evidence IDs；LangGraph 编排待实现 | `tests/test_reproduction.py` | P0 | 部分：模板规划已实现 |
| REQ-010 | 代码生成 | 生成可运行算法及测试、分析依赖 | `TemplateArtifactWriter` + `PythonDependencyAnalyzer`；后续接 LLM | `schemas/reproduction.py`, `services/reproduction.py`, `services/dependency.py` | 产物有 hash、dependency report 且明确 unverified；通用 LLM 生成和 workspace 待实现 | `tests/test_reproduction.py`, `tests/test_dependency.py` | P0 | 部分：确定性模板和静态依赖分析已实现 |
| REQ-011 | 执行测试与指标评估 | 运行生成代码并收集日志 | Docker-only runner + `ExecutionPolicy`；pytest/metrics later | `schemas/execution.py`, `services/sandbox.py` | 未安装/不可用 Docker 时明确 blocked；真实容器运行待验证 | `tests/test_sandbox.py` | P0 | 部分：隔离边界已实现，真实 daemon 未验证 |
| REQ-012 | 错误修复/优化 | 根据外部测试反馈迭代 | `BoundedRepairLoop` consumes `ExecutionResult` and enforces max attempts | `schemas/repair.py`, `services/repair.py` | 失败 observation 可追踪，达到上限或 blocked 时停止；LLM edit callback 待接入 | `tests/test_repair.py` | P1 | 部分：有界编排已实现 |
| REQ-013 | 验证结果回写 | 形成可复用能力资产 | SQLite capability versions + passing-report promotion | `schemas/registry.py`, `services/registry.py` | 版本可追加、搜索；只有 passing report 可标记 verified | `tests/test_registry.py` | P0 | 部分：持久化与 promotion 已实现 |
| REQ-014 | Git 与完整文档 | 支持复现和审阅 | Git、README、CHANGELOG、ADR | 项目根目录和 `docs/` | 文档与代码一致 | 文档检查 | P0 | 部分：文档已补齐，feature branch 已推送，尚未合并 main |
| REQ-015 | 示例材料、抽取结果、工作流、报告、依赖和测试 | 形成可展示交付包 | examples/data/docs/tests | 项目各目录 | README 命令可复现 | 全量回归 | P0 | 部分 |
| REQ-016 | 进阶：多轮修复、候选比较、可视化、配置和插件 | 提升展示完整性 | 后续按时间选择 | 后续模块 | 有独立验收证据 | 专项测试 | P1 | 未实现 |
| REQ-017 | 加分：图搜索、多 Agent、代码仓库抽取、沙箱等 | 形成创新与安全边界 | 采用研究笔记中的边界设计 | 后续模块 | 不影响主闭环 | 专项评测 | P2 | 未实现 |
| REQ-018 | 技术能力 40% / 代码质量 30% / 创新 15% / 完整 15% | 以端到端证据评估 | 报告与演示脚本 | `docs/reports/` | 每项有结果或明确缺口 | 验收清单 | P0 | 持续跟踪 |
