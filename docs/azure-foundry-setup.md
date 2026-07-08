# Microsoft Foundry setup — step by step (first-timer edition)

This is the click-by-click guide to provision the AI backend for this project: a **Microsoft Foundry**
project (formerly "Azure AI Foundry") with a **chat model** and an **embedding model** deployed, plus the
`.env` values the code needs.

You only do this once. Budget ~20–30 minutes. Cost for a portfolio project is a few dollars — you pay
per API call, not per hour, and nothing here runs when you're not using it.

> **What you're creating and why:**
> - A **Foundry resource + project** — the container Azure bills against and where models live.
> - A **chat model deployment** (`gpt-5-mini`) — the agent's reasoning + tool-calling brain.
> - An **embedding model deployment** (`text-embedding-3-small`) — turns guideline text into vectors for RAG.
> - An **endpoint URL + API key** — how our Python code talks to the above.

---

## Prerequisites

- A personal Microsoft/Azure account. If you don't have an Azure *subscription* yet, you'll create a free
  one during sign-up (it includes free credit; this project costs well under that).
- **Use your personal identity**, not any work account — this is portfolio work (see PRD §11).

---

## Step 1 — Sign in to the Foundry portal

1. Open a browser to **https://ai.azure.com**.
2. Click **Sign in** and use your **personal** Microsoft account.
3. If prompted to create/confirm an **Azure subscription**, follow the flow (you may need to add a card;
   the free tier won't charge without your say-so). A "Pay-As-You-Go" subscription is fine.
4. Dismiss any welcome/tour pop-ups. You should land on the Foundry home page.

---

## Step 2 — Create a project

1. On the home page, click **+ Create** (or **New project** / **Create project** — wording varies).
2. Give the project a name, e.g. **`loan-intake`**.
3. **Expand "Advanced options"** and set:
   - **Foundry resource**: a name like `loan-intake-foundry` (this is the billable Azure resource).
   - **Subscription**: your personal subscription.
   - **Resource group**: click **Create new** → name it `rg-loan-intake` (a resource group is just a
     folder for related Azure resources; keeping this project in its own group makes cleanup trivial).
   - **Region**: pick one from the **"recommended"** list. `East US 2` or `Sweden Central` usually have the
     widest model availability. If a model you want isn't offered later, the region is the usual reason.
4. Click **Create**. Provisioning takes a few minutes. Wait for it to finish and open the project.

---

## Step 3 — Deploy the chat model

1. In the left nav of your project, open **Model catalog** (may be under **Discover → Models**).
2. Filter/search the **OpenAI** collection for **`gpt-5-mini`**. (Any current small GPT-class chat model
   works — `gpt-5-mini` is cheap and more than enough here. If it's unavailable in your region, `gpt-4o-mini`
   is a fine substitute — just note the name.)
3. Open the model → click **Use this model** / **Deploy**.
4. Accept the default deployment settings. **Note the "Deployment name"** it gives you (usually matches the
   model, e.g. `gpt-5-mini`). **You'll need this exact string.**
5. Wait ~1 minute for **Succeeded**.

---

## Step 4 — Deploy the embedding model

1. Back in **Model catalog**, filter the **OpenAI** collection and search **`text-embedding-3-small`**.
   (If unavailable, `text-embedding-ada-002` works — note whichever name you use.)
2. Open it → **Use this model** / **Deploy** → accept defaults.
3. **Note this deployment name too.**
4. Wait for **Succeeded**.

You should now have **two deployments** listed under **Models + endpoints** (or **Deployments**).

---

## Step 5 — Grab the endpoint

1. Go to the project's **Home** / **Overview** page.
2. Find and copy the **Project endpoint** — a URL like
   `https://<resource>.services.ai.azure.com/api/projects/<project>`

You do **not** need the API key. `agent-framework`'s `FoundryChatClient` authenticates with an Azure
credential (`AzureCliCredential`), not a raw key — see Step 7.

---

## Step 6 — Fill in `.env` (never committed)

In the repo root:

```bash
cp .env.example .env
```

Open `.env` and paste your values:

```
FOUNDRY_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
FOUNDRY_CHAT_DEPLOYMENT=gpt-5-mini              # the exact name from Step 3
FOUNDRY_EMBEDDING_DEPLOYMENT=text-embedding-3-small   # the exact name from Step 4
```

`.env` is git-ignored (verified in `.gitignore`).

---

## Step 7 — Verify with the Azure CLI (required for auth)

From a terminal:

```bash
az login                 # opens a browser; sign in with the SAME personal account
az account show          # confirms which subscription you're on
```

This isn't just a sanity check — `scripts/foundry_spike.py` (P0.2) uses `AzureCliCredential`, which reads
this login to authenticate. Stay logged in via `az login` for local dev.

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Model not in the catalog | Wrong **region** — recreate the project in `East US 2` / `Sweden Central`, or pick a model offered in your region and note its name. |
| "Quota exceeded" on deploy | New subscriptions have low default quota; lower the deployment's tokens-per-minute, or request a quota bump in the deploy dialog. |
| 401 / auth errors later | Endpoint or key mismatched, or key regenerated. Re-copy both from the project Home page. |
| Can't find endpoint/key | Look under **Models + endpoints** → your deployment, or the project **Overview**. |

---

## When you're done

You have all four `.env` values filled and `az account show` succeeds. Tell me, and we'll do **P0.2**: pin
the exact `agent-framework` Foundry client in code and run a 10-line spike that makes a real tool call
against your deployment — the last gate before Phase 1.
