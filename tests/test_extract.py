"""P1.3: extract_1003 maps a raw document to Fields.

Done when: it runs over every fixture without crashing, and missing/malformed
fields are represented as None rather than raising.
"""

import json
from pathlib import Path

import pytest

from loan_intake_agent.extract import extract_1003
from loan_intake_agent.schema import Fields

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "1003"


@pytest.mark.parametrize(
    "name",
    ["clean.json", "high_ltv.json", "high_dti.json", "missing_employment.json"],
)
def test_extract_1003_runs_over_every_fixture_without_crashing(name):
    document = (FIXTURES_DIR / name).read_text()
    fields = extract_1003(document)
    assert isinstance(fields, Fields)


def test_extract_1003_populates_matching_sections():
    document = (FIXTURES_DIR / "clean.json").read_text()
    fields = extract_1003(document)
    assert fields.borrower.first_name == "Jane"
    assert fields.employment.monthly_income == 6000.0
    assert fields.loan.loan_amount == 240000.0


def test_extract_1003_represents_missing_section_as_none():
    document = (FIXTURES_DIR / "missing_employment.json").read_text()
    fields = extract_1003(document)
    assert fields.employment is None
    assert fields.borrower is not None


def test_extract_1003_handles_unparseable_document_without_crashing():
    fields = extract_1003("this is not json at all")
    assert isinstance(fields, Fields)
    assert fields.borrower is None
    assert fields.employment is None
    assert fields.debts is None
    assert fields.loan is None


def test_extract_1003_represents_malformed_section_as_none_not_fatal():
    document = json.dumps(
        {
            "borrower": {"first_name": "Jane", "last_name": "Doe"},
            "employment": {"monthly_income": "not-a-number"},
        }
    )
    fields = extract_1003(document)
    assert fields.borrower.first_name == "Jane"
    assert fields.employment is None
