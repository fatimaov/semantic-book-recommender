from importlib import import_module
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from backend.app import create_app
from backend.app.services.recommendation_service import RecommendationService


recommendations_module = import_module("backend.app.routes.recommendations")
RESPONSE_FIELDS = {
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
    "similarity_score",
}


@pytest.fixture
def client_factory():
    def make_client(app_env="local"):
        app = create_app(
            {
                "TESTING": True,
                "APP_ENV": app_env,
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
            }
        )
        return app.test_client()

    return make_client


def _book(title):
    return {
        "isbn13": "9780000000000",
        "title_and_subtitle": title,
        "authors": "Test Author",
        "thumbnail": None,
        "description": "Test description",
        "simple_categories": "Fiction",
        "published_year": 2020,
        "average_rating": 4.2,
        "anger": 0.01,
        "disgust": 0.02,
        "fear": 0.03,
        "joy": 0.8,
        "sadness": 0.04,
        "surprise": 0.05,
        "neutral": 0.05,
        "similarity_score": 0.91,
    }


def _patch_service(monkeypatch, service):
    provider = object()
    repository = object()
    dependencies = Mock(return_value=(provider, repository))
    service_class = Mock(return_value=service)
    monkeypatch.setattr(
        recommendations_module, "get_retrieval_dependencies", dependencies
    )
    monkeypatch.setattr(recommendations_module, "RecommendationService", service_class)
    return dependencies, service_class, provider, repository


def test_valid_request_returns_expected_json_and_uses_defaults(
    client_factory, monkeypatch
):
    book = _book("Book")
    service = Mock()
    service.recommend.return_value = [book]
    dependencies, service_class, provider, repository = _patch_service(
        monkeypatch, service
    )
    client = client_factory()

    response = client.post("/api/recommendations", json={"query": "a query"})

    assert response.status_code == 200
    assert response.get_json() == {"recommendations": [book], "total": 1}
    assert set(response.get_json()["recommendations"][0]) == RESPONSE_FIELDS
    service.recommend.assert_called_once_with(
        query="a query", category="All", emotion="All", top_k=250
    )
    service_class.assert_called_once_with(provider, repository)
    dependencies.assert_called_once()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"query": ""},
        {"query": "   "},
        {"query": 123},
        {"query": "query", "top_k": True},
        {"query": "query", "top_k": "10"},
        {"query": "query", "top_k": 0},
        {"query": "query", "top_k": 251},
        {"query": "query", "category": "Unknown"},
        {"query": "query", "emotion": "Unknown"},
    ],
)
def test_invalid_payload_returns_400_without_initializing_services(
    client_factory, monkeypatch, payload
):
    dependency_factory = Mock()
    event_logger = Mock()
    monkeypatch.setattr(
        recommendations_module, "get_retrieval_dependencies", dependency_factory
    )
    monkeypatch.setattr(
        recommendations_module,
        "SearchEventService",
        Mock(return_value=event_logger),
    )
    response = client_factory("production").post(
        "/api/recommendations", json=payload
    )

    assert response.status_code == 400
    dependency_factory.assert_not_called()
    event_logger.log_search.assert_not_called()


def test_non_json_and_malformed_json_requests_return_400(client_factory):
    client = client_factory()

    non_json = client.post("/api/recommendations", data="query=text")
    malformed_json = client.post(
        "/api/recommendations",
        data='{"query":',
        content_type="application/json",
    )

    assert non_json.status_code == 400
    assert malformed_json.status_code == 400


def test_empty_results_return_200_with_empty_recommendation_list(
    client_factory, monkeypatch
):
    service = Mock()
    service.recommend.return_value = []
    _patch_service(monkeypatch, service)

    response = client_factory().post("/api/recommendations", json={"query": "query"})

    assert response.status_code == 200
    assert response.get_json() == {"recommendations": [], "total": 0}


@pytest.mark.parametrize(
    "emotion",
    ["Anger", "Disgust", "Fear", "Joy", "Sadness", "Surprise", "Neutral"],
)
def test_accepts_each_supported_emotion(client_factory, monkeypatch, emotion):
    service = Mock()
    service.recommend.return_value = []
    _patch_service(monkeypatch, service)

    response = client_factory().post(
        "/api/recommendations",
        json={"query": "query", "emotion": emotion},
    )

    assert response.status_code == 200
    service.recommend.assert_called_once_with(
        query="query", category="All", emotion=emotion, top_k=250
    )


def test_endpoint_returns_no_more_than_16_recommendations(
    client_factory, monkeypatch
):
    provider = Mock()
    provider.embed_query.return_value = [0.0] * 768
    repository = Mock()
    repository.search_similar.return_value = [_book(str(index)) for index in range(30)]
    monkeypatch.setattr(
        recommendations_module,
        "get_retrieval_dependencies",
        Mock(return_value=(provider, repository)),
    )

    response = client_factory().post("/api/recommendations", json={"query": "query"})

    assert response.status_code == 200
    assert response.get_json()["total"] == 16
    assert len(response.get_json()["recommendations"]) == 16
    repository.search_similar.assert_called_once_with(
        query_vector=[0.0] * 768,
        top_k=250,
    )


@pytest.mark.parametrize(
    ("exception", "expected_status"),
    [
        (SQLAlchemyError("database unavailable"), 503),
        (ConnectionError("provider unavailable"), 503),
        (RuntimeError("sensitive internal detail"), 500),
    ],
)
def test_service_failures_return_safe_status_and_message(
    client_factory, monkeypatch, exception, expected_status
):
    service = Mock()
    service.recommend.side_effect = exception
    _patch_service(monkeypatch, service)

    response = client_factory().post("/api/recommendations", json={"query": "query"})

    assert response.status_code == expected_status
    assert "sensitive internal detail" not in response.get_data(as_text=True)
    assert "database unavailable" not in response.get_data(as_text=True)
