#!/usr/bin/env python3
"""
Runs the full pipeline end to end:
  research -> verification -> pattern analysis -> dashboard

Usage:
    python scripts/run_all.py
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGES = [
    "scripts/run_research.py",
    "scripts/run_composio_crosscheck.py",
    "scripts/run_verification.py",
    "scripts/run_pattern_analysis.py",
    "scripts/generate_dashboard.py",
]

if __name__ == "__main__":
    for stage in STAGES:
        print(f"\n=== Running {stage} ===")
        result = subprocess.run([sys.executable, str(ROOT / stage)], cwd=ROOT)
        if result.returncode != 0:
            print(f"!! {stage} failed, stopping pipeline.")
            sys.exit(result.returncode)
    print("\n=== Pipeline complete. See output/dashboard.html ===")
