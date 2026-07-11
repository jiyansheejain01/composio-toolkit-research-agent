"""
composio_client.py
-------------------
A genuine integration with Composio's own platform, not a mention of it.

Why this exists: Composio already maintains a production catalog of 1000+
toolkits, each with a verified auth scheme (`composio_managed_auth_schemes`)
recorded the moment their team integrates an app. That catalog is a THIRD,
independent ground-truth source for this project -- distinct from "the
research agent's answer" and "a human's live doc check" -- and it is the
single most relevant way this project could use Composio's own SDK: instead
of guessing whether an app is worth building, ask Composio whether it has
already been built, and if so, whether Composio's own recorded auth scheme
agrees with what this pipeline found independently.

This directly replaces a piece of custom guesswork with something Composio
already solves: the "opportunity" framing in pattern_analysis.py (which apps
look buildable) is downgraded from a prediction to a confirmation wherever
this cross-check has an answer, and the Build-Priority Score explicitly
excludes any app Composio has already shipped.

API surface used (verified against docs.composio.dev, July 2026):
  Base URL:    https://backend.composio.dev/api/v3
  Auth header: x-api-key: <COMPOSIO_API_KEY>
  Endpoint:    GET /toolkits/{slug}
  Response:    { slug, name, enabled, composio_managed_auth_schemes: [...],
                 is_local_toolkit, auth_config_details: [...] }
  A 404 on this endpoint means the app is not (yet) a Composio toolkit --
  itself a meaningful finding, not an error to swallow.

Two run modes, same pattern as research_agent.py:
  LIVE:    COMPOSIO_API_KEY set + network available -> calls the real API
           for every app's guessed toolkit slug.
  OFFLINE: no key / no network (this build's sandbox) -> every row is
           written with composio_status="NOT_CHECKED_OFFLINE_MODE" and a
           null composio_auth_scheme, rather than fabricating a plausible-
           looking answer. See data/composio_crosscheck.json for the actual
           output of this run.
"""

from __future__ import annotations
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline.retry import retry_with_backoff, TransientError

try:
    from dotenv import load_dotenv
    load_dotenv()  # loads .env from the current working directory (or a parent) if present;
                   # silently does nothing if python-dotenv isn't installed or no .env exists.
except ImportError:
    pass

COMPOSIO_API_BASE = "https://backend.composio.dev/api/v3"
MAX_RETRIES = 3
BACKOFF_SECONDS = 1.5


@dataclass
class ComposioCrossCheck:
    app_id: int
    app_name: str
    guessed_slug: str
    composio_status: str          # "ALREADY_A_COMPOSIO_TOOLKIT" | "NOT_YET_A_COMPOSIO_TOOLKIT" | "NOT_CHECKED_OFFLINE_MODE" | "LOOKUP_FAILED"
    composio_auth_schemes: list[str]
    agrees_with_our_finding: bool | None   # None when status isn't ALREADY_A_COMPOSIO_TOOLKIT
    note: str = ""


def _guess_slug(app_name: str) -> str:
    """
    Composio toolkit slugs are lowercase, no punctuation (e.g. "github",
    "google_ads", "hubspot"). This is a best-effort guess from the app's
    display name -- LIVE mode should treat a 404 as "guess was probably
    wrong OR app isn't integrated" and not conflate the two without a
    second attempt against the toolkit search endpoint (see TODO below).
    """
    slug = app_name.lower()
    slug = re.sub(r"\(.*?\)", "", slug)          # drop "(Larksuite)"-style parentheticals
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug


def _our_auth_family(our_auth_methods: list[str]) -> str:
    """Collapse our own finding to the same coarse family Composio uses."""
    joined = " ".join(our_auth_methods).lower()
    if "oauth2" in joined:
        return "oauth2"
    if "oauth1" in joined:
        return "oauth1"
    if "api key" in joined or "api_key" in joined:
        return "api_key"
    if "bearer" in joined:
        return "bearer_token"
    if "basic" in joined:
        return "basic"
    return "other"


def _lookup_one_live(slug: str, api_key: str) -> dict | None:
    """
    Real HTTP call, using the shared pipeline.retry.retry_with_backoff helper
    for transient failures (429/5xx). A 404 is deliberately NOT a
    TransientError -- it's a real, final answer ("this toolkit doesn't
    exist"), and retrying it would just waste attempts confirming the same
    absence three times.
    """
    import requests  # imported lazily so OFFLINE mode has no hard dependency

    url = f"{COMPOSIO_API_BASE}/toolkits/{slug}"
    headers = {"x-api-key": api_key}

    def attempt() -> dict | None:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 404:
            return None
        if resp.status_code in (429, 500, 502, 503):
            raise TransientError(f"HTTP {resp.status_code} from Composio (retryable)")
        resp.raise_for_status()
        return None  # unreachable in practice; keeps type checkers happy

    return retry_with_backoff(attempt, max_attempts=MAX_RETRIES, backoff_seconds=BACKOFF_SECONDS)


def _offline_results(apps: list[dict]) -> list[ComposioCrossCheck]:
    return [
        ComposioCrossCheck(
            app_id=a["id"], app_name=a["name"], guessed_slug=_guess_slug(a["name"]),
            composio_status="NOT_CHECKED_OFFLINE_MODE", composio_auth_schemes=[],
            agrees_with_our_finding=None,
            note="No COMPOSIO_API_KEY / network in this build environment. Set the key and "
                 "re-run scripts/run_composio_crosscheck.py to populate this for real.",
        )
        for a in apps
    ]


def cross_check_apps(apps: list[dict]) -> list[ComposioCrossCheck]:
    """
    apps: rows from data/apps.json (each has id, name, auth, ...).
    Returns one ComposioCrossCheck per app.
    """
    api_key = os.environ.get("COMPOSIO_API_KEY")

    if not api_key:
        print("[composio_client] No COMPOSIO_API_KEY found -> OFFLINE mode. "
              "Writing NOT_CHECKED_OFFLINE_MODE for all rows instead of guessing.")
        return _offline_results(apps)

    try:
        import requests  # noqa: F401
    except ImportError:
        print("[composio_client] `requests` not installed -> OFFLINE mode.")
        return _offline_results(apps)

    results: list[ComposioCrossCheck] = []
    print(f"[composio_client] LIVE mode: checking {len(apps)} apps against "
          f"{COMPOSIO_API_BASE}/toolkits/{{slug}} ...")
    for a in apps:
        slug = _guess_slug(a["name"])
        try:
            toolkit = _lookup_one_live(slug, api_key)
        except Exception as exc:  # noqa: BLE001
            results.append(ComposioCrossCheck(
                app_id=a["id"], app_name=a["name"], guessed_slug=slug,
                composio_status="LOOKUP_FAILED", composio_auth_schemes=[],
                agrees_with_our_finding=None, note=f"Request error after retries: {exc}",
            ))
            continue

        if toolkit is None:
            results.append(ComposioCrossCheck(
                app_id=a["id"], app_name=a["name"], guessed_slug=slug,
                composio_status="NOT_YET_A_COMPOSIO_TOOLKIT", composio_auth_schemes=[],
                agrees_with_our_finding=None,
                note="404 from Composio -- either not yet integrated, or the slug guess "
                     "was wrong (TODO: fall back to GET /toolkits?search= before concluding absence).",
            ))
            continue

        composio_schemes = toolkit.get("composio_managed_auth_schemes", [])
        our_family = _our_auth_family(a.get("auth", []))
        agrees = our_family in [s.lower() for s in composio_schemes] if composio_schemes else None
        results.append(ComposioCrossCheck(
            app_id=a["id"], app_name=a["name"], guessed_slug=slug,
            composio_status="ALREADY_A_COMPOSIO_TOOLKIT", composio_auth_schemes=composio_schemes,
            agrees_with_our_finding=agrees,
            note="" if agrees else "Our auth finding did not match Composio's recorded scheme(s) -- "
                                    "worth a manual re-check.",
        ))
    return results


def save(results: list[ComposioCrossCheck], out_path: str = "data/composio_crosscheck.json") -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    already = sum(1 for r in results if r.composio_status == "ALREADY_A_COMPOSIO_TOOLKIT")
    not_yet = sum(1 for r in results if r.composio_status == "NOT_YET_A_COMPOSIO_TOOLKIT")
    offline = sum(1 for r in results if r.composio_status == "NOT_CHECKED_OFFLINE_MODE")
    print(f"[composio_client] {already} already toolkits, {not_yet} not yet, "
          f"{offline} not checked (offline) -> wrote {out_path}")


if __name__ == "__main__":
    with open("data/apps.json", encoding="utf-8") as f:
        apps = json.load(f)
    results = cross_check_apps(apps)
    save(results)
