#!/usr/bin/env python3
"""ModelRouter Academic Live Demo V2: Choice / Score / Noul typed decisions on A6000.

Features:
- Dual model native inference: Laya-421M (ModernBERT) and Kev-4B (Qwen3.5-4B).
- TypeSafe System One 3 decision primitives: Choice, Score, Noul.
- Side-by-side dual-model comparison and single-model drill-down.
- Real-time SVG dials, bar charts, and discrete distribution histograms.
- 16:9 widescreen layout for projector and advisor presentation.
- Zero mock, zero hallucinations: all predictions come from true forward passes.
- Local server: http://127.0.0.1:8766
"""
from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("modelrouter_demo")

HOST = "127.0.0.1"
PORT = int(os.environ.get("DEMO_PORT", "8766"))
ROUTER_URL = os.environ.get("ROUTER_API_URL", "http://127.0.0.1:8000").rstrip("/")
JEV_URL = "https://api.typesafe.ai/v1/systemone"
MAX_PAYLOAD = 256 * 1024

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>ModelRouter · 双模型三类型真实决策现场演示</title>
<style>
:root {
  --bg: #090d16;
  --panel: #111827;
  --panel-border: #1f293d;
  --panel-hover: #1e293b;
  --text-main: #f1f5f9;
  --text-sub: #94a3b8;
  --text-muted: #64748b;
  --laya: #06b6d4;
  --laya-bg: rgba(6, 182, 212, 0.12);
  --kev: #10b981;
  --kev-bg: rgba(16, 185, 129, 0.12);
  --accent-purple: #8b5cf6;
  --accent-purple-bg: rgba(139, 92, 246, 0.15);
  --card-bg: #151e32;
  --card-border: #24324f;
  --success: #10b981;
  --danger: #ef4444;
  --warning: #f59e0b;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  line-height: 1.5;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
header {
  background: linear-gradient(135deg, #0b1329 0%, #111d3d 50%, #0d1e38 100%);
  border-bottom: 1px solid var(--panel-border);
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}
.header-title h1 {
  font-size: 20px;
  font-weight: 750;
  letter-spacing: -0.5px;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
}
.header-title p {
  font-size: 13px;
  color: var(--text-sub);
  margin-top: 3px;
}
.status-pill-group {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-sub);
}
.pill.online {
  background: rgba(16, 185, 129, 0.12);
  border-color: rgba(16, 185, 129, 0.35);
  color: #34d399;
}
.pill.offline {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.35);
  color: #f87171;
}
.pill.laya-badge {
  background: var(--laya-bg);
  border-color: rgba(6, 182, 212, 0.35);
  color: #38bdf8;
}
.pill.kev-badge {
  background: var(--kev-bg);
  border-color: rgba(16, 185, 129, 0.35);
  color: #4ade80;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 8px currentColor;
}
main {
  flex: 1;
  max-width: 1720px;
  width: 100%;
  margin: 0 auto;
  padding: 20px 24px 32px;
  display: grid;
  grid-template-columns: 480px 1fr;
  gap: 22px;
}
@media (max-width: 1200px) {
  main { grid-template-columns: 1fr; }
}
.panel {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 12px;
}
.panel-head h2 {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 8px;
}
.preset-bar {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.btn-preset {
  background: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  font-size: 12px;
  font-weight: 600;
  padding: 6px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-preset:hover {
  background: #2d3b55;
  color: #fff;
  border-color: #475569;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-sub);
}
textarea, input {
  background: #0d1424;
  border: 1px solid #24324f;
  color: #f1f5f9;
  border-radius: 8px;
  padding: 10px 12px;
  font-family: inherit;
  font-size: 13px;
  transition: border-color 0.15s;
}
textarea:focus, input:focus {
  outline: none;
  border-color: var(--laya);
}
textarea { resize: vertical; min-height: 85px; line-height: 1.5; }
.sub-card {
  background: #0d1424;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.sub-card-title {
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
  display: flex;
  justify-content: space-between;
}
.actions-cluster {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 4px;
}
.btn-run {
  background: linear-gradient(135deg, #0284c7, #06b6d4);
  color: #fff;
  border: none;
  font-size: 13px;
  font-weight: 700;
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.btn-run:hover:not(:disabled) {
  filter: brightness(1.15);
  box-shadow: 0 4px 14px rgba(6, 182, 212, 0.3);
}
.btn-run.kev-btn {
  background: linear-gradient(135deg, #059669, #10b981);
}
.btn-run.kev-btn:hover:not(:disabled) {
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3);
}
.btn-run.both-btn {
  grid-column: span 2;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  font-size: 14px;
  padding: 13px;
}
.btn-run.both-btn:hover:not(:disabled) {
  box-shadow: 0 4px 18px rgba(139, 92, 246, 0.35);
}
.btn-run:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.results-container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 380px;
  color: var(--text-muted);
  border: 1px dashed var(--panel-border);
  border-radius: 12px;
  gap: 12px;
}
.results-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
@media (max-width: 900px) {
  .results-grid { grid-template-columns: 1fr; }
}
.dual-results-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 1100px) {
  .dual-results-grid { grid-template-columns: 1fr; }
}
.model-column {
  background: #0d1424;
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.model-column.laya-col {
  border-top: 3px solid var(--laya);
}
.model-column.kev-col {
  border-top: 3px solid var(--kev);
}
.col-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.col-title {
  font-size: 15px;
  font-weight: 800;
  display: flex;
  align-items: center;
  gap: 6px;
}
.laya-col .col-title { color: var(--laya); }
.kev-col .col-title { color: var(--kev); }
.metric-card {
  background: var(--panel);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.metric-card-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.metric-name {
  font-size: 13px;
  font-weight: 750;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #cbd5e1;
}
.metric-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 4px;
}
.metric-badge.choice-b { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
.metric-badge.score-b { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.metric-badge.noul-b { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.top-choice-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  padding: 8px 12px;
  border-radius: 6px;
}
.top-choice-val {
  font-size: 16px;
  font-weight: 800;
  color: #fff;
}
.conf-label {
  font-size: 12px;
  color: var(--text-muted);
}
.bar-track {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.bar-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.bar-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #94a3b8;
}
.bar-fill-wrap {
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
  overflow: hidden;
}
.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.4s ease;
}
.laya-col .bar-fill { background: linear-gradient(90deg, #0284c7, #06b6d4); }
.kev-col .bar-fill { background: linear-gradient(90deg, #059669, #10b981); }
.score-highlight {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 0;
}
.score-big {
  font-size: 26px;
  font-weight: 850;
  color: #fbbf24;
}
.score-max {
  font-size: 13px;
  color: var(--text-muted);
}
.score-histogram {
  display: flex;
  align-items: flex-end;
  height: 60px;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.hist-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  height: 100%;
  justify-content: flex-end;
}
.hist-bar {
  width: 100%;
  background: #f59e0b;
  border-radius: 4px 4px 0 0;
  min-height: 2px;
  transition: height 0.4s ease;
}
.hist-lbl {
  font-size: 11px;
  color: var(--text-muted);
}
.hist-pct {
  font-size: 10px;
  font-weight: 600;
  color: #cbd5e1;
}
.noul-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}
.gauge-svg {
  width: 140px;
  height: 80px;
}
.noul-pct-big {
  font-size: 26px;
  font-weight: 850;
  color: #34d399;
  margin-top: -15px;
}
.noul-desc {
  font-size: 12px;
  color: var(--text-sub);
  margin-top: 4px;
  text-align: center;
}
.footer-meta {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-muted);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 8px;
}
details {
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.2);
  padding: 8px 12px;
  font-size: 12px;
}
summary {
  cursor: pointer;
  color: var(--text-sub);
  font-weight: 600;
}
summary:hover { color: #fff; }
pre {
  background: #070b14;
  padding: 10px;
  border-radius: 6px;
  margin-top: 8px;
  overflow-x: auto;
  font-size: 11px;
  line-height: 1.4;
  color: #94a3b8;
  max-height: 220px;
}
.alert-box {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  display: none;
}
</style>
</head>
<body>

<header>
  <div class="header-title">
    <h1><span>⚡</span> ModelRouter · 双模型三类型真实决策现场演示</h1>
    <p>Laya-421M (ModernBERT) &amp; Kev-4B (Qwen3.5) · 物理权重真实前向 · Zero Mock</p>
  </div>
  <div class="status-pill-group" id="headerPills">
    <div class="pill" id="pillA6000"><span class="dot"></span>A6000 隧道 (127.0.0.1:8000): 探测中...</div>
    <div class="pill laya-badge" id="pillLaya">Laya: 检测中...</div>
    <div class="pill kev-badge" id="pillKev">Kev: 检测中...</div>
    <div class="pill" id="pillGpu">GPU 训练: 监控中...</div>
  </div>
</header>

<main>
  <!-- Left Column: Input State & Config -->
  <section class="panel">
    <div class="panel-head">
      <h2><span>01</span> 输入 Agent 状态与问卷设定</h2>
      <div class="preset-bar">
        <button class="btn-preset" onclick="loadScenario(1)">场景 1: 软件修复</button>
        <button class="btn-preset" onclick="loadScenario(2)">场景 2: 路由决策</button>
        <button class="btn-preset" onclick="loadScenario(3)">场景 3: 生产运维</button>
      </div>
    </div>

    <div class="alert-box" id="errorBox"></div>

    <div class="form-group">
      <label for="agentState">当前 Agent 状态 / 决策前观察 (State)</label>
      <textarea id="agentState" placeholder="输入 Agent 执行过程中收集的上下文、代码 diff、错误信号与环境约束..."></textarea>
    </div>

    <!-- Question 1: Choice -->
    <div class="sub-card">
      <div class="sub-card-title">
        <span>Q1: Choice (离散候选概率分布)</span>
        <span class="metric-badge choice-b">CHOICE</span>
      </div>
      <input id="q1_inst" value="Which action should the agent take next?" placeholder="Choice Instructions"/>
      <textarea id="q1_crit" rows="3" placeholder="JSON: {'opt1': 'desc1', ...}"></textarea>
    </div>

    <!-- Question 2: Score -->
    <div class="sub-card">
      <div class="sub-card-title">
        <span>Q2: Score (有序离散等级期望)</span>
        <span class="metric-badge score-b">SCORE</span>
      </div>
      <input id="q2_inst" value="How severe and technically complex is the visible issue?" placeholder="Score Instructions"/>
      <textarea id="q2_crit" rows="2" placeholder="JSON Array: ['Level 0', 'Level 1', 'Level 2']"></textarea>
    </div>

    <!-- Question 3: Noul -->
    <div class="sub-card">
      <div class="sub-card-title">
        <span>Q3: Noul (命题成立概率 P(True))</span>
        <span class="metric-badge noul-b">NOUL</span>
      </div>
      <input id="q3_inst" value="Does the agent need an explicit test verification pass before completion?" placeholder="Noul Instructions"/>
    </div>

    <!-- Execution Cluster -->
    <div class="actions-cluster">
      <button class="btn-run" id="btnRunLaya" onclick="runSingle('laya')">▶ 运行 Laya-421M</button>
      <button class="btn-run kev-btn" id="btnRunKev" onclick="runSingle('kev')">▶ 运行 Kev-4B</button>
      <button class="btn-run both-btn" id="btnRunBoth" onclick="runDual()">⚡ 双模型同态实时对比 (Laya vs Kev)</button>
    </div>
  </section>

  <!-- Right Column: Interactive Results Dashboard -->
  <section class="panel">
    <div class="panel-head">
      <h2><span>02</span> 原生三类型决策响应 (TypeSafe System One)</h2>
      <span id="timingBadge" style="font-size:12px; color:var(--text-sub);">尚未请求</span>
    </div>

    <div id="resultsArea" class="results-container">
      <div class="empty-state" id="emptyNotice">
        <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/></svg>
        <p>点击左侧「运行 Laya」、「运行 Kev」或「双模型同态对比」，在此呈现模型真实前向计算结果。</p>
        <p style="font-size:12px; color:#475569;">绝无预填答案 · 绝无 Mock 数字 · 绝不调用生成式 GPT 假装决策</p>
      </div>

      <!-- Single Model View -->
      <div id="singleView" style="display:none;" class="results-grid"></div>

      <!-- Dual Model Comparison View -->
      <div id="dualView" style="display:none;" class="dual-results-grid"></div>

      <!-- Raw JSON Inspector -->
      <details id="rawDetails" style="display:none;">
        <summary>查看真实 API Request &amp; Response 报文 (JSON)</summary>
        <pre id="rawJsonBox"></pre>
      </details>
    </div>
  </section>
</main>

<script>
const SCENARIOS = {
  1: {
    state: "A coding agent has modified a Python AST parser function. 2 unit tests are failing with TypeError on edge cases. Remaining token budget is 25,000 tokens. Context contains 4,200 lines of traceback and code modifications.",
    q1_inst: "Which action should the agent take next?",
    q1_crit: JSON.stringify({
      "debug_tests": "Investigate failing unit tests and call stack",
      "inspect_diff": "Review recent code modifications in git diff",
      "ask_stronger_model": "Escalate to stronger reasoning model with high effort"
    }, null, 2),
    q2_inst: "How severe is the visible test failure and bug impact?",
    q2_crit: JSON.stringify([
      "Low severity (isolated unit failure)",
      "Moderate severity (module regression)",
      "Critical severity (blocking test suite)"
    ], null, 2),
    q3_inst: "Does the agent need another explicit verification pass before completion?"
  },
  2: {
    state: "User requests complex multi-step refactoring of a distributed consensus algorithm with formal TLA+ specifications. Memory overhead and correctness invariants are critical.",
    q1_inst: "Select the optimal model and native reasoning effort for the next step:",
    q1_crit: JSON.stringify({
      "gpt-6-luna:high": "Model gpt-6-luna with native reasoning effort: high",
      "gpt-6-luna:medium": "Model gpt-6-luna with native reasoning effort: medium",
      "gpt-5.6-luna:none": "Model gpt-5.6-luna with native reasoning effort: none"
    }, null, 2),
    q2_inst: "Rate the technical complexity and theoretical depth of this refactoring:",
    q2_crit: JSON.stringify([
      "Routine refactoring",
      "Moderate algorithmic difficulty",
      "Mission-critical distributed complexity"
    ], null, 2),
    q3_inst: "Does this task warrant routing to the highest tier reasoning model?"
  },
  3: {
    state: "Kubernetes pod CrashLoopBackOff detected in payment-gateway service. Latency p99 jumped to 4.2s. 502 error rate exceeds 8.4%. Canary deployment rollback is pending approval.",
    q1_inst: "Which mitigation protocol should be triggered immediately?",
    q1_crit: JSON.stringify({
      "trigger_rollback": "Trigger automated canary rollback to previous stable replica",
      "isolate_traffic": "Drain traffic from affected availability zone",
      "deep_profile": "Attach eBPF profiler to debug memory leak"
    }, null, 2),
    q2_inst: "Classify the production incident severity level:",
    q2_crit: JSON.stringify([
      "P3 - Minor degradation",
      "P2 - Significant user impact",
      "P1 - Critical revenue outage"
    ], null, 2),
    q3_inst: "Should an emergency on-call incident paging alert be triggered?"
  }
};

function loadScenario(id) {
  const s = SCENARIOS[id];
  if (!s) return;
  document.getElementById('agentState').value = s.state;
  document.getElementById('q1_inst').value = s.q1_inst;
  document.getElementById('q1_crit').value = s.q1_crit;
  document.getElementById('q2_inst').value = s.q2_inst;
  document.getElementById('q2_crit').value = s.q2_crit;
  document.getElementById('q3_inst').value = s.q3_inst;
}

function parseInputQuestions() {
  let c1, c2;
  try {
    c1 = JSON.parse(document.getElementById('q1_crit').value);
  } catch (e) {
    throw new Error("Choice criteria 必须为合法 JSON 字典: " + e.message);
  }
  try {
    c2 = JSON.parse(document.getElementById('q2_crit').value);
  } catch (e) {
    throw new Error("Score criteria 必须为合法 JSON 数组: " + e.message);
  }
  return {
    "action_choice": {
      "type": "choice",
      "instructions": document.getElementById('q1_inst').value,
      "criteria": c1
    },
    "severity_score": {
      "type": "score",
      "instructions": document.getElementById('q2_inst').value,
      "criteria": c2
    },
    "needs_retry_noul": {
      "type": "noul",
      "instructions": document.getElementById('q3_inst').value
    }
  };
}

function setButtonsLoading(loading) {
  document.getElementById('btnRunLaya').disabled = loading;
  document.getElementById('btnRunKev').disabled = loading;
  document.getElementById('btnRunBoth').disabled = loading;
  const timing = document.getElementById('timingBadge');
  if (loading) timing.textContent = "⏳ A6000 模型前向计算中...";
}

function renderChoiceCard(ans, criteria) {
  const choice = ans.choice || "N/A";
  const conf = ans.confidence != null ? (ans.confidence * 100).toFixed(1) + "%" : "N/A";
  const probs = ans.probabilities || {};

  let barsHtml = "";
  for (const [k, p] of Object.entries(probs)) {
    const isTop = k === choice;
    const pct = (p * 100).toFixed(1);
    const label = (criteria && criteria[k]) ? `${k} (${criteria[k]})` : k;
    barsHtml += `
      <div class="bar-item">
        <div class="bar-meta">
          <span style="${isTop ? 'color:#fff; font-weight:700;' : ''}">${label}</span>
          <b style="${isTop ? 'color:#38bdf8;' : ''}">${pct}%</b>
        </div>
        <div class="bar-fill-wrap">
          <div class="bar-fill" style="width:${pct}%; ${isTop ? 'filter:brightness(1.2);' : 'opacity:0.75;'}"></div>
        </div>
      </div>
    `;
  }

  return `
    <div class="metric-card">
      <div class="metric-card-head">
        <span class="metric-name">01 · Choice (最佳决策)</span>
        <span class="metric-badge choice-b">CHOICE</span>
      </div>
      <div class="top-choice-row">
        <div>
          <div style="font-size:11px; color:#64748b;">选中选项</div>
          <div class="top-choice-val">${choice}</div>
        </div>
        <div style="text-align:right;">
          <div class="conf-label">置信度</div>
          <div style="font-size:14px; font-weight:750; color:#38bdf8;">${conf}</div>
        </div>
      </div>
      <div class="bar-track">${barsHtml}</div>
    </div>
  `;
}

function renderScoreCard(ans, criteria) {
  const score = ans.score != null ? ans.score.toFixed(2) : "N/A";
  const conf = ans.confidence != null ? (ans.confidence * 100).toFixed(1) + "%" : "N/A";
  const legend = ans.legend || {};
  const probs = ans.probabilities || {};
  const numLevels = Object.keys(legend).length || (Array.isArray(criteria) ? criteria.length : 3);
  const maxIdx = Math.max(1, numLevels - 1);

  let histHtml = "";
  for (let i = 0; i < numLevels; i++) {
    const k = String(i);
    const p = probs[k] || 0.0;
    const pct = (p * 100).toFixed(1);
    const height = Math.max(4, Math.round(p * 50));
    const lbl = (Array.isArray(criteria) && criteria[i]) ? criteria[i].split(" ")[0] : `L${i}`;
    histHtml += `
      <div class="hist-col">
        <span class="hist-pct">${pct}%</span>
        <div class="hist-bar" style="height:${height}px;"></div>
        <span class="hist-lbl">${lbl}</span>
      </div>
    `;
  }

  return `
    <div class="metric-card">
      <div class="metric-card-head">
        <span class="metric-name">02 · Score (等级评分)</span>
        <span class="metric-badge score-b">SCORE</span>
      </div>
      <div class="score-highlight">
        <span class="score-big">${score}</span>
        <span class="score-max">/ ${maxIdx}.00 期望索引</span>
        <span style="margin-left:auto; font-size:12px; color:#64748b;">置信度: <b>${conf}</b></span>
      </div>
      <div class="score-histogram">${histHtml}</div>
      <div style="font-size:11px; color:#64748b; line-height:1.4;">
        有序离散概率加权: E[Index] = ∑ (i × P(Level_i))
      </div>
    </div>
  `;
}

function renderNoulCard(ans) {
  const noul = ans.noul != null ? ans.noul : 0.0;
  const pct = (noul * 100).toFixed(1);
  const strokeDash = Math.round(noul * 180);

  return `
    <div class="metric-card">
      <div class="metric-card-head">
        <span class="metric-name">03 · Noul (真值概率)</span>
        <span class="metric-badge noul-b">NOUL</span>
      </div>
      <div class="noul-center">
        <svg class="gauge-svg" viewBox="0 0 160 90">
          <path d="M 20 80 A 60 60 0 0 1 140 80" fill="none" stroke="#1e293b" stroke-width="14" stroke-linecap="round"/>
          <path d="M 20 80 A 60 60 0 0 1 140 80" fill="none" stroke="url(#noulGrad)" stroke-width="14" stroke-linecap="round" stroke-dasharray="${strokeDash} 200"/>
          <line x1="80" y1="80" x2="80" y2="20" stroke="#f59e0b" stroke-width="2" stroke-dasharray="3 3"/>
          <text x="80" y="88" fill="#64748b" font-size="9" text-anchor="middle">门限 50%</text>
          <defs>
            <linearGradient id="noulGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#0284c7"/>
              <stop offset="50%" stop-color="#10b981"/>
              <stop offset="100%" stop-color="#34d399"/>
            </linearGradient>
          </defs>
        </svg>
        <div class="noul-pct-big">${pct}%</div>
        <div class="noul-desc">P(True) · 命题成立概率</div>
      </div>
      <div style="font-size:11px; color:#64748b; text-align:center;">
        ${noul >= 0.5 ? '🟢 判定命题为真 (超越 50% 门限)' : '⚪ 判定命题不成立 (低于 50% 门限)'}
      </div>
    </div>
  `;
}

function renderModelColumn(res, criteriaChoice, criteriaScore) {
  const family = res.router_family || res.model_family || "Router";
  const ckpt = res.checkpoint_id || "default";
  const lat = res.decision_latency_ms != null ? res.decision_latency_ms.toFixed(1) + " ms" : (res.elapsed_ms ? res.elapsed_ms.toFixed(1) + " ms" : "N/A");
  const fallback = res.fallback_used ? "⚠️ Fallback" : "🟢 真实物理前向";
  const tokens = res.usage ? `${res.usage.input_tokens || 0} in` : "";

  const answers = res.answers || {};
  const cAns = answers.action_choice || answers.next_action || Object.values(answers).find(a => a.type === 'choice') || {};
  const sAns = answers.severity_score || answers.severity || Object.values(answers).find(a => a.type === 'score') || {};
  const nAns = answers.needs_retry_noul || answers.needs_retry || Object.values(answers).find(a => a.type === 'noul') || {};

  return `
    <div class="model-column ${family.toLowerCase()}-col">
      <div class="col-header">
        <div class="col-title">
          <span>${family.toUpperCase()}</span>
          <span style="font-size:12px; font-weight:600; color:var(--text-sub);">(${family.toLowerCase() === 'laya' ? '421M' : '4B'})</span>
        </div>
        <span class="pill ${family.toLowerCase() === 'laya' ? 'laya-badge' : 'kev-badge'}">${fallback}</span>
      </div>
      ${renderChoiceCard(cAns, criteriaChoice)}
      ${renderScoreCard(sAns, criteriaScore)}
      ${renderNoulCard(nAns)}
      <div class="footer-meta">
        <span>Ckpt: <b>${ckpt.length > 20 ? ckpt.slice(0, 16) + '...' : ckpt}</b></span>
        <span>耗时: <b>${lat}</b></span>
        <span>${tokens}</span>
      </div>
    </div>
  `;
}

async function runSingle(router) {
  const errBox = document.getElementById('errorBox');
  errBox.style.display = 'none';
  setButtonsLoading(true);

  try {
    const questions = parseInputQuestions();
    const state = document.getElementById('agentState').value.trim();
    if (!state) throw new Error("Agent 状态不能为空");

    const payload = {
      router: router,
      state: state,
      questions: questions
    };

    const t0 = performance.now();
    const resp = await fetch('/api/decision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (!resp.ok || data.error) throw new Error(data.error || "HTTP " + resp.status);

    const totalMs = (performance.now() - t0).toFixed(0);
    document.getElementById('timingBadge').textContent = `✅ 请求成功 · 总耗时: ${totalMs} ms`;

    document.getElementById('emptyNotice').style.display = 'none';
    document.getElementById('dualView').style.display = 'none';

    const sView = document.getElementById('singleView');
    sView.style.display = 'grid';
    sView.innerHTML = renderModelColumn(data, questions.action_choice.criteria, questions.severity_score.criteria);

    document.getElementById('rawDetails').style.display = 'block';
    document.getElementById('rawJsonBox').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    errBox.style.display = 'block';
    errBox.textContent = "请求失败: " + e.message;
    document.getElementById('timingBadge').textContent = "❌ 请求失败";
  } finally {
    setButtonsLoading(false);
  }
}

async function runDual() {
  const errBox = document.getElementById('errorBox');
  errBox.style.display = 'none';
  setButtonsLoading(true);

  try {
    const questions = parseInputQuestions();
    const state = document.getElementById('agentState').value.trim();
    if (!state) throw new Error("Agent 状态不能为空");

    const payload = {
      router: "both",
      state: state,
      questions: questions
    };

    const t0 = performance.now();
    const resp = await fetch('/api/decision', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (!resp.ok || data.error) throw new Error(data.error || "HTTP " + resp.status);

    const totalMs = (performance.now() - t0).toFixed(0);
    document.getElementById('timingBadge').textContent = `✅ 双模型对照完成 · 耗时: ${totalMs} ms`;

    document.getElementById('emptyNotice').style.display = 'none';
    document.getElementById('singleView').style.display = 'none';

    const dView = document.getElementById('dualView');
    dView.style.display = 'grid';

    const layaCol = renderModelColumn(data.laya, questions.action_choice.criteria, questions.severity_score.criteria);
    const kevCol = renderModelColumn(data.kev, questions.action_choice.criteria, questions.severity_score.criteria);
    dView.innerHTML = layaCol + kevCol;

    document.getElementById('rawDetails').style.display = 'block';
    document.getElementById('rawJsonBox').textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    errBox.style.display = 'block';
    errBox.textContent = "双模型对比请求失败: " + e.message;
    document.getElementById('timingBadge').textContent = "❌ 请求失败";
  } finally {
    setButtonsLoading(false);
  }
}

async function checkStatus() {
  try {
    const r = await fetch('/api/status');
    const d = await r.json();
    const pA = document.getElementById('pillA6000');
    if (d.router_reachable) {
      pA.className = "pill online";
      pA.innerHTML = '<span class="dot"></span>A6000 隧道 (127.0.0.1:8000): 在线';
    } else {
      pA.className = "pill offline";
      pA.innerHTML = '<span class="dot"></span>A6000 隧道: 断开';
    }

    const pL = document.getElementById('pillLaya');
    if (d.laya_loaded) {
      pL.textContent = `Laya: ${d.laya_checkpoint || 'F05'} (421M)`;
    } else {
      pL.textContent = "Laya: 未加载";
    }

    const pK = document.getElementById('pillKev');
    if (d.kev_loaded) {
      pK.textContent = `Kev: ${d.kev_checkpoint || '4B'} (Pointer)`;
    } else {
      pK.textContent = "Kev: 未加载";
    }

    const pG = document.getElementById('pillGpu');
    if (d.gpu && d.gpu.utilization_pct != null) {
      pG.textContent = `GPU: ${d.gpu.utilization_pct}% (${Math.round(d.gpu.memory_used_mb || 0)}MB)`;
    }
  } catch (e) {
    console.warn("Status check failed:", e);
  }
}

// Initial setup
loadScenario(1);
checkStatus();
setInterval(checkStatus, 8000);
</script>

</body>
</html>
'''


def fetch_remote_json(url: str, body: Optional[Dict[str, Any]] = None, timeout: float = 45.0) -> Dict[str, Any]:
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST" if payload is not None else "GET"
    )
    # Bypassing macOS system proxies
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def execute_single_system_one(family: str, state: Any, questions: Dict[str, Any]) -> Dict[str, Any]:
    t0 = time.perf_counter()
    endpoint = f"{ROUTER_URL}/system-one"
    payload = {
        "router_family": family,
        "state": state,
        "questions": questions
    }
    raw = fetch_remote_json(endpoint, payload, timeout=45.0)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    raw["elapsed_ms"] = elapsed_ms
    return raw


class DemoServerHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        logger.info(f"{self.address_string()} - {fmt % args}")

    def respond_json(self, status_code: int, data: Any):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def respond_html(self, status_code: int, html_str: str):
        body = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self.respond_html(200, HTML_CONTENT)

        if self.path == "/api/status":
            reachable = False
            laya_loaded = False
            kev_loaded = False
            laya_ckpt = "F05/best"
            kev_ckpt = "1001bb4d82..."
            gpu_info = {}

            try:
                h = fetch_remote_json(f"{ROUTER_URL}/health", timeout=3.0)
                reachable = (h.get("status") == "healthy")
                laya_loaded = bool(h.get("models_loaded", {}).get("laya"))
                kev_loaded = bool(h.get("models_loaded", {}).get("kev"))
                gpu_info = {
                    "name": h.get("gpu_name"),
                    "memory_used_mb": h.get("gpu_memory_used_mb"),
                    "utilization_pct": h.get("gpu_utilization_pct")
                }
            except Exception:
                reachable = False

            return self.respond_json(200, {
                "router_reachable": reachable,
                "router_url": ROUTER_URL,
                "laya_loaded": laya_loaded,
                "kev_loaded": kev_loaded,
                "laya_checkpoint": laya_ckpt,
                "kev_checkpoint": kev_ckpt,
                "gpu": gpu_info
            })

        return self.respond_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path != "/api/decision":
            return self.respond_json(404, {"error": "Not Found"})

        length = int(self.headers.get("Content-Length", 0))
        if length <= 0 or length > MAX_PAYLOAD:
            return self.respond_json(400, {"error": "Invalid request payload size"})

        try:
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            router = body.get("router", "laya").lower()
            state = body.get("state")
            questions = body.get("questions")

            if not state or not questions:
                return self.respond_json(400, {"error": "Missing 'state' or 'questions'"})

            if router in ("laya", "kev"):
                res = execute_single_system_one(router, state, questions)
                return self.respond_json(200, res)

            elif router in ("both", "compare"):
                # Execute Laya and Kev concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    fut_laya = executor.submit(execute_single_system_one, "laya", state, questions)
                    fut_kev = executor.submit(execute_single_system_one, "kev", state, questions)
                    res_laya = fut_laya.result()
                    res_kev = fut_kev.result()

                return self.respond_json(200, {
                    "mode": "both",
                    "laya": res_laya,
                    "kev": res_kev
                })

            else:
                return self.respond_json(400, {"error": f"Unsupported router family: {router}"})

        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            logger.error(f"Upstream HTTP error: {e.code} - {err_body}")
            return self.respond_json(502, {"error": f"Upstream A6000 Serving Error (HTTP {e.code}): {err_body}"})
        except Exception as e:
            logger.error(f"Internal Demo Error: {e}", exc_info=True)
            return self.respond_json(500, {"error": f"Demo Server Error: {str(e)}"})


def main():
    logger.info(f"Starting ModelRouter Typed Decision Demo on http://{HOST}:{PORT}")
    logger.info(f"Target Router API: {ROUTER_URL}")
    server = ThreadingHTTPServer((HOST, PORT), DemoServerHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Demo server stopping...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
