# ADR-006：先使用可审计 JSON，再扩展 SQLite/PostgreSQL

- 状态：Proposed
- 日期：2026-11-06

当前能力卡片以 Pydantic JSON 保存，便于演示、diff 和复现。能力版本、验证报告和检索索引稳定后，再选择 SQLite 或 PostgreSQL；不提前引入数据库服务运维成本。
