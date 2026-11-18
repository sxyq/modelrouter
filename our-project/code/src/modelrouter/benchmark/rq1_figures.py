"""Plot recorded RQ1 episodes; unscored and unexecuted positions remain distinct."""
import csv
import json
import sys
from pathlib import Path


def pareto_rows(root):
    """Use the predeclared two-task seed43 cohort, not each policy's scored subset."""
    root = Path(root).resolve()
    repo = Path(__file__).resolve().parents[5]
    config = json.loads((root / "config.json").read_text())
    cohort = {("openssl-selfsigned-cert", 43), ("regex-log", 43)}
    records = {}
    for source in [repo / p for p in config["comparison_batches"]] + [root]:
        strategies = json.loads((source / "config.json").read_text())["strategies"]
        for strategy in strategies:
            sid = strategy["id"]
            parts = sid.split("_")
            model_only = "_model_only_" in sid
            joint = (len(parts) == 3 and parts[0] in ("laya", "kev")
                     and parts[1] in ("original", "trained") and parts[2] in ("off", "on"))
            if not (strategy.get("model") or model_only or joint):
                continue
            episodes = [json.loads(p.read_text()) for p in (source / "trials").glob(f"*/{sid}/*/summary.json")]
            episodes = [r for r in episodes if (r["task_id"], r["seed"]) in cohort]
            scored = [r for r in episodes if r["reward"] in (0, 1)
                      and r["effort_comparison_eligible"] and not r.get("verifier_dependency_failure")]
            paid = [r["reference_cost_usd"] for r in episodes if r["reference_cost_usd"] is not None]
            known = [r[k] for r in episodes for k in ("generator_known_reference_usd", "teacher_known_reference_usd")
                     if r.get(k) is not None]
            panel = f"{parts[0].title()} Model-only" if model_only else "联合 Laya / Kev" if joint else "固定模型"
            label = (f"{'微调' if parts[1] == 'trained' else '原始'} {'ON' if parts[2] == 'on' else 'OFF'}"
                     if model_only or joint else sid.replace("_", " ").title())
            if joint:
                label = parts[0].title() + " " + label
            if model_only:
                label += " " + strategy["effort"].title()
            reasons = ([] if len(scored) == 2 else ["缺有效官方评分"])
            reasons += [] if len(paid) == 2 else ["缺API费用"]
            records[sid] = {"strategy_id": sid, "panel": panel, "label": label,
                "source_run_id": source.name, "cohort_size": 2, "scored_tasks": len(scored),
                "passed_tasks": sum(r["reward"] == 1 for r in scored),
                "pass_rate_percent": sum(r["reward"] for r in scored) * 50 if len(scored) == 2 else None,
                "api_reference_total_usd": sum(paid) if len(paid) == 2 else None,
                "api_reference_known_usd": sum(known) if known else None,
                "complete_cash_total_usd": None, "plot_eligible": not reasons,
                "missing": "；".join(reasons), "teacher_enabled": strategy.get("teacher_enabled", False),
                "effort": strategy.get("effort"), "checkpoint": strategy.get("checkpoint", {}).get("path"),
                "aa_snapshot_id": episodes[0]["aa_snapshot_id"] if episodes else None}
    rows = list(records.values())
    eligible = [r for r in rows if r["plot_eligible"]]
    for r in rows:
        r["pareto"] = r["plot_eligible"] and not any(
            other["api_reference_total_usd"] <= r["api_reference_total_usd"]
            and other["pass_rate_percent"] >= r["pass_rate_percent"]
            and (other["api_reference_total_usd"] < r["api_reference_total_usd"]
                 or other["pass_rate_percent"] > r["pass_rate_percent"]) for other in eligible)
    return rows


def render_pareto_comparison(root, rows):
    """Draw measured Pareto points; missing cost or quality remains unplotted."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    root = Path(root)
    plt.rcParams.update({"font.family": "PingFang HK", "font.size": 10, "axes.unicode_minus": False,
                         "pdf.fonttype": 42, "svg.fonttype": "none"})
    destination = root / "figures"
    destination.mkdir(exist_ok=True)
    with (root / "metrics/pareto_points.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    eligible = [r for r in rows if r["plot_eligible"]]
    frontier = sorted((r for r in eligible if r["pareto"]), key=lambda r: r["api_reference_total_usd"])
    colors = {"glm": "#009E73", "luna": "#0072B2", "terra": "#D55E00", "laya": "#CC79A7", "kev": "#E69F00"}
    panels = ["固定模型", "联合 Laya / Kev", "Laya Model-only", "Kev Model-only"]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True, sharey=True)
    fig.subplots_adjust(left=.075, right=.975, bottom=.19, top=.85, hspace=.38, wspace=.16)
    limits = (min(r["api_reference_total_usd"] for r in eligible) * .7,
              max(r["api_reference_total_usd"] for r in eligible) * 1.35)
    for index, (ax, panel) in enumerate(zip(axes.flat, panels)):
        group = [r for r in eligible if r["panel"] == panel]
        ax.set(xscale="log", xlim=limits, ylim=(0, 116), yticks=[0, 25, 50, 75, 100])
        ax.set_title(f"{'ABCD'[index]}  {panel}（{len(group)}组费用与评分齐全）", loc="left", fontsize=11, pad=12)
        ax.grid(axis="y", color="#dddddd", linewidth=.5)
        ax.spines[["top", "right"]].set_visible(False)
        ax.plot([r["api_reference_total_usd"] for r in frontier], [r["pass_rate_percent"] for r in frontier],
                "k--", linewidth=1, marker="D", markersize=5, zorder=2)
        for position, r in enumerate(sorted(group, key=lambda r: r["api_reference_total_usd"])):
            color = colors[r["strategy_id"].split("_")[0]]
            marker = {"low": "o", "high": "^", "max": "s", "xhigh": "P"}.get(r["effort"],
                        "D" if "trained" in r["strategy_id"] else "o")
            x, y = r["api_reference_total_usd"], r["pass_rate_percent"]
            ax.scatter(x, y, s=50, marker=marker, facecolor=color if r["teacher_enabled"] or panel == "固定模型" else "white",
                       edgecolor=color, linewidth=1.3, zorder=3)
            right = x > limits[1] / 2
            ax.annotate(r["label"], (x, y), xytext=(-8 if right else 8,
                        -20 if y < 75 else -(16 + 13 * (position % 5))),
                        textcoords="offset points", ha="right" if right else "left", fontsize=8.5,
                        color=color, arrowprops={"arrowstyle": "-", "color": "#aaaaaa", "lw": .5})
        if index % 2 == 0:
            ax.set_ylabel("官方完整任务通过率（%）")
        if index >= 2:
            ax.set_xlabel("同两题累计模型＋教师参考费（USD，对数轴）")
    fig.suptitle("RQ1 部分帕雷托前沿｜Terminal-Bench 2.0", fontsize=16, y=.985)
    fig.text(.5, .93, "共同任务：openssl-selfsigned-cert / regex-log · seed43 · 原始及11-11微调权重 · 固定AA v7", ha="center", fontsize=10)
    fig.legend(handles=[Line2D([], [], color="black", linestyle="--", marker="D", label="同两题全部策略的帕雷托点"),
                        Line2D([], [], color="#666666", marker="o", markerfacecolor="white", linestyle="", label="教师 OFF"),
                        Line2D([], [], color="#666666", marker="o", linestyle="", label="教师 ON（Luna Low）")],
               loc="lower center", bbox_to_anchor=(.5, .10), ncol=3, frameon=False, fontsize=9)
    fig.text(.5, .065, f"每点为同2题有效官方评分（含有评分的超时）；{len(eligible)}/{len(rows)}组可定位，另{len(rows)-len(eligible)}组缺项。", ha="center", fontsize=10)
    fig.text(.5, .035, "费用累计全部尝试；供应商实收、Router、工具及资源费用缺项。89题完整任务—总现金成本前沿待数据齐全。", ha="center", fontsize=9)
    for extension in ("png", "svg", "pdf"):
        fig.savefig(destination / f"rq1_pareto_partial.{extension}", dpi=300)
    plt.close(fig)
    report = ["# RQ1 部分帕雷托前沿\n",
        "**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**\n",
        "共同任务：openssl-selfsigned-cert、regex-log；seed43；原始与11-11微调实体；AA v7。\n",
        "通过率只在同两题均有有效官方Reward时计算，含有评分的超时；费用累计全部尝试及晚到响应的模型＋教师参考费。正常提交、超时与未评分分别沿原记录保留。完整现金费用缺项保持空值。\n",
        "![部分帕雷托前沿](../figures/rq1_pareto_partial.png)\n",
        "| 策略 | 有效评分 | 通过数 | 同两题Pass率 | 累计API参考费USD | 状态 |",
        "|---|---:|---:|---:|---:|---|"]
    for r in rows:
        rate = "未知" if r["pass_rate_percent"] is None else f"{r['pass_rate_percent']:.0f}%"
        cost = "未知" if r["api_reference_total_usd"] is None else f"{r['api_reference_total_usd']:.8f}"
        report.append(f"| {r['strategy_id']} | {r['scored_tasks']}/2 | {r['passed_tasks']} | {rate} | {cost} | {'帕雷托点' if r['pareto'] else r['missing'] or '已绘制'} |")
    (root / "metrics/pareto_review.md").write_text("\n".join(report) + "\n")
    return frontier


def model_only_effort_rows(root):
    """Summarize current Terminal-Bench 2.0 Model-only strategies by effort."""
    root = Path(root).resolve()
    path = root / "metrics/per_strategy.csv"
    efforts = {"low": 0, "high": 1, "max": 2}
    rows = []
    for raw in csv.DictReader(path.open(encoding="utf-8-sig")):
        sid = raw["strategy_id"]
        if raw.get("subset") != "all" or "_model_only_" not in sid:
            continue
        prefix, effort = sid.split("_model_only_", 1)
        family, checkpoint, teacher = prefix.split("_")
        reward_1 = int(raw.get("reward_1") or 0)
        reward_0 = int(raw.get("reward_0") or 0)
        scored = reward_1 + reward_0
        attempted = int(raw.get("attempted") or 0)
        generator_cost = (float(raw["generator_known_reference_usd"])
                          if raw.get("generator_known_reference_usd") else None)
        teacher_cost = (float(raw["teacher_known_reference_usd"])
                        if raw.get("teacher_known_reference_usd") else None)
        known_cost = sum(v for v in (generator_cost, teacher_cost) if v is not None)
        rows.append({
            "source_run_id": root.name,
            "strategy_id": sid,
            "family": family,
            "checkpoint": checkpoint,
            "teacher": teacher,
            "effort": effort,
            "planned_positions": int(raw["tasks"]),
            "completed_positions": attempted,
            "running_positions": int(raw.get("running") or 0),
            "not_started_positions": int(raw.get("not_started") or 0),
            "scored_positions": scored,
            "reward_1": reward_1,
            "reward_0": reward_0,
            "scored_pass_rate_percent": 100 * reward_1 / scored if scored else None,
            "known_generator_reference_usd": generator_cost,
            "known_teacher_reference_usd": teacher_cost,
            "known_reference_total_usd": known_cost,
            "known_reference_per_completed_position_usd": known_cost / attempted if attempted else None,
            "unknown_provider_cost_requests": int(raw.get("unknown_provider_cost_requests") or 0),
            "verifier_dependency_failed_positions": int(raw.get("verifier_dependency_failed_positions") or 0),
            "complete_cost_usd": raw.get("complete_cost_usd") or "",
            "supplier_billed_usd": raw.get("supplier_billed_usd") or "",
        })
    rows.sort(key=lambda r: (r["family"], r["checkpoint"], r["teacher"], efforts[r["effort"]]))
    return rows


def render_model_only_effort(root, rows):
    """Plot all Model-only checkpoints on one cost/quality plane."""
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import LogLocator, FuncFormatter

    root = Path(root)
    destination = root / "figures"
    destination.mkdir(exist_ok=True)
    table = root / "metrics/model_only_effort_points.csv"
    with table.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    family_colors = {"laya": "#0072B2", "kev": "#D55E00"}
    checkpoint_lines = {"original": "-", "trained": "--"}
    effort_markers = {"low": "o", "high": "^", "max": "s"}
    effort_order = {"low": 0, "high": 1, "max": 2}
    plot_rows = [r for r in rows if r["known_reference_per_completed_position_usd"]
                 and r["scored_pass_rate_percent"] is not None]
    groups = {}
    for r in plot_rows:
        groups.setdefault((r["family"], r["checkpoint"], r["teacher"]), []).append(r)

    plt.rcParams.update({"font.family": "PingFang HK", "font.size": 10,
                         "axes.unicode_minus": False, "pdf.fonttype": 42,
                         "svg.fonttype": "none"})
    fig, ax = plt.subplots(figsize=(11, 8.5))
    fig.subplots_adjust(left=.12, right=.98, top=.82, bottom=.34)
    for (family, checkpoint, teacher), group in groups.items():
        group.sort(key=lambda r: effort_order[r["effort"]])
        color = family_colors[family]
        linestyle = checkpoint_lines[checkpoint]
        xs = [r["known_reference_per_completed_position_usd"] for r in group]
        ys = [r["scored_pass_rate_percent"] for r in group]
        ax.plot(xs, ys, color=color, linestyle=linestyle, linewidth=1.35, alpha=.82, zorder=1)
        for r in group:
            x = r["known_reference_per_completed_position_usd"]
            y = r["scored_pass_rate_percent"]
            face = color if teacher == "on" else "white"
            ax.scatter(x, y, marker=effort_markers[r["effort"]], s=62,
                       facecolor=face, edgecolor=color, linewidth=1.35, zorder=3)
            if r["running_positions"]:
                ax.scatter(x, y, marker="o", s=108, facecolor="none",
                           edgecolor="#222222", linewidth=1.2, zorder=4)

    series_handles = []
    for family in ("laya", "kev"):
        for checkpoint in ("original", "trained"):
            for teacher in ("off", "on"):
                color = family_colors[family]
                label = "{} · {} · Teacher {}".format(
                    family.title(), "微调" if checkpoint == "trained" else "原版", teacher.upper())
                series_handles.append(Line2D(
                    [], [], color=color, linestyle=checkpoint_lines[checkpoint],
                    marker="o", markerfacecolor="white" if teacher == "off" else color,
                    markeredgecolor=color, linewidth=1.3, markersize=6, label=label))
    effort_handles = [Line2D([], [], color="#444444", marker=effort_markers[e],
                             linestyle="", markersize=6, label=e.title())
                      for e in ("low", "high", "max")]

    total = sum(r["planned_positions"] for r in rows)
    done = sum(r["completed_positions"] for r in rows)
    running = sum(r["running_positions"] for r in rows)
    pending = sum(r["not_started_positions"] for r in rows)
    valid_scores = sum(r["scored_positions"] for r in rows)
    unknown_requests = sum(r["unknown_provider_cost_requests"] for r in rows)
    scored_counts = [r["scored_positions"] for r in rows]
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(LogLocator(base=10))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: "${:g}".format(x)))
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("已知模型 + 教师参考费 / 已完成任务位置（USD/位置，对数轴）")
    ax.set_ylabel("有效官方评分通过率（%）")
    ax.set_title("Terminal-Bench 2.0 · Model-only：Laya / Kev 原版与微调版", loc="left", fontsize=15, pad=14)
    ax.grid(True, which="major", color="#dedede", linewidth=.55)
    ax.spines[["top", "right"]].set_visible(False)
    ax.margins(x=.12, y=.06)
    fig.text(.5, .915, "每条线按 Low → High → Max 连接；颜色=Laya/Kev，线型=原版/微调，空心/实心=Teacher OFF/ON",
             ha="center", fontsize=9.5)
    fig.legend(handles=series_handles, loc="lower center", bbox_to_anchor=(.5, .205),
               ncol=4, frameon=False, fontsize=8.8, columnspacing=1.35)
    fig.legend(handles=effort_handles, loc="lower center", bbox_to_anchor=(.5, .155),
               ncol=3, frameon=False, fontsize=8.8)
    fig.text(.5, .095,
             "24 个策略 × 89 个计划位置：已结束 {}，运行中 {}，未开始 {}；有效评分 {}，每策略 n={}–{}。".format(
                 done, running, pending, valid_scores, min(scored_counts), max(scored_counts)),
             ha="center", fontsize=9)
    fig.text(.5, .055,
             "费用仅含已知模型/教师参考费；{} 次请求费用未知，完整现金成本栏为空。黑色外圈表示该策略仍有运行中的任务。".format(unknown_requests),
             ha="center", fontsize=8.6)
    fig.savefig(destination / "rq1_model_only_effort_comparison.png", dpi=300, bbox_inches="tight")
    fig.savefig(destination / "rq1_model_only_effort_comparison.pdf", bbox_inches="tight")
    plt.close(fig)


def render_batch_figures(root):
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    root = Path(root)
    csv.field_size_limit(sys.maxsize)
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
    fees.margins(x=.35)
    fig.suptitle("Terminal-Bench 2.0")
    fig.supxlabel("Supplier billing and resource USD are unknown.", fontsize=8)
    save(fig, "success_cost_frontier")

    fixed = [s["id"] for s in strategies if s["stage"] == "fixed" or s.get("effort")]
    fig, ax = plt.subplots(figsize=(9, max(4.6, len(fixed) * .34 + 1.5)), layout="constrained")
    for row in ended:
        cost = row.get("latest_trial_reference_usd", row["reference_cost_usd"])
        if row["strategy_id"] not in fixed or not cost:
            continue
        reward = row["reward"]
        eligible = row["effort_comparison_eligible"] == "True" and row.get("verifier_dependency_failure") != "True"
        marker = "o" if reward and float(reward) == 1 and eligible else "x" if reward and float(reward) == 0 and eligible else "^"
        ax.scatter(float(cost), fixed.index(row["strategy_id"]), marker=marker, color=colors[row["strategy_id"].split("_")[0]], alpha=.7)
    ax.set(yticks=range(len(fixed)), yticklabels=fixed, xlabel="Final episode model + teacher reference fee (USD)", title="Fixed requested Native Effort: actual task results")
    ax.invert_yaxis()
    fig.supxlabel("Circle: Reward 1; cross: Reward 0; triangle: no eligible score. Episodes with incomplete fees omitted.", fontsize=8)
    save(fig, "model_effort_comparison")

    lookup = {(r["task_id"], r["strategy_id"], r["seed"]): r for r in ended}
    fig, ax = plt.subplots(figsize=(7.2, 4.2), layout="constrained")
    pairs = 0
    for row in ended:
        if "_off" not in row["strategy_id"]:
            continue
        other = lookup.get((row["task_id"], row["strategy_id"].replace("_off", "_on", 1), row["seed"]))
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
    if "--model-only-effort" in sys.argv[2:]:
        render_model_only_effort(sys.argv[1], model_only_effort_rows(sys.argv[1]))
    elif "--pareto" in sys.argv[2:]:
        render_pareto_comparison(sys.argv[1], pareto_rows(sys.argv[1]))
    else:
        render_batch_figures(sys.argv[1])
