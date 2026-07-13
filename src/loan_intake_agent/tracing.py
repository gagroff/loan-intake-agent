"""P3.3: tracing — log each agent tool call (name, args, result) + token usage.

`TracingMiddleware` implements agent-framework's `FunctionMiddleware` protocol
so it can be passed straight into `client.as_agent(middleware=[...])`: the
framework calls `process()` around every tool invocation, and recording after
`call_next()` returns captures the actual result the tool produced (not just
the arguments the LLM chose). `format_trace` turns the recorded calls plus the
run's `usage_details` into a readable report.
"""

from dataclasses import dataclass, field
from typing import Any

from agent_framework import FunctionMiddleware


@dataclass
class ToolCallTrace:
    name: str
    arguments: dict[str, Any]
    result: Any = None


def _readable_result(result: Any) -> Any:
    """Unwrap agent-framework's tool-result Content wrapper so the trace shows
    readable JSON rather than a Content object repr. A tool's raw return value
    is parsed into `list[Content]` before middleware observes it: a plain
    string result becomes `Content(type="text", text=...)`, so `.text` (when
    set) holds the value; `.result` is the fallback for non-text content
    types."""
    if isinstance(result, list) and len(result) == 1 and hasattr(result[0], "text"):
        item = result[0]
        return item.text if item.text is not None else getattr(item, "result", result)
    return result


class TracingMiddleware(FunctionMiddleware):
    def __init__(self) -> None:
        self.calls: list[ToolCallTrace] = []

    async def process(self, context, call_next) -> None:
        await call_next()
        self.calls.append(
            ToolCallTrace(
                name=context.function.name,
                arguments=dict(context.arguments) if context.arguments else {},
                result=_readable_result(context.result),
            )
        )


def format_trace(calls: list[ToolCallTrace], usage: dict[str, Any] | None = None) -> str:
    lines = ["Trace:"]
    if not calls:
        lines.append("  (no tool calls)")
    else:
        for i, call in enumerate(calls, 1):
            lines.append(f"  {i}. {call.name}({call.arguments}) -> {call.result!r}")

    if usage:
        input_tokens = usage.get("input_token_count")
        output_tokens = usage.get("output_token_count")
        total_tokens = usage.get("total_token_count")
        lines.append(f"Tokens: input={input_tokens} output={output_tokens} total={total_tokens}")

    return "\n".join(lines)
