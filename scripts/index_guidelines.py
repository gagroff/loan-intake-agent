"""P2.3 spike: search_guidelines returns grounded passages for a real query.

Run: uv run python scripts/index_guidelines.py
"""

import asyncio

from dotenv import load_dotenv

from loan_intake_agent.search import GuidelineIndex, search_guidelines


async def main() -> None:
    load_dotenv()

    index = await GuidelineIndex.build()

    for query in [
        "What's the maximum loan-to-value ratio allowed?",
        "What happens if my debt-to-income ratio is too high?",
        "What is the minimum credit score required?",
    ]:
        passages = await search_guidelines(query, index)
        print(f"\nQuery: {query!r}")
        for p in passages.items[:2]:
            print(f"  [{p.score:.3f}] Rule {p.id}: {p.text[:90]}...")


if __name__ == "__main__":
    asyncio.run(main())
