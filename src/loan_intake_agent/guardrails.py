"""Check extracted Fields + Ratios against underwriting guardrails.

Each guardrail produces a Flag with a human-readable reason. A missing
section only produces a "missing_section" flag — it never also drives a
ratio flag, since calc_ratios already returns None when its inputs are
absent.
"""

from .schema import Fields, Flag, Flags, Ratios

LTV_THRESHOLD = 0.80
DTI_THRESHOLD = 0.43

_REQUIRED_SECTIONS = ["borrower", "employment", "debts", "loan"]


def check_guardrails(fields: Fields, ratios: Ratios) -> Flags:
    items: list[Flag] = []

    if ratios.ltv is not None and ratios.ltv > LTV_THRESHOLD:
        items.append(
            Flag(
                code="high_ltv",
                reason=f"LTV of {ratios.ltv:.0%} exceeds the {LTV_THRESHOLD:.0%} threshold.",
                guideline_ref="1.1",
            )
        )

    if ratios.dti is not None and ratios.dti > DTI_THRESHOLD:
        items.append(
            Flag(
                code="high_dti",
                reason=f"DTI of {ratios.dti:.0%} exceeds the {DTI_THRESHOLD:.0%} threshold.",
                guideline_ref="2.1",
            )
        )

    for section in _REQUIRED_SECTIONS:
        if getattr(fields, section) is None:
            items.append(
                Flag(
                    code="missing_section",
                    reason=f"Required section '{section}' is missing from the application.",
                    guideline_ref="3.1",
                )
            )

    return Flags(items=items)
