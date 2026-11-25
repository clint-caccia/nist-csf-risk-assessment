import csv
import os

import pytest

from csf_assess.analysis import function_scores, heat_map, overall_maturity, prioritized_gaps
from csf_assess.model import Risk, load_assessment, load_framework
from csf_assess.report import build_report

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def sample():
    return load_assessment(
        os.path.join(DATA, "csf_categories.csv"),
        os.path.join(DATA, "assessment.csv"),
        os.path.join(DATA, "risks.csv"),
    )


def test_framework_has_six_functions_and_22_categories():
    fw = load_framework(os.path.join(DATA, "csf_categories.csv"))
    assert len(fw) == 22
    assert {c.function_id for c in fw.values()} == {"GV", "ID", "PR", "DE", "RS", "RC"}


def test_risk_score_and_rating():
    def risk(l, i):
        return Risk("R", "t", "s", [], l, i, "Mitigate", "r")

    assert risk(4, 5).score == 20 and risk(4, 5).rating == "High"
    assert risk(3, 5).rating == "High"  # 15 is the cutoff
    assert risk(2, 4).rating == "Medium"
    assert risk(2, 3).rating == "Low"


def test_function_scores_are_averages():
    scores = {s["function_id"]: s for s in function_scores(sample())}
    # Detect has two categories, both scored 0 now and 2 target
    assert scores["DE"]["current"] == 0
    assert scores["DE"]["target"] == 2
    assert len(scores) == 6


def test_priority_rewards_risk_exposure():
    gaps = prioritized_gaps(sample())
    ids = [g["category_id"] for g in gaps]
    # PR.AA has a gap of 2 and three risks depend on it, so it should beat
    # GV.OV, which also has a gap of 2 but only one risk depends on it.
    assert ids.index("PR.AA") < ids.index("GV.OV")
    # categories with no gap are left out
    assert all(g["gap"] > 0 for g in gaps)


def test_heat_map_places_every_risk():
    a = sample()
    grid = heat_map(a)
    placed = [rid for ids in grid.values() for rid in ids]
    assert sorted(placed) == sorted(r.risk_id for r in a.risks)
    assert "R01" in grid[(4, 5)]


def test_overall_maturity_range():
    current, target = overall_maturity(sample())
    assert 0 <= current <= target <= 4


def test_report_mentions_top_risk():
    text = build_report(sample(), "Test Org")
    assert "Ransomware on office PCs" in text
    assert "## Priority gaps" in text


def test_bad_score_is_rejected(tmp_path):
    bad = tmp_path / "assessment.csv"
    with open(bad, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["category_id", "current", "target", "notes"])
        writer.writerow(["GV.OC", "7", "3", "out of range"])
    with pytest.raises(ValueError):
        load_assessment(os.path.join(DATA, "csf_categories.csv"), bad, os.path.join(DATA, "risks.csv"))


def test_unknown_category_is_rejected(tmp_path):
    bad = tmp_path / "assessment.csv"
    with open(bad, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["category_id", "current", "target", "notes"])
        writer.writerow(["XX.YY", "1", "3", "typo"])
    with pytest.raises(ValueError):
        load_assessment(os.path.join(DATA, "csf_categories.csv"), bad, os.path.join(DATA, "risks.csv"))
