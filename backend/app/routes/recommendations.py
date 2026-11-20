from flask import Blueprint, current_app, jsonify, request
from chromadb.errors import ChromaError
from google.genai.errors import APIError as GeminiAPIError
from httpx import HTTPError as HttpClientError
from langchain_google_genai._common import GoogleGenerativeAIError
from sqlalchemy.exc import SQLAlchemyError

from ..factories import get_retrieval_dependencies
from ..models.enums import BookCategory
from ..services.recommendation_service import RecommendationService, SUPPORTED_TONES
from ..services.search_event_service import SearchEventService


recommendations = Blueprint("recommendations", __name__, url_prefix="/api")

DEFAULT_TOP_K = 250
MAX_TOP_K = 250
_RECOMMENDATION_SERVICE_KEY = "book_recommender_recommendation_service"
API_EMOTIONS = frozenset(
    {"All", "Anger", "Disgust", "Fear", "Joy", "Sadness", "Surprise", "Neutral"}
)
EMOTIONS = API_EMOTIONS | SUPPORTED_TONES
CATEGORIES = frozenset({"All", *(category.value for category in BookCategory)})
DEPENDENCY_ERRORS = (
    ChromaError,
    GeminiAPIError,
    GoogleGenerativeAIError,
    HttpClientError,
    SQLAlchemyError,
    ConnectionError,
    TimeoutError,
    OSError,
)


def _error(message: str, status_code: int):
    return jsonify(error={"message": message}), status_code


def _get_recommendation_service() -> RecommendationService:
    app = current_app._get_current_object()
    service = app.extensions.get(_RECOMMENDATION_SERVICE_KEY)
    if service is None:
        provider, book_repository = get_retrieval_dependencies(app)
        service = RecommendationService(provider, book_repository)
        app.extensions[_RECOMMENDATION_SERVICE_KEY] = service
    return service


@recommendations.post("/recommendations")
def create_recommendations():
    if not request.is_json:
        return _error("Content-Type must be application/json.", 400)

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
            "'emotion' must be 'All' or a supported emotion or tone label.",
            400,
        )

    if current_app.config.get("SEARCH_LOGGING_ENABLED", False):
        try:
            SearchEventService().log_search(
                query=query.strip(),
                category=category,
                emotion=emotion,
            )
        except Exception:
            current_app.logger.exception("Search analytics logging failed.")

    try:
        books = _get_recommendation_service().recommend(
            query=query,
            category=category,
            emotion=emotion,
            top_k=top_k,
        )
        response = jsonify(recommendations=books, total=len(books))
    except DEPENDENCY_ERRORS:
        current_app.logger.exception("Recommendation request failed.")
        return _error("Recommendations are temporarily unavailable.", 503)
    except Exception:
        current_app.logger.exception("Unexpected recommendation request failure.")
        return _error("An unexpected error occurred.", 500)

    return response, 200
