# Synthetic Underwriting Guidelines

> **This is a fictional guideline set written for a portfolio demo.** The rules,
> thresholds, and numbering below are invented for this project. They do not
> represent any real lender's policy and must never be treated as real
> underwriting guidance.

## 1. Loan-to-Value (LTV)

**Rule 1.1 — Maximum LTV.** The loan-to-value ratio (loan amount ÷ appraised
property value) must not exceed **80%**. LTV is expressed as a percentage
and rounded to the nearest whole point.

**Rule 1.2 — Why the threshold exists.** Loans above 80% LTV leave the
borrower with less than 20% equity in the property, which increases the
lender's loss exposure if the borrower defaults and the property must be
sold. Applications above the threshold are flagged as `high_ltv` for manual
underwriter review rather than automatic approval.

**Rule 1.3 — What happens on a flag.** A `high_ltv` flag does not mean the
loan is denied. It means the file is routed to a human underwriter, who may
approve it with compensating factors (e.g. mortgage insurance, a lower DTI,
or a larger reserve balance) — none of which this demo evaluates.

## 2. Debt-to-Income (DTI)

**Rule 2.1 — Maximum DTI.** The debt-to-income ratio (total monthly debt
payments ÷ gross monthly income) must not exceed **43%**.

**Rule 2.2 — Why the threshold exists.** A DTI above 43% indicates the
borrower is committing a large share of income to debt obligations, which
raises the risk of missed payments if income drops or expenses rise. This
43% line is the same "qualified mortgage" benchmark used broadly in the
real mortgage industry, chosen here because it is a well-known, defensible
number for a demo — not because this project models real policy.

**Rule 2.3 — What happens on a flag.** A `high_dti` flag routes the file to
manual review, same as a high-LTV flag. Both flags can fire on the same
application; each is evaluated independently.

## 3. Application completeness

**Rule 3.1 — Required sections.** A complete application must include all
four sections: **borrower**, **employment**, **debts**, and **loan/property**.
An application missing any one of these sections cannot be fully evaluated —
ratios that depend on a missing section (for example, DTI when the
employment section is absent) cannot be computed at all.

**Rule 3.2 — Why completeness is required.** LTV and DTI cannot be
calculated without their inputs. Rather than guessing or defaulting a
missing value to zero (which would silently understate risk), an
application missing a required section is flagged as `missing_section` per
missing section, naming which one, so the gap is visible and can be
resolved before underwriting proceeds.

## 4. Scope of these guidelines

**Rule 4.1 — What this document does not cover.** These guidelines cover
only LTV, DTI, and completeness — the three checks this project's guardrail
engine implements. Real underwriting also considers credit score, loan
purpose, occupancy type, property type, reserves, and many other factors;
none of those are modeled here. If asked about a rule not listed above, the
correct answer is that it is **not covered by these guidelines**, not a
guess.
