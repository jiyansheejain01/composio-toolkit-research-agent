#!/usr/bin/env python3
"""Run the final stage: render the case-study dashboard to output/dashboard.html."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.dashboard_generator import generate

if __name__ == "__main__":
    generate()
