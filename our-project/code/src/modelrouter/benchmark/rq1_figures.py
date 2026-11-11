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
    n_tasks = len({r["task_id"] for r in episodes})
    max_cost = max(float(r["generator_known_reference_usd"] or 0) + float(r["teacher_known_reference_usd"] or 0) for r in totals)
    fig, (ax, fees) = plt.subplots(1, 2, figsize=(11, max(7.2, len(totals) * .34 + 1.5)), sharey=True,
                                  gridspec_kw={"width_ratios": [2, 1]}, layout="constrained")
    for i, row in enumerate(totals):
        one, zero, n = (int(row[k]) for k in ("reward_1", "reward_0", "tasks"))
        ax.barh(i, one, color="#009E73")
        ax.barh(i, zero, left=one, color="#D55E00")
        ax.barh(i, n - one - zero, left=one + zero, color="#dddddd")
        ax.text(n + .03 * n_tasks, i, f"{one}/{one + zero} scored", va="center", fontsize=8)
        model, teacher = row["generator_known_reference_usd"], row["teacher_known_reference_usd"]
        if model:
            cost = float(model) + float(teacher or 0)
            fees.barh(i, cost, color=colors[row["strategy_id"].split("_")[0]])
            fees.text(cost + .02 * max_cost, i, f"${cost:.4f}", va="center", fontsize=8)
    ax.set(yticks=range(len(totals)), yticklabels=[r["strategy_id"] for r in totals],
           xlabel="Official tasks per strategy", xlim=(0, n_tasks * 1.45))
    ax.set_title(f"{n_tasks}-task outcomes and scoring coverage", pad=28)
    ax.invert_yaxis()
    ax.legend(handles=[Line2D([], [], color=color, linewidth=6, label=label)
                       for color, label in (("#009E73", "Reward 1"), ("#D55E00", "Reward 0"),
                                            ("#dddddd", "No eligible official score"))], fontsize=8,
              loc="lower left", bbox_to_anchor=(0, 1.005), ncol=3)
    fees.set(xlabel="Known model + teacher reference USD", title="All attempts, including failures")
    fees.tick_params(axis="y", labelleft=False)
    fees.margins(x=.22)
    fig.suptitle("Terminal-Bench 2.0")
    fig.supxlabel("Supplier billing and resource USD are unknown.", fontsize=8)
    save(fig, "success_cost_frontier")

    fixed = [s["id"] for s in strategies if s["stage"] == "fixed"]
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
    for row in ended:
        cost = row.get("latest_trial_reference_usd", row["reference_cost_usd"])
        if row["strategy_id"] not in fixed or not cost:
            continue
        reward = row["reward"]
        eligible = row["effort_comparison_eligible"] == "True" and row.get("verifier_dependency_failure") != "True"
        marker = "o" if reward and float(reward) == 1 and eligible else "x" if reward and float(reward) == 0 and eligible else "^"
        ax.scatter(float(cost), fixed.index(row["strategy_id"]), marker=marker, color=colors[row["strategy_id"].split("_")[0]], alpha=.7)
    ax.set(yticks=range(len(fixed)), yticklabels=fixed, xlabel="Final episode model reference fee (USD)", title="Fixed model × requested Native Effort: actual task results")
    ax.invert_yaxis()
    fig.supxlabel("Circle: Reward 1; cross: Reward 0; triangle: no eligible score. Episodes with incomplete fees omitted.", fontsize=8)
    save(fig, "model_effort_comparison")

    lookup = {(r["task_id"], r["strategy_id"], r["seed"]): r for r in ended}
    fig, ax = plt.subplots(figsize=(7.2, 4.2), layout="constrained")
    pairs = 0
    for row in ended:
        if not row["strategy_id"].endswith("_off"):
            continue
        other = lookup.get((row["task_id"], row["strategy_id"][:-3] + "on", row["seed"]))
        if not other or not all(r["reward"] and r.get("latest_trial_reference_usd", r["reference_cost_usd"]) and r.get("verifier_dependency_failure") != "True" for r in (row, other)):
            continue
        pairs += 1
        delta = float(other.get("latest_trial_reference_usd", other["reference_cost_usd"])) - float(row.get("latest_trial_reference_usd", row["reference_cost_usd"]))
        ax.scatter(delta, float(other["reward"]) - float(row["reward"]), color=colors[row["strategy_id"].split("_")[0]], marker="s" if "original" in row["strategy_id"] else "o", alpha=.6)
    if not pairs:
        ax.text(.5, .5, "No scored Teacher OFF/ON pairs yet", ha="center", transform=ax.transAxes)
    ax.axhline(0, color="#999999", linewidth=.6)
    ax.axvline(0, color="#999999", linewidth=.6)
    ax.set(xlabel="ON − OFF final episode model + teacher reference fee (USD)", ylabel="ON − OFF official Reward", yticks=[-1, 0, 1], ylim=(-1.3, 1.3), title=f"Same task / seed / weight teacher comparison: {pairs} pairs")
    ax.legend(handles=[Line2D([], [], color=colors[family], marker="s" if version == "original" else "o", linestyle="", label=f"{family.title()} {version}") for family in ("laya", "kev") for version in ("original", "trained")], fontsize=8, loc="upper right")
    fig.supxlabel("Each point is one task pair; complete cash net benefit remains unknown.", fontsize=8)
    save(fig, "teacher_effect")


if __name__ == "__main__":
    import sys
    render_batch_figures(sys.argv[1])
