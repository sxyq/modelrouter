#!/usr/bin/env python3
"""
test_dataset_audit.py - Unit tests for DatasetAuditor and public sources registry.
"""

import unittest
from modelrouter.datasets.public_sources import PUBLIC_SOURCES_REGISTRY, PublicDatasetLoader
from modelrouter.datasets.audit import DatasetAuditor


class TestDatasetAudit(unittest.TestCase):
    def setUp(self):
        self.loader = PublicDatasetLoader()
        self.auditor = DatasetAuditor()

    def test_registry_has_16_sources(self):
        self.assertEqual(len(PUBLIC_SOURCES_REGISTRY), 16)

    def test_active_sources_sum_to_6600628(self):
        total = sum(s.valid_cleaned_records for s in PUBLIC_SOURCES_REGISTRY.values())
        self.assertEqual(total, 6600628)

    def test_gated_sources_are_zero(self):
        cmu = PUBLIC_SOURCES_REGISTRY["TRA-003"]
        self.assertEqual(cmu.valid_cleaned_records, 0)
        self.assertFalse(cmu.is_active)

        marble = PUBLIC_SOURCES_REGISTRY["MAS-001"]
        self.assertEqual(marble.valid_cleaned_records, 0)
        self.assertFalse(marble.is_active)

    def test_preview_samples_load_and_validate(self):
        # Sample test TRA-001, ROUTE-004, CACHE-001
        for sid in ["TRA-001", "ROUTE-004", "CACHE-001"]:
            samples = list(self.loader.iter_preview_samples(sid))
            self.assertGreater(len(samples), 0, f"No preview samples for {sid}")

    def test_full_audit_runs_cleanly(self):
        report = self.auditor.run_full_audit()
        self.assertEqual(report["overall_status"], "PASS")
        self.assertEqual(report["inventory_summary"]["total_verified_records"], 6600628)
        self.assertEqual(report["causal_isolation_audit"]["total_causal_violations"], 0)
        self.assertEqual(report["benchmark_isolation_audit"]["leakage_audit_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
