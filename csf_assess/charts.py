"""Draw the maturity radar chart and the risk heat map as PNG files."""

import math

import matplotlib

matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt  # noqa: E402

CURRENT_COLOR = "#2563eb"
TARGET_COLOR = "#9ca3af"


def radar_chart(scores, path, title="CSF 2.0 maturity by function"):
    labels = [s["function_name"] for s in scores]
    current = [s["current"] for s in scores]
    target = [s["target"] for s in scores]

    angles = [n / len(labels) * 2 * math.pi for n in range(len(labels))]
    # close the shape by repeating the first point
    angles += angles[:1]
    current += current[:1]
    target += target[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 4)
    ax.set_yticks([1, 2, 3, 4])
    ax.set_yticklabels(["1", "2", "3", "4"], color="#6b7280", fontsize=8)

    ax.plot(angles, target, color=TARGET_COLOR, linewidth=2, linestyle="--", label="Target")
    ax.fill(angles, target, color=TARGET_COLOR, alpha=0.10)
    ax.plot(angles, current, color=CURRENT_COLOR, linewidth=2, label="Current")
    ax.fill(angles, current, color=CURRENT_COLOR, alpha=0.25)

    ax.set_title(title, fontsize=13, pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def heat_map_chart(grid, path, title="Risk heat map (likelihood x impact)"):
    fig, ax = plt.subplots(figsize=(7, 6))

    for likelihood in range(1, 6):
        for impact in range(1, 6):
            score = likelihood * impact
            if score >= 15:
                color = "#fca5a5"
            elif score >= 8:
                color = "#fde68a"
            else:
                color = "#bbf7d0"
            ax.add_patch(plt.Rectangle((impact - 0.5, likelihood - 0.5), 1, 1, facecolor=color, edgecolor="white", linewidth=2))
            ids = grid[(likelihood, impact)]
            if ids:
                ax.text(impact, likelihood, "\n".join(ids), ha="center", va="center", fontsize=9, fontweight="bold")

    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xlabel("Impact")
    ax.set_ylabel("Likelihood")
    ax.set_title(title, fontsize=13)
    ax.set_aspect("equal")
    for spine in ax.spines.values():
        spine.set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
