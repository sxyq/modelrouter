window.LAYA_SHARD_TOP5_AND_ROUTING_ALIGNED = {
  "top5_checkpoints": [
    {
      "rank": 1,
      "checkpoint_id": "P0_B03_C01_QB_PB-e02",
      "run_id": "P0_B03_C01_QB_PB",
      "epoch": 2,
      "task_family": "S1",
      "assigned_layer": "L3",
      "s1_loss": 0.6039,
      "s1_accuracy": 0.6863,
      "s1_brier": 0.4165,
      "primary_score": 159.25,
      "internal_score": 159.25,
      "external_dev_score": null,
      "external_dev_status": "ROUTER_SERVING_NOT_READY",
      "selection_score": 159.25,
      "loadable": true,
      "parameters": 421293827,
      "size_bytes": 846196824,
      "retention_status": "RETAINED_BEST",
      "role": "S1 Accuracy Champion (Highest S1 Accuracy 68.63%)",
      "path": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/P0_B03_C01_QB_PB/checkpoints/epoch_02"
    },
    {
      "rank": 2,
      "checkpoint_id": "P0_B01_C01_QB_PB-e02",
      "run_id": "P0_B01_C01_QB_PB",
      "epoch": 2,
      "task_family": "S1",
      "assigned_layer": "L1",
      "s1_loss": 0.5998,
      "s1_accuracy": 0.6774,
      "s1_brier": 0.4128,
      "primary_score": 158.83,
      "internal_score": 158.83,
      "external_dev_score": null,
      "external_dev_status": "ROUTER_SERVING_NOT_READY",
      "selection_score": 158.83,
      "loadable": true,
      "parameters": 421293827,
      "size_bytes": 846196824,
      "retention_status": "RETAINED_TOP_K",
      "role": "S1 Loss & Brier Champion (Lowest S1 Loss 0.5998 & Brier 0.4128)",
      "path": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/P0_B01_C01_QB_PB/checkpoints/epoch_02"
    },
    {
      "rank": 3,
      "checkpoint_id": "P0_B03_C05_QB_PB-e02",
      "run_id": "P0_B03_C05_QB_PB",
      "epoch": 2,
      "task_family": "S1",
      "assigned_layer": "L3",
      "s1_loss": 0.6199,
      "s1_accuracy": 0.6756,
      "s1_brier": 0.4293,
      "primary_score": 157.66,
      "internal_score": 157.66,
      "external_dev_score": null,
      "external_dev_status": "ROUTER_SERVING_NOT_READY",
      "selection_score": 157.66,
      "loadable": true,
      "parameters": 421293827,
      "size_bytes": 846196824,
      "retention_status": "RETAINED_TOP_K",
      "role": "S1+S2 Multi-Task Balanced Champion (Routing + Agent Outcome 2:1)",
      "path": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/P0_B03_C05_QB_PB/checkpoints/epoch_02"
    },
    {
      "rank": 4,
      "checkpoint_id": "P0_B03_C08_QB_PB-e02",
      "run_id": "P0_B03_C08_QB_PB",
      "epoch": 2,
      "task_family": "S1",
      "assigned_layer": "L3",
      "s1_loss": 0.6067,
      "s1_accuracy": 0.6667,
      "s1_brier": 0.4196,
      "primary_score": 157.51,
      "internal_score": 157.51,
      "external_dev_score": null,
      "external_dev_status": "ROUTER_SERVING_NOT_READY",
      "selection_score": 157.51,
      "loadable": true,
      "parameters": 421293827,
      "size_bytes": 846196824,
      "retention_status": "RETAINED_TOP_K",
      "role": "S1+S3 Multi-Task Balanced Champion (Routing + Auxiliary Cache 2:1)",
      "path": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/P0_B03_C08_QB_PB/checkpoints/epoch_02"
    },
    {
      "rank": 5,
      "checkpoint_id": "P0_B02_C01_QB_PB-e02",
      "run_id": "P0_B02_C01_QB_PB",
      "epoch": 2,
      "task_family": "S1",
      "assigned_layer": "L2",
      "s1_loss": 0.6087,
      "s1_accuracy": 0.6595,
      "s1_brier": 0.4213,
      "primary_score": 157.46,
      "internal_score": 157.46,
      "external_dev_score": null,
      "external_dev_status": "ROUTER_SERVING_NOT_READY",
      "selection_score": 157.46,
      "loadable": true,
      "parameters": 421293827,
      "size_bytes": 846196824,
      "retention_status": "RETAINED_TOP_K",
      "role": "S1 Routing High-Performer (L2 20% Stratified Layer)",
      "path": "runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/P0_B02_C01_QB_PB/checkpoints/epoch_02"
    }
  ],
  "pinned_parents": [
    {
      "checkpoint_id": "R1-e01",
      "size_bytes": 846196824,
      "loadable": true,
      "reason": "Protected curriculum training parent"
    },
    {
      "checkpoint_id": "R2-e01",
      "size_bytes": 846196824,
      "loadable": true,
      "reason": "Protected curriculum training parent"
    }
  ],
  "active_resume": {
    "run_id": "F02",
    "status": "RUNNING",
    "gpu_name": "NVIDIA RTX A6000",
    "gpu_memory": "31157MiB / 49140MiB",
    "gpu_utilization": "100%",
    "daemon_pid": 2207051,
    "train_pid": 2287331,
    "current_epoch": "2 / 2",
    "current_chunk": "62 / 123",
    "current_step": "23588 / 31304",
    "current_loss": 0.5174,
    "consumed_items": 1509599,
    "total_items": 2003390,
    "progress_pct": "75.35%",
    "eta_remaining": "~4.3 hours (estimated completion ~14:20 Oct 14)",
    "reason": "Active GPU training job protected from pruning"
  },
  "cleanup_summary": {
    "total_scanned_dirs": 129,
    "pruned_dirs": 122,
    "retained_physical_models": 7,
    "freed_bytes": 103249108992,
    "freed_gib": 96.16,
    "disk_free_available_bytes": 1239149690880,
    "disk_free_pct": 34.6
  },
  "autonomous_training_v4": {
    "protocol_version": "AUTONOMOUS-TRAINING-V4",
    "execution_mode": "HEADLESS_DAEMON_ON_SERVER",
    "sole_training_entry": "router_data/run_full_graded_queue.py --mode continuous_full_coverage",
    "three_tier_benchmarks": {
      "internal_validation": {
        "tier": "INTERNAL_VALIDATION",
        "description": "Fixed internal validation set evaluated after every epoch (S1 561 items, S2 337 items, S3 1,397 items)",
        "status": "ACTIVE_CONTINUOUS",
        "s1_baseline_loss": 0.6596,
        "s1_baseline_acc": 0.5793,
        "weight_in_selection": "80% (when DEV evaluated) / 100% (when DEV unready)"
      },
      "canary": {
        "tier": "CANARY",
        "benchmark": "ENV-004: Terminal-Bench 2.0 (Canary Subset)",
        "task_count": 12,
        "status": "PASSED_SMOKE_TEST",
        "description": "Parser, schema verification, and container connectivity check"
      },
      "external_dev": {
        "tier": "EXTERNAL_DEV",
        "benchmark": "ENV-004: Terminal-Bench 2.0 (Dev Subset)",
        "task_count": 48,
        "status": "ROUTER_SERVING_NOT_READY",
        "reason": "Router serving endpoint and agent harness await deployment; pass rate not fabricated (0.0% / NOT_EVALUATED)",
        "trigger": "Evaluated exclusively on Top-5 candidates and champions",
        "weight_in_selection": "20% (when live evaluation completes)"
      },
      "final_test": {
        "tier": "FINAL_TEST",
        "benchmark": "ENV-004: Terminal-Bench 2.0 (Test Subset)",
        "task_count": 100,
        "status": "PERMANENTLY_SEALED",
        "access_weight": "0.00 (Permanently air-gapped from training & model selection)"
      }
    },
    "composite_score_formula": "selection_score = 0.80 * internal + 0.20 * external_dev (defaults to 1.00 * internal when external_dev status is ROUTER_SERVING_NOT_READY)",
    "long_term_stages": [
      {"stage": 1, "name": "监督组合与路由对齐基线", "runs": "ALGN_01 (S1), ALGN_02 (S1+S2), ALGN_03 (S1+S3), ALGN_04 (S1+S2+S3)", "status": "QUEUED"},
      {"stage": 2, "name": "数据规模阶梯", "runs": "10% (F08), 25% (F09), 50% (F10), 100% (F07)", "status": "QUEUED"},
      {"stage": 3, "name": "分层全量与跨层覆盖", "runs": "L1 (F01), L2 (F02), L3 (F03), L4 (F04), L1+L2 (F05), L1..L3 (F06), L1..L4 (F07)", "status": "IN_PROGRESS (F02 Epoch 2/2 Chunk 62/123 · 75.3% 累计完成 · Loss 0.5174)"},
      {"stage": 4, "name": "部分比例与分位抽样", "runs": "F11..F16 嵌套子集对比", "status": "QUEUED"},
      {"stage": 5, "name": "课程学习与能力渐进", "runs": "Base -> L1 -> L1+L2 -> L1..L4 (F17..F20)", "status": "QUEUED"},
      {"stage": 6, "name": "多 Seed 与状态变量消融", "runs": "Seed 42/43/44, V1..V8 状态变量消融", "status": "QUEUED"}
    ]
  },
  "census_reconciliation": {
    "legal_candidate_references": 4863900,
    "materialized_items": 1180742,
    "encoded_items": 1180742,
    "trained_items": 1180742,
    "distinct_trained_units": 166448,
    "distinct_candidate_units": 1344240,
    "class_breakdown": {
      "S1": 31766,
      "S2": 3537955,
      "S3": 1294179,
      "S4": 0
    },
    "source_breakdown": {
      "TRA-001": 1673528,
      "TRA-002": 1864427,
      "ROUTE-004": 31766,
      "CACHE-001": 28714,
      "TIME-001": 1122577,
      "OWN-002": 142888
    },
    "quantile_breakdown": {
      "L1": 485210,
      "L2": 1001005,
      "L3": 1466724,
      "L4": 1910961
    },
    "isolation_audit": {
      "train_val_overlap": 0,
      "train_test_overlap": 0,
      "test_status": "Strictly Sealed & Air-Gapped",
      "unit_split_integrity": "Verified 100% disjoint split assignments (quality_v2 unique unit mapping invariant holds with 0 conflicts)",
      "route_001_002_license_status": "Strictly excluded from training candidate pool (LICENSE_PENDING: 152,524 rows isolated)",
      "env_001_002_status": "Strictly excluded from training candidate pool (S4 environment metadata: 10,821 rows isolated)",
      "env_004_status": "ENV-004 Terminal-Bench 2.0 strictly isolated from 6.6M training pool (0 training leakage; 12 Canary / 48 Dev / 100 Sealed Test)"
    }
  },
  "routing_aligned_v2": {
    "views": [
      {
        "id": "STATIC_MODEL_PREFERENCE",
        "name": "静态模型路由偏好 (S1)",
        "source": "ROUTE-004",
        "records": 31766,
        "target": "human_pairwise_preference",
        "status": "READY"
      },
      {
        "id": "OBSERVED_AGENT_OUTCOME",
        "name": "观测智能体行为与结果 (S2)",
        "source": "TRA-001, TRA-002",
        "records": 3537955,
        "target": "observed_action / decision_success",
        "status": "READY"
      },
      {
        "id": "RESOURCE_CACHE_AUXILIARY",
        "name": "资源消耗与前缀缓存辅助 (S3)",
        "source": "TIME-001, CACHE-001, OWN-002",
        "records": 1294179,
        "target": "request_response_tokens / cache_tier",
        "status": "READY"
      },
      {
        "id": "JOINT_ROUTING_COMPARISON",
        "name": "联合路由多目标比较 (JOINT)",
        "source": "None (跨来源缺失并发客观真值)",
        "records": 0,
        "target": "None",
        "status": "DATA_NOT_READY (学术诚实拒绝伪造虚假联合标签)"
      }
    ],
    "ablation_queue": [
      {
        "run_id": "ALGN_01_S1",
        "classes": "S1 (单任务路由)",
        "layers": "L1-L4 (100%全覆盖)",
        "ratio": "1.0",
        "description": "单任务路由偏好基线"
      },
      {
        "run_id": "ALGN_02_S1_S2",
        "classes": "S1 + S2 (路由 + 智能体)",
        "layers": "L1-L4 (100%全覆盖)",
        "ratio": "2:1 平衡采样",
        "description": "路由偏好与智能体执行联合训练"
      },
      {
        "run_id": "ALGN_03_S1_S3",
        "classes": "S1 + S3 (路由 + 资源缓存)",
        "layers": "L1-L4 (100%全覆盖)",
        "ratio": "2:1 平衡采样",
        "description": "路由偏好与推理资源消耗联合训练"
      },
      {
        "run_id": "ALGN_04_S1_S2_S3",
        "classes": "S1 + S2 + S3 (三任务联合)",
        "layers": "L1-L4 (100%全覆盖)",
        "ratio": "2:1:1 平衡采样",
        "description": "三视角多任务平衡消融训练"
      }
    ]
  }
};
