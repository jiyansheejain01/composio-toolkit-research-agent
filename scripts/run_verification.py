#!/usr/bin/env python3
"""Run Stage 6-7: verification loop + human sample, write data/verification_report.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.verification_agent import run_verification, save_report

if __name__ == "__main__":
    report = run_verification()
    save_report(report)
