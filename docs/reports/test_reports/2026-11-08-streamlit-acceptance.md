# Streamlit interaction acceptance report

**Date:** 2026-11-08 (Asia/Shanghai)  
**Scope:** automated browser-equivalent interaction plus live HTTP runtime smoke

## Automated interaction

`tests/test_ui.py::test_dashboard_entrypoint_renders_and_submits_request` uses
Streamlit `AppTest` to execute the actual `src/algo_weaver/ui.py` entrypoint. It
verifies:

1. the page title and default inventory description render;
2. the primary run button exists;
3. clicking the button submits the reproduction payload;
4. capability, evidence, plan and report JSON panels render without exceptions.

The request boundary is mocked in this unit test so it does not claim a live model
call. The live API boundary was separately exercised with FastAPI and returned HTTP
200 for `/health` and `/metrics`.

## Runtime page smoke

Streamlit was started on `127.0.0.1:8510` while FastAPI ran on `127.0.0.1:8010`.
The Streamlit health endpoint returned HTTP 200 (`ok`) and the root page returned
HTTP 200 with 7,863 bytes of HTML. This confirms the deployed page process and HTTP
surface are reachable.

## Boundary

This report is automated interaction evidence. A human browser session with file
upload and visual inspection is still recommended before public deployment; no such
manual session is claimed here.
