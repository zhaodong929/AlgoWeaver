"""Streamlit workspace for the AlgoWeaver end-to-end reproduction flow.

The UI intentionally remains a thin client over ``POST /reproduce``.  The
request schema is kept stable so the dashboard can be used with the local API,
Docker Compose, or a hosted FastAPI service without any code changes.
"""

from __future__ import annotations

import json
import os
from collections.abc import Sequence
from html import escape
from urllib import request

DEFAULT_SOURCE_TEXT = (
    "# Inventory demand forecasting\n"
    "Use a moving average over historical daily sales.\n"
    "Inputs: ordered sales sequence and positive window.\n"
    "Outputs: window averages and next-period forecast."
)


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


def build_compare_payload(
    *, actual: Sequence[float], window: int, selection_metric: str = "mae"
) -> dict:
    """Build the deterministic candidate-comparison request."""

    return {"actual": list(actual), "window": window, "selection_metric": selection_metric}


def _post_json(
    url: str,
    payload: dict,
    *,
    api_key: str = "",
    timeout: float = 300.0,
) -> tuple[int, dict]:
    """POST JSON to the API, optionally using the dashboard API key."""

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


def _inject_styles(st) -> None:
    """Install a small, self-contained visual system for the workspace."""

    st.markdown(
        """
        <style>
        :root { --aw-ink: #2f2d2a; --aw-muted: #77716a; --aw-line: #e5e0d8;
                --aw-paper: #fbfaf8; --aw-card: #ffffff; --aw-accent: #c46b4f;
                --aw-accent-soft: #f6e8e1; --aw-green: #2f7d64; }
        .stApp { background: var(--aw-paper); color: var(--aw-ink); }
        [data-testid="stSidebar"] { background: #f5f1ec; border-right: 1px solid var(--aw-line); }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.3rem; }
        .aw-brand { display:flex; align-items:center; gap:.7rem; margin-bottom:1.5rem; }
        .aw-mark { width:2.2rem; height:2.2rem; border-radius:.7rem; display:grid; place-items:center;
                   background: #2f2d2a; color:#fff; font-size:1.15rem; }
        .aw-brand-title { font-size:1.05rem; font-weight:700; letter-spacing:-.02em; }
        .aw-brand-sub { font-size:.67rem; color:var(--aw-muted); margin-top:.08rem; }
        .aw-kicker { color:var(--aw-accent); text-transform:uppercase; letter-spacing:.13em;
                     font-size:.69rem; font-weight:700; margin-bottom:.35rem; }
        .aw-hero { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem;
                   padding:1.2rem 1.35rem; background:linear-gradient(110deg,#fff,#fff9f6);
                   border:1px solid var(--aw-line); border-radius:1.05rem; margin: .2rem 0 1rem; }
        .aw-hero h1 { margin:0; font-size:1.9rem; letter-spacing:-.045em; color:var(--aw-ink); }
        .aw-hero p { margin:.4rem 0 0; color:var(--aw-muted); font-size:.88rem; }
        .aw-pill { display:inline-flex; align-items:center; gap:.35rem; border:1px solid var(--aw-line);
                   background:#fff; border-radius:999px; padding:.35rem .65rem; color:var(--aw-muted);
                   font-size:.73rem; white-space:nowrap; }
        .aw-pill.live { border-color:#b9dfd0; color:var(--aw-green); background:#f1faf6; }
        .aw-card { border:1px solid var(--aw-line); border-radius:1rem; background:var(--aw-card);
                   padding:1rem 1.1rem; box-shadow:0 4px 18px rgba(47,45,42,.035); }
        .aw-card-title { display:flex; justify-content:space-between; align-items:center; gap:.7rem;
                         margin-bottom:.7rem; font-weight:700; }
        .aw-card-title small { color:var(--aw-muted); font-weight:400; font-size:.75rem; }
        .aw-stepper { display:grid; grid-template-columns:repeat(6,1fr); gap:.45rem; margin: .8rem 0 1rem; }
        .aw-step { border-top:3px solid #d8d2ca; padding-top:.45rem; color:var(--aw-muted); font-size:.71rem; }
        .aw-step.done { border-color:var(--aw-green); color:var(--aw-green); }
        .aw-step.active { border-color:var(--aw-accent); color:var(--aw-accent); }
        .aw-step b { display:block; color:var(--aw-ink); font-size:.78rem; margin-bottom:.12rem; }
        .aw-empty { border:1px dashed #d8d2ca; border-radius:.85rem; padding:1.15rem; color:var(--aw-muted);
                    text-align:center; background:#fdfcfb; }
        .aw-history-item { padding:.65rem .75rem; border-bottom:1px solid var(--aw-line); }
        .aw-history-item:last-child { border-bottom:0; }
        .aw-history-name { color:var(--aw-ink); font-size:.8rem; font-weight:600; }
        .aw-history-meta { color:var(--aw-muted); font-size:.7rem; margin-top:.12rem; }
        div[data-testid="stMetric"] { background:#fff; border:1px solid var(--aw-line); border-radius:.8rem; padding:.7rem .8rem; }
        div[data-testid="stTabs"] button { font-size:.83rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_brand(st) -> None:
    st.markdown(
        """
        <div class="aw-brand">
          <div class="aw-mark">✦</div>
          <div><div class="aw-brand-title">AlgoWeaver</div>
          <div class="aw-brand-sub">Algorithm Intelligence Studio</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar(st) -> tuple[str, str, str, str, bool, str, bool, str]:
    """Render navigation and connection controls while keeping one run action."""

    with st.sidebar:
        _render_brand(st)
        st.caption("WORKSPACE")
        section = st.radio(
            "工作区",
            ["任务工作台", "执行记录", "能力资产", "系统设置"],
            index=0,
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("连接与运行")
        api_base = st.text_input(
            "FastAPI 地址",
            value=os.getenv("ALGOWEAVER_UI_API_BASE", "http://127.0.0.1:8000"),
            help="本地开发使用 127.0.0.1；部署后填写 HTTPS API 地址。",
        ).rstrip("/")
        api_key = st.text_input(
            "API Key",
            value=os.getenv("ALGOWEAVER_UI_API_KEY", ""),
            type="password",
            help="仅通过请求头发送，不会写入任务结果。",
        )
        mode = st.selectbox("理解模型", ["mock", "litellm"], index=0)
        generation_mode = st.selectbox("代码生成", ["template", "mock", "llm"], index=0)
        execute = st.checkbox("在隔离环境执行", value=False)
        backend = st.selectbox("执行后端", ["docker", "wsl"], index=0)
        repair = st.checkbox("失败后自动修复", value=False)
        st.divider()
        st.markdown(
            '<span class="aw-pill live">● 本地工作区在线</span>',
            unsafe_allow_html=True,
        )
        return api_base, api_key, mode, generation_mode, execute, backend, repair, section


def _status_label(result: dict) -> tuple[str, str]:
    execution = result.get("execution") or {}
    status = str(execution.get("status", ""))
    if status == "passed":
        return "已验证", "live"
    if status in {"failed", "timeout"}:
        return "需要修复", ""
    if result.get("capability"):
        return "已生成", ""
    return "等待运行", ""


def _step_state(result: dict, execute: bool) -> list[tuple[str, str]]:
    if not result:
        return [("资料接入", "active"), ("能力抽取", ""), ("混合检索", ""), ("复刻规划", ""), ("验证执行", ""), ("能力沉淀", "")]
    reports = result.get("reports") or []
    execution_status = (result.get("execution") or {}).get("status")
    states = ["done", "done", "done", "done", "", ""]
    if execute and execution_status:
        states[4] = "done" if execution_status == "passed" else "active"
        states[5] = "done" if result.get("registry_record") else ""
    elif reports:
        states[4] = "done"
    return list(
        zip(
            ("资料接入", "能力抽取", "混合检索", "复刻规划", "验证执行", "能力沉淀"),
            states,
            strict=False,
        )
    )


def _render_stepper(st, result: dict, execute: bool) -> None:
    steps = "".join(
        f'<div class="aw-step {state}"><b>{escape(name)}</b>{"完成" if state == "done" else "进行中" if state == "active" else "待执行"}</div>'
        for name, state in _step_state(result, execute)
    )
    st.markdown(f'<div class="aw-stepper">{steps}</div>', unsafe_allow_html=True)


def _render_overview(st, result: dict) -> None:
    capability = result.get("capability") or {}
    hits = result.get("hits") or []
    reports = result.get("reports") or []
    execution = result.get("execution") or {}
    registry = result.get("registry_record") or {}
    status, style = _status_label(result)
    cols = st.columns(4)
    cols[0].metric("能力状态", status)
    cols[1].metric("检索证据", len(hits))
    cols[2].metric("验证报告", len(reports))
    cols[3].metric("执行结果", execution.get("status", "未执行"))
    st.markdown(
        '<div class="aw-card"><div class="aw-card-title">能力摘要 '
        f'<span class="aw-pill {style}">{escape(str(capability.get("name", "待生成能力")))}</span></div>'
        f'<div style="color:#77716a;font-size:.84rem;line-height:1.6">{escape(str(capability.get("description", "运行任务后，将在这里展示算法能力、输入输出与适用条件。")))}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if registry:
        st.caption(
            f"能力资产已写入注册表 · {registry.get('capability_id', 'unknown')} · v{registry.get('version', '?')}"
        )


def _render_sources(st, result: dict) -> None:
    sources = result.get("sources") or []
    if not sources:
        st.info("本次任务使用工作区文本作为主来源。追加文件后，来源定位会显示在这里。")
        return
    for source in sources:
        st.markdown(
            f"**{escape(str(source.get('source_id', 'source')))}** · "
            f"{escape(str(source.get('source_type', 'document')))} · "
            f"`{escape(str(source.get('content_sha256', ''))[:12])}`"
        )
    st.json(sources)


def _render_history(st) -> None:
    history = st.session_state.get("aw_history", [])
    if not history:
        st.markdown('<div class="aw-empty">运行第一项任务后，最近任务会出现在这里。</div>', unsafe_allow_html=True)
        return
    for item in history[-5:][::-1]:
        st.markdown(
            '<div class="aw-history-item">'
            f'<div class="aw-history-name">{escape(item["name"])}</div>'
            f'<div class="aw-history-meta">{escape(item["status"])} · {escape(item["mode"])} · {escape(item["time"])}</div>'
            '</div>',
            unsafe_allow_html=True,
        )


def _render_results(st, result: dict, execute: bool) -> None:
    st.subheader("任务结果")
    tabs = st.tabs(["概览", "检索证据", "复刻计划", "代码与测试", "验证报告", "能力资产"])
    with tabs[0]:
        _render_overview(st, result)
    with tabs[1]:
        left, right = st.columns([1.15, 1])
        with left:
            st.markdown("**证据命中**")
            st.json(result.get("hits", []))
        with right:
            st.markdown("**来源追踪**")
            _render_sources(st, result)
    with tabs[2]:
        st.markdown("**Agent 复刻计划**")
        st.json(result.get("plan", {}))
    with tabs[3]:
        artifacts = (result.get("bundle") or {}).get("artifacts", [])
        if not artifacts:
            st.markdown('<div class="aw-empty">当前任务没有返回生成文件。</div>', unsafe_allow_html=True)
        else:
            for artifact in artifacts:
                path = str(artifact.get("path", "artifact"))
                st.markdown(f"**{escape(path)}** · {escape(str(artifact.get('kind', 'file')))}")
                st.code(str(artifact.get("content", "")), language="python" if path.endswith(".py") else "text")
        st.markdown("**依赖分析**")
        st.json(result.get("dependency_reports", []))
    with tabs[4]:
        st.markdown("**验证报告**")
        st.json(result.get("reports", []))
        if execute:
            st.markdown("**沙箱执行与修复轨迹**")
            st.json(result.get("execution", {}))
            if result.get("repair_result"):
                st.json(result["repair_result"])
        if result.get("metric_report"):
            st.markdown("**业务指标**")
            st.json(result["metric_report"])
    with tabs[5]:
        registry = result.get("registry_record")
        if registry:
            st.success("能力已沉淀到版本化注册表。")
            st.json(registry)
        else:
            st.info("本次请求未开启持久化；打开 API 的 persist 配置后可将验证通过的能力写入注册表。")
    comparison = st.session_state.get("aw_comparison")
    if comparison:
        st.subheader("候选方案比较")
        st.caption("基于同一组历史数据比较候选算法，并保留指标门禁与选择理由。")
        st.json(comparison)


def main() -> None:
    """Render the AlgoWeaver task workspace."""

    import streamlit as st

    st.set_page_config(page_title="AlgoWeaver · Intelligence Studio", page_icon="✦", layout="wide")
    _inject_styles(st)
    api_base, api_key, mode, generation_mode, execute, backend, repair, section = _render_sidebar(st)

    st.title("AlgoWeaver")
    st.caption("Algorithm Intelligence Studio · 从资料到可验证算法能力")
    result = st.session_state.get("aw_result", {})
    status, style = _status_label(result)
    st.markdown(
        '<div class="aw-hero"><div><div class="aw-kicker">Reproduction workspace</div>'
        '<h1>把算法能力编织成可复用资产</h1>'
        '<p>描述目标，接入证据，生成计划与代码，并在隔离环境完成验证。</p></div>'
        f'<span class="aw-pill {style}">● {escape(status)}</span></div>',
        unsafe_allow_html=True,
    )
    if section == "执行记录":
        st.subheader("执行记录")
        st.caption("最近五次任务会保留在当前浏览器会话中，便于快速复盘。")
        _render_history(st)
        return
    if section == "能力资产":
        st.subheader("能力资产")
        st.caption("验证通过并持久化的算法能力会在这里展示。")
        if result.get("registry_record"):
            st.json(result["registry_record"])
        else:
            st.markdown('<div class="aw-empty">当前会话暂无已加载的能力资产。</div>', unsafe_allow_html=True)
        return
    if section == "系统设置":
        st.subheader("系统设置")
        st.markdown(
            '<div class="aw-card"><div class="aw-card-title">运行边界</div>'
            '<div style="color:#77716a;line-height:1.7;font-size:.84rem">'
            'API Key 仅在请求时放入 <code>X-API-Key</code> 请求头；生成代码通过 FastAPI 的隔离执行路径运行。'
            '生产部署建议使用 HTTPS、反向代理限流和独立的 Qdrant 持久化服务。</div></div>',
            unsafe_allow_html=True,
        )
        return
    _render_stepper(st, result, execute)

    input_col, context_col = st.columns([1.65, 1])
    with input_col:
        st.markdown('<div class="aw-card-title">任务描述 <small>Describe the capability</small></div>', unsafe_allow_html=True)
        source_text = st.text_area(
            "算法能力描述或业务文档",
            value=DEFAULT_SOURCE_TEXT,
            height=220,
            label_visibility="collapsed",
        )
        uploaded = st.file_uploader(
            "追加历史代码、实验记录或测试报告",
            type=["txt", "md", "py", "csv", "json", "yaml", "yml"],
            help="追加文件会作为带来源定位的证据传给 Agent。",
        )
    with context_col:
        st.markdown('<div class="aw-card-title">任务配置 <small>Runtime controls</small></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="aw-card"><div style="font-size:.8rem;color:#77716a">理解</div><b>{escape(mode)}</b>'
            f'<div style="font-size:.8rem;color:#77716a;margin-top:.7rem">生成</div><b>{escape(generation_mode)}</b>'
            f'<div style="font-size:.8rem;color:#77716a;margin-top:.7rem">执行</div><b>{"隔离沙箱 · " + escape(backend) if execute else "仅静态验证"}</b>'
            f'<div style="font-size:.8rem;color:#77716a;margin-top:.7rem">修复</div><b>{"自动修复开启" if repair else "按需修复"}</b></div>',
            unsafe_allow_html=True,
        )
        st.caption("提示：首次演示可使用 mock + template；接入真实模型时切换为 litellm + llm。")
        compare_values = st.text_input(
            "库存历史序列（候选比较）",
            value="18,21,20,24,22",
            help="输入逗号分隔的历史销量，至少 2 个数。",
        )
        compare_window = st.number_input("比较窗口", min_value=1, value=3, step=1)
        compare_clicked = st.button("比较候选算法", use_container_width=True)

    if compare_clicked:
        try:
            values = [float(item.strip()) for item in compare_values.split(",") if item.strip()]
            payload = build_compare_payload(actual=values, window=int(compare_window))
            with st.spinner("正在比较候选算法…"):
                status_code, response = _post_json(f"{api_base}/compare", payload, api_key=api_key)
            if status_code >= 400:
                st.error(response.get("detail", response))
            else:
                st.session_state["aw_comparison"] = response
        except (TypeError, ValueError) as exc:
            st.error(f"候选比较输入无效：{exc}")

    if st.button("运行 AlgoWeaver", type="primary", use_container_width=True):
        additional_sources: list[dict[str, str]] = []
        if uploaded is not None:
            suffix = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else "txt"
            additional_sources.append(
                {
                    "source_text": uploaded.getvalue().decode("utf-8", errors="replace"),
                    "source_id": uploaded.name,
                    "source_type": "code" if suffix == "py" else "document",
                    "source_format": suffix,
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
                status_code, response = _post_json(f"{api_base}/reproduce", payload, api_key=api_key)
            except Exception as exc:  # pragma: no cover - UI runtime boundary
                st.error(f"API 调用失败：{exc}")
                return
        if status_code >= 400:
            st.error(response.get("detail", response))
            return
        st.session_state["aw_result"] = response
        st.session_state.setdefault("aw_history", []).append(
            {
                "name": str((response.get("capability") or {}).get("name", "未命名能力")),
                "status": _status_label(response)[0],
                "mode": generation_mode,
                "time": "刚刚",
            }
        )
        result = response

    if result:
        _render_results(st, result, execute)
    else:
        st.markdown('<div class="aw-empty">准备就绪。提交任务后，这里会按证据、计划、代码、验证和资产分层展示结果。</div>', unsafe_allow_html=True)

    with st.expander("最近任务", expanded=bool(st.session_state.get("aw_history"))):
        _render_history(st)


if __name__ == "__main__":  # pragma: no cover
    main()
