from typing import Any

from flask import Flask


_EXTENSION_KEY = "book_recommender_retrieval"


class RetrievalConfigurationError(ValueError):
    """Raised when APP_ENV does not select a supported retrieval setup."""


def get_retrieval_dependencies(app: Flask) -> tuple[Any, Any]:
    """Return the app's cached embedding provider and vector repository.

    Dependencies are initialized on first use and stored on the Flask app, so
    requests reuse them without making app startup depend on retrieval assets.
    """
    cached_dependencies = app.extensions.get(_EXTENSION_KEY)
    if cached_dependencies is not None:
        return cached_dependencies

    app_env = str(app.config.get("APP_ENV", "")).strip().lower()
    if app_env == "local":
        from ..providers.huggingface_embeddings import HuggingFaceEmbeddingProvider
        from ..repositories.chroma_repository import ChromaRepository

        dependencies = (HuggingFaceEmbeddingProvider(), ChromaRepository())
    elif app_env == "production":
        from ..providers.gemini_embeddings import GeminiEmbeddingProvider
        from ..repositories.postgres_repository import PostgresRepository

        dependencies = (GeminiEmbeddingProvider(), PostgresRepository())
    else:
        raise RetrievalConfigurationError(
            f"Unsupported APP_ENV value {app_env!r}. "
            "Expected 'local' or 'production'."
        )

    app.extensions[_EXTENSION_KEY] = dependencies
    return dependencies
