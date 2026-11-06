# 测试策略

- Schema：正常、空值、非法额外字段和状态迁移。
- Ingestion：支持格式、CSV 行数、空文件、缺失路径和不支持扩展名。
- LLM：Mock 适配器做确定性测试；真实 Provider 单独标记并不作为离线通过证据。
- Workflow：图节点成功、异常和有界重试。
- Reproduction：静态语法、导入、接口、功能、指标、稳定性和资源限制。
- Regression：每个可验收模块运行 `pytest -q` 与 `ruff check src tests`。
