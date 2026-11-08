# HTTPS runtime smoke report

**Date:** 2026-11-08 (Asia/Shanghai)  
**Runtime:** Caddy 2.10 Alpine in WSL Docker  
**Scope:** local TLS termination with Caddy's internal CA

A temporary Caddy site using `localhost:8443`, `tls internal` and a fixed response
was started from the same Caddy image used by the production bundle. The request:

```text
curl --insecure --resolve localhost:8443:127.0.0.1 https://localhost:8443
```

returned `ok` with exit status 0. The smoke container was removed after the check.
This proves the Caddy HTTPS listener and certificate termination path. Public DNS,
ACME certificate issuance and external firewall ingress remain deployment-specific.
