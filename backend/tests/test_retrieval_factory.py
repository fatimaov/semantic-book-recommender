from unittest.mock import Mock

import pytest
from flask import Flask

from backend.app.factories.retrieval_factory import (
    RetrievalConfigurationError,
    get_retrieval_dependencies,
)


def _app(app_env: str) -> Flask:
    app = Flask(__name__)
    app.config["APP_ENV"] = app_env
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://example/database"
    return app


def test_local_environment_selects_and_caches_huggingface_and_chroma(monkeypatch):
    from backend.app.providers import huggingface_embeddings
    from backend.app.repositories import chroma_repository

    provider = Mock(name="huggingface_provider")
    repository = Mock(name="chroma_repository")
    provider_class = Mock(return_value=provider)
    repository_class = Mock(return_value=repository)
    monkeypatch.setattr(
        huggingface_embeddings, "HuggingFaceEmbeddingProvider", provider_class
    )
    monkeypatch.setattr(chroma_repository, "ChromaRepository", repository_class)
    app = _app("local")

    first_result = get_retrieval_dependencies(app)
    second_result = get_retrieval_dependencies(app)

    assert first_result == (provider, repository)
    assert second_result is first_result
    provider_class.assert_called_once_with()
    repository_class.assert_called_once_with()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "postgresql://example/database"


def test_production_environment_selects_and_caches_gemini_and_postgres(monkeypatch):
    from backend.app.providers import gemini_embeddings
    from backend.app.repositories import postgres_repository

    provider = Mock(name="gemini_provider")
    repository = Mock(name="postgres_repository")
    provider_class = Mock(return_value=provider)
    repository_class = Mock(return_value=repository)
    monkeypatch.setattr(gemini_embeddings, "GeminiEmbeddingProvider", provider_class)
    monkeypatch.setattr(postgres_repository, "PostgresRepository", repository_class)
    app = _app("production")

    first_result = get_retrieval_dependencies(app)
    second_result = get_retrieval_dependencies(app)

    assert first_result == (provider, repository)
    assert second_result is first_result
    provider_class.assert_called_once_with()
    repository_class.assert_called_once_with()
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "postgresql://example/database"


def test_unsupported_environment_raises_clear_configuration_error():
    app = _app("staging")

    with pytest.raises(
        RetrievalConfigurationError,
        match="Unsupported APP_ENV value 'staging'.*local.*production",
    ):
        get_retrieval_dependencies(app)


def test_unsupported_environment_does_not_import_or_create_dependencies(monkeypatch):
    app = _app("test")

    with pytest.raises(RetrievalConfigurationError):
        get_retrieval_dependencies(app)

    assert "book_recommender_retrieval" not in app.extensions
