"""P3.3: tracing — log each agent step (tool, args, result) + token usage per run.

`RunTrace` is a plain recorder: pure logic, no network, so it's fully
unit-tested here. The live wiring (real tool calls through a real agent
producing a real token count) is proven end-to-end by `scripts/agent_spike.py`,
consistent with how P2.2-P3.2 kept live-model behavior out of the pytest suite.
"""

from loan_intake_agent.trace import RunTrace


def test_record_appends_a_step_with_tool_args_and_result():
    trace = RunTrace()

    trace.record("calc_ratios_tool", {"fields_json": '{"a": 1}'}, '{"ltv": 0.8}')

    assert len(trace.steps) == 1
    step = trace.steps[0]
    assert step.tool == "calc_ratios_tool"
    assert step.args == {"fields_json": '{"a": 1}'}
    assert step.result == '{"ltv": 0.8}'


def test_record_appends_multiple_steps_in_order():
    trace = RunTrace()

    trace.record("extract_1003_tool", {"document": "doc"}, '{"borrower": null}')
    trace.record("calc_ratios_tool", {"fields_json": "{}"}, '{"ltv": null}')

    assert [step.tool for step in trace.steps] == ["extract_1003_tool", "calc_ratios_tool"]


def test_render_with_no_steps_and_no_usage():
    trace = RunTrace()

    output = trace.render()

    assert "(no tool calls)" in output
    assert "Tokens: unknown" in output


def test_render_lists_each_step_with_tool_args_and_result():
    trace = RunTrace()
    trace.record("check_guardrails_tool", {"fields_json": "{}", "ratios_json": "{}"}, '{"items": []}')

    output = trace.render()

    assert "check_guardrails_tool" in output
    assert "fields_json" in output
    assert '{"items": []}' in output


def test_set_usage_populates_token_counts_in_render():
    trace = RunTrace()

    trace.set_usage({"input_token_count": 120, "output_token_count": 45, "total_token_count": 165})

    output = trace.render()
    assert "input=120" in output
    assert "output=45" in output
    assert "total=165" in output


def test_set_usage_handles_missing_keys():
    trace = RunTrace()

    trace.set_usage({})

    output = trace.render()
    assert "Tokens:" in output
