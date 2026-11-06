# Known issues

| ID | Issue | Impact | Workaround / next action | Status |
|---|---|---|---|---|
| KI-001 | `uv` is not installed in the current PowerShell environment | Cannot generate or verify `uv.lock` here | Keep `pyproject.toml` authoritative; install uv before lockfile release | OPEN |
| KI-002 | LangGraph is not installed | Two graph tests are skipped | Keep the offline fallback; install the declared dependency for full graph verification | OPEN |
| KI-003 | Optional Docling, Tree-sitter, Qdrant, Docker and API dependencies are not verified in this environment | Later milestones cannot claim integration completion yet | Build stdlib interfaces first and gate adapters with explicit tests | OPEN |
| KI-004 | Project runs on Python 3.13.9 while the long-term target prefers Python 3.12 | Compatibility is plausible but not yet dual-version verified | Re-run CI on Python 3.12 before final acceptance | OPEN |
| KI-005 | Tencent document page was not independently exported by browser automation | Exact page formatting, comments and hidden content are unverified | Use the user-provided source text as the current requirements source | OPEN |
| KI-006 | `main` has not been merged or published from the feature branch | Stable branch acceptance remains pending | Keep work on feature branches until explicit review/merge approval | OPEN |
