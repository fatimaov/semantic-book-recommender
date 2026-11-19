from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest
from sqlalchemy.dialects import postgresql

from backend.app.models.enums import BookCategory
from backend.app.repositories import chroma_repository
from backend.app.repositories.chroma_repository import ChromaRepository
from backend.app.repositories.postgres_repository import PostgresRepository


def _csv_book(isbn13: str = "9780141439518") -> dict:
    return {
        "isbn13": isbn13,
        "title_and_subtitle": "Pride and Prejudice",
        "authors": "Jane Austen",
        "thumbnail": "https://example.com/cover.jpg",
        "description": "A novel about love and social expectations.",
        "simple_categories": "Fiction",
        "published_year": 1813,
        "average_rating": 4.3,
        "anger": 0.02,
        "disgust": 0.01,
        "fear": 0.05,
        "joy": 0.62,
        "sadness": 0.18,
        "surprise": 0.07,
        "neutral": 0.05,
    }


def _orm_book():
    book = _csv_book()
    book["simple_categories"] = BookCategory.FICTION
    return SimpleNamespace(**book)


def test_chroma_repository_searches_with_vector_and_maps_isbn_to_csv(
    monkeypatch, tmp_path
):
    vector_store = Mock()
    vector_store.similarity_search_by_vector_with_relevance_scores.return_value = [
        (SimpleNamespace(page_content="9780141439518 Pride and Prejudice"), 0.91),
        (SimpleNamespace(page_content='"9780000000000 Unknown book"'), 0.82),
    ]
    chroma_constructor = Mock(return_value=vector_store)
    monkeypatch.setattr(chroma_repository, "Chroma", chroma_constructor)
    monkeypatch.setattr(chroma_repository, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        chroma_repository.pd,
        "read_csv",
        Mock(return_value=pd.DataFrame([_csv_book()])),
    )
    monkeypatch.setenv("CHROMA_PERSIST_DIRECTORY", "vector-data")
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "books-test")

    repository = ChromaRepository()
    query_vector = [0.25] * 768
    results = repository.search_similar(query_vector, top_k=10)

    chroma_constructor.assert_called_once_with(
        collection_name="books-test",
        persist_directory=str(tmp_path / "vector-data"),
        embedding_function=None,
    )
    vector_store.similarity_search_by_vector_with_relevance_scores.assert_called_once_with(
        embedding=query_vector,
        k=10,
    )
    assert len(results) == 1
    assert results[0]["isbn13"] == "9780141439518"
    assert results[0]["title_and_subtitle"] == "Pride and Prejudice"
    assert results[0]["similarity_score"] == 0.91


def test_chroma_repository_rejects_invalid_vector_before_search(monkeypatch, tmp_path):
    vector_store = Mock()
    monkeypatch.setattr(
        chroma_repository, "Chroma", Mock(return_value=vector_store)
    )
    monkeypatch.setattr(chroma_repository, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(
        chroma_repository.pd,
        "read_csv",
        Mock(return_value=pd.DataFrame([_csv_book()])),
    )

    repository = ChromaRepository()

    with pytest.raises(ValueError, match="exactly 768 values"):
        repository.search_similar([0.1, 0.2])

    vector_store.similarity_search_by_vector_with_relevance_scores.assert_not_called()


def test_postgres_repository_builds_cosine_search_for_configured_model(monkeypatch):
    session = Mock()
    session.execute.return_value.all.return_value = [(_orm_book(), 0.89)]
    monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")

    repository = PostgresRepository(session=session)
    query_vector = [0.15] * 768
    results = repository.search_similar(query_vector, top_k=5)

    statement = session.execute.call_args.args[0]
    compiled = statement.compile(dialect=postgresql.dialect())
    sql = str(compiled)

    assert "FROM books JOIN book_embeddings" in sql
    assert "book_embeddings.embedding <=>" in sql
    assert "book_embeddings.model" in sql
    assert "gemini-embedding-2" in compiled.params.values()
    assert statement._limit_clause.value == 5
    assert results[0]["simple_categories"] == "Fiction"
    assert results[0]["similarity_score"] == 0.89


def test_postgres_repository_rejects_invalid_top_k_before_query():
    session = Mock()
    repository = PostgresRepository(model_name="gemini-embedding-2", session=session)

    with pytest.raises(ValueError, match="top_k must be a positive integer"):
        repository.search_similar([0.1] * 768, top_k=0)

    session.execute.assert_not_called()
