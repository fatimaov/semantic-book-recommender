import os
from typing import Any

from sqlalchemy import select

from ..extensions import db
from ..models import Book, BookEmbedding
from . import serialize_book, validate_search_arguments


class PostgresRepository:
    """Retrieve Gemini embedding matches and their related book records."""

    def __init__(self, model_name: str | None = None, session=None) -> None:
        self.model_name = model_name or os.getenv("GEMINI_EMBEDDING_MODEL")
        if not self.model_name:
            raise ValueError("GEMINI_EMBEDDING_MODEL must be configured.")
        self.session = session

    def search_similar(
        self, query_vector: list[float], top_k: int = 250
    ) -> list[dict[str, Any]]:
        vector = validate_search_arguments(query_vector, top_k)
        distance = BookEmbedding.embedding.cosine_distance(vector)
        similarity = (1.0 - distance).label("similarity_score")
        statement = (
            select(Book, similarity)
            .join(BookEmbedding, BookEmbedding.book_id == Book.id)
            .where(BookEmbedding.model == self.model_name)
            .order_by(distance.asc())
            .limit(top_k)
        )

        session = self.session if self.session is not None else db.session
        rows = session.execute(statement).all()
        return [
            serialize_book(book, similarity_score)
            for book, similarity_score in rows
        ]
