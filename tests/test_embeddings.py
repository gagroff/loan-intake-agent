"""P2.2: resource-root parsing for the embedding client's Azure OpenAI endpoint.

The project's OpenAI-compatible endpoint (FOUNDRY_PROJECT_ENDPOINT) doesn't
proxy embeddings; embeddings go to the bare Cognitive Services resource
root instead. This is the pure, no-network part of that wiring.
"""

import pytest

from loan_intake_agent.embeddings import resource_root


def test_resource_root_strips_project_path():
    endpoint = "https://loan-intake-resource.services.ai.azure.com/api/projects/loan-intake"

    assert resource_root(endpoint) == "https://loan-intake-resource.services.ai.azure.com"


def test_resource_root_handles_bare_host():
    endpoint = "https://loan-intake-resource.services.ai.azure.com"

    assert resource_root(endpoint) == "https://loan-intake-resource.services.ai.azure.com"


def test_resource_root_rejects_malformed_endpoint():
    with pytest.raises(ValueError):
        resource_root("not-a-url")
