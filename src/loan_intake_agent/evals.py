"""P3.1: eval set — typed loaders for the fixtures P3.2's run_evals scores against.

Guardrail cases map a document fixture to the flag codes check_guardrails
should produce for it. RAG cases map a query to the rule id search_guidelines
should surface as its top passage — or `None` when the question is
deliberately out-of-corpus, so the eval can check for an honest decline
instead of a hallucinated answer.
"""

import json
from pathlib import Path

from .schema import GuardrailEvalCase, RagEvalCase

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "evals"


def load_guardrail_evals(path: Path = FIXTURES_DIR / "guardrail_evals.json") -> list[GuardrailEvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [GuardrailEvalCase.model_validate(item) for item in data]


def load_rag_evals(path: Path = FIXTURES_DIR / "rag_evals.json") -> list[RagEvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [RagEvalCase.model_validate(item) for item in data]
