"""P2.2: VectorStore indexes chunks by embedding and returns the closest match by cosine similarity."""

import pytest

from loan_intake_agent.schema import Chunk
from loan_intake_agent.vector_store import VectorStore


def _chunk(id_: str, text: str) -> Chunk:
    return Chunk(id=id_, section="S", text=text)


def test_query_returns_the_closest_vector_first():
    store = VectorStore()
    store.add([_chunk("a", "apple banana"), _chunk("b", "car truck")], [[1.0, 0.0], [0.0, 1.0]])

    results = store.query([0.9, 0.1], top_k=1)

    assert results[0].chunk.id == "a"


def test_query_orders_multiple_results_by_descending_similarity():
    store = VectorStore()
    store.add(
        [_chunk("a", "x"), _chunk("b", "y"), _chunk("c", "z")],
        [[1.0, 0.0], [0.0, 1.0], [0.7, 0.7]],
    )

    results = store.query([1.0, 0.0], top_k=3)

    assert [r.chunk.id for r in results] == ["a", "c", "b"]


def test_query_respects_top_k():
    store = VectorStore()
    store.add([_chunk("a", "x"), _chunk("b", "y")], [[1.0, 0.0], [0.0, 1.0]])

    results = store.query([1.0, 0.0], top_k=1)

    assert len(results) == 1


def test_query_score_is_highest_for_identical_vector():
    store = VectorStore()
    store.add([_chunk("a", "x")], [[1.0, 2.0, 3.0]])

    results = store.query([1.0, 2.0, 3.0], top_k=1)

    assert results[0].score == pytest.approx(1.0)


def test_add_requires_matching_chunk_and_vector_counts():
    store = VectorStore()

    with pytest.raises(ValueError):
        store.add([_chunk("a", "x"), _chunk("b", "y")], [[1.0, 0.0]])


def test_query_on_empty_store_returns_empty_list():
    store = VectorStore()

    assert store.query([1.0, 0.0], top_k=3) == []
