#!/usr/bin/env python3
"""
rq4_analysis.py - RQ4 Systematic Ablation Analysis Engine for ModelRouter.

Generates authoritative ablation datasets for:
- Table 5: Action Structure Ablation (Fixed, Model-only, Effort-only, Hierarchical, Joint MxE)
- Table 4: Information State Representation (T, M, H, minus Role, minus KV, minus Verifier)
- Table 8: Supervision View Ablation (S1, S2, S3, combinations)
- Table 11: Checkpoint Comparison (Laya-421M vs Kev-4B)
- Fig. 7: Panels A, B, and C
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("modelrouter.experiments.rq4")

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
CONFIGS_DIR = WORKSPACE_ROOT / "our-project" / "experiments" / "configs"
RESULTS_DIR = WORKSPACE_ROOT / "our-project" / "results" / "benchmarks"


class RQ4AblationAnalyzer:
    """Analyzes action spaces, state information groups, and multi-task supervision views."""

    FLAGSHIP_COST_USD = 0.0540

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (CONFIGS_DIR / "rq4_ablation_matrix.json")
        self.matrix_data: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        if self.config_path.is_file():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.matrix_data = json.load(f)

    def generate_table_5_actions(self) -> List[Dict[str, Any]]:
        """Action Structure Ablation (Table 5)."""
        raw = self.matrix_data.get("action_ablation_table_5", {})
        results = []
        for k, v in raw.items():
            cost = v["mean_cost_usd"]
            savings_pct = round((1.0 - (cost / self.FLAGSHIP_COST_USD)) * 100.0, 2)
            efficiency_score = round(v["pass_at_1"] / max(0.001, cost), 1)
            results.append({
                "action_id": k,
                "name": v["name"],
                "action_type": v["action_type"],
                "pass_at_1": v["pass_at_1"],
                "mean_cost_usd": cost,
                "cost_savings_pct": savings_pct,
                "routing_overhead_ms": v["routing_overhead_ms"],
                "quality_cost_efficiency": efficiency_score,
            })
        return results

    def generate_table_4_information(self) -> List[Dict[str, Any]]:
        """Information Group Ablation (Table 4)."""
        raw = self.matrix_data.get("information_ablation_table_4", {})
        full_pass = raw.get("T_M_H_FULL", {}).get("pass_at_1", 0.702)
        results = []
        for k, v in raw.items():
            pass_val = v["pass_at_1"]
            delta = round(pass_val - full_pass, 3)
            cost = v["mean_cost_usd"]
            results.append({
                "config_id": k,
                "features": v["features"],
                "description": v["description"],
                "pass_at_1": pass_val,
                "delta_vs_full": delta,
                "mean_cost_usd": cost,
            })
        return results

    def generate_table_8_supervision(self) -> List[Dict[str, Any]]:
        """Supervision Views Ablation (Table 8)."""
        raw = self.matrix_data.get("supervision_ablation_table_8_11", {})
        keys = ["S1_ONLY", "S2_ONLY", "S3_ONLY", "S1_PLUS_S2", "S1_PLUS_S3", "S1_S2_S3_FULL"]
        results = []
        for k in keys:
            v = raw.get(k)
            if not v:
                continue
            results.append({
                "config_id": k,
                "views": v["views"],
                "description": v["description"],
                "s1_accuracy": v["s1_accuracy"],
                "pass_at_1": v["pass_at_1"],
                "brier_score": v["brier_score"],
                "mean_cost_usd": v["mean_cost_usd"],
            })
        return results

    def generate_table_11_checkpoints(self) -> List[Dict[str, Any]]:
        """Laya vs Kev Checkpoints Comparison (Table 11)."""
        raw = self.matrix_data.get("supervision_ablation_table_8_11", {})
        results = []
        for k in ["LAYA_421M_CHECKPOINT", "KEV_4B_CHECKPOINT"]:
            v = raw.get(k)
            if not v:
                continue
            results.append({
                "model_id": k,
                "model_name": v["model"],
                "serving_checkpoint": v["serving_checkpoint"],
                "s1_accuracy": v["s1_accuracy"],
                "pass_at_1": v["pass_at_1"],
                "mean_cost_usd": v["mean_cost_usd"],
                "routing_latency_ms": v["routing_latency_ms"],
            })
        return results

    def generate_fig_7_data(self) -> Dict[str, Any]:
        """Generates Fig. 7 data structures (Panels A, B, C)."""
        t5 = self.generate_table_5_actions()
        t4 = self.generate_table_4_information()
        t8 = self.generate_table_8_supervision()

        panel_a = {
            "title": "Panel A: Action Space Formulations vs Fixed Baseline",
            "categories": [x["name"] for x in t5],
            "pass_at_1": [x["pass_at_1"] for x in t5],
            "cost_savings_pct": [x["cost_savings_pct"] for x in t5],
        }

        panel_b = {
            "title": "Panel B: Information State Group Contributions",
            "categories": [x["config_id"] for x in t4],
            "pass_at_1": [x["pass_at_1"] for x in t4],
            "delta_vs_full": [x["delta_vs_full"] for x in t4],
        }

        panel_c = {
            "title": "Panel C: Multi-Task Supervision Synergy",
            "combinations": [x["config_id"] for x in t8],
            "s1_accuracy": [x["s1_accuracy"] for x in t8],
            "pass_at_1": [x["pass_at_1"] for x in t8],
            "brier_score": [x["brier_score"] for x in t8],
        }

        return {
            "figure_title": "Fig. 7: Systematic Ablation of Action Spaces, State Groups, and Supervision Synergy",
            "panel_a_action": panel_a,
            "panel_b_information": panel_b,
            "panel_c_supervision": panel_c,
        }

    def execute_and_save(self) -> Dict[str, Any]:
        table_5 = self.generate_table_5_actions()
        table_4 = self.generate_table_4_information()
        table_8 = self.generate_table_8_supervision()
        table_11 = self.generate_table_11_checkpoints()
        fig_7 = self.generate_fig_7_data()

        payload = {
            "data_origin": "SYNTHETIC_PREFILLED_CONFIG",
            "publication_eligible": False,
            "experiment_id": "RQ4_SYSTEMATIC_ABLATION",
            "table_5_action_ablation": table_5,
            "table_4_information_ablation": table_4,
            "table_8_supervision_ablation": table_8,
            "table_11_checkpoint_comparison": table_11,
            "fig_7_panels": fig_7,
        }

        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = RESULTS_DIR / "rq4_data.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        logger.info(f"RQ4 analysis completed. Output saved to {out_path}")
        return payload


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    analyzer = RQ4AblationAnalyzer()
    res = analyzer.execute_and_save()
    print("\n--- Table 5: Action Ablation ---")
    for r in res["table_5_action_ablation"]:
        print(f"{r['action_id']:25} | Pass@1: {r['pass_at_1']*100:.1f}% | Savings: {r['cost_savings_pct']:.1f}% | Overhead: {r['routing_overhead_ms']:.1f}ms")
    print("\n--- Table 11: Checkpoint Comparison ---")
    for r in res["table_11_checkpoint_comparison"]:
        print(f"{r['model_name']:30} | S1 Acc: {r['s1_accuracy']*100:.1f}% | Pass@1: {r['pass_at_1']*100:.1f}% | Latency: {r['routing_latency_ms']:.1f}ms")
