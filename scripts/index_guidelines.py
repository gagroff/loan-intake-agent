"""P2.2 spike: embed the guideline corpus and prove a similarity query returns the right passage.

Run: uv run python scripts/index_guidelines.py
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from loan_intake_agent.chunking import chunk_guidelines
from loan_intake_agent.embeddings import build_embedding_client, embed_texts
from loan_intake_agent.vector_store import VectorStore

GUIDELINES_PATH = Path(__file__).parent.parent / "fixtures" / "guidelines" / "underwriting_guidelines.md"


async def main() -> None:
    load_dotenv()

    chunks = chunk_guidelines(GUIDELINES_PATH.read_text(encoding="utf-8"))
    print(f"Chunked corpus into {len(chunks)} rules.")

    client = build_embedding_client()
    vectors = await embed_texts(client, [c.text for c in chunks])

    store = VectorStore()
    store.add(chunks, vectors)

    query = "What's the maximum loan-to-value ratio allowed?"
    query_vector = (await embed_texts(client, [query]))[0]
    results = store.query(query_vector, top_k=2)

    print(f"\nQuery: {query!r}")
    for r in results:
        print(f"  [{r.score:.3f}] Rule {r.chunk.id}: {r.chunk.text[:80]}...")


if __name__ == "__main__":
    asyncio.run(main())
