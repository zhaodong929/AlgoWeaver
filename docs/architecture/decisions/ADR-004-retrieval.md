# ADR-004：检索先定义项目内接口，再接入 Qdrant

- 状态：Proposed
- 日期：2026-11-06

先稳定 chunk、metadata、evidence 和 retriever 接口，再评估 Qdrant 的 hybrid search 与本地 embedding/reranker。GPU 为 RTX 5070 Laptop、约 8 GiB；模型大小和 CUDA 轮子必须在实际 benchmark 后决定。
