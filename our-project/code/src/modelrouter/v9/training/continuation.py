"""Continue at existing queue boundaries, keeping plans in the original ledgers."""

from __future__ import annotations

import copy
import json
import math
import os
import sys
import time
from collections import Counter
from pathlib import Path

from modelrouter.serving.schemas import PreDecisionState


GROUPS = ("S1", "S2", "S3")
LAYA_DONE = {"completed", "early_stopped"}
V9_PROTOCOL = "MODELROUTER_V9_FEATURES_V1"
KEV_COMPLETION_GROUP = "KEV_TYPED_COVERAGE_V1"


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _read(path):
    path = Path(path)
    return json.loads(path.read_text(encoding="utf8")) if path.is_file() else {}


def _path(root, value):
    value = Path(value)
    return value if value.is_absolute() else Path(root) / value


def prepared_metadata(project_root, path=None):
    """Use the existing preparation output; never create another data directory."""
    if path is not None:
        selected = _path(project_root, path).resolve()
        return (selected, _read(selected)) if selected.is_file() else None
    roots = (Path(project_root) / "data/v9/prepared",
             Path(project_root) / "our-project/code/data/v9/prepared")
    for root in roots:
        for name in ("index.json", "summary.json"):
            selected = root / name
            if selected.is_file():
                return selected, _read(selected)
    return None


def serialize_training_record(row):
    """Share serving's serializer and keep question/card candidate order intact."""
    result = copy.deepcopy(row)
    state = result.get("pre_decision_state")
    if state is None:
        state = result["state"]
        if isinstance(state, str):
            state = json.loads(state)
        state = state.get("pre_decision_state", state)
    state = dict(state)
    for name in ("teacher_assessment", "capability_cards", "capability_snapshot_id",
                 "feature_training_status", "agent_context", "continuity"):
        if name in result and (name not in state or state[name] is None or state[name] == []):
            state[name] = result[name]
    decision = PreDecisionState.model_validate(state)
    teacher = decision.teacher_assessment
    if teacher and teacher.get("assessed_through_step") is not None:
        step = decision.step_index
        if step is not None and teacher["assessed_through_step"] > step:
            raise ValueError("Teacher assessment includes a later decision")
    result["state"] = decision.router_text()
    result["pre_decision_state"] = decision.model_dump()
    for qid, question in result["questions"].items():
        if "label" not in question:
            question["label"] = result["expected"][qid]
        elif qid in result.get("expected", {}) and question["label"] != result["expected"][qid]:
            raise ValueError("Prepared target and question label differ")
    return result


def training_paths(metadata, metadata_path):
    root = _trainer_root(metadata, metadata_path)
    views = metadata.get("trainer_views", {}).get("train", {})
    return {group: _path(root, views.get(group, f"train/{group}.jsonl"))
            for group in GROUPS
            if group in views or (root / "train" / f"{group}.jsonl").is_file()}


def _trainer_root(metadata, metadata_path):
    return _path(Path(metadata_path).parent, metadata.get("trainer_root", ".")).resolve()


def _material(metadata_path, metadata):
    paths = training_paths(metadata, metadata_path)
    missing = [str(path) for path in paths.values() if not path.is_file()]
    counts, teachers, snapshots = Counter(), Counter(), Counter()
    references = []
    if not missing:
        for group, path in paths.items():
            with path.open(encoding="utf8") as stream:
                for line in stream:
                    if not line.strip():
                        continue
                    row = serialize_training_record(json.loads(line))
                    counts[group] += 1
                    state = row["pre_decision_state"]
                    teacher = state.get("teacher_assessment") or {}
                    if any(teacher.get(key) for key in ("progress_summary", "main_blocker", "next_milestone")):
                        if teacher.get("teacher_model_id"):
                            teachers[teacher["teacher_model_id"]] += 1
                        for ref in teacher.get("reference_ids", []):
                            if ref not in references:
                                references.append(ref)
                    if state.get("capability_snapshot_id"):
                        snapshots[state["capability_snapshot_id"]] += 1
    reason = ("missing_prepared_training_views" if not paths or missing else
              "empty_prepared_training_views" if not sum(counts.values()) else None)
    identity = {
        "prepared_metadata": str(Path(metadata_path).resolve()),
        "dataset_revision": metadata.get("dataset_revision"),
        "teacher_dataset_revision": metadata.get("teacher_dataset_revision"),
        "source_records": dict(counts), "teacher_data_status": metadata.get("teacher_data_status"),
        "teacher_model_id": next(iter(teachers)) if len(teachers) == 1 else None,
        "teacher_model_ids": dict(teachers), "teacher_reference_ids": references,
        "capability_snapshot_id": next(iter(snapshots)) if len(snapshots) == 1 else None,
        "capability_snapshot_ids": dict(snapshots),
    }
    return paths, identity, reason


def _input_feature_values(text):
    values = {}
    for name in ("teacher_assessment", "capability_cards"):
        marker = json.dumps(name) + ":"
        start = text.find(marker)
        if start < 0:
            continue
        try:
            value, _ = json.JSONDecoder().raw_decode(text[start + len(marker):].lstrip())
        except ValueError:
            continue
        if (name == "teacher_assessment" and isinstance(value, dict)
                and any(value.get(key) for key in ("progress_summary", "main_blocker", "next_milestone"))
                or name == "capability_cards" and isinstance(value, list) and value):
            values[name] = value
    return values


class InputExposure:
    """Ephemeral counts from the inputs the original Trainer actually encodes."""

    def __init__(self):
        self.material = {}
        self.source_text = {}
        self.used = set()
        self.full_state_records = set()
        self.partial_state_records = set()
        self.retained = {name: set() for name in ("teacher_assessment", "capability_cards")}
        self.counts = Counter()

    def add(self, key, text):
        self.material[key] = _input_feature_values(text)
        self.source_text[key] = text

    def observe(self, key, text):
        self.used.add(key)
        self.counts["input_passes"] += 1
        full = text == self.source_text[key]
        (self.full_state_records if full else self.partial_state_records).add(key)
        self.counts["full_state_input_passes" if full else "partial_state_input_passes"] += 1
        actual = _input_feature_values(text)
        for name, expected in self.material[key].items():
            short = "teacher" if name == "teacher_assessment" else "capability"
            if actual.get(name) == expected:
                self.retained[name].add(key)
                self.counts[short + "_input_passes_retained"] += 1
            else:
                self.counts[short + "_input_passes_incomplete"] += 1

    def summary(self):
        value = {"source_records": len(self.material), "records_used": len(self.used),
                 "source_records_not_used": len(self.material) - len(self.used),
                 "full_state_records_retained": len(self.full_state_records - self.partial_state_records),
                 "partial_state_records_retained": len(self.partial_state_records), **self.counts}
        value.setdefault("full_state_input_passes", 0)
        value.setdefault("partial_state_input_passes", 0)
        for name, retained in self.retained.items():
            short = "teacher" if name == "teacher_assessment" else "capability"
            value[short + "_source_records"] = sum(name in fields for fields in self.material.values())
            value[short + "_records_retained"] = len(retained)
            for suffix in ("_input_passes_retained", "_input_passes_incomplete"):
                value.setdefault(short + suffix, 0)
        value.setdefault("input_passes", 0)
        return value


def feature_training_status(exposure, complete=False):
    used = sum(exposure.get(name + "_input_passes_retained", 0) for name in ("teacher", "capability"))
    if not used:
        return "FEATURE_NOT_TRAINED"
    total = exposure.get("source_records", 0)
    full = (complete and total > 0 and exposure.get("records_used") == total
            and not exposure.get("partial_state_input_passes")
            and all(exposure.get(name + "_records_retained") == total
                    and not exposure.get(name + "_input_passes_incomplete") for name in ("teacher", "capability")))
    return "FEATURE_TRAINED" if full else "FEATURE_PARTIALLY_TRAINED"


def _finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def _laya_validation_complete(run, validation, fixed_counts):
    declared = run.get("val_groups") or {}
    groups = (list(declared) or run.get("supervision_classes") or list(run.get("train_groups") or {})
              or [group for group in GROUPS if group in validation])
    if not groups or any(group not in fixed_counts for group in groups):
        return False
    if any(count != fixed_counts.get(group) for group, count in declared.items()):
        return False
    return all(fixed_counts[group] > 0
               and validation.get(group, {}).get("items") == fixed_counts[group]
               and all(_finite(validation[group].get(key)) for key in ("loss", "accuracy", "brier", "ece"))
               for group in groups)


def _laya_val_complete(run, fixed_counts):
    if run.get("status") not in LAYA_DONE or (run.get("audit_flags") or {}).get("test_used") is True:
        return False
    history = run.get("history") or []
    # A finite Val does not clear an observed non-finite training run (F14/F04).
    # Keep its results, but do not promote its weights as a V9 parent.
    train_losses = [run.get("train_loss"), *(entry.get("train_loss") for entry in history)]
    if any(loss is not None and not _finite(loss) for loss in train_losses):
        return False
    validation = (history[-1].get("validation") if history else run.get("validation")) or {}
    if (run.get("status") == "completed" and run.get("epochs_max")
            and (not history or history[-1].get("epoch", 0) < run["epochs_max"])):
        return False
    return _laya_validation_complete(run, validation, fixed_counts)


def _laya_fixed_paths(out_root):
    full = _read(Path(out_root) / "full_coverage_manifest.json")
    return {group: _path(out_root, full.get("fixed_validation", {}).get(group, f"val/{group}.jsonl"))
            for group in GROUPS}


def _laya_fixed_counts(out_root):
    fixed_counts = {}
    for group, path in _laya_fixed_paths(out_root).items():
        if path.is_file():
            with path.open(encoding="utf8") as stream:
                fixed_counts[group] = sum(bool(line.strip()) for line in stream)
    return fixed_counts


def select_laya_parent(out_root, queue_state, fixed_counts, parent_group=None):
    from router_data.checkpoint_retention import (
        _node_primary_sort_key, has_physical_weights, is_loadable_checkpoint_path,
        select_run_best_epoch,
    )
    out_root = Path(out_root)
    manifest = _read(out_root / "checkpoint_manifest.json")
    eligible = []
    for node in manifest.get("checkpoints", []):
        if node["run_id"] not in queue_state.get("completed_runs", []):
            continue
        path = _path(out_root, node["path"]).resolve()
        run = _read(out_root / node["run_id"] / "run.json")
        validation = node.get("validation") or {}
        config = _read(path / "rl_agent_config.json")
        origin = config.get("training_run") or {}
        complete_history = [entry for entry in run.get("history", [])
                            if _laya_validation_complete(run, entry.get("validation") or {}, fixed_counts)]
        epoch_result = next((entry.get("validation") or {} for entry in run.get("history", [])
                             if entry.get("epoch") == node.get("epoch")), {})
        if (node.get("run_status") in LAYA_DONE and node.get("comparable_group_id")
                and _finite(node.get("primary_score")) and node.get("loadable")
                and has_physical_weights(path) and is_loadable_checkpoint_path(path)
                and _laya_val_complete(run, fixed_counts)
                and _laya_validation_complete(run, validation, fixed_counts)
                and "S1" in fixed_counts and validation.get("S1", {}).get("items") == fixed_counts["S1"]
                and all(_finite(validation["S1"].get(key)) for key in ("loss", "accuracy", "brier", "ece"))
                and all(validation.get(group) == epoch_result.get(group) for group in GROUPS)
                and origin.get("run_id") == node["run_id"] and origin.get("epoch") == node.get("epoch")
                and config.get("encoder") and config.get("head_layers") is not None
                and node.get("epoch") == select_run_best_epoch(
                    {**run, "history": complete_history}, manifest.get("baseline_0"),
                    bool(queue_state.get("s2_audit_passed")))):
            eligible.append((node, path, run))
    if parent_group is None:
        completed_order = queue_state.get("completed_runs", [])
        for run_id in reversed(completed_order):
            group = next((node["comparable_group_id"] for node, _, _ in eligible
                          if node["run_id"] == run_id), None)
            if group is not None:
                parent_group = group
                break
    same_group = [item for item in eligible if item[0]["comparable_group_id"] == parent_group]
    if not same_group:
        return None
    completed_order = queue_state.get("completed_runs", [])
    anchor = max(same_group, key=lambda item: completed_order.index(item[0]["run_id"]))
    architecture = _read(anchor[1] / "rl_agent_config.json")
    fields = ("encoder", "head_layers", "max_prefixes")
    same_group = [item for item in same_group if all(
        _read(item[1] / "rl_agent_config.json").get(key) == architecture.get(key) for key in fields)]
    return min(same_group, key=lambda item: (
        -item[0]["primary_score"], _node_primary_sort_key(item[0], "S1"),
        item[0]["checkpoint_id"])) if same_group else None


def continue_laya(*, project_root, out_root, completed_run_id, queue_state=None, prepared_path=None,
                  epochs=2, active_budget_gib=120.0, trainer=None, resource_reader=None):
    """One original child calls this after its own saved two-epoch fixed-Val result."""
    from router_data import run_full_graded_queue as queue_module
    from modelrouter.training.kev_candidate_dispatcher import is_pid_alive
    from router_data.checkpoint_retention import has_physical_weights, is_loadable_checkpoint_path
    out_root = Path(out_root).resolve()
    boundary = _read(out_root / completed_run_id / "run.json")
    owner_path, record = out_root / completed_run_id / "run.json", None
    for path in sorted(out_root.glob("*/run.json")):
        run = _read(path)
        value = run.get("v9_continuation")
        if isinstance(value, dict) and value.get("boundary_run_id") == run.get("run_id"):
            owner_path, record = path, value
            break
    if record is not None:
        if record.get("status") == "COMPLETED":
            return record
        if record.get("status") == "RUNNING" and record.get("worker_pid") and is_pid_alive(record["worker_pid"]):
            return record
    prepared = prepared_metadata(project_root, prepared_path)
    if prepared is None:
        return None
    metadata_path, metadata = prepared
    if record is None:
        ordinal = 1
        while (out_root / f"V9_LAYA_{ordinal:03d}").exists():
            ordinal += 1
        record = {"run_id": f"V9_LAYA_{ordinal:03d}", "boundary_run_id": completed_run_id,
                  "created_at": _now(), "training_kind": "NOT_SELECTED",
                  "feature_training_status": "FEATURE_NOT_TRAINED"}

    def persist():
        queue_module._write_json(owner_path, {**_read(owner_path), "v9_continuation": record})

    fixed_counts = _laya_fixed_counts(out_root)

    def finish(result):
        completed = _laya_val_complete(result, fixed_counts)
        output_path = (out_root / record["run_id"] / "checkpoints/best").resolve()
        physical = has_physical_weights(output_path) and is_loadable_checkpoint_path(output_path)
        exposure = result.get("v9_continuation", {}).get("input_exposure", {})
        record.update(status="COMPLETED" if completed and physical else
                      "CHECKPOINT_PENDING" if completed else "VALIDATION_PENDING",
                      training_status=result.get("status"), finished_at=_now(),
                      checkpoint_path=str(output_path.resolve()) if physical else None,
                      pending_reason="v9_fixed_val_incomplete" if not completed else
                      None if physical else "v9_saved_checkpoint_not_available",
                      input_exposure=exposure, feature_training_status=feature_training_status(exposure, completed))
        result_path = out_root / record["run_id"] / "run.json"
        if result_path.is_file():
            saved = _read(result_path)
            saved.setdefault("v9_continuation", {}).update(record)
            queue_module._write_json(result_path, saved)
        persist()
        return record

    existing = _read(out_root / record["run_id"] / "run.json")
    if existing.get("status") in LAYA_DONE:
        return finish(existing)
    last_epoch = (boundary.get("history") or [{}])[-1].get("epoch", 0)
    record.update(status="TRAINING_PENDING", updated_at=_now(),
                  latest_boundary_run_id=completed_run_id, pending_reason=None)
    if not _laya_val_complete(boundary, fixed_counts) or last_epoch < 2:
        record["pending_reason"] = "original_child_two_epochs_or_fixed_val_incomplete"
        persist()
        return record
    record["original_boundary"] = {"run_id": completed_run_id, "epochs_completed": last_epoch,
                                   "finished_at": boundary.get("finished_at"), "fixed_val_counts": fixed_counts}
    try:
        paths, identity, material_reason = _material(metadata_path, metadata)
    except (ValueError, KeyError, OSError) as exc:
        record.update(status="FAILED", pending_reason="prepared_training_data_invalid",
                      error_type=type(exc).__name__, error=str(exc))
        persist()
        return record
    record.update(data_identity=identity, pending_reason=material_reason,
                  training_paths={group: str(path) for group, path in paths.items()})
    state = copy.deepcopy(queue_state if queue_state is not None else _read(out_root / "queue_state.json"))
    if completed_run_id not in state.setdefault("completed_runs", []):
        state["completed_runs"].append(completed_run_id)
    settings = metadata.get("training", {}).get("laya", {})
    parent = select_laya_parent(out_root, state, fixed_counts, settings.get("parent_group"))
    if parent is not None:
        node, parent_path, parent_run = parent
        record.update(parent_checkpoint_id=node["checkpoint_id"], parent_model_dir=str(parent_path),
                      parent_comparable_group_id=node["comparable_group_id"],
                      parent_selection_score=node["primary_score"],
                      parent_selection_basis="FIXED_VAL_INTERNAL_ONLY",
                      training_kind="HEAD_ONLY" if parent_run.get("config", {}).get("freeze_encoder") else "ENCODER_AND_HEAD")
    elif not record["pending_reason"]:
        record["pending_reason"] = "no_loadable_parent_in_original_scoring_group"
    if not record["pending_reason"] and any(group not in fixed_counts for group in paths):
        record["pending_reason"] = "original_fixed_val_files_not_available"
    persist()
    if record["pending_reason"]:
        return record
    run_id = record["run_id"]
    import gc
    gc.collect()
    if "torch" in sys.modules:
        sys.modules["torch"].cuda.empty_cache()
    available, resource = (resource_reader or queue_module.check_gpu_available)()
    record["gpu_resource"] = resource
    if not available:
        record.update(status="WAITING_FOR_GPU", pending_reason="existing_gpu_resource_wait")
        persist()
        return record
    config = parent_run.get("config") or {}
    parent_config = _read(parent_path / "rl_agent_config.json")
    parameters = {"epochs": int(settings.get("epochs", epochs)),
                  "max_len": int(settings.get("max_len", parent_run.get("max_len") or parent_config.get("max_len") or 1024)),
                  "head_max_len": int(settings.get("head_max_len", parent_run.get("head_max_len") or parent_config.get("head_max_len") or 512))}
    record.update(training_parameters=parameters,
                  encoder_context_limit=_read(parent_path / "encoder/config.json").get("max_position_embeddings"))
    spec = {"run_id": run_id, "data": ".", "groups": list(paths),
            "supervision_classes": list(paths), "parent_checkpoint_id": node["checkpoint_id"],
            "parent_model_dir": str(parent_path), "train_origin": "V9_FEATURE_CONTINUATION",
            "protocol_version": V9_PROTOCOL, "v9_continuation": copy.deepcopy(record),
            "encoder_lr": config.get("encoder_lr", 2.5e-5),
            "head_lr": config.get("head_lr", 1e-4),
            "freeze_encoder": config.get("freeze_encoder", False),
            "seed": parent_run.get("seed", 42)}
    manifest = _read(out_root / "experiment_matrix.json") or _read(out_root / "full_coverage_manifest.json")
    manifest.setdefault("plans", {}).update(_read(out_root / "full_coverage_manifest.json").get("plans", {}))
    manifest["plans"][run_id] = spec
    trainer_root = _trainer_root(metadata, metadata_path)
    fixed_paths = _laya_fixed_paths(out_root)
    try:
        record.pop("error_type", None)
        record.pop("error", None)
        record.update(status="RUNNING", started_at=_now(), pending_reason=None, worker_pid=os.getpid())
        spec["v9_continuation"] = copy.deepcopy(record)
        persist()
        if trainer is None:
            laya_source = str(Path(project_root) / "external/laya")
            if laya_source not in sys.path:
                sys.path.insert(0, laya_source)
            from router_data.laya_batch_train import run_sweep_experiment
            trainer = run_sweep_experiment
        result = trainer(run_id, manifest, str(parent_path), str(out_root), data_root=str(trainer_root),
                         validation_root=str(out_root), record_transform=serialize_training_record,
                         training_paths={group: str(path) for group, path in paths.items()},
                         validation_paths={group: str(fixed_paths[group]) for group in paths},
                         **parameters,
                         active_budget_bytes=int(active_budget_gib * queue_module.GIB),
                         s2_audit_passed=bool(state.get("s2_audit_passed", False)))
        return finish(result)
    except Exception as exc:
        failed = _read(out_root / run_id / "run.json")
        exposure = failed.get("v9_continuation", {}).get("input_exposure", {})
        record.update(status="FAILED", error_type=type(exc).__name__, error=str(exc), finished_at=_now(),
                      input_exposure=exposure, feature_training_status=feature_training_status(exposure))
    persist()
    return record


def _kev_group(candidate):
    from router_data.checkpoint_retention import KEV_RESEARCH_GROUPS
    return candidate.get("retention_group") or KEV_RESEARCH_GROUPS.get(candidate["candidate_id"])


def _kev_completed_result(candidate, project_root):
    from router_data.checkpoint_retention import _kev_val_issue
    if (candidate.get("status") != "COMPLETED" or candidate.get("training_status") != "COMPLETED"
            or candidate.get("training_exit_code", 0) != 0
            or candidate.get("evaluation_status", "EVALUATED") != "EVALUATED"):
        return None
    path = _path(project_root, candidate["checkpoint_path"])
    metrics = candidate.get("metrics") or {}
    saved = _read(path / "val_metrics.json")
    if _kev_val_issue(metrics) or saved != metrics:
        return None
    report_path = metrics.get("report_path")
    report = _read(_path(project_root, report_path)) if report_path else {}
    if (not report or report.get("clean") != metrics["clean"] or report.get("coverage") != metrics["coverage"]
            or _path(project_root, report.get("run", ".")).resolve() != path.resolve()
            or _path(project_root, report.get("data", ".")).resolve() != _path(project_root, metrics["validation_set"]).resolve()
            or not _path(project_root, metrics["validation_set"]).is_file()):
        return None
    return metrics


def select_kev_parent(queue, project_root, parent_group=None):
    from modelrouter.training.kev_candidate_dispatcher import check_checkpoint_integrity
    from router_data.checkpoint_retention import compute_kev_selection_score
    reference = next((_kev_completed_result(c, project_root) for c in queue
                      if c["candidate_id"] == "KEV-V8-C03"), None) or {}
    eligible = []
    for candidate in queue:
        if candidate.get("v9_continuation") or candidate.get("candidate_kind") == "SELECTION":
            continue
        path = _path(project_root, candidate["checkpoint_path"])
        args = _read(path / "training_config.json").get("args") or candidate.get("training_parameters") or {}
        metrics = _kev_completed_result(candidate, project_root)
        score = compute_kev_selection_score(metrics or {}, reference)
        adapter = _read(path / "adapter_config.json")
        if (score.get("score") is not None and _kev_group(candidate)
                and args.get("full_ft") == 0 and args.get("base") and args.get("lora")
                and adapter.get("r") == args["lora"] and adapter.get("base_model_name_or_path") == args["base"]
                and check_checkpoint_integrity(path)[0]):
            eligible.append((candidate, path, args, score))
    if parent_group is None and eligible:
        parent_group = _kev_group(eligible[-1][0])
    same_group = [item for item in eligible if _kev_group(item[0]) == parent_group]
    if not same_group:
        return None
    architecture = {key: same_group[-1][2].get(key) for key in
                    ("base", "lora", "lora_targets", "head_dim", "option_isolation", "special_embeddings")}
    same_group = [item for item in same_group if all(item[2].get(key) == value
                                                   for key, value in architecture.items())]
    return min(same_group, key=lambda item: (-item[3]["score"], item[0]["metrics"]["clean"]["nll"],
               -item[0]["metrics"]["clean"]["acc"], item[0]["metrics"]["clean"]["brier"],
               item[0]["metrics"]["clean"]["ece"], item[0]["candidate_id"]))


def plan_kev_continuation(queue, *, project_root, persist, prepared_path=None, completion_group=None):
    """Add one V9 candidate to the existing dispatcher; it launches the official Trainer."""
    from router_data.checkpoint_retention import compute_kev_selection_score
    candidate = next((item for item in queue if item.get("v9_continuation")), None)
    if candidate is not None:
        record = candidate["v9_continuation"]
        if _kev_completed_result(candidate, project_root):
            record["status"] = "COMPLETED"
            return record
        from modelrouter.training.kev_candidate_dispatcher import is_pid_alive
        if candidate.get("pid") and is_pid_alive(candidate["pid"]):
            record["status"] = "RUNNING"
            return record
        if candidate.get("training_status") == "COMPLETED":
            record["status"] = "VALIDATION_PENDING"
            return record
    prepared = prepared_metadata(project_root, prepared_path)
    if prepared is None:
        return None
    metadata_path, metadata = prepared
    paths, identity, material_reason = _material(metadata_path, metadata)
    candidate = next((item for item in queue if item.get("v9_continuation")), None)
    if candidate is not None:
        candidate["v9_continuation"]["data_identity"] = identity
    if candidate is None:
        ordinal = sum(bool(c.get("v9_continuation")) for c in queue) + 1
        while _path(project_root, f"runs/KEV-V9-{ordinal:03d}").exists():
            ordinal += 1
        name = f"KEV-V9-{ordinal:03d}"
        candidate = {"candidate_id": name, "name": name, "status": "PENDING",
                     "training_status": "NOT_STARTED", "evaluation_status": "NOT_EVALUATED",
                     "checkpoint_path": f"runs/{name}/checkpoint", "data_path": str(metadata_path),
                     "init_from": "", "training_kind": "FORMAL_LORA", "retention_group": V9_PROTOCOL,
                     "v9_continuation": {"data_identity": identity, "created_at": _now(),
                                          "feature_training_status": "FEATURE_NOT_TRAINED"}}
        queue.append(candidate)
    record = candidate["v9_continuation"]
    originals = [c for c in queue if not c.get("v9_continuation") and c.get("candidate_kind") != "SELECTION"]
    settings = metadata.get("training", {}).get("kev", {})
    completion_group = (completion_group or record.get("original_completion_group")
                        or settings.get("completion_group"))
    boundary = [c for c in originals if not completion_group or _kev_group(c) == completion_group]
    expected = [c["candidate_id"] for c in boundary]
    matrix_reason = None
    if completion_group == KEV_COMPLETION_GROUP:
        original_plan = _read(Path(project_root) / "data/kev/v8_extension/materialization_coverage.json")
        expected = ["KEV-V8-" + rid for rid, run in original_plan.get("runs", {}).items()
                    if run.get("status") == "READY"]
        if not expected:
            matrix_reason = "original_matrix_plan_not_recorded"
    reference = next((_kev_completed_result(c, project_root) for c in originals
                      if c["candidate_id"] == "KEV-V8-C03"), None) or {}
    pending = [cid for cid in expected if not any(c["candidate_id"] == cid for c in boundary)]
    pending.extend(c["candidate_id"] for c in boundary
                   if compute_kev_selection_score(_kev_completed_result(c, project_root) or {}, reference).get("score") is None)
    reason = matrix_reason or ("original_training_or_fixed_val_pending" if pending or not boundary else material_reason)
    record.update(status="TRAINING_PENDING", original_pending_runs=pending,
                  original_completion_group=completion_group, original_boundary_ids=expected,
                  training_paths={group: str(path) for group, path in paths.items()},
                  pending_reason=reason, updated_at=_now(), candidate_id=candidate["candidate_id"])
    parent = select_kev_parent(originals, project_root, settings.get("parent_group") or completion_group)
    if parent is None:
        reason = reason or "no_loadable_parent_in_original_scoring_group"
    else:
        selected, parent_path, args, score = parent
        record.update(parent_candidate_id=selected["candidate_id"], parent_model_dir=str(parent_path),
                      parent_comparable_group_id=_kev_group(selected), parent_selection_score=score["score"],
                      parent_selection_basis="FIXED_VAL_FOUR_METRIC_INTERNAL_ONLY")
        parameters = {**args, "data": str(metadata_path), "init_from": str(parent_path),
                      "out": str(_path(project_root, candidate["checkpoint_path"])),
                      "epochs": int(settings.get("epochs", 2)),
                      "max_state": int(settings.get("max_state", 8192))}
        record["parent_training_parameters"] = {key: args[key] for key in ("epochs", "max_state", "batch", "accum")}
        candidate.update(init_from=str(parent_path), training_parameters=parameters,
                         lr=str(args["lr"]), lora=str(args["lora"]), epochs=str(parameters["epochs"]),
                         batch=str(args["batch"]), accum=str(args["accum"]), seed=args["seed"],
                         coverage_analysis={"prepared_metadata": str(metadata_path), "data_identity": identity,
                                            "training_paths": record["training_paths"], "counts": metadata.get("counts", {})})
        if selected.get("question_loss_weights"):
            candidate["question_loss_weights"] = copy.deepcopy(selected["question_loss_weights"])
    record["pending_reason"] = reason
    candidate.update(status="PENDING" if reason else "QUEUED", material_status="PENDING" if reason else "READY")
    if reason:
        candidate["pending_reason"] = reason
    else:
        candidate.pop("pending_reason", None)
        candidate.pop("failure_reason", None)
        candidate["training_status"] = "NOT_STARTED"
        record["status"] = "QUEUED"
    persist(queue)
    return record


def reserve_kev_attempt(candidate, command):
    """Use the original worker/result evidence; failed attempts can be tried normally."""
    from modelrouter.training.kev_candidate_dispatcher import is_pid_alive
    record = candidate["v9_continuation"]
    if candidate.get("training_status") == "COMPLETED" or candidate.get("status") == "COMPLETED":
        return None
    if candidate.get("pid") and is_pid_alive(candidate["pid"]):
        candidate.update(status="RUNNING", training_status="RUNNING")
        record["status"] = "RUNNING"
        return None
    attempts = candidate.setdefault("training_attempts", [])
    out_path = Path(candidate["training_parameters"]["out"])
    if attempts and attempts[-1]["status"] == "FAILED" and out_path.exists():
        failed_out = out_path.with_name(f"failed_attempt_{len(attempts):04d}")
        out_path.rename(failed_out)
        attempts[-1]["preserved_output_path"] = str(failed_out)
    attempt = {"command": command, "started_at": _now(), "status": "LAUNCH_REQUESTED"}
    attempts.append(attempt)
    record.update(status="LAUNCH_REQUESTED")
    return attempt
