"""Small Streamlit client for the AlgoWeaver FastAPI surface."""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from urllib import request


def build_reproduce_payload(
    *,
    source_text: str,
    source_id: str,
    mode: str,
    generation_mode: str,
    execute: bool,
    backend: str,
    repair: bool,
    additional_sources: Sequence[dict[str, str]] = (),
) -> dict:
    """Build the stable JSON payload used by the dashboard and API."""

    return {
        "source_text": source_text,
        "source_id": source_id,
        "mode": mode,
        "generation_mode": generation_mode,
        "execute": execute,
        "backend": backend,
        "repair": repair,
        "repair_mode": "llm" if repair and generation_mode == "llm" else "template",
        "additional_sources": list(additional_sources),
    }


def _post_json(
    url: str,
    payload: dict,
    *,
    api_key: str = "",
    timeout: float = 300.0,
) -> tuple[int, dict]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key.strip():
        headers["X-API-Key"] = api_key.strip()
    req = request.Request(
        url,
        data=body,
        headers=headers,
        method="POST",
    )
    with request.urlopen(req, timeout=timeout) as response:
        return response.status, json.loads(response.read())


def main() -> None:
    """Render the minimal end-to-end dashboard."""

    import streamlit as st

    st.set_page_config(page_title="AlgoWeaver", page_icon="🧵", layout="wide")
    st.title("AlgoWeaver · Algorithm Intelligence & Reproduction Agent")
    st.caption("资料接入 → 能力抽取 → 复刻生成 → 沙箱验证 → 能力沉淀")

    api_base = st.sidebar.text_input(
        "FastAPI 地址",
        value=os.getenv("ALGOWEAVER_UI_API_BASE", "http://127.0.0.1:8000"),
    ).rstrip("/")
    api_key = st.sidebar.text_input(
        "FastAPI API Key（可选）",
        value=os.getenv("ALGOWEAVER_UI_API_KEY", ""),
        type="password",
    )
    mode = st.sidebar.selectbox("LLM 模式", ["mock", "litellm"], index=0)
    generation_mode = st.sidebar.selectbox("生成模式", ["template", "mock", "llm"], index=0)
    execute = st.sidebar.checkbox("在 Docker/WSL 沙箱执行", value=False)
    backend = st.sidebar.selectbox("执行后端", ["docker", "wsl"], index=0)
    repair = st.sidebar.checkbox("失败后自动修复", value=False)

    source_text = st.text_area(
        "算法能力描述或业务文档",
        value=(
            "# Inventory demand forecasting\n"
            "Use a moving average over historical daily sales.\n"
            "Inputs: ordered sales sequence and positive window.\n"
            "Outputs: window averages and next-period forecast."
        ),
        height=220,
    )
    uploaded = st.file_uploader("追加历史代码、实验记录或测试报告", type=["txt", "md", "py", "csv", "json"])

    if st.button("运行 AlgoWeaver", type="primary", use_container_width=True):
        additional_sources: list[dict[str, str]] = []
        if uploaded is not None:
            additional_sources.append(
                {
                    "source_text": uploaded.getvalue().decode("utf-8", errors="replace"),
                    "source_id": uploaded.name,
                    "source_type": "code" if uploaded.name.endswith(".py") else "document",
                    "source_format": uploaded.name.rsplit(".", 1)[-1],
                    "source_location": uploaded.name,
                }
            )
        payload = build_reproduce_payload(
            source_text=source_text,
            source_id="streamlit-input",
            mode=mode,
            generation_mode=generation_mode,
            execute=execute,
            backend=backend,
            repair=repair,
            additional_sources=additional_sources,
        )
        with st.spinner("Agent 正在执行检索、规划、生成和验证…"):
            try:
                status, result = _post_json(f"{api_base}/reproduce", payload, api_key=api_key)
            except Exception as exc:  # pragma: no cover - UI runtime boundary
                st.error(f"API 调用失败：{exc}")
                return
        if status >= 400:
            st.error(result.get("detail", result))
            return

        left, right = st.columns(2)
        with left:
            st.subheader("能力卡片")
            st.json(result.get("capability", {}))
            st.subheader("检索证据")
            st.json(result.get("hits", []))
        with right:
            st.subheader("复刻计划")
            st.json(result.get("plan", {}))
            st.subheader("验证结果")
            st.json(result.get("reports", []))
            if result.get("execution"):
                st.subheader("沙箱执行")
                st.json(result["execution"])

        st.subheader("生成代码和测试")
        for artifact in result.get("bundle", {}).get("artifacts", []):
            st.markdown(f"**{artifact.get('path', 'artifact')}**")
            st.code(artifact.get("content", ""), language="python")


if __name__ == "__main__":  # pragma: no cover
    main()
