"""Plot recorded RQ1 episodes; unscored and unexecuted positions remain distinct."""
import csv
import json
from pathlib import Path


def render_batch_figures(root):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    root = Path(root)
    episodes = list(csv.DictReader((root / "metrics/per_episode.csv").open()))
    strategies = json.loads((root / "config.json").read_text())["strategies"]
    destination = root / "figures"
    destination.mkdir(exist_ok=True)
    ended = [r for r in episodes if r["episode_wall_s"]]
    colors = {"glm": "#009E73", "luna": "#0072B2", "terra": "#D55E00", "rule": "#666666", "laya": "#CC79A7", "kev": "#E69F00"}
    def save(fig, name):
        for extension in ("png", "svg", "pdf"):
            fig.savefig(destination / f"{name}.{extension}", dpi=300)
        plt.close(fig)

    totals = [r for r in csv.DictReader((root / "metrics/per_strategy.csv").open()) if r["subset"] == "all"]
    fig, (ax, fees) = plt.subplots(1, 2, figsize=(11, 7.2), sharey=True,
                                  gridspec_kw={"width_ratios": [2, 1]}, layout="constrained")
    for i, row in enumerate(totals):
        one, zero, n = (int(row[k]) for k in ("reward_1", "reward_0", "tasks"))
        ax.barh(i, one, color="#009E73")
        ax.barh(i, zero, left=one, color="#D55E00")
        ax.barh(i, n - one - zero, left=one + zero, color="#dddddd")
        ax.text(n + 1, i, f"{one}/{one + zero} scored", va="center", fontsize=8)
        model, teacher = row["generator_known_reference_usd"], row["teacher_known_reference_usd"]
        if model:
            cost = float(model) + float(teacher or 0)
            fees.barh(i, cost, color=colors[row["strategy_id"].split("_")[0]])
            fees.text(cost + .03, i, f"${cost:.3f}", va="center", fontsize=8)
    ax.set(yticks=range(len(totals)), yticklabels=[r["strategy_id"] for r in totals],
           xlabel="Official tasks per strategy", xlim=(0, 115))
    ax.set_title("89-task outcomes and scoring coverage", pad=28)
    ax.invert_yaxis()
    ax.legend(handles=[Line2D([], [], color=color, linewidth=6, label=label)
                       for color, label in (("#009E73", "Reward 1"), ("#D55E00", "Reward 0"),
                                            ("#dddddd", "No eligible score yet"))], fontsize=8,
              loc="lower left", bbox_to_anchor=(0, 1.005), ncol=3)
    fees.set(xlabel="Known model + teacher reference USD", title="All attempts, including failures")
    fees.tick_params(axis="y", labelleft=False)
    fees.margins(x=.22)
    fig.suptitle("Terminal-Bench 2.0: task results, not Router prediction accuracy")
    fig.supxlabel("Gray includes missing Reward, unfinished positions and reported effort conflicts. Supplier billing and resource USD are unknown.", fontsize=8)
    save(fig, "success_cost_frontier")

    fixed = [s["id"] for s in strategies if s["stage"] == "fixed"]
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
    for row in ended:
        if row["strategy_id"] not in fixed or not row["generator_known_reference_usd"]:
            continue
        reward = row["reward"]
        ax.scatter(float(row["generator_known_reference_usd"]), fixed.index(row["strategy_id"]), marker="o" if reward == "1.0" else "x" if reward == "0.0" else "^", color=colors[row["strategy_id"].split("_")[0]], alpha=.7)
    ax.set(yticks=range(len(fixed)), yticklabels=fixed, xlabel="Known model reference fee / episode (USD)", title="Fixed model × requested Native Effort: actual task results")
    ax.invert_yaxis()
    fig.supxlabel("Circle: Reward 1; cross: Reward 0; triangle: no Reward. Missing request fees excluded from known sum.", fontsize=8)
    save(fig, "model_effort_comparison")

    lookup = {(r["task_id"], r["strategy_id"], r["seed"]): r for r in ended}
    fig, ax = plt.subplots(figsize=(7.2, 4.2), layout="constrained")
    pairs = 0
    for row in ended:
        if not row["strategy_id"].endswith("_off"):
            continue
        other = lookup.get((row["task_id"], row["strategy_id"][:-3] + "on", row["seed"]))
        if not other or not all(r["reward"] and r["reference_cost_usd"] for r in (row, other)):
            continue
        pairs += 1
        ax.scatter(float(other["reference_cost_usd"]) - float(row["reference_cost_usd"]), float(other["reward"]) - float(row["reward"]), color=colors[row["strategy_id"].split("_")[0]], marker="s" if "original" in row["strategy_id"] else "o", alpha=.6)
    if not pairs:
        ax.text(.5, .5, "No scored Teacher OFF/ON pairs yet", ha="center", transform=ax.transAxes)
    ax.axhline(0, color="#999999", linewidth=.6)
    ax.axvline(0, color="#999999", linewidth=.6)
    ax.set(xlabel="ON − OFF model + teacher reference fee (USD)", ylabel="ON − OFF official Reward", yticks=[-1, 0, 1], ylim=(-1.3, 1.3), title=f"Same task / seed / weight teacher comparison: {pairs} pairs")
    ax.legend(handles=[Line2D([], [], color=colors[family], marker="s" if version == "original" else "o", linestyle="", label=f"{family.title()} {version}") for family in ("laya", "kev") for version in ("original", "trained")], fontsize=8, loc="upper right")
    fig.supxlabel("Each point is one task pair; complete cash net benefit remains unknown.", fontsize=8)
    save(fig, "teacher_effect")


if __name__ == "__main__":
    import sys
    render_batch_figures(sys.argv[1])
