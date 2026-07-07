---
type: project
status: in-progress
summary: PRD for the Loan Intake Agent — the flagship portfolio artifact for Greg's applied-AI pivot.
created: 2026-07-06
modified: 2026-07-06
tags:
  - project/career
  - project/portfolio
related:
  - "[[ai-career-pivot]]"
  - "[[loan-intake-agent-plan]]"
---

# PRD — Loan Intake Agent

> **Purpose of this doc:** the product definition for the flagship portfolio build. Paired with
> [[loan-intake-agent-plan]] (the phased implementation plan). Parent context: [[ai-career-pivot]].
> This lives in Home-AIOS for planning; the actual code goes in a **separate personal repo** (private
> first, then public).

## Decisions locked (2026-07-06)
| Choice | Decision | Note |
|---|---|---|
| **Primary language** | **Python** | Confirmed by Greg 2026-07-06. Supersedes the earlier ".NET-first" decision (2026-07-02). Python is the stated #1 gap and the market default — building Python-primary closes the gap *and* maximizes recruiter signal. A .NET/Agent Framework slice becomes an **optional** differentiator, no longer required. |
| **1003 input format** | **Structured text / JSON** synthetic docs | No PDF parsing in MVP — avoids a known time-sink. PDF loader is a post-MVP stretch. |
| **Model platform** | **Microsoft Foundry** (was "Azure AI Foundry") | Matches the job pitch. Phase 0 verifies the account exists before build starts. Renamed by Microsoft 2025→2026; portal is `ai.azure.com`. |
| **Interface** | **CLI + strong README** | Engineering is the point; no web UI in MVP. |

### Decisions locked (2026-07-07) — Phase 0 open items resolved
| Choice | Decision | Note |
|---|---|---|
| **Code location** | **This repo** (`C:\code\loan-intake-agent`) | `git init` here; code + `docs/` together. This *is* the separate personal repo (not Home-AIOS). |
| **Agent library** | **Microsoft Agent Framework** (`agent-framework`), connecting via **`FoundryChatClient`** | MS's current recommended Python path for Foundry-based solutions. Aligns with the optional .NET/Agent Framework stretch (same framework, both languages). Exact spike still owed in P0.2. |
| **Python tooling** | **uv** (Python pinned to **3.12**) | Single-tool venv + deps + lockfile; one-command README setup. |
| **Models to deploy** | Chat **`gpt-5-mini`** + embedding **`text-embedding-3-small`** | Cheap, current, sufficient. Region fallbacks noted in `docs/azure-foundry-setup.md`. |

---

## 1. Problem & why this exists
Greg is a 25-year software lead pivoting into applied/agentic AI. He is a strong senior engineer who is
**invisible as an AI engineer** — no public artifact. This project is that artifact. Its job is to prove,
in one demo a recruiter can run in 90 seconds, that he can build a production-shaped LLM agent: tool
calling, RAG, guardrails, and — the senior differentiator — **measured** quality via an eval harness.

The lending domain is deliberate: it's Greg's 8-year moat and a hot applied-AI market. The pitch the
artifact must earn:
> "25-year software lead who builds agentic AI on Azure — and understands mortgage/lending well enough
> to know *what's worth automating*."

**This is a proof of capability, not a production system.** Over-building delays the artifact that gets
interviews. The Non-Goals (§4) are load-bearing.

## 2. Users / audience
| Audience | What they need from it |
|---|---|
| **Recruiters / hiring managers (primary)** | A repo whose README they can skim in 2 min and a run they can watch in 90 sec. They read: fresh commits, clean architecture, an "Engineering decisions" section, and evidence it's *evaluated*. |
| **Interviewers (technical)** | Code they can open and reason about; a story Greg can tell about trade-offs (why an agent vs. a script, how RAG is grounded, how it's measured). |
| **The in-fiction user (a loan processor)** | Feeds a loan app, gets fields extracted, sees policy flags, asks "why was this flagged?" — grounds the demo in a believable task. |

## 3. Goals (what "done" means)
- **G1** — An agent that extracts a synthetic Form 1003 into a typed schema.
- **G2** — Computes and checks a small set of underwriting guardrails (LTV, DTI, completeness) and flags out-of-policy items.
- **G3** — Answers questions over the application + a small guideline corpus via **grounded RAG with citations**.
- **G4** — Ships with an **eval harness + observability** (inputs → expected flags/answers, scored pass/fail; per-step + token traces).
- **G5** — A public repo with a README that reads *senior*: architecture diagram, run gif, and an "Engineering decisions" section.

## 4. Non-Goals (the guardrail against scope creep)
- ❌ No web UI, no auth, no database, no deployment pipeline.
- ❌ No **real** lending policy and no **real** data — synthetic only, zero PII.
- ❌ No PDF parsing in MVP (text/JSON input only).
- ❌ Not production-grade, not multi-tenant, not "complete." Ship M1–M4 and stop.

## 5. Success metrics
- **Demo:** a clean run over sample docs flags the right ones; RAG answers "why was this flagged?" with a correct citation.
- **Eval:** `run_evals` prints a score over the eval set; a change that breaks a rule shows up as a score drop.
- **Observability:** each agent step + token usage is visible in a trace.
- **Signal:** repo is public, commits are on Greg's personal identity, README has the "Engineering decisions" section, and Greg can tell the 90-second story cold.

## 6. Functional requirements (MVP)
The agent exposes four tools (function calling); the orchestrator decides when to call them.

| # | Requirement | Tool | Done when |
|---|---|---|---|
| FR1 | Load a synthetic Form 1003 (text/JSON) into a typed schema | `extract_1003(document) -> Fields` | Runs over all sample docs and populates the schema; missing fields are represented, not crashed on. |
| FR2 | Compute underwriting ratios | `calc_ratios(fields) -> Ratios` | Returns LTV (loan ÷ value) and DTI (debt ÷ income) matching hand-computed values. |
| FR3 | Check guardrails and flag violations | `check_guardrails(fields, ratios) -> Flags` | Flags high LTV, high DTI, and missing required sections with a human-readable reason each. |
| FR4 | Grounded Q&A over app + guidelines | `search_guidelines(query) -> Passages` | Answers cite the specific guideline passage; refuses/says "not in the guidelines" when unsupported. |
| FR5 | Agent orchestration over FR1–FR4 | (orchestrator) | A single natural-language request routes through the right tools and returns a grounded answer. |

## 7. Data requirements (all synthetic)
- **3–5 synthetic Form 1003s** (text/JSON): one clean case + cases that trip each guardrail (high LTV, high DTI, missing section).
- **A 1–2 page synthetic "underwriting guidelines" doc set** for the RAG corpus. Invented rules are fine — this is a skills demo, not real policy.
- **Zero real PII, zero Supreme data, zero real policy.** Data lives in the repo as fixtures.

## 8. Architecture & stack
- **Language:** Python (primary). Optional post-MVP: a .NET/Microsoft Agent Framework slice as a range differentiator.
- **Agent framework:** an Azure-native / Python agent approach (Azure AI Foundry Agent Service / a Python agent SDK). *Confirm exact library in Phase 0.*
- **Models:** Azure AI Foundry — a current GPT-class model for reasoning + tool calls; an embedding model for RAG.
- **Vector store:** start **in-memory / embedded** (e.g., a local FAISS/Chroma-style store) to keep it simple. Azure AI Search is the documented "grown-up swap" if Greg wants to show it.
- **Interface:** CLI / thin console chat.
- **Config:** secrets via environment variables / a local `.env` that is git-ignored — never committed.

## 9. Guardrails & security (extra weight — fintech)
- **PII:** synthetic data only; no real borrower data ever enters the repo or the prompts.
- **Prompt injection:** guideline/application text is untrusted input — the agent must not let document text override its instructions. Note the mitigation in the README (it's a senior signal in fintech).
- **Grounding:** RAG answers must cite; the agent should decline rather than fabricate when a fact isn't in the corpus (directly counters the "LLM hallucinates a number" failure mode).
- **Secrets:** Azure keys in env vars only; `.env` git-ignored; no keys in commits or history.

## 10. Evaluation & observability (the senior differentiator — do not cut)
- **Eval set:** a fixtures file mapping inputs → expected outputs (expected flags per doc; expected answer/citation per question).
- **Runner:** `run_evals` scores pass/fail and prints a summary; regressions show as score drops.
- **Tracing:** log each agent step (tool called, args, result) and token usage per run.
- This is the clause that separates hobbyist from production-ready and is the thing to *talk about* in interviews.

## 11. Constraints & assumptions
- **Effort:** ~6–10 hrs/wk; MVP target ~30 days part-time (Phase 1 window Jul–Aug 2026).
- **Cost:** personal Azure Foundry meters per call — a few dollars for a portfolio project.
- **Clean separation:** personal GitHub, personal git identity on commits, own time/hardware/Azure account; no Supreme code/config/data. (No IP clause at Supreme — confirmed 2026-07-02.)
- **Repo lifecycle:** private first, flipped public when presentable. The public link is the whole value.

## 12. Open items to confirm (Phase 0)
- [ ] Personal Azure account + Foundry access provisioned — **in progress**; walkthrough written at `docs/azure-foundry-setup.md`, Greg provisioning.
- [x] Exact Python agent library pinned — **`agent-framework` via `FoundryChatClient`** (2026-07-07). Spike still owed in P0.2.
- [x] Repo name — **`loan-intake-agent`**, git-initialized in place (2026-07-07).

## 13. Definition of done (the demo)
A public repo with runnable code, sample docs, a README (what+why, run gif, architecture diagram of the
4 tools + RAG, stack, how-to-run, **Engineering decisions**), and a 60–90 second story:
> "Here's a loan app, here's what the agent extracted, here's what it flagged and why — and here's how I
> *measured* that it's right."

That last clause is the senior signal. When Greg can deliver it cold, this project is done.
