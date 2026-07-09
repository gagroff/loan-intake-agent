"""Map a raw Form 1003 document (JSON text) to the typed `Fields` schema.

A document is untrusted input: it may be unparseable, missing sections, or
have malformed values in a section. None of that is fatal — extraction
degrades to `None` for whatever it can't read rather than raising, so a bad
document still produces a `Fields` a caller can inspect and flag.
"""

import json

from pydantic import ValidationError

from .schema import Borrower, Debts, Employment, Fields, LoanProperty

_SECTION_MODELS = {
    "borrower": Borrower,
    "employment": Employment,
    "debts": Debts,
    "loan": LoanProperty,
}


def extract_1003(document: str) -> Fields:
    try:
        data = json.loads(document)
    except (json.JSONDecodeError, TypeError):
        return Fields()

    if not isinstance(data, dict):
        return Fields()

    sections = {}
    for key, model in _SECTION_MODELS.items():
        raw_section = data.get(key)
        if raw_section is None:
            continue
        try:
            sections[key] = model.model_validate(raw_section)
        except ValidationError:
            sections[key] = None

    return Fields(**sections)
