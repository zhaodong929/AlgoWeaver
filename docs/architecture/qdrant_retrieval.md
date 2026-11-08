# Qdrant vector adapter

`QdrantVectorRetriever` is an optional adapter over the existing `EvidenceChunk` and `RetrievalHit` schemas. It accepts externally supplied vectors, stores them in an in-memory or configured Qdrant service, and returns the original source ID, path and line range with every hit.

The default `ALGOWEAVER_QDRANT_MODE=memory` keeps tests and offline demos self-contained. For persistence, start `deploy/qdrant/docker-compose.yml`, set `ALGOWEAVER_QDRANT_MODE=server` and point `ALGOWEAVER_QDRANT_URL` at `http://127.0.0.1:6333`. The collection is created idempotently and data is stored under the Compose `storage` volume. Set `ALGOWEAVER_QDRANT_API_KEY` when the service is protected.

```powershell
cd deploy/qdrant
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

Then configure the application environment:

```powershell
$env:ALGOWEAVER_QDRANT_MODE = "server"
$env:ALGOWEAVER_QDRANT_URL = "http://127.0.0.1:6333"
```

The test suite uses Qdrant's local in-memory client and a mocked server constructor; it validates the storage/provenance contract and connection configuration without requiring Docker. A real service smoke check is:

```powershell
Invoke-WebRequest http://127.0.0.1:6333/readyz
```
