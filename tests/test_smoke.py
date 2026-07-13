"""Phase 0 smoke tests: the package imports and the CLI runs green."""

from loan_intake_agent import __version__
from loan_intake_agent.__main__ import build_parser, main


def test_version_is_set():
    assert __version__ == "0.1.0"


def test_help_runs_and_exits_zero():
    # No subcommand -> prints help, returns 0 (does not raise SystemExit).
    assert main([]) == 0


def test_parser_builds():
    parser = build_parser()
    assert parser.prog == "loan-intake-agent"


def test_run_evals_subcommand_is_registered():
    parser = build_parser()
    args = parser.parse_args(["run-evals"])
    assert args.func is not None
