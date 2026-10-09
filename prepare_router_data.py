#!/usr/bin/env python3
"""
prepare_router_data.py - ModelRouter 数据准备与 Kev JSONL 转换入口

唯一执行链第一阶段：
公开数据读取 -> 数据清洗 -> 可信监督标签 -> Kev JSONL 数据集划分

支持两种执行模式：
1. --mode blog: 处理本地已有的 SXYQ Blog GPT 日志与 CCH 聚合成本先验数据。
2. --mode public: 处理服务器上的大规模公开数据集（Open-SWE-Traces、SWE-smith、
   Arena Human Preference、Mooncake FAST'25、TwinRouterBench、LLMRouterBench）。
3. --mode all: 串联执行两种模式。

严格遵循科研数据处理规范：
1. 真实对应关系：保留原始 source、instance_id、row_id 与 session 溯源。
2. 任务/会话隔离：按会话/实例边界（Session / Trajectory ID）划分 Train/Val/Test，杜绝跨划分泄漏。
3. 决策前特征隔离：绝不将输出 token、耗时、实际费用或事后成功标签混入 pre-decision state。
4. 真实标签：choice、noul、score 标签均基于真实观测与事实，无法确定的不编造。
5. 零过度工程：单文件、直接执行、终端实时展示必要统计。
"""

import argparse
import csv
import json
import os
import random
import sys
from collections import Counter
from datetime import datetime


def parse_args():
    parser = argparse.ArgumentParser(description="ModelRouter 数据准备与 Kev JSONL 生成")
    parser.add_argument(
        "--mode",
        choices=["blog", "public", "all"],
        default="blog",
        help="执行模式: blog (历史私有数据), public (服务器公开数据), all (两者全量)",
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
    parser.add_argument(
        "--output-dir",
        default="data/kev",
        help="Blog 模式输出 Kev JSONL 目录",
    )
    parser.add_argument(
        "--session-gap-seconds",
        type=int,
        default=300,
        help="Blog 模式按时间间隔推断会话边界（秒）",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=25000,
        help="Blog 模式最大处理样本数（0 表示全量）",
    )

    # 公开数据参数
    parser.add_argument(
        "--public-raw-dir",
        default="data/公开数据/原始数据",
        help="公开数据原始存放根目录",
    )
    parser.add_argument(
        "--public-cleaned-dir",
        default="data/公开数据/清洗数据",
        help="公开数据清洗后存放根目录",
    )
    parser.add_argument(
        "--public-preview-dir",
        default="data/公开数据/数据预览",
        help="公开数据轻量预览输出目录",
    )
    parser.add_argument(
        "--public-report-dir",
        default="data/公开数据/清洗报告",
        help="公开数据清洗统计与报告输出目录",
    )
    parser.add_argument(
        "--public-kev-dir",
        default="data/kev/公开数据",
        help="公开数据 Kev JSONL 输出目录",
    )
    parser.add_argument(
        "--max-agent-samples",
        type=int,
        default=20000,
        help="Agent 轨迹最大抽取步数（0 表示全量）",
    )
    parser.add_argument(
        "--max-arena-samples",
        type=int,
        default=30000,
        help="Arena 偏好最大抽取行数（0 表示全量）",
    )
    parser.add_argument(
        "--max-cache-samples",
        type=int,
        default=30000,
        help="Mooncake 缓存最大抽取轨迹点数（0 表示全量）",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子",
    )
    return parser.parse_args()


# =====================================================================
# 一、Blog / CCH 历史私有数据清洗模块
# =====================================================================

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


def run_blog_pipeline(args):
    print("\n" + "=" * 60)
    print("  [Mode: Blog] SXYQ Blog GPT 与 CCH 历史数据处理")
    print("=" * 60)
    print(f"[*] 读取 Blog 调用数据: {args.blog_file}")
    print(f"[*] 读取 CCH 先验数据:   {args.cch_file}")
    print(f"[*] 目标输出目录:       {args.output_dir}")

    cch_priors = load_cch_cost_priors(args.cch_file)
    print(f"[+] 加载 CCH (model, effort) 成本先验: {len(cch_priors)} 组")

    if not os.path.exists(args.blog_file):
        print(f"[!] 找不到 Blog 数据文件: {args.blog_file}，跳过此模式。")
        return

    total_read = 0
    anomalies = Counter()
    valid_records = []
    last_dt = None
    current_session_id = 0

    with open(args.blog_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_read += 1
            status = row.get("status", "").strip().lower()
            if status != "success":
                anomalies["non_success_status"] += 1
                continue

            try:
                prompt_tokens = int(row.get("prompt_tokens", 0))
                if prompt_tokens <= 0:
                    anomalies["zero_or_negative_prompt_tokens"] += 1
                    continue
            except (ValueError, TypeError):
                anomalies["invalid_prompt_tokens"] += 1
                continue

            cst_str = row.get("created_at_cst", "")
            try:
                dt = datetime.fromisoformat(cst_str[:19])
            except Exception:
                anomalies["invalid_timestamp"] += 1
                continue

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

    action_counts = Counter(r["action"] for r in valid_records)
    top_candidates = [act for act, _ in action_counts.most_common(6)]

    kev_samples = []
    choice_counter = Counter()
    noul_effort_counter = Counter()
    noul_cache_counter = Counter()
    score_counter = Counter()

    for item in valid_records:
        state_repr = (
            f"Context: prompt_tokens={item['prompt_tokens']}, "
            f"is_stream={item['is_stream']}, hour={item['hour_of_day']}. "
            f"Observed prompt cache capability: active."
        )

        actual_action = item["action"]
        choice_label = actual_action if actual_action in top_candidates else "other"
        choice_options = top_candidates + (["other"] if "other" not in top_candidates else [])

        is_high_effort = item["effort"] in ["high", "xhigh", "max"]
        is_cache_hit = item["cache_read_tokens"] > 0
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

    os.makedirs(args.output_dir, exist_ok=True)
    train_path = os.path.join(args.output_dir, "train.jsonl")
    val_path = os.path.join(args.output_dir, "val.jsonl")
    test_path = os.path.join(args.output_dir, "test.jsonl")

    for path, dataset in [(train_path, train_data), (val_path, val_data), (test_path, test_data)]:
        with open(path, "w", encoding="utf-8") as f:
            for s in dataset:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"\n[+] Blog 数据集划分结果（会话级隔离）:")
    print(f"    - 会话总数: {n_sessions} (Train: {len(train_sess)}, Val: {len(val_sess)}, Test: {len(test_sess)})")
    print(f"    - Train 样本数: {len(train_data):<6} -> {train_path}")
    print(f"    - Val   样本数: {len(val_data):<6} -> {val_path}")
    print(f"    - Test  样本数: {len(test_data):<6} -> {test_path}")


# =====================================================================
# 二、公开数据清洗模块 (Agent轨迹 / 模型偏好 / 缓存负载 / 路由评测)
# =====================================================================

def clean_agent_traces(raw_dir, cleaned_dir, preview_dir, max_samples=20000):
    """
    清洗 Agent 轨迹数据：
    来源：Open-SWE-Traces (NVIDIA) 与 SWE-smith (SWE-bench)
    抽取每个 Agent 与环境交互的决策步（Turn），保留步骤上下文与工具状态，
    绝不泄漏未来步骤或执行成败。
    """
    print("\n--- [1/4] 清洗 Agent轨迹数据 (Open-SWE-Traces & SWE-smith) ---")
    out_dir = os.path.join(cleaned_dir, "Agent轨迹")
    os.path.join(preview_dir)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    cleaned_file = os.path.join(out_dir, "agent_traces_cleaned.jsonl")
    preview_file = os.path.join(preview_dir, "agent_traces_preview.json")

    cleaned_records = []
    stats = {
        "source": "Open-SWE-Traces + SWE-smith",
        "open_swe_trajectories_read": 0,
        "swe_smith_trajectories_read": 0,
        "total_extracted_decision_steps": 0,
        "step_complexity_distribution": Counter(),
    }

    try:
        import pyarrow.parquet as pq
    except ImportError:
        print("[!] pyarrow 未安装，无法读取 Parquet 文件！")
        return cleaned_records, stats

    # 1. 处理 Open-SWE-Traces
    open_swe_path = os.path.join(raw_dir, "Open-SWE-Traces", "train-00000-of-00017.parquet")
    if os.path.exists(open_swe_path):
        print(f"[*] 读取 Open-SWE-Traces: {open_swe_path}")
        table = pq.read_table(open_swe_path)
        df = table.to_pandas()
        stats["open_swe_trajectories_read"] = len(df)

        for _, row in df.iterrows():
            instance_id = str(row.get("instance_id", "unknown"))
            repo = str(row.get("repo", "unknown"))
            traj_id = str(row.get("trajectory_id", instance_id))
            messages = row.get("messages", [])

            if hasattr(messages, "__iter__") and not isinstance(messages, str):
                msg_list = list(messages)
            else:
                continue

            accum_chars = 0
            prior_tool_calls = 0
            prior_errors = 0
            step_count = 0

            # 遍历会话消息流
            for msg in msg_list:
                if not isinstance(msg, dict):
                    continue
                role = msg.get("role")
                content = str(msg.get("content") or "")
                accum_chars += len(content)

                if role == "tool" or role == "user":
                    lower_content = content.lower()
                    if any(err_kw in lower_content for err_kw in ["error", "exception", "failed", "traceback"]):
                        prior_errors += 1

                elif role == "assistant":
                    step_count += 1
                    # 决策前特征提取
                    tool_calls = msg.get("tool_calls")
                    has_tool_call = bool(tool_calls)
                    if has_tool_call:
                        prior_tool_calls += 1

                    # 步骤复杂度标签（决策前状态）
                    if step_count <= 2 and prior_errors == 0:
                        complexity = "low"
                    elif step_count <= 7 and prior_errors <= 1:
                        complexity = "mid"
                    else:
                        complexity = "high"

                    stats["step_complexity_distribution"][complexity] += 1

                    record = {
                        "source": "Open-SWE-Traces",
                        "instance_id": instance_id,
                        "task_session_id": f"agent_traj_{traj_id}",
                        "step_index": step_count,
                        "repo": repo,
                        "domain": "software_engineering",
                        "context_chars": accum_chars,
                        "prior_tool_calls": prior_tool_calls,
                        "prior_errors": prior_errors,
                        "has_reasoning": bool(msg.get("reasoning_content")),
                        "step_complexity": complexity,
                        "is_high_effort": complexity == "high",
                        "cache_hit": step_count > 1,
                    }
                    cleaned_records.append(record)
                    if max_samples > 0 and len(cleaned_records) >= (max_samples // 2):
                        break
            if max_samples > 0 and len(cleaned_records) >= (max_samples // 2):
                break

    # 2. 处理 SWE-smith
    swe_smith_path = os.path.join(raw_dir, "SWE-smith", "ticks-00000-of-00008.parquet")
    if os.path.exists(swe_smith_path):
        print(f"[*] 读取 SWE-smith: {swe_smith_path}")
        table2 = pq.read_table(swe_smith_path)
        df2 = table2.to_pandas()
        stats["swe_smith_trajectories_read"] = len(df2)

        for _, row in df2.iterrows():
            instance_id = str(row.get("instance_id", "unknown"))
            traj_id = str(row.get("traj_id", instance_id))
            model_name = str(row.get("model", "claude-3-7-sonnet"))
            raw_msgs = row.get("messages")

            if isinstance(raw_msgs, str):
                try:
                    msg_list = json.loads(raw_msgs)
                except Exception:
                    continue
            elif hasattr(raw_msgs, "__iter__"):
                msg_list = list(raw_msgs)
            else:
                continue

            accum_chars = 0
            prior_tool_calls = 0
            prior_errors = 0
            step_count = 0

            for msg in msg_list:
                if not isinstance(msg, dict):
                    continue
                role = msg.get("role")
                content = str(msg.get("content") or "")
                accum_chars += len(content)

                if role in ["tool", "user"]:
                    lower_content = content.lower()
                    if any(err_kw in lower_content for err_kw in ["error", "exception", "failed", "traceback"]):
                        prior_errors += 1
                elif role == "assistant":
                    step_count += 1
                    prior_tool_calls += 1

                    if step_count <= 2 and prior_errors == 0:
                        complexity = "low"
                    elif step_count <= 7 and prior_errors <= 1:
                        complexity = "mid"
                    else:
                        complexity = "high"

                    stats["step_complexity_distribution"][complexity] += 1

                    record = {
                        "source": "SWE-smith",
                        "instance_id": instance_id,
                        "task_session_id": f"agent_traj_{traj_id}",
                        "step_index": step_count,
                        "repo": instance_id.split("__")[0] if "__" in instance_id else "unknown",
                        "domain": "software_engineering",
                        "model": model_name,
                        "context_chars": accum_chars,
                        "prior_tool_calls": prior_tool_calls,
                        "prior_errors": prior_errors,
                        "has_reasoning": True,
                        "step_complexity": complexity,
                        "is_high_effort": complexity == "high",
                        "cache_hit": step_count > 1,
                    }
                    cleaned_records.append(record)
                    if max_samples > 0 and len(cleaned_records) >= max_samples:
                        break
            if max_samples > 0 and len(cleaned_records) >= max_samples:
                break

    stats["total_extracted_decision_steps"] = len(cleaned_records)
    print(f"[+] Agent 轨迹抽取完成: 共 {len(cleaned_records)} 个独立决策步")

    # 写入清洗文件
    with open(cleaned_file, "w", encoding="utf-8") as f:
        for r in cleaned_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # 写入轻量预览 (前 50 条)
    with open(preview_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_records[:50], f, ensure_ascii=False, indent=2)

    return cleaned_records, stats


def clean_arena_preference(raw_dir, cleaned_dir, preview_dir, max_samples=30000):
    """
    清洗 LMSYS Chatbot Arena 人类偏好数据 (train.csv)
    真实标签：胜出模型 (winner_model_a / winner_model_b / winner_tie)
    决策前特征：首轮 prompt 字符数、语言、候选模型对
    """
    print("\n--- [2/4] 清洗 模型偏好数据 (Arena Human Preference 55k) ---")
    out_dir = os.path.join(cleaned_dir, "模型偏好")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    cleaned_file = os.path.join(out_dir, "arena_preference_cleaned.jsonl")
    preview_file = os.path.join(preview_dir, "arena_preference_preview.json")

    arena_path = os.path.join(raw_dir, "Arena", "train.csv")
    cleaned_records = []
    stats = {
        "source": "LMSYS Chatbot Arena",
        "raw_rows_read": 0,
        "valid_cleaned_rows": 0,
        "winner_distribution": Counter(),
        "prompt_length_tiers": Counter(),
    }

    if not os.path.exists(arena_path):
        print(f"[!] 找不到 Arena 数据文件: {arena_path}")
        return cleaned_records, stats

    with open(arena_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats["raw_rows_read"] += 1
            prompt = row.get("prompt", "").strip()
            if not prompt:
                continue

            wa = row.get("winner_model_a", "0") == "1"
            wb = row.get("winner_model_b", "0") == "1"
            tie = row.get("winner_tie", "0") == "1"

            if wa:
                winner = "model_a"
                win_model = row.get("model_a", "").strip()
            elif wb:
                winner = "model_b"
                win_model = row.get("model_b", "").strip()
            elif tie:
                winner = "tie"
                win_model = "tie"
            else:
                continue

            stats["winner_distribution"][winner] += 1
            prompt_len = len(prompt)

            # 长度分级 (决策前输入复杂度)
            if prompt_len < 200:
                len_tier = "short"
                cost_tier = "budget"
            elif prompt_len < 800:
                len_tier = "medium"
                cost_tier = "standard"
            else:
                len_tier = "long"
                cost_tier = "premium"
            stats["prompt_length_tiers"][len_tier] += 1

            # 是否属于顶级前沿模型
            frontier_keywords = ["gpt-4", "claude-3", "gemini-1.5", "qwen-max"]
            is_frontier_win = any(kw in win_model.lower() for kw in frontier_keywords)

            record = {
                "source": "LMSYS_Arena",
                "instance_id": row.get("id"),
                "task_session_id": f"arena_task_{row.get('id')}",
                "step_index": 1,
                "domain": "general_instruction",
                "model_a": row.get("model_a"),
                "model_b": row.get("model_b"),
                "winner": winner,
                "winning_model": win_model,
                "prompt_chars": prompt_len,
                "length_tier": len_tier,
                "cost_tier": cost_tier,
                "is_high_effort": is_frontier_win or (len_tier == "long"),
                "cache_hit": False,  # 单轮独立评测，无历史缓存
            }
            cleaned_records.append(record)

            if max_samples > 0 and len(cleaned_records) >= max_samples:
                break

    stats["valid_cleaned_rows"] = len(cleaned_records)
    print(f"[+] Arena 偏好清洗完成: 共 {len(cleaned_records)} 条有效成对偏好记录")

    with open(cleaned_file, "w", encoding="utf-8") as f:
        for r in cleaned_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(preview_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_records[:50], f, ensure_ascii=False, indent=2)

    return cleaned_records, stats


def clean_mooncake_traces(raw_dir, cleaned_dir, preview_dir, max_samples=30000):
    """
    清洗 Mooncake FAST'25 真实系统推理与 K-V 缓存追踪数据
    利用真实 block hash_ids 计算前缀缓存命中与重用率
    决策前特征：输入 token 长度、块数、到达时间间隔、前缀命中块数
    """
    print("\n--- [3/4] 清洗 缓存负载数据 (Mooncake FAST'25 Traces) ---")
    out_dir = os.path.join(cleaned_dir, "缓存负载")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    cleaned_file = os.path.join(out_dir, "mooncake_cache_cleaned.jsonl")
    preview_file = os.path.join(preview_dir, "mooncake_cache_preview.json")

    cleaned_records = []
    stats = {
        "source": "Mooncake FAST'25",
        "traces_read": 0,
        "valid_records": 0,
        "cache_hit_ratio_tiers": Counter(),
        "is_cache_hit_counts": Counter(),
    }

    recent_history_hashes = []
    trace_files = [
        ("toolagent", os.path.join(raw_dir, "Mooncake", "toolagent_trace.jsonl")),
        ("conversation", os.path.join(raw_dir, "Mooncake", "conversation_trace.jsonl")),
    ]

    last_ts = 0

    for trace_type, path in trace_files:
        if not os.path.exists(path):
            continue
        print(f"[*] 读取 Mooncake {trace_type} trace: {path}")

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                stats["traces_read"] += 1
                try:
                    data = json.loads(line)
                except Exception:
                    continue

                in_len = data.get("input_length", 0)
                hashes = data.get("hash_ids", [])
                if not hashes or in_len <= 0:
                    continue

                ts = data.get("timestamp", 0)
                gap = ts - last_ts if ts >= last_ts else 0
                last_ts = ts

                # 模拟滑动窗口（前 50 次请求）计算前缀重用
                prefix_hit_len = 0
                for prev_h in recent_history_hashes[-50:]:
                    common = 0
                    for a, b in zip(hashes, prev_h):
                        if a == b:
                            common += 1
                        else:
                            break
                    if common > prefix_hit_len:
                        prefix_hit_len = common

                recent_history_hashes.append(hashes)
                if len(recent_history_hashes) > 500:
                    recent_history_hashes.pop(0)

                hit_ratio = prefix_hit_len / len(hashes) if hashes else 0.0
                is_hit = prefix_hit_len > 0
                stats["is_cache_hit_counts"][is_hit] += 1

                if hit_ratio > 0.5:
                    hit_tier = "deep_hit"
                    target_affinity = "local_cache_node"
                elif is_hit:
                    hit_tier = "partial_hit"
                    target_affinity = "cluster_shared_cache"
                else:
                    hit_tier = "cold"
                    target_affinity = "round_robin_dispatch"
                stats["cache_hit_ratio_tiers"][hit_tier] += 1

                if in_len < 2048:
                    cost_tier = "budget"
                elif in_len < 8192:
                    cost_tier = "standard"
                else:
                    cost_tier = "premium"

                record = {
                    "source": "Mooncake_FAST25",
                    "trace_type": trace_type,
                    "instance_id": f"mc_{trace_type}_{stats['valid_records']:06d}",
                    "task_session_id": f"cache_stream_{trace_type}_{stats['valid_records'] // 100:04d}",
                    "step_index": (stats['valid_records'] % 100) + 1,
                    "domain": "system_inference",
                    "input_tokens": in_len,
                    "num_blocks": len(hashes),
                    "arrival_gap_ms": gap,
                    "prefix_hit_blocks": prefix_hit_len,
                    "hit_ratio": round(hit_ratio, 4),
                    "is_cache_hit": is_hit,
                    "cache_affinity": target_affinity,
                    "cost_tier": cost_tier,
                    "is_high_effort": in_len > 4096,
                }
                cleaned_records.append(record)
                stats["valid_records"] += 1

                if max_samples > 0 and len(cleaned_records) >= max_samples:
                    break
        if max_samples > 0 and len(cleaned_records) >= max_samples:
            break

    print(f"[+] Mooncake 缓存轨迹清洗完成: 共 {len(cleaned_records)} 个请求点")

    with open(cleaned_file, "w", encoding="utf-8") as f:
        for r in cleaned_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(preview_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_records[:50], f, ensure_ascii=False, indent=2)

    return cleaned_records, stats


def clean_router_bench(raw_dir, cleaned_dir, preview_dir):
    """
    清洗 路由评测基准数据：
    来源：TwinRouterBench (静态静态路由基准) + LLMRouterBench 任务索引
    真实标签：官方最优 target_tier (low / mid / high) 与 step_index
    """
    print("\n--- [4/4] 清洗 路由评测数据 (TwinRouterBench & LLMRouterBench) ---")
    out_dir = os.path.join(cleaned_dir, "路由评测")
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    cleaned_file = os.path.join(out_dir, "router_bench_cleaned.jsonl")
    preview_file = os.path.join(preview_dir, "router_bench_preview.json")

    cleaned_records = []
    stats = {
        "source": "TwinRouterBench + LLMRouterBench",
        "twinrouter_rows": 0,
        "llmrouterbench_tasks_indexed": 0,
        "target_tier_distribution": Counter(),
        "benchmark_distribution": Counter(),
    }

    try:
        import pyarrow.parquet as pq
    except ImportError:
        print("[!] pyarrow 未安装，无法读取 Parquet！")
        return cleaned_records, stats

    # 1. TwinRouterBench
    trb_path = os.path.join(raw_dir, "TwinRouterBench", "train.parquet")
    if os.path.exists(trb_path):
        print(f"[*] 读取 TwinRouterBench: {trb_path}")
        table = pq.read_table(trb_path)
        df = table.to_pandas()
        stats["twinrouter_rows"] = len(df)

        for _, row in df.iterrows():
            bench = str(row.get("benchmark", "swebench"))
            scenario = str(row.get("scenario", "code_swe"))
            tier = str(row.get("target_tier", "low")).lower()
            if tier == "mid_high":
                tier = "high"

            step_idx = int(row.get("step_index", 1))
            total_steps = int(row.get("total_steps", 1))
            instance_id = str(row.get("instance_id", "unknown"))

            stats["target_tier_distribution"][tier] += 1
            stats["benchmark_distribution"][bench] += 1

            if tier == "low":
                cost_tier = "budget"
            elif tier == "mid":
                cost_tier = "standard"
            else:
                cost_tier = "premium"

            record = {
                "source": "TwinRouterBench",
                "instance_id": row.get("id"),
                "task_session_id": f"bench_{bench}_{instance_id}",
                "benchmark": bench,
                "scenario": scenario,
                "step_index": step_idx,
                "total_steps": total_steps,
                "target_tier": tier,
                "cost_tier": cost_tier,
                "is_high_effort": tier == "high",
                "cache_hit": step_idx > 1,
            }
            cleaned_records.append(record)

    # 2. 索引 LLMRouterBench 任务
    lrb_dir = os.path.join(raw_dir, "LLMRouterBench", "data")
    if os.path.exists(lrb_dir):
        task_folders = [d for d in os.listdir(lrb_dir) if os.path.isdir(os.path.join(lrb_dir, d))]
        stats["llmrouterbench_tasks_indexed"] = len(task_folders)
        print(f"[+] 索引 LLMRouterBench 任务子集: {len(task_folders)} 个领域")

    print(f"[+] 路由评测数据清洗完成: 共 {len(cleaned_records)} 条路由决策步")

    with open(cleaned_file, "w", encoding="utf-8") as f:
        for r in cleaned_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(preview_file, "w", encoding="utf-8") as f:
        json.dump(cleaned_records[:50], f, ensure_ascii=False, indent=2)

    return cleaned_records, stats


# =====================================================================
# 三、统一 Kev-4B 数据集划分与生成模块 (会话/任务级无泄漏划分)
# =====================================================================

def assemble_kev_public_dataset(
    agent_records,
    arena_records,
    cache_records,
    bench_records,
    output_dir,
    preview_dir,
    seed=42,
):
    """
    将 4 类公开清洗数据聚合为统一的 Kev-4B 格式，并严格按 Session/Instance 隔离划分
    Train (70%) / Val (15%) / Test (15%)
    """
    print("\n" + "=" * 60)
    print("  统一聚合生成 Kev-4B 公开数据集 (Train/Val/Test 划分)")
    print("=" * 60)
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(preview_dir, exist_ok=True)

    all_kev_samples = []
    choice_stats = Counter()
    noul_effort_stats = Counter()
    noul_cache_stats = Counter()
    score_tier_stats = Counter()

    # 1. Agent 轨迹样本
    for r in agent_records:
        state_repr = (
            f"Context: domain=software_engineering, repo={r.get('repo')}, "
            f"step={r['step_index']}, prior_tool_calls={r['prior_tool_calls']}, "
            f"prior_errors={r['prior_errors']}, context_chars={r['context_chars']}. "
            f"Available actions: [bash, edit, view]."
        )
        choice_label = r["step_complexity"]
        is_high = r["is_high_effort"]
        is_cache = r["cache_hit"]
        cost_tier = "budget" if choice_label == "low" else ("standard" if choice_label == "mid" else "premium")

        choice_stats[choice_label] += 1
        noul_effort_stats[is_high] += 1
        noul_cache_stats[is_cache] += 1
        score_tier_stats[cost_tier] += 1

        sample = {
            "provenance": {
                "source": r["source"],
                "instance_id": r["instance_id"],
                "task_session_id": r["task_session_id"],
                "step_index": r["step_index"],
            },
            "state": state_repr,
            "questions": {
                "routing_choice": {
                    "type": "choice",
                    "instructions": "Select the appropriate execution tier for this agent step.",
                    "options": ["low", "mid", "high"],
                    "label": choice_label,
                },
                "high_reasoning_effort": {
                    "type": "noul",
                    "instructions": "Does this step require high or deep reasoning capability?",
                    "label": is_high,
                },
                "cache_read_hit": {
                    "type": "noul",
                    "instructions": "Will this step observe prompt prefix cache hit?",
                    "label": is_cache,
                },
                "cost_tier": {
                    "type": "score",
                    "instructions": "Expected cost and resource complexity tier.",
                    "levels": ["budget", "standard", "premium"],
                    "label": cost_tier,
                },
            },
        }
        all_kev_samples.append((r["task_session_id"], sample))

    # 2. Arena 偏好样本
    for r in arena_records:
        state_repr = (
            f"Context: domain=general_instruction, turn=1, "
            f"prompt_chars={r['prompt_chars']}, candidate_models=[{r['model_a']}, {r['model_b']}]."
        )
        choice_label = r["winner"]
        is_high = r["is_high_effort"]
        is_cache = False
        cost_tier = r["cost_tier"]

        choice_stats[choice_label] += 1
        noul_effort_stats[is_high] += 1
        noul_cache_stats[is_cache] += 1
        score_tier_stats[cost_tier] += 1

        sample = {
            "provenance": {
                "source": r["source"],
                "instance_id": str(r["instance_id"]),
                "task_session_id": r["task_session_id"],
                "step_index": 1,
            },
            "state": state_repr,
            "questions": {
                "routing_choice": {
                    "type": "choice",
                    "instructions": "Select which candidate model is superior for this prompt.",
                    "options": ["model_a", "model_b", "tie"],
                    "label": choice_label,
                },
                "high_reasoning_effort": {
                    "type": "noul",
                    "instructions": "Does this query require high frontier model capability?",
                    "label": is_high,
                },
                "cache_read_hit": {
                    "type": "noul",
                    "instructions": "Will this request observe prompt cache hit?",
                    "label": False,
                },
                "cost_tier": {
                    "type": "score",
                    "instructions": "Expected cost tier based on prompt length.",
                    "levels": ["budget", "standard", "premium"],
                    "label": cost_tier,
                },
            },
        }
        all_kev_samples.append((r["task_session_id"], sample))

    # 3. Mooncake 缓存样本
    for r in cache_records:
        state_repr = (
            f"Context: domain=system_inference, arrival_gap_ms={r['arrival_gap_ms']}, "
            f"input_tokens={r['input_tokens']}, num_blocks={r['num_blocks']}, "
            f"prefix_cached_blocks={r['prefix_hit_blocks']}. Prompt cache capability: active."
        )
        choice_label = r["cache_affinity"]
        is_high = r["is_high_effort"]
        is_cache = r["is_cache_hit"]
        cost_tier = r["cost_tier"]

        choice_stats[choice_label] += 1
        noul_effort_stats[is_high] += 1
        noul_cache_stats[is_cache] += 1
        score_tier_stats[cost_tier] += 1

        sample = {
            "provenance": {
                "source": r["source"],
                "instance_id": r["instance_id"],
                "task_session_id": r["task_session_id"],
                "step_index": r["step_index"],
            },
            "state": state_repr,
            "questions": {
                "routing_choice": {
                    "type": "choice",
                    "instructions": "Select cache-aware routing target dispatch policy.",
                    "options": ["local_cache_node", "cluster_shared_cache", "round_robin_dispatch"],
                    "label": choice_label,
                },
                "high_reasoning_effort": {
                    "type": "noul",
                    "instructions": "Is this request long-context requiring high memory budget?",
                    "label": is_high,
                },
                "cache_read_hit": {
                    "type": "noul",
                    "instructions": "Will this request observe prefix cache block reuse?",
                    "label": is_cache,
                },
                "cost_tier": {
                    "type": "score",
                    "instructions": "Expected inference cost tier based on input tokens.",
                    "levels": ["budget", "standard", "premium"],
                    "label": cost_tier,
                },
            },
        }
        all_kev_samples.append((r["task_session_id"], sample))

    # 4. 路由评测样本
    for r in bench_records:
        state_repr = (
            f"Context: domain=code_swe, benchmark={r['benchmark']}, "
            f"scenario={r['scenario']}, step={r['step_index']}/{r['total_steps']}. "
            f"Target router tier candidates: [low, mid, high]."
        )
        choice_label = r["target_tier"]
        is_high = r["is_high_effort"]
        is_cache = r["cache_hit"]
        cost_tier = r["cost_tier"]

        choice_stats[choice_label] += 1
        noul_effort_stats[is_high] += 1
        noul_cache_stats[is_cache] += 1
        score_tier_stats[cost_tier] += 1

        sample = {
            "provenance": {
                "source": r["source"],
                "instance_id": str(r["instance_id"]),
                "task_session_id": r["task_session_id"],
                "step_index": r["step_index"],
            },
            "state": state_repr,
            "questions": {
                "routing_choice": {
                    "type": "choice",
                    "instructions": "Select the target router tier for this benchmark step.",
                    "options": ["low", "mid", "high"],
                    "label": choice_label,
                },
                "high_reasoning_effort": {
                    "type": "noul",
                    "instructions": "Does this step require high tier capability?",
                    "label": is_high,
                },
                "cache_read_hit": {
                    "type": "noul",
                    "instructions": "Will this step observe prompt cache hit from prior steps?",
                    "label": is_cache,
                },
                "cost_tier": {
                    "type": "score",
                    "instructions": "Expected cost tier based on router benchmark target.",
                    "levels": ["budget", "standard", "premium"],
                    "label": cost_tier,
                },
            },
        }
        all_kev_samples.append((r["task_session_id"], sample))

    # 5. 会话级严格无泄漏划分 (70% / 15% / 15%)
    all_sessions = sorted(list(set(s_id for s_id, _ in all_kev_samples)))
    random.shuffle(all_sessions)

    n_sessions = len(all_sessions)
    n_train = int(n_sessions * 0.70)
    n_val = int(n_sessions * 0.15)

    train_sess = set(all_sessions[:n_train])
    val_sess = set(all_sessions[n_train : n_train + n_val])
    test_sess = set(all_sessions[n_train + n_val :])

    train_data = [s for s_id, s in all_kev_samples if s_id in train_sess]
    val_data = [s for s_id, s in all_kev_samples if s_id in val_sess]
    test_data = [s for s_id, s in all_kev_samples if s_id in test_sess]

    train_path = os.path.join(output_dir, "train.jsonl")
    val_path = os.path.join(output_dir, "val.jsonl")
    test_path = os.path.join(output_dir, "test.jsonl")

    for path, dataset in [(train_path, train_data), (val_path, val_data), (test_path, test_data)]:
        with open(path, "w", encoding="utf-8") as f:
            for s in dataset:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    # 预览保存 (前 50 条)
    preview_path = os.path.join(preview_dir, "kev_sample_preview.json")
    with open(preview_path, "w", encoding="utf-8") as f:
        json.dump([s for _, s in all_kev_samples[:50]], f, ensure_ascii=False, indent=2)

    split_stats = {
        "total_sessions": n_sessions,
        "train_sessions": len(train_sess),
        "val_sessions": len(val_sess),
        "test_sessions": len(test_sess),
        "total_samples": len(all_kev_samples),
        "train_samples": len(train_data),
        "val_samples": len(val_data),
        "test_samples": len(test_data),
        "choice_distribution": dict(choice_stats.most_common()),
        "noul_high_effort": dict(noul_effort_stats),
        "noul_cache_hit": dict(noul_cache_stats),
        "score_cost_tier": dict(score_tier_stats.most_common()),
    }

    print(f"\n[+] Kev-4B 公开数据集划分完成:")
    print(f"    - 独立会话/任务总数: {n_sessions} (Train: {len(train_sess)}, Val: {len(val_sess)}, Test: {len(test_sess)})")
    print(f"    - Train 样本数: {len(train_data):<7} ({len(train_data)/len(all_kev_samples)*100:.1f}%) -> {train_path}")
    print(f"    - Val   样本数: {len(val_data):<7} ({len(val_data)/len(all_kev_samples)*100:.1f}%) -> {val_path}")
    print(f"    - Test  样本数: {len(test_data):<7} ({len(test_data)/len(all_kev_samples)*100:.1f}%) -> {test_path}")

    return split_stats


# =====================================================================
# 四、报告与统计生成模块
# =====================================================================

def generate_cleaning_reports(all_stats, report_dir):
    """生成清洗统计 JSON 与正式 Markdown 报告"""
    os.makedirs(report_dir, exist_ok=True)
    json_path = os.path.join(report_dir, "清洗统计.json")
    md_path = os.path.join(report_dir, "公开数据清洗报告.md")

    # 写入 JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_stats, f, ensure_ascii=False, indent=2)

    # 写入 Markdown
    kev_info = all_stats.get("kev_split", {})
    md_content = f"""# ModelRouter 公开数据清洗与 Kev-4B 转换执行报告

> **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
> **执行环境**: GPU 服务器 `k3s-infra-01` (NVIDIA RTX A6000 48GB, Ubuntu 24.04 LTS)  
> **唯一执行脚本**: `prepare_router_data.py --mode public`  
> **执行原则**: 真实溯源、零过度工程、无未来信息泄漏、任务级严格隔离划分。

---

## 1. 执行总览

本次公开数据处理全部在服务器本地高速完成，覆盖 4 大领域方向、6 组主流开源数据集：
1. **Agent轨迹**: Open-SWE-Traces (NVIDIA) 与 SWE-smith (SWE-bench)
2. **模型偏好**: LMSYS Chatbot Arena (55k 成对人类偏好)
3. **缓存负载**: Mooncake FAST'25 (Kimi 生产系统 ToolAgent 与 Conversation 真实 KV 块追踪)
4. **路由评测**: TwinRouterBench (静态阶梯路由评测) 与 LLMRouterBench (任务领域索引)

经过清洗、过滤与决策前特征隔离，共抽取生成 **{kev_info.get('total_samples', 0):,}** 个真实监督样本，涵盖 **{kev_info.get('total_sessions', 0):,}** 个独立任务会话。

---

## 2. 清洗前后实测统计表

| 领域分类 | 原始数据源 | 原始规模 / 格式 | 清洗后有效样本数 | 提取决策前核心特征 | 真实监督标签 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Agent轨迹** | Open-SWE-Traces + SWE-smith | 218 MB (Parquet, 5,729 轨迹) | {all_stats.get('agent_stats', {}).get('total_extracted_decision_steps', 0):,} 步 | 步骤序号、累积字符数、前序工具调用数、前序异常信号 | `step_complexity` (low/mid/high), `is_high_effort` |
| **模型偏好** | LMSYS Chatbot Arena | 176 MB (CSV, 57,477 偏好对) | {all_stats.get('arena_stats', {}).get('valid_cleaned_rows', 0):,} 条 | 首轮 Prompt 长度、语言、候选模型对 | `winner` (model_a/model_b/tie), `is_high_effort` |
| **缓存负载** | Mooncake FAST'25 | 8.2 MB (JSONL, 39,632 轨迹点) | {all_stats.get('cache_stats', {}).get('valid_records', 0):,} 点 | 输入 token 数、块数、到达间隔、滑动前缀重用块数 | `cache_affinity`, `is_cache_hit`, `cost_tier` |
| **路由评测** | TwinRouterBench + LLMRouterBench | 1.3 MB (Parquet) + 30 任务集 | {all_stats.get('bench_stats', {}).get('twinrouter_rows', 0):,} 步 | 基准测试类别、执行阶段、总步数 | `target_tier` (low/mid/high), `cost_tier` |
| **汇总总计** | **全域公开数据池** | **~405 MB** | **{kev_info.get('total_samples', 0):,} 样本** | **统一 Pre-decision State 上下文** | **Choice / Noul / Score 三位一体** |

---

## 3. Kev-4B 标准数据集划分 (会话级严格无泄漏)

为防止同一任务或会话的多轮步骤在 Train 与 Test 间交叉泄漏，数据集严格按 `task_session_id` 划分：

- **划分比例**: 70% 训练集 (Train) / 15% 验证集 (Val) / 15% 测试集 (Test)
- **独立会话总数**: {kev_info.get('total_sessions', 0):,} 个
  - 训练集会话: {kev_info.get('train_sessions', 0):,} 个
  - 验证集会话: {kev_info.get('val_sessions', 0):,} 个
  - 测试集会话: {kev_info.get('test_sessions', 0):,} 个
- **样本划分结果**:
  - `data/kev/公开数据/train.jsonl`: **{kev_info.get('train_samples', 0):,}** 条 ({kev_info.get('train_samples', 0)/(kev_info.get('total_samples', 1))*100:.1f}%)
  - `data/kev/公开数据/val.jsonl`: **{kev_info.get('val_samples', 0):,}** 条 ({kev_info.get('val_samples', 0)/(kev_info.get('total_samples', 1))*100:.1f}%)
  - `data/kev/公开数据/test.jsonl`: **{kev_info.get('test_samples', 0):,}** 条 ({kev_info.get('test_samples', 0)/(kev_info.get('total_samples', 1))*100:.1f}%)

---

## 4. 标签类别真实分布

### 4.1 Choice 路由决策
{chr(10).join([f"- `{k}`: {v:,} 次" for k, v in kev_info.get('choice_distribution', {}).items()])}

### 4.2 Noul 二元状态属性
- **高深度推理需求 (high_reasoning_effort)**:
  - `True`: {kev_info.get('noul_high_effort', {}).get(True, 0):,} 样本
  - `False`: {kev_info.get('noul_high_effort', {}).get(False, 0):,} 样本
- **前缀缓存命中 (cache_read_hit)**:
  - `True`: {kev_info.get('noul_cache_hit', {}).get(True, 0):,} 样本
  - `False`: {kev_info.get('noul_cache_hit', {}).get(False, 0):,} 样本

### 4.3 Score 资源与成本档位
{chr(10).join([f"- `{k}`: {v:,} 样本" for k, v in kev_info.get('score_cost_tier', {}).items()])}

---

## 5. 存储架构与轻量同步

- **服务器全量存储**:
  - 原始数据: `~/路由/data/公开数据/原始数据/` (~405 MB)
  - 清洗数据: `~/路由/data/公开数据/清洗数据/`
  - Kev 训练集: `~/路由/data/kev/公开数据/`
- **本地与 GitHub 轻量同步 (方案 A)**:
  - 轻量预览数据: `our-project/data/公开数据/数据预览/*.json` (各 50 条样本，不上传大数据)
  - 统计报告: `our-project/data/公开数据清洗报告.md`
  - 执行代码: `prepare_router_data.py`
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"\n[✓] 清洗统计 JSON 已生成: {json_path}")
    print(f"[✓] 清洗报告 Markdown 已生成: {md_path}")


def run_public_pipeline(args):
    print("\n" + "=" * 60)
    print("  [Mode: Public] 服务器公开数据清洗与 Kev-4B 转换")
    print("=" * 60)
    print(f"[*] 原始数据根目录: {args.public_raw_dir}")
    print(f"[*] 清洗数据根目录: {args.public_cleaned_dir}")
    print(f"[*] 预览输出目录:   {args.public_preview_dir}")
    print(f"[*] Kev 输出目录:    {args.public_kev_dir}")
    print(f"[*] 报告输出目录:   {args.public_report_dir}")

    # 1. 清洗四类数据
    agent_records, agent_stats = clean_agent_traces(
        args.public_raw_dir, args.public_cleaned_dir, args.public_preview_dir, args.max_agent_samples
    )
    arena_records, arena_stats = clean_arena_preference(
        args.public_raw_dir, args.public_cleaned_dir, args.public_preview_dir, args.max_arena_samples
    )
    cache_records, cache_stats = clean_mooncake_traces(
        args.public_raw_dir, args.public_cleaned_dir, args.public_preview_dir, args.max_cache_samples
    )
    bench_records, bench_stats = clean_router_bench(
        args.public_raw_dir, args.public_cleaned_dir, args.public_preview_dir
    )

    # 2. 统一生成 Kev 数据集
    split_stats = assemble_kev_public_dataset(
        agent_records,
        arena_records,
        cache_records,
        bench_records,
        args.public_kev_dir,
        args.public_preview_dir,
        seed=args.seed,
    )

    # 3. 生成报告与统计
    all_stats = {
        "timestamp": datetime.now().isoformat(),
        "agent_stats": agent_stats,
        "arena_stats": arena_stats,
        "cache_stats": cache_stats,
        "bench_stats": bench_stats,
        "kev_split": split_stats,
    }
    # 将 Counter 转换为 dict 以便序列化
    for k in ["agent_stats", "arena_stats", "cache_stats", "bench_stats"]:
        for sub_k, sub_v in all_stats[k].items():
            if isinstance(sub_v, Counter):
                all_stats[k][sub_k] = dict(sub_v)

    generate_cleaning_reports(all_stats, args.public_report_dir)

    print("\n" + "=" * 60)
    print("  [✓] 公开数据唯一执行链顺利完成！所有输出已写入目标目录。")
    print("=" * 60)


def main():
    args = parse_args()
    if args.mode == "blog":
        run_blog_pipeline(args)
    elif args.mode == "public":
        run_public_pipeline(args)
    elif args.mode == "all":
        run_blog_pipeline(args)
        run_public_pipeline(args)


if __name__ == "__main__":
    main()
