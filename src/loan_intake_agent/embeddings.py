"""Embed text via the Foundry-deployed embedding model.

The Foundry project's OpenAI-compatible endpoint (FOUNDRY_PROJECT_ENDPOINT,
``.../api/projects/<name>/openai/v1``) only proxies chat/response calls, not
embeddings. Embeddings must go directly to the Cognitive Services resource
root using the standard Azure OpenAI SDK, authenticated with a token scoped
to ``https://cognitiveservices.azure.com/.default`` rather than the
``https://ai.azure.com`` scope the project endpoint uses.
"""

import os
import re

from azure.identity.aio import AzureCliCredential, get_bearer_token_provider
from openai import AsyncAzureOpenAI

_COGNITIVE_SERVICES_SCOPE = "https://cognitiveservices.azure.com/.default"
_API_VERSION = "2024-06-01"


def resource_root(project_endpoint: str) -> str:
    match = re.match(r"(https://[^/]+)", project_endpoint)
    if not match:
        raise ValueError(f"Could not parse a resource root from project endpoint: {project_endpoint!r}")
    return match.group(1)


def build_embedding_client(
    project_endpoint: str | None = None,
    credential: AzureCliCredential | None = None,
) -> AsyncAzureOpenAI:
    project_endpoint = project_endpoint or os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    credential = credential or AzureCliCredential()
    token_provider = get_bearer_token_provider(credential, _COGNITIVE_SERVICES_SCOPE)
    return AsyncAzureOpenAI(
        azure_endpoint=resource_root(project_endpoint),
        azure_ad_token_provider=token_provider,
        api_version=_API_VERSION,
    )


async def embed_texts(
    client: AsyncAzureOpenAI,
    texts: list[str],
    model: str | None = None,
) -> list[list[float]]:
    model = model or os.environ["FOUNDRY_EMBEDDING_DEPLOYMENT"]
    response = await client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]
