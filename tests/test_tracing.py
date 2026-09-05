"""P3.3: tracing — log each agent tool call (name, args, result) + token usage.

TracingMiddleware hooks agent-framework's FunctionMiddleware protocol, so it's
tested against a fake FunctionInvocationContext (real one requires a live
agent run to construct). format_trace() is pure formatting logic, tested
directly. scripts/agent_spike.py (wired with tracing) proves a real run
emits a readable trace + token count end to end.
"""

from dataclasses import dataclass, field
from typing import Any

import pytest

from loan_intake_agent.tracing import TracingMiddleware, ToolCallTrace, format_trace


@dataclass
class _FakeFunction:
    name: str


@dataclass
class _FakeContext:
    function: _FakeFunction
    arguments: dict[str, Any]
    result: Any = None


@pytest.mark.anyio
async def test_tracing_middleware_records_a_call_after_call_next_runs():
    middleware = TracingMiddleware()
    context = _FakeContext(function=_FakeFunction(name="extract_1003_tool"), arguments={"document": "{}"})

    async def call_next():
        context.result = '{"borrower": null}'

    await middleware.process(context, call_next)

    assert len(middleware.calls) == 1
    call = middleware.calls[0]
    assert call.name == "extract_1003_tool"
    assert call.arguments == {"document": "{}"}
    assert call.result == '{"borrower": null}'


@dataclass
class _FakeContent:
    text: Any = None
    result: Any = None


@pytest.mark.anyio
async def test_tracing_middleware_unwraps_text_content_for_readability():
    """A tool's raw string return value is parsed by agent-framework into a
    list of Content(type="text") before middleware observes it — record
    `.text` directly rather than the object's repr, so the trace stays
    readable."""
    middleware = TracingMiddleware()
    context = _FakeContext(function=_FakeFunction(name="extract_1003_tool"), arguments={"document": "{}"})

    async def call_next():
        context.result = [_FakeContent(text='{"borrower": null}')]

    await middleware.process(context, call_next)

    assert middleware.calls[0].result == '{"borrower": null}'


@pytest.mark.anyio
async def test_tracing_middleware_falls_back_to_result_for_non_text_content():
    middleware = TracingMiddleware()
    context = _FakeContext(function=_FakeFunction(name="extract_1003_tool"), arguments={})

    async def call_next():
        context.result = [_FakeContent(text=None, result="raw-value")]

    await middleware.process(context, call_next)

    assert middleware.calls[0].result == "raw-value"


@pytest.mark.anyio
async def test_tracing_middleware_records_calls_in_order_across_multiple_calls():
    middleware = TracingMiddleware()

    for name in ["extract_1003_tool", "calc_ratios_tool", "check_guardrails_tool"]:
        context = _FakeContext(function=_FakeFunction(name=name), arguments={})

        async def call_next(context=context):
            context.result = "ok"

        await middleware.process(context, call_next)

    assert [c.name for c in middleware.calls] == ["extract_1003_tool", "calc_ratios_tool", "check_guardrails_tool"]


def test_format_trace_lists_each_call_in_order():
    calls = [
        ToolCallTrace(name="extract_1003_tool", arguments={"document": "{}"}, result='{"borrower": null}'),
        ToolCallTrace(name="calc_ratios_tool", arguments={"fields_json": "{}"}, result='{"ltv": null}'),
    ]

    report = format_trace(calls)

    assert "extract_1003_tool" in report
    assert "calc_ratios_tool" in report
    assert report.index("extract_1003_tool") < report.index("calc_ratios_tool")


def test_format_trace_includes_token_usage_when_given():
    report = format_trace([], usage={"input_token_count": 100, "output_token_count": 20, "total_token_count": 120})

    assert "100" in report
    assert "20" in report
    assert "120" in report


def test_format_trace_handles_no_calls_and_no_usage():
    report = format_trace([])

    assert "no tool calls" in report.lower()
