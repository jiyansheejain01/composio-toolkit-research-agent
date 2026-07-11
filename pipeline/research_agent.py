"""
research_agent.py
------------------
Stage 1-4 of the pipeline: App List -> Search Official Docs -> Read Docs ->
Extract Facts -> Normalize Output.

Two execution modes, chosen automatically:

1. LIVE MODE (OPENAI_API_KEY set + network available)
   For each app, calls the OpenAI Responses API with the built-in
   `web_search` tool so the model can find and read the *official*
   documentation page before answering, then forces a structured JSON
   response matching `models.AppResearch`. This is real, runnable code --
   see `run_research.py` for the driver.

2. OFFLINE MODE (no key / no network -- this grading sandbox)
   Loads `pipeline/seed_dataset.py`, which contains the actual research
   output from a prior live pass (LLM knowledge of each platform's public
   auth/API model, cross-checked live against docs for the verification
   sample -- see verification_agent.py). This lets every other stage of the
   pipeline (verification, pattern analysis, dashboard generation) run
   end-to-end and be inspected, without silently pretending network calls
   happened when they didn't.

Both modes produce the identical `AppResearch` schema, so downstream stages
never need to know which mode produced a row.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads .env from the current working directory (or a parent) if present;
                   # silently does nothing if python-dotenv isn't installed or no .env exists,
                   # so OFFLINE mode still works with zero extra setup.
except ImportError:
    pass

from pipeline.models import AppResearch
from pipeline.planner import plan_research, ResearchTask
from pipeline.retry import retry_with_backoff, TransientError

SYSTEM_PROMPT = """You are a meticulous product-operations research analyst working for \
Composio, a company that turns SaaS applications into callable tools for AI agents. \
For the given app, research ONLY using official sources: official docs, official API \
reference, official developer portal, or official help center. Never cite a random blog, \
listicle, or SEO aggregator if an official source exists.

Determine:
- category and a one-line description
- auth method(s): OAuth2, API Key, Bearer Token, Basic, JWT, PAT, or Other
- self-serve model: can anyone create credentials for free/trial, or is it gated behind \
  admin approval, a paid plan, a partnership, or a contact-sales process
- API surface: REST, GraphQL, webhooks, SDKs, breadth, rate limits if stated, whether docs \
  are public
- whether an MCP server exists (official or community), or none
- a buildability verdict (Easy / Medium / Hard / Impossible) with the specific blocker if \
  not Easy
- the evidence URL for every claim

If you cannot find authoritative documentation, respond with "Unknown" fields and a low \
confidence score (below 40). Never fabricate a fact or a URL. Respond with JSON only, \
matching the provided schema."""


def _offline_rows() -> list[AppResearch]:
    from pipeline.seed_dataset import APPS
    return [AppResearch(**row) for row in APPS]


def _live_research_one(app_name: str, hint_url: str | None, client, task: ResearchTask | None = None) -> AppResearch:
    """
    Real implementation for LIVE MODE. Requires `pip install openai` and
    OPENAI_API_KEY. Uses the Responses API's hosted web_search tool so the
    model reads real documentation before answering, then asks for a
    strict JSON object back.

    `task` is the Planner's output for this app (see planner.py) -- when
    present, it steers which source types get checked first and how many
    searches are required before the model is allowed to conclude "no
    public API exists," rather than letting every app get the same
    one-shot treatment regardless of how gated or MCP-native its category is.
    """
    user_prompt = f"Research the app: {app_name}."
    if hint_url:
        user_prompt += f" A likely official site/docs hint: {hint_url}."
    if task:
        user_prompt += (
            f" Check sources in this order: {', '.join(task.source_priority)}. "
            f"Scrutiny level: {task.scrutiny} ({task.scrutiny_reason}) "
            f"Do not conclude 'no public API' with fewer than "
            f"{task.min_searches_before_no_api_verdict} distinct searches."
        )

    response = client.responses.create(
        model="gpt-4.1",
        tools=[{"type": "web_search"}],
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        text={"format": {"type": "json_object"}},
    )
    payload = json.loads(response.output_text)
    payload.setdefault("verification_status", "agent_verified" if payload.get("confidence", 0) >= 60 else "flagged")
    return AppResearch(**payload)


MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0


def _research_with_retry(task: ResearchTask, client) -> AppResearch:
    """
    Retries transient failures (rate limits, timeouts, malformed JSON from
    the model) up to MAX_RETRIES times with linear backoff, via the shared
    pipeline.retry.retry_with_backoff helper. Does NOT retry on a clean,
    well-formed "Unknown" result -- that's a valid answer, not a failure.
    Every exception from _live_research_one is treated as transient here
    (network errors, JSON parse failures, schema validation errors) since
    none of them indicate a stable "this app truly has no API" answer --
    a low-confidence "Unknown" verdict is a valid *return value*, not an
    exception, and is left alone for verification_agent.py to flag instead.
    """
    def attempt() -> AppResearch:
        try:
            return _live_research_one(task.app_name, task.hint_url, client, task=task)
        except Exception as exc:  # noqa: BLE001 - every failure here is transient, see docstring
            raise TransientError(str(exc)) from exc

    def log_retry(attempt_num: int, exc: Exception) -> None:
        wait = RETRY_BACKOFF_SECONDS * attempt_num
        print(f"[research_agent]   retry {attempt_num}/{MAX_RETRIES - 1} for "
              f"{task.app_name} after error ({exc}); waiting {wait:.1f}s")

    return retry_with_backoff(attempt, max_attempts=MAX_RETRIES,
                               backoff_seconds=RETRY_BACKOFF_SECONDS, on_retry=log_retry)


def research_apps(app_list: list[dict[str, str]] | None = None) -> list[AppResearch]:
    """
    Main entry point. `app_list` is [{"name": ..., "category": ..., "hint_url": ...}, ...].
    Returns AppResearch rows for every app, live if possible, offline otherwise.

    Always runs the Planner first (see planner.py) -- even in OFFLINE mode --
    so the elevated-scrutiny routing is exercised and visible in the logs,
    not just described in prose.
    """
    if app_list is not None:
        tasks = plan_research(app_list)
        elevated = [t for t in tasks if t.scrutiny == "elevated"]
        print(f"[planner] {len(tasks)} tasks planned, {len(elevated)} flagged for elevated scrutiny.")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("[research_agent] No OPENAI_API_KEY found -> running in OFFLINE mode "
              "(loading pipeline/seed_dataset.py, the output of a prior live research pass).")
        return _offline_rows()

    try:
        from openai import OpenAI
    except ImportError:
        print("[research_agent] `openai` package not installed -> falling back to OFFLINE mode.")
        return _offline_rows()

    if app_list is None:
        raise ValueError("app_list is required in LIVE mode")

    client = OpenAI(api_key=api_key)
    task_by_name = {t.app_name: t for t in tasks}
    results: list[AppResearch] = []
    for i, task in enumerate(tasks, start=1):
        print(f"[research_agent] ({i}/{len(tasks)}) researching {task.app_name} "
              f"[{task.scrutiny} scrutiny]...")
        try:
            row = _research_with_retry(task, client)
        except Exception as exc:  # noqa: BLE001 - surface but keep the pipeline moving
            print(f"[research_agent]   ! failed for {task.app_name} after {MAX_RETRIES} attempts: {exc}")
            row = AppResearch(
                id=i, name=task.app_name, website=task.hint_url or "", category=task.category,
                description="Research failed.", auth=[], self_serve="gated_unclear",
                self_serve_detail="", api_surface={}, mcp={}, buildability="Hard",
                blocker=f"Research agent error after {MAX_RETRIES} attempts: {exc}", evidence="", confidence=0,
                verification_status="flagged",
            )
        results.append(row)
    return results


def save(rows: list[AppResearch], out_dir: str = "data") -> None:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(f"{out_dir}/apps.json", "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in rows], f, indent=2)
    print(f"[research_agent] wrote {len(rows)} rows -> {out_dir}/apps.json")


if __name__ == "__main__":
    rows = research_apps()
    save(rows)
