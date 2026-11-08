from pydantic import SecretStr

from algo_weaver.config import Settings
from algo_weaver.services.qdrant_retrieval import create_qdrant_retriever


def test_qdrant_settings_keep_memory_as_the_safe_default() -> None:
    settings = Settings(_env_file=None)

    assert settings.qdrant_mode == "memory"
    assert settings.qdrant_url == "http://127.0.0.1:6333"


def test_server_factory_uses_configured_collection_and_credentials(monkeypatch) -> None:
    captured: dict = {}

    def fake_init(self, **kwargs) -> None:
        captured.update(kwargs)

    def fake_collection_exists(_self, _name: str) -> bool:
        return True

    import qdrant_client

    monkeypatch.setattr(qdrant_client.QdrantClient, "__init__", fake_init)
    monkeypatch.setattr(qdrant_client.QdrantClient, "collection_exists", fake_collection_exists)
    settings = Settings(
        _env_file=None,
        qdrant_mode="server",
        qdrant_url="http://qdrant:6333",
        qdrant_api_key=SecretStr("test-key"),
        qdrant_collection_name="test_chunks",
        qdrant_timeout_seconds=13,
    )

    retriever = create_qdrant_retriever(settings, dimension=3)

    assert retriever.collection_name == "test_chunks"
    assert captured == {"url": "http://qdrant:6333", "api_key": "test-key", "timeout": 13.0}
