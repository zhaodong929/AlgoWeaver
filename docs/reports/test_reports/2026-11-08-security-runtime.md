# API security runtime smoke report

**Date:** 2026-11-08 (Asia/Shanghai)  
**Endpoint:** local Uvicorn on `127.0.0.1:8011`  
**Configuration:** API-key mode, one request per 60-second window

The service was started with a temporary smoke secret supplied through environment
variables. No secret was written to the repository.

Observed HTTP results:

```text
GET  /health                       -> 200
POST /metrics (without API key)   -> 401
POST /metrics (valid API key)     -> 200
POST /metrics (second request)    -> 429
```

This verifies the application-level authentication and rate-limit boundary. HTTPS
certificate issuance and a shared multi-replica gateway limit still require deployment
DNS and an external gateway.
