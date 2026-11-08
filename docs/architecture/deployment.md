# Production API deployment

The API has three explicit production controls:

1. **API-key authentication**: set `ALGOWEAVER_API_AUTH_MODE=api_key` and
   `ALGOWEAVER_API_KEY` in the deployment secret store. Clients send either
   `X-API-Key: ...` or `Authorization: Bearer ...`. `/health` remains public for
   container and load-balancer probes.
2. **Per-process rate limiting**: `ALGOWEAVER_RATE_LIMIT_REQUESTS` requests per
   `ALGOWEAVER_RATE_LIMIT_WINDOW_SECONDS` for each client IP. Set the request
   limit to `0` only for local development. For multiple API replicas, configure
   a shared limit at the reverse proxy or API gateway because the built-in limit
   is intentionally process-local.
3. **HTTPS termination**: terminate TLS at a reverse proxy such as Caddy or
   Nginx, then forward traffic to Uvicorn on a private network. The application
   should not be exposed directly to the public internet.

## Example environment

```dotenv
ALGOWEAVER_APP_ENV=production
ALGOWEAVER_API_AUTH_MODE=api_key
ALGOWEAVER_API_KEY=<generated-deployment-secret>
ALGOWEAVER_RATE_LIMIT_REQUESTS=60
ALGOWEAVER_RATE_LIMIT_WINDOW_SECONDS=60
```

Keep the secret outside Git and outside generated-code workspaces. In a hosted
environment use the platform's secret manager; for a single server use a
root-readable environment file or service secret with restrictive permissions.

## Example Caddy reverse proxy

```caddyfile
api.example.edu.cn {
    reverse_proxy 127.0.0.1:8000
}
```

Caddy obtains and renews a certificate automatically when DNS points to the
server and ports 80/443 are reachable. Run the application behind it with:

```powershell
uv run uvicorn algo_weaver.api:create_app --factory --host 127.0.0.1 --port 8000
```

For a managed platform, map the same environment variables to its secret and
configuration settings, enable HTTPS-only ingress, and set a gateway-level
rate limit in addition to the application limit.

## Is a domain and ACME certificate required?

No. It depends on the audience:

| Use case | Recommended route | DNS/ACME required |
|---|---|---:|
| Same Windows machine or lab LAN | Run FastAPI + Streamlit locally; share the machine or private LAN address | No |
| One-time advisor demonstration | Cloudflare Quick Tunnel or ngrok forwarding to Streamlit | No; temporary HTTPS URL |
| Stable public service | Production Compose + Caddy with a domain pointed at the server | Yes |
| Streamlit-only public demo | Streamlit Community Cloud, with the API moved to a reachable service | No custom domain required |

For the fastest demonstration, start FastAPI on port 8000 and Streamlit on port
8501, then expose only Streamlit:

```powershell
cloudflared tunnel --url http://127.0.0.1:8501
```

The command returns a temporary `trycloudflare.com` HTTPS URL. The Streamlit
process still calls the local FastAPI service, so API credentials remain on the
machine. This route is suitable for a short demo and should not be treated as a
permanent production endpoint. If the API itself must be reachable externally,
expose it through a separate authenticated tunnel and keep
`ALGOWEAVER_API_AUTH_MODE=api_key` enabled.

The Streamlit sidebar includes an optional FastAPI API-key field and sends it as
`X-API-Key`, so a tunneled Streamlit page can still call an authenticated API.

An equivalent ngrok demo is:

```powershell
ngrok http 8501
```

Both tunnel processes must remain running while the advisor tests the system.

## Reproducible production compose

`deploy/production/docker-compose.yml` provides an API container, a persistent
Qdrant service and Caddy TLS termination. Copy
`deploy/production/.env.production.example` to `.env.production`, replace every
placeholder through the deployment secret manager, point DNS at the server, and
run:

```bash
cd deploy/production
cp .env.production.example .env.production
docker compose up -d --build
docker compose ps
```

Caddy obtains the certificate after ports 80 and 443 are reachable. The API
container does not mount the host Docker socket; generated-code execution should
be delegated to the separately controlled WSL/Docker runner. This keeps the
public API container from receiving host-daemon privileges.
