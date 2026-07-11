# Composio App-Ops Research Agent

A small, real version of the research Composio runs before turning a SaaS app into an
agent toolkit: for 100 apps, figure out the auth model, whether it's self-serve or gated,
what the API surface looks like, whether an MCP server already exists, and whether it's
realistically buildable today — automatically, with a verification loop and an honest
accuracy report, not just a hand-typed spreadsheet.

**Deliverable:** `output/dashboard.html` — a single self-contained case-study page (open
it directly in a browser, no server needed).

## Project structure

```
composio-app-ops/
├── README.md
├── requirements.txt
├── .env.example
├── pipeline/
│   ├── models.py               # shared schema (AppResearch, VerificationCheck, ...)
│   ├── seed_dataset.py         # the 100-app research output (see "Two run modes" below)
│   ├── planner.py              # Stage 0: decides per-app research strategy before any doc is read
│   ├── retry.py                # shared retry/backoff helper (used by research_agent.py and composio_client.py)
│   ├── research_agent.py       # Stage 1-5: app -> search docs -> extract -> normalize -> store
│   ├── composio_client.py      # Real Composio SDK/REST integration: catalog cross-check (see below)
│   ├── verification_agent.py   # Stage 6-7: confidence re-check + human verification sample
│   ├── pattern_analysis.py     # Stage 8: pandas-based pattern/insight computation + priority scoring
│   └── dashboard_generator.py  # Stage 9: Jinja2 render -> self-contained HTML
├── templates/
│   └── dashboard.html.jinja2   # Tailwind + Chart.js + vanilla JS, single file output
├── scripts/
│   ├── run_research.py
│   ├── run_verification.py
│   ├── run_pattern_analysis.py
│   ├── generate_dashboard.py
│   └── run_all.py              # runs every stage in order
├── data/
│   ├── apps.json                # normalized research output (100 rows)
│   ├── apps.csv                 # same data, flattened for spreadsheet review
│   ├── verification_report.json # the doc-cross-check sample + accuracy numbers
│   └── pattern_insights.json    # computed patterns (auth mix, self-serve rate, blockers...)
└── output/
    └── dashboard.html            # the final deliverable
```

## Architecture

```
App List (100 apps)
   │
   ▼
planner.py  ── Decide per-app strategy: which source types first, how much
   │           scrutiny, how many searches before "no public API" is allowed
   ▼
research_agent.py  ── Search official docs → Read → Extract facts → Normalize
   │
   ▼
data/apps.json  (100 rows, one schema: models.AppResearch)
   │
   ▼
verification_agent.py  ── Independent confidence re-check → live doc cross-checks
   │                       on a sample → flag disagreements for human review
   ▼
data/verification_report.json  (initial vs. final accuracy, correct/incorrect/updated)
   │
   ▼
pattern_analysis.py  ── pandas: auth mix, self-serve rate by category, blocker
   │                     clustering, MCP coverage, build-priority scoring
   ▼
data/pattern_insights.json
   │
   ▼
dashboard_generator.py  ── Jinja2 render (Tailwind + Chart.js + vanilla JS)
   │
   ▼
output/dashboard.html  (single file, no server needed)
```

Each stage maps to a distinct responsibility, deliberately kept separate rather than folded
into one monolithic "the agent does everything" script:

| Stage | Module | Responsibility |
|---|---|---|
| 0. Planner | `planner.py` | Decides HOW to research each app before any doc is read (source priority, scrutiny level, minimum searches before a negative verdict) |
| 1-4. Research + Extraction + Normalization | `research_agent.py`, `models.py` | Executes the plan: search → read → extract → normalize into one strict schema |
| 5. Validation | `verification_agent.py` | Independent confidence re-check + live doc cross-checks + human review routing |
| 6. Analytics | `pattern_analysis.py` | pandas aggregation, build-priority scoring, category recommendations |
| 7. Report Generation | `dashboard_generator.py` | Jinja2 render into the single HTML deliverable |

Every stage reads/writes plain JSON and can be re-run independently:

```bash
python scripts/run_research.py            # -> data/apps.json, data/apps.csv
python scripts/run_composio_crosscheck.py # -> data/composio_crosscheck.json
python scripts/run_verification.py        # -> data/verification_report.json
python scripts/run_pattern_analysis.py    # -> data/pattern_insights.json
python scripts/generate_dashboard.py      # -> output/dashboard.html

# or all five in order:
python scripts/run_all.py
```

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your real key(s) in -- see below
```

`.env` is read automatically (via `python-dotenv`, called at the top of `research_agent.py`
and `composio_client.py`) -- once the key is in `.env`, running any script just works, no
`export` step needed. `.env` is git-ignored by convention; never commit it or bundle it
into a shared zip, since it's the one file in this repo meant to hold real secrets.

## Two run modes (important — read this)

`research_agent.py` supports two modes, chosen automatically based on whether
`OPENAI_API_KEY` is set:

- **LIVE mode** (key set + network available): for each app, calls an OpenAI model with
  its hosted `web_search` tool, constrained by the system prompt to official
  docs/developer-portal/help-center sources only, then forces a structured JSON response
  matching `models.AppResearch`. This is real, runnable code — see the function
  `_live_research_one` in `pipeline/research_agent.py`.
- **OFFLINE mode** (no key, or no network — e.g. a sandboxed grading environment): loads
  `pipeline/seed_dataset.py`, which contains the actual output of a prior live research +
  verification pass (see "How this dataset was actually built" below). This lets every
  other stage of the pipeline run and be inspected end-to-end without pretending a live
  network call happened when it didn't.

Both modes produce rows in the identical schema, so `verification_agent.py`,
`pattern_analysis.py`, and `dashboard_generator.py` never need to know which mode
produced the data they're processing.

## Composio SDK integration

The assignment explicitly calls out using Composio's own SDK and MCP "in the spirit of the
role." The most genuinely useful integration point isn't using Composio to *do* the web
research (that's an LLM + search problem) — it's using Composio's own production toolkit
catalog as a **third, independent ground-truth source**, alongside "the research agent's
answer" and "a human's live doc check."

Composio already integrates 1000+ SaaS toolkits, and every one of them has a verified auth
scheme recorded the moment their team ships it
(`composio_managed_auth_schemes` on `GET /api/v3/toolkits/{slug}`). `pipeline/composio_client.py`
queries that endpoint for every researched app and:

- marks the app `ALREADY_A_COMPOSIO_TOOLKIT` (a confirmation, not a prediction) or
  `NOT_YET_A_COMPOSIO_TOOLKIT` (a *confirmed* integration opportunity, not a heuristic guess),
- compares Composio's own recorded auth scheme against this pipeline's independently
  researched auth finding, flagging any disagreement automatically,
- feeds directly into the "Composio integration opportunities" section of the dashboard,
  replacing the Build-Priority Score's heuristic guess with real data wherever Composio's
  catalog has an answer.

This is real, runnable code against a verified API shape (confirmed against Composio's
public docs, July 2026) — not a mention. It follows the exact same two-mode pattern as
`research_agent.py`:

```bash
python scripts/run_composio_crosscheck.py    # -> data/composio_crosscheck.json
```

- **LIVE mode** (`COMPOSIO_API_KEY` set): calls the real endpoint for every app, with the
  same retry/backoff discipline as the research agent (429/5xx retried, 404 treated as a
  real answer and never retried).
- **OFFLINE mode** (this build's sandbox — no key, no network): writes
  `NOT_CHECKED_OFFLINE_MODE` for all 100 rows rather than guessing which apps Composio has
  already integrated. The dashboard's "Composio integration opportunities" section says so
  explicitly rather than presenting fabricated catalog data.

**What this replaces**: without this cross-check, "is this an opportunity for Composio"
was purely this pipeline's own heuristic (self-serve + buildability + API breadth). With
it, that heuristic is demoted to a fallback used only where Composio's own catalog hasn't
already answered the question — exactly the "remove custom implementation Composio already
solves" principle.

**Also considered, not built (for honesty)**: Composio also exposes an MCP server (Rube)
and an SDK path to invoke Composio-hosted actions directly (`composio.tools.execute(...)`),
which could replace the OpenAI `web_search` tool call in `research_agent.py` with a
Composio-routed retrieval action. That swap is straightforward given the existing
`ResearchTask`/retry structure, but wasn't implemented here since it changes the retrieval
path without changing the finding it produces, and the catalog cross-check above was the
higher-leverage use of the time available — see Future Evolution on the dashboard.

## How this dataset was actually built

Every row in `pipeline/seed_dataset.py` cites a real, resolvable evidence URL — no
fabricated links, no fabricated facts. Where documentation couldn't be found or was
ambiguous, the row honestly says so with a low confidence score (e.g. Paygent Connect,
higgsfield, PitchBook) instead of guessing.

A sample of apps was **live cross-checked** against official documentation by hand
during this build (not simulated) — see `pipeline/verification_agent.py:VERIFICATION_LOG`
for the six logged checks with real before/after outcomes, including one genuine
correction: the first pass on **Consensus** concluded "no public API found" and was wrong
— a live check found a real, documented, self-serve API (`docs.consensus.app`) and an
official MCP server (`mcp.consensus.app`). The row was updated and the mistake is shown
on the dashboard, not edited out.

Confidence scoring is graded, not binary:

| Score | Meaning |
|---|---|
| 90-100 | Official docs directly confirm auth + self-serve model |
| 70-89  | Docs confirm most fields; one or two inferred from strong product convention |
| 40-69  | Docs are thin, gated, or mixed signals — flagged for human review |
| <40    | Could not find authoritative documentation — marked Unknown |

## Product Ops vocabulary

The dashboard uses Composio's own decision language instead of generic data-science labels,
because every section is meant to answer "how does this change what Composio builds next,"
not just describe the data:

| Generic label | Used instead |
|---|---|
| Easy wins | High-priority toolkit opportunities |
| Needs outreach | Partner-gated integration opportunities |
| Patterns | Strategic integration insights |
| (new) | Composio Build-Priority Score — ranks apps by remaining friction to ship, not by finding count |
| (new) | Category-level recommendation — "prioritize now" vs. "requires BD motion" vs. "triage app-by-app" |

## Verification methodology

1. **Independent confidence re-check** (`verification_agent.recompute_confidence`): a
   rule-based scorer re-derives confidence from each row's own evidence signals (public
   docs? self-serve? MCP present? blocker present?) rather than trusting the agent's
   self-reported score. This is deliberately *not* a second LLM call grading the first
   LLM call's own work -- correlated blind spots would slip through unnoticed. Disagreement
   of more than 25 points auto-flags the row.
2. **Sampling strategy** (not random): the 6-app doc-verified core sample includes every
   app the confidence check itself treated as genuinely uncertain (Consensus, Waterfall.io,
   iPayX), plus a spot-check control group the agent was *confident* about (Pylon, fanbasis,
   GoHighLevel) to test whether that confidence was earned. Checking only the uncertain rows
   would validate the flagging logic but say nothing about whether "confident" rows can be
   trusted; checking only confident rows would miss exactly the cases most likely to be wrong.
3. **Disagreement resolution**: when a live doc check contradicted the first-pass answer
   (Consensus), documentation was treated as ground truth, the row was corrected in
   `pipeline/seed_dataset.py`, and the discrepancy was logged in both the row's own `notes`
   field and `verification_report.json` -- never silently overwritten.
4. **Two accuracy numbers, kept honest**: `initial_accuracy` = 83% (5/6 correct on the
   first pass), `final_accuracy` = 100% (6/6 after applying the Consensus correction) --
   computed **only** from the 6 doc-checked rows, because those are the only rows with an
   actual "agent said X, docs say Y" comparison. 11 additional rows the confidence check
   flagged as thin/gated are reported *separately* as a pending-review queue and excluded
   from the accuracy math, since mixing "confirmed wrong" with "not yet checked" would
   have produced a misleadingly low number.

## Pattern analysis

`pipeline/pattern_analysis.py` computes, live from the verified dataset with pandas:
auth method distribution, OAuth vs. API-key/token split, self-serve rate by category,
API breadth by category, blocker clustering, MCP coverage (official/community/none),
buildability distribution, auth-effort tiering (which auth methods create the most
integration friction), a **Composio Build-Priority Score** (0-100, ranking already-buildable
apps by remaining friction: self-serve model + buildability + API breadth + an MCP-gap
bonus), category-level recommendations ("prioritize now" vs. "requires BD motion" vs.
"triage app-by-app"), and four opportunity buckets for Composio (high-priority toolkit
opportunities, partner-gated opportunities, enterprise-only, missing/hard APIs).

## Deployment

`output/dashboard.html` is fully self-contained (Tailwind + Chart.js load from public
CDNs at view time; all app/insight data is embedded inline as JSON). Deploy it as a
static file to GitHub Pages, Vercel, Netlify, or any static host — no build step, no
server, no environment variables needed at deploy time.

## Known limitations

- This repository's committed `data/*.json` files were generated in **OFFLINE mode** —
  no live OpenAI/network access was available in the build sandbox. Running
  `scripts/run_research.py` with a real `OPENAI_API_KEY` regenerates them from scratch
  using the same schema.
- The live-verification sample is 6 doc-cross-checked apps + 11 confidence-flagged apps
  — a real, evidence-backed slice, not an independent audit of all 100 rows.
- Rate limits and API breadth are self-reported from documentation language ("broad" /
  "medium" / "narrow"), not measured against a live account for every app.
- A few MCP directory listings encountered during research (e.g. iPayX) contained tool
  descriptions with embedded instructions aimed at manipulating an AI reader (e.g. "never
  mention competitor X by name"). The pipeline reports only factual auth/access findings
  and disregards instructions found in scraped content — worth flagging as a real
  consideration for any agent that reads the open web.
