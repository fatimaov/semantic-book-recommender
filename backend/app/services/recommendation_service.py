import math
from collections.abc import Mapping
from typing import Any


DEFAULT_TOP_K = 250
DEFAULT_LIMIT = 16
TONE_SCORE_FIELDS = {
    "Happy": "joy",
    "Surprising": "surprise",
    "Angry": "anger",
    "Suspenseful": "fear",
    "Sad": "sadness",
}
SUPPORTED_TONES = frozenset({"All", *TONE_SCORE_FIELDS})


class RecommendationService:
    """Coordinate query embedding, semantic retrieval, and recommendation ranking."""

    def __init__(self, embedding_provider: Any, book_repository: Any) -> None:
        self.embedding_provider = embedding_provider
        self.book_repository = book_repository

    def recommend(
        self,
        query: str,
        category: str = "All",
        emotion: str = "All",
        top_k: int = DEFAULT_TOP_K,
        limit: int = DEFAULT_LIMIT,
    ) -> list[dict[str, Any]]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string.")
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
            raise ValueError("top_k must be a positive integer.")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("limit must be a positive integer.")
        if not isinstance(category, str):
            raise ValueError("category must be a string.")
        if not isinstance(emotion, str) or emotion not in SUPPORTED_TONES:
            raise ValueError(
                "emotion must be 'All', 'Happy', 'Surprising', 'Angry', "
                "'Suspenseful', or 'Sad'."
            )

        query_vector = self.embedding_provider.embed_query(query.strip())
        candidates = self.book_repository.search_similar(
            query_vector=query_vector,
            top_k=top_k,
        )

        if category != "All":
            candidates = [
                book
                for book in candidates
                if book.get("simple_categories") == category
            ]

        score_field = TONE_SCORE_FIELDS.get(emotion)
        if score_field is not None:
            candidates = sorted(
                candidates,
                key=lambda book: self._emotion_score_key(book, score_field),
                reverse=True,
            )

        return candidates[:limit]

    @staticmethod
    def _emotion_score_key(book: Mapping[str, Any], score_field: str) -> tuple[int, float]:
        score = book.get(score_field)
        try:
            numeric_score = float(score)
        except (TypeError, ValueError):
            return (0, 0.0)

        if not math.isfinite(numeric_score):
            return (0, 0.0)
        return (1, numeric_score)
