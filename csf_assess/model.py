"""Load the framework, the assessment scores, and the risk register from CSV."""

import csv
from dataclasses import dataclass, field
from typing import Dict, List

# This project's own maturity scale for each category. It is NOT the same as
# the CSF "Tiers", which describe the organization as a whole.
MATURITY_SCALE = {
    0: "Not performed",
    1: "Ad hoc",
    2: "Partially documented",
    3: "Implemented and consistent",
    4: "Measured and improving",
}


@dataclass
class Category:
    function_id: str
    function_name: str
    category_id: str
    category_name: str
    current: int = 0
    target: int = 0
    notes: str = ""

    @property
    def gap(self) -> int:
        return max(self.target - self.current, 0)


@dataclass
class Risk:
    risk_id: str
    title: str
    scenario: str
    categories: List[str]
    likelihood: int
    impact: int
    treatment: str
    recommendation: str

    @property
    def score(self) -> int:
        return self.likelihood * self.impact

    @property
    def rating(self) -> str:
        if self.score >= 15:
            return "High"
        if self.score >= 8:
            return "Medium"
        return "Low"


@dataclass
class Assessment:
    categories: Dict[str, Category] = field(default_factory=dict)
    risks: List[Risk] = field(default_factory=list)


def _check_score(value, name, low, high, where):
    number = int(value)
    if not low <= number <= high:
        raise ValueError(f"{where}: {name} must be between {low} and {high}, got {number}")
    return number


def load_framework(path) -> Dict[str, Category]:
    with open(path, newline="", encoding="utf-8") as handle:
        return {row["category_id"]: Category(**row) for row in csv.DictReader(handle)}


def load_assessment(framework_path, assessment_path, risks_path) -> Assessment:
    categories = load_framework(framework_path)

    with open(assessment_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            cid = row["category_id"].strip()
            if cid not in categories:
                raise ValueError(f"Unknown CSF category in assessment: {cid}")
            cat = categories[cid]
            cat.current = _check_score(row["current"], "current", 0, 4, cid)
            cat.target = _check_score(row["target"], "target", 0, 4, cid)
            cat.notes = row.get("notes", "").strip()

    risks = []
    with open(risks_path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            linked = [c.strip() for c in row["categories"].split(";") if c.strip()]
            unknown = [c for c in linked if c not in categories]
            if unknown:
                raise ValueError(f"{row['risk_id']} links to unknown categories: {unknown}")
            risks.append(
                Risk(
                    risk_id=row["risk_id"],
                    title=row["title"],
                    scenario=row["scenario"],
                    categories=linked,
                    likelihood=_check_score(row["likelihood"], "likelihood", 1, 5, row["risk_id"]),
                    impact=_check_score(row["impact"], "impact", 1, 5, row["risk_id"]),
                    treatment=row["treatment"],
                    recommendation=row["recommendation"],
                )
            )
    return Assessment(categories=categories, risks=risks)
