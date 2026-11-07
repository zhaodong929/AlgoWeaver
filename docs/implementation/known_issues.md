# Known issues

| ID | Issue | Impact | Workaround / next action | Status |
|---|---|---|---|---|
| KI-001 | `uv` was initially unavailable | Lockfile and uv-based install were unverified | `uv 0.13.7`, `uv.lock` and `uv sync --group dev --extra api` now verified | CLOSED |
| KI-002 | LangGraph was initially unavailable | Graph tests were skipped | LangGraph 1.2.20 installed; full graph tests now run | CLOSED |
| KI-003 | Docling and complex PDF layout parsing are unavailable; Qdrant client is installed but no embedding model/vector service is configured | WSL2 Docker execution is verified; complex PDF layout and semantic retrieval remain unverified | Install Docling/embedding models only when needed for those integration gates | OPEN |
| KI-004 | Project runs locally on Python 3.13.9 while the long-term target prefers Python 3.12 | Local and CI environments differ | CI #50 verified the full workflow on Python 3.12 and 3.13 | CLOSED |
| KI-005 | Tencent document page was not independently exported by browser automation | Exact page formatting, comments and hidden content are unverified | Use the user-provided source text as the current requirements source | OPEN |
| KI-006 | `main` has not been merged or published from the feature branch | Stable branch acceptance remains pending | Keep work on feature branches until explicit review/merge approval | OPEN |
