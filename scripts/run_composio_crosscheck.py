#!/usr/bin/env python3
"""Cross-check every researched app against Composio's live toolkit catalog."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.composio_client import cross_check_apps, save

if __name__ == "__main__":
    with open("data/apps.json", encoding="utf-8") as f:
        apps = json.load(f)
    results = cross_check_apps(apps)
    save(results)
