#!/usr/bin/env python3
"""
test_causal_schema.py - Unit tests for Causal Schema and state-outcome isolation.
"""

import unittest
from modelrouter.datasets.causal_schema import (
    CausalRecord,
    PreDecisionState,
    ObservedDecision,
    GroundTruthOutcome,
    Provenance,
    PolicyTag,
    SupervisionType,
    LabelNature,
    validate_causal_isolation,
)


class TestCausalSchema(unittest.TestCase):
    def setUp(self):
        self.valid_record = {
            "provenance": {
                "source_id": "TRA-001",
                "source_name": "Open-SWE-Traces",
                "official_origin": "https://huggingface.co/datasets/nvidia/Open-SWE-Traces",
                "license": "CC-BY-4.0",
                "instance_id": "test_inst_001",
            },
            "pre_decision_state": {
                "task_domain": "software_engineering",
                "step_index": 0,
                "context_chars": 1200,
                "prior_tool_calls_count": 0,
                "prior_error_signals_count": 0,
                "initial_prompt_snippet": "Fix issue in repo",
            },
            "observed_decision": {
                "action_type": "str_replace_editor",
                "model_choice": "Claude-3.7-Sonnet",
            },
            "ground_truth_outcome": {
                "label_nature": "OBSERVED_ACTION",
                "task_resolved": True,
            },
            "policy_tag": "TRAIN_ROUTER_CANDIDATE",
        }

    def test_valid_record_passes(self):
        is_valid, violations = validate_causal_isolation(self.valid_record)
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_causal_leakage_detected(self):
        # Inject future outcome into pre-decision state
        leaky_record = dict(self.valid_record)
        leaky_record["pre_decision_state"] = dict(self.valid_record["pre_decision_state"])
        leaky_record["pre_decision_state"]["task_resolved"] = True

        is_valid, violations = validate_causal_isolation(leaky_record)
        self.assertFalse(is_valid)
        self.assertTrue(any("task_resolved" in v for v in violations))

    def test_negative_step_or_tools_rejected(self):
        bad_record = dict(self.valid_record)
        bad_record["pre_decision_state"] = dict(self.valid_record["pre_decision_state"])
        bad_record["pre_decision_state"]["step_index"] = -1

        is_valid, violations = validate_causal_isolation(bad_record)
        self.assertFalse(is_valid)
        self.assertTrue(any("step_index" in v for v in violations))

    def test_data_class_construction(self):
        record = CausalRecord(
            provenance=Provenance(
                source_id="ROUTE-004",
                source_name="Arena",
                official_origin="https://lmsys.org",
                license="LMSYS",
                instance_id="battle_01",
            ),
            pre_decision_state=PreDecisionState(
                task_domain="general",
                initial_prompt_snippet="Hello",
            ),
            observed_decision=ObservedDecision(
                model_choice="gpt-4o",
            ),
            ground_truth_outcome=GroundTruthOutcome(
                label_nature=LabelNature.HUMAN_PREFERENCE,
                supervision_type=SupervisionType.S1_HUMAN_PREFERENCE,
                winner_choice="model_a",
            ),
            policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        )
        d = record.to_dict()
        self.assertEqual(d["provenance"]["source_id"], "ROUTE-004")
        self.assertEqual(d["ground_truth_outcome"]["supervision_type"], "S1")
        is_valid, violations = validate_causal_isolation(d)
        self.assertTrue(is_valid)


if __name__ == "__main__":
    unittest.main()
