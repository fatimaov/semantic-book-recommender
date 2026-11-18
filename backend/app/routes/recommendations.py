from flask import Blueprint, jsonify, request

from ..models.enums import BookCategory


recommendations = Blueprint("recommendations", __name__, url_prefix="/api")

DEFAULT_TOP_K = 250
MAX_TOP_K = 250
EMOTIONS = frozenset(
    {"All", "Anger", "Disgust", "Fear", "Joy", "Sadness", "Surprise", "Neutral"}
)
CATEGORIES = frozenset({"All", *(category.value for category in BookCategory)})


def _error(message: str, status_code: int):
    return jsonify(error={"message": message}), status_code


@recommendations.post("/recommendations")
def create_recommendations():
    if not request.is_json:
        return _error("Content-Type must be application/json.", 415)

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Request body must be a JSON object.", 400)

    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        return _error("'query' is required and must be a non-empty string.", 400)

    top_k = payload.get("top_k", DEFAULT_TOP_K)
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        return _error("'top_k' must be an integer.", 400)
    if not 1 <= top_k <= MAX_TOP_K:
        return _error(f"'top_k' must be between 1 and {MAX_TOP_K}.", 400)

    category = payload.get("category", "All")
    if not isinstance(category, str) or category not in CATEGORIES:
        return _error(
            "'category' must be 'All' or one of the supported book categories.", 400
        )

    emotion = payload.get("emotion", "All")
    if not isinstance(emotion, str) or emotion not in EMOTIONS:
        return _error(
            "'emotion' must be 'All' or one of the seven supported emotions.", 400
        )

    # The API contract is available now; the recommendation service will be
    # connected in the next implementation step.
    return _error("Recommendation service is not implemented yet.", 501)
