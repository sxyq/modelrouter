"""TwinRouterBench Evaluation Interface.

Provides:
- Dataset loader for TwinRouterBench 970-item step-level holdout set.
- Mapping between TwinRouterBench capability tiers (low, mid, mid_high, high) and agent model pools.
- Offline evaluation metrics: Accuracy, Normalized Score, Confusion Matrix, and Cost Efficiency.
"""
from __future__ import annotations

import json
import sys
import time
from itertools import chain
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


TIER_MAPPING = {
    "low": 0,
    "mid": 1,
    "mid_high": 2,
    "high": 3,
}

TIER_NAMES = ["low", "mid", "mid_high", "high"]


@dataclass
class TwinRouterRecord:
    instance_id: str
    step_index: int
    state_text: str
    expected_choice: str
    expected_score: int
    raw_data: Dict[str, Any]

    @property
    def key(self) -> str:
        return f"{self.instance_id}_step_{self.step_index}"


def _find_project_root() -> Path:
    p = Path(__file__).resolve()
    while p != p.parent:
        if (p / "external" / "benchmarks" / "twinrouterbench" / "test_twinrouterbench_holdout.jsonl").is_file():
            return p
        p = p.parent
    return Path.cwd()


class TwinRouterBenchEvaluator:
    def __init__(self, data_path: Optional[str | Path] = None):
        if data_path is None:
            data_path = _find_project_root() / "external" / "benchmarks" / "twinrouterbench" / "test_twinrouterbench_holdout.jsonl"
        self.data_path = Path(data_path)
        if not self.data_path.is_file():
            raise FileNotFoundError(f"TwinRouterBench dataset not found at: {self.data_path}")
        self.records: List[TwinRouterRecord] = self._load_records()

    def _load_records(self) -> List[TwinRouterRecord]:
        records = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = json.loads(line)
                prov = d.get("provenance", {})
                expected = d.get("expected", {})
                records.append(
                    TwinRouterRecord(
                        instance_id=prov.get("instance_id", ""),
                        step_index=prov.get("step_index", 0),
                        state_text=d.get("state", ""),
                        expected_choice=expected.get("routing_tier_choice", "low"),
                        expected_score=expected.get("routing_tier_score", 0),
                        raw_data=d,
                    )
                )
        return records

    def __len__(self) -> int:
        return len(self.records)

    def evaluate_policy(
        self,
        predict_fn: Callable[[TwinRouterRecord], str],
        max_samples: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Evaluates a prediction function on the benchmark.
        
        predict_fn takes TwinRouterRecord and returns one of: 'low', 'mid', 'mid_high', 'high'.
        """
        targets = self.records[:max_samples] if max_samples else self.records
        total = len(targets)
        correct = 0
        confusion: Dict[str, Dict[str, int]] = {
            t: {p: 0 for p in TIER_NAMES} for t in TIER_NAMES
        }
        predictions_dist: Dict[str, int] = {t: 0 for t in TIER_NAMES}

        for rec in targets:
            pred = predict_fn(rec)
            if pred not in TIER_NAMES:
                pred = "low"  # default fallback
            predictions_dist[pred] += 1
            exp = rec.expected_choice
            if exp not in TIER_NAMES:
                exp = "low"
            confusion[exp][pred] += 1
            if pred == exp:
                correct += 1

        acc = correct / total if total > 0 else 0.0
        return {
            "total_samples": total,
            "correct": correct,
            "accuracy": round(acc, 4),
            "predictions_distribution": predictions_dist,
            "confusion_matrix": confusion,
        }

    def evaluate_checkpoint(self, checkpoint_dir, model_type, output_dir, *,
                            project_root, threads=8, completed_predictions=()):
        """Score one original checkpoint on the existing four-tier holdout, on CPU."""
        import numpy as np
        import torch

        project_root = Path(project_root).resolve()
        for source in (project_root, project_root / "external/laya", project_root / "external/kev"):
            sys.path.insert(0, str(source))
        from kev.metrics import metrics

        torch.set_num_threads(threads)
        checkpoint_dir, output_dir = Path(checkpoint_dir).resolve(), Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        started = time.perf_counter()
        qid = "routing_tier_choice"
        offset = len(completed_predictions)
        rows = [{"state": rec.state_text,
                 "questions": {qid: {**rec.raw_data["questions"][qid], "src": qid}},
                 "expected": {qid: rec.expected_choice}} for rec in self.records]
        print(f"Loading {model_type}: {checkpoint_dir}", flush=True)
        if model_type == "laya":
            from laya.train import load_checkpoint, items_from_rows, calibration_records

            model, tok, cfg = load_checkpoint(str(checkpoint_dir))
            model.encoder.config.reference_compile = False
            items, skipped = items_from_rows(tok, rows, max_len=1024, head_max_len=512)
            context = {"max_len": 1024, "head_max_len": 512}
            dtype = str(next(model.parameters()).dtype)

            def outputs():
                with torch.inference_mode():
                    for start in range(offset, len(items), 16):
                        records = calibration_records(model, tok, items[start:start + 16],
                                                      torch.device("cpu"), 1024, 512)
                        for _, logits, _, _ in records:
                            yield np.asarray(logits, dtype=float)
        else:
            from kev.checkpoint import LoadOptions
            from kev.data import materialize
            from kev.predictors import LocalPredictor

            context = {"max_state": 1024, "max_branch": 512, "max_packed": 4096}
            predictor = LocalPredictor(str(checkpoint_dir), "cpu",
                                       LoadOptions(temperature=1.0, backend="torch"), context=context)
            dtype = str(next(predictor.model.parameters()).dtype)
            skipped = {}

            def outputs():
                with torch.inference_mode():
                    for start in range(offset, len(rows), 16):
                        encs = [predictor.model.encode(predictor.tok, materialize(row), max_state=1024,
                                                       max_branch=512, strict=True)
                                for row in rows[start:start + 16]]
                        for logits in predictor.model.forward_batch(encs):
                            yield logits[0].float().cpu().numpy().astype(float)

        loaded_sec = time.perf_counter() - started
        print(f"Loaded in {loaded_sec:.2f}s; scoring {len(self.records)} steps", flush=True)
        stream = chain((np.asarray(row["logits"], dtype=float) for row in completed_predictions), outputs())
        scored = []
        with (output_dir / "predictions.jsonl").open("w", encoding="utf-8") as output:
            def predict(rec):
                logits = next(stream)
                probabilities = np.exp(logits - logits.max())
                probabilities /= probabilities.sum()
                label = TIER_MAPPING[rec.expected_choice]
                prediction = TIER_NAMES[int(probabilities.argmax())]
                row = {"id": rec.key, "instance_id": rec.instance_id, "step_index": rec.step_index,
                       "type": "choice", "keys": TIER_NAMES, "label": label,
                       "p": probabilities.tolist(), "logits": logits.tolist(),
                       "predicted_tier": prediction, "expected_tier": rec.expected_choice}
                scored.append(row)
                output.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
                output.flush()
                if len(scored) % 50 == 0:
                    print(f"Scored {len(scored)}/{len(self.records)}", flush=True)
                return prediction

            result = self.evaluate_policy(predict)
        result.update(metrics=metrics(scored), task_count=len({r.instance_id for r in self.records}),
                      tier_accuracy_score_100=100 * result["correct"] / result["total_samples"],
                      score_definition="100 * exact step-level tier accuracy; not Agent task success or a cost score",
                      model_type=model_type, checkpoint=str(checkpoint_dir.relative_to(project_root)),
                      dataset=str(self.data_path.resolve().relative_to(project_root)),
                      execution_mode="REAL_LOCAL_ROUTER_INFERENCE", evaluation_scope="INDEPENDENT_STATIC_FOUR_TIER",
                      device="cpu", threads=threads, dtype=dtype, context=context,
                      native_batch_size=16, reused_prediction_count=offset,
                      duration_scope="CURRENT_PROCESS_SEGMENT" if offset else "COMPLETE_EVALUATION",
                      inference_temperature=1.0, temperature_fitted_on_holdout=False,
                      skipped=skipped, load_sec=loaded_sec, duration_sec=time.perf_counter() - started,
                      generation_api_calls=0, resource_cost_usd=None, train_eligible=False)
        (output_dir / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                                         allow_nan=False), encoding="utf-8")
        print(json.dumps({k: result[k] for k in ("checkpoint", "correct", "total_samples", "metrics")}), flush=True)
        return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-type", required=True, choices=("laya", "kev"))
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--threads", type=int, default=8)
    args = parser.parse_args()
    TwinRouterBenchEvaluator(args.data).evaluate_checkpoint(
        args.checkpoint, args.model_type, args.out, project_root=args.project_root, threads=args.threads)
