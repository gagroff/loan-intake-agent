"""P1.4: calc_ratios computes LTV and DTI.

Done when: outputs match hand-computed values in a unit test.
"""

import pytest

from loan_intake_agent.ratios import calc_ratios
from loan_intake_agent.schema import Debts, Employment, Fields, LoanProperty


def test_calc_ratios_matches_hand_computed_values():
    fields = Fields(
        employment=Employment(monthly_income=6000.0),
        debts=Debts(monthly_payments=800.0),
        loan=LoanProperty(loan_amount=240000.0, property_value=300000.0),
    )

    ratios = calc_ratios(fields)

    assert ratios.ltv == pytest.approx(0.8)
    assert ratios.dti == pytest.approx(800.0 / 6000.0)


def test_calc_ratios_high_ltv_case():
    fields = Fields(loan=LoanProperty(loan_amount=285000.0, property_value=300000.0))

    ratios = calc_ratios(fields)

    assert ratios.ltv == pytest.approx(0.95)


def test_calc_ratios_high_dti_case():
    fields = Fields(
        employment=Employment(monthly_income=4000.0),
        debts=Debts(monthly_payments=2000.0),
    )

    ratios = calc_ratios(fields)

    assert ratios.dti == pytest.approx(0.5)


def test_calc_ratios_ltv_is_none_when_loan_section_missing():
    fields = Fields(employment=Employment(monthly_income=6000.0), debts=Debts(monthly_payments=800.0))

    ratios = calc_ratios(fields)

    assert ratios.ltv is None


def test_calc_ratios_dti_is_none_when_employment_section_missing():
    fields = Fields(loan=LoanProperty(loan_amount=180000.0, property_value=220000.0))

    ratios = calc_ratios(fields)

    assert ratios.dti is None


def test_calc_ratios_ltv_is_none_when_property_value_is_zero():
    fields = Fields(loan=LoanProperty(loan_amount=100000.0, property_value=0.0))

    ratios = calc_ratios(fields)

    assert ratios.ltv is None


def test_calc_ratios_dti_is_none_when_income_is_zero():
    fields = Fields(employment=Employment(monthly_income=0.0), debts=Debts(monthly_payments=500.0))

    ratios = calc_ratios(fields)

    assert ratios.dti is None


def test_calc_ratios_on_empty_fields_returns_none_ratios():
    ratios = calc_ratios(Fields())

    assert ratios.ltv is None
    assert ratios.dti is None
