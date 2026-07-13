"""P2.4: agent orchestration — register the four tools and let the agent route.

Each underlying function (`extract_1003`, `calc_ratios`, `check_guardrails`,
`search_guidelines`) works with typed pydantic models, but agent-framework
tool calls pass string/JSON arguments from the LLM and expect string/JSON
results back. The `*_tool` wrappers here are the JSON-in/JSON-out adapters
that make each function callable by the agent; the underlying logic is
untouched and stays covered by its own tests.

`search_guidelines` additionally needs a `GuidelineIndex`, which isn't
something the LLM can supply — `build_search_guidelines_tool` closes over an
already-built index so the tool the agent sees only takes `query`.
"""

from collections.abc import Awaitable, Callable

from .extract import extract_1003
from .guardrails import check_guardrails
from .ratios import calc_ratios
from .schema import Fields, Ratios
from .search import GuidelineIndex

INSTRUCTIONS = (
    "You are a loan intake assistant. Use extract_1003_tool to read a raw application "
    "document into structured fields, calc_ratios_tool to compute LTV/DTI from those "
    "fields, check_guardrails_tool to flag issues from the fields and ratios, and "
    "search_guidelines_tool to ground any answer about underwriting rules in the "
    "guideline corpus. If the guidelines don't cover something, say so honestly "
    "instead of guessing."
)


def extract_1003_tool(document: str) -> str:
    """Extract Form 1003 fields (borrower, employment, debts, loan) from a raw application document as JSON."""
    return extract_1003(document).model_dump_json()


def calc_ratios_tool(fields_json: str) -> str:
    """Compute LTV and DTI ratios as JSON from Fields JSON (the output of extract_1003_tool)."""
    fields = Fields.model_validate_json(fields_json)
    return calc_ratios(fields).model_dump_json()


def check_guardrails_tool(fields_json: str, ratios_json: str) -> str:
    """Check Fields JSON and Ratios JSON against underwriting guardrails; returns flags with reasons as JSON."""
    fields = Fields.model_validate_json(fields_json)
    ratios = Ratios.model_validate_json(ratios_json)
    return check_guardrails(fields, ratios).model_dump_json()


def build_search_guidelines_tool(index: GuidelineIndex) -> Callable[[str], Awaitable[str]]:
    """Bind a GuidelineIndex into a query-only tool the agent can call."""

    async def search_guidelines_tool(query: str) -> str:
        """Search the underwriting guideline corpus for passages relevant to a query; returns scored passages as JSON."""
        passages = await index.search(query)
        return passages.model_dump_json()

    return search_guidelines_tool


def build_agent(client, index: GuidelineIndex):
    """Register all four tools on a chat client and return the resulting agent."""
    tools = [
        extract_1003_tool,
        calc_ratios_tool,
        check_guardrails_tool,
        build_search_guidelines_tool(index),
    ]
    return client.as_agent(instructions=INSTRUCTIONS, tools=tools)
