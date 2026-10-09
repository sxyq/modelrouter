#!/usr/bin/env python3
"""
prepare_router_data.py - ModelRouter 数据准备与 Kev JSONL 转换入口

唯一执行链第一阶段：
公开数据读取 -> 数据清洗 -> 可信监督标签 -> Kev JSONL 数据集划分

严格遵循科研数据处理规范：
1. 真实对应关系：保留原始 source、row_id 与 session 溯源。
2. 任务/会话隔离：按会话边界（默认 300 秒无活动切分）划分 Train/Val/Test，杜绝跨划分泄漏。
3. 决策前特征隔离：绝不将输出 token、耗时、实际费用或事后成功标签混入 pre-decision state。
4. 真实标签：choice、noul、score 标签均基于真实观测与事实，无法确定的不编造。
5. 零过度工程：单文件、直接执行、终端实时展示必要统计。
"""

import argparse
import csv
import json
import os
import random
from datetime import datetime
from collections import Counter


def parse_args():
    parser = argparse.ArgumentParser(description="ModelRouter 数据准备与 Kev JSONL 生成")
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
    parser.add_argument(
        "--output-dir",
        default="data/kev",
        help="输出 Kev JSONL 文件目录",
    )
    parser.add_argument(
        "--session-gap-seconds",
        type=int,
        default=300,
        help="按时间间隔推断任务/会话边界（秒）",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=25000,
        help="最大处理样本数（0 表示全量处理）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子",
    )
    return parser.parse_args()


def load_cch_cost_priors(cch_path):
    """读取 CCH 价格先验，用于构建客观的费用分级 (Score) 标签"""
    priors = {}
    if not os.path.exists(cch_path):
        return priors

    with open(cch_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            model = row.get("model", "").strip()
            effort = row.get("reasoning_effort", "").strip() or "(unspecified)"
            avg_cost = row.get("avg_cost_usd")
            if avg_cost:
                try:
                    priors[(model, effort)] = float(avg_cost)
                except ValueError:
                    pass
    return priors


def get_cost_tier(cost_usd):
    """基于 USD 先验划定客观的三档费用评分"""
    if cost_usd is None:
        return "unspecified"
    if cost_usd < 0.05:
        return "budget"
    elif cost_usd < 0.20:
        return "standard"
    else:
        return "premium"


def main():
    args = parse_args()
    random.seed(args.seed)

    print("==================================================")
    print("  ModelRouter 唯一执行链：数据准备 (prepare_router_data)")
    print("==================================================")
    print(f"[*] 读取 Blog 调用数据: {args.blog_file}")
    print(f"[*] 读取 CCH 先验数据:   {args.cch_file}")
    print(f"[*] 目标输出目录:       {args.output_dir}")

    # 1. 加载 CCH 成本先验
    cch_priors = load_cch_cost_priors(args.cch_file)
    print(f"[+] 加载 CCH (model, effort) 成本先验: {len(cch_priors)} 组")

    # 2. 读取并清洗 Blog 数据
    if not os.path.exists(args.blog_file):
        raise FileNotFoundError(f"找不到数据文件: {args.blog_file}")

    total_read = 0
    anomalies = Counter()
    valid_records = []

    last_dt = None
    current_session_id = 0

    with open(args.blog_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_read += 1

            # 异常检查 1: 状态必须为 success
            status = row.get("status", "").strip().lower()
            if status != "success":
                anomalies["non_success_status"] += 1
                continue

            # 异常检查 2: prompt_tokens 必须为有效正整数
            try:
                prompt_tokens = int(row.get("prompt_tokens", 0))
                if prompt_tokens <= 0:
                    anomalies["zero_or_negative_prompt_tokens"] += 1
                    continue
            except (ValueError, TypeError):
                anomalies["invalid_prompt_tokens"] += 1
                continue

            # 异常检查 3: 时间格式解析
            cst_str = row.get("created_at_cst", "")
            try:
                dt = datetime.fromisoformat(cst_str[:19])
            except Exception:
                anomalies["invalid_timestamp"] += 1
                continue

            # 划分会话 / 任务边界
            if last_dt is None or (dt - last_dt).total_seconds() > args.session_gap_seconds:
                current_session_id += 1
            last_dt = dt

            model_norm = row.get("model_normalized", "").strip()
            effort = row.get("reasoning_effort", "").strip() or "(unspecified)"
            if not model_norm:
                anomalies["missing_model"] += 1
                continue

            cache_read = int(row.get("cache_read_tokens", 0) or 0)
            is_stream = row.get("is_stream", "").strip().lower() == "true"

            valid_records.append({
                "source": row.get("source", "sxyq_blog"),
                "row_id": row.get("row_id"),
                "session_id": f"task_session_{current_session_id:05d}",
                "timestamp": cst_str,
                "hour_of_day": dt.hour,
                "prompt_tokens": prompt_tokens,
                "cache_read_tokens": cache_read,
                "is_stream": is_stream,
                "model_norm": model_norm,
                "effort": effort,
                "action": f"{model_norm}:{effort}",
            })

            if args.max_samples > 0 and len(valid_records) >= args.max_samples:
                break

    print(f"\n[+] 原始数据读取总数: {total_read} 条")
    print(f"[+] 有效清洗样本总数: {len(valid_records)} 条")
    if anomalies:
        print("[!] 过滤/异常原因分布:")
        for reason, cnt in anomalies.most_common():
            print(f"    - {reason}: {cnt} 条")

    # 3. 统计高频动作候选空间 (Choice options)
    action_counts = Counter(r["action"] for r in valid_records)
    # 取最常见的 Top 6 作为统一 Choice 候选池
    top_candidates = [act for act, _ in action_counts.most_common(6)]
    print("\n[+] 统一 Model × Effort 候选池 (Top 6):")
    for act, cnt in action_counts.most_common(6):
        pct = (cnt / len(valid_records)) * 100
        print(f"    - {act:<30} 频次: {cnt:<6} ({pct:.1f}%)")

    # 4. 构建 Kev JSONL 样本 (严禁泄露未来执行结果)
    kev_samples = []
    choice_counter = Counter()
    noul_effort_counter = Counter()
    noul_cache_counter = Counter()
    score_counter = Counter()

    for item in valid_records:
        # Pre-decision State: 决策前上下文
        state_repr = (
            f"Context: prompt_tokens={item['prompt_tokens']}, "
            f"is_stream={item['is_stream']}, hour={item['hour_of_day']}. "
            f"Observed prompt cache capability: active."
        )

        actual_action = item["action"]
        # 如果实际动作在 Top 候选池中，则保留为真实 Choice 标签；否则标记为 other
        choice_label = actual_action if actual_action in top_candidates else "other"
        choice_options = top_candidates + (["other"] if "other" not in top_candidates else [])

        # Noul 1: 是否需要高深度推理 (high / xhigh / max)
        is_high_effort = item["effort"] in ["high", "xhigh", "max"]

        # Noul 2: 是否观察到缓存读取命中 (>0)
        is_cache_hit = item["cache_read_tokens"] > 0

        # Score: 成本等级 (依据 CCH 价格先验)
        cost_val = cch_priors.get((item["model_norm"], item["effort"]))
        tier_label = get_cost_tier(cost_val)

        choice_counter[choice_label] += 1
        noul_effort_counter[is_high_effort] += 1
        noul_cache_counter[is_cache_hit] += 1
        score_counter[tier_label] += 1

        sample = {
            "provenance": {
                "source": item["source"],
                "row_id": item["row_id"],
                "task_session_id": item["session_id"],
                "timestamp": item["timestamp"],
            },
            "state": state_repr,
            "questions": {
                "model_effort_choice": {
                    "type": "choice",
                    "instructions": "Select the appropriate (model, reasoning_effort) action.",
                    "options": choice_options,
                    "label": choice_label,
                },
                "high_reasoning_effort": {
                    "type": "noul",
                    "instructions": "Does this query require high or maximum reasoning effort?",
                    "label": is_high_effort,
                },
                "cache_read_hit": {
                    "type": "noul",
                    "instructions": "Will this request observe prompt cache read hits?",
                    "label": is_cache_hit,
                },
                "cost_tier": {
                    "type": "score",
                    "instructions": "Expected cost tier based on CCH benchmark prior.",
                    "levels": ["budget", "standard", "premium", "unspecified"],
                    "label": tier_label,
                },
            },
        }
        kev_samples.append((item["session_id"], sample))

    # 5. 按任务/会话隔离划分 Train / Val / Test (70% / 15% / 15%)
    all_sessions = sorted(list(set(s_id for s_id, _ in kev_samples)))
    random.shuffle(all_sessions)

    n_sessions = len(all_sessions)
    n_train = int(n_sessions * 0.70)
    n_val = int(n_sessions * 0.15)

    train_sess = set(all_sessions[:n_train])
    val_sess = set(all_sessions[n_train : n_train + n_val])
    test_sess = set(all_sessions[n_train + n_val :])

    train_data = [s for s_id, s in kev_samples if s_id in train_sess]
    val_data = [s for s_id, s in kev_samples if s_id in val_sess]
    test_data = [s for s_id, s in kev_samples if s_id in test_sess]

    # 6. 保存划分结果
    os.makedirs(args.output_dir, exist_ok=True)
    train_path = os.path.join(args.output_dir, "train.jsonl")
    val_path = os.path.join(args.output_dir, "val.jsonl")
    test_path = os.path.join(args.output_dir, "test.jsonl")

    for path, dataset in [(train_path, train_data), (val_path, val_data), (test_path, test_data)]:
        with open(path, "w", encoding="utf-8") as f:
            for s in dataset:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    # 7. 打印实验数据准备核心统计
    print("\n[+] 数据集划分结果（会话级无泄漏划分）:")
    print(f"    - 会话总数: {n_sessions} (Train: {len(train_sess)}, Val: {len(val_sess)}, Test: {len(test_sess)})")
    print(f"    - Train 样本数: {len(train_data):<6} ({len(train_data)/len(kev_samples)*100:.1f}%) -> {train_path}")
    print(f"    - Val   样本数: {len(val_data):<6} ({len(val_data)/len(kev_samples)*100:.1f}%) -> {val_path}")
    print(f"    - Test  样本数: {len(test_data):<6} ({len(test_data)/len(kev_samples)*100:.1f}%) -> {test_path}")

    print("\n[+] 标签类别与真实分布 (全量有效样本):")
    print("    [Choice] model_effort_choice:")
    for k, v in choice_counter.most_common():
        print(f"      * {k:<25}: {v:<6} ({v/len(kev_samples)*100:.1f}%)")
    print("    [Noul] high_reasoning_effort (true/false):")
    for k, v in noul_effort_counter.items():
        print(f"      * {str(k):<25}: {v:<6} ({v/len(kev_samples)*100:.1f}%)")
    print("    [Noul] cache_read_hit (true/false):")
    for k, v in noul_cache_counter.items():
        print(f"      * {str(k):<25}: {v:<6} ({v/len(kev_samples)*100:.1f}%)")
    print("    [Score] cost_tier:")
    for k, v in score_counter.most_common():
        print(f"      * {k:<25}: {v:<6} ({v/len(kev_samples)*100:.1f}%)")

    print("\n[✓] 第一阶段数据准备成功完成！已生成 Kev 标准训练与评估格式。")


if __name__ == "__main__":
    main()
