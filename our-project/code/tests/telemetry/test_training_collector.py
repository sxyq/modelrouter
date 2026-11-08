"""Existing training history, results and duration cases."""
import copy
import json
import tempfile
from pathlib import Path

from router_data.checkpoint_retention import NEW_PROTOCOL_VERSION


def test_collector_original_history_inputs_and_unchanged_revision():
    from scripts import fetch_live_status as collector

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        runs_root = root / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
        def write_json(path, value):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")

        for rid, loss, validation_set in (("F01", .5, "same-fixed-val"),
                                          ("F02", .6, "same-fixed-val"),
                                          ("F03", .7, "other-fixed-val"),
                                          ("F03_LEGACY_MINFACTOR", .8, "legacy-fixed-val")):
            directory = runs_root / rid
            history = [{"checkpoint_id": rid + "-e01", "epoch": 1, "global_step": 10,
                        "train_loss": None if rid == "F03" else .4,
                        "validation": {"S1": {"loss": loss, "accuracy": .6, "items": 561}}}]
            if rid == "F01":
                history.append({"checkpoint_id": "F01-e02", "epoch": 2, "global_step": 20,
                                "train_loss": None, "validation": {"S1": {"loss": None, "items": 561}}})
            write_json(directory / "run.json", {"run_id": rid, "status": "completed",
                "protocol_version": "LEGACY_MINFACTOR" if "LEGACY" in rid else NEW_PROTOCOL_VERSION,
                "validation_set": validation_set, "history": history})
            write_json(directory / "epoch_metrics.json", history)
            write_json(directory / "cursor.json", {"consumed_items": 100, "consumed_units": 7})
        physical = runs_root / "F01/checkpoints/epoch_01.pt"
        physical.parent.mkdir(parents=True)
        physical.write_bytes(b"temporary fixture only")
        queue_log = runs_root / "continuous_queue.log"
        queue_log.write_text("[F03] Epoch 1/2 Chunk 1/2: loss=0.123, step=99/100, consumed=90/100\n")

        imported = root / "models/kev-4b-adapter"
        local_parent = root / "runs/KEV-FIXTURE"
        for directory, maximum in ((imported, None), (local_parent / "smoke_run", 2),
                                   (local_parent / "test_run", 3)):
            args = {"device": "cpu", "epochs": 2}
            if maximum is not None:
                args["max_steps"] = maximum
            write_json(directory / "training_config.json", {"args": args})
            write_json(directory / "training_metrics.json", {"optimizer_steps": maximum or 8,
                       "records_seen": 4, "grad_norm": [1.0, .9]})
            (directory / "adapter_model.pt").write_bytes(b"temporary adapter fixture only")
        (local_parent / "train_cpu.log").write_text("ep0 step 2/3 loss 0.111 1.0s/rec\n")

        originals = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
        output = root / "dashboard"
        payload = collector.build_training_history(root, output, processes={})
        assert payload["counts"]["laya"]["local_runs"] == 4
        assert payload["counts"]["kev"]["local_runs"] == 2
        assert payload["counts"]["kev"]["imported_assets"] == 1
        local_kev = [row for row in payload["runs"] if row["family"] == "kev" and row["origin"] == "LOCAL_RUN"]
        assert len(local_kev) == 2
        assert all(row["epochs"] == 0 and row["curve_points"] == 0 for row in local_kev)
        assert all(row["checkpoints"][0]["physical"] for row in local_kev)
        f01 = next(row for row in payload["runs"] if row["run_id"] == "F01")
        assert f01["checkpoints"][0]["physical"] is True
        assert f01["checkpoints"][0]["weight_bytes"] == physical.stat().st_size
        assert f01["checkpoints"][1]["evidence"] == "MISSING_HISTORY_UNCERTAIN"
        assert f01["checkpoints"][1]["ever_saved"] is None
        assert f01["exposure"]["trained_records"] == 100
        assert f01["validation"][1]["loss"] is None
        for row in payload["runs"]:
            detail = json.loads((output / row["curve_path"]).read_text())
            if row["run_id"] in ("F03", "F03_LEGACY_MINFACTOR"):
                assert all(point["step"] != 99 for point in detail["points"])
            if row["run_id"] == "F03":
                assert detail["points"][0]["train_loss"] is None
        comparison = next(row for row in payload["comparisons"]
                          if row["metric"] == "loss" and "same-fixed-val" in row["validation_set"])
        assert comparison["observations"] == 2
        assert comparison["best"]["run_id"] == "F01"
        assert comparison["worst"]["run_id"] == "F02"
        index = output / "shards/training_history.json"
        first_mtime = index.stat().st_mtime_ns
        again = collector.build_training_history(root, output, processes={})
        assert again["revision"] == payload["revision"]
        assert index.stat().st_mtime_ns == first_mtime
        assert all(path.read_bytes() == content for path, content in originals.items())

        # Report production reads existing shards and leaves source observations intact.
        research_root = root / "our-project/dashboard"
        published = collector.build_training_history(root, research_root, processes={})
        summary = collector.write_training_research_report(published, root)
        report = json.loads((root / summary["data"]).read_text())
        selected = next(r for r in report["observations"] if r["run_id"] == "F01")
        assert selected["best_loss_epoch"]["epoch"] == 1
        assert selected["selected_epoch_physical"] is True
        assert selected["best_accuracy_epoch"]["epoch"] == 1
        assert selected["epoch_records"][0]["global_step"] == 10
        assert len(report["observations"]) == 7
        assert selected["actual_cost_usd"] is None
        assert all(path.read_bytes() == content for path, content in originals.items())


def test_collector_research_same_target_and_loadable_epochs(tmp_path):
    from scripts import fetch_live_status as collector

    def write_json(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    runs_root = tmp_path / "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012"
    fixtures = {
        "F06": ("S1", [(1, .6738, .6002, .4141, .0247), (2, .6863, .6017, .415, .0549)]),
        "F06_S1": ("S1", [(2, .6809, .5936, .4079, None)]),
        "F07": ("S1", [(1, .6827, .6076, .4203, .0567), (2, .6791, .6145, .4213, .0388)]),
        "F08": ("S1", [(2, .6702, .6123, .4246, .0555)]),
        "F09": ("S1", [(2, .6649, .6100, .4226, .0271)]),
        "AUX_S2": ("S2", [(1, .9, .2, None, None)]),
        "AUX_S3": ("S3", [(1, .9, .2, None, None)]),
    }
    for index, (rid, (stream, values)) in enumerate(fixtures.items()):
        epochs = [{"epoch": epoch, "weights_saved": False,
                   "validation": {stream: {"accuracy": acc, "loss": loss, "brier": brier, "ece": ece, "items": 561}}}
                  for epoch, acc, loss, brier, ece in values]
        write_json(runs_root / rid / "run.json", {"run_id": rid, "status": "completed", "epochs_max": 2,
            "protocol_version": NEW_PROTOCOL_VERSION, "validation_set": "same-fixed-val",
            "supervision_classes": ["S1", "S2", "S3"] if rid in ("F06", "F07", "F08", "F09") else [stream],
            "train_origin": "cumulative", "base_model": "fixture-base",
            "layers": ["L1"], "config": {"loss": "soft-ce"},
            "started_at": f"2026-10-{index + 10:02d}T00:00:00Z", "history": epochs})
    physical = runs_root / "F06/checkpoints/epoch_02.pt"
    physical.parent.mkdir(parents=True)
    physical.write_bytes(b"temporary fixture only")

    c03 = {"acc": .5715969989281886, "nll": 1.0795525776246775,
           "brier": .537533605673637, "ece": .05104668378873653, "n": 9330}
    c04 = {"acc": .5711682743837084, "nll": 1.0872975000322915,
           "brier": .5402653787706695, "ece": .05987151793598101, "n": 9330}
    candidates = []
    for rid, metrics, seconds in (("KEV-V8-C03", c03, 3099.012350168079),
                                  ("KEV-V8-C04", c04, 2982.712651308626)):
        directory = tmp_path / "runs" / rid / "formal_run"
        write_json(directory / "training_config.json", {"args": {"device": "cuda", "epochs": 1,
                   "init_from": "fixture-parent-" + rid}})
        write_json(directory / "training_metrics.json", {"optimizer_steps": 16857, "grad_norm": [1.0]})
        val_metrics = {"clean": metrics, "duration_sec": seconds,
                   "validation_protocol": "fixed-val", "validation_set": "kev-fixed-val",
                   "coverage": {"requested_questions": 9330, "evaluated_questions": 9330}}
        write_json(directory / "val_metrics.json", val_metrics)
        (directory / "adapter_model.pt").write_bytes(b"temporary adapter fixture only")
        candidates.append({"candidate_id": rid, "status": "COMPLETED", "evaluation_status": "EVALUATED",
                           "checkpoint_path": str(directory.relative_to(tmp_path)), "metrics": val_metrics})
    candidates[1]["comparison_to_c03"] = {"status": "COMPARABLE", "direction": "candidate_minus_c03",
                                          "deltas": {k: c04[k] - c03[k] for k in ("acc", "nll", "brier", "ece")}}
    candidates[1]["coverage_analysis"] = {"ratio": {"S1": 2, "S3": 1}, "splits": {"train": {
        "records_by_class": {"S1": 4, "S3": 2}, "independent_units_by_class": {"S1": 4, "S3": 1}}},
        "encoding": {"encoded_records": 6}}
    write_json(tmp_path / "our-project/results/training/kev/candidate_queue.json", candidates)
    matrix_path = tmp_path / "our-project/planning/CANDIDATE_PROGRESSION_MATRIX.md"
    matrix_path.parent.mkdir(parents=True)
    matrix_header = "# 候选推进矩阵\n\n"
    matrix_history = "## 历史\n\n2026-10-24：C03/C04 已完成固定 Val，原有科学对照记录继续保留。\n"
    matrix_path.write_text(matrix_header + matrix_history, encoding="utf-8")
    originals = {p: p.read_bytes() for p in tmp_path.rglob("*") if p.is_file() and p != matrix_path}
    history = collector.build_training_history(tmp_path, processes={})
    original_validation = copy.deepcopy({r["key"]: r["validation"] for r in history["runs"]})
    # Other Val identities, counts, protocols and loss definitions stay separate.
    reference = next(r for r in history["runs"] if r["run_id"] == "F06_S1")
    for field, value in (("validation_set", "other-fixed-val"), ("items", 562),
                         ("protocol", "other-protocol"), ("loss_definition", "other-loss")):
        other = copy.deepcopy(reference)
        other["run_id"] = other["key"] = "OTHER_" + field
        if field in ("validation_set", "items"):
            other["validation"][0][field] = value
        else:
            other[field] = value
        history["runs"].append(other)
    live = {"kev": {"run_id": "KEV-V8-C04", "status": "COMPLETED", "evaluation_status": "EVALUATED",
                    "is_training": False}, "process": {"kev": {}}}
    summary = collector.write_training_research_report(history, tmp_path, live)
    report = json.loads((tmp_path / summary["data"]).read_text())
    rows = {r["run_id"]: r for r in report["observations"]}
    f06 = rows["F06"]
    assert (f06["best_loss_epoch"]["epoch"], f06["best_loss_epoch"]["loss"], f06["selected_epoch_physical"]) == (1, .6002, False)
    assert (f06["best_accuracy_epoch"]["epoch"], f06["best_accuracy_epoch"]["accuracy"], f06["best_accuracy_physical"]) == (2, .6863, True)
    assert rows["F06_S1"]["best_loss_epoch"]["loss"] == .5936
    assert (rows["F07"]["best_loss_epoch"]["epoch"], rows["F07"]["best_accuracy_epoch"]["epoch"]) == (1, 1)
    for rid in ("F07", "F08", "F09"):
        assert all(not c["physical"] and not c["pruned"] and c["ever_saved"] is None for c in rows[rid]["checkpoints"])
    for rid in ("AUX_S2", "AUX_S3"):
        assert rows[rid]["comparison"]["control_key"] is None
        assert rows[rid]["comparison"]["accuracy_delta"] is None
        assert rows[rid]["comparison"]["loss_delta"] is None
    trend = next(g for g in report["objective_trends"] if g["family"] == "laya" and g["stream"] == "S1"
                 and g["validation_set"] == "same-fixed-val" and g["items"] == 561
                 and g["protocol"] == NEW_PROTOCOL_VERSION and g["loss_definition"] == "soft-ce")
    assert [r["run_id"] for r in trend["observations"]] == ["F06", "F06_S1", "F07", "F08", "F09"]
    loaded = next(c for c in report["loadable_candidates"] if c["run_id"] == "F06")
    assert loaded["epoch"] == 2 and loaded["is_best_loss_epoch"] is False and loaded["is_best_accuracy_epoch"] is True
    assert [loaded["primary_validation"][k] for k in ("accuracy", "loss", "brier", "ece")] == [.6863, .6017, .415, .0549]
    assert "其他Epoch" in f06["candidate_role"]
    assert all(c["run_id"] not in ("F07", "F08", "F09", "F06_S1") for c in report["loadable_candidates"])
    kev_trend = next(g for g in report["objective_trends"] if g["protocol"] == "KEV_FORMAL_LORA")
    assert len(kev_trend["observations"]) == 2
    for rid, metrics in (("KEV-V8-C03", c03), ("KEV-V8-C04", c04)):
        assert [rows[rid]["best_loss_epoch"][k] for k in ("accuracy", "nll", "brier", "ece")] == [metrics[k] for k in ("acc", "nll", "brier", "ece")]
        assert rows[rid]["validation_coverage"]["evaluated_questions"] == 9330
    assert rows["KEV-V8-C04"]["evaluation_seconds"] == 2982.712651308626
    assert rows["KEV-V8-C04"]["comparison_to_c03"] == candidates[1]["comparison_to_c03"]
    assert rows["KEV-V8-C04"]["supervision"] == ["S1", "S3"]
    assert rows["KEV-V8-C04"]["sampling"]["ratio_label"] == "2:1"
    assert rows["KEV-V8-C04"]["sampling"]["materialized_per_epoch_by_stream"] == {"S1": 4, "S3": 2}
    assert rows["KEV-V8-C04"]["exposure"]["materialized_records"] == 6
    assert rows["KEV-V8-C04"]["exposure"]["encoded_records"] == 6
    assert rows["KEV-V8-C04"]["exposure"]["trained_records"] is None
    assert rows["KEV-V8-C03"]["exposure"]["materialized_records"] is None
    assert collector.public_training_record({str(tmp_path / "data"): {"raw_output": "private", "error": "private", "n": 6}}, tmp_path) == {"data": {"n": 6}}
    current = report["training_eta"]["current"]["kev"]
    assert (current["remaining_training_seconds"], current["validation_seconds"], current["estimated_finish_at"]) == (0, 0, None)
    assert current["validation_in_finish_estimate"] is False
    assert len(current["validation_samples"]) == 2
    assert "median of 2" in current["validation_method"]
    assert all(r["validation"] == original_validation[r["key"]] for r in history["runs"] if r["key"] in original_validation)
    assert all(p.read_bytes() == content for p, content in originals.items())
    markdown = (tmp_path / summary["report"]).read_text()
    assert "| F06 | 最低S1 Loss | 1 | 0.6738 | 0.6002 | 0.4141 | 0.0247 | False |" in markdown
    assert "| F06 | 最高S1 Accuracy | 2 | 0.6863 | 0.6017 | 0.415 | 0.0549 | True |" in markdown
    assert "0.6863/0.6017/N/A/0.415/0.0549" in markdown
    assert "9330" in markdown and "2982.712651308626" in markdown
    assert "COMPLETED" in markdown and "EVALUATED" in markdown
    assert "当前F07为两Epoch" not in markdown and "Kev运行中的旧dispatcher" not in markdown
    assert "节省229小时" not in markdown and "节省40小时" not in markdown and "节省26小时" not in markdown
    begin, end = "<!-- KEV_LIVE_CANDIDATES_BEGIN -->", "<!-- KEV_LIVE_CANDIDATES_END -->"
    for _ in range(2):
        matrix = matrix_path.read_text(encoding="utf-8")
        assert matrix.count(begin) == matrix.count(end) == 1
        assert matrix.startswith(matrix_header.rstrip("\n")) and matrix.endswith(matrix_history)
        for cid, metrics in (("KEV-V8-C03", c03), ("KEV-V8-C04", c04)):
            row = next(line for line in matrix.splitlines() if line.startswith("| " + cid + " |"))
            cells = [cell.strip() for cell in row.strip("|").split("|")]
            assert [float(value) for value in cells[4:8]] == [metrics[k] for k in ("acc", "nll", "brier", "ece")]
            assert cells[8] == "9330"
        if _ == 0:
            collector.write_training_research_report(history, tmp_path, live)
    assert all(p.read_bytes() == content for p, content in originals.items())


def test_collector_training_eta_original_budget(tmp_path):
    from scripts import fetch_live_status as collector
    history = {"runs": [{"root": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F01", "run_id": "F01",
        "protocol": NEW_PROTOCOL_VERSION,
        "status": "COMPLETED", "family": "laya", "sampling": {"mode": "FULL_COVERAGE"},
        "exposure": {"trained_records": 1000}, "training_seconds": 100,
        "supervision_classes": ["S1", "S2", "S3"], "source": "run.json"}],
        "data_census": {"layers": {"L1": {"S1": 1000}}}, "experiment_plans": {"kev_queue": []}}
    plans = {"full_coverage": {"F08": {"supervision_classes": ["S1"], "layer_fractions": {"L1": .25}, "epochs": 2}}, "matrix": {}}
    rows = [{"category": "full_coverage", "status": "ELIGIBLE", "run_id": "F08", "materialized": False}]
    estimate = collector.training_eta(history, plans, {}, rows)
    assert estimate["groups"][0]["remaining_records"] == 500
    assert estimate["groups"][0]["training_seconds"] == 50
    assert estimate["totals"]["planned_executable_runs"] == 1
    assert estimate["current"]["laya"]["remaining_training_seconds"] is None
    kev_val = {"stream": "clean", "validation_set": "same-kev-val", "items": 9330, "source": "val_metrics.json"}
    history["runs"] += [{"family": "kev", "root": "runs/" + rid, "run_id": rid, "protocol": "KEV_FORMAL_LORA",
                         "validation": [kev_val], "evaluation_status": "EVALUATED", "evaluation_seconds": seconds}
                        for rid, seconds in (("C03", 3000), ("C04", 3200))]
    history["runs"].append({"family": "kev", "root": "models/imported", "run_id": "imported", "protocol": "KEV_IMPORTED_LORA",
                            "validation": [kev_val], "evaluation_status": "EVALUATED", "evaluation_seconds": 9000})
    live = {"kev": {"run_id": "C04", "status": "TRAINING", "step": 5, "total_steps": 10,
                    "samples_per_s": 2, "is_training": True}, "process": {"kev": {"train_pid": 123, "batch": 1, "accum": 4}}}
    current = collector.training_eta(history, plans, live, rows)["current"]["kev"]
    assert current["remaining_training_seconds"] == 10 and current["validation_seconds"] == 3100
    assert current["validation_in_finish_estimate"] is True
    assert [s["run_id"] for s in current["validation_samples"]] == ["C03", "C04"]
    assert current["validation_method"] == "median of 2 same fixed Kev Val observed durations"
    path = tmp_path / "status.json"
    collector.atomic_json(path, {"loss": float("nan")})
    assert json.loads(path.read_text()) == {"loss": None}


def test_collector_live_terminal_results_and_observed_rate(tmp_path, monkeypatch):
    from scripts import fetch_live_status as collector
    monkeypatch.setattr(collector, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(collector, "_PROGRESS", {})
    directory = tmp_path / "runs/KEV-EXAMPLE/formal_run"
    directory.mkdir(parents=True)
    (directory / "training_metrics.json").write_text(json.dumps({
        "optimizer_steps": 17, "records_seen": 68, "wall_seconds": 30}))
    (directory.parent / "cursor.json").write_text(json.dumps({
        "step": 10, "consumed_records": 40, "loss": .4, "updated_at": "2026-10-20T04:00:00Z"}))
    history = {"runs": [{"family": "kev", "training_kind": "FORMAL_LORA", "root": "runs/KEV-EXAMPLE/formal_run",
        "run_id": "C03", "status": "COMPLETED", "training_status": "COMPLETED", "epochs": 1, "planned_epochs": 1,
        "evaluation_status": "FAILED", "queue_status": "FAILED", "failure_reason": "Validation evaluation failed",
        "protocol": "KEV_FORMAL_LORA"}]}
    result = collector._live_family("kev", {}, history)
    assert (result["step"], result["consumed_records"], result["loss_step"]) == (17, 68, 10)
    assert result["evaluation_status"] == "FAILED" and result["training_seconds"] == 30
    assert result["samples_per_s"] == 68 / 30
    assert result["speed_step"] == 17

    laya = tmp_path / "runs/LAYA/F07"
    laya.mkdir(parents=True)
    cursor = {"step_count": 10, "consumed_items": 100, "updated_at": "2026-10-20T04:00:00Z"}
    (laya / "cursor.json").write_text(json.dumps(cursor))
    monkeypatch.setattr(collector, "age_seconds", lambda t: 20 if t.endswith("00Z") else 10)
    proc = {"laya": {"train_pid": 123, "run_id": "F07", "out_root": "runs/LAYA", "elapsed_s": 30}}
    history = {"runs": [{"family": "laya", "run_id": "F07", "root": "runs/LAYA/F07", "protocol": "example"}]}
    assert collector._live_family("laya", proc, history)["samples_per_s"] is None
    cursor.update(step_count=20, consumed_items=200, updated_at="2026-10-20T04:00:10Z")
    (laya / "cursor.json").write_text(json.dumps(cursor))
    assert collector._live_family("laya", proc, history)["samples_per_s"] == 10

    (directory.parent / "train.log").write_text("ep0 step 10/17 loss 0.400 2.0s/rec\n")
    proc = {"kev": {"train_pid": 456, "out": str(directory), "elapsed_s": 30}}
    history = {"runs": [{"family": "kev", "run_id": "C04", "root": "runs/KEV-EXAMPLE/formal_run",
                          "protocol": "KEV_FORMAL_LORA", "planned_epochs": 1}]}
    live = collector._live_family("kev", proc, history)
    assert live["samples_per_s"] == .5 and live["speed_step"] == 10
    assert live["consumed_records"] is None
    assert live["speed_source"] == "runs/KEV-EXAMPLE/train.log"
    assert collector._live_family("kev", proc, history)["samples_per_s"] == .5
    with (directory.parent / "train.log").open("a") as stream:
        stream.write("ep0 step 15/17 loss 0.300 2.5s/rec\n")
    live = collector._live_family("kev", proc, history)
    assert live["samples_per_s"] == .4 and live["speed_step"] == 15


def test_collector_kev_validation_appended_rows(tmp_path, monkeypatch):
    from scripts import fetch_live_status as collector
    monkeypatch.setattr(collector, "_VAL_CACHE", {})
    monkeypatch.setattr(collector, "age_seconds", lambda value: 15 if value else None)
    directory = tmp_path / "formal_run"
    attempt = directory / "val_metrics/attempt_0002"
    attempt.mkdir(parents=True)
    data = tmp_path / "val.jsonl"
    data.write_text(json.dumps({"questions": {"a": {}, "b": {}}}) + "\n"
                    + json.dumps({"questions": {"c": {}}}) + "\n")
    result = {"evaluation_status": "EVALUATING", "validation_set": str(data),
              "report_path": str(attempt / "report.json"), "attempt_id": 2, "device": "cuda"}
    (directory / "val_metrics.json").write_text(json.dumps(result))
    predictions = attempt / "predictions.jsonl"
    first = json.dumps({"rows": [{}, {}]}) + "\n"
    second = json.dumps({"rows": [{}]})
    predictions.write_text(first + second)
    candidate = {"evaluation_attempts": [{"started_at": "2026-10-20T08:00:00Z"}]}
    observed = collector.live_kev_validation(directory, candidate)
    assert observed["validation_coverage"] == {"requested_records": 2, "requested_questions": 3,
                                               "evaluated_records": 1, "evaluated_questions": 2}
    assert observed["evaluation_seconds"] == 15 and observed["validation_metrics"] == {}
    assert collector.live_kev_validation(directory, candidate)["validation_coverage"] == observed["validation_coverage"]
    with predictions.open("a") as stream:
        stream.write("\n")
    assert collector.live_kev_validation(directory, candidate)["validation_coverage"]["evaluated_records"] == 2
    result.update(evaluation_status="EVALUATED", clean={"acc": .75}, duration_sec=20,
                  coverage={"evaluated_records": 2, "requested_records": 2})
    (directory / "val_metrics.json").write_text(json.dumps(result))
    complete = collector.live_kev_validation(directory, candidate)
    assert complete["validation_metrics"]["acc"] == .75 and complete["evaluation_seconds"] == 20
    (directory.parent / "cursor.json").write_text("{}")
    assert collector.kev_cursor(directory) == directory.parent / "cursor.json"
    (directory / "cursor.json").write_text("{}")
    assert collector.kev_cursor(directory) == directory / "cursor.json"


