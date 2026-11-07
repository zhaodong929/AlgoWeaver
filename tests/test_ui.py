from algo_weaver.ui import build_reproduce_payload


def test_dashboard_payload_preserves_generation_and_additional_sources() -> None:
    payload = build_reproduce_payload(
        source_text="# Moving Average",
        source_id="doc-1",
        mode="litellm",
        generation_mode="llm",
        execute=True,
        backend="wsl",
        repair=True,
        additional_sources=[{"source_text": "history", "source_id": "history.py"}],
    )

    assert payload["generation_mode"] == "llm"
    assert payload["repair_mode"] == "llm"
    assert payload["additional_sources"][0]["source_id"] == "history.py"
