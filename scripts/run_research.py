#!/usr/bin/env python3
"""Run Stage 1-5: research all 100 apps and write data/apps.json + apps.csv."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.research_agent import research_apps, save
from pipeline.models import AppResearch


def write_csv(rows: list[AppResearch], out_path: str = "data/apps.csv") -> None:
    flat_rows = [r.to_flat_row() for r in rows]
    fieldnames = list(flat_rows[0].keys())
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_rows)
    print(f"[run_research] wrote {len(flat_rows)} rows -> {out_path}")


def _app_list_for_planning() -> list[dict[str, str]]:
    """
    Builds the {name, category, hint_url} list the Planner needs. In LIVE
    mode this would normally come from the raw 100-app research brief
    (name + website hint only, no category yet); here we source it from the
    seed dataset so the Planner still runs against real inputs even offline.
    """
    from pipeline.seed_dataset import APPS
    return [{"name": a["name"], "category": a["category"], "hint_url": a["website"]} for a in APPS]


if __name__ == "__main__":
    rows = research_apps(app_list=_app_list_for_planning())
    save(rows)
    write_csv(rows)
