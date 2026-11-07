# Known issues

| ID | Issue | Impact | Workaround / next action | Status |
|---|---|---|---|---|
| KI-001 | `uv` was initially unavailable | Lockfile and uv-based install were unverified | `uv 0.13.7`, `uv.lock` and `uv sync --group dev --extra api` now verified | CLOSED |
| KI-002 | LangGraph was initially unavailable | Graph tests were skipped | LangGraph 1.2.20 installed; full graph tests now run | CLOSED |
| KI-003 | Docling and complex PDF layout parsing are unavailable; Qdrant client is installed but no embedding model/vector service is configured | WSL2 Docker execution is verified; complex PDF layout and semantic retrieval remain unverified | Install Docling/embedding models only when needed for those integration gates | OPEN |
| KI-004 | Project runs locally on Python 3.13.9 while the long-term target prefers Python 3.12 | Local and CI environments differ | CI #50 verified the full workflow on Python 3.12 and 3.13 | CLOSED |
| KI-005 | Tencent document page was not independently exported by browser automation | Exact page formatting, comments and hidden content are unverified | Use the user-provided source text as the current requirements source | OPEN |
| KI-006 | `main` has not been merged or published from the feature branch | Stable branch acceptance remains pending | Keep work on feature branches until explicit review/merge approval | OPEN |
| KI-007 | GitHub Ubuntu runners exposed a `wsl.exe` compatibility command and Click rendered Typer errors differently from the Windows shell | CI could run a Windows-only integration test and a stream-sensitive CLI assertion | Gate WSL integration by host platform and assert the provider guard through the command boundary; CI #68 passes on Python 3.12/3.13 | CLOSED |
| KI-008 | Real provider credentials are unavailable in the current environment | Live LLM generation and repair cannot be claimed from Mock contract tests | Keep provider-backed modes explicit and run the acceptance path when a configured provider is supplied | OPEN |
| KI-009 | `/reproduce` sandbox metrics currently target the inventory moving-average contract | Other task-specific prediction interfaces and metric policies are not yet configurable | Add explicit task adapters after the core demo is stable | OPEN |
| KI-010 | Windows/WSL GPU is visible, but Docker GPU runtime and CUDA image pull are not verified | Local embedding/reranker execution cannot yet be claimed reproducible | Verify Docker GPU integration and image supply before selecting model weights | OPEN |
