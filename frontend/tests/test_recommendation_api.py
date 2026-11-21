from unittest.mock import Mock

import pytest
import requests

from frontend.services import recommendation_api


@pytest.fixture
def api_post(monkeypatch):
    post = Mock()
    monkeypatch.setattr(recommendation_api.requests, "post", post)
    return post


def _response(body):
    response = Mock()
    response.json.return_value = body
    response.raise_for_status.return_value = None
    return response


def test_fetch_recommendations_posts_payload_to_environment_url(api_post, monkeypatch):
    books = [{"title_and_subtitle": "A Test Book"}]
    api_post.return_value = _response({"recommendations": books, "total": 1})
    monkeypatch.setenv("FLASK_API_URL", "https://books.example.test/")

    result = recommendation_api.fetch_recommendations(
        "friendship story", top_k=20, category="Fiction", emotion="Happy"
    )

    assert result == books
    api_post.assert_called_once_with(
        "https://books.example.test/api/recommendations",
        json={
            "query": "friendship story",
            "top_k": 20,
            "category": "Fiction",
            "emotion": "Happy",
        },
        timeout=(5, 60),
    )


def test_fetch_recommendations_requires_environment_url(api_post, monkeypatch):
    monkeypatch.delenv("FLASK_API_URL", raising=False)

    with pytest.raises(
        recommendation_api.RecommendationAPIError,
        match="Set FLASK_API_URL",
    ):
        recommendation_api.fetch_recommendations("friendship story")

    api_post.assert_not_called()


@pytest.mark.parametrize(
    ("request_error", "message"),
    [
        (requests.exceptions.Timeout("timed out"), "request timed out"),
        (requests.exceptions.ConnectionError("offline"), "Could not connect"),
    ],
)
def test_fetch_recommendations_handles_network_errors(
    api_post, monkeypatch, request_error, message
):
    api_post.side_effect = request_error
    monkeypatch.setenv("FLASK_API_URL", "http://127.0.0.1:5000")

    with pytest.raises(recommendation_api.RecommendationAPIError, match=message):
        recommendation_api.fetch_recommendations("friendship story")


def test_fetch_recommendations_includes_api_http_error(api_post, monkeypatch):
    response = _response({"error": {"message": "Invalid category."}})
    response.status_code = 400
    response.raise_for_status.side_effect = requests.exceptions.HTTPError("400")
    api_post.return_value = response
    monkeypatch.setenv("FLASK_API_URL", "http://127.0.0.1:5000")

    with pytest.raises(recommendation_api.RecommendationAPIError) as error:
        recommendation_api.fetch_recommendations("friendship story")

    assert str(error.value) == "Invalid category."
    assert error.value.status_code == 400


def test_fetch_recommendations_rejects_invalid_json(api_post, monkeypatch):
    response = _response(None)
    response.json.side_effect = requests.exceptions.JSONDecodeError(
        "Invalid JSON", "not json", 0
    )
    api_post.return_value = response
    monkeypatch.setenv("FLASK_API_URL", "http://127.0.0.1:5000")

    with pytest.raises(
        recommendation_api.RecommendationAPIError,
        match="not valid JSON",
    ):
        recommendation_api.fetch_recommendations("friendship story")


@pytest.mark.parametrize(
    "body",
    [
        [],
        {"recommendations": None, "total": 0},
        {"recommendations": ["not a book object"], "total": 1},
        {"recommendations": [], "total": 1},
    ],
)
def test_fetch_recommendations_rejects_invalid_response_shape(
    api_post, monkeypatch, body
):
    api_post.return_value = _response(body)
    monkeypatch.setenv("FLASK_API_URL", "http://127.0.0.1:5000")

    with pytest.raises(recommendation_api.RecommendationAPIError):
        recommendation_api.fetch_recommendations("friendship story")
