"""Typed schema for an extracted Form 1003.

Every section is optional: a source document missing a section should still
produce a valid `Fields`, not a validation error. Extraction represents
missing data as `None` rather than failing.
"""

from pydantic import BaseModel


class Borrower(BaseModel):
    first_name: str | None = None
    last_name: str | None = None


class Employment(BaseModel):
    employer_name: str | None = None
    years_employed: float | None = None
    monthly_income: float | None = None


class Debts(BaseModel):
    monthly_payments: float | None = None


class LoanProperty(BaseModel):
    loan_amount: float | None = None
    property_value: float | None = None
    property_address: str | None = None


class Fields(BaseModel):
    borrower: Borrower | None = None
    employment: Employment | None = None
    debts: Debts | None = None
    loan: LoanProperty | None = None


class Ratios(BaseModel):
    ltv: float | None = None
    dti: float | None = None


class Flag(BaseModel):
    code: str
    reason: str


class Flags(BaseModel):
    items: list[Flag] = []
