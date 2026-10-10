#!/usr/bin/env python3
"""
prepare_router_data.py - ModelRouter 数据准备与 Kev/规范化处理唯一入口

严格遵循科研规范：
1. 真实对应关系：保留原始 source_id、instance_id、task_id、repo、step_index。
2. 决策前特征隔离：绝不将输出 token、耗时、实际费用或事后成功标签混入 pre_decision_state。
3. 真实监督标签：绝不人为推断伪造“最优模型”或“物理缓存命中”；
   标签明确标为 OBSERVED_ACTION / HUMAN_PREFERENCE / POST_HOC_EVALUATOR / UNKNOWN。
4. 任务/会话隔离：按真实任务 (instance_id/task_name) 隔离划分 Train/Val/Test，杜绝跨划分泄漏。
5. 唯一正式主脚本，不设第二套清洗流水线。
"""

import argparse
import os

from router_data.cache_time import run_cache_time_batch
from router_data.env_memory import run_mem_mas_env_batch
from router_data.route import run_route_batch
from router_data.tra import run_tra_batch
from router_data.views import build_unified_training_and_evaluation_views


def parse_args():
    parser = argparse.ArgumentParser(description="ModelRouter 唯一数据清洗与特征提取入口")
    parser.add_argument(
        "--mode",
        choices=["blog", "tra", "route", "cache_time", "mem_mas_env", "public", "views", "all"],
        default="public",
        help="执行模式: blog (私有数据), tra (Batch 1: Agent轨迹), route (Batch 2: 路由比较), cache_time (Batch 3: 缓存时间), mem_mas_env (Batch 4: 记忆协作环境), public (全部公开数据并生成训练视图), views (仅构建训练视图与Kev划分), all (全部私有+公开+训练视图)",
    )
    # 路径配置
    parser.add_argument(
        "--raw-root",
        default="data/公开数据/原始数据",
        help="原始数据根目录",
    )
    parser.add_argument(
        "--cleaned-root",
        default="data/公开数据/清洗数据",
        help="清洗数据根目录",
    )
    parser.add_argument(
        "--preview-root",
        default="data/公开数据/数据预览",
        help="轻量预览与审查报告输出目录",
    )
    parser.add_argument(
        "--report-root",
        default="data/公开数据/清洗报告",
        help="全量统计与报告输出目录",
    )
    parser.add_argument(
        "--kev-root",
        default="data/kev/公开数据",
        help="Kev 格式输出目录",
    )
    parser.add_argument(
        "--laya-root",
        default="data/laya/公开数据",
        help="Laya 格式输出目录",
    )
    parser.add_argument(
        "--stage1-out-dir",
        default="runs/MR-STAGE1-20261010/stage1_pure_static_scheme_b_fixed",
        help="Stage 1 纯静态 Scheme B 修复版输出目录（不覆盖历史冻结目录）",
    )
    parser.add_argument(
        "--manifest-path",
        default="",
        help="机器可读 Manifest 输出路径（默认生成于 preview-root 同级目录的 manifest.json）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子",
    )
    # Blog / CCH 参数
    parser.add_argument(
        "--blog-file",
        default="our-project/data/cleaned/sxyq-blog-gpt-usage-cleaned.csv",
        help="Blog GPT 清洗数据路径",
    )
    parser.add_argument(
        "--cch-file",
        default="our-project/data/source/cch-model-cost-cache-statistics.csv",
        help="CCH 聚合统计数据路径",
    )
    return parser.parse_args()



def run_blog_pipeline(args):
    print("\n" + "=" * 60)
    print("  [Blog Mode] SXYQ Blog GPT 与 CCH 历史数据处理")
    print("=" * 60)
    if not os.path.exists(args.blog_file):
        print(f"[!] 找不到 Blog 数据文件: {args.blog_file}，跳过。")
        return
    print(f"[*] Blog 数据: {args.blog_file}, CCH 数据: {args.cch_file}")



def main():
    args = parse_args()
    if args.mode == "blog":
        run_blog_pipeline(args)
    elif args.mode == "tra":
        run_tra_batch(args)
    elif args.mode == "route":
        run_route_batch(args)
    elif args.mode == "cache_time":
        run_cache_time_batch(args)
    elif args.mode == "mem_mas_env":
        run_mem_mas_env_batch(args)
    elif args.mode == "views":
        build_unified_training_and_evaluation_views(args)
    elif args.mode == "public":
        print("\n" + "=" * 70)
        print("  ModelRouter 公开数据全量清洗与规范化流水线 (--mode public)")
        print("  包含: Batch 1 (TRA), Batch 2 (ROUTE), Batch 3 (CACHE/TIME), Batch 4 (ENV/MEM/MAS)")
        print("  以及: 统一训练视图构建与 Kev 格式任务级划分")
        print("=" * 70)
        run_tra_batch(args)
        run_route_batch(args)
        run_cache_time_batch(args)
        run_mem_mas_env_batch(args)
        build_unified_training_and_evaluation_views(args)
    elif args.mode == "all":
        run_blog_pipeline(args)
        run_tra_batch(args)
        run_route_batch(args)
        run_cache_time_batch(args)
        run_mem_mas_env_batch(args)
        build_unified_training_and_evaluation_views(args)



if __name__ == "__main__":
    main()
