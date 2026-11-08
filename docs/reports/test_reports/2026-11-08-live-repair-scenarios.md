# Live repair scenario report

**Date:** 2026-11-08 (Asia/Shanghai)  
**Code model:** `deepseek-v4.1-flash-1017` through the configured Bailian-compatible endpoint  
**Execution:** WSL2 Docker, `python:3.12-slim`, network disabled, one repair attempt per case

The runs used the reviewed inventory moving-average plan and intentionally corrupted
`algorithm.py` in a temporary workspace. The model received the external sandbox
observation through `LLMRepairer`; the bounded loop then rewrote the existing artifact
and re-ran the same isolated test command.

| Case | Initial observation | Repair result | Evidence |
|---|---|---|---|
| Import error | `ModuleNotFoundError: No module named 'missing_helpers'` | `passed` after 1 attempt | final artifact SHA-256 `a016385230c3ab79fe9d1f06ca0646dca2325511788f70a6e5c0302444177cae` |
| Missing dependency | `ModuleNotFoundError: No module named 'pandas'` in `python:3.12-slim` | `passed` after 1 attempt | final artifact SHA-256 `a016385230c3ab79fe9d1f06ca0646dca2325511788f70a6e5c0302444177cae` |
| Timeout | WSL Docker command timed out after 8 seconds while running an infinite loop | `passed` after 1 attempt | final artifact SHA-256 `6ef05dab49bb8fdfd5e54ba9d4b45567fdd5c13280d1089ed084b85d846043c6` |

All final executions ran the generated two-test unittest suite and returned exit code
0. The import and dependency cases completed in under one second after repair; the
timeout case was bounded at 8 seconds before repair. The raw temporary workspaces were
deleted after each case, so no generated source or secret entered the repository.

This is live provider evidence for three failure classes. It does not claim that every
possible dependency or timeout can be repaired; the loop remains bounded and the model
patch is still subject to static validation and sandbox execution.
