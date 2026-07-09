"""P1.5: check_guardrails flags high LTV, high DTI, and missing required sections.

Done when: it flags the right docs and only those, each with a human-readable reason.
"""

import json
from pathlib import Path

from loan_intake_agent.extract import extract_1003
from loan_intake_agent.guardrails import check_guardrails
from loan_intake_agent.ratios import calc_ratios
from loan_intake_agent.schema import Borrower, Debts, Employment, Fields, LoanProperty

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "1003"


def _complete_fields(**overrides) -> Fields:
    defaults = dict(
        borrower=Borrower(first_name="Jane", last_name="Doe"),
        employment=Employment(monthly_income=6000.0),
        debts=Debts(monthly_payments=800.0),
        loan=LoanProperty(loan_amount=240000.0, property_value=300000.0),
    )
    defaults.update(overrides)
    return Fields(**defaults)


def test_no_flags_for_a_clean_complete_application():
    fields = _complete_fields()
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert flags.items == []


def test_flags_high_ltv_only():
    fields = _complete_fields(loan=LoanProperty(loan_amount=285000.0, property_value=300000.0))
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert len(flags.items) == 1
    assert flags.items[0].code == "high_ltv"
    assert "ltv" in flags.items[0].reason.lower()


def test_flags_high_dti_only():
    fields = _complete_fields(
        employment=Employment(monthly_income=4000.0),
        debts=Debts(monthly_payments=2000.0),
    )
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert len(flags.items) == 1
    assert flags.items[0].code == "high_dti"
    assert "dti" in flags.items[0].reason.lower()


def test_flags_missing_required_section_only():
    fields = _complete_fields(employment=None)
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert len(flags.items) == 1
    assert flags.items[0].code == "missing_section"
    assert "employment" in flags.items[0].reason.lower()


def test_flags_one_entry_per_missing_section():
    fields = Fields(borrower=Borrower(first_name="Jane"))
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    codes = [f.code for f in flags.items]
    reasons = " ".join(f.reason.lower() for f in flags.items)
    assert codes.count("missing_section") == 3
    assert "employment" in reasons
    assert "debts" in reasons
    assert "loan" in reasons


def test_flags_combine_high_ltv_and_missing_section():
    fields = _complete_fields(
        employment=None,
        loan=LoanProperty(loan_amount=285000.0, property_value=300000.0),
    )
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    codes = {f.code for f in flags.items}
    assert codes == {"high_ltv", "missing_section"}


def test_clean_fixture_end_to_end_has_no_flags():
    document = (FIXTURES_DIR / "clean.json").read_text()
    fields = extract_1003(document)
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert flags.items == []


def test_high_ltv_fixture_end_to_end_flags_only_high_ltv():
    document = (FIXTURES_DIR / "high_ltv.json").read_text()
    fields = extract_1003(document)
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert [f.code for f in flags.items] == ["high_ltv"]


def test_high_dti_fixture_end_to_end_flags_only_high_dti():
    document = (FIXTURES_DIR / "high_dti.json").read_text()
    fields = extract_1003(document)
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert [f.code for f in flags.items] == ["high_dti"]


def test_missing_employment_fixture_end_to_end_flags_only_missing_section():
    document = (FIXTURES_DIR / "missing_employment.json").read_text()
    fields = extract_1003(document)
    ratios = calc_ratios(fields)

    flags = check_guardrails(fields, ratios)

    assert [f.code for f in flags.items] == ["missing_section"]
    assert "employment" in flags.items[0].reason.lower()
