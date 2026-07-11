#!/usr/bin/env python3
"""Run Stage 8: pattern analysis, write data/pattern_insights.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.pattern_analysis import load_df, analyze, save

if __name__ == "__main__":
    df = load_df()
    insights = analyze(df)
    save(insights)
