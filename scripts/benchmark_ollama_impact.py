#!/usr/bin/env python3
"""
Benchmark the real impact of single-concurrency and dual-concurrency Ollama Qwen3.5:9b-local
inference on the active F05 GPU training queue.
"""
import sys
import os
import time
import json
import urllib.request
import concurrent.futures
import subprocess
from datetime import datetime

CURSOR_PATH = "/home/syy/路由/runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F05/cursor.json"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen3.5:9b-local"

PROMPTS = [
    "请详细分析 Transformer 架构中自注意力机制（Self-Attention）与传统的循环神经网络（RNN）相比的核心优劣势，从并行度、长程依赖建模和显存复杂度三个维度展开，约200字。",
    "请写一段 Python 代码，使用 PyTorch 实现一个带有 LayerNorm 和残差连接的前馈全连接层（FFN），并简要说明其数值稳定性设计。",
    "请简述在深度强化学习中，Policy Gradient 与 Q-learning 的根本区别，以及 PPO 算法如何通过裁剪目标函数来防止策略崩溃，约200字。",
    "请讨论大语言模型训练过程中混合精度（AMP FP16 vs BF16）对梯度溢出和吞吐的影响，以及何时需要 Gradient Scaler。",
    "请用中文解释现代分布式大模型训练中张量并行（Tensor Parallelism）与流水线并行（Pipeline Parallelism）的通信开销瓶颈及适用场景。"
]

def query_gpu_stats():
    cmd = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
        "--format=csv,noheader,nounits"
    ]
    try:
        res = subprocess.check_output(cmd, text=True).strip()
        parts = [p.strip() for p in res.split(",")]
        return {
            "gpu_util_pct": float(parts[0]),
            "mem_used_mib": float(parts[1]),
            "mem_total_mib": float(parts[2]),
            "temp_c": float(parts[3]),
            "power_w": float(parts[4])
        }
    except Exception as e:
        return {"error": str(e)}

def get_f05_cursor():
    try:
        with open(CURSOR_PATH) as f:
            return json.load(f)
    except Exception:
        return None

def send_ollama_request(prompt, req_id):
    data = json.dumps({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 256,
            "temperature": 0.7
        }
    }).encode("utf-8")
    req = urllib.request.Request(OLLAMA_URL, data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            elapsed = time.time() - t0
            eval_count = body.get("eval_count", 0)
            eval_duration_sec = body.get("eval_duration", 1) / 1e9
            tokens_per_sec = eval_count / eval_duration_sec if eval_duration_sec > 0 else 0
            return {
                "req_id": req_id,
                "success": True,
                "elapsed_sec": round(elapsed, 2),
                "eval_count": eval_count,
                "tokens_per_sec": round(tokens_per_sec, 2),
                "prompt_eval_count": body.get("prompt_eval_count", 0)
            }
    except Exception as e:
        return {
            "req_id": req_id,
            "success": False,
            "elapsed_sec": round(time.time() - t0, 2),
            "error": str(e)
        }

def run_concurrency_phase(phase_name, concurrency, total_requests):
    print(f"\n==========================================")
    print(f"Starting {phase_name}: concurrency={concurrency}, total_requests={total_requests}")
    print(f"==========================================")
    
    start_cursor = get_f05_cursor()
    print(f"Initial F05 Cursor: chunk={start_cursor.get('chunk_idx')}, step={start_cursor.get('step_count')}, loss={start_cursor.get('latest_chunk_loss'):.4f}")
    
    results = []
    gpu_samples = []
    t_start = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {}
        prompt_idx = 0
        for i in range(total_requests):
            prompt = PROMPTS[prompt_idx % len(PROMPTS)]
            prompt_idx += 1
            fut = executor.submit(send_ollama_request, prompt, i + 1)
            futures[fut] = i + 1
            
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            results.append(res)
            gpu = query_gpu_stats()
            gpu_samples.append(gpu)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Req {res['req_id']}/{total_requests}: {res['elapsed_sec']}s, {res.get('eval_count', 0)} tokens ({res.get('tokens_per_sec', 0)} t/s) | GPU Util: {gpu.get('gpu_util_pct')}%, VRAM: {gpu.get('mem_used_mib')} MiB, Power: {gpu.get('power_w')}W, Temp: {gpu.get('temp_c')}C")
    
    total_elapsed = time.time() - t_start
    end_cursor = get_f05_cursor()
    
    total_tokens = sum(r.get("eval_count", 0) for r in results if r["success"])
    avg_tokens_per_sec = sum(r.get("tokens_per_sec", 0) for r in results if r["success"]) / max(1, len([r for r in results if r["success"]]))
    avg_latency = sum(r.get("elapsed_sec", 0) for r in results if r["success"]) / max(1, len([r for r in results if r["success"]]))
    
    avg_util = sum(g.get("gpu_util_pct", 0) for g in gpu_samples) / max(1, len(gpu_samples))
    avg_vram = sum(g.get("mem_used_mib", 0) for g in gpu_samples) / max(1, len(gpu_samples))
    avg_power = sum(g.get("power_w", 0) for g in gpu_samples) / max(1, len(gpu_samples))
    max_temp = max([g.get("temp_c", 0) for g in gpu_samples], default=0)
    
    summary = {
        "phase": phase_name,
        "concurrency": concurrency,
        "total_requests": total_requests,
        "successful_requests": len([r for r in results if r["success"]]),
        "total_duration_sec": round(total_elapsed, 2),
        "total_tokens_generated": total_tokens,
        "avg_latency_sec": round(avg_latency, 2),
        "avg_tokens_per_sec": round(avg_tokens_per_sec, 2),
        "avg_gpu_util_pct": round(avg_util, 1),
        "avg_vram_mib": round(avg_vram, 1),
        "avg_power_w": round(avg_power, 1),
        "max_temp_c": max_temp,
        "f05_cursor_start": start_cursor,
        "f05_cursor_end": end_cursor
    }
    return summary

def main():
    print(f"Ollama Qwen3.5:9b-local & F05 Co-run Benchmark")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # 1. Single Concurrency Phase (5 requests sequentially)
    single_res = run_concurrency_phase("Phase 1: Single Concurrency (1-worker)", concurrency=1, total_requests=6)
    
    # Rest 5 seconds
    time.sleep(5)
    
    # 2. Dual Concurrency Phase (2 workers in parallel, 6 requests total = 3 rounds of 2 parallel)
    dual_res = run_concurrency_phase("Phase 2: Dual Concurrency (2-workers)", concurrency=2, total_requests=6)
    
    output = {
        "benchmark_timestamp": datetime.now().isoformat(),
        "single_concurrency": single_res,
        "dual_concurrency": dual_res
    }
    
    print("\n================ FINAL REPORT ================")
    print(json.dumps(output, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
