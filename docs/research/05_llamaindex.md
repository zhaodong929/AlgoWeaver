# 05 LlamaIndex

- 官方仓库：https://github.com/run-llama/llama_index
- 研究 SHA：`444fdf0684707de62ebb447d658dba137dd9cb99`
- 核心源码：`llama-index-core/llama_index/core/ingestion/pipeline.py`、`.../node_parser/`、`.../base_retriever/`、`.../vector_stores/`、`.../workflow/`。

## 解决的问题

LlamaIndex 把多源数据接入、解析、节点切分、元数据、Embedding、索引、向量存储、检索、Agent 和 Workflow 组织成可组合模块。它的优势是数据层与检索层抽象清晰，可替换具体 Reader、Embedding 和 Vector Store。

## 关键类与流程

- `IngestionPipeline`：接受 `Document`/`BaseNode`，依次应用 `TransformComponent`（如 `SentenceSplitter`、元数据抽取和 Embedding），可写入向量库和 docstore。
- `IngestionCache`：按输入节点和 transformation 哈希缓存，重复运行时复用结果。
- `DocstoreStrategy`：通过文档 hash 做 duplicates/upserts，输入不变时跳过，内容改变时重新处理并更新向量库。
- `VectorStoreIndex`/`BaseRetriever`：将节点与向量存储连接，返回节点及元数据来源。
- `llama_index.core.workflow.Workflow`、`Context`、`step`：事件驱动的异步工作流；step 可调用 LLM、检索、人工输入或派发批量任务。
- `FunctionAgent`/`AgentWorkflow`：在 Workflow 上组合函数工具和 Agent，但应按需引入。

## AlgoWeaver 采用与取舍

采用其数据模型思想：统一 `SourceDocument`、`EvidenceChunk`、`CodeSymbol` 和 `AlgorithmCapability`，每个块保存来源路径、页码/行号、哈希、解析器版本和证据级别。采用“转换链 + 缓存 + 去重”以支持重复上传和增量索引。

第一版不强制引入整个 LlamaIndex 运行时，避免依赖树过大；先实现项目内稳定接口，后续可接 Qdrant、BM25、Embedding 和 reranker。LlamaIndex 的 Workflow 不与 LangGraph 主编排叠加，避免两套持久化/事件模型同时成为事实源。

## 重要工程风险

官方 IngestionPipeline 的部分持久化路径对 Windows 有注释限制；AlgoWeaver 应使用 pathlib 和独立的本地存储适配器验证 Windows 行为。检索结果必须包含原始证据和元数据过滤条件，不能只返回一段无来源文本。

## 改进建议

代码按函数/类边界切分，文档按标题和表格边界切分，实验报告按“设置/结果/结论/失败”切分；先做稀疏检索与元数据过滤，再按需启用 Dense/Reranker。建立 Recall@k、MRR、证据覆盖率和答案可追溯性评估集。
