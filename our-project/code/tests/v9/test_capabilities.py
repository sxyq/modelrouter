"""Narrow capability parsing, action identity, and refresh-retention tests."""

import io
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from modelrouter.v9.capabilities.features import candidate_action, capability_cards, load_current
from modelrouter.v9.capabilities.normalize import normalize_catalog, public_catalog
from modelrouter.v9.capabilities.refresh import API_URL, PUBLIC_URL, refresh


class Reply(io.BytesIO):
    status = 200
    headers = {"Content-Type": "application/json", "Date": "Thu, 29 Oct 2026 00:00:00 GMT",
               "X-api-key": "private-test-key", "Set-Cookie": "private-test-key"}


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.row = {
            "id": "aa-uuid", "slug": "gpt-6-luna", "native_effort": "high",
            "revision": "2026-10-01",
            "evaluations": {
                "artificial_analysis_intelligence_index": 47.2,
                "artificial_analysis_intelligence_index_version": 4,
                "livecodebench": {"score": 0.62, "unit": "fraction", "version": "v6"},
            },
        }
        self.payload = {"data": [self.row, {
            "id": "different-id", "slug": "another-model", "name": "qwen3.8-flash",
            "evaluations": {"artificial_analysis_intelligence_index": 99},
        }]}

    def test_exact_identity_raw_values_and_effort_scope(self):
        models = normalize_catalog(self.payload, API_URL, "2026-10-29T00:00:00Z")
        cards = capability_cards({"snapshot_id": "test-v1", "models": models}, [
            {"model": model, "native_effort": effort, "action_id": f"{model}:{effort}"}
            for model, effort in [("gpt-6-luna", "high"), ("gpt-6-luna", "low"),
                                  ("qwen3.8-flash", "none")]
        ])
        high = {item["metric_name"]: item for item in cards[0]["action_metrics"]}
        self.assertEqual(high["artificial_analysis_intelligence_index"]["score_raw"], 47.2)
        self.assertEqual(high["artificial_analysis_intelligence_index"]["score_unit"], "INDEX")
        self.assertEqual(high["livecodebench"]["score_raw"], 0.62)
        self.assertEqual(high["livecodebench"]["score_unit"], "fraction")
        self.assertEqual(high["livecodebench"]["benchmark_version"], "v6")
        self.assertEqual(high["artificial_analysis_intelligence_index"]["benchmark_version"], 4)
        self.assertNotIn("artificial_analysis_intelligence_index_version", high)
        self.assertTrue(all(item["score_raw"] is None for item in cards[1]["action_metrics"]))
        self.assertEqual(cards[2]["model_evidence_status"], "MODEL_NOT_FOUND")
        self.assertEqual(cards[2]["evidence_status"], "NOT_MEASURED")
        self.assertEqual(cards[2]["action_id"], "qwen3.8-flash:none")
        unscoped = dict(self.row, native_effort=None)
        model_only = normalize_catalog({"data": [unscoped]}, API_URL, "now")
        card = capability_cards({"models": model_only}, [
            {"model_id": "gpt-6-luna", "native_effort": "high", "action_id": "gpt-6-luna:high"}
        ])[0]
        self.assertEqual(card["model_metrics"][0]["score_raw"], 47.2)
        self.assertEqual(card["evidence_status"], "NOT_MEASURED")
        self.assertTrue(all(item["score_scope"] == "effort" for item in card["action_metrics"]))
        self.assertEqual(capability_cards({}, [{"model": "gpt-6-luna", "native_effort": "high",
                         "action_id": "gpt-6-luna:high"}])[0]["model_evidence_status"], "NOT_MEASURED")

    def test_public_embedded_json_and_flight(self):
        document = {"props": {"pageProps": self.payload}}
        html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(document) + '</script>'
        self.assertEqual(len(public_catalog(html)["data"]), 2)
        flight = "1:" + json.dumps(document) + "\n"
        html = '<script>self.__next_f.push(' + json.dumps([1, flight]) + ')</script>'
        self.assertEqual(len(public_catalog(html)["data"]), 2)

    def test_candidate_inputs_do_not_invent_effort_or_relabel_models(self):
        model_only = normalize_catalog({"data": [dict(self.row, native_effort=None)]}, API_URL, "now")
        cards = capability_cards({"snapshot_id": "snapshot", "models": model_only}, [
            "gpt-6-luna", "gpt-6-luna:high", {"model_id": "qwen3.8-flash", "native_effort": "none"},
        ])
        self.assertEqual([card["action_id"] for card in cards],
                         ["gpt-6-luna", "gpt-6-luna:high", "qwen3.8-flash:none"])
        self.assertIsNone(cards[0]["native_effort"])
        self.assertEqual(cards[0]["model_metrics"][0]["score_raw"], 47.2)
        self.assertTrue(all(metric["score_raw"] is None for card in cards for metric in card["action_metrics"]))
        self.assertEqual(cards[0]["action_metrics"][0]["missing_reason"], "EFFORT_NOT_REPORTED")
        for action in ({"model": "other-model", "model_id": "gpt-6-luna"},
                       {"model": "gpt-6-luna", "native_effort": "high", "action_id": "gpt-6-luna:low"}):
            with self.assertRaises(ValueError):
                candidate_action(action)

    def test_invalid_scores_units_and_conflicting_identity_are_not_measurements(self):
        for score in (True, "47.2", float("nan"), float("inf")):
            row = dict(self.row, evaluations={"artificial_analysis_intelligence_index": {"score": score}})
            with self.assertRaises(ValueError):
                normalize_catalog({"data": [row]}, API_URL, "now")
        row = dict(self.row, evaluations={"artificial_analysis_intelligence_index": {"score": 47.2, "unit": "%"}})
        with self.assertRaises(ValueError):
            normalize_catalog({"data": [row]}, API_URL, "now")
        with self.assertRaises(ValueError):
            normalize_catalog({"data": [dict(self.row, model_id="gpt-6.1-sol")]}, API_URL, "now")

    def test_each_refresh_fetches_and_failure_retains_current(self):
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            with patch.dict(os.environ, {"ARTIFICIAL_ANALYSIS_API_KEY": "private-test-key"}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen") as fetch:
                fetch.side_effect = [Reply(json.dumps(self.payload).encode()),
                                     Reply(json.dumps(self.payload).encode()),
                                     urllib.error.URLError("private-test-key")]
                first = refresh(data_dir)
                refreshed = refresh(data_dir)
                index_before = (data_dir / "current.json").read_bytes()
                second = refresh(data_dir)
                self.assertEqual(fetch.call_count, 3)
                self.assertEqual(first["status"], "PARTIAL")
                self.assertEqual(first["capability_evidence_status"], "PARTIAL")
                self.assertEqual(first["measured_metric_count"], 2)
                self.assertNotEqual(first["snapshot_id"], refreshed["snapshot_id"])
                self.assertEqual(second["status"], "FAILED")
                self.assertEqual((data_dir / "current.json").read_bytes(), index_before)
                self.assertEqual(load_current(data_dir)["snapshot_id"], refreshed["snapshot_id"])
                self.assertEqual(load_current(data_dir / "current.json")["snapshot_version"], 2)
                self.assertEqual(len(list((data_dir / "snapshots").glob("*.json"))), 2)
                events = (data_dir / "refresh_log.jsonl").read_text()
                self.assertEqual(len(events.splitlines()), 3)
                self.assertNotIn("private-test-key", events)
                self.assertEqual(second["attempts"][-1]["source_url"], API_URL)
                self.assertTrue(second["attempts"][-1]["fetched_at_utc"].endswith("Z"))

    def test_public_missing_pages_keep_other_exact_records(self):
        html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps(self.payload) + '</script>'
        absent = urllib.error.HTTPError("https://artificialanalysis.ai/models/missing", 404, "missing", {}, io.BytesIO())
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            config = data_dir / "existing.json"
            config.write_text(json.dumps({"api_key": "generator-only-key"}))
            with patch.dict(os.environ, {}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen") as fetch:
                fetch.side_effect = [absent, Reply(html.encode()), absent]
                result = refresh(data_dir, config_path=config)
                self.assertEqual(result["status"], "PARTIAL")
                self.assertEqual(fetch.call_count, 3)
                self.assertTrue(all(not call.args[0].has_header("X-api-key") for call in fetch.call_args_list))
                snapshot = load_current(data_dir)
                self.assertEqual(snapshot["models"]["gpt-6-luna"]["evidence_status"], "MEASURED")
                self.assertEqual(snapshot["models"]["qwen3.8-flash"]["evidence_status"], "MODEL_NOT_FOUND")

    def test_public_parse_failure_continues_to_flash_once(self):
        flash = dict(self.row, slug="qwen3.8-flash", native_effort=None,
                     evaluations={"artificial_analysis_intelligence_index": 51.4})
        html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps({"data": [flash]}) + '</script>'
        absent = urllib.error.HTTPError(PUBLIC_URL.format("gpt-6.1-sol"), 404, "missing", {}, io.BytesIO())
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            with patch.dict(os.environ, {}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", side_effect=[
                     absent, Reply(b"<html>No embedded records</html>"), Reply(html.encode())]) as fetch:
                result = refresh(data_dir, config_path=data_dir / "no-config.json")
            self.assertEqual(fetch.call_count, 3)
            self.assertEqual([call.args[0].full_url for call in fetch.call_args_list],
                             [PUBLIC_URL.format(model) for model in ("gpt-6.1-sol", "gpt-6-luna", "qwen3.8-flash")])
            self.assertEqual([attempt["status"] for attempt in result["attempts"][1:]],
                             ["MODEL_NOT_FOUND", "FAILED", "FETCHED"])
            self.assertEqual(result["attempts"][2]["model_id"], "gpt-6-luna")
            self.assertEqual(result["attempts"][2]["http_status"], 200)
            self.assertEqual(result["attempts"][2]["error_type"], "ValueError")
            self.assertEqual(result["status"], "PARTIAL")
            self.assertEqual(result["attempt_measured_metric_count"], 1)
            models = load_current(data_dir)["models"]
            self.assertEqual(models["gpt-6-luna"]["evidence_status"], "NOT_MEASURED")
            self.assertEqual(models["gpt-6-luna"]["source_url"], PUBLIC_URL.format("gpt-6-luna"))
            self.assertEqual(models["qwen3.8-flash"]["metrics"][0]["score_raw"], 51.4)

    def test_public_partial_success_retains_other_models_measured_evidence(self):
        flash = dict(self.row, slug="qwen3.8-flash", native_effort=None,
                     evaluations={"artificial_analysis_intelligence_index": 51.4})
        html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps({"data": [flash]}) + '</script>'
        absent = urllib.error.HTTPError(PUBLIC_URL.format("gpt-6.1-sol"), 404, "missing", {}, io.BytesIO())
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            with patch.dict(os.environ, {"ARTIFICIAL_ANALYSIS_API_KEY": "private-test-key"}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", return_value=Reply(json.dumps(self.payload).encode())):
                refresh(data_dir)
            saved = load_current(data_dir)["models"]["gpt-6-luna"]
            with patch.dict(os.environ, {}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", side_effect=[
                     absent, Reply(b"<html>No embedded records</html>"), Reply(html.encode())]):
                result = refresh(data_dir, config_path=data_dir / "no-config.json")
            self.assertEqual(result["status"], "PARTIAL")
            self.assertEqual(result["measured_metric_count"], 3)
            self.assertEqual(result["attempt_measured_metric_count"], 1)
            self.assertEqual(load_current(data_dir)["models"]["gpt-6-luna"], saved)

    def test_same_model_partial_measurement_keeps_prior_metric_version_and_time(self):
        new_row = dict(self.row, evaluations={"artificial_analysis_intelligence_index": {
            "score": 48.5, "version": 5}})
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            with patch.dict(os.environ, {"ARTIFICIAL_ANALYSIS_API_KEY": "private-test-key"}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", side_effect=[
                     Reply(json.dumps(self.payload).encode()), Reply(json.dumps({"data": [new_row]}).encode())]):
                first = refresh(data_dir)
                second = refresh(data_dir)
            metrics = load_current(data_dir)["models"]["gpt-6-luna"]["metrics"]
            measured = {m["metric_name"]: m for m in metrics if m["evidence_status"] == "MEASURED"}
            self.assertEqual(measured["artificial_analysis_intelligence_index"]["score_raw"], 48.5)
            self.assertEqual(measured["artificial_analysis_intelligence_index"]["benchmark_version"], 5)
            self.assertEqual(measured["livecodebench"]["score_raw"], .62)
            self.assertEqual(measured["livecodebench"]["benchmark_version"], "v6")
            self.assertEqual(measured["livecodebench"]["fetched_at_utc"], first["fetched_at_utc"])
            self.assertEqual(second["attempt_measured_metric_count"], 1)
            self.assertEqual(second["measured_metric_count"], 2)

    def test_empty_fetch_retains_scored_current(self):
        empty_row = dict(self.row, evaluations={})
        empty_html = '<script id="__NEXT_DATA__" type="application/json">' + json.dumps({"data": [empty_row]}) + '</script>'
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            with patch.dict(os.environ, {"ARTIFICIAL_ANALYSIS_API_KEY": "private-test-key"}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", return_value=Reply(json.dumps(self.payload).encode())):
                first = refresh(data_dir)
            index_before = (data_dir / "current.json").read_bytes()
            for responses in ([urllib.error.HTTPError("https://artificialanalysis.ai/models/missing", 404,
                                                     "missing", {}, io.BytesIO()) for _ in range(3)],
                              [Reply(empty_html.encode()) for _ in range(3)]):
                with patch.dict(os.environ, {}, clear=True), \
                     patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", side_effect=responses) as fetch:
                    result = refresh(data_dir, config_path=data_dir / "no-config.json")
                    self.assertEqual(fetch.call_count, 3)
                    self.assertEqual(result["status"], "UNCHANGED_MISSING")
                    self.assertEqual(result["snapshot_id"], first["snapshot_id"])
                    self.assertEqual(result["measured_metric_count"], 2)
                    self.assertEqual(result["attempt_measured_metric_count"], 0)
                    self.assertEqual(result["attempt_capability_evidence_status"], "NOT_MEASURED")
                    self.assertEqual((data_dir / "current.json").read_bytes(), index_before)
            self.assertEqual(len(list((data_dir / "snapshots").glob("*.json"))), 1)

    def test_first_missing_snapshot_is_explicit_and_next_run_fetches_again(self):
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            responses = [urllib.error.HTTPError("https://artificialanalysis.ai/models/missing", 404,
                         "missing", {"Content-Type": "text/html", "X-api-key": "private-test-key"}, io.BytesIO())
                         for _ in range(6)]
            with patch.dict(os.environ, {}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", side_effect=responses) as fetch:
                first = refresh(data_dir, config_path=data_dir / "no-config.json")
                second = refresh(data_dir, config_path=data_dir / "no-config.json")
                self.assertEqual(fetch.call_count, 6)
                self.assertEqual(first["status"], "UPDATED_MISSING")
                self.assertEqual(second["status"], "UPDATED_MISSING")
                self.assertEqual(first["capability_evidence_status"], "NOT_MEASURED")
                self.assertEqual(first["measured_metric_count"], 0)
                self.assertEqual(load_current(data_dir)["snapshot_version"], 2)
                self.assertTrue(all(model["evidence_status"] == "MODEL_NOT_FOUND"
                                    for model in load_current(data_dir)["models"].values()))
                self.assertTrue(all(attempt["status"] == "MODEL_NOT_FOUND" for attempt in first["attempts"][1:]))
                self.assertNotIn("private-test-key", (data_dir / "refresh_log.jsonl").read_text())

    def test_first_access_failure_still_has_a_loadable_unmeasured_snapshot(self):
        with tempfile.TemporaryDirectory(prefix="mr-aa-test-") as temporary:
            data_dir = Path(temporary)
            denied = urllib.error.HTTPError("https://artificialanalysis.ai/models/gpt-6.1-sol", 403,
                                           "private-test-key", {}, io.BytesIO())
            with patch.dict(os.environ, {}, clear=True), \
                 patch("modelrouter.v9.capabilities.refresh.urllib.request.urlopen", side_effect=denied) as fetch:
                first = refresh(data_dir, config_path=data_dir / "no-config.json")
                self.assertEqual(fetch.call_count, 1)
            snapshot = load_current(data_dir)
            self.assertEqual(first["status"], "FAILED")
            self.assertEqual(snapshot["status"], "FAILED")
            self.assertEqual(snapshot["measured_metric_count"], 0)
            self.assertEqual(snapshot["capability_evidence_status"], "NOT_MEASURED")
            self.assertTrue(all(model["evidence_status"] == "NOT_MEASURED" for model in snapshot["models"].values()))
            self.assertTrue(all(metric["missing_reason"] == "SOURCE_UNAVAILABLE"
                                for model in snapshot["models"].values() for metric in model["metrics"]))
            self.assertNotIn("private-test-key", (data_dir / "refresh_log.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()
