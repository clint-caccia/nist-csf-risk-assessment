"""Score the CSF functions, rank the gaps, and build the risk heat map."""

from collections import OrderedDict

FUNCTION_ORDER = ["GV", "ID", "PR", "DE", "RS", "RC"]


def function_scores(assessment):
    """Average current and target maturity for each of the six CSF functions."""
    grouped = OrderedDict((f, []) for f in FUNCTION_ORDER)
    names = {}
    for cat in assessment.categories.values():
        grouped[cat.function_id].append(cat)
        names[cat.function_id] = cat.function_name
    results = []
    for fid, cats in grouped.items():
        if not cats:
            continue
        current = sum(c.current for c in cats) / len(cats)
        target = sum(c.target for c in cats) / len(cats)
        results.append(
            {
                "function_id": fid,
                "function_name": names[fid],
                "current": round(current, 2),
                "target": round(target, 2),
                "gap": round(target - current, 2),
            }
        )
    return results


def risk_exposure_by_category(assessment):
    """Add up the scores of every risk that links to each category."""
    exposure = {cid: 0 for cid in assessment.categories}
    for risk in assessment.risks:
        for cid in risk.categories:
            exposure[cid] += risk.score
    return exposure


def prioritized_gaps(assessment, top_n=None):
    """Rank categories by gap size weighted by how much risk depends on them.

    priority = gap * (1 + risk exposure / 10)

    A category with a gap of 2 that three high risks depend on should come
    before a category with a gap of 2 that nothing depends on.
    """
    exposure = risk_exposure_by_category(assessment)
    rows = []
    for cat in assessment.categories.values():
        if cat.gap == 0:
            continue
        priority = cat.gap * (1 + exposure[cat.category_id] / 10)
        rows.append(
            {
                "category_id": cat.category_id,
                "category_name": cat.category_name,
                "function_name": cat.function_name,
                "current": cat.current,
                "target": cat.target,
                "gap": cat.gap,
                "risk_exposure": exposure[cat.category_id],
                "priority": round(priority, 1),
                "notes": cat.notes,
            }
        )
    rows.sort(key=lambda r: (-r["priority"], r["category_id"]))
    return rows[:top_n] if top_n else rows


def heat_map(assessment):
    """5x5 grid of risk IDs keyed by (likelihood, impact)."""
    grid = {(l, i): [] for l in range(1, 6) for i in range(1, 6)}
    for risk in assessment.risks:
        grid[(risk.likelihood, risk.impact)].append(risk.risk_id)
    return grid


def overall_maturity(assessment):
    cats = list(assessment.categories.values())
    return round(sum(c.current for c in cats) / len(cats), 2), round(sum(c.target for c in cats) / len(cats), 2)
