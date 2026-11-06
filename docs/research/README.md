# AlgoWeaver 开源项目研究索引

本目录记录截至 2026-11-06 对六个官方开源项目的源码与文档研究。研究仓库采用 `git ls-remote <url> HEAD` 获取的公开 HEAD SHA，未将上游完整源码加入 AlgoWeaver。

| 编号 | 项目 | 研究版本（HEAD SHA） | 主要借鉴点 |
|---|---|---|---|
| 01 | Hello Agents | `36f583c233ea5cee4537ef93455702b55053af18` | ReAct、Plan-and-Solve、Reflection、Memory/RAG、上下文工程、评估 |
| 02 | LangGraph 101 | `71e2a14fe0643e8b8878819d76b8b7e4d69f91ca` | 状态图、条件路由、循环、检查点、线程、HITL、子图 |
| 03 | smolagents | `96f33faaf028479119ec8d34507b47694cf14e34` | CodeAgent 与 ToolCallingAgent、Python 执行器、工具描述、多步循环 |
| 04 | SWE-agent | `3ea751c087f32b16e039a2233dd6eefecef325d5` | ACI、仓库探索、受限编辑、语法门禁、测试反馈修复 |
| 05 | LlamaIndex | `444fdf0684707de62ebb447d658dba137dd9cb99` | 摄取流水线、转换缓存、去重、向量存储、检索与 Workflows |
| 06 | OpenHands Software Agent SDK | `fc9f801f0ef8fe4486efcbce6d24310571e73daa` | 事件流、Workspace、沙箱、安全策略、会话暂停/恢复 |

## 研究边界

- 重点查看官方 README、官方文档及核心源码路径；没有把搜索摘要当作实现证据。
- 当前环境对部分 GitHub clone 存在连接超时，因此以可访问的官方网页源码、文档和 `git ls-remote` 的 SHA 为主；无法本地运行上游示例的地方在各笔记中标注。
- 研究结论用于 AlgoWeaver 的设计决策，不代表直接复制上游实现。许可证、版权和依赖兼容性在引入代码前必须单独复核。

## 阅读顺序

建议先读 `architecture_comparison.md` 和 `reusable_patterns.md`，再按模块阅读六份项目笔记，最后查看 `technology_decisions.md`。
