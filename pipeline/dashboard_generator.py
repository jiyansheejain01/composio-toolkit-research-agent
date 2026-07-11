"""
dashboard_generator.py
-----------------------
Final pipeline stage: renders templates/dashboard.html.jinja2 with the
verified dataset (data/apps.json), the pattern insights
(data/pattern_insights.json), and the verification report
(data/verification_report.json) into a single self-contained HTML file at
output/dashboard.html.

The template embeds the raw JSON as <script type="application/json"> blocks
so the in-page search/filter/table and Chart.js visuals run entirely
client-side with vanilla JS -- no server, no build step, one file to share.
"""

from __future__ import annotations
import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent


def generate(
    apps_path: str = "data/apps.json",
    insights_path: str = "data/pattern_insights.json",
    verification_path: str = "data/verification_report.json",
    template_dir: str = "templates",
    out_path: str = "output/dashboard.html",
) -> str:
    apps = json.loads((ROOT / apps_path).read_text(encoding="utf-8"))
    insights = json.loads((ROOT / insights_path).read_text(encoding="utf-8"))
    verification = json.loads((ROOT / verification_path).read_text(encoding="utf-8"))

    env = Environment(loader=FileSystemLoader(str(ROOT / template_dir)))
    template = env.get_template("dashboard.html.jinja2")
    html = template.render(apps=apps, insights=insights, verification=verification)

    out_full = ROOT / out_path
    out_full.parent.mkdir(parents=True, exist_ok=True)
    out_full.write_text(html, encoding="utf-8")
    print(f"[dashboard_generator] wrote {len(html):,} chars -> {out_full}")
    return str(out_full)


if __name__ == "__main__":
    generate()
