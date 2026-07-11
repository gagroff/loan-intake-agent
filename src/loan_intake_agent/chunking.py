"""Split the markdown guideline corpus into citable chunks, one per numbered rule.

Each rule paragraph (``**Rule 1.1 — ...** ...``) becomes its own `Chunk`,
tagged with the enclosing `## ` section heading. Titles and blockquote
disclaimers are not citable content and are skipped.
"""

import re

from .schema import Chunk

_RULE_PATTERN = re.compile(r"\*\*Rule (\d+\.\d+) — [^*]+\*\*")


def chunk_guidelines(markdown_text: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    current_section: str | None = None

    for block in markdown_text.split("\n\n"):
        block = block.strip()
        if not block or block.startswith("# ") or block.startswith(">"):
            continue
        if block.startswith("## "):
            current_section = block[3:].strip()
            continue

        match = _RULE_PATTERN.match(block)
        if not match:
            continue

        chunks.append(Chunk(id=match.group(1), section=current_section, text=block))

    return chunks
