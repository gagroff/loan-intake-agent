"""Compute underwriting ratios (LTV, DTI) from extracted Fields.

A ratio is None whenever an input it depends on is missing or the
denominator is zero, rather than raising — consistent with extraction's
"missing is representable, not fatal" rule.
"""

from .schema import Fields, Ratios


def calc_ratios(fields: Fields) -> Ratios:
    ltv = None
    if fields.loan and fields.loan.loan_amount is not None and fields.loan.property_value:
        ltv = fields.loan.loan_amount / fields.loan.property_value

    dti = None
    if fields.debts and fields.employment and fields.debts.monthly_payments is not None and fields.employment.monthly_income:
        dti = fields.debts.monthly_payments / fields.employment.monthly_income

    return Ratios(ltv=ltv, dti=dti)
