# Live LLM reproduction and repair report

**Date:** 2026-11-08 (Asia/Shanghai)  
**Primary model:** `qwen3.8-max-0902`  
**Code model:** `deepseek-v4.1-flash-1017`  
**Execution:** WSL2 Docker, `python:3.12-slim`, network disabled

## First live generation

The command used `--mode litellm --generation-mode llm --backend wsl --execute` with
the inventory description and CSV. Qwen extracted and planned the capability, and
DeepSeek generated `algorithm.py` and `test_algorithm.py`. The sandbox then exposed a
real dependency failure:

```text
ModuleNotFoundError: No module named 'pytest'
```

The generated test imported `pytest`, while the minimal execution image intentionally
contains only the standard library. The run was retained as a genuine failure record
under `data/processed/live_llm_demo_20261108/` and was not marked verified.

## Live repair and rerun

The same live workflow was rerun with `--repair --repair-mode llm`. The bounded repair
loop sent the sandbox failure to DeepSeek, applied a patch to the existing artifacts,
and reran the same isolated command. The final result was:

- sandbox status: `passed`;
- generated tests: 8 passed;
- image: `python:3.12-slim`;
- execution duration: `5.966` seconds;
- no network access or host execution;
- output: `data/processed/live_llm_repair_demo_20261108/`.

The final bundle remains labelled `unverified` until an independent promotion step
accepts its complete capability and metric policy. This report demonstrates the full
live generation → external failure → LLM repair → isolated rerun path.
