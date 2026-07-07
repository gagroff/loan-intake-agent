# Loan Intake Agent

> An agentic AI that reads a synthetic mortgage **Form 1003**, extracts it into a typed schema,
> checks underwriting **guardrails** (LTV, DTI, completeness), and answers grounded questions over a
> small lending-guidelines corpus — with an **eval harness** and **traces** so its quality is *measured*,
> not asserted.

**Status:** 🚧 In development (Phase 0 — scaffold). See [`docs/loan-intake-agent-plan.md`](docs/loan-intake-agent-plan.md).

This is a **proof of capability, not a production system**. All data is synthetic — zero PII, zero real
lending policy.

## What it does (target)

1. **Extract** — `extract_1003` maps a synthetic Form 1003 (text/JSON) into a typed `Fields` schema.
2. **Compute** — `calc_ratios` derives LTV and DTI.
3. **Check** — `check_guardrails` flags high LTV, high DTI, and missing required sections, each with a reason.
4. **Ground** — `search_guidelines` answers questions over an underwriting-guidelines corpus *with citations*,
   and declines when a fact isn't in the corpus.

An agent orchestrates these four tools; a single natural-language request routes through the right ones.

## Stack

- **Python 3.12**, packaged with **uv**
- **Microsoft Agent Framework** (`agent-framework`) on **Microsoft Foundry** (Azure AI Foundry) — `FoundryChatClient`
- In-memory / embedded vector store for RAG (grown-up swap: Azure AI Search)
- **pytest** for the deterministic core and evals

## Quickstart

```bash
# 1. Install dependencies (creates .venv automatically)
uv sync

# 2. Run the CLI
uv run loan-intake-agent --help

# 3. Run tests
uv run pytest
```

To use the LLM features you'll need a Microsoft Foundry project — see
[`docs/azure-foundry-setup.md`](docs/azure-foundry-setup.md), then copy `.env.example` to `.env` and fill it in.

## Engineering decisions

_(Populated as the build progresses — agent-vs-script, how RAG is grounded, how it's evaluated, and prompt-injection handling.)_

## License

MIT — see [LICENSE](LICENSE). Synthetic data only.
