"""P3.3 spike: a run emits a readable trace (tool, args, result per step) and a token count.

Run: uv run python scripts/trace_spike.py
"""

import asyncio
import os

from agent_framework_foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from loan_intake_agent.agent import build_agent
from loan_intake_agent.search import GuidelineIndex
from loan_intake_agent.trace import RunTrace

CLEAN_DOCUMENT = """
{
  "borrower": {"first_name": "Jane", "last_name": "Doe"},
  "employment": {"employer_name": "Acme Corp", "years_employed": 3.5, "monthly_income": 6000.0},
  "debts": {"monthly_payments": 800.0},
  "loan": {"loan_amount": 285000.0, "property_value": 300000.0, "property_address": "123 Main St"}
}
"""


async def main() -> None:
    load_dotenv()
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_CHAT_DEPLOYMENT"],
        credential=AzureCliCredential(),
    )
    index = await GuidelineIndex.build()

    prompt = (
        f"Here is a loan application:\n{CLEAN_DOCUMENT}\nExtract the fields, compute the ratios, "
        "check the guardrails, and tell me whether this application is flagged and why."
    )

    trace = RunTrace()
    agent = build_agent(client, index, trace=trace)
    result = await agent.run(prompt)
    trace.set_usage(result.usage_details or {})

    print(f"Prompt: {prompt[:80]}...")
    print(f"Answer: {result.text}")
    print()
    print(trace.render())


if __name__ == "__main__":
    asyncio.run(main())
