"""P2.4: agent orchestration — register the four tools and let the agent route.

The wrapper functions (JSON-in/JSON-out) are pure and unit-tested here without
network access. `build_agent` wiring is tested against a fake chat client that
records what it was asked to register. Whether a live LLM actually *picks* the
right tool for a natural-language request is proven by `scripts/agent_spike.py`
end to end — consistent with how P2.2/P2.3 kept live-model behavior out of the
pytest suite.
"""

import json

import pytest

from loan_intake_agent.agent import (
    build_agent,
    build_search_guidelines_tool,
    calc_ratios_tool,
    check_guardrails_tool,
    extract_1003_tool,
)
from loan_intake_agent.schema import Fields, Ratios
from loan_intake_agent.search import GuidelineIndex
from loan_intake_agent.trace import RunTrace

CLEAN_DOCUMENT = json.dumps(
    {
        "borrower": {"first_name": "Jane", "last_name": "Doe"},
        "employment": {"employer_name": "Acme Corp", "years_employed": 3.5, "monthly_income": 6000.0},
        "debts": {"monthly_payments": 800.0},
        "loan": {"loan_amount": 240000.0, "property_value": 300000.0, "property_address": "123 Main St"},
    }
)


def test_extract_1003_tool_returns_fields_json():
    result_json = extract_1003_tool(CLEAN_DOCUMENT)

    fields = Fields.model_validate_json(result_json)
    assert fields.borrower.first_name == "Jane"
    assert fields.loan.loan_amount == 240000.0


def test_calc_ratios_tool_computes_from_fields_json():
    fields_json = extract_1003_tool(CLEAN_DOCUMENT)

    ratios_json = calc_ratios_tool(fields_json)

    ratios = Ratios.model_validate_json(ratios_json)
    assert ratios.ltv == pytest.approx(0.8)


def test_check_guardrails_tool_flags_high_ltv():
    fields_json = extract_1003_tool(CLEAN_DOCUMENT)
    ratios_json = calc_ratios_tool(fields_json)

    flags_json = check_guardrails_tool(fields_json, ratios_json)

    flags = json.loads(flags_json)
    # LTV is exactly 0.8 (the threshold), not over it — no flags expected.
    assert flags["items"] == []


def test_check_guardrails_tool_flags_missing_section():
    fields_json = Fields().model_dump_json()
    ratios_json = Ratios().model_dump_json()

    flags_json = check_guardrails_tool(fields_json, ratios_json)

    flags = json.loads(flags_json)
    codes = [item["code"] for item in flags["items"]]
    assert codes.count("missing_section") == 4


GUIDELINES_TEXT = (
    "# Title\n\n"
    "> Disclaimer.\n\n"
    "## 1. Loan-to-Value (LTV)\n\n"
    "**Rule 1.1 — Maximum LTV.** LTV must not exceed 80%.\n"
)


async def _fake_embed_fn(texts: list[str]) -> list[list[float]]:
    return [[1.0, 0.0, 0.0] for _ in texts]


@pytest.mark.anyio
async def test_search_guidelines_tool_delegates_to_the_bound_index():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_fake_embed_fn)
    search_tool = build_search_guidelines_tool(index)

    passages_json = await search_tool("what's the max LTV?")

    passages = json.loads(passages_json)
    assert passages["items"][0]["id"] == "1.1"


class _FakeAgent:
    def __init__(self, instructions, tools):
        self.instructions = instructions
        self.tools = tools


class _FakeChatClient:
    def as_agent(self, instructions, tools):
        return _FakeAgent(instructions, tools)


@pytest.mark.anyio
async def test_build_agent_registers_all_four_tools():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_fake_embed_fn)
    client = _FakeChatClient()

    agent = build_agent(client, index)

    tool_names = {getattr(t, "__name__", None) for t in agent.tools}
    assert tool_names == {"extract_1003_tool", "calc_ratios_tool", "check_guardrails_tool", "search_guidelines_tool"}


@pytest.mark.anyio
async def test_build_agent_preserves_tool_names_and_docstrings_without_a_trace():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_fake_embed_fn)
    client = _FakeChatClient()

    agent = build_agent(client, index)

    by_name = {t.__name__: t for t in agent.tools}
    assert by_name["calc_ratios_tool"].__doc__ == calc_ratios_tool.__doc__


@pytest.mark.anyio
async def test_build_agent_with_trace_records_a_sync_tool_call():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_fake_embed_fn)
    client = _FakeChatClient()
    trace = RunTrace()

    agent = build_agent(client, index, trace=trace)

    by_name = {t.__name__: t for t in agent.tools}
    fields_json = by_name["extract_1003_tool"](CLEAN_DOCUMENT)
    ratios_json = by_name["calc_ratios_tool"](fields_json)

    assert [step.tool for step in trace.steps] == ["extract_1003_tool", "calc_ratios_tool"]
    assert trace.steps[1].args == {"fields_json": fields_json}
    assert trace.steps[1].result == ratios_json


@pytest.mark.anyio
async def test_build_agent_with_trace_records_an_async_tool_call():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_fake_embed_fn)
    client = _FakeChatClient()
    trace = RunTrace()

    agent = build_agent(client, index, trace=trace)

    by_name = {t.__name__: t for t in agent.tools}
    passages_json = await by_name["search_guidelines_tool"]("what's the max LTV?")

    assert [step.tool for step in trace.steps] == ["search_guidelines_tool"]
    assert trace.steps[0].args == {"query": "what's the max LTV?"}
    assert trace.steps[0].result == passages_json


@pytest.mark.anyio
async def test_build_agent_without_trace_does_not_record_anything():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_fake_embed_fn)
    client = _FakeChatClient()

    agent = build_agent(client, index)

    by_name = {t.__name__: t for t in agent.tools}
    by_name["extract_1003_tool"](CLEAN_DOCUMENT)  # should not raise without a trace
