"""P3.2: run_evals — scores the P3.1 eval set pass/fail and prints a summary.

Guardrail scoring runs the real extract -> ratios -> guardrails pipeline
against each case's document fixture and compares flag codes; it takes no
network. RAG scoring embeds each query with the given index and checks
whether the top passage matches the expected rule id at a minimum
confidence, or — for a `None` expected_rule_id — that the top score falls
*below* that confidence, so an honest decline scores as a pass rather than
a hallucinated citation.
"""

from collections.abc import Callable
from pathlib import Path

from .extract import extract_1003
from .guardrails import check_guardrails
from .ratios import calc_ratios
from .schema import Flags, GuardrailEvalCase, GuardrailEvalResult, RagEvalCase, RagEvalResult
from .search import GuidelineIndex

FIXTURES_ROOT = Path(__file__).parent.parent.parent / "fixtures"

# In-corpus queries scored ~0.6-0.75 against the real embedding model during
# P2.3's live spike; out-of-corpus queries scored ~0.38. This threshold sits
# between the two so a confident wrong match still fails.
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


def run_guardrail_evals(
    cases: list[GuardrailEvalCase],
    fixtures_root: Path = FIXTURES_ROOT,
    check_guardrails_fn: Callable = check_guardrails,
) -> list[GuardrailEvalResult]:
    results = []
    for case in cases:
        document = (fixtures_root / case.document_fixture).read_text(encoding="utf-8")
        fields = extract_1003(document)
        ratios = calc_ratios(fields)
        flags: Flags = check_guardrails_fn(fields, ratios)

        actual_codes = sorted(flag.code for flag in flags.items)
        expected_codes = sorted(case.expected_flag_codes)
        results.append(
            GuardrailEvalResult(
                name=case.name,
                passed=actual_codes == expected_codes,
                expected_flag_codes=expected_codes,
                actual_flag_codes=actual_codes,
            )
        )
    return results


async def run_rag_evals(
    cases: list[RagEvalCase],
    index: GuidelineIndex,
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> list[RagEvalResult]:
    results = []
    for case in cases:
        passages = await index.search(case.query, top_k=1)
        top = passages.items[0] if passages.items else None
        actual_rule_id = top.id if top else None
        actual_score = top.score if top else None

        if case.expected_rule_id is None:
            passed = actual_score is None or actual_score < confidence_threshold
        else:
            passed = (
                actual_rule_id == case.expected_rule_id
                and actual_score is not None
                and actual_score >= confidence_threshold
            )

        results.append(
            RagEvalResult(
                name=case.name,
                passed=passed,
                expected_rule_id=case.expected_rule_id,
                actual_rule_id=actual_rule_id,
                score=actual_score,
            )
        )
    return results


def score(results: list[GuardrailEvalResult] | list[RagEvalResult]) -> tuple[int, int]:
    passed = sum(1 for r in results if r.passed)
    return passed, len(results)


def format_report(
    guardrail_results: list[GuardrailEvalResult],
    rag_results: list[RagEvalResult],
) -> str:
    lines = ["Guardrail evals:"]
    for r in guardrail_results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"  [{status}] {r.name} — expected {r.expected_flag_codes}, got {r.actual_flag_codes}")
    gp, gt = score(guardrail_results)
    lines.append(f"  {gp}/{gt} passed")

    lines.append("RAG evals:")
    for r in rag_results:
        status = "PASS" if r.passed else "FAIL"
        lines.append(f"  [{status}] {r.name} — expected {r.expected_rule_id}, got {r.actual_rule_id} (score={r.score})")
    rp, rt = score(rag_results)
    lines.append(f"  {rp}/{rt} passed")

    total_passed, total = gp + rp, gt + rt
    lines.append(f"Overall: {total_passed}/{total} passed")
    return "\n".join(lines)


async def main() -> int:
    from dotenv import load_dotenv

    from .evals import load_guardrail_evals, load_rag_evals

    load_dotenv()

    guardrail_results = run_guardrail_evals(load_guardrail_evals())
    index = await GuidelineIndex.build()
    rag_results = await run_rag_evals(load_rag_evals(), index)

    print(format_report(guardrail_results, rag_results))

    total_passed, total = score(guardrail_results + rag_results)
    return 0 if total_passed == total else 1
