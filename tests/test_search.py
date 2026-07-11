"""P2.3: search_guidelines retrieves grounded passages for a query.

The embedding call is injected as `embed_fn` so this is testable without
network access; `scripts/index_guidelines.py` proves the real embedding
model end to end.
"""

import pytest

from loan_intake_agent.schema import Passages
from loan_intake_agent.search import GuidelineIndex, search_guidelines

GUIDELINES_TEXT = (
    "# Title\n\n"
    "> Disclaimer.\n\n"
    "## 1. Loan-to-Value (LTV)\n\n"
    "**Rule 1.1 — Maximum LTV.** LTV must not exceed 80%.\n\n"
    "## 2. Debt-to-Income (DTI)\n\n"
    "**Rule 2.1 — Maximum DTI.** DTI must not exceed 43%.\n\n"
    "## 3. Completeness\n\n"
    "**Rule 3.1 — Required sections.** All four sections are required.\n"
)

# One-hot vectors keyed by rule id, so a query vector can deterministically
# target a specific rule without a real embedding model.
_VECTORS_BY_RULE_ID = {
    "1.1": [1.0, 0.0, 0.0],
    "2.1": [0.0, 1.0, 0.0],
    "3.1": [0.0, 0.0, 1.0],
}


def _fake_embed_fn(vectors_by_text):
    async def embed_fn(texts: list[str]) -> list[list[float]]:
        return [vectors_by_text[text] for text in texts]

    return embed_fn


async def _build_index() -> GuidelineIndex:
    from loan_intake_agent.chunking import chunk_guidelines

    chunks = chunk_guidelines(GUIDELINES_TEXT)
    vectors_by_text = {c.text: _VECTORS_BY_RULE_ID[c.id] for c in chunks}
    embed_fn = _fake_embed_fn(vectors_by_text)
    return await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=embed_fn)


@pytest.mark.anyio
async def test_search_returns_the_matching_rule_as_top_passage():
    index = await _build_index()

    async def query_embed_fn(texts: list[str]) -> list[list[float]]:
        assert texts == ["what's the max LTV?"]
        return [[1.0, 0.0, 0.0]]

    index._embed_fn = query_embed_fn  # simulate the query embedding independently of corpus text

    passages = await index.search("what's the max LTV?", top_k=1)

    assert isinstance(passages, Passages)
    assert passages.items[0].id == "1.1"
    assert "80%" in passages.items[0].text


@pytest.mark.anyio
async def test_search_orders_passages_by_relevance():
    index = await _build_index()

    async def query_embed_fn(texts: list[str]) -> list[list[float]]:
        return [[0.0, 0.9, 0.1]]

    index._embed_fn = query_embed_fn

    passages = await index.search("dti question", top_k=3)

    assert [p.id for p in passages.items] == ["2.1", "3.1", "1.1"]


@pytest.mark.anyio
async def test_search_guidelines_tool_function_delegates_to_index():
    index = await _build_index()

    async def query_embed_fn(texts: list[str]) -> list[list[float]]:
        return [[0.0, 0.0, 1.0]]

    index._embed_fn = query_embed_fn

    passages = await search_guidelines("what sections are required?", index)

    assert passages.items[0].id == "3.1"


@pytest.mark.anyio
async def test_search_on_index_with_no_matches_returns_empty_passages():
    from loan_intake_agent.vector_store import VectorStore

    index = GuidelineIndex(store=VectorStore(), embed_fn=_fake_embed_fn({}))

    async def query_embed_fn(texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0, 0.0]]

    index._embed_fn = query_embed_fn

    passages = await index.search("anything", top_k=3)

    assert passages.items == []
