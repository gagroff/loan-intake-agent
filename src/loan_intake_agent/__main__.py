"""CLI entry point for the loan intake agent.

Subcommands are added as milestones land (`run` / `chat` still pending;
`run-evals` landed in P3.2).
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from collections.abc import Sequence

from loan_intake_agent import __version__


def _run_evals(args: argparse.Namespace) -> int:
    from loan_intake_agent.run_evals import main as run_evals_main

    return asyncio.run(run_evals_main())


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
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(dest="command")
    run_evals_parser = subparsers.add_parser(
        "run-evals", help="Score the eval set (guardrails + RAG) and print a pass/fail summary."
    )
    run_evals_parser.set_defaults(func=_run_evals)

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
