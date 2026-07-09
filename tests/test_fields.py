"""P1.1: Fields is a typed schema for an extracted Form 1003, with sensible optionals."""

import pytest
from pydantic import ValidationError

from loan_intake_agent.schema import Borrower, Debts, Employment, Fields, LoanProperty


def test_fields_constructs_with_no_data():
    # A doc missing every section must still produce a Fields instance, not raise.
    fields = Fields()

    assert fields.borrower is None
    assert fields.employment is None
    assert fields.debts is None
    assert fields.loan is None


def test_fields_constructs_with_full_data():
    fields = Fields(
        borrower=Borrower(first_name="Jane", last_name="Doe"),
        employment=Employment(employer_name="Acme Corp", years_employed=3.5, monthly_income=6000.0),
        debts=Debts(monthly_payments=800.0),
        loan=LoanProperty(loan_amount=300000.0, property_value=350000.0, property_address="123 Main St"),
    )

    assert fields.borrower.first_name == "Jane"
    assert fields.employment.monthly_income == 6000.0
    assert fields.debts.monthly_payments == 800.0
    assert fields.loan.loan_amount == 300000.0


def test_fields_with_partial_section_present():
    # A doc with only a borrower section populated still parses; other sections stay None.
    fields = Fields(borrower=Borrower(first_name="Jane"))

    assert fields.borrower.first_name == "Jane"
    assert fields.borrower.last_name is None
    assert fields.employment is None


def test_loan_property_rejects_wrong_type():
    with pytest.raises(ValidationError):
        LoanProperty(loan_amount="not-a-number")
