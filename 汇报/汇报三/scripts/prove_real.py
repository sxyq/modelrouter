#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P16/P17 真实调用自证脚本

用三条互相独立的证据证明页面没有在前端模拟：
  A. 服务端计数：调用前后 A6000 的 total_requests 必须精确增加 2/轮
  B. 同输入复现：同一 state+questions 调两次，概率必须逐位相同（确定性前向）
  C. 异输入变化：换一个任务描述，概率必须变化（前端查表做不到任意输入）

另外做一次 D. 直连对照：绕过桥接、直接打 A6000 /system-one，结果应与桥接一致。

用法：
  python scripts/prove_real.py
  python scripts/prove_real.py --rounds 1     # 少跑一次，省时间
"""

import argparse
import json
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CST = timezone(timedelta(hours=8))
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def upstream():
    cfg = ASSETS / "local_config.json"
    if cfg.exists():
        return json.loads(cfg.read_text(encoding="utf-8"))["upstream"].rstrip("/")
    return "http://127.0.0.1:8000"


def bridge():
    cfg = ASSETS / "local_config.json"
    port = 8775
    if cfg.exists():
        data = json.loads(cfg.read_text(encoding="utf-8"))
        port = int(data.get("bridge_port", port))
    return f"http://127.0.0.1:{port}"


def get(url):
    with OPENER.open(urllib.request.Request(url), timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))


def post(url, payload, timeout=240):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with OPENER.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def base_questions():
    return {
        "q_choice": {
            "type": "choice",
            "instructions": "这一步应该交给哪一档模型处理？",
            "criteria": {
                "cheap_fast": "轻量快速：小参数模型，成本低，不做长推理",
                "mid_balanced": "均衡中档：中等模型，给予适度推理预算",
                "strong_deep": "旗舰深度：前沿模型，高精度推理，长链路分析",
            },
        },
        "q_score": {
            "type": "score",
            "instructions": "评估这一步的修复难度。",
            "criteria": ["很简单", "较简单", "中等", "较困难", "非常困难"],
        },
        "q_noul": {"type": "noul", "instructions": "下一步是否可能复用前缀缓存？"},
    }


CASE_A = {
    "task_domain": "软件工程",
    "step_index": 3,
    "context_chars": 1240,
    "prior_tool_calls_count": 2,
    "prior_error_signals_count": 1,
    "prompt": "单元测试 test_refresh_token 在令牌轮换后返回 401；进程内存中仍保留过期的用户标识，缓存与数据库不一致。",
}

CASE_B = {
    "task_domain": "生产运维",
    "step_index": 9,
    "context_chars": 18600,
    "prior_tool_calls_count": 11,
    "prior_error_signals_count": 4,
    "prompt": "支付网关在大促开始两分钟后持续返回 504，订单队列堆积超过八万条，三个下游服务连接池被打满，需要立刻决定回滚还是限流。",
}


def signature(resp, family):
    a = resp["answers"]
    c = a["q_choice"]
    return {
        "choice": c["choice"],
        "probs": {k: round(v, 6) for k, v in c["probabilities"].items()},
        "score": round(a["q_score"]["score"], 6),
        "noul": a["q_noul"]["noul"],
        "latency": resp["decision_latency_ms"],
    }


def run_pair(tag, state, questions):
    body = {"state": state, "questions": questions, "families": ["laya", "kev"],
            "test_id": f"PROOF-{tag}-{datetime.now(CST).strftime('%H%M%S')}"}
    out = post(f"{bridge()}/api/pair", body)
    if "results" not in out:
        raise SystemExit(f"桥接请求失败：{out}")
    return {f: signature(r["response"], f) for f, r in out["results"].items() if r.get("ok")}


def same(a, b):
    return a["probs"] == b["probs"] and a["score"] == b["score"] and a["noul"] == b["noul"] and a["choice"] == b["choice"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=2, help="同输入重复次数，默认 2")
    args = ap.parse_args()

    up = upstream()
    print("=" * 66)
    print("真实调用自证 ·", datetime.now(CST).strftime("%Y-%m-%d %H:%M:%S"))
    print("上游:", up)
    print("=" * 66)

    m0 = get(f"{up}/metrics")
    print(f"\n[A] 调用前 A6000 total_requests = {m0['total_requests']}")

    questions = base_questions()

    print("\n[B] 同一输入重复调用（应完全一致）")
    runs = []
    for i in range(args.rounds):
        r = run_pair(f"A{i+1}", CASE_A, questions)
        runs.append(r)
        print(f"    第{i+1}次  Laya {r['laya']['choice']:>13} {r['laya']['probs'][r['laya']['choice']]:.4f}"
              f" | 难度 {r['laya']['score']:.4f} | P(真) {r['laya']['noul']} | {r['laya']['latency']:.0f}ms")
        print(f"           Kev  {r['kev']['choice']:>13} {r['kev']['probs'][r['kev']['choice']]:.4f}"
              f" | 难度 {r['kev']['score']:.4f} | P(真) {r['kev']['noul']} | {r['kev']['latency']:.0f}ms")

    stable = all(same(runs[0]["laya"], r["laya"]) for r in runs) and \
             all(same(runs[0]["kev"], r["kev"]) for r in runs)
    print(f"    → 概率/评分/判断{'完全一致 ✓（确定性前向）' if stable else '出现差异 ✗'}")

    print("\n[C] 换一个任务描述（分布必须变化）")
    rb = run_pair("B1", CASE_B, questions)
    for fam in ("laya", "kev"):
        before, after = runs[0][fam], rb[fam]
        moved = before["probs"] != after["probs"]
        print(f"    {fam:<5} 原 {before['choice']:>13} {before['probs'][before['choice']]:.4f} → "
              f"新 {after['choice']:>13} {after['probs'][after['choice']]:.4f}  "
              f"{'分布已变化 ✓' if moved else '未变化 ✗'}")

    m1 = get(f"{up}/metrics")
    delta = m1["total_requests"] - m0["total_requests"]
    expected = (args.rounds + 1) * 2
    print(f"\n[A] 调用后 total_requests = {m1['total_requests']}  Δ = {delta}  "
          f"（预期 {expected} = {(args.rounds + 1)} 轮 × 2 模型）{'✓' if delta == expected else '✗'}")

    print("\n[D] 直连对照：绕过桥接，直接打 A6000 /system-one")
    direct = post(f"{up}/system-one", {"router_family": "laya", "state": CASE_A, "questions": questions})
    d = signature(direct, "laya")
    ref = runs[0]["laya"]
    print(f"    直连 Laya {d['choice']} {d['probs'][d['choice']]:.4f} | 难度 {d['score']:.4f} | P(真) {d['noul']}")
    print(f"    与桥接结果{'完全一致 ✓' if same(d, ref) else '存在差异 ✗'}")

    verdict = stable and delta == expected and all(
        runs[0][f]["probs"] != rb[f]["probs"] for f in ("laya", "kev")
    ) and same(d, ref)
    print("\n" + "=" * 66)
    print("结论：", "数据来自 A6000 真实前向推理，页面未做模拟 ✓" if verdict else "存在异常，需要排查 ✗")
    print("=" * 66)

    out = Path(__file__).resolve().parent.parent / "runs" / f"proof_{datetime.now(CST).strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps({
        "at": datetime.now(CST).isoformat(),
        "metrics_before": m0, "metrics_after": m1,
        "same_input_runs": runs, "different_input": rb, "direct_upstream": d,
        "verdict": verdict,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n证据已存档：{out.name}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
