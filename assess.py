#!/usr/bin/env python3
"""Run a NIST CSF 2.0 assessment from CSV files and write a report with charts.

Example:
    python assess.py --org "Blue Ridge Family Dental (fictional)"
"""

import argparse
import os
import sys

from csf_assess.analysis import function_scores, heat_map, overall_maturity, prioritized_gaps
from csf_assess.charts import heat_map_chart, radar_chart
from csf_assess.model import load_assessment
from csf_assess.report import build_report


def main(argv=None):
    p = argparse.ArgumentParser(description="NIST CSF 2.0 maturity and risk assessment")
    p.add_argument("--framework", default="data/csf_categories.csv")
    p.add_argument("--assessment", default="data/assessment.csv")
    p.add_argument("--risks", default="data/risks.csv")
    p.add_argument("--org", default="Example Organization")
    p.add_argument("--out", default="reports", help="folder for the report and charts")
    args = p.parse_args(argv)

    try:
        assessment = load_assessment(args.framework, args.assessment, args.risks)
    except (FileNotFoundError, ValueError) as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    radar_chart(function_scores(assessment), os.path.join(args.out, "maturity_radar.png"))
    heat_map_chart(heat_map(assessment), os.path.join(args.out, "risk_heatmap.png"))

    report = build_report(assessment, args.org, radar_png="maturity_radar.png", heatmap_png="risk_heatmap.png")
    report_path = os.path.join(args.out, "assessment_report.md")
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(report)

    current, target = overall_maturity(assessment)
    print(f"Overall maturity {current} / 4 (target {target})")
    for s in function_scores(assessment):
        print(f"  {s['function_name']:<9} current {s['current']:<4} target {s['target']:<4} gap {s['gap']}")
    print("Top 3 priority gaps:")
    for g in prioritized_gaps(assessment, top_n=3):
        print(f"  {g['category_id']:<6} {g['category_name']} (priority {g['priority']})")
    print(f"Report written to {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
