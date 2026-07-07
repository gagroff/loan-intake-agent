"""CLI entry point for the loan intake agent.

Phase 0 stub: proves `python -m loan_intake_agent --help` runs. Real
subcommands (`run`, `chat`, `run-evals`) land in later phases.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from loan_intake_agent import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loan-intake-agent",
        description=(
            "Extract a synthetic Form 1003, check underwriting guardrails, "
            "and answer grounded questions over lending guidelines."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    # Subcommands are added as milestones land (run / chat / run-evals).
    parser.set_defaults(func=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "func", None) is None:
        parser.print_help()
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
