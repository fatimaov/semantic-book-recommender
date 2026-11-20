from importlib import import_module
from unittest.mock import Mock

import pytest

from backend.app import create_app
from backend.app.services.search_event_service import SearchEventService


search_event_module = import_module("backend.app.services.search_event_service")
recommendations_module = import_module("backend.app.routes.recommendations")


@pytest.fixture
def app_factory():
    def make_app(app_env):
        return create_app(
            {
                "TESTING": True,
                "APP_ENV": app_env,
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
            }
        )

    return make_app


def test_log_search_adds_and_commits_a_new_event(monkeypatch):
    session = Mock()
    event = object()
    event_factory = Mock(return_value=event)
    monkeypatch.setattr(search_event_module, "SearchEvent", event_factory)
    service = SearchEventService(session=session)

    result = service.log_search("friendship and adventure", "Fiction", "Happy")

    assert result is True
    event_factory.assert_called_once_with(
        query="friendship and adventure",
        category="Fiction",
        emotion="Happy",
    )
    session.add.assert_called_once_with(event)
    session.commit.assert_called_once_with()
    session.rollback.assert_not_called()


def test_log_search_rolls_back_and_returns_false_when_commit_fails(caplog):
    session = Mock()
    session.commit.side_effect = RuntimeError("database unavailable")
    service = SearchEventService(session=session)

    result = service.log_search("query", "All", "All")

    assert result is False
    session.add.assert_called_once()
    session.rollback.assert_called_once_with()
    assert "Could not persist search event" in caplog.text


def test_app_enables_logging_only_for_production(app_factory):
    production_app = app_factory("production")
    local_app = app_factory("local")

    assert production_app.config["SEARCH_LOGGING_ENABLED"] is True
    assert local_app.config["SEARCH_LOGGING_ENABLED"] is False


def _mock_recommendation_dependencies(monkeypatch):
    provider = object()
    repository = object()
    dependency_factory = Mock(return_value=(provider, repository))
    recommendation_service = Mock()
    recommendation_service.recommend.return_value = [{"title_and_subtitle": "Book"}]
    recommendation_service_class = Mock(return_value=recommendation_service)

    monkeypatch.setattr(
        recommendations_module, "get_retrieval_dependencies", dependency_factory
    )
    monkeypatch.setattr(
        recommendations_module,
        "RecommendationService",
        recommendation_service_class,
    )
    return dependency_factory, recommendation_service_class, recommendation_service


def test_production_route_logs_every_valid_submission_and_reuses_recommender(
    app_factory, monkeypatch
):
    dependency_factory, service_class, service = _mock_recommendation_dependencies(
        monkeypatch
    )
    event_logger = Mock()
    event_service_class = Mock(return_value=event_logger)
    monkeypatch.setattr(
        recommendations_module, "SearchEventService", event_service_class
    )
    client = app_factory("production").test_client()
    payload = {
        "query": "  friendship and adventure  ",
        "category": "Fiction",
        "emotion": "Happy",
    }

    first_response = client.post("/api/recommendations", json=payload)
    second_response = client.post("/api/recommendations", json=payload)

    assert first_response.status_code == second_response.status_code == 200
    assert first_response.get_json() == {
        "recommendations": [{"title_and_subtitle": "Book"}],
        "total": 1,
    }
    assert event_logger.log_search.call_count == 2
    event_logger.log_search.assert_called_with(
        query="friendship and adventure",
        category="Fiction",
        emotion="Happy",
    )
    assert dependency_factory.call_count == 1
    service_class.assert_called_once_with(*dependency_factory.return_value)
    assert service.recommend.call_count == 2


def test_local_route_skips_search_event_logging(app_factory, monkeypatch):
    _mock_recommendation_dependencies(monkeypatch)
    event_service_class = Mock()
    monkeypatch.setattr(
        recommendations_module, "SearchEventService", event_service_class
    )
    client = app_factory("local").test_client()

    response = client.post("/api/recommendations", json={"query": "query"})

    assert response.status_code == 200
    event_service_class.assert_not_called()


def test_search_logging_failure_does_not_fail_recommendations(app_factory, monkeypatch):
    _mock_recommendation_dependencies(monkeypatch)
    event_logger = Mock()
    event_logger.log_search.return_value = False
    monkeypatch.setattr(
        recommendations_module,
        "SearchEventService",
        Mock(return_value=event_logger),
    )
    client = app_factory("production").test_client()

    response = client.post("/api/recommendations", json={"query": "query"})

    assert response.status_code == 200
    assert response.get_json()["total"] == 1
    event_logger.log_search.assert_called_once()


def test_search_event_service_initialization_failure_does_not_fail_recommendations(
    app_factory, monkeypatch
):
    _mock_recommendation_dependencies(monkeypatch)
    monkeypatch.setattr(
        recommendations_module,
        "SearchEventService",
        Mock(side_effect=RuntimeError("database session unavailable")),
    )
    client = app_factory("production").test_client()

    response = client.post("/api/recommendations", json={"query": "query"})

    assert response.status_code == 200
    assert response.get_json()["total"] == 1


@pytest.mark.parametrize("invalid_payload", [{}, {"query": "  "}])
def test_invalid_requests_are_not_logged(app_factory, monkeypatch, invalid_payload):
    event_service_class = Mock()
    monkeypatch.setattr(
        recommendations_module, "SearchEventService", event_service_class
    )
    client = app_factory("production").test_client()

    response = client.post("/api/recommendations", json=invalid_payload)

    assert response.status_code == 400
    event_service_class.assert_not_called()
