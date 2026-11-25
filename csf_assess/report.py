"""Write the assessment as a Markdown report."""

from datetime import date

from .analysis import function_scores, overall_maturity, prioritized_gaps
from .model import MATURITY_SCALE


def _bar(value, width=20, top=4):
    filled = round(value / top * width)
    return "█" * filled + "░" * (width - filled)


def build_report(assessment, org_name, radar_png=None, heatmap_png=None, top_n=8):
    scores = function_scores(assessment)
    current, target = overall_maturity(assessment)
    gaps = prioritized_gaps(assessment, top_n=top_n)
    risks = sorted(assessment.risks, key=lambda r: -r.score)
    high = [r for r in risks if r.rating == "High"]

    out = []
    out.append(f"# NIST CSF 2.0 Risk Assessment: {org_name}")
    out.append("")
    out.append(f"_Generated {date.today().isoformat()} by csf-assess_")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(
        f"Overall maturity is **{current} out of 4** against a target of **{target}**. "
        f"Of the {len(risks)} risks in the register, **{len(high)} are rated High**."
    )
    weakest = min(scores, key=lambda s: s["current"])
    out.append("")
    out.append(
        f"The weakest function is **{weakest['function_name']}** ({weakest['current']}). "
        f"The top priority gap is **{gaps[0]['category_id']} {gaps[0]['category_name']}**."
        if gaps
        else ""
    )
    out.append("")

    out.append("## Maturity by function")
    out.append("")
    if radar_png:
        out.append(f"![Maturity radar chart]({radar_png})")
        out.append("")
    out.append("| Function | Current | Target | Gap | |")
    out.append("|---|---|---|---|---|")
    for s in scores:
        out.append(f"| {s['function_name']} ({s['function_id']}) | {s['current']} | {s['target']} | {s['gap']} | `{_bar(s['current'])}` |")
    out.append("")
    out.append("Scale: " + ", ".join(f"{k} = {v}" for k, v in MATURITY_SCALE.items()) + ".")
    out.append("")

    out.append("## Risk register")
    out.append("")
    if heatmap_png:
        out.append(f"![Risk heat map]({heatmap_png})")
        out.append("")
    out.append("| ID | Risk | L | I | Score | Rating | CSF categories | Treatment |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in risks:
        out.append(
            f"| {r.risk_id} | {r.title} | {r.likelihood} | {r.impact} | {r.score} | {r.rating} | {', '.join(r.categories)} | {r.treatment} |"
        )
    out.append("")
    out.append("Likelihood and impact are each scored 1 to 5. Score = L x I. High is 15 or more, Medium is 8 to 14, Low is under 8.")
    out.append("")

    out.append("## Priority gaps")
    out.append("")
    out.append("Ranked by `gap x (1 + linked risk exposure / 10)`, so gaps that many serious risks depend on come first.")
    out.append("")
    out.append("| Rank | Category | Function | Current | Target | Risk exposure | Priority |")
    out.append("|---|---|---|---|---|---|---|")
    for n, g in enumerate(gaps, 1):
        out.append(
            f"| {n} | {g['category_id']} {g['category_name']} | {g['function_name']} | {g['current']} | {g['target']} | {g['risk_exposure']} | {g['priority']} |"
        )
    out.append("")

    out.append("## Recommendations")
    out.append("")
    out.append("In order of risk score:")
    out.append("")
    for r in risks:
        if r.treatment.lower() == "accept":
            continue
        out.append(f"- **{r.risk_id} {r.title}** ({r.rating}, {r.score}): {r.recommendation}")
    accepted = [r for r in risks if r.treatment.lower() == "accept"]
    if accepted:
        out.append("")
        out.append("Accepted risks: " + "; ".join(f"{r.risk_id} {r.title} ({r.recommendation})" for r in accepted))
    out.append("")

    out.append("## Category detail")
    out.append("")
    out.append("| Category | Current | Target | Observations |")
    out.append("|---|---|---|---|")
    for cat in assessment.categories.values():
        out.append(f"| {cat.category_id} {cat.category_name} | {cat.current} | {cat.target} | {cat.notes} |")
    out.append("")
    return "\n".join(out)
