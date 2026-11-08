# Qdrant persistence verification

**Date:** 2026-11-08 (Asia/Shanghai)  
**Status:** `PASSED` for the WSL Docker service and AlgoWeaver server adapter

## Service

WSL2 exposes Docker Engine 29.1.3. The service uses image
`qdrant/qdrant:v1.20.0` and the named volume `qdrant_qdrant_storage`. The readiness
probe returned:

```text
all shards are ready
```

The container publishes `0.0.0.0:6333->6333`. On this Windows installation the
stable client route is the WSL address from `hostname -I` (`172.29.210.79` during
this run), because localhost forwarding was intermittent.

## Write, restart, and read

Using AlgoWeaver's `QdrantVectorRetriever` with
`ALGOWEAVER_QDRANT_MODE=server`, the smoke test created collection
`algo_weaver_p0_1_smoke`, wrote two provenance-preserving chunks, and returned:

```json
{"ready": true, "top_hit": "p0-1-inventory", "count": 2}
```

The container was restarted while retaining the named volume. A second Windows
client then searched the same collection and returned:

```json
{"after_restart": true, "top_hit": "p0-1-inventory", "count": 2}
```

## Hybrid retrieval

The real hybrid path used `qwen3.7-text-embedding-flash`, the persistent Qdrant
server and `qwen3-rerank`. It returned `hybrid-inventory` first with score
`0.8839408239352218`, followed by `hybrid-anomaly` with score
`0.21865348132538215`.

This closes the P0-1 service persistence gate. The Qdrant image, named volume and
WSL-IP connection procedure are now reflected in the deployment files and architecture
documentation.
