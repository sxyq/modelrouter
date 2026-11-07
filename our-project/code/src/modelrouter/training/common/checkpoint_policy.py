"""Retention decisions for comparable training cohorts."""
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from .checkpoint_metrics import *
from .checkpoint_identity import *
from .checkpoint_identity import _finite_metric, _node_primary_sort_key, _rankable_node

def evaluate_cohort_retention(
    nodes: List[Dict[str, Any]],
    pinned_map: Dict[str, List[str]],
    s2_audit_passed: bool = False,
    allow_legacy_reference_eval: bool = False,
    baseline_0: Optional[Dict[str, Any]] = None,
    out_root: Optional[Path] = None,
) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    """Evaluate Three-Tier Baselines (BASELINE_0/1/2), Multi-Metric Composite Scores, and Top 30% retention.

    Implements Sections 2, 3, and 4:
    1. Strictly separates new-protocol checkpoints from `LEGACY_INPUT_PROTOCOL`.
    2. Never mixes S1, S2, and S3 rankings.
    3. Within each Run, selects at most 1 best Epoch (`is_run_best_epoch`) for non-dependent retention.
    4. Deduplicates Runs by `dedup_signature = (protocol_version, data_manifest_hash, config_hash, seed)`
       so each distinct Run contributes at most 1 record (its best Epoch) to `BASELINE_1` & `BASELINE_2`.
    5. Evaluates Conditions A (beat `BASELINE_0`, score > 100), B (`score >= 0.98 * loo_robust_mean_score`),
       C (Top 30% `ceil(0.30 * N)` when N >= 5), D (Cold-Start Top-2 when N < 5), E (Pareto tie-break),
       and F (Mandatory retention: `PINNED_PARENT`, Global S1 champions, per-batch `B01..B07` best passing Cond A).
    """
    b0 = baseline_0 or DEFAULT_BASELINE_0
    b0_val = b0.get("validation") or DEFAULT_BASELINE_0["validation"]
    decisions: Dict[str, Dict[str, Any]] = {}
    group_summaries: Dict[str, Dict[str, Any]] = {}

    # Attach composite scores and dedup signature to every node first
    by_group: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        is_legacy = bool(node.get("legacy_input_protocol"))
        if is_legacy and not allow_legacy_reference_eval:
            continue
        family = node.get("task_family") or primary_task_family(node)
        node["task_family"] = family
        comp = compute_node_composite_scores(
            node.get("validation") or {},
            task_family=family,
            baseline_0=b0,
            s2_audit_passed=s2_audit_passed,
        )
        node["composite_scores"] = comp
        node["primary_score"] = comp["primary_score"]
        node["s1_score"] = comp["s1_score"]
        node["s2_score"] = comp["s2_score"]
        node["s2_diagnostic_score"] = comp["s2_diagnostic_score"]
        node["s2_status"] = comp["s2_status"]
        node["s3_score"] = comp["s3_score"]
        node["beats_baseline_0"] = comp["beats_baseline_0"]
        # Multi-tier selection score: combine internal score with external DEV score if present
        dev_res = node.get("external_dev_result")
        sel_info = compute_composite_selection_score(comp["primary_score"], dev_res)
        node["selection_score"] = sel_info["selection_score"]
        node["external_dev_status"] = sel_info["external_dev_status"]
        node["external_dev_score"] = sel_info["external_dev_score"]
        node["selection_formula"] = sel_info["formula_used"]
        node["dedup_signature"] = node.get("dedup_signature") or compute_run_dedup_signature(node, out_root=out_root)
        gid = build_comparable_group_id(node)
        node["comparable_group_id"] = gid
        by_group[gid].append(node)

    # Identify within-run best epoch across all active nodes
    nodes_by_run: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        if bool(node.get("legacy_input_protocol")) and not allow_legacy_reference_eval:
            continue
        nodes_by_run[node["run_id"]].append(node)

    run_best_ckpt_id: Dict[str, str] = {}
    for rid, rnodes in nodes_by_run.items():
        fam = rnodes[0].get("task_family", "S1")
        best_epoch = select_run_best_epoch({**rnodes[0], "history": rnodes}, b0, s2_audit_passed)
        best_n = next((n for n in rnodes if n.get("epoch") == best_epoch), None)
        if best_n is None:
            for rn in rnodes:
                rn["is_run_best_epoch"] = False
            continue
        run_best_ckpt_id[rid] = best_n["checkpoint_id"]
        for rn in rnodes:
            rn["is_run_best_epoch"] = (rn["checkpoint_id"] == best_n["checkpoint_id"])

    # Identify canonical Run for each `dedup_signature` within each comparable group
    canonical_run_by_sig: Dict[Tuple[str, str], str] = {}
    for gid, gnodes in sorted(by_group.items()):
        for n in sorted(gnodes, key=lambda x: (str(x.get("started_at") or ""), str(x["run_id"]), int(x.get("epoch", 0)))):
            sig_key = (gid, n["dedup_signature"])
            if sig_key not in canonical_run_by_sig:
                canonical_run_by_sig[sig_key] = n["run_id"]
        for n in gnodes:
            sig_key = (gid, n["dedup_signature"])
            n["canonical_run_id"] = canonical_run_by_sig[sig_key]
            n["is_duplicate_run_signature"] = (n["run_id"] != canonical_run_by_sig[sig_key])

    # 1. Global S1 champions (Condition F: strictly within the active protocol cohort, excluding duplicate run signatures)
    s1_candidates = [
        n for n in nodes
        if (not n.get("legacy_input_protocol") or allow_legacy_reference_eval)
        and not n.get("is_duplicate_run_signature")
        and n.get("task_family") == "S1"
        and isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))
    ]
    global_best_s1_score_id = None
    global_best_s1_loss_id = None
    global_best_s1_acc_id = None
    global_best_s1_brier_id = None
    batch_best_s1_ids: Dict[str, str] = {}

    if s1_candidates:
        best_score_node = max(
            s1_candidates,
            key=lambda n: (
                n.get("s1_score") if isinstance(n.get("s1_score"), (int, float)) else -999.0,
                -(n["validation"]["S1"]["loss"]),
                n["validation"]["S1"].get("accuracy") or 0.0,
            ),
        )
        global_best_s1_score_id = best_score_node["checkpoint_id"]

        best_loss_node = min(
            s1_candidates,
            key=lambda n: (
                n["validation"]["S1"]["loss"],
                -(n["validation"]["S1"].get("accuracy") or 0.0),
                n["validation"]["S1"].get("brier") or 999.0,
            ),
        )
        global_best_s1_loss_id = best_loss_node["checkpoint_id"]

        best_acc_node = max(
            s1_candidates,
            key=lambda n: (
                n["validation"]["S1"].get("accuracy") or -1.0,
                -(n["validation"]["S1"]["loss"]),
                -(n["validation"]["S1"].get("brier") or 999.0),
            ),
        )
        global_best_s1_acc_id = best_acc_node["checkpoint_id"]

        brier_nodes = [n for n in s1_candidates if isinstance(n["validation"]["S1"].get("brier"), (int, float))]
        if brier_nodes:
            best_brier_node = min(
                brier_nodes,
                key=lambda n: (
                    n["validation"]["S1"]["brier"],
                    n["validation"]["S1"]["loss"],
                    -(n["validation"]["S1"].get("accuracy") or 0.0),
                ),
            )
            global_best_s1_brier_id = best_brier_node["checkpoint_id"]

        # Per-batch best S1 checkpoint that passes Condition A (`beats_baseline_0`)
        by_batch: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for n in s1_candidates:
            bid = n.get("batch_id")
            if bid and n.get("is_run_best_epoch") and n.get("beats_baseline_0"):
                by_batch[str(bid)].append(n)
        for bid, bnodes in by_batch.items():
            best_b = max(
                bnodes,
                key=lambda n: (
                    n.get("s1_score") or -999.0,
                    -(n["validation"]["S1"]["loss"]),
                ),
            )
            batch_best_s1_ids[bid] = best_b["checkpoint_id"]

    # 2. Evaluate each comparable group using Three-Tier Baselines + Top 30%
    for gid, gnodes in sorted(by_group.items()):
        if not gnodes:
            continue
        family = gnodes[0].get("task_family", "S1")
        n_total_epochs = len(gnodes)

        # Distinct Runs contributing to BASELINE_1 & BASELINE_2 (1 best epoch per distinct non-duplicate Run)
        distinct_run_best_nodes = [
            n for n in gnodes
            if n.get("is_run_best_epoch") and not n.get("is_duplicate_run_signature")
        ]
        duplicate_run_ids = sorted({
            n["run_id"] for n in gnodes if n.get("is_duplicate_run_signature")
        })
        n_distinct_runs = len(distinct_run_best_nodes)
        cold_start = n_distinct_runs < MIN_COMPARABLE_RUNS
        top_30pct_quota = (
            COLD_START_TOP_K if cold_start else max(1, int(math.ceil(n_distinct_runs * RETENTION_TARGET)))
        )

        # Pareto frontier among distinct run best nodes
        pareto_ids = compute_pareto_frontier_ids(distinct_run_best_nodes, task_family=family)
        for n in gnodes:
            n["is_pareto_front"] = (n["checkpoint_id"] in pareto_ids)

        # Compute BASELINE_1 & BASELINE_2 distributions over distinct_run_best_nodes
        run_scores = [
            float(n["primary_score"])
            for n in distinct_run_best_nodes
            if isinstance(n.get("primary_score"), (int, float))
        ]
        score_stats = compute_robust_distribution_stats(run_scores, trim_ratio=TRIM_RATIO)

        # Also compute epoch-level & run-level metric averages for compatibility and diagnostics
        if family == "S1":
            run_losses = [n["validation"]["S1"]["loss"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
            run_accs = [n["validation"]["S1"]["accuracy"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S1") or {}).get("accuracy"), (int, float))]
            run_briers = [n["validation"]["S1"]["brier"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S1") or {}).get("brier"), (int, float))]
            ep_losses = [n["validation"]["S1"]["loss"] for n in gnodes if not n.get("is_duplicate_run_signature") and isinstance((n.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
            ep_accs = [n["validation"]["S1"]["accuracy"] for n in gnodes if not n.get("is_duplicate_run_signature") and isinstance((n.get("validation", {}).get("S1") or {}).get("accuracy"), (int, float))]
            ep_briers = [n["validation"]["S1"]["brier"] for n in gnodes if not n.get("is_duplicate_run_signature") and isinstance((n.get("validation", {}).get("S1") or {}).get("brier"), (int, float))]

            loss_stats = compute_robust_distribution_stats(run_losses, trim_ratio=TRIM_RATIO)
            acc_stats = compute_robust_distribution_stats(run_accs, trim_ratio=TRIM_RATIO)
            brier_stats = compute_robust_distribution_stats(run_briers, trim_ratio=TRIM_RATIO)

            mean_loss = loss_stats["robust_mean"]
            mean_acc = acc_stats["robust_mean"]
            mean_brier = brier_stats["robust_mean"]
            mean_score = score_stats["robust_mean"]
            mean_score_floor = round(mean_score * MEAN_FLOOR_RATIO, 4) if mean_score is not None else None

            # Evaluate each node in the group
            qualified_best_nodes: List[Dict[str, Any]] = []
            node_eval: Dict[str, Dict[str, Any]] = {}
            for n in gnodes:
                cid = n["checkpoint_id"]
                rid = n["run_id"]
                s1 = n.get("validation", {}).get("S1") or {}
                l_val = s1.get("loss")
                a_val = s1.get("accuracy")
                b_val = s1.get("brier")
                sc_val = n.get("primary_score")

                # Leave-one-out BASELINE_1 for this Run
                other_best = [x for x in distinct_run_best_nodes if x["run_id"] != n.get("canonical_run_id")]
                other_scores = [float(x["primary_score"]) for x in other_best if isinstance(x.get("primary_score"), (int, float))]
                other_losses = [float(x["validation"]["S1"]["loss"]) for x in other_best if isinstance((x.get("validation", {}).get("S1") or {}).get("loss"), (int, float))]
                loo_score_stats = compute_robust_distribution_stats(other_scores, trim_ratio=TRIM_RATIO) if other_scores else score_stats
                loo_loss_stats = compute_robust_distribution_stats(other_losses, trim_ratio=TRIM_RATIO) if other_losses else loss_stats
                loo_mean_score = loo_score_stats["robust_mean"] if loo_score_stats["robust_mean"] is not None else mean_score
                loo_mean_loss = loo_loss_stats["robust_mean"] if loo_loss_stats["robust_mean"] is not None else mean_loss
                loo_floor = round(loo_mean_score * MEAN_FLOOR_RATIO, 4) if loo_mean_score is not None else None

                # Condition A: Beat BASELINE_0 (`S1_score > 100.0`, `loss <= L0`, `acc >= A0 - 0.005`)
                cond_a_b0 = bool(n.get("beats_baseline_0"))
                # Classical P1 Condition A/B diagnostics
                p1_cond_a = bool(
                    loo_mean_loss is not None and mean_acc is not None
                    and isinstance(l_val, (int, float)) and isinstance(a_val, (int, float))
                    and l_val <= loo_mean_loss * (1.0 - S1_LOSS_IMPROVEMENT_REL)
                    and a_val >= mean_acc - S1_ACC_DEGRADATION_TOL
                )
                p1_cond_b = bool(
                    loo_mean_loss is not None and mean_acc is not None and mean_brier is not None
                    and isinstance(l_val, (int, float)) and isinstance(a_val, (int, float)) and isinstance(b_val, (int, float))
                    and a_val >= mean_acc + S1_ACC_IMPROVEMENT_ABS
                    and l_val <= loo_mean_loss * (1.0 + S1_LOSS_BRIER_DEGRADATION_REL)
                    and b_val <= mean_brier * (1.0 + S1_LOSS_BRIER_DEGRADATION_REL)
                )
                # Condition B: Composite score >= 0.98 * historical robust mean (leave-one-out)
                cond_b_mean_floor = bool(
                    loo_floor is not None
                    and isinstance(sc_val, (int, float))
                    and sc_val >= loo_floor
                )
                passes_thresholds = (
                    bool(cond_a_b0 or n.get("is_run_best_epoch"))
                    if cold_start
                    else bool(cond_a_b0 and (cond_b_mean_floor or p1_cond_a or p1_cond_b))
                )
                node_eval[cid] = {
                    "cond_a_baseline0_pass": cond_a_b0,
                    "cond_b_mean_floor_pass": cond_b_mean_floor,
                    "cond_a_pass": cond_a_b0 or p1_cond_a,
                    "cond_b_pass": cond_b_mean_floor or p1_cond_b,
                    "loo_mean_score": loo_mean_score,
                    "loo_score_floor": loo_floor,
                    "threshold_pass": passes_thresholds,
                    "cold_start": cold_start,
                }
                if (
                    passes_thresholds
                    and n.get("is_run_best_epoch")
                    and not n.get("is_duplicate_run_signature")
                    and isinstance(sc_val, (int, float))
                ):
                    qualified_best_nodes.append(n)

            # Condition C & E: Rank qualified run-best nodes by Composite Score + Pareto tie-breaker (within 0.5 pts)
            def _s1_rank_key(cand: Dict[str, Any]) -> Tuple[float, float, float, float]:
                sc = float(cand.get("primary_score") or 0.0)
                # Condition E: Pareto frontier models receive +PARETO_TIE_MARGIN (0.5) tie-break priority
                eff_sc = sc + (PARETO_TIE_MARGIN if cand.get("is_pareto_front") else 0.0)
                s1_v = cand["validation"]["S1"]
                return (
                    -round(eff_sc, 4),
                    -round(sc, 4),
                    float(s1_v["loss"]),
                    -(float(s1_v.get("accuracy") or 0.0)),
                )

            ranked = sorted(qualified_best_nodes, key=_s1_rank_key)
            non_pinned_ranked = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
            top_k_ids = [n["checkpoint_id"] for n in non_pinned_ranked[:top_30pct_quota]]

            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S1",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_total_epochs,
                "distinct_run_count": n_distinct_runs,
                "distinct_completed_runs": n_distinct_runs,
                "duplicate_runs_excluded": len(duplicate_run_ids),
                "duplicate_run_ids_excluded": duplicate_run_ids,
                "cold_start_mode": cold_start,
                "min_controls_required": MIN_COMPARABLE_RUNS,
                "retention_target_ratio": RETENTION_TARGET,
                "top_k_limit": top_30pct_quota,
                "top_k_quota": top_30pct_quota,
                "baseline_0": {
                    "s1_score": S1_SCORE_BASELINE,
                    "loss": b0_val["S1"]["loss"],
                    "accuracy": b0_val["S1"]["accuracy"],
                    "brier": b0_val["S1"]["brier"],
                    "ece": b0_val["S1"]["ece"],
                },
                "baseline_1_historical": {
                    "score_stats": score_stats,
                    "loss_stats": loss_stats,
                    "accuracy_stats": acc_stats,
                    "brier_stats": brier_stats,
                    "trimmed_mean_active": n_distinct_runs >= 10,
                    "mean_floor_ratio": MEAN_FLOOR_RATIO,
                    "mean_score_floor": mean_score_floor,
                },
                "baseline_1_stats": {
                    "score": score_stats,
                    "loss": loss_stats,
                    "accuracy": acc_stats,
                    "brier": brier_stats,
                },
                "baseline_2_quantiles": {
                    "p50_score": score_stats["p50"],
                    "p70_score": score_stats["p70"],
                    "p90_score": score_stats["p90"],
                    "best_score": score_stats["max"],
                    "P50": score_stats["p50"],
                    "P70": score_stats["p70"],
                    "P90": score_stats["p90"],
                    "BEST": score_stats["max"],
                    "pareto_frontier_ids": sorted(pareto_ids),
                },
                "mean_val_loss": round(sum(ep_losses) / len(ep_losses), 4) if ep_losses else None,
                "mean_accuracy": round(sum(ep_accs) / len(ep_accs), 4) if ep_accs else None,
                "mean_brier": round(sum(ep_briers) / len(ep_briers), 4) if ep_briers else None,
                "run_best_mean_val_loss": mean_loss,
                "run_best_mean_accuracy": mean_acc,
                "run_best_mean_brier": mean_brier,
                "mean_composite_score": score_stats["mean"],
                "trimmed_mean_composite_score": score_stats["trimmed_mean"],
                "thresholds": {
                    "baseline_0_score": S1_SCORE_BASELINE,
                    "mean_score_floor": mean_score_floor,
                    "p70_top30pct_score": score_stats["p70"],
                    "p90_top10pct_score": score_stats["p90"],
                    "top_30pct_quota": top_30pct_quota,
                },
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "is_run_best_epoch": n.get("is_run_best_epoch", False),
                        "is_duplicate_run_signature": n.get("is_duplicate_run_signature", False),
                        "is_pareto_front": n.get("is_pareto_front", False),
                        "s1_score": n.get("s1_score"),
                        "loss": (n.get("validation", {}).get("S1") or {}).get("loss"),
                        "accuracy": (n.get("validation", {}).get("S1") or {}).get("accuracy"),
                        "brier": (n.get("validation", {}).get("S1") or {}).get("brier"),
                        "ece": (n.get("validation", {}).get("S1") or {}).get("ece"),
                        "cond_a": node_eval[n["checkpoint_id"]]["cond_a_pass"],
                        "cond_b": node_eval[n["checkpoint_id"]]["cond_b_pass"],
                        "in_top_k": n["checkpoint_id"] in top_k_ids,
                    }
                    for n in gnodes
                ],
            }

            for n in gnodes:
                cid = n["checkpoint_id"]
                ev = node_eval[cid]
                reasons: List[str] = []
                if cid in pinned_map:
                    reasons.append(f"pinned_parent_for:{','.join(pinned_map[cid])}")
                if not n.get("is_duplicate_run_signature"):
                    if cid == global_best_s1_score_id and n.get("beats_baseline_0"):
                        reasons.append("global_best_s1_composite_score")
                    if cid == global_best_s1_loss_id:
                        reasons.append("global_best_s1_loss")
                    if cid == global_best_s1_acc_id:
                        reasons.append("global_best_s1_accuracy")
                    if cid == global_best_s1_brier_id and n.get("is_run_best_epoch"):
                        reasons.append("global_best_s1_brier")
                    bid = str(n.get("batch_id") or "")
                    if bid and batch_best_s1_ids.get(bid) == cid:
                        reasons.append(f"batch_{bid}_best_s1_score")
                    if cid in top_k_ids:
                        if cold_start:
                            reasons.append(f"group_cold_start_top_{top_30pct_quota}(runs={n_distinct_runs}<{MIN_COMPARABLE_RUNS})")
                        else:
                            reasons.append(
                                f"group_top_30pct(quota={top_30pct_quota}/{n_distinct_runs},"
                                f"score={n.get('s1_score')}>=floor_{ev['loo_score_floor']})"
                            )
                        if n.get("is_pareto_front"):
                            reasons.append("pareto_frontier_non_dominated")

                should_retain = len(reasons) > 0
                if not should_retain:
                    if n.get("is_duplicate_run_signature"):
                        reject_reason = f"duplicate_run_signature_of_{n.get('canonical_run_id')}"
                    elif not n.get("is_run_best_epoch"):
                        reject_reason = f"non_best_epoch_within_run(best={run_best_ckpt_id.get(n['run_id'])})"
                    elif not ev["cond_a_baseline0_pass"]:
                        reject_reason = f"below_baseline_0(s1_score={n.get('s1_score')}<=100.0_or_loss_acc_degraded)"
                    elif not ev["threshold_pass"]:
                        reject_reason = (
                            f"below_historical_mean_floor(s1_score={n.get('s1_score')}<0.98*mean={ev['loo_score_floor']})"
                        )
                    else:
                        reject_reason = (
                            f"s1_outside_top_30pct(quota={top_30pct_quota}/{n_distinct_runs},p70={score_stats['p70']})"
                        )
                else:
                    reject_reason = None

                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": cid in {global_best_s1_score_id, global_best_s1_loss_id, global_best_s1_acc_id, global_best_s1_brier_id} and not n.get("is_duplicate_run_signature"),
                    "is_top_k": cid in top_k_ids,
                    "is_pareto_front": bool(n.get("is_pareto_front")),
                    "is_run_best_epoch": bool(n.get("is_run_best_epoch")),
                    "is_duplicate_run_signature": bool(n.get("is_duplicate_run_signature")),
                    "primary_score": n.get("primary_score"),
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S1",
                    "cond_a_pass": ev["cond_a_pass"],
                    "cond_b_pass": ev["cond_b_pass"],
                }

        elif family == "S2":
            # S2 Rule (Section 3.2 & 4): before independent audit passes, DIAGNOSTIC_ONLY,
            # never crown as global champion, retain at most 1 diagnostic model across the group.
            s2_losses = [n["validation"]["S2"]["loss"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S2") or {}).get("loss"), (int, float))]
            s2_accs = [n["validation"]["S2"]["accuracy"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S2") or {}).get("accuracy"), (int, float))]
            s2_briers = [n["validation"]["S2"]["brier"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S2") or {}).get("brier"), (int, float))]
            mean_loss = sum(s2_losses) / len(s2_losses) if s2_losses else None
            mean_acc = sum(s2_accs) / len(s2_accs) if s2_accs else None
            mean_brier = sum(s2_briers) / len(s2_briers) if s2_briers else None

            if not s2_audit_passed:
                ranked = sorted(
                    distinct_run_best_nodes,
                    key=lambda n: (
                        (n.get("validation", {}).get("S2") or {}).get("loss") if isinstance((n.get("validation", {}).get("S2") or {}).get("loss"), (int, float)) else 999.0,
                        n.get("epoch", 99),
                    ),
                )
                top_k_ids = [ranked[0]["checkpoint_id"]] if ranked else []
                s2_quota = 1
            else:
                qualified = [
                    n for n in distinct_run_best_nodes
                    if n.get("beats_baseline_0")
                    and (n.get("composite_scores", {}).get("S2_detail") or {}).get("beats_majority_baseline")
                    and (
                        cold_start
                        or (
                            score_stats["robust_mean"] is not None
                            and isinstance(n.get("primary_score"), (int, float))
                            and n["primary_score"] >= score_stats["robust_mean"] * MEAN_FLOOR_RATIO
                        )
                    )
                ]
                ranked = sorted(
                    qualified,
                    key=lambda n: (
                        -(float(n.get("primary_score") or 0.0)),
                        n["validation"]["S2"]["loss"],
                        -(n["validation"]["S2"].get("balanced_accuracy") or 0.0),
                    ),
                )
                non_pinned = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
                s2_quota = top_30pct_quota
                top_k_ids = [n["checkpoint_id"] for n in non_pinned[:s2_quota]]

            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S2",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_total_epochs,
                "distinct_run_count": n_distinct_runs,
                "duplicate_run_ids_excluded": duplicate_run_ids,
                "s2_audit_passed": s2_audit_passed,
                "s2_policy_mode": "AUDIT_PASSED_TOP_30PCT" if s2_audit_passed else "DIAGNOSTIC_SINGLE_CAP_PENDING_AUDIT",
                "majority_baseline": S2_VAL_BASELINE,
                "baseline_1_historical": {"score_stats": score_stats},
                "baseline_2_quantiles": {
                    "p50_score": score_stats["p50"],
                    "p70_score": score_stats["p70"],
                    "p90_score": score_stats["p90"],
                    "best_score": score_stats["max"],
                },
                "top_k_limit": s2_quota,
                "mean_val_loss": round(mean_loss, 4) if mean_loss is not None else None,
                "mean_accuracy": round(mean_acc, 4) if mean_acc is not None else None,
                "mean_brier": round(mean_brier, 4) if mean_brier is not None else None,
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "is_run_best_epoch": n.get("is_run_best_epoch", False),
                        "s2_score": n.get("s2_score"),
                        "s2_diagnostic_score": n.get("s2_diagnostic_score"),
                        "s2_status": n.get("s2_status"),
                        "loss": (n.get("validation", {}).get("S2") or {}).get("loss"),
                        "accuracy": (n.get("validation", {}).get("S2") or {}).get("accuracy"),
                        "balanced_accuracy": (n.get("validation", {}).get("S2") or {}).get("balanced_accuracy"),
                        "macro_f1": (n.get("validation", {}).get("S2") or {}).get("macro_f1"),
                        "brier": (n.get("validation", {}).get("S2") or {}).get("brier"),
                        "in_top_k": n["checkpoint_id"] in top_k_ids,
                    }
                    for n in gnodes
                ],
            }

            for n in gnodes:
                cid = n["checkpoint_id"]
                reasons = []
                if cid in pinned_map:
                    reasons.append(f"pinned_parent_for:{','.join(pinned_map[cid])}")
                if cid in top_k_ids and not n.get("is_duplicate_run_signature"):
                    if not s2_audit_passed:
                        reasons.append("s2_diagnostic_single_model_pending_audit(not_global_champion)")
                    else:
                        reasons.append(f"s2_audited_top_30pct(quota={s2_quota})")
                should_retain = len(reasons) > 0
                reject_reason = (
                    None if should_retain
                    else f"duplicate_run_signature_of_{n.get('canonical_run_id')}"
                    if n.get("is_duplicate_run_signature")
                    else "s2_100pct_not_trusted_pending_independent_audit(diagnostic_cap=1)"
                    if not s2_audit_passed
                    else "s2_below_majority_baseline_or_outside_top_30pct"
                )
                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": False,  # S2 is never crowned global champion before audit
                    "is_top_k": cid in top_k_ids,
                    "is_pareto_front": bool(n.get("is_pareto_front")),
                    "is_run_best_epoch": bool(n.get("is_run_best_epoch")),
                    "is_duplicate_run_signature": bool(n.get("is_duplicate_run_signature")),
                    "primary_score": n.get("primary_score"),
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S2",
                }

        else:
            # S3 Rule (Section 3.3 & 4): compare per real target against each target's majority/prior baseline
            # and rank by macro-averaged S3_score (never summing raw S3 losses).
            per_target_stats: Dict[str, Dict[str, Any]] = {}
            for t_key, base in S3_VAL_BASELINES.items():
                t_losses = []
                t_accs = []
                t_briers = []
                t_scores = []
                for n in distinct_run_best_nodes:
                    tb = (n.get("validation", {}).get("S3_by_source_target") or {}).get(t_key) or {}
                    if isinstance(tb.get("loss"), (int, float)):
                        t_losses.append(tb["loss"])
                    if isinstance(tb.get("accuracy"), (int, float)):
                        t_accs.append(tb["accuracy"])
                    if isinstance(tb.get("brier"), (int, float)):
                        t_briers.append(tb["brier"])
                    if isinstance(tb.get("s3_target_score"), (int, float)):
                        t_scores.append(tb["s3_target_score"])
                m_loss = sum(t_losses) / len(t_losses) if t_losses else None
                m_acc = sum(t_accs) / len(t_accs) if t_accs else None
                m_brier = sum(t_briers) / len(t_briers) if t_briers else None
                m_score = sum(t_scores) / len(t_scores) if t_scores else None
                per_target_stats[t_key] = {
                    "baseline_majority_accuracy": base["majority_accuracy"],
                    "baseline_prior_loss": base["prior_loss"],
                    "baseline_balanced_accuracy": base["majority_balanced_accuracy"],
                    "mean_val_loss": round(m_loss, 4) if m_loss is not None else None,
                    "mean_accuracy": round(m_acc, 4) if m_acc is not None else None,
                    "mean_brier": round(m_brier, 4) if m_brier is not None else None,
                    "mean_target_score": round(m_score, 4) if m_score is not None else None,
                    "threshold_max_loss": round(min(base["prior_loss"] * 0.995, (m_loss * 0.995) if (m_loss and not cold_start) else base["prior_loss"] * 0.995), 4),
                    "threshold_min_accuracy": round(max(base["majority_accuracy"] + 0.005, (m_acc - 0.005) if (m_acc and not cold_start) else base["majority_accuracy"] + 0.005), 4),
                }

            qualified = []
            node_s3_summary: Dict[str, Dict[str, Any]] = {}
            mean_s3_score = score_stats["robust_mean"]
            s3_score_floor = round(mean_s3_score * MEAN_FLOOR_RATIO, 4) if mean_s3_score is not None else None

            for n in gnodes:
                cid = n["checkpoint_id"]
                s3_detail = (n.get("composite_scores") or {}).get("S3_detail") or compute_s3_composite_score(
                    (n.get("validation") or {}).get("S3"),
                    (n.get("validation") or {}).get("S3_by_source_target"),
                    b0_val.get("S3"),
                )
                s3_sc = s3_detail.get("s3_score")
                passes_floor = bool(
                    cold_start
                    or (
                        s3_score_floor is not None
                        and isinstance(s3_sc, (int, float))
                        and s3_sc >= s3_score_floor
                    )
                )
                eligible = bool(s3_detail.get("beats_baseline_0") and passes_floor)
                node_s3_summary[cid] = {
                    "s3_score": s3_sc,
                    "beaten_targets": s3_detail.get("beaten_targets") or [],
                    "beaten_target_count": s3_detail.get("beaten_target_count", 0),
                    "active_target_count": s3_detail.get("active_target_count", 0),
                    "per_target_scores": s3_detail.get("per_target_scores") or {},
                    "mean_relative_loss_reduction_vs_prior": s3_detail.get("mean_relative_loss_reduction_vs_prior", -1.0),
                    "eligible": eligible,
                }
                if eligible and n.get("is_run_best_epoch") and not n.get("is_duplicate_run_signature"):
                    qualified.append(n)

            ranked = sorted(
                qualified,
                key=lambda n: (
                    -(float(node_s3_summary[n["checkpoint_id"]]["s3_score"] or 0.0)),
                    -node_s3_summary[n["checkpoint_id"]]["beaten_target_count"],
                    -node_s3_summary[n["checkpoint_id"]]["mean_relative_loss_reduction_vs_prior"],
                    n.get("epoch", 99),
                ),
            )
            non_pinned = [n for n in ranked if n["checkpoint_id"] not in pinned_map]
            top_k_ids = [n["checkpoint_id"] for n in non_pinned[:top_30pct_quota]]

            s3_accs = [n["validation"]["S3"]["accuracy"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S3") or {}).get("accuracy"), (int, float))]
            s3_briers = [n["validation"]["S3"]["brier"] for n in distinct_run_best_nodes if isinstance((n.get("validation", {}).get("S3") or {}).get("brier"), (int, float))]
            group_summaries[gid] = {
                "comparable_group_id": gid,
                "task_family": "S3",
                "protocol_version": gnodes[0].get("protocol_version"),
                "legacy_input_protocol": bool(gnodes[0].get("legacy_input_protocol")),
                "supervision_classes": gnodes[0].get("supervision_classes"),
                "checkpoint_count": n_total_epochs,
                "distinct_run_count": n_distinct_runs,
                "duplicate_run_ids_excluded": duplicate_run_ids,
                "cold_start_mode": cold_start,
                "retention_target_ratio": RETENTION_TARGET,
                "top_k_limit": top_30pct_quota,
                "ranking_rule": "per_target_macro_composite_s3_score_and_majority_baseline_filter (raw losses never summed)",
                "baseline_1_historical": {
                    "score_stats": score_stats,
                    "mean_score_floor": s3_score_floor,
                },
                "baseline_2_quantiles": {
                    "p50_score": score_stats["p50"],
                    "p70_score": score_stats["p70"],
                    "p90_score": score_stats["p90"],
                    "best_score": score_stats["max"],
                },
                "mean_accuracy": round(sum(s3_accs) / len(s3_accs), 4) if s3_accs else None,
                "mean_brier": round(sum(s3_briers) / len(s3_briers), 4) if s3_briers else None,
                "mean_composite_score": score_stats["mean"],
                "per_target_thresholds": per_target_stats,
                "top_k_checkpoints": top_k_ids,
                "scores": [
                    {
                        "checkpoint_id": n["checkpoint_id"],
                        "run_id": n["run_id"],
                        "epoch": n["epoch"],
                        "is_run_best_epoch": n.get("is_run_best_epoch", False),
                        "s3_score": node_s3_summary[n["checkpoint_id"]]["s3_score"],
                        "accuracy": (n.get("validation", {}).get("S3") or {}).get("accuracy"),
                        "brier": (n.get("validation", {}).get("S3") or {}).get("brier"),
                        "beaten_targets": node_s3_summary[n["checkpoint_id"]]["beaten_targets"],
                        "beaten_target_count": node_s3_summary[n["checkpoint_id"]]["beaten_target_count"],
                        "mean_rel_gain": node_s3_summary[n["checkpoint_id"]]["mean_relative_loss_reduction_vs_prior"],
                        "in_top_k": n["checkpoint_id"] in top_k_ids,
                    }
                    for n in gnodes
                ],
            }

            for n in gnodes:
                cid = n["checkpoint_id"]
                s3_ev = node_s3_summary[cid]
                reasons = []
                if cid in pinned_map:
                    reasons.append(f"pinned_parent_for:{','.join(pinned_map[cid])}")
                if cid in top_k_ids and not n.get("is_duplicate_run_signature"):
                    reasons.append(
                        f"s3_per_target_top_30pct(quota={top_30pct_quota},s3_score={s3_ev['s3_score']},"
                        f"beat_baseline={s3_ev['beaten_target_count']}/{s3_ev['active_target_count']})"
                    )
                should_retain = len(reasons) > 0
                if not should_retain:
                    if n.get("is_duplicate_run_signature"):
                        reject_reason = f"duplicate_run_signature_of_{n.get('canonical_run_id')}"
                    elif not n.get("is_run_best_epoch"):
                        reject_reason = f"non_best_epoch_within_run(best={run_best_ckpt_id.get(n['run_id'])})"
                    elif not s3_ev["eligible"]:
                        reject_reason = (
                            f"s3_targets_below_majority_baseline_or_b0(s3_score={s3_ev['s3_score']},"
                            f"beat={s3_ev['beaten_target_count']}/{s3_ev['active_target_count']})"
                        )
                    else:
                        reject_reason = f"s3_outside_group_top_30pct(quota={top_30pct_quota})"
                else:
                    reject_reason = None

                decisions[cid] = {
                    "should_retain": should_retain,
                    "is_pinned_parent": cid in pinned_map,
                    "is_global_best": False,
                    "is_top_k": cid in top_k_ids,
                    "is_pareto_front": bool(n.get("is_pareto_front")),
                    "is_run_best_epoch": bool(n.get("is_run_best_epoch")),
                    "is_duplicate_run_signature": bool(n.get("is_duplicate_run_signature")),
                    "primary_score": n.get("primary_score"),
                    "retention_reasons": reasons,
                    "rejection_reason": reject_reason,
                    "comparable_group_id": gid,
                    "task_family": "S3",
                    "s3_beaten_targets": s3_ev["beaten_targets"],
                    "s3_mean_rel_gain": s3_ev["mean_relative_loss_reduction_vs_prior"],
                }

    # Dual Pool Retention (Section 3):
    # 1. Old Core Pool: 5 fixed core checkpoints retained prior to policy change. Permanently preserved.
    # 2. New Core Pool: Dynamic best-of retention of ~15% (ceil(0.15 * N_new_eligible)) of eligible new run best-epochs.
    # Pinned parents (R1-e01, R2-e01) and temp recovery checkpoints are protected separately.
    is_simulation = any(n.get("run_id", "").startswith("P0_SIM_") for n in nodes)
    if not allow_legacy_reference_eval and not is_simulation:
        node_map = {n["checkpoint_id"]: n for n in nodes}

        # 1. Old Core Pool: protect the 5 historical core checkpoints
        for cid in OLD_CORE_CHECKPOINT_IDS:
            if cid in decisions:
                dec = decisions[cid]
                dec["should_retain"] = True
                dec["retention_pool"] = "OLD_CORE_POOL"
                if "retention_reasons" not in dec or dec["retention_reasons"] is None:
                    dec["retention_reasons"] = []
                if "old_core_pool_protected(5_fixed_core)" not in dec["retention_reasons"]:
                    dec["retention_reasons"].append("old_core_pool_protected(5_fixed_core)")

        # 2. Pinned parents: ensure marked as PINNED_PARENT pool
        for cid, dec in decisions.items():
            if dec.get("is_pinned_parent") or cid in pinned_map:
                dec["should_retain"] = True
                dec["retention_pool"] = "PINNED_PARENT"
                dec["rejection_reason"] = None
                if "retention_reasons" not in dec or dec["retention_reasons"] is None:
                    dec["retention_reasons"] = []
                p_reason = f"pinned_parent_protected({','.join(pinned_map.get(cid, ['dependency']))})"
                if p_reason not in dec["retention_reasons"]:
                    dec["retention_reasons"].append(p_reason)

        # 3. New Candidates: candidate unit is best epoch of each eligible independent run after policy adjustment
        # Old strategy models (P0_*, historical sweeps, etc.) were already evaluated under the old policy
        # and MUST NOT be added to the new candidate denominator.
        new_eligible_candidates = []
        for n in nodes:
            cid = n["checkpoint_id"]
            run_id = n.get("run_id", "")
            # Exclude old core checkpoints
            if cid in OLD_CORE_CHECKPOINT_IDS:
                continue
            # Exclude pre-Q012 historical completed runs from inflating new candidate denominator
            if run_id in HISTORICAL_PRE_Q012_COMPLETED_RUNS:
                continue
            # Exclude old strategy historical models from inflating the new candidate denominator
            if run_id.startswith(("P0_", "R0_", "N", "R1", "R2", "R3")) or n.get("experiment_group") in ("OVERNIGHT-LAYA-TRAINING", "OVERNIGHT-LAYA-SWEEP-02"):
                continue
            # Exclude legacy protocol or min_factor runs
            if run_id.endswith("_LEGACY_MINFACTOR") or n.get("protocol_version") == "LEGACY_MINFACTOR" or n.get("legacy_input_protocol"):
                continue
            if n.get("is_pinned_parent") or cid in pinned_map:
                continue
            # Exclude duplicate signatures and uncompleted runs without valid validation
            if n.get("is_duplicate_run_signature"):
                continue
            # Exclude in-flight, unfinished runs that only have temporary epoch metrics
            if n.get("run_status") not in ("completed", "early_stopped"):
                continue
            if not n.get("is_run_best_epoch"):
                continue
            val = n.get("validation", {})
            family = n["task_family"]
            if not _rankable_node(n) or not _finite_metric(n.get("selection_score")):
                continue
            if family == "S2" and n.get("s2_status") != "AUDITED_RANKING":
                continue
            new_eligible_candidates.append(n)

        n_new_eligible = len(new_eligible_candidates)
        new_pool_quota = math.ceil(NEW_CORE_POOL_RATIO * n_new_eligible) if n_new_eligible > 0 else 0

        # Group by comparable group: (protocol_version, task_family/primary_supervision_class)
        by_group = defaultdict(list)
        for n in new_eligible_candidates:
            cid = n["checkpoint_id"]
            gid = decisions.get(cid, {}).get("comparable_group_id") or n.get("comparable_group_id") or "default"
            by_group[gid].append(n)

        # Allocate seats by group size; compare scores only inside each group.
        new_retained_ids = set()
        group_quotas = {gid: new_pool_quota * len(group) // n_new_eligible for gid, group in by_group.items()}
        remainder_order = sorted(by_group, key=lambda gid: (
            -(new_pool_quota * len(by_group[gid]) % n_new_eligible), gid))
        for gid in remainder_order[:new_pool_quota - sum(group_quotas.values())]:
            group_quotas[gid] += 1
        for gid in sorted(by_group):
            g_nodes = by_group[gid]
            sorted_g = sorted(g_nodes, key=lambda n: (
                -n["selection_score"], _node_primary_sort_key(n, n["task_family"]), n["checkpoint_id"]))
            g_quota = group_quotas[gid]
            new_retained_ids.update(n["checkpoint_id"] for n in sorted_g[:g_quota])
            group_summaries[gid].update(new_pool_eligible_runs=len(g_nodes), new_pool_quota=g_quota,
                                        new_pool_total_quota=new_pool_quota,
                                        new_pool_allocation="largest_remainder_by_group_size")

        # Update decisions for new candidates
        for n in nodes:
            cid = n["checkpoint_id"]
            run_id = n.get("run_id", "")
            if cid in OLD_CORE_CHECKPOINT_IDS or n.get("is_pinned_parent") or cid in pinned_map:
                continue
            if run_id in HISTORICAL_PRE_Q012_COMPLETED_RUNS:
                if cid in decisions:
                    dec = decisions[cid]
                    dec["should_retain"] = False
                    dec["is_global_best"] = False
                    dec["is_top_k"] = False
                    dec["retention_pool"] = "HISTORICAL_METADATA_ONLY"
                    dec["rejection_reason"] = "pre_q012_historical_metadata_only"
                continue
            if cid in decisions:
                dec = decisions[cid]
                if cid in new_retained_ids:
                    dec["should_retain"] = True
                    dec["retention_pool"] = "NEW_CORE_POOL"
                    dec["rejection_reason"] = None
                    if "retention_reasons" not in dec or dec["retention_reasons"] is None:
                        dec["retention_reasons"] = []
                    dec["retention_reasons"].append(f"new_core_pool_15pct(quota={new_pool_quota}/{n_new_eligible})")
                else:
                    dec["should_retain"] = False
                    dec["is_global_best"] = False
                    dec["is_top_k"] = False
                    dec["retention_pool"] = "METADATA_ONLY"
                    if not dec.get("rejection_reason"):
                        dec["rejection_reason"] = f"outside_new_core_pool_15pct_quota({new_pool_quota}/{n_new_eligible})"

    return decisions, group_summaries


def resolve_retention_status(
    decision: Dict[str, Any],
    weights_currently_saved: bool,
    was_previously_saved: bool,
    is_legacy: bool,
) -> str:
    """Map policy decision + physical disk state to one of the 8 canonical statuses."""
    if is_legacy and not weights_currently_saved:
        return STATUS_LEGACY_METADATA_ONLY
    if decision.get("is_pinned_parent") and weights_currently_saved:
        return STATUS_PINNED_PARENT
    if decision.get("is_global_best") and weights_currently_saved:
        return STATUS_RETAINED_BEST
    if decision.get("should_retain") and weights_currently_saved:
        return STATUS_RETAINED_TOP_K
    if not decision.get("should_retain"):
        if decision.get("is_duplicate_run_signature") and was_previously_saved and not weights_currently_saved:
            return STATUS_PRUNED_DUPLICATE
        if was_previously_saved and not weights_currently_saved:
            return STATUS_PRUNED_LOW_SCORE
        if weights_currently_saved:
            return STATUS_METADATA_ONLY
        return STATUS_METADATA_ONLY
    return STATUS_METADATA_ONLY
