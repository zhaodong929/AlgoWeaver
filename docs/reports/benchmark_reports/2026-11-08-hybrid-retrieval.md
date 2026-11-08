# Hybrid retrieval evaluation

**Date:** 2026-11-08 (Asia/Shanghai)  
**Providers:** `qwen3.7-text-embedding-flash`, Qdrant 1.20.0 server, `qwen3-rerank`

Four provenance-preserving chunks were indexed and evaluated with four queries:

| Query | Top-2 IDs | Recall@2 | Reciprocal rank |
|---|---|---:|---:|
| inventory demand | inventory, retrieval | 1.0 | 1.0 |
| sensor anomaly | anomaly, retrieval | 1.0 | 1.0 |
| moving average replenishment | inventory, retrieval | 1.0 | 1.0 |
| docker sandbox timeout | sandbox, retrieval | 1.0 | 1.0 |

Mean Recall@2 was `1.0` and MRR was `1.0` on this small smoke set. This is a
connectivity and provenance evaluation, not a claim about production-scale retrieval
quality; a larger benchmark remains necessary.
