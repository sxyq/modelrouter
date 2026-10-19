#!/usr/bin/env python3
"""
public_sources.py - Public Datasets Registry & Preview Loader for ModelRouter.

Registers the 14 active public sources (6,600,628 records total) + 2 gated sources:
- Agent Trajectories: TRA-001, TRA-002, TRA-003 (gated), TRA-004
- Routing & Benchmarks: ROUTE-001, ROUTE-002, ROUTE-003 (eval holdout), ROUTE-004, ROUTE-005 (analysis only)
- Cache & Workload: CACHE-001, TIME-001
- Memory & Environment: ENV-001, ENV-002, MEM-003, MEM-005, MAS-001 (gated)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from modelrouter.datasets.causal_schema import PolicyTag, SupervisionType, LabelNature

logger = logging.getLogger("modelrouter.datasets.public_sources")

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
PREVIEW_ROOT = WORKSPACE_ROOT / "our-project" / "data" / "公开数据" / "数据预览"
MANIFEST_PATH = WORKSPACE_ROOT / "our-project" / "data" / "公开数据" / "manifest.json"


@dataclass
class SourceMetadata:
    source_id: str
    source_name: str
    official_origin: str
    license: str
    valid_cleaned_records: int
    supervision_type: SupervisionType
    label_nature: LabelNature
    policy_tag: PolicyTag
    batch_category: str
    directory_name: str
    is_active: bool = True
    gated_reason: Optional[str] = None


PUBLIC_SOURCES_REGISTRY: Dict[str, SourceMetadata] = {
    "TRA-001": SourceMetadata(
        source_id="TRA-001",
        source_name="Open-SWE-Traces",
        official_origin="https://huggingface.co/datasets/nvidia/Open-SWE-Traces",
        license="CC-BY-4.0",
        valid_cleaned_records=2075629,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.OBSERVED_ACTION,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 1: Agent轨迹",
        directory_name="TRA-001_Open-SWE-Traces",
    ),
    "TRA-002": SourceMetadata(
        source_id="TRA-002",
        source_name="SWE-smith Trajectories",
        official_origin="https://huggingface.co/datasets/SWE-bench/SWE-smith-trajectories",
        license="MIT",
        valid_cleaned_records=2331584,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.OBSERVED_ACTION,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 1: Agent轨迹",
        directory_name="TRA-002_SWE-smith",
    ),
    "TRA-003": SourceMetadata(
        source_id="TRA-003",
        source_name="CMU Agent Trajectories",
        official_origin="https://huggingface.co/datasets/cx-cmu/agent_trajectories",
        license="GATED / Terms Required",
        valid_cleaned_records=0,
        supervision_type=SupervisionType.UNSUPERVISED_OR_TIED,
        label_nature=LabelNature.GATED_INACCESSIBLE,
        policy_tag=PolicyTag.GATED_PENDING,
        batch_category="Batch 1: Agent轨迹",
        directory_name="TRA-003_CMU-Agent",
        is_active=False,
        gated_reason="HTTP 403 Forbidden on upstream repository",
    ),
    "TRA-004": SourceMetadata(
        source_id="TRA-004",
        source_name="AgentSuite multi_challenge",
        official_origin="https://huggingface.co/datasets/AgentSuite/multi_challenge-trajectories",
        license="Apache-2.0",
        valid_cleaned_records=41430,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.OBSERVED_ACTION,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 1: Agent轨迹",
        directory_name="TRA-004_AgentSuite",
    ),
    "ROUTE-001": SourceMetadata(
        source_id="ROUTE-001",
        source_name="LLMRouterBench",
        official_origin="https://huggingface.co/datasets/NPULH/LLMRouterBench",
        license="Open Source",
        valid_cleaned_records=548059,
        supervision_type=SupervisionType.S1_HUMAN_PREFERENCE,
        label_nature=LabelNature.POST_HOC_BENCHMARK_ORACLE,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 2: 路由评测",
        directory_name="ROUTE-001_LLMRouterBench",
    ),
    "ROUTE-002": SourceMetadata(
        source_id="ROUTE-002",
        source_name="RouterBench",
        official_origin="https://huggingface.co/datasets/withmartian/routerbench",
        license="CC-BY-4.0",
        valid_cleaned_records=36497,
        supervision_type=SupervisionType.S1_HUMAN_PREFERENCE,
        label_nature=LabelNature.POST_HOC_BENCHMARK_ORACLE,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 2: 路由评测",
        directory_name="ROUTE-002_RouterBench",
    ),
    "ROUTE-003": SourceMetadata(
        source_id="ROUTE-003",
        source_name="TwinRouterBench",
        official_origin="https://huggingface.co/datasets/Amorph/TwinRouterBench",
        license="Open Source",
        valid_cleaned_records=970,
        supervision_type=SupervisionType.S1_HUMAN_PREFERENCE,
        label_nature=LabelNature.POST_HOC_BENCHMARK_ORACLE,
        policy_tag=PolicyTag.EVAL_BENCHMARK_ONLY,
        batch_category="Batch 2: 路由评测",
        directory_name="ROUTE-003_TwinRouterBench",
    ),
    "ROUTE-004": SourceMetadata(
        source_id="ROUTE-004",
        source_name="Arena Human Preference 55k",
        official_origin="https://huggingface.co/datasets/lmarena-ai/arena-human-preference-55k",
        license="LMSYS Terms of Use",
        valid_cleaned_records=57477,
        supervision_type=SupervisionType.S1_HUMAN_PREFERENCE,
        label_nature=LabelNature.HUMAN_PREFERENCE,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 2: 路由评测",
        directory_name="ROUTE-004_Arena",
    ),
    "ROUTE-005": SourceMetadata(
        source_id="ROUTE-005",
        source_name="FindingTheRightFit",
        official_origin="https://huggingface.co/datasets/yixuanli97/finding-the-right-fit",
        license="Custom Research License (Prohibits Training/Distillation)",
        valid_cleaned_records=6204,
        supervision_type=SupervisionType.S1_HUMAN_PREFERENCE,
        label_nature=LabelNature.POST_HOC_BENCHMARK_ORACLE,
        policy_tag=PolicyTag.RESEARCH_ANALYSIS_ONLY,
        batch_category="Batch 2: 路由评测",
        directory_name="ROUTE-005_FindingTheRightFit",
    ),
    "CACHE-001": SourceMetadata(
        source_id="CACHE-001",
        source_name="Mooncake-FAST25",
        official_origin="https://github.com/kvcache-ai/Mooncake / FAST'25 release",
        license="Apache-2.0",
        valid_cleaned_records=39632,
        supervision_type=SupervisionType.S3_AUXILIARY_SYSTEM,
        label_nature=LabelNature.OBSERVED_REUSE_OPPORTUNITY,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 3: 缓存与时延",
        directory_name="CACHE-001_Mooncake",
    ),
    "TIME-001": SourceMetadata(
        source_id="TIME-001",
        source_name="BurstGPT",
        official_origin="https://github.com/HPMLL/BurstGPT",
        license="Open Source",
        valid_cleaned_records=1404294,
        supervision_type=SupervisionType.S3_AUXILIARY_SYSTEM,
        label_nature=LabelNature.OBSERVED_WORKLOAD,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 3: 缓存与时延",
        directory_name="TIME-001_BurstGPT",
    ),
    "ENV-001": SourceMetadata(
        source_id="ENV-001",
        source_name="SWE-Gym",
        official_origin="https://huggingface.co/datasets/SWE-Gym/SWE-Gym",
        license="MIT",
        valid_cleaned_records=2438,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.TASK_ENVIRONMENT,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 4: 记忆与环境",
        directory_name="ENV-001_SWE-Gym",
    ),
    "ENV-002": SourceMetadata(
        source_id="ENV-002",
        source_name="SWE-rebench-V2",
        official_origin="https://huggingface.co/datasets/nebius/SWE-rebench-V2",
        license="MIT",
        valid_cleaned_records=32079,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.TASK_ENVIRONMENT,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 4: 记忆与环境",
        directory_name="ENV-002_SWE-rebench-V2",
    ),
    "MEM-003": SourceMetadata(
        source_id="MEM-003",
        source_name="LongMemEval-V2",
        official_origin="https://huggingface.co/datasets/xiaowu0162/LongMemEval-V2",
        license="MIT",
        valid_cleaned_records=451,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.MEMORY_BENCHMARK,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 4: 记忆与环境",
        directory_name="MEM-003_LongMemEval-V2",
    ),
    "MEM-005": SourceMetadata(
        source_id="MEM-005",
        source_name="MemoryCraft",
        official_origin="https://huggingface.co/datasets/daven3/MemoryCraft",
        license="Open Source",
        valid_cleaned_records=23884,
        supervision_type=SupervisionType.S2_AGENT_OUTCOME,
        label_nature=LabelNature.MEMORY_BENCHMARK,
        policy_tag=PolicyTag.TRAIN_ROUTER_CANDIDATE,
        batch_category="Batch 4: 记忆与环境",
        directory_name="MEM-005_MemoryCraft",
    ),
    "MAS-001": SourceMetadata(
        source_id="MAS-001",
        source_name="MARBLE-MultiAgentBench",
        official_origin="https://github.com/ulab-uiuc/MARBLE",
        license="Unknown",
        valid_cleaned_records=0,
        supervision_type=SupervisionType.UNSUPERVISED_OR_TIED,
        label_nature=LabelNature.GATED_INACCESSIBLE,
        policy_tag=PolicyTag.GATED_PENDING,
        batch_category="Batch 4: 记忆与环境",
        directory_name="MAS-001_MARBLE",
        is_active=False,
        gated_reason="HTTP 401 Unauthorized on upstream repository",
    ),
}


class PublicDatasetLoader:
    """Loads and validates sample records for registered public datasets."""

    def __init__(self, preview_dir: Optional[Path] = None):
        self.preview_dir = preview_dir or PREVIEW_ROOT

    def get_source_metadata(self, source_id: str) -> Optional[SourceMetadata]:
        return PUBLIC_SOURCES_REGISTRY.get(source_id)

    def list_sources(self) -> List[SourceMetadata]:
        return list(PUBLIC_SOURCES_REGISTRY.values())

    def get_total_verified_records(self) -> int:
        return sum(s.valid_cleaned_records for s in PUBLIC_SOURCES_REGISTRY.values())

    def iter_preview_samples(self, source_id: str) -> Iterator[Dict[str, Any]]:
        meta = self.get_source_metadata(source_id)
        if not meta:
            raise KeyError(f"Unknown source ID: {source_id}")

        sample_file = self.preview_dir / meta.directory_name / "清洗样本.jsonl"
        if not sample_file.is_file():
            logger.warning(f"Preview sample file does not exist: {sample_file}")
            return

        with open(sample_file, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    yield record
                except json.JSONDecodeError as e:
                    logger.error(f"Malformed JSON in {sample_file}:{line_no}: {e}")

    def load_field_stats(self, source_id: str) -> Dict[str, Any]:
        meta = self.get_source_metadata(source_id)
        if not meta:
            raise KeyError(f"Unknown source ID: {source_id}")

        stat_file = self.preview_dir / meta.directory_name / "字段统计.json"
        if not stat_file.is_file():
            return {}
        with open(stat_file, "r", encoding="utf-8") as f:
            return json.load(f)
