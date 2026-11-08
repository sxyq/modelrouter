"""Existing Kev selection and physical retention cases."""
import copy
import json
from pathlib import Path

from router_data.checkpoint_retention import (
    OLD_CORE_CHECKPOINT_IDS,
    compute_kev_selection_score, evaluate_kev_retention,
)


def _kev_candidate(root, number, **updates):
    cid = f"KEV-V8-C{number:02d}"
    name = f"KEV-RUN-{number:02d}"
    checkpoint = f"runs/{name}/checkpoint"
    metrics = {"evaluation_status": "EVALUATED", "exit_code": 0,
               "validation_protocol": "KEV_FIXED_VAL_JSONL", "dataset_split": "val", "test_used": False,
               "validation_set": "data/kev/公开数据/val.jsonl", "report_path": checkpoint + "/report.json",
               "evaluated_at": "2026-10-25T00:00:00Z",
               "clean": {"n": 9330, "nll": 1.0, "acc": .6, "brier": .5, "ece": .05},
               "coverage": {"requested_records": 8436, "evaluated_records": 8436,
                            "requested_questions": 9330, "evaluated_questions": 9330,
                            "rejected_records": 0, "truncated_records": 0}}
    candidate = {"candidate_id": cid, "name": name, "checkpoint_path": checkpoint,
                 "status": "COMPLETED", "training_status": "COMPLETED", "evaluation_status": "EVALUATED",
                 "init_from": "models/kev-4b-adapter", "data_path": "data/kev/公开数据/train.jsonl",
                 "metrics": metrics, "loss": .8, "finished_at": "2026-10-25T00:00:00Z",
                 "training_parameters": {"lr": 2e-5, "lora": 16, "epochs": 1, "batch": 1, "accum": 4,
                                         "seed": 42, "dtype": "bf16", "head_lr": 0, "weight_decay": .01,
                                         "lora_targets": "all", "max_state": 384},
                 "training_metrics": {"optimizer_steps": 16857, "records_seen": 67428,
                                      "requested_records": 67428, "wall_seconds": 100}}
    candidate["recipe"] = {"run_id": name, "candidate_id": cid, "source_git_sha": "recorded-project-revision",
                           "upstream_git_sha": "recorded-kev-revision", "base_model": "models/base",
                           "base_revision": "recorded-model-revision", "init_from": candidate["init_from"],
                           "parent_init_source": {"revision": "recorded-parent-revision"},
                           "data_path": candidate["data_path"], "data_identity": {"version": "fixed-project-data"},
                           "validation_set": metrics["validation_set"], "test_used": False,
                           "command": ["python", "-m", "kev.train"], "checkpoint_path": checkpoint,
                           "retraining": "Use the recorded initialization, data and parameters"}
    directory = root / checkpoint
    directory.mkdir(parents=True)
    (directory / "head.pt").write_bytes(b"pointer-weights")
    (directory / "adapter_model.safetensors").write_bytes(b"adapter-weights")
    (directory / "training_config.json").write_text(json.dumps(candidate["training_parameters"]))
    (directory / "train.log").write_text("recorded loss .8")
    candidate.update(updates)
    return candidate


def _kev_queue(root):
    queue = [_kev_candidate(root, n) for n in (3, 4, 10, 20, 21, 22, 23, 24)]
    for c in queue[3:]:
        c["retention_group"] = "HOMOLOGOUS_CONTINUATION"
        c["metrics"]["clean"].update(nll=1.2 + int(c["candidate_id"][-2:]) / 100,
                                      acc=.55, brier=.6, ece=.08)
    return queue


def test_kev_selection_formula_directions_and_reference_scales(tmp_path):
    reference = _kev_candidate(tmp_path, 3)["metrics"]
    result = compute_kev_selection_score(reference, reference)
    assert result["score"] == 100 and result["version"] == "KEV_FIXED_VAL_FOUR_METRIC_V1"
    assert result["weights"] == {"nll": .45, "acc": .30, "brier": .15, "ece": .10}
    for metric, delta in (("nll", -.1), ("acc", .1), ("brier", -.1), ("ece", -.01)):
        improved = copy.deepcopy(reference)
        improved["clean"][metric] += delta
        score = compute_kev_selection_score(improved, reference)
        assert score["score"] > 100
        expected = 100 * (1 + result["weights"][metric] * abs(delta) / result["scales"][metric])
        assert abs(score["score"] - expected) < 1e-10
    reference["clean"].update(ece=0, nll=0, brier=0, acc=1)
    result = compute_kev_selection_score(reference, reference)
    assert result["score"] == 100
    assert result["scales"] == {"nll": 1e-6, "acc": .05, "brier": 1e-6, "ece": .05}


def test_kev_selection_incomplete_or_invalid_results_never_rank(tmp_path):
    reference = _kev_candidate(tmp_path, 3)["metrics"]
    invalid = []
    for key in ("acc", "nll", "brier", "ece"):
        for value in (None, float("nan"), float("inf"), True, -.1):
            item = copy.deepcopy(reference)
            item["clean"][key] = value
            invalid.append(item)
    for key, value in (("requested_records", 1264), ("evaluated_records", 8435),
                       ("evaluated_questions", 9329), ("rejected_records", 1), ("truncated_records", 1)):
        item = copy.deepcopy(reference)
        item["coverage"][key] = value
        invalid.append(item)
    for key, value in (("dataset_split", "test"), ("validation_set", "other/val.jsonl"),
                       ("test_used", True), ("evaluation_status", "PARTIAL"), ("exit_code", 1)):
        invalid.append({**copy.deepcopy(reference), key: value})
    for item in invalid:
        result = compute_kev_selection_score(item, reference)
        assert result["score"] is None and result["rank"] is None
        assert compute_kev_selection_score(reference, item)["score"] is None


def test_kev_selection_targets_policy_and_original_report_agree(tmp_path):
    reference = _kev_candidate(tmp_path, 3)["metrics"]
    reference["report"] = {"clean": copy.deepcopy(reference["clean"]),
                           "coverage": copy.deepcopy(reference["coverage"]),
                           "tasks": {"custom_choice": {"n": 8436}, "custom_score": {"n": 894}},
                           "metric_policy": {"version": 2, "nll_floor": 1e-9}}
    assert compute_kev_selection_score(reference, reference)["score"] == 100
    other = copy.deepcopy(reference)
    other["report"]["tasks"]["custom_choice"]["n"] -= 1
    assert compute_kev_selection_score(other, reference)["score"] is None
    other = copy.deepcopy(reference)
    other["report"]["metric_policy"]["version"] = 1
    assert compute_kev_selection_score(other, reference)["score"] is None
    other = copy.deepcopy(reference)
    other["report"]["clean"]["nll"] = .1
    assert compute_kev_selection_score(other, reference)["reason"] == "inconsistent_report_clean"


def test_kev_retention_continuation_and_single_s1_group_keep_all(tmp_path):
    queue = [_kev_candidate(tmp_path, n) for n in (3, 4, 10)]
    queue[1]["metrics"]["clean"].update(nll=1.1, ece=.06)
    queue[2]["init_from"] = queue[0]["checkpoint_path"]
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert report["released_bytes"] == 0
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue)
    assert queue[0]["selection"]["score"] == 100
    assert queue[1]["selection"]["score"] < 100
    assert queue[2]["selection"]["group"] == "S1_WEIGHT_ABLATION"
    assert report["groups"]["HOMOLOGOUS_CONTINUATION"]["eligible_runs"] == 2
    assert report["groups"]["S1_WEIGHT_ABLATION"]["eligible_runs"] == 1


def test_kev_retention_group_quota_ties_and_required_control_levels(tmp_path):
    queue = _kev_queue(tmp_path)
    for c in queue[3:]:
        c["metrics"]["clean"] = copy.deepcopy(queue[0]["metrics"]["clean"])
    first = evaluate_kev_retention(queue, project_root=tmp_path)
    second = evaluate_kev_retention(list(reversed(queue)), project_root=tmp_path)
    assert first["groups"] == second["groups"]
    group = first["groups"]["HOMOLOGOUS_CONTINUATION"]
    assert group["eligible_runs"] == 7 and group["core_quota"] == 2
    assert group["ranked_ids"] == ["KEV-V8-C03", "KEV-V8-C04", "KEV-V8-C20", "KEV-V8-C21",
                                    "KEV-V8-C22", "KEV-V8-C23", "KEV-V8-C24"]
    queue += [_kev_candidate(tmp_path, n) for n in (5, 6, 7, 8, 9)]
    # The original state contrasts remain necessary even with a shared display label.
    queue[-5]["control_variant"] = queue[-4]["control_variant"] = "STATE_PAIR"
    evaluate_kev_retention(queue, project_root=tmp_path)
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue[-5:])


def test_kev_retention_report_persists_fields_without_removing_weights(tmp_path):
    queue = _kev_queue(tmp_path)
    saved = []
    report = evaluate_kev_retention(queue, project_root=tmp_path, persist=lambda q: saved.append(copy.deepcopy(q)))
    assert len(saved) == 1 and saved[0][-1]["selection"]["rank"] is not None
    assert report["released_bytes"] == 0
    low = queue[-1]
    assert low["retention"]["status"] == "PENDING"
    assert low["retention"]["planned_action"] == "PRUNED_LOW_SCORE"
    assert (tmp_path / low["checkpoint_path"] / "head.pt").is_file()


def test_kev_retention_apply_only_weights_with_real_bytes_and_repeat(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    directory = tmp_path / low["checkpoint_path"]
    originals = {p: p.read_bytes() for p in directory.iterdir() if p.suffix in (".json", ".log")}
    allocated = sum((directory / n).stat().st_blocks * 512 for n in ("head.pt", "adapter_model.safetensors"))
    logical = sum((directory / n).stat().st_size for n in ("head.pt", "adapter_model.safetensors"))
    queue_path = tmp_path / "candidate_queue.json"
    ledger_path = tmp_path / "candidate_ledger.json"
    snapshots = []
    def persist(q):
        snapshots.append(copy.deepcopy(q))
        queue_path.write_text(json.dumps(q))
        ledger_path.write_text(json.dumps({"candidates": q}))
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=persist)
    assert snapshots[0][-1]["recipe"] == low["recipe"]
    assert snapshots[0][-1]["retention"]["status"] == "PENDING"
    assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
    assert low["retention"]["released_bytes"] == allocated
    assert low["retention"]["removed_weight_bytes"] == logical
    assert report["released_bytes"] == allocated * 5
    assert directory.is_dir() and all(p.read_bytes() == data for p, data in originals.items())
    assert json.loads(ledger_path.read_text())["candidates"][-1]["retention"]["status"] == "PRUNED_LOW_SCORE"
    pruned_at = low["retention"]["pruned_at"]
    again = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=persist)
    assert again["released_bytes"] == 0 and low["retention"]["released_bytes"] == 0
    assert low["retention"]["total_released_bytes"] == allocated
    assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
    assert low["retention"]["pruned_at"] == pruned_at


def test_kev_retention_missing_recipe_or_persistence_preserves_weights(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    for missing in ("source_git_sha", "parent_init_source", "data_identity", "base_model", "init_from", "command"):
        value = low["recipe"].pop(missing)
        evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
        assert low["retention"]["status"] == "PENDING"
        assert missing in low["retention"]["reason"]
        assert (tmp_path / low["checkpoint_path"] / "head.pt").is_file()
        low["recipe"][missing] = value
    source = low["recipe"]["source_git_sha"]
    low["recipe"]["source_git_sha"] = "N/A"
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and "source_git_sha" in low["retention"]["reason"]
    low["recipe"]["source_git_sha"] = source
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True)
    assert low["retention"]["reason"] == "original_queue_persistence_required"
    def cannot_persist(q):
        raise OSError("original record is not writable")
    import pytest
    with pytest.raises(OSError):
        evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=cannot_persist)
    assert (tmp_path / low["checkpoint_path"] / "head.pt").is_file()


def test_kev_retention_all_entity_protections_and_pending_metrics(tmp_path):
    queue = _kev_queue(tmp_path)
    queue[3]["status"] = "RUNNING"
    queue[4]["recovery_in_use"] = True
    queue[5]["scientific_representative"] = True
    queue[6]["is_curriculum_parent"] = True
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None,
                                   protected_paths=[queue[7]["checkpoint_path"]])
    assert report["released_bytes"] == 0
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue)
    queue[7]["metrics"]["clean"]["nll"] = None
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert queue[7]["selection"]["score"] is None
    assert queue[7]["retention"]["status"] == "PENDING"
    assert (tmp_path / queue[7]["checkpoint_path"] / "head.pt").is_file()


def test_kev_retention_missing_entity_does_not_invent_pruning(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    for name in ("head.pt", "adapter_model.safetensors"):
        (tmp_path / low["checkpoint_path"] / name).unlink()
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING"
    assert low["retention"]["released_bytes"] == 0
    low["weights_saved"] = False
    evaluate_kev_retention(queue, project_root=tmp_path)
    assert low["retention"]["status"] == "NOT_SAVED"


def test_kev_retention_symlink_shared_files_and_outside_runs_preserved(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    directory = tmp_path / low["checkpoint_path"]
    head = directory / "head.pt"
    target = tmp_path / "outside-weight.pt"
    target.write_bytes(head.read_bytes())
    head.unlink()
    head.symlink_to(target)
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and target.is_file()
    head.unlink()
    import os
    os.link(target, head)
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and head.is_file()
    low["checkpoint_path"] = "outside"
    low["recipe"]["checkpoint_path"] = "outside"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "head.pt").write_bytes(b"not-a-run")
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and (outside / "head.pt").is_file()


def test_kev_retention_partial_entity_requires_original_removal_record(tmp_path):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    (tmp_path / low["checkpoint_path"] / "head.pt").unlink()
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["reason"] == "incomplete_weight_entity_without_removal_record"
    assert low["retention"]["status"] == "PENDING" and low["retention"]["freed_bytes"] == 0
    assert (tmp_path / low["checkpoint_path"] / "adapter_model.safetensors").is_file()


def test_kev_retention_partial_removal_records_only_successful_bytes(tmp_path, monkeypatch):
    queue = _kev_queue(tmp_path)
    low = queue[-1]
    head = tmp_path / low["checkpoint_path"] / "head.pt"
    adapter = head.with_name("adapter_model.safetensors")
    head_bytes, adapter_bytes = head.stat().st_blocks * 512, adapter.stat().st_blocks * 512
    original_unlink = Path.unlink
    def unlink(path, *args, **kwargs):
        if path == adapter:
            raise PermissionError("recorded weight cannot be removed")
        return original_unlink(path, *args, **kwargs)
    monkeypatch.setattr(Path, "unlink", unlink)
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PENDING" and adapter.is_file()
    assert low["retention"]["freed_bytes"] == low["retention"]["released_bytes"] == head_bytes
    assert low["retention"]["applied"] is True
    monkeypatch.setattr(Path, "unlink", original_unlink)
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
    assert low["retention"]["released_bytes"] == adapter_bytes
    assert low["retention"]["total_released_bytes"] == head_bytes + adapter_bytes
    assert report["freed_bytes"] == report["released_bytes"] == adapter_bytes


def test_kev_retention_c11_original_observations_survive(tmp_path):
    queue = _kev_queue(tmp_path)
    original = {"best_accuracy": "KEV-V8-C03", "best_nll": "KEV-V8-C03", "outstanding": ["KEV-V8-C09"]}
    c11 = {"candidate_id": "KEV-V8-C11", "name": "KEV-V8-VAL-BEST", "candidate_kind": "SELECTION",
           "status": "PENDING", "selection": copy.deepcopy(original)}
    queue.append(c11)
    report = evaluate_kev_retention(queue, project_root=tmp_path)
    assert all(c11["selection"][k] == v for k, v in original.items())
    assert c11["selection"]["score"] is None and c11["retention"]["status"] == "NOT_SAVED"
    assert report["applied"] is False and report["freed_bytes"] == 0


def _kev_ratio_queue(root):
    queue = [_kev_candidate(root, n) for n in (3, 4)]
    for index in range(16):
        cid, variant = f"KEV-V8-R{index + 1:02d}", f"R{index + 1:02d}"
        c = _kev_candidate(root, index + 20, candidate_id=cid, control_variant=variant,
                           retention_group="KEV_TYPED_COVERAGE_V1", init_from=queue[0]["checkpoint_path"])
        c["recipe"].update(candidate_id=cid, init_from=c["init_from"], base_revision=None)
        c["metrics"]["clean"]["nll"] += (index + 1) * .01
        queue.append(c)
    return queue


def test_kev_retention_sixteen_ratio_names_keep_three_and_prune_fixtures(tmp_path):
    queue = _kev_ratio_queue(tmp_path)
    first = evaluate_kev_retention(copy.deepcopy(queue), project_root=tmp_path)
    reversed_report = evaluate_kev_retention(copy.deepcopy(list(reversed(queue))), project_root=tmp_path)
    assert first["groups"] == reversed_report["groups"]
    assert first["decisions"] == reversed_report["decisions"]
    group = first["groups"]["KEV_TYPED_COVERAGE_V1"]
    assert (group["eligible_runs"], group["core_quota"]) == (16, 3)
    removed = [tmp_path / c["checkpoint_path"] / name for c in queue[5:]
               for name in ("head.pt", "adapter_model.safetensors")]
    allocated = sum(p.stat().st_blocks * 512 for p in removed)
    originals = {p: p.read_bytes() for c in queue for p in (tmp_path / c["checkpoint_path"]).iterdir()
                 if p.suffix in (".json", ".log")}
    snapshots = []
    def persist(candidates):
        snapshots.append(copy.deepcopy(candidates))
        (tmp_path / "candidate_queue.json").write_text(json.dumps(candidates))
        (tmp_path / "candidate_ledger.json").write_text(json.dumps({"candidates": candidates}))
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=persist)
    kept = [c["candidate_id"] for c in queue[2:] if c["retention"]["status"] in ("RETAINED", "PROTECTED")]
    assert kept == ["KEV-V8-R01", "KEV-V8-R02", "KEV-V8-R03"]
    assert all(c["retention"]["status"] == "PRUNED_LOW_SCORE" for c in queue[5:])
    assert all(not p.exists() for p in removed)
    assert report["released_bytes"] == allocated and report["removed_weight_bytes"] > 0
    assert snapshots[0][-1]["recipe"]["base_revision"] is None
    assert snapshots[0][-1]["retention"]["planned_action"] == "PRUNED_LOW_SCORE"
    assert all(c["recipe"]["base_revision"] is None and c["retention"]["base_revision"] == "N/A"
               and c["retention"]["retraining_limitations"] for c in queue[2:])
    assert all((tmp_path / c["checkpoint_path"]).is_dir() for c in queue)
    assert all(p.read_bytes() == content for p, content in originals.items())
    assert all(c["retention"]["status"] == "PROTECTED" for c in queue[:2])


def test_kev_retention_ratios_explicit_science_parent_and_active_protections(tmp_path):
    queue = _kev_ratio_queue(tmp_path)
    queue[-1]["scientific_representative"] = True
    queue[-3]["is_serving"] = True
    queue[-4].update(status="RUNNING", training_status="RUNNING", metrics={})
    queue[-5]["checkpoint_id"] = sorted(OLD_CORE_CHECKPOINT_IDS)[0]
    child = _kev_candidate(tmp_path, 90, status="PENDING", training_status="QUEUED", metrics={},
                           init_from=queue[-2]["checkpoint_path"])
    queue.append(child)
    first = evaluate_kev_retention(copy.deepcopy(queue), project_root=tmp_path)
    second = evaluate_kev_retention(copy.deepcopy(list(reversed(queue))), project_root=tmp_path)
    assert first["groups"] == second["groups"] and first["decisions"] == second["decisions"]
    assert first["groups"]["KEV_TYPED_COVERAGE_V1"]["core_quota"] == 3
    evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    for c in queue[13:18]:
        assert c["retention"]["status"] == "PROTECTED"
        assert (tmp_path / c["checkpoint_path"] / "head.pt").is_file()
    assert "base_import_serving_or_parent_path" in queue[16]["retention"]["protection_reasons"]
    assert "scientific_representative" in queue[17]["retention"]["protection_reasons"]
    assert any(c["retention"]["status"] == "PRUNED_LOW_SCORE" for c in queue[5:13])


def test_kev_retention_low_rank_s1_only_r01_remains_required(tmp_path):
    queue = _kev_ratio_queue(tmp_path)
    r01 = queue[2]
    r01["metrics"]["clean"]["nll"] = 2.0
    first = evaluate_kev_retention(copy.deepcopy(queue), project_root=tmp_path)
    reversed_report = evaluate_kev_retention(copy.deepcopy(list(reversed(queue))), project_root=tmp_path)
    assert first["groups"] == reversed_report["groups"] and first["decisions"] == reversed_report["decisions"]
    assert first["groups"]["KEV_TYPED_COVERAGE_V1"]["ranked_ids"][-1] == "KEV-V8-R01"
    report = evaluate_kev_retention(queue, project_root=tmp_path, apply=True, persist=lambda q: None)
    assert r01["selection"]["rank"] == 16 and r01["retention"]["status"] == "PROTECTED"
    assert (tmp_path / r01["checkpoint_path"] / "head.pt").is_file()
    assert report["groups"]["KEV_TYPED_COVERAGE_V1"]["core_quota"] == 3
    kept = [c["candidate_id"] for c in queue[2:] if c["retention"]["status"] in ("RETAINED", "PROTECTED")]
    assert kept == ["KEV-V8-R01", "KEV-V8-R02", "KEV-V8-R03", "KEV-V8-R04"]
    assert all(c["retention"]["status"] == "PRUNED_LOW_SCORE" for c in queue[6:])


def test_kev_retention_unknown_revision_alone_preserves_recipe_and_allows_pruning(tmp_path):
    for index, revision in enumerate((None, "N/A", "", "UNKNOWN", "missing")):
        root = tmp_path / str(index)
        queue = _kev_queue(root)
        low = queue[-1]
        if revision == "missing":
            low["recipe"].pop("base_revision")
        else:
            low["recipe"]["base_revision"] = revision
        recipe = copy.deepcopy(low["recipe"])
        evaluate_kev_retention(queue, project_root=root, apply=True, persist=lambda q: None)
        assert low["retention"]["status"] == "PRUNED_LOW_SCORE"
        assert low["recipe"] == recipe
        assert low["retention"]["base_revision"] == "N/A"
        assert low["retention"]["retraining_limitations"]


