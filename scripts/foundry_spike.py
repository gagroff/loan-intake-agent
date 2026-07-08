"""P0.2 spike: prove Foundry + agent-framework tool calling works end to end.

Run: uv run python scripts/foundry_spike.py
"""

import asyncio
import os

from agent_framework_foundry import FoundryChatClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv


def get_ltv(loan_amount: float, property_value: float) -> str:
    """Compute loan-to-value ratio as a percentage."""
    return f"{loan_amount / property_value:.1%}"


async def main() -> None:
    load_dotenv()
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_CHAT_DEPLOYMENT"],
        credential=AzureCliCredential(),
    )
    agent = client.as_agent(instructions="Use the get_ltv tool to answer LTV questions.", tools=get_ltv)
    result = await agent.run("What's the LTV for a $300,000 loan on a $400,000 property?")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
