"""P3.3: tracing — record each agent tool call (tool, args, result) plus per-run token usage.

`RunTrace` is a plain recorder with no dependency on agent-framework types:
`build_agent` (see `agent.py`) wraps each tool so calling it appends a step
here, and the caller copies `AgentResponse.usage_details` in after `agent.run`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass
class ToolStep:
    tool: str
    args: dict[str, Any]
    result: str


@dataclass
class RunTrace:
    steps: list[ToolStep] = field(default_factory=list)
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    def record(self, tool: str, args: dict[str, Any], result: str) -> None:
        self.steps.append(ToolStep(tool=tool, args=args, result=result))

    def set_usage(self, usage_details: Mapping[str, Any]) -> None:
        self.input_tokens = usage_details.get("input_token_count")
        self.output_tokens = usage_details.get("output_token_count")
        self.total_tokens = usage_details.get("total_token_count")

    def render(self) -> str:
        lines = ["Trace:"]
        if not self.steps:
            lines.append("  (no tool calls)")
        for i, step in enumerate(self.steps, start=1):
            args_str = ", ".join(f"{key}={value!r}" for key, value in step.args.items())
            lines.append(f"  {i}. {step.tool}({args_str}) -> {step.result}")
        lines.append(self._usage_line())
        return "\n".join(lines)

    def _usage_line(self) -> str:
        if self.input_tokens is None and self.output_tokens is None and self.total_tokens is None:
            return "Tokens: unknown"
        return f"Tokens: input={self.input_tokens} output={self.output_tokens} total={self.total_tokens}"
