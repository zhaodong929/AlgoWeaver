from pathlib import Path
from urllib import request

from algo_weaver.ui import _post_json, build_compare_payload, build_reproduce_payload


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


def test_compare_payload_is_json_ready() -> None:
    assert build_compare_payload(actual=[18, 21, 20], window=2) == {
        "actual": [18, 21, 20],
        "window": 2,
        "selection_metric": "mae",
    }


def test_post_json_adds_api_key_header(monkeypatch) -> None:
    captured: dict[str, str] = {}

    class Response:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return b"{}"

    def fake_urlopen(req, *, timeout):
        captured["api_key"] = req.get_header("X-api-key")
        return Response()

    monkeypatch.setattr(request, "urlopen", fake_urlopen)
    _post_json("http://api.test/reproduce", {}, api_key=" secret ")

    assert captured["api_key"] == "secret"


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
    assert len(app_test.button) == 2

    app_test.button[1].click().run()

    assert not app_test.exception
    assert len(app_test.json) >= 4
