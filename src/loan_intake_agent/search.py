"""P2.3: search_guidelines — retrieval over the embedded guideline corpus.

The embedding call is injected as an `EmbedFn` rather than hard-wired to a
live client, so `GuidelineIndex` is testable without network access. The
default (no `embed_fn` given) uses the real Foundry embedding client.
"""

from collections.abc import Awaitable, Callable
from pathlib import Path

from .chunking import chunk_guidelines
from .embeddings import build_embedding_client, embed_texts
from .schema import Passage, Passages
from .vector_store import VectorStore

DEFAULT_GUIDELINES_PATH = Path(__file__).parent.parent.parent / "fixtures" / "guidelines" / "underwriting_guidelines.md"

EmbedFn = Callable[[list[str]], Awaitable[list[list[float]]]]


class GuidelineIndex:
    def __init__(self, store: VectorStore, embed_fn: EmbedFn) -> None:
        self._store = store
        self._embed_fn = embed_fn

    @classmethod
    async def build(
        cls,
        path: Path = DEFAULT_GUIDELINES_PATH,
        text: str | None = None,
        embed_fn: EmbedFn | None = None,
    ) -> "GuidelineIndex":
        if embed_fn is None:
            client = build_embedding_client()

            async def embed_fn(texts: list[str]) -> list[list[float]]:
                return await embed_texts(client, texts)

        corpus_text = text if text is not None else path.read_text(encoding="utf-8")
        chunks = chunk_guidelines(corpus_text)

        store = VectorStore()
        if chunks:
            vectors = await embed_fn([c.text for c in chunks])
            store.add(chunks, vectors)

        return cls(store, embed_fn)

    async def search(self, query: str, top_k: int = 3) -> Passages:
        [query_vector] = await self._embed_fn([query])
        results = self._store.query(query_vector, top_k=top_k)
        return Passages(
            items=[
                Passage(id=r.chunk.id, section=r.chunk.section, text=r.chunk.text, score=r.score)
                for r in results
            ]
        )


async def search_guidelines(query: str, index: GuidelineIndex) -> Passages:
    """The FR4 tool: retrieval over the guideline corpus, grounded in the indexed passages."""
    return await index.search(query)
