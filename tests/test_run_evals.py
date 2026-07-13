"""P3.2: run_evals — scores the eval set pass/fail and prints a summary.

Guardrail scoring is pure/deterministic (extract -> ratios -> guardrails) so
it's tested directly, including proving a broken rule drops the score.
RAG scoring needs an embedding call, so it's tested against a fake embed_fn
the same way test_search.py is — the real model is only exercised via the
`run-evals` CLI subcommand.
"""

import pytest

from loan_intake_agent.run_evals import format_report, run_guardrail_evals, run_rag_evals, score
from loan_intake_agent.schema import Flags, GuardrailEvalCase, RagEvalCase
from loan_intake_agent.search import GuidelineIndex


def _cases():
    return [
        GuardrailEvalCase(name="clean", document_fixture="1003/clean.json", expected_flag_codes=[]),
        GuardrailEvalCase(name="high_ltv", document_fixture="1003/high_ltv.json", expected_flag_codes=["high_ltv"]),
        GuardrailEvalCase(name="high_dti", document_fixture="1003/high_dti.json", expected_flag_codes=["high_dti"]),
        GuardrailEvalCase(
            name="missing_employment",
            document_fixture="1003/missing_employment.json",
            expected_flag_codes=["missing_section"],
        ),
    ]


def test_run_guardrail_evals_all_pass_against_the_real_pipeline():
    results = run_guardrail_evals(_cases())

    assert all(r.passed for r in results)
    assert score(results) == (4, 4)


def test_run_guardrail_evals_score_drops_when_a_rule_is_broken():
    def broken_check_guardrails(fields, ratios):
        return Flags(items=[])  # never flags anything

    results = run_guardrail_evals(_cases(), check_guardrails_fn=broken_check_guardrails)

    # clean.json still expects [] -> passes; the other 3 expect a flag -> fail.
    assert score(results) == (1, 4)
    failed_names = {r.name for r in results if not r.passed}
    assert failed_names == {"high_ltv", "high_dti", "missing_employment"}


GUIDELINES_TEXT = (
    "# Title\n\n"
    "> Disclaimer.\n\n"
    "## 1. Loan-to-Value (LTV)\n\n"
    "**Rule 1.1 — Maximum LTV.** LTV must not exceed 80%.\n"
)


async def _confident_embed_fn(texts: list[str]) -> list[list[float]]:
    return [[1.0, 0.0, 0.0] for _ in texts]


async def _unconfident_embed_fn(texts: list[str]) -> list[list[float]]:
    return [[0.0, 1.0, 0.0] for _ in texts]  # orthogonal to the corpus vector -> cosine score 0


@pytest.mark.anyio
async def test_run_rag_evals_passes_a_confident_correct_match():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_confident_embed_fn)
    cases = [RagEvalCase(name="max_ltv", query="what's the max LTV?", expected_rule_id="1.1")]

    results = await run_rag_evals(cases, index)

    assert results[0].passed
    assert results[0].actual_rule_id == "1.1"


@pytest.mark.anyio
async def test_run_rag_evals_passes_an_honest_decline_on_low_confidence():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_confident_embed_fn)

    async def query_embed_fn(texts):
        return await _unconfident_embed_fn(texts)

    index._embed_fn = query_embed_fn
    cases = [RagEvalCase(name="credit_score", query="minimum credit score?", expected_rule_id=None)]

    results = await run_rag_evals(cases, index)

    assert results[0].passed


@pytest.mark.anyio
async def test_run_rag_evals_fails_a_confident_wrong_match():
    index = await GuidelineIndex.build(text=GUIDELINES_TEXT, embed_fn=_confident_embed_fn)
    cases = [RagEvalCase(name="max_ltv", query="what's the max LTV?", expected_rule_id="9.9")]

    results = await run_rag_evals(cases, index)

    assert not results[0].passed


def test_format_report_includes_scores_and_case_names():
    guardrail_results = run_guardrail_evals(_cases())

    report = format_report(guardrail_results, [])

    assert "4/4" in report
    assert "clean" in report
    assert "Overall" in report
