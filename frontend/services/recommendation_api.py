"""Client for the Flask book recommendation endpoint."""

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


RECOMMENDATIONS_PATH = "/api/recommendations"
REQUEST_TIMEOUT = (5, 60)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


class RecommendationAPIError(RuntimeError):
    """Raised when the Flask API cannot return a valid recommendation list."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _http_error_message(response: requests.Response) -> str:
    """Return a safe message from the API error body when one is available."""
    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError:
        body = None

    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if isinstance(message, str) and message.strip():
                return message
        if isinstance(error, str) and error.strip():
            return error

    return f"The Flask API returned HTTP {response.status_code}."


def fetch_recommendations(
    query: str,
    top_k: int = 250,
    category: str = "All",
    emotion: str = "All",
    *,
    timeout: tuple[float, float] = REQUEST_TIMEOUT,
) -> list[dict[str, Any]]:
    """Request recommendations and return the validated book records.

    The base URL comes from ``FLASK_API_URL`` in the environment or project
    ``.env`` file.
    """
    base_url = os.getenv("FLASK_API_URL", "").strip()
    if not base_url:
        raise RecommendationAPIError("Set FLASK_API_URL to the Flask API base URL.")

    endpoint = f"{base_url.rstrip('/')}{RECOMMENDATIONS_PATH}"
    payload = {
        "query": query,
        "top_k": top_k,
        "category": category,
        "emotion": emotion,
    }

    try:
        response = requests.post(endpoint, json=payload, timeout=timeout)
    except requests.exceptions.Timeout as error:
        raise RecommendationAPIError("The Flask API request timed out.") from error
    except requests.exceptions.ConnectionError as error:
        raise RecommendationAPIError(
            "Could not connect to the Flask API. Check that the server is running "
            "and FLASK_API_URL is correct."
        ) from error
    except requests.exceptions.RequestException as error:
        raise RecommendationAPIError(f"Could not reach the Flask API: {error}") from error

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        raise RecommendationAPIError(
            _http_error_message(response), status_code=response.status_code
        ) from error

    try:
        body = response.json()
    except requests.exceptions.JSONDecodeError as error:
        raise RecommendationAPIError(
            "The Flask API returned a response that was not valid JSON."
        ) from error

    if not isinstance(body, dict):
        raise RecommendationAPIError("The Flask API response must be a JSON object.")

    books = body.get("recommendations")
    total = body.get("total")
    if not isinstance(books, list) or any(not isinstance(book, dict) for book in books):
        raise RecommendationAPIError(
            "The Flask API response must contain a list of book objects in "
            "'recommendations'."
        )
    if isinstance(total, bool) or not isinstance(total, int) or total != len(books):
        raise RecommendationAPIError(
            "The Flask API response contains an invalid 'total' value."
        )

    return books
