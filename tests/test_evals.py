"""P3.1: eval set — fixtures mapping inputs to expected outputs.

Done when: the eval file covers each guardrail (high_ltv, high_dti,
missing_section, and the clean/no-flag case) plus a couple of RAG questions
(including one the corpus doesn't cover, to eval the honest-decline path).
"""

from loan_intake_agent.evals import load_guardrail_evals, load_rag_evals


def test_load_guardrail_evals_returns_typed_cases():
    cases = load_guardrail_evals()

    assert len(cases) >= 4
    for case in cases:
        assert case.name
        assert case.document_fixture
        assert isinstance(case.expected_flag_codes, list)


def test_guardrail_evals_cover_every_guardrail_and_the_clean_case():
    cases = load_guardrail_evals()

    all_codes = {code for case in cases for code in case.expected_flag_codes}
    assert all_codes == {"high_ltv", "high_dti", "missing_section"}
    assert any(case.expected_flag_codes == [] for case in cases)


def test_guardrail_eval_document_fixtures_exist_and_load():
    from pathlib import Path

    from loan_intake_agent.extract import extract_1003

    fixtures_dir = Path(__file__).parent.parent / "fixtures"
    for case in load_guardrail_evals():
        document = (fixtures_dir / case.document_fixture).read_text(encoding="utf-8")
        fields = extract_1003(document)
        assert fields is not None


def test_load_rag_evals_returns_typed_cases():
    cases = load_rag_evals()

    assert len(cases) >= 2
    for case in cases:
        assert case.name
        assert case.query

def test_rag_evals_include_an_out_of_corpus_question():
    cases = load_rag_evals()

    assert any(case.expected_rule_id is None for case in cases)
    assert any(case.expected_rule_id is not None for case in cases)
