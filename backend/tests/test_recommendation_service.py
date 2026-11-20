from unittest.mock import Mock

import pytest

from backend.app.services.recommendation_service import RecommendationService


@pytest.fixture
def retrieval():
    provider = Mock()
    provider.embed_query.return_value = [0.1, 0.2, 0.3]
    repository = Mock()
    service = RecommendationService(provider, repository)
    return service, provider, repository


def _book(title, category="Fiction", **scores):
    return {
        "title_and_subtitle": title,
        "simple_categories": category,
        "similarity_score": 0.9,
        **scores,
    }


def test_recommend_embeds_query_and_requests_candidates(retrieval):
    service, provider, repository = retrieval
    candidates = [_book("Book A")]
    repository.search_similar.return_value = candidates

    result = service.recommend("  a friendship story  ")

    provider.embed_query.assert_called_once_with("a friendship story")
    repository.search_similar.assert_called_once_with(
        query_vector=[0.1, 0.2, 0.3],
        top_k=250,
    )
    assert result == candidates


def test_category_filter_preserves_semantic_order(retrieval):
    service, _, repository = retrieval
    repository.search_similar.return_value = [
        _book("First fiction"),
        _book("Nonfiction", category="Nonfiction"),
        _book("Second fiction"),
    ]

    result = service.recommend("query", category="Fiction")

    assert [book["title_and_subtitle"] for book in result] == [
        "First fiction",
        "Second fiction",
    ]


@pytest.mark.parametrize(
    ("tone", "score_field"),
    [
        ("Happy", "joy"),
        ("Surprising", "surprise"),
        ("Angry", "anger"),
        ("Suspenseful", "fear"),
        ("Sad", "sadness"),
    ],
)
def test_selected_tone_ranks_by_matching_score_and_puts_missing_scores_last(
    retrieval, tone, score_field
):
    service, _, repository = retrieval
    repository.search_similar.return_value = [
        _book("Lower", **{score_field: 0.2}),
        _book("Missing"),
        _book("Higher", **{score_field: 0.8}),
    ]

    result = service.recommend("query", emotion=tone)

    assert [book["title_and_subtitle"] for book in result] == [
        "Higher",
        "Lower",
        "Missing",
    ]


def test_all_category_and_tone_keep_repository_order(retrieval):
    service, _, repository = retrieval
    candidates = [
        _book("First", joy=0.1),
        _book("Second", joy=0.9),
    ]
    repository.search_similar.return_value = candidates

    result = service.recommend("query", category="All", emotion="All")

    assert result == candidates


def test_returns_at_most_limit_recommendations(retrieval):
    service, _, repository = retrieval
    repository.search_similar.return_value = [_book(str(index)) for index in range(20)]

    result = service.recommend("query", limit=16)

    assert len(result) == 16


@pytest.mark.parametrize("candidates", [[], [_book("One"), _book("Two")]])
def test_handles_empty_or_short_candidate_lists(retrieval, candidates):
    service, _, repository = retrieval
    repository.search_similar.return_value = candidates

    result = service.recommend("query")

    assert result == candidates


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"query": "  "}, "query must be a non-empty string"),
        ({"query": "query", "top_k": 0}, "top_k must be a positive integer"),
        ({"query": "query", "limit": 0}, "limit must be a positive integer"),
        ({"query": "query", "emotion": "Joy"}, "emotion must be 'All'"),
    ],
)
def test_rejects_invalid_service_arguments(retrieval, kwargs, message):
    service, provider, repository = retrieval

    with pytest.raises(ValueError, match=message):
        service.recommend(**kwargs)

    provider.embed_query.assert_not_called()
    repository.search_similar.assert_not_called()
