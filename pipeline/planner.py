"""
planner.py
----------
Stage 1 of the pipeline: Planner.

Before any documentation gets searched, the planner decides HOW each app
should be researched: which source types are likely to have the answer,
what to check first, and how much scrutiny the app deserves. This is a
genuinely separate responsibility from research_agent.py (which executes
the plan) -- splitting them out means the research strategy is inspectable
and testable on its own, and a different app category can get a different
strategy without touching the extraction logic at all.

The rule set below is intentionally simple and legible (no LLM call needed
for planning itself -- only for the actual document reading/extraction
downstream), because a Product Ops reviewer should be able to read this
file top to bottom and know exactly why an app got the scrutiny it got.
"""

from __future__ import annotations
from dataclasses import dataclass

# Categories where a working product frequently ships an MCP server before
# it ships conventional docs marketing -- so MCP registries are checked
# *first*, not as an afterthought, and a "no MCP found" result gets less
# benefit of the doubt (i.e. lower default confidence) because the negative
# is easier to get wrong by under-searching (see: the Consensus correction).
MCP_FIRST_CATEGORIES = {"AI, Research & Media", "Developer & Infra"}

# Categories where the interesting finding is usually the *gate*, not the
# API shape -- so the planner prioritizes finding pricing/access-tier pages
# and partner-program pages over the API reference itself.
GATE_FIRST_CATEGORIES = {"Finance & Fintech", "Marketing, Ads & Social", "CRM & Sales"}

SOURCE_PRIORITY_DEFAULT = ["official_docs", "developer_portal", "help_center", "mcp_registry"]
SOURCE_PRIORITY_MCP_FIRST = ["mcp_registry", "official_docs", "developer_portal", "help_center"]
SOURCE_PRIORITY_GATE_FIRST = ["pricing_page", "partner_program_page", "official_docs", "developer_portal"]


@dataclass
class ResearchTask:
    app_name: str
    category: str
    hint_url: str | None
    source_priority: list[str]
    scrutiny: str                 # "standard" | "elevated"
    scrutiny_reason: str
    min_searches_before_no_api_verdict: int
    notes: str = ""


def plan_one(app_name: str, category: str, hint_url: str | None = None) -> ResearchTask:
    """
    Decide the research strategy for a single app. Deterministic and
    rule-based on purpose: the plan itself should never need an LLM call,
    only the document reading it hands off to does.
    """
    if category in MCP_FIRST_CATEGORIES:
        priority = SOURCE_PRIORITY_MCP_FIRST
        scrutiny = "elevated"
        reason = ("Category ships MCP servers ahead of conventional marketing docs; "
                  "a quick 'no docs found' read is unreliable here -- require more "
                  "searches before concluding no public API exists.")
        min_searches = 3
    elif category in GATE_FIRST_CATEGORIES:
        priority = SOURCE_PRIORITY_GATE_FIRST
        scrutiny = "elevated"
        reason = ("Category is dominated by tiered/gated access; the access model "
                  "(not the endpoint list) is the finding Composio actually needs, "
                  "so pricing and partner-program pages are checked before the API reference.")
        min_searches = 2
    else:
        priority = SOURCE_PRIORITY_DEFAULT
        scrutiny = "standard"
        reason = "Category has historically well-documented, self-serve developer platforms."
        min_searches = 1

    return ResearchTask(
        app_name=app_name, category=category, hint_url=hint_url,
        source_priority=priority, scrutiny=scrutiny, scrutiny_reason=reason,
        min_searches_before_no_api_verdict=min_searches,
    )


def plan_research(apps: list[dict]) -> list[ResearchTask]:
    """
    apps: [{"name": ..., "category": ..., "hint_url": ...}, ...]
    Returns one ResearchTask per app, in the order research_agent.py should
    process them (elevated-scrutiny apps first, so a research budget cut
    short by rate limits or time still covers the highest-risk apps).
    """
    tasks = [plan_one(a["name"], a.get("category", "Unknown"), a.get("hint_url")) for a in apps]
    tasks.sort(key=lambda t: 0 if t.scrutiny == "elevated" else 1)
    return tasks


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from pipeline.seed_dataset import APPS

    apps = [{"name": a["name"], "category": a["category"], "hint_url": a["website"]} for a in APPS]
    tasks = plan_research(apps)
    elevated = [t for t in tasks if t.scrutiny == "elevated"]
    print(f"Planned {len(tasks)} research tasks. {len(elevated)} flagged for elevated scrutiny "
          f"before this pipeline even reads a single doc page:")
    for t in elevated[:8]:
        print(f"  - {t.app_name} ({t.category}): {t.scrutiny_reason}")
