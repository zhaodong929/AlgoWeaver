from pathlib import Path

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


def test_dashboard_entrypoint_renders_and_submits_request(monkeypatch) -> None:
    """Exercise the dashboard's default form and request path with Streamlit AppTest."""

    streamlit_testing = __import__("streamlit.testing.v1", fromlist=["AppTest"])
    app_test = streamlit_testing.AppTest.from_file(
        Path(__file__).resolve().parents[1] / "src" / "algo_weaver" / "ui.py"
    )

    class FakeResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def read(self) -> bytes:
            return (
                b'{"capability": {}, "hits": [], "plan": {}, "reports": [], '
                b'"bundle": {"artifacts": []}}'
            )

    def fake_urlopen(*args, **kwargs):
        return FakeResponse()

    # ui.py imports urllib.request as ``request``; patching its shared urlopen
    # function keeps this test independent of a running API process.
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    app_test.run()

    assert app_test.title[0].value.startswith("AlgoWeaver")
    assert app_test.text_area[0].value.startswith("# Inventory demand forecasting")
    assert len(app_test.button) == 1

    app_test.button[0].click().run()

    assert not app_test.exception
    assert len(app_test.json) >= 4
