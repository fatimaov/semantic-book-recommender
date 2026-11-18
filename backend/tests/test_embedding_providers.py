from unittest.mock import patch

import pytest

from backend.app.providers.gemini_embeddings import GeminiEmbeddingProvider
from backend.app.providers.huggingface_embeddings import HuggingFaceEmbeddingProvider


def _sample_embedding() -> list[float]:
    return [0.1] * 768


@patch("backend.app.providers.huggingface_embeddings.HuggingFaceEmbeddings")
def test_huggingface_provider_uses_expected_model_and_embeds_query(
    embeddings_class,
):
    expected_embedding = _sample_embedding()
    embeddings_class.return_value.embed_query.return_value = expected_embedding

    provider = HuggingFaceEmbeddingProvider()
    result = provider.embed_query("A story about friendship")

    embeddings_class.assert_called_once_with(model_name="BAAI/bge-base-en-v1.5")
    embeddings_class.return_value.embed_query.assert_called_once_with(
        "A story about friendship"
    )
    assert isinstance(result, list)
    assert len(result) == 768
    assert result == expected_embedding


@patch("backend.app.providers.gemini_embeddings.GoogleGenerativeAIEmbeddings")
def test_gemini_provider_uses_query_settings_and_embeds_query(
    embeddings_class, monkeypatch
):
    expected_embedding = _sample_embedding()
    embeddings_class.return_value.embed_query.return_value = expected_embedding
    monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")

    provider = GeminiEmbeddingProvider()
    result = provider.embed_query("A story about personal growth")

    embeddings_class.assert_called_once_with(
        model="gemini-embedding-2",
        task_type="RETRIEVAL_QUERY",
        output_dimensionality=768,
    )
    embeddings_class.return_value.embed_query.assert_called_once_with(
        "A story about personal growth"
    )
    assert isinstance(result, list)
    assert len(result) == 768
    assert result == expected_embedding


def test_gemini_provider_requires_model_configuration(monkeypatch):
    monkeypatch.delenv("GEMINI_EMBEDDING_MODEL", raising=False)

    with pytest.raises(
        ValueError, match="GEMINI_EMBEDDING_MODEL must be configured"
    ):
        GeminiEmbeddingProvider()
