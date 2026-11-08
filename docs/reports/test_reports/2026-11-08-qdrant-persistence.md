# Qdrant persistence verification

**Date:** 2026-11-08 (Asia/Shanghai)  
**Status:** `BLOCKED` at image acquisition; server configuration is implemented.

The WSL2 distribution is running and exposes Docker Engine 29.1.3:

```text
/usr/bin/docker
29.1.3
```

The repository Compose definition is `deploy/qdrant/docker-compose.yml`. The local
WSL installation does not include the Compose plugin, so the equivalent service
command was prepared with `docker run`.

The actual image acquisition command was:

```sh
docker pull qdrant/qdrant:v1.15.5
```

It failed before container creation because Docker Hub could not be reached:

```text
failed to resolve reference ... dial tcp 198.18.0.90:443: i/o timeout
```

Therefore no Qdrant service-success or persistence claim is made. Once registry
access is available, run:

```sh
docker run -d --name algo-weaver-qdrant \
  -p 127.0.0.1:6333:6333 \
  -v "$PWD/deploy/qdrant/storage:/qdrant/storage" \
  qdrant/qdrant:v1.15.5
curl --fail http://127.0.0.1:6333/readyz
```

Then set `ALGOWEAVER_QDRANT_MODE=server` and
`ALGOWEAVER_QDRANT_URL=http://127.0.0.1:6333`, run the hybrid retrieval smoke test,
restart the container, and verify that the collection remains searchable.
