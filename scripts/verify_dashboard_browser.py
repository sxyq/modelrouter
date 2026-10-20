#!/usr/bin/env python3
"""Compare the existing training dashboard with its real JSON responses."""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlsplit

from playwright.sync_api import sync_playwright

TARGET_URL = "http://10.16.15.202:8765/"
COUNT_FIELDS = (
    "planned_runs", "observed_runs", "local_runs", "executed_runs", "local_completed_runs", "metadata_only_runs", "imported_assets", "running_runs",
    "checkpoint_versions", "physical_checkpoints", "confirmed_saved_versions", "metadata_versions",
    "pruned_versions", "unknown_missing_versions", "train_curve_runs", "step_curve_runs",
    "epoch_only_runs", "unrecorded_curve_runs",
)


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def normalized(value):
    return str(value).replace(",", "").replace("\u00a0", "").strip()


def local_run_counts(runs):
    return {
        "local_runs": sum(r.get("origin") == "LOCAL_RUN" for r in runs),
        "local_completed_runs": sum(r.get("origin") == "LOCAL_RUN"
                                    and r.get("execution_evidence")
                                    and r.get("status") in ("COMPLETED", "EARLY_STOPPED") for r in runs),
        "imported_assets": sum(r.get("origin") == "IMPORTED_ADAPTER" for r in runs),
    }


def run_browser_verification(url=TARGET_URL, output_dir=Path("output/playwright"), browser_executable=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    report = {"url": url, "started_at": datetime.now(timezone.utc).isoformat(),
              "status": "RUNNING", "checks": [], "failed_requests": [],
              "http_errors": [], "console_errors": [], "page_errors": []}
    report_path = output_dir / "dashboard_verification.json"
    responses = []

    def require(condition, name, **evidence):
        report["checks"].append({"name": name, "passed": bool(condition), **evidence})
        if not condition:
            raise AssertionError(f"{name}: {evidence}")

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, args=["--no-proxy-server"],
                                                 executable_path=browser_executable)
            try:
                context = browser.new_context(viewport={"width": 1600, "height": 1100})
                page = context.new_page()
                page.on("response", lambda response: responses.append(response))
                page.on("requestfailed", lambda request: report["failed_requests"].append(
                    {"method": request.method, "url": request.url, "error": request.failure}))
                page.on("console", lambda message: report["console_errors"].append(message.text)
                        if message.type == "error" else None)
                page.on("pageerror", lambda error: report["page_errors"].append(str(error)))

                response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                require(response is not None and response.status == 200, "page_http",
                        status=response.status if response else None)
                live_url = urljoin(page.url, "live_status.json")
                page.wait_for_function(
                    "() => document.querySelector('#collected')?.textContent.startsWith('采集于')"
                    " || document.querySelector('#connection')?.textContent.includes('失败')"
                    " || document.querySelector('#connection')?.textContent.includes('DISCONNECTED')",
                    timeout=15000)
                live_responses = [r for r in responses if urlsplit(r.url).path == urlsplit(live_url).path]
                if not live_responses:
                    live_responses = [page.wait_for_event("response", predicate=lambda r:
                        urlsplit(r.url).path == urlsplit(live_url).path, timeout=15000)]
                require(bool(live_responses), "live_json_response_received", url=live_url)
                live_response = live_responses[-1]
                require(live_response.status == 200, "live_json_http", status=live_response.status)
                live = live_response.json()
                live_ready = live.get("connection_status") == "CONNECTED" and bool(live.get("history", {}).get("index"))
                report["checks"].append({"name": "live_collector_updated", "passed": live_ready,
                                         "connection_status": live.get("connection_status"),
                                         "collector_source": live.get("collector_source")})
                history_url = urljoin(page.url, "shards/training_history.json")
                existing_history = [r for r in responses if urlsplit(r.url).path == urlsplit(history_url).path]
                history_response = existing_history[-1] if existing_history else page.wait_for_event(
                    "response", predicate=lambda r: urlsplit(r.url).path == urlsplit(history_url).path,
                    timeout=15000)
                require(history_response.status == 200, "history_json_http", status=history_response.status)
                history = history_response.json()
                runs = history["runs"]
                require(isinstance(runs, list) and bool(runs), "history_has_runs", count=len(runs))
                page.wait_for_function(
                    "(n) => document.querySelector('#selected-run')?.options.length === n"
                    " && !document.querySelector('#curve-status')?.textContent.includes('正在读取')",
                    arg=len(runs), timeout=15000)

                (output_dir / "live_status_observed.json").write_text(
                    json.dumps(live, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                (output_dir / "training_history_observed.json").write_text(
                    json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

                for family in ("laya", "kev"):
                    model = live.get(family, {})
                    card = page.locator(f"#live-models .{family}")
                    require(card.locator(".run-id").inner_text() == str(model.get("run_id") or "N/A"),
                            "live_run_id", family=family, expected=model.get("run_id"))
                    metrics = card.locator(".metrics").evaluate(
                        "node => Object.fromEntries([...node.children].map(c =>"
                        " [c.querySelector('dt').textContent, c.querySelector('dd').textContent]))")
                    for field, label in (("step", "Step"), ("consumed_records", "已消费记录"),
                                         ("optimizer_updates", "优化器更新"), ("process_pid", "PID")):
                        value = model.get(field)
                        expected = str(value) if numeric(value) else "N/A"
                        require(normalized(metrics[label]) == normalized(expected),
                                "live_field", family=family, field=field,
                                expected=expected, observed=metrics[label])
                    if model.get("loss") is None:
                        require(card.locator(".loss").inner_text().startswith("N/A"),
                                "missing_loss_is_na", family=family)
                    speed_label = "样本 / 秒（累计实测）" if model.get("speed_scope") else "样本 / 秒（进度观测）"
                    speed = model.get("samples_per_s")
                    matches_speed = abs(float(normalized(metrics[speed_label])) - speed) <= .005 if numeric(speed) else normalized(metrics[speed_label]) == "N/A"
                    require(matches_speed,
                            "live_training_speed", family=family, expected=speed,
                            observed=metrics[speed_label], source=model.get("speed_source"))
                    if family == "kev" and model.get("validation_coverage"):
                        coverage = model["validation_coverage"]
                        expected = f"覆盖 {coverage.get('evaluated_records')} / {coverage.get('requested_records')}"
                        require(normalized(expected) in normalized(card.inner_text()), "kev_val_coverage", expected=expected)
                        for field, label in (("acc", "Accuracy"), ("nll", "NLL"), ("brier", "Brier"), ("ece", "ECE")):
                            value = model.get("validation_metrics", {}).get(field)
                            formatted = f"{value:.3f}".rstrip("0").rstrip(".") if numeric(value) else "N/A"
                            require(f"{label} {formatted}" in normalized(card.inner_text()),
                                    "kev_val_metric", field=field, expected=value)
                        for candidate in model.get("candidates", []):
                            require(f"{candidate['candidate_id']} {candidate['status']}" in card.inner_text(),
                                    "kev_candidate_status", candidate=candidate["candidate_id"], status=candidate["status"])

                    family_runs = [r for r in runs if r["family"] == family]
                    row = page.locator("#counts-body tr").filter(
                        has=page.locator("td:first-child", has_text=family)).first
                    cells = row.locator("td").all_text_contents()
                    require(len(cells) == len(COUNT_FIELDS) + 2, "count_columns", family=family)
                    epochs = [len(r["epochs"]) if isinstance(r.get("epochs"), list)
                              else r.get("epochs") for r in family_runs]
                    epoch_total = sum(epochs) if all(numeric(e) for e in epochs) else None
                    expected_counts = [epoch_total] + [history.get("counts", {}).get(family, {}).get(f)
                                                      for f in COUNT_FIELDS]
                    for index, value in enumerate(expected_counts, start=1):
                        require(normalized(cells[index]) == normalized(value if value is not None else "N/A"),
                                "history_count", family=family,
                                field="recorded_epochs" if index == 1 else COUNT_FIELDS[index - 2],
                                expected=value, observed=cells[index])
                    require(history["counts"][family]["observed_runs"] == len(family_runs),
                            "observed_run_count_matches_index", family=family, count=len(family_runs))
                    for field, expected in local_run_counts(family_runs).items():
                        require(history["counts"][family].get(field) == expected,
                                "local_and_imported_counts_match_index", family=family,
                                field=field, expected=expected, observed=history["counts"][family].get(field))

                keys = [r["key"] for r in runs]
                options = page.locator("#selected-run option").evaluate_all(
                    "nodes => nodes.map(n => ({key:n.value, label:n.textContent}))")
                require([o["key"] for o in options] == keys, "run_dropdown_matches_index")
                require(all(r["run_id"] in option["label"] for r, option in zip(runs, options)),
                        "run_dropdown_labels")
                table_keys = page.locator("#run-table [data-run]").evaluate_all(
                    "nodes => nodes.map(n => n.dataset.run)")
                require(table_keys == keys, "run_table_matches_index")
                names = page.locator("#run-table td:first-child b").all_text_contents()
                require(names == [r["run_id"] for r in runs], "run_table_labels")

                page.locator("#overlay-toggle").uncheck()
                filter_cases = (
                    ("family", lambda r: r.get("family")),
                    ("protocol", lambda r: r.get("protocol")),
                    ("supervision", lambda r: " + ".join(sorted(r.get("supervision_classes") or [])) or None),
                    ("sampling-ratio", lambda r: json.dumps([
                        r["sampling"].get("mode"), r["sampling"].get("ratio_label"),
                        r["sampling"].get("requested_ratios")], ensure_ascii=False, separators=(",", ":"))
                        if r.get("sampling") is not None else None),
                    ("training-stage", lambda r: r.get("stage")),
                    ("data-volume", lambda r: r.get("exposure", {}).get("trained_records")
                        if r.get("exposure") else None),
                )
                for control, field in filter_cases:
                    values = page.locator(f"#{control} option").evaluate_all("nodes => nodes.map(n => n.value)")
                    for value in dict.fromkeys((values[1], "__unknown__")):
                        if value not in values:
                            continue
                        expected_keys = [r["key"] for r in runs if (
                            "__unknown__" if field(r) is None or field(r) == "" else str(field(r))) == value]
                        page.locator(f"#{control}").select_option(value)
                        page.wait_for_function(
                            "(keys) => JSON.stringify([...document.querySelectorAll('#run-table [data-run]')]"
                            ".map(n => n.dataset.run)) === JSON.stringify(keys)", arg=expected_keys, timeout=15000)
                        selected_keys = page.locator("#selected-run option").evaluate_all("nodes => nodes.map(n => n.value)")
                        require(selected_keys == expected_keys, "filtered_run_dropdown", control=control,
                                value=value, expected=expected_keys, observed=selected_keys)
                    page.locator(f"#{control}").select_option("all")
                for exposure_field in ("candidate_records", "materialized_records", "encoded_records", "distinct_units"):
                    page.locator("#exposure-field").select_option(exposure_field)
                    options = page.locator("#data-volume option").evaluate_all("nodes => nodes.map(n => n.value)")
                    value = options[1]
                    expected_keys = [r["key"] for r in runs if (
                        str((r.get("exposure") or {}).get(exposure_field))
                        if numeric((r.get("exposure") or {}).get(exposure_field)) else "__unknown__") == value]
                    page.locator("#data-volume").select_option(value)
                    require(page.locator("#run-table [data-run]").evaluate_all("nodes => nodes.map(n => n.dataset.run)")
                            == expected_keys, "exposure_quantity_filter", field=exposure_field, expected=expected_keys)
                    page.locator("#data-volume").select_option("all")
                page.locator("#exposure-field").select_option("trained_records")
                page.wait_for_function(
                    "() => !document.querySelector('#curve-status').textContent.includes('正在读取')", timeout=15000)

                initial_key = page.locator("#selected-run").input_value()
                initial = next(r for r in runs if r["key"] == initial_key)
                candidates = [initial]
                other = next((r for r in runs if r["key"] != initial_key and r.get("curve_path")), None)
                require(other is not None, "single_run_switch_target_available", observed_runs=len(runs))
                candidates.append(other)
                candidates.extend(r for r in runs if r.get("run_id") in ("F06", "KEV-V8-C03")
                                  and r["key"] not in {c["key"] for c in candidates})

                for run in candidates:
                    if page.locator("#selected-run").input_value() != run["key"]:
                        page.locator("#selected-run").select_option(run["key"])
                    page.wait_for_function(
                        "(id) => document.querySelector('#curve-status').textContent.startsWith(id + ' ·')",
                        arg=run["run_id"], timeout=15000)
                    require(page.locator("#selected-run").input_value() == run["key"],
                            "single_run_selected", key=run["key"])
                    metadata = page.locator("#run-metadata").evaluate(
                        "node => Object.fromEntries([...node.children].map(c =>"
                        " [c.querySelector('dt').textContent, c.querySelector('dd').textContent]))")
                    for field, label in (("stage", "训练阶段"), ("initialization", "初始化"), ("source", "来源")):
                        expected = run.get(field)
                        if isinstance(expected, (dict, list)):
                            observed = json.loads(metadata[label])
                        else:
                            expected = str(expected) if expected is not None and expected != "" else "N/A"
                            observed = metadata[label]
                        require(observed == expected, "run_training_field", run=run["key"], field=field,
                                expected=expected, observed=observed)
                    summary = page.locator("#run-training-summary tr").first.locator("td").all_text_contents()
                    sampling = run.get("sampling") or {}
                    for column, field in ((2, "requested_ratios"), (3, "materialized_per_epoch_by_stream"),
                                          (4, "trained_total_by_stream")):
                        expected = sampling.get(field)
                        observed = json.loads(summary[column]) if isinstance(expected, (dict, list)) else summary[column]
                        require(observed == (expected if expected is not None else "N/A"), "run_sampling_field",
                                run=run["key"], field=field, expected=expected, observed=observed)
                    require(metadata["训练耗时"] == "N/A" if not numeric(run.get("training_seconds")) else
                            normalized(metadata["训练耗时"]) == normalized(f"{run['training_seconds']:.1f} 秒"),
                            "run_training_seconds", run=run["key"], expected=run.get("training_seconds"))
                    curve_responses = [r for r in responses if r.url.split("?")[0] ==
                                       urljoin(page.url, run.get("curve_path", ""))]
                    if run.get("curve_path"):
                        require(bool(curve_responses), "curve_json_response_received", key=run["key"])
                        curve_response = curve_responses[-1]
                        require(curve_response.status == 200, "curve_json_http",
                                key=run["key"], status=curve_response.status)
                        detail = curve_response.json()
                        require(detail["run"]["key"] == run["key"], "curve_run_identity", key=run["key"])
                    else:
                        detail = {"points": [], "validation": []}
                    points = detail["points"]
                    status = page.locator("#curve-status").inner_text()
                    require(f"· {len(points)} 训练点 ·" in status, "curve_point_count", key=run["key"])
                    axis = page.locator("#curve-axis").input_value()
                    expected_axis = "epoch" if "epoch" in str(run.get("curve_granularity", "")).lower() or (
                        points and all(p.get("step") is None for p in points)
                        and any(numeric(p.get("epoch")) for p in points)) else "step"
                    require(axis == expected_axis, "curve_default_axis", expected=expected_axis, observed=axis)
                    require(page.locator("#train-charts .chart").count() == 6,
                            "training_metric_charts", key=run["key"])
                    for metric, chart in zip(("train_loss", "consumed_records", "learning_rate",
                                              "samples_per_s", "optimizer_updates"),
                                             page.locator("#train-charts .chart").all()):
                        usable = [p for p in points if numeric(p.get(metric)) and
                                  (p.get(axis) is not None if axis == "timestamp" else numeric(p.get(axis)))]
                        if usable:
                            require(chart.locator("svg path").count() > 0, "curve_svg",
                                    run=run["key"], metric=metric, points=len(usable))
                        else:
                            require(chart.locator("svg").count() == 0 and "N/A" in chart.inner_text(),
                                    "missing_curve_is_na", run=run["key"], metric=metric)
                    if other and run["key"] == other["key"]:
                        require(page.locator("#run-metadata").inner_text().find(run["run_id"]) >= 0,
                                "single_run_switch", key=run["key"])

                ratio_pairs = [(a, b) for i, a in enumerate(runs) for b in runs[i + 1:]
                               if a.get("family") == b.get("family") and a.get("protocol")
                               and a.get("protocol") == b.get("protocol")
                               and a.get("supervision_classes") and b.get("supervision_classes")
                               and sorted(a["supervision_classes"]) == sorted(b["supervision_classes"])
                               and a.get("sampling") and b.get("sampling")
                               and (a["sampling"].get("ratio_label"), a["sampling"].get("requested_ratios"))
                               != (b["sampling"].get("ratio_label"), b["sampling"].get("requested_ratios"))]
                if ratio_pairs:
                    a, b = ratio_pairs[0]
                    page.locator("#selected-run").select_option(a["key"])
                    page.locator("#overlay-toggle").check()
                    page.locator('#overlay-list [data-overlay-action="none"]').click()
                    page.locator("#overlay-list [data-overlay]").evaluate_all(
                        "(nodes, key) => { const n = nodes.find(n => n.dataset.overlay === key);"
                        " n.checked = true; n.dispatchEvent(new Event('change', {bubbles:true})); }", b["key"])
                    page.wait_for_function(
                        "() => document.querySelector('#run-training-summary').rows.length === 2"
                        " && !document.querySelector('#curve-status').textContent.includes('正在读取')", timeout=15000)
                    require([a["run_id"], b["run_id"]] == page.locator("#run-training-summary tr td:first-child").evaluate_all(
                            "nodes => nodes.map(n => n.firstChild.textContent)"),
                            "same_protocol_supervision_different_ratio_overlay", runs=[a["key"], b["key"]])
                else:
                    report["checks"].append({"name": "same_protocol_supervision_different_ratio_overlay",
                                             "status": "NOT_EVALUATED", "reason": "No real different-ratio pair in the index"})

                page.screenshot(path=str(output_dir / "dashboard_training.png"), full_page=True)
                report["http_errors"] = [{"url": r.url, "status": r.status}
                                         for r in responses if r.status >= 400]
                require(not report["failed_requests"], "no_failed_requests",
                        failures=report["failed_requests"])
                require(not report["http_errors"], "no_http_errors", failures=report["http_errors"])
                require(not report["console_errors"], "no_console_errors", errors=report["console_errors"])
                require(not report["page_errors"], "no_page_errors", errors=report["page_errors"])
                require(live_ready, "continuous_collector_uses_current_schema")
                report["status"] = "PASS"
            finally:
                browser.close()
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = {"type": type(error).__name__, "message": str(error)}
    report["http_errors"] = [{"url": r.url, "status": r.status} for r in responses if r.status >= 400]
    report["duration_s"] = time.perf_counter() - started
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "duration_s": report["duration_s"],
                      "report": str(report_path), "error": report.get("error")}, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description="Verify the existing dashboard against real telemetry")
    parser.add_argument("--url", default=TARGET_URL)
    parser.add_argument("--output-dir", type=Path, default=Path("output/playwright"))
    parser.add_argument("--browser-executable", help="Use an already installed Chromium executable")
    args = parser.parse_args(argv)
    return run_browser_verification(args.url, args.output_dir, args.browser_executable)


if __name__ == "__main__":
    sys.exit(main())
