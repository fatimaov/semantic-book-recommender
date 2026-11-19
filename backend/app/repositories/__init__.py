import math
from collections.abc import Mapping, Sequence
from enum import Enum
from typing import Any


EMBEDDING_DIMENSIONS = 768
BOOK_RESULT_FIELDS = (
    "isbn13",
    "title_and_subtitle",
    "authors",
    "thumbnail",
    "description",
    "simple_categories",
    "published_year",
    "average_rating",
    "anger",
    "disgust",
    "fear",
    "joy",
    "sadness",
    "surprise",
    "neutral",
)


def validate_search_arguments(
    query_vector: Sequence[float], top_k: int
) -> list[float]:
    if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer.")
    if isinstance(query_vector, (str, bytes)) or len(query_vector) != EMBEDDING_DIMENSIONS:
        raise ValueError(
            f"query_vector must contain exactly {EMBEDDING_DIMENSIONS} values."
        )

    vector = [float(value) for value in query_vector]
    if not all(math.isfinite(value) for value in vector):
        raise ValueError("query_vector values must be finite numbers.")
    return vector


def serialize_book(book: Any, similarity_score: float) -> dict[str, Any]:
    """Return the shared candidate shape for ORM objects and CSV row mappings."""
    result = {}
    for field in BOOK_RESULT_FIELDS:
        value = book.get(field) if isinstance(book, Mapping) else getattr(book, field)
        if isinstance(value, Enum):
            value = value.value
        elif isinstance(value, float) and not math.isfinite(value):
            value = None
        result[field] = value

    result["similarity_score"] = float(similarity_score)
    return result
