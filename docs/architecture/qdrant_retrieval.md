# Qdrant vector adapter

`QdrantVectorRetriever` is an optional adapter over the existing `EvidenceChunk` and `RetrievalHit` schemas. It accepts externally supplied vectors, stores them in an in-memory or configured Qdrant service, and returns the original source ID, path and line range with every hit.

The default `ALGOWEAVER_QDRANT_MODE=memory` keeps tests and offline demos self-contained. For a Windows-local persistent path, set `ALGOWEAVER_QDRANT_MODE=local` and `ALGOWEAVER_QDRANT_PATH=data/processed/qdrant`; the adapter reopens the same collection across client instances. For a service, start `deploy/qdrant/docker-compose.yml`, set `ALGOWEAVER_QDRANT_MODE=server` and point `ALGOWEAVER_QDRANT_URL` at `http://127.0.0.1:6333`. The collection is created idempotently and data is stored in the Docker named volume `qdrant_qdrant_storage`. A named volume is intentional: Qdrant's mmap storage must stay on the Linux Docker filesystem; binding `/mnt/d` or another Windows-mounted path can corrupt payload files after restart. Set `ALGOWEAVER_QDRANT_API_KEY` when the service is protected.

```powershell
cd deploy/qdrant
Copy-Item .env.example .env
docker compose up -d
docker compose ps
```

If Docker Compose is unavailable, the equivalent WSL Docker command is:

```bash
docker volume create qdrant_qdrant_storage
docker run -d --name algo-weaver-qdrant -p 127.0.0.1:6333:6333 \
  -v qdrant_qdrant_storage:/qdrant/storage qdrant/qdrant:v1.20.0
```

Then configure the application environment:

```powershell
$env:ALGOWEAVER_QDRANT_MODE = "server"
$env:ALGOWEAVER_QDRANT_URL = "http://127.0.0.1:6333"
```

When Windows localhost forwarding is unavailable, obtain the WSL address with
`wsl.exe -e sh -lc "hostname -I"` and use
`http://<wsl-ip>:6333` instead. The service must publish port 6333 on
`0.0.0.0` inside WSL, as shown by the smoke report.

For the local persistent mode:

```powershell
$env:ALGOWEAVER_QDRANT_MODE = "local"
$env:ALGOWEAVER_QDRANT_PATH = "data/processed/qdrant"
```

The test suite uses Qdrant's local in-memory client and a mocked server constructor; it validates the storage/provenance contract and connection configuration without requiring Docker. A real service smoke check is:

```powershell
Invoke-WebRequest http://127.0.0.1:6333/readyz
```
