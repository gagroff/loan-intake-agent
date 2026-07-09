---
type: project
status: in-progress
summary: Phased implementation plan (phases → tasks, each with a done-when) for the Loan Intake Agent.
created: 2026-07-06
modified: 2026-07-06
tags:
  - project/career
  - project/portfolio
related:
  - "[[ai-career-pivot]]"
  - "[[loan-intake-agent-prd]]"
---

# Implementation Plan — Loan Intake Agent

> Paired with [[loan-intake-agent-prd]]. Build it **Python-first**, in a **separate personal repo**
> (private → public). Each task has a **done-when**. Ship M1→M4 and stop — the Non-Goals in the PRD are
> the guardrail. Work order: environment → engineering skeleton → AI → measurement → publish.

**Principle:** build the deterministic engine (schema, ratios, guardrails, eval) *before* wiring the LLM.
When the LLM misbehaves, you want a trustworthy oracle to measure it against.

---

## Phase 0 — Environment & scaffold  (~½ week)
Get the repo and Azure ready so no later phase stalls on setup.

- [x] **P0.1 — Provision Azure Foundry.** *Done when:* a personal Azure account exists with a deployed chat model + an embedding model, and their names/keys are captured in a local (git-ignored) `.env`. — Done 2026-07-07: `loan-intake` Foundry project, `gpt-5-mini` + `text-embedding-3-small` deployed, endpoint in `.env` (auth via `az login`, no key needed).
- [x] **P0.2 — Pin the agent library.** *Done when:* the exact Python agent approach is chosen (Foundry Agent Service vs. a lightweight agent SDK) and a 10-line "hello, tool call" spike runs against Foundry. — Done 2026-07-07: `agent-framework` + `FoundryChatClient` (from `agent_framework_foundry`, not `agent_framework.azure`), auth via `AzureCliCredential`/`az login` (no API key). Spike at `scripts/foundry_spike.py`.
- [x] **P0.3 — Create the repo (private).** *Done when:* `loan-intake-agent` exists on Greg's **personal** GitHub, private, with git configured to his **personal** email/identity for this repo. — Done 2026-07-07: github.com/gagroff/loan-intake-agent, private, commits under Greg Groff / gagroff@hotmail.com.
- [x] **P0.4 — Project skeleton.** *Done when:* Python project scaffolds (venv/uv or poetry), `.gitignore` covers `.env` + secrets, README stub + LICENSE present, `pytest` runs green on a trivial test. — Done 2026-07-07: uv-managed venv, `.gitignore` covers `.env`/secrets, README + MIT LICENSE present, `pytest` passes (3 tests).
- **Exit:** ✅ `python -m loan_intake_agent --help` runs; a trivial LLM call to Foundry succeeds (`scripts/foundry_spike.py`).

## Phase 1 — M1: Extraction + guardrails (deterministic core)  (~1–1.5 weeks)
The engine, no LLM reasoning yet — pure, testable logic.

- [x] **P1.1 — Typed schema.** Define `Fields` (borrower, income, debts, loan amount, property value, employment section, etc.). *Done when:* the schema is a typed model (dataclass/pydantic) with sensible optionals. — Done 2026-07-09: `src/loan_intake_agent/schema.py`, pydantic `BaseModel`s (`Borrower`, `Employment`, `Debts`, `LoanProperty`, `Fields`), every field/section optional so a missing section is `None` not a crash. Tests in `tests/test_fields.py`.
- [x] **P1.2 — Synthetic 1003 fixtures.** Create 3–5 text/JSON sample apps: 1 clean, + high-LTV, high-DTI, missing-section cases. *Done when:* all fixtures load into `Fields`. — Done 2026-07-09: 4 JSON fixtures in `fixtures/1003/` (`clean`, `high_ltv` ~95% LTV, `high_dti` 50% DTI, `missing_employment` — no employment section). Loader tests in `tests/test_fixtures.py` validate each via `Fields.model_validate`.
- [x] **P1.3 — `extract_1003`.** Map a document to `Fields`. *Done when:* runs over every fixture without crashing; missing fields are represented, not fatal. — Done 2026-07-09: `src/loan_intake_agent/extract.py`. Parses JSON text section-by-section; unparseable documents, non-dict payloads, missing sections, and malformed sections all degrade to `None` instead of raising (document text is untrusted input). Tests in `tests/test_extract.py`.
- [ ] **P1.4 — `calc_ratios`.** Compute LTV and DTI. *Done when:* outputs match hand-computed values in a unit test.
- [ ] **P1.5 — `check_guardrails`.** Flag high LTV, high DTI, and missing required sections, each with a human-readable reason. *Done when:* flags the right docs and only those; covered by unit tests.
- **Exit / M1 done:** `run` over all sample docs prints the correct flags. Committed with tests.

## Phase 2 — M2: Agent + RAG chat  (~1.5–2 weeks)
Now the LLM — wire the four tools and ground answers in the guideline corpus.

- [ ] **P2.1 — Guideline corpus.** Write the 1–2 page synthetic underwriting guidelines. *Done when:* it contains the rules the guardrails enforce (so answers can cite them).
- [ ] **P2.2 — Embed + index.** Chunk + embed the guidelines into an in-memory/embedded vector store. *Done when:* a similarity query returns the relevant passage.
- [ ] **P2.3 — `search_guidelines` tool.** Retrieval over the corpus. *Done when:* returns grounded passages for a test query.
- [ ] **P2.4 — Agent orchestration.** Register `extract_1003`, `calc_ratios`, `check_guardrails`, `search_guidelines` as tools; let the agent route. *Done when:* one NL request flows through the right tools to a grounded answer.
- [ ] **P2.5 — Grounding + injection guardrails.** Answers cite passages; the agent declines when a fact isn't in the corpus; document text can't override instructions. *Done when:* "why was this flagged?" cites the guideline, and an out-of-corpus question gets an honest "not in the guidelines."
- **Exit / M2 done:** CLI chat answers "what's the max LTV for this loan type?" and "why was this flagged?" with citations.

## Phase 3 — M4: Eval + observability (the senior signal)  (~1 week)
> Sequenced before the optional .NET slice because it's required and it's the hiring differentiator.

- [ ] **P3.1 — Eval set.** Fixtures mapping inputs → expected outputs (expected flags per doc; expected answer/citation per question). *Done when:* the file covers each guardrail + a couple of RAG questions.
- [ ] **P3.2 — `run_evals` runner.** Scores pass/fail and prints a summary. *Done when:* it prints a score, and deliberately breaking a rule drops the score.
- [ ] **P3.3 — Tracing.** Log each agent step (tool, args, result) + token usage per run. *Done when:* a run emits a readable trace and a token count.
- **Exit / M4 done:** `run_evals` prints a score; traces are visible. **This is the interview talking point.**

## Phase 4 — Publish  (~½–1 week)
Make it legible to a recruiter and flip it public.

- [ ] **P4.1 — README.** What+why, run **gif**, architecture diagram (4 tools + RAG), stack, how-to-run, and an **"Engineering decisions"** section (agent-vs-script, how RAG is grounded, how it's evaluated, injection handling). *Done when:* a stranger could run it and understand the choices.
- [ ] **P4.2 — Clean-separation pass.** No secrets in history; `.env` ignored; synthetic data only; personal identity on all commits. *Done when:* `git log` shows personal email and history scans clean.
- [ ] **P4.3 — Flip public.** *Done when:* repo is public and the link is added to [[ai-career-pivot]] + LinkedIn.
- [ ] **P4.4 — 90-second story.** Rehearse the extract→flag→why→measured narrative. *Done when:* Greg can tell it cold.
- **Exit:** public repo + rehearsed demo = the flagship artifact is live.

## Optional stretch (post-MVP, only if time) — .NET / Agent Framework slice
- [ ] Re-implement one path (extraction+guardrails *or* the RAG path) in .NET on Microsoft Agent Framework. *Done when:* a .NET entry point runs end-to-end. **Value:** range signal (Python + .NET/Foundry). Skip if it delays going to market.
- [ ] Stretch: swap the in-memory store for **Azure AI Search**; add a PDF loader for real 1003s.

---

## Timeline (fits the ~6–10 hrs/wk, ~30-day MVP window)
| Phase | Focus | Rough duration |
|---|---|---|
| 0 | Environment & scaffold | ~½ wk |
| 1 (M1) | Extraction + guardrails | ~1–1.5 wk |
| 2 (M2) | Agent + RAG | ~1.5–2 wk |
| 3 (M4) | Eval + observability | ~1 wk |
| 4 | Publish | ~½–1 wk |
| — | Optional .NET slice | post-MVP |

## Immediate next action
**P0.1 + P0.3** — confirm/provision the personal Azure Foundry account and create the private
`loan-intake-agent` repo with your personal git identity. Everything else unblocks from there.
