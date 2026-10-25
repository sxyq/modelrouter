#!/usr/bin/env python3
"""
test_leakage_and_isolation.py - Unit tests for leakage detector and split isolation.
"""

import unittest
import gzip
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from modelrouter.data_pipeline.leakage_checker import LeakageDetector, normalize_prompt, prompt_hash


class TestLeakageAndIsolation(unittest.TestCase):
    def setUp(self):
        self.detector = LeakageDetector()
        self.detector.register_benchmark_tasks(
            task_ids=["terminal_bench_task_01", "adaptive-rejection-sampler"],
            prompts=["Implement an adaptive rejection sampler in R", "Fix bug in memory allocator"],
        )

    def test_exact_task_id_leakage_detected(self):
        has_leak, detail = self.detector.check_leakage("adaptive-rejection-sampler", "unrelated text")
        self.assertTrue(has_leak)
        self.assertIn("Exact task ID match", detail)

    def test_normalized_prompt_leakage_detected(self):
        # Case variation and punctuation
        dirty_prompt = "  IMPLEMENT an ADAPTIVE rejection sampler in R!  "
        has_leak, detail = self.detector.check_leakage("safe_candidate_id", dirty_prompt)
        self.assertTrue(has_leak)
        self.assertIn("Normalized prompt hash match", detail)

    def test_unrelated_task_passes(self):
        has_leak, detail = self.detector.check_leakage("unique_training_task_999", "Optimize SQL index on users")
        self.assertFalse(has_leak)
        self.assertIsNone(detail)


class TestV8TypedIsolation(unittest.TestCase):
    def test_auxiliary_export_preserves_labels_state_split_and_old_material(self):
        from router_data.build_v8_data_extension import export_kev_training

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            saved = root / "saved"
            destination = root / "data/kev/v8_extension"
            destination.mkdir(parents=True)
            for name in ("train.jsonl", "val.jsonl", "materialization.json"):
                (destination / name).write_text("historical material")
            expected_counts = {"train": 3, "val": 3}
            for split in ("train", "val"):
                (saved / split).mkdir(parents=True)
                outcome = {"provenance": {"source_id": "TRA-001", "split": split,
                    "source_file": "trajectories.jsonl", "source_line": 1,
                    "independent_unit_id": split, "trajectory_id": split, "stable_record_id": split},
                    "state": {"pre_decision_state": {"initial_prompt_snippet": "Keep Task", "step_index": 1}},
                    "questions": {"trajectory_resolved": {"type": "noul", "instructions": "old target hint",
                        "criteria": {"false": "Not resolved", "true": "Resolved"}}},
                    "expected": {"trajectory_resolved": False},
                    "_meta": {"target": "observed_failure", "supervision_class": "S2"}}
                unknown = {**outcome, "expected": {"trajectory_resolved": "UNKNOWN"}}
                auxiliary = {"provenance": {"source_id": "CACHE-001", "split": split,
                    "source_file": "cache.jsonl", "source_line": 1,
                    "independent_unit_id": split, "stable_record_id": split},
                    "state": {"pre_decision_state": {"input_length": 2048}},
                    "questions": {"historical_prefix_reuse_tier": {"type": "score", "instructions": "old",
                        "criteria": ["none", "partial", "moderate", "high"]}},
                    "expected": {"historical_prefix_reuse_tier": 2},
                    "_meta": {"target": "prefix_reuse_opportunity", "supervision_class": "S3"}}
                (saved / split / "S2.jsonl").write_text("\n".join(json.dumps(r) for r in (outcome, unknown, outcome)) + "\n")
                same_id_other_line = {**auxiliary,
                    "provenance": {**auxiliary["provenance"], "source_line": 2},
                    "state": {"pre_decision_state": {"input_length": 4096}},
                    "expected": {"historical_prefix_reuse_tier": 1}}
                (saved / split / "S3.jsonl").write_text("\n".join(json.dumps(r) for r in (auxiliary, same_id_other_line)) + "\n")
                (saved / split / "S1.jsonl").write_text("must not read C03 material")
            result = export_kev_training("original-config.json", root, "saved")
            self.assertEqual(result["configuration_source"], "original-config.json")
            self.assertEqual(result["new_train_questions_vs_c03"], 3)
            self.assertEqual(result["model_choice_labels_created"], 0)
            for split, count in expected_counts.items():
                details = result["splits"][split]
                self.assertEqual(details["written_records"], count)
                self.assertEqual(details["excluded_unknown_or_invalid_label"], 1)
                self.assertEqual(details["excluded_repeated_supervision"], 1)
                rows = [json.loads(s) for s in Path(result["data_paths"][split]).read_text().splitlines()]
                self.assertEqual(rows[0]["state"], {"pre_decision_state": {"initial_prompt_snippet": "Keep Task", "step_index": 1}})
                self.assertEqual(rows[0]["questions"]["trajectory_resolved"]["label"], False)
                self.assertEqual(rows[1]["questions"]["historical_prefix_reuse_tier"]["label"], 2)
                self.assertEqual(rows[2]["questions"]["historical_prefix_reuse_tier"]["label"], 1)
                self.assertEqual(details["independent_units_by_class"], {"S2": 1, "S3": 1})
                self.assertTrue(all(row["provenance"]["split"] == split for row in rows))
                self.assertTrue(all("model_choice" not in row["questions"] for row in rows))
                self.assertEqual(sum(details["question_target_counts"].values()), count)
            for name in ("train.jsonl", "val.jsonl", "materialization.json"):
                self.assertEqual((destination / name).read_text(), "historical material")
            self.assertFalse(result["test_used"])

    def test_missing_typed_input_does_not_create_training_material(self):
        from router_data.build_v8_data_extension import export_kev_training

        with tempfile.TemporaryDirectory() as tmp:
            result = export_kev_training("config.json", tmp, "missing")
            self.assertEqual(result["configuration_status"], "PENDING_NO_NEW_TYPED_LABELS")
            self.assertEqual(result["new_train_questions_vs_c03"], 0)
            self.assertFalse((Path(tmp) / "data/kev/v8_extension").exists())

    def test_triplet_loader_uses_real_candidates_and_only_known_outcomes(self):
        from modelrouter.training.v8_real_finetune import load_v8_triplet_data

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            choice = {"candidate_models": ["real-a", "real-b"], "winner_choice": "model_b",
                      "winner_model": "real-b", "prompt_snippet": "original Task"}
            cache = {"estimated_reusable_blocks": 2, "prefix_block_count": 4, "input_length": 4096}
            outcome = {"known_terminal_outcome": "SUCCESS", "observed_model": "executed-a",
                       "state_before": {"prompt_snippet": "real Task", "prior_tool_calls_count": 1}}
            for name, rows in (
                ("router_choice", [choice, {**choice, "winner_choice": "tie"}, {**choice, "winner_model": "wrong"}]),
                ("cache_reuse_opportunity", [cache, {**cache, "prefix_block_count": 0}, {**cache, "estimated_reusable_blocks": 5}]),
                ("observed_agent_outcome", [outcome, {**outcome, "known_terminal_outcome": "UNKNOWN"},
                                           {**outcome, "observed_model": "unknown_model"}]),
            ):
                with gzip.open(root / (name + "_train.jsonl.gz"), "wt") as stream:
                    stream.write("\n".join(json.dumps(r) for r in rows) + "\n")
            result = load_v8_triplet_data(root)
            self.assertEqual(len(result), 3)
            self.assertEqual((result[0]["opt_a"], result[0]["opt_b"], result[0]["label"]),
                             ("Model: real-a", "Model: real-b", 1))
            self.assertEqual(result[1]["ratio"], 0.5)
            self.assertEqual(result[2]["outcome"], 1.0)
            self.assertIn("real Task", result[2]["prompt"])
            self.assertIn("executed-a", result[2]["prompt"])


class TestV8Coverage(unittest.TestCase):
    @staticmethod
    def _row(group, split, number):
        source, target, qid, typ, criteria, label = {
            "S1": ("ROUTE-004", "human_pairwise_preference", "model_choice", "choice", {"a": "", "b": ""}, "a"),
            "S2": ("TRA-001", "observed_success", "trajectory_resolved", "noul", {"false": "No", "true": "Yes"}, True),
            "S3": ("CACHE-001", "prefix_reuse_opportunity", "historical_prefix_reuse_tier", "score", ["none", "low", "high"], 2),
        }[group]
        return {"provenance": {"source_id": source, "split": split, "source_file": source + ".jsonl",
                    "source_line": number, "stable_record_id": "shared-id", "independent_unit_id": f"{split}-{number}"},
                "state": {"pre_decision_state": {"task": f"original {split} task {number}"}},
                "questions": {qid: {"type": typ, "criteria": criteria, "instructions": "old target hint"}},
                "expected": {qid: label}, "_meta": {"supervision_class": group, "target": target}}

    def _inputs(self, root, sizes):
        source = root / "saved"
        for split, groups in sizes.items():
            (source / split).mkdir(parents=True)
            for group, count in groups.items():
                (source / split / (group + ".jsonl")).write_text(
                    "".join(json.dumps(self._row(group, split, n)) + "\n" for n in range(1, count + 1)))
        (source / "test").mkdir()
        (source / "test/S1.jsonl").write_text("must not read")
        return source

    def test_all_16_ratios_select_maximum_without_replacement_and_keep_history(self):
        from router_data.build_v8_data_extension import export_kev_coverage

        sizes = {"train": {"S1": 5, "S2": 3, "S3": 7}, "val": {"S1": 4, "S2": 2, "S3": 6}}
        vectors = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (2, 1, 0), (1, 2, 0),
                   (1, 0, 1), (2, 0, 1), (1, 0, 2), (0, 1, 1), (0, 2, 1), (0, 1, 2),
                   (1, 1, 1), (2, 1, 1), (1, 2, 1), (1, 1, 2)]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._inputs(root, sizes)
            destination = root / "data/kev/v8_extension"
            destination.mkdir(parents=True)
            for name in ("train.jsonl", "val.jsonl", "materialization.json", "train_typed_auxiliary.jsonl"):
                (destination / name).write_text("historical material")
            result = export_kev_coverage("saved", root, configuration_source="original-config.json")
            self.assertEqual(list(result["runs"]), [f"R{n:02}" for n in range(1, 17)])
            self.assertEqual(result["configuration"]["seed"], 42)
            self.assertEqual(result["configuration"]["configuration_source"], "original-config.json")
            self.assertFalse(result["test_used"])
            self.assertEqual(len(result["configuration"]["input_files"]), 6)
            for number, vector in enumerate(vectors, 1):
                ratio = {g: w for g, w in zip(("S1", "S2", "S3"), vector) if w}
                run = result["runs"][f"R{number:02}"]
                self.assertEqual(run["ratio"], ratio)
                self.assertEqual(run["status"], "READY")
                for split in sizes:
                    multiplier = min(sizes[split][g] // w for g, w in ratio.items())
                    expected = {g: multiplier * w for g, w in ratio.items()}
                    summary = run["splits"][split]
                    self.assertEqual(summary["records_by_class"], expected)
                    self.assertEqual(summary["questions_by_class"], expected)
                    self.assertEqual(summary["independent_units_by_class"], expected)
                    rows = [json.loads(line) for line in Path(run["dataPaths"][split]).read_text().splitlines()]
                    identities = {(r["provenance"]["source_file"], r["provenance"]["source_line"]) for r in rows}
                    self.assertEqual(len(identities), sum(expected.values()))
                    self.assertEqual(summary["total_records"], len(rows))
                    self.assertEqual(sum(summary["source_counts"].values()), len(rows))
                    self.assertEqual(sum(summary["target_counts"].values()), len(rows))
                    self.assertEqual(sum(summary["question_target_counts"].values()), len(rows))
                    for row in rows:
                        self.assertEqual(row["provenance"]["split"], split)
                        original = self._row(row["_meta"]["supervision_class"], split, row["provenance"]["source_line"])
                        self.assertEqual(row["state"], original["state"])
                        for qid, q in row["questions"].items():
                            self.assertEqual(q["label"], original["expected"][qid])
                            self.assertNotEqual(q["instructions"], "old target hint")
            for name in ("train.jsonl", "val.jsonl", "materialization.json", "train_typed_auxiliary.jsonl"):
                self.assertEqual((destination / name).read_text(), "historical material")

    def test_same_configuration_reuses_and_changed_seed_does_not_overwrite(self):
        from router_data import build_v8_data_extension as builder

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._inputs(root, {"train": {"S1": 5, "S2": 3, "S3": 7}, "val": {"S1": 4, "S2": 2, "S3": 6}})
            first = builder.export_kev_coverage("saved", root)
            manifest = Path(first["materialization_path"])
            before = manifest.read_text()
            times = {path: Path(path).stat().st_mtime_ns for run in first["runs"].values() for path in run["dataPaths"].values()}
            with patch.object(builder, "_kev_coverage_rows", side_effect=AssertionError("must reuse existing material")):
                second = builder.export_kev_coverage("saved", root)
                self.assertEqual(first, second)
                changed = builder.export_kev_coverage("saved", root, seed=43)
            self.assertEqual(changed["status"], "PENDING")
            self.assertEqual(manifest.read_text(), before)
            self.assertEqual(times, {path: Path(path).stat().st_mtime_ns for path in times})

    def test_illegal_sources_unknown_labels_and_insufficient_ratios_are_recorded(self):
        from router_data.build_v8_data_extension import export_kev_coverage

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self._inputs(root, {"train": {"S1": 1, "S2": 3, "S3": 0}, "val": {"S1": 1, "S2": 2, "S3": 0}})
            illegal = []
            for src in ("ROUTE-001", "ROUTE-002", "TRA-004"):
                row = self._row("S1", "train", 9)
                row["provenance"]["source_id"] = src
                illegal.append(row)
            illegal.append(self._row("S1", "val", 10))
            with (source / "train/S1.jsonl").open("a") as stream:
                stream.write("".join(json.dumps(row) + "\n" for row in illegal))
            unknown = self._row("S3", "train", 1)
            unknown["expected"]["historical_prefix_reuse_tier"] = "UNKNOWN"
            (source / "train/S3.jsonl").write_text(json.dumps(unknown) + "\n")
            result = export_kev_coverage("saved", root)
            self.assertEqual(result["pools"]["train"]["S1"]["legal_records"], 1)
            self.assertEqual(result["pools"]["train"]["S1"]["excluded_split_or_source_target"], 4)
            self.assertEqual(result["pools"]["train"]["S3"]["excluded_unknown_or_invalid_label"], 1)
            self.assertEqual(result["runs"]["R04"]["status"], "READY")
            self.assertEqual(result["runs"]["R05"]["status"], "PENDING")
            self.assertIn("S1", result["runs"]["R05"]["reason"])
            for run_id in ("R03", "R07", "R13", "R16"):
                self.assertEqual(result["runs"][run_id]["status"], "PENDING")
                self.assertIn("S3", result["runs"][run_id]["reason"])
                self.assertFalse(result["runs"][run_id]["dataPaths"])

    def test_preexisting_run_file_is_preserved_without_preventing_other_views(self):
        from router_data.build_v8_data_extension import export_kev_coverage

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._inputs(root, {"train": {"S1": 5, "S2": 3, "S3": 7}, "val": {"S1": 4, "S2": 2, "S3": 6}})
            historical = root / "data/kev/v8_extension/R01/train.jsonl"
            historical.parent.mkdir(parents=True)
            historical.write_text("historical run")
            result = export_kev_coverage("saved", root)
            self.assertEqual(result["runs"]["R01"]["status"], "PENDING")
            self.assertEqual(historical.read_text(), "historical run")
            self.assertEqual(result["runs"]["R02"]["status"], "READY")


if __name__ == "__main__":
    unittest.main()
