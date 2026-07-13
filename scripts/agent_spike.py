"""P2.4 spike: one NL request flows through the right tools to a grounded answer.

Run: uv run python scripts/agent_spike.py
"""

import asyncio
import os

from agent_framework_foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

from loan_intake_agent.agent import build_agent
from loan_intake_agent.search import GuidelineIndex

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
    agent = build_agent(client, index)

    prompts = [
        f"Here is a loan application:\n{CLEAN_DOCUMENT}\nExtract the fields, compute the ratios, "
        "check the guardrails, and tell me whether this application is flagged and why.",
        "What's the maximum debt-to-income ratio allowed, according to the guidelines?",
    ]
    for prompt in prompts:
        result = await agent.run(prompt)
        print(f"\nPrompt: {prompt[:80]}...")
        print(f"Answer: {result.text}")


if __name__ == "__main__":
    asyncio.run(main())
