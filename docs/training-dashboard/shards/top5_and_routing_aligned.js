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
    "gpu_memory": "8948MiB",
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
  "census_reconciliation": {
    "legal_candidate_references": 4863900,
    "materialized_items": 1180742,
    "encoded_items": 1180742,
    "trained_items": 1180742,
    "distinct_trained_units": 166448,
    "distinct_candidate_units": 1389767,
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
      "env_001_002_status": "Strictly excluded from training candidate pool (S4 environment metadata: 10,821 rows isolated)"
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
