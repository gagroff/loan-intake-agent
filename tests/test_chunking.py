"""P2.2: chunk_guidelines splits the guideline corpus into citable passages."""

from pathlib import Path

from loan_intake_agent.chunking import chunk_guidelines

GUIDELINES_PATH = Path(__file__).parent.parent / "fixtures" / "guidelines" / "underwriting_guidelines.md"


def test_chunk_guidelines_splits_simple_doc_into_one_chunk_per_rule():
    text = (
        "# Title\n\n"
        "> A disclaimer.\n\n"
        "## 1. Section One\n\n"
        "**Rule 1.1 — First.** Some text about rule one.\n\n"
        "**Rule 1.2 — Second.** Some text about rule two.\n\n"
        "## 2. Section Two\n\n"
        "**Rule 2.1 — Third.** Some text about rule three.\n"
    )

    chunks = chunk_guidelines(text)

    assert [c.id for c in chunks] == ["1.1", "1.2", "2.1"]
    assert chunks[0].section == "1. Section One"
    assert chunks[2].section == "2. Section Two"
    assert "rule one" in chunks[0].text
    assert "rule three" in chunks[2].text


def test_chunk_guidelines_skips_title_and_disclaimer():
    text = "# Title\n\n> A disclaimer paragraph.\n\n## 1. Section\n\n**Rule 1.1 — X.** Body text.\n"

    chunks = chunk_guidelines(text)

    assert len(chunks) == 1
    assert "disclaimer" not in chunks[0].text.lower()


def test_chunk_guidelines_on_real_corpus_covers_every_guardrail_rule():
    text = GUIDELINES_PATH.read_text(encoding="utf-8")

    chunks = chunk_guidelines(text)

    ids = {c.id for c in chunks}
    assert {"1.1", "2.1", "3.1"}.issubset(ids)
    assert len(chunks) >= 8
    ltv_chunk = next(c for c in chunks if c.id == "1.1")
    assert "80%" in ltv_chunk.text
    dti_chunk = next(c for c in chunks if c.id == "2.1")
    assert "43%" in dti_chunk.text
