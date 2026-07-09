"""P1.2: synthetic 1003 fixtures. Done when every fixture loads into `Fields`."""

import json
from pathlib import Path

import pytest

from loan_intake_agent.schema import Fields

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "1003"


def _load(name: str) -> Fields:
    data = json.loads((FIXTURES_DIR / name).read_text())
    return Fields.model_validate(data)


def test_fixtures_directory_has_at_least_four_cases():
    fixture_files = list(FIXTURES_DIR.glob("*.json"))
    assert len(fixture_files) >= 4


@pytest.mark.parametrize(
    "name",
    ["clean.json", "high_ltv.json", "high_dti.json", "missing_employment.json"],
)
def test_every_fixture_loads_into_fields(name):
    fields = _load(name)
    assert isinstance(fields, Fields)


def test_clean_fixture_is_fully_populated():
    fields = _load("clean.json")
    assert fields.borrower is not None
    assert fields.employment is not None
    assert fields.debts is not None
    assert fields.loan is not None


def test_high_ltv_fixture_has_loan_near_property_value():
    fields = _load("high_ltv.json")
    ltv = fields.loan.loan_amount / fields.loan.property_value
    assert ltv >= 0.9


def test_high_dti_fixture_has_debts_near_income():
    fields = _load("high_dti.json")
    dti = fields.debts.monthly_payments / fields.employment.monthly_income
    assert dti >= 0.45


def test_missing_employment_fixture_has_no_employment_section():
    fields = _load("missing_employment.json")
    assert fields.employment is None
