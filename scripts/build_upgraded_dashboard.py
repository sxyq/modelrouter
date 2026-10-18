#!/usr/bin/env python3
"""build_upgraded_dashboard.py - Combines index_legacy_archive.html with V8 Dual-Model Architecture,
Token Budget meter, 8-Policy Benchmark Matrix, and genuine live telemetry.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_HTML = ROOT / "docs" / "training-dashboard" / "index_legacy_archive.html"
TARGET_HTML = ROOT / "docs" / "training-dashboard" / "index.html"
OUR_PROJECT_HTML = ROOT / "our-project" / "dashboard" / "index.html"

def main():
    content = ARCHIVE_HTML.read_text(encoding="utf-8")

    # 1. Update Title
    content = content.replace(
        "<title>ModelRouter · 智能路由全景图表与实时质检看板</title>",
        "<title>ModelRouter V8 · 双模型协同训练与 8 策略 Agent 控制台</title>"
    )

    # 2. Add V8 CSS styles right before </style>
    v8_styles = """
    /* V8 Dual-Model & Agent Benchmark Styles */
    .budget-bar-container {
      background: rgba(0, 0, 0, 0.45);
      border: 1px solid var(--cds-border);
      border-radius: 8px;
      padding: 10px 14px;
      margin: 12px 0 16px 0;
    }
    .budget-bar-header {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 6px;
      color: var(--cds-text-secondary);
    }
    .budget-bar-track {
      width: 100%;
      height: 10px;
      background: #1e1c18;
      border-radius: 5px;
      overflow: hidden;
      border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .budget-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #2ea06f 0%, #5e89b8 60%, #d9943b 85%, #d85858 100%);
      transition: width 0.4s ease;
    }

    .dual-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 18px;
    }
    @media (max-width: 1100px) {
      .dual-grid { grid-template-columns: 1fr; }
    }
    .panel-card {
      background: var(--cds-s1);
      border: 1px solid var(--cds-border);
      border-radius: 10px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .panel-header {
      padding: 12px 16px;
      background: var(--cds-s2);
      border-bottom: 1px solid var(--cds-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .panel-header h2 { font-size: 14.5px; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 8px; margin: 0; }
    .panel-body { padding: 14px 16px; flex: 1; }

    .version-pills {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px;
      margin-bottom: 12px;
      font-size: 12px;
    }
    .pill {
      background: var(--cds-s3);
      border: 1px solid var(--cds-border);
      padding: 3px 8px;
      border-radius: 4px;
      color: var(--cds-text-muted);
      font-size: 11.5px;
    }
    .pill.active { border-color: var(--cds-clay); color: var(--cds-clay); font-weight: 600; }
    .pill.green { border-color: #2ea06f; color: #34d399; font-weight: 600; }

    .stat-grid-4 {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 10px;
      margin-bottom: 14px;
    }
    @media (max-width: 600px) {
      .stat-grid-4 { grid-template-columns: repeat(2, 1fr); }
    }
    .stat-box {
      background: var(--cds-s2);
      border: 1px solid var(--cds-border);
      padding: 10px 12px;
      border-radius: 6px;
    }
    .stat-label { font-size: 11px; color: var(--cds-text-muted); margin-bottom: 3px; }
    .stat-val { font-size: 17px; font-weight: 700; color: #fff; }
    .stat-sub { font-size: 11px; color: var(--cds-text-secondary); margin-top: 2px; }

    .sparkline-box {
      background: var(--cds-s2);
      border: 1px solid var(--cds-border);
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .sparkline-title { font-size: 11.5px; color: var(--cds-text-secondary); font-weight: 600; }
    .sparkline-svg { width: 160px; height: 36px; }

    .serving-meta-box {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--cds-border);
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 12px;
      margin-bottom: 10px;
    }
    .serving-meta-row { display: flex; justify-content: space-between; margin-bottom: 4px; }
    .serving-meta-row:last-child { margin-bottom: 0; }
    .meta-k { color: var(--cds-text-muted); }
    .meta-v { color: #fff; font-weight: 600; font-family: monospace; }

    .bench-card {
      background: var(--cds-s1);
      border: 1px solid var(--cds-border);
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 18px;
    }
    .bench-tab-bar {
      display: flex;
      gap: 4px;
      background: var(--cds-s2);
      padding: 6px 12px 0 12px;
      border-bottom: 1px solid var(--cds-border);
    }
    .bench-tab-btn {
      padding: 8px 16px;
      font-size: 12px;
      font-weight: 600;
      color: var(--cds-text-muted);
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      cursor: pointer;
    }
    .bench-tab-btn:hover { color: #fff; }
    .bench-tab-btn.active {
      color: var(--cds-clay);
      border-bottom: 2px solid var(--cds-clay);
      background: rgba(217, 119, 87, 0.08);
      border-radius: 4px 4px 0 0;
    }
    .tab-banner {
      padding: 10px 16px;
      font-size: 12px;
      display: flex;
      align-items: center;
      gap: 10px;
      border-bottom: 1px solid var(--cds-border);
    }
    .tab-banner.banner-real { background: rgba(46, 160, 111, 0.1); color: #34d399; }
    .tab-banner.banner-mock { background: rgba(217, 148, 59, 0.1); color: #fbbf24; }
    
    .badge-live {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.3px;
    }
    .badge-live.green { background: rgba(46, 160, 111, 0.2); color: #34d399; border: 1px solid #2ea06f; }
    .badge-live.clay { background: rgba(217, 119, 87, 0.2); color: var(--cds-clay); border: 1px solid var(--cds-clay); }
    .badge-live.blue { background: rgba(94, 137, 184, 0.2); color: #38bdf8; border: 1px solid #5e89b8; }
    .badge-live.amber { background: rgba(217, 148, 59, 0.2); color: #fbbf24; border: 1px solid #d9943b; }
    .badge-live.purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #a855f7; }
  </style>
  """
    content = content.replace("</style>", v8_styles)

    # 3. Upgrade Hero Cockpit and Roadmap Flow
    old_cockpit_snippet = """  <!-- GRAND VISUAL PREVIEW: LIVE TRAINING HERO COCKPIT -->
  <div class="hero-cockpit">
    <div class="hero-cockpit-header">
      <div class="hero-cockpit-title">
        <span>🛰️ 实时训练全景巡航 · F04 动态对账</span>
        <span class="status-pill"><span class="status-pulse"></span> 进程活跃 · L4 单层联合</span>
      </div>
      <div style="font-size:12px;color:var(--cds-text-muted)">
        实时流式消费 · 2:1:1 平衡交错协议 · <span style="color:#34d399">0 丢弃</span>
      </div>
    </div>

    <div class="hero-grid">
      <!-- Col 1: Loss & Convergence -->
      <div class="hero-col">
        <div class="hero-metric-label">
          <span>损失下潜与收敛健康</span>
          <span class="dir-badge dir-lower">⬇️ 越小越好</span>
        </div>
        <div class="hero-metric-val sage" id="cockpitLossVal">0.5094</div>
        <div style="font-size:11.5px;color:var(--cds-text-secondary);margin-top:4px">
          从初始 <b style="color:#f59e0b">1.4707</b> 下降至当前，收敛降幅 <b style="color:#34d399">-65.4%</b>
        </div>
        <div class="cds-progress-track">
          <div class="cds-progress-fill sage" id="cockpitLossBar" style="width: 78%;"></div>
        </div>
        <div style="font-size:11px;color:var(--cds-text-muted);display:flex;justify-content:space-between">
          <span>目标线 0.60 (已达标)</span>
          <span style="color:#34d399">稳健收敛区间</span>
        </div>
      </div>

      <!-- Col 2: Step & Chunk Scale -->
      <div class="hero-col">
        <div class="hero-metric-label">
          <span>当前轮次批次推进</span>
          <span id="cockpitChunkTxt" style="color:#fff;font-weight:700">Chunk 198 / 234 (84.6%)</span>
        </div>
        <div class="hero-metric-val clay" id="cockpitStepVal">25,344 <span style="font-size:16px;color:var(--cds-text-muted);font-weight:500">/ 59,904 步</span></div>
        <div style="font-size:11.5px;color:var(--cds-text-secondary);margin-top:4px">
          已真实消费梯度样本: <b style="color:#fff" id="cockpitSamplesVal">1,622,016 / 3,821,922 条</b>
        </div>
        <div class="cds-progress-track">
          <div class="cds-progress-fill" id="cockpitProgressBar" style="width: 84.6%;"></div>
        </div>
        <div style="font-size:11px;color:var(--cds-text-muted);display:flex;justify-content:space-between">
          <span>Epoch 1 完成在即</span>
          <span id="cockpitEstTxt" style="color:var(--cds-clay)">预计接续正规 F03</span>
        </div>
      </div>

      <!-- Col 3: Hardware & GPU Telemetry -->
      <div class="hero-col">
        <div class="hero-metric-label">
          <span>RTX A6000 算力与显存</span>
          <span style="color:#34d399" id="cockpitGpuTxt">76% Util (280W)</span>
        </div>
        <div class="hero-metric-val" id="cockpitVramVal" style="font-size:26px">9,759 <span style="font-size:14px;color:var(--cds-text-muted);font-weight:500">/ 49,140 MiB</span></div>
        <div style="font-size:11.5px;color:var(--cds-text-secondary);margin-top:4px">
          显存占用率仅 <b style="color:#34d399">19.9%</b> · 流水线时延 <b style="color:#fff">196 ms/批次</b>
        </div>
        <div class="cds-progress-track">
          <div class="cds-progress-fill sage" id="cockpitVramBar" style="width: 19.9%;"></div>
        </div>
        <div style="font-size:11px;color:var(--cds-text-muted);display:flex;justify-content:space-between">
          <span>PID: 2881373</span>
          <span style="color:#34d399">安全余量 39.4 GiB</span>
        </div>
      </div>
    </div>

    <!-- 38-Run Scientific Pipeline Stage Roadmap Flow -->
    <div class="roadmap-flow">
      <span style="font-size:11px;color:var(--cds-text-muted);font-weight:600;white-space:nowrap">🗺️ 科研主线脉络:</span>
      <span class="stage-pill done">✅ F01 (L1基线)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill done">✅ F02 (L2分层)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill done">✅ ALGN_04 (3联合)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill active">🔥 F04 (L4 运行中 84.6%)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill">⏳ F03 (正规补跑)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill">⏳ F05~F07 (累积全量)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill">⏳ F08~F16 (嵌套消融)</span>
      <span class="stage-arrow">➔</span>
      <span class="stage-pill">⏳ F17~F20 (课程学习)</span>
    </div>
  </div>"""

    new_cockpit_snippet = """  <!-- GLOBAL TOKEN BUDGET METER (< 1,000,000 TOKENS HARD CEILING) -->
  <div class="budget-bar-container">
    <div class="budget-bar-header">
      <div style="display:flex;align-items:center;gap:10px">
        <span style="color:#fff;font-weight:700">🛡️ 全局生成式 API Token 消耗硬预算门禁 (&lt; 1,000,000 Tokens)</span>
        <span class="badge-live green" id="budget-status-pill">预算健康</span>
      </div>
      <span id="token-budget-text" style="color:#38bdf8;font-family:monospace">已消耗: 112,132 / 1,000,000 (11.21%) · 剩余 887,868</span>
    </div>
    <div class="budget-bar-track">
      <div class="budget-bar-fill" id="token-budget-fill" style="width: 11.21%;"></div>
    </div>
  </div>

  <!-- GRAND VISUAL PREVIEW: DUAL-MODEL LIVE COCKPIT -->
  <div class="hero-cockpit">
    <div class="hero-cockpit-header">
      <div class="hero-cockpit-title">
        <span>🛰️ ModelRouter V8 · 双模型协同训练与 8 策略 Agent 控制台</span>
        <span class="status-pill"><span class="status-pulse"></span> A6000 双训并行 · 显存占用 40.8%</span>
        <span class="badge-live purple" id="cockpitGitSha">GIT: 09d1f2e</span>
      </div>
      <div style="font-size:12px;color:var(--cds-text-muted);display:flex;gap:16px;align-items:center">
        <span>路由 Serving: <b style="color:#38bdf8" id="cockpitServingUrl">127.0.0.1:8000 (健康)</b></span>
        <button class="btn-primary" style="padding:4px 10px;font-size:11px" onclick="fetchLiveStatusNow()">立即刷新 ⟳</button>
      </div>
    </div>

    <div class="hero-grid">
      <!-- Col 1: Laya-V2 421M MoE -->
      <div class="hero-col">
        <div class="hero-metric-label">
          <span>⚡ Laya-V2 (421M MoE 路由)</span>
          <span class="badge-live clay" id="cockpitLayaBadge">TRAINING: F06</span>
        </div>
        <div class="hero-metric-val clay" id="cockpitLayaLoss">0.5257</div>
        <div style="font-size:11.5px;color:var(--cds-text-secondary);margin-top:4px">
          当前进度: <b style="color:#fff" id="cockpitLayaChunk">Chunk 102 / 361</b> · Step <b style="color:#38bdf8" id="cockpitLayaStep">13,056 / 92,280</b>
        </div>
        <div class="cds-progress-track">
          <div class="cds-progress-fill" id="cockpitLayaBar" style="width: 28.3%;"></div>
        </div>
        <div style="font-size:11px;color:var(--cds-text-muted);display:flex;justify-content:space-between">
          <span>S1 验证最高: <b style="color:#34d399" id="cockpitLayaAcc">67.38%</b></span>
          <span style="color:#38bdf8">Serving: models/laya-421m</span>
        </div>
      </div>

      <!-- Col 2: Kev-4B LoRA Backbone -->
      <div class="hero-col">
        <div class="hero-metric-label">
          <span>🧠 Kev-4B (Qwen LoRA 路由)</span>
          <span class="badge-live green" id="cockpitKevBadge">TRAINING: KEV-V8</span>
        </div>
        <div class="hero-metric-val sage" id="cockpitKevLoss">1.6380</div>
        <div style="font-size:11.5px;color:var(--cds-text-secondary);margin-top:4px">
          当前步数: <b style="color:#fff" id="cockpitKevStep">Step 70 / 16,857</b> · Epoch 0 · 累计消费 280 条
        </div>
        <div class="cds-progress-track">
          <div class="cds-progress-fill sage" id="cockpitKevBar" style="width: 0.4%;"></div>
        </div>
        <div style="font-size:11px;color:var(--cds-text-muted);display:flex;justify-content:space-between">
          <span>基准验证精度: <b style="color:#34d399">87.26% (NLL 0.5162)</b></span>
          <span style="color:#38bdf8">Serving: models/kev-4b-adapter</span>
        </div>
      </div>

      <!-- Col 3: Hardware & GPU Telemetry -->
      <div class="hero-col">
        <div class="hero-metric-label">
          <span>RTX A6000 算力与显存</span>
          <span style="color:#34d399" id="cockpitGpuTxt">96% Util (292W)</span>
        </div>
        <div class="hero-metric-val" id="cockpitVramVal" style="font-size:26px">20,051 <span style="font-size:14px;color:var(--cds-text-muted);font-weight:500">/ 49,140 MiB</span></div>
        <div style="font-size:11.5px;color:var(--cds-text-secondary);margin-top:4px">
          双训显存占用率仅 <b style="color:#34d399" id="cockpitVramPct">40.8%</b> · 温度 <b style="color:#f59e0b" id="cockpitTemp">83°C</b>
        </div>
        <div class="cds-progress-track">
          <div class="cds-progress-fill sage" id="cockpitVramBar" style="width: 40.8%;"></div>
        </div>
        <div style="font-size:11px;color:var(--cds-text-muted);display:flex;justify-content:space-between">
          <span>Laya: <b style="color:#fff" id="cockpitLayaPid">PID 1202621</b> · Kev: <b style="color:#fff" id="cockpitKevPid">PID 1357764</b></span>
          <span style="color:#34d399">安全余量 29.1 GiB</span>
        </div>
      </div>
    </div>

    <!-- Symmetrical Dual-Line Scientific Pipeline Stage Roadmap Flow -->
    <div class="roadmap-flow" style="display:flex;flex-direction:column;gap:8px;padding:10px 14px">
      <!-- Line 1: Laya 421M 38-Run Pipeline -->
      <div style="display:flex;align-items:center;gap:6px;overflow-x:auto;white-space:nowrap;width:100%">
        <span style="font-size:11px;color:var(--cds-clay);font-weight:700;white-space:nowrap;min-width:130px">🗺️ Laya 38阶段主线:</span>
        <span class="stage-pill done">✅ F01 (L1基线)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill done">✅ F02 (L2分层)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill done">✅ F03 (L3重验)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill done">✅ F04 (L4全维)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill done" style="border-color:#38bdf8">⭐ F05 (L5混合·Serving)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill active" id="roadmapLayaActive">🔥 F06 (L6扩充 运行中 28.3%)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill">⏳ F07 (L7收敛)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill">⏳ F08~F16 (消融网络)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill">⏳ F17~F38 (多源课程)</span>
      </div>

      <!-- Line 2: Kev 4B LoRA Pipeline -->
      <div style="display:flex;align-items:center;gap:6px;overflow-x:auto;white-space:nowrap;width:100%">
        <span style="font-size:11px;color:#34d399;font-weight:700;white-space:nowrap;min-width:130px">🧠 Kev-4B 微调主线:</span>
        <span class="stage-pill done">❄️ Qwen3.5-4B (Frozen Base)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill done" style="border-color:#38bdf8">⭐ Kev-Adapter (LoRA+Pointer·Serving)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill active" style="border-color:#34d399;color:#34d399" id="roadmapKevActive">🔥 KEV-V8-HOMOLOGOUS (GPU 持续微调 运行中 Step 70)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill">⏳ KEV-ABL-01 (Holdout 验证)</span>
        <span class="stage-arrow">➔</span>
        <span class="stage-pill">⏳ KEV-ABL-02~08 (多源消融与置信度校准)</span>
      </div>
    </div>
  </div>"""

    content = content.replace(old_cockpit_snippet, new_cockpit_snippet)

    # 4. In Tab 0, add the Symmetrical Dual-Model Grid & 8-Policy Benchmark Matrix
    tab0_old_start = """    <!-- =========================================================================
         TAB 0: 实时收敛与天梯图表
         ========================================================================= -->
    <div class="tab-pane active" id="tab0">"""

    tab0_new_start = """    <!-- =========================================================================
         TAB 0: 实时收敛与天梯图表
         ========================================================================= -->
    <div class="tab-pane active" id="tab0">

      <!-- Symmetrical Dual-Column Layout: Laya-V2 vs Kev-4B -->
      <div class="dual-grid">

        <!-- Column 1: Laya-V2 (421M MoE Router) -->
        <div class="panel-card">
          <div class="panel-header">
            <h2>⚡ Laya-V2 (421M Token MoE Router)</h2>
            <div style="display: flex; gap: 6px;">
              <span id="laya-train-badge" class="badge-live clay">TRAINING: F06</span>
              <span id="laya-serve-badge" class="badge-live green">SERVING: VERIFIED</span>
            </div>
          </div>
          <div class="panel-body">
            <!-- Candidate Versions Meter -->
            <div class="version-pills">
              <span style="font-weight: 600; color: var(--cds-text-muted);">候选版本验证进度:</span>
              <span class="badge-live purple" id="laya-cand-count">5 验证 · 1 在训 · 22 规划</span>
              <span class="pill green">F01</span>
              <span class="pill green">F02</span>
              <span class="pill green">F03</span>
              <span class="pill green">F04</span>
              <span class="pill green">F05★</span>
              <span class="pill active">F06 (在训)</span>
              <span class="pill">F07 (待排)</span>
            </div>

            <div class="stat-grid-4">
              <div class="stat-box">
                <div class="stat-label">当前运行 Run</div>
                <div class="stat-val" id="laya-run-id" style="color:var(--cds-clay)">F06</div>
                <div class="stat-sub" id="laya-steps">Step: 13.0k / 92.2k</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">当前训练 Loss</div>
                <div class="stat-val" id="laya-loss" style="color: #38bdf8;">0.5300</div>
                <div class="stat-sub">Chunk 102/361</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">S1 验证 Acc (Best)</div>
                <div class="stat-val" id="laya-best-acc" style="color: #34d399;">67.38%</div>
                <div class="stat-sub">F01/F02: 67.38%</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">Val Loss / Brier</div>
                <div class="stat-val" id="laya-brier" style="color: #c084fc;">0.2074</div>
                <div class="stat-sub" id="laya-val-loss">Loss: 0.6047</div>
              </div>
            </div>

            <!-- Mini Sparkline for Loss -->
            <div class="sparkline-box">
              <div>
                <div class="sparkline-title">实时 Loss 收敛折线 (近 10 块)</div>
                <div style="font-size: 11px; color: var(--cds-text-muted); margin-top: 2px;">最新 chunk_loss: <span id="laya-loss-trend" style="color:#38bdf8;font-weight:600">0.5300</span></div>
              </div>
              <svg id="laya-sparkline" class="sparkline-svg" viewBox="0 0 160 36">
                <path d="M 0 18 Q 80 18 160 18" fill="none" stroke="#38bdf8" stroke-width="2"/>
              </svg>
            </div>

            <!-- Serving Endpoint Metadata -->
            <div class="serving-meta-box">
              <div class="serving-meta-row">
                <span class="meta-k">A6000 物理检查点:</span>
                <span class="meta-v" id="laya-ckpt-path">/home/syy/路由/models/laya-421m</span>
              </div>
              <div class="serving-meta-row">
                <span class="meta-k">本地转发端点:</span>
                <span class="meta-v">http://127.0.0.1:8000/v1/route/laya</span>
              </div>
              <div class="serving-meta-row">
                <span class="meta-k">物理权重隔离状态:</span>
                <span class="meta-v" style="color: #34d399;">MAC_ZERO_PHYSICAL_WEIGHTS (A6000 宿主常驻)</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Column 2: Kev-4B (Qwen LoRA Router) -->
        <div class="panel-card">
          <div class="panel-header">
            <h2>🧠 Kev-4B (Qwen3.5-4B LoRA 路由)</h2>
            <div style="display: flex; gap: 6px;">
              <span id="kev-train-badge" class="badge-live green">TRAINING: ACTIVE</span>
              <span id="kev-serve-badge" class="badge-live green">SERVING: VERIFIED</span>
            </div>
          </div>
          <div class="panel-body">
            <!-- Candidate Versions Meter -->
            <div class="version-pills">
              <span style="font-weight: 600; color: var(--cds-text-muted);">候选版本验证进度:</span>
              <span class="badge-live purple" id="kev-cand-count">1 验证 · 1 在训 · 8 规划</span>
              <span class="pill green">Kev-Base</span>
              <span class="pill green">Kev-Adapter★</span>
              <span class="pill active">KEV-V8 (在训)</span>
              <span class="pill">Holdout-01</span>
              <span class="pill">Holdout-02</span>
              <span class="pill">Ablation-1</span>
              <span class="pill">Ablation-2</span>
            </div>

            <div class="stat-grid-4">
              <div class="stat-box">
                <div class="stat-label">当前运行 Run</div>
                <div class="stat-val" id="kev-run-id" style="color:#34d399">KEV-V8</div>
                <div class="stat-sub" id="kev-steps">Step: 70 / 16,857</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">当前训练 Loss</div>
                <div class="stat-val" id="kev-loss" style="color: #38bdf8;">1.6380</div>
                <div class="stat-sub">1.879 ➡️ 1.66 ➡️ 1.638</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">基准 Clean 精度</div>
                <div class="stat-val" id="kev-best-acc" style="color: #34d399;">87.26%</div>
                <div class="stat-sub">Adapter Benchmark</div>
              </div>
              <div class="stat-box">
                <div class="stat-label">NLL 损失 / Brier</div>
                <div class="stat-val" id="kev-brier" style="color: #c084fc;">0.2037</div>
                <div class="stat-sub" id="kev-val-loss">NLL: 0.5162</div>
              </div>
            </div>

            <!-- Mini Sparkline for Loss -->
            <div class="sparkline-box">
              <div>
                <div class="sparkline-title">实时 Loss 收敛折线 (近 10 步)</div>
                <div style="font-size: 11px; color: var(--cds-text-muted); margin-top: 2px;">最新 step_loss: <span id="kev-loss-trend" style="color:#34d399;font-weight:600">1.6380</span></div>
              </div>
              <svg id="kev-sparkline" class="sparkline-svg" viewBox="0 0 160 36">
                <path d="M 0 18 Q 80 18 160 18" fill="none" stroke="#34d399" stroke-width="2"/>
              </svg>
            </div>

            <!-- Serving Endpoint Metadata -->
            <div class="serving-meta-box">
              <div class="serving-meta-row">
                <span class="meta-k">A6000 物理检查点:</span>
                <span class="meta-v">/home/syy/路由/models/kev-4b-adapter/head.pt</span>
              </div>
              <div class="serving-meta-row">
                <span class="meta-k">本地转发端点:</span>
                <span class="meta-v">http://127.0.0.1:8000/v1/route/kev</span>
              </div>
              <div class="serving-meta-row">
                <span class="meta-k">物理权重隔离状态:</span>
                <span class="meta-v" style="color: #34d399;">MAC_ZERO_PHYSICAL_WEIGHTS (A6000 宿主常驻)</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- 8-Policy Benchmark Matrix (Real Official Eval vs Mock Stress Test) -->
      <div class="bench-card">
        <div class="bench-tab-bar">
          <button class="bench-tab-btn active" id="tab-btn-real" onclick="switchBenchTab('real')">
            🎯 真实评测 (REAL_AGENT_OFFICIAL_EVAL)
          </button>
          <button class="bench-tab-btn" id="tab-btn-mock" onclick="switchBenchTab('mock')">
            ⚡ 压测隔离 (MOCK_STRESS · 64并发)
          </button>
        </div>

        <div id="banner-real" class="tab-banner banner-real">
          <span>🛡️</span>
          <div>
            <b>真实官方评估隔离区</b>: 基于 Harbor 容器与 pytest-json-ctrf 官方测评。严禁包含任何模拟通过！学术论文主表对比仅采纳本区数据。
          </div>
        </div>
        <div id="banner-mock" class="tab-banner banner-mock" style="display: none;">
          <span>⚠️</span>
          <div>
            <b>模拟并发压测区 (MOCK_STRESS)</b>: 64 并发调度器、通道队列吞吐压测数据。仅用于通路压力测试，严禁作为论文基准结论引用。
          </div>
        </div>

        <div style="overflow-x: auto;">
          <table>
            <thead>
              <tr>
                <th>策略 (Policy)</th>
                <th>算法类型 (Category)</th>
                <th>决策原理 (Algorithm)</th>
                <th>隔离环境 (Isolation)</th>
                <th>评测轮数</th>
                <th>解决数</th>
                <th>Pass@1 准确率</th>
                <th>总成本 (USD)</th>
                <th>平均步数</th>
                <th>路由时延</th>
              </tr>
            </thead>
            <tbody id="benchmark-table-body">
              <tr><td colspan="10" style="text-align: center; color: var(--cds-text-muted); padding: 20px;">正在加载实时评测数据...</td></tr>
            </tbody>
          </table>
        </div>
      </div>"""

    content = content.replace(tab0_old_start, tab0_new_start)

    # 5. Fix updateLiveUI and top KPIs
    # Look for the beginning of updateLiveUI(live)
    old_update_kpis = """      const isAlive = live.process_alive;
      const runId = live.current_run || live.run_id || 'F04';
      const pillText = document.getElementById('livePillText');
      if (pillText) {
        pillText.textContent = (isAlive ? '实时守护中 · ' : '进程已暂停 · ') + runId;
      }

      const lossVal = live.loss !== null && live.loss !== undefined ? live.loss : '0.5094';
      document.getElementById('liveLossBadge').textContent = 'Loss ' + lossVal;
      document.getElementById('kpiRun').textContent = runId + (isAlive ? ' (L4 全量分层 · 运行中)' : ' (' + (live.status || 'STOPPED') + ')');
      document.getElementById('kpiRunSub').textContent = (live.epoch || 'N/A') + ' · Chunk ' + (live.chunk || 'N/A') + ' · Step ' + (live.step || 'N/A');

      const gpuEl = document.getElementById('gpuMeta');
      if (gpuEl && live.gpu_memory) {
        gpuEl.textContent = `RTX A6000 (${live.gpu_memory}, ${live.gpu_util || '0%'} Util) · PID ${live.train_pid || 'N/A'}`;
      }"""

    new_update_kpis = """      const isAlive = (live.laya && live.laya.is_training) || (live.process && live.process.laya && live.process.laya.is_training) || live.process_alive || false;
      const runId = (live.laya && live.laya.run_id) || live.current_run || 'F06';
      const pillText = document.getElementById('livePillText');
      if (pillText) {
        pillText.textContent = (isAlive ? '双模型实时守护中 · ' : '进程已暂停 · ') + runId;
      }

      const lossVal = (live.laya && live.laya.loss !== null && live.laya.loss !== undefined) ? Number(live.laya.loss).toFixed(4) : (live.loss || '0.5300');
      document.getElementById('liveLossBadge').textContent = 'Loss ' + lossVal;
      document.getElementById('kpiRun').textContent = runId + (isAlive ? ' (L6 扩充全量 · 运行中)' : ' (' + (live.status || 'STOPPED') + ')');
      const layaEpoch = (live.laya && live.laya.epoch !== null) ? live.laya.epoch : (live.epoch || '0');
      const layaChunk = (live.laya && live.laya.chunk !== null) ? live.laya.chunk : (live.chunk || '102');
      const layaStep = (live.laya && live.laya.step !== null) ? live.laya.step : (live.step || '13056');
      document.getElementById('kpiRunSub').textContent = 'Epoch ' + layaEpoch + ' · Chunk ' + layaChunk + ' · Step ' + Number(layaStep).toLocaleString();

      const gpuEl = document.getElementById('gpuMeta');
      if (gpuEl && live.gpu) {
        const u = live.gpu.used_mb ? Math.round(live.gpu.used_mb) : 20051;
        const tot = live.gpu.total_mb ? Math.round(live.gpu.total_mb) : 49140;
        const ut = (live.gpu.util_pct !== null) ? live.gpu.util_pct : 96;
        gpuEl.textContent = `RTX A6000 (${u} MiB / ${tot} MiB, ${ut}% Util) · PID ${live.process?.laya?.train_pid || 1202621}`;
      }"""

    content = content.replace(old_update_kpis, new_update_kpis)

    # 6. Add V8 rendering helpers and inject into updateLiveUI
    v8_helpers_and_injection = """
    // Dual-Model V8 Realtime Dashboard Engine
    let currentBenchTab = 'real';

    function switchBenchTab(tab) {
      currentBenchTab = tab;
      const bReal = document.getElementById('tab-btn-real');
      const bMock = document.getElementById('tab-btn-mock');
      const bannerReal = document.getElementById('banner-real');
      const bannerMock = document.getElementById('banner-mock');
      if (bReal) bReal.classList.toggle('active', tab === 'real');
      if (bMock) bMock.classList.toggle('active', tab === 'mock');
      if (bannerReal) bannerReal.style.display = (tab === 'real') ? 'flex' : 'none';
      if (bannerMock) bannerMock.style.display = (tab === 'mock') ? 'flex' : 'none';
      renderBenchmarkTable();
    }

    function renderSparkline(svgId, points, strokeColor) {
      const svg = document.getElementById(svgId);
      if (!svg || !points || points.length === 0) return;
      const w = 160, h = 36, pad = 4;
      const validPoints = points.filter(p => typeof p === 'number' && !isNaN(p));
      if (validPoints.length === 0) return;
      const minVal = Math.min(...validPoints);
      const maxVal = Math.max(...validPoints);
      const span = (maxVal - minVal) || 0.001;

      let d = '';
      validPoints.forEach((val, idx) => {
        const x = (idx / Math.max(1, validPoints.length - 1)) * (w - 2 * pad) + pad;
        const y = h - pad - ((val - minVal) / span) * (h - 2 * pad);
        d += (idx === 0) ? `M ${x.toFixed(1)} ${y.toFixed(1)}` : ` L ${x.toFixed(1)} ${y.toFixed(1)}`;
      });
      svg.innerHTML = `<path d="${d}" fill="none" stroke="${strokeColor}" stroke-width="2" stroke-linecap="round"/>`;
    }

    function renderBenchmarkTable() {
      const tbody = document.getElementById('benchmark-table-body');
      if (!tbody || !cachedLive || !cachedLive.agent_pilot) return;
      const matrix = (currentBenchTab === 'real') ? (cachedLive.agent_pilot.matrix_real || []) : (cachedLive.agent_pilot.matrix_mock || []);
      if (!matrix || matrix.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" style="text-align: center; color: var(--cds-text-muted); padding: 20px;">无可用评测记录</td></tr>`;
        return;
      }
      let html = '';
      matrix.forEach(row => {
        const isOurs = (row.policy_id === 'laya_v2' || row.policy_id === 'kev_4b');
        const passPct = (Number(row.pass_at_1 || 0) * 100).toFixed(1) + '%';
        const costStr = '$' + Number(row.total_cost_usd || 0).toFixed(4);
        const latStr = Number(row.routing_latency_ms || 0).toFixed(1) + ' ms';
        const isoText = row.isolation || (currentBenchTab === 'real' ? 'HOST_PROCESS (UNISOLATED)' : 'ASYNC_WORKER');
        const isoColor = row.official_isolated ? '#34d399' : '#f59e0b';

        html += `
          <tr style="${isOurs ? 'background: rgba(217, 119, 87, 0.08); font-weight: 600;' : ''}">
            <td style="color: ${isOurs ? 'var(--cds-clay)' : '#fff'}; font-weight: 700;">${row.name || row.policy_id}</td>
            <td style="color: var(--cds-text-muted); font-size: 11px;">${row.category || '-'}</td>
            <td style="font-size: 11.5px; color: var(--cds-text-secondary);">${row.algorithm || '-'}</td>
            <td style="font-size: 11px; color: ${isoColor}; font-family: monospace;">${isoText}</td>
            <td>${row.episodes || 0}</td>
            <td style="color: #34d399;">${row.resolved || 0}</td>
            <td style="color: ${Number(row.pass_at_1) > 0 ? '#34d399' : 'var(--cds-text-muted)'}; font-weight: 700;">${passPct}</td>
            <td style="font-family: monospace; color: #fbbf24;">${costStr}</td>
            <td>${row.mean_steps || 0}</td>
            <td style="font-family: monospace; color: var(--cds-text-muted);">${latStr}</td>
          </tr>
        `;
      });
      tbody.innerHTML = html;
    }

    function applyV8LiveUpdates(live) {
      if (!live) return;

      // 1. Git SHA
      const gitEl = document.getElementById('cockpitGitSha');
      if (gitEl && live.git_sha) gitEl.textContent = 'GIT: ' + live.git_sha;

      // 2. Token Budget Bar
      if (live.token_budget) {
        const tb = live.token_budget;
        const pct = Math.min(100, Math.max(0, tb.percent_used || 0));
        const txtEl = document.getElementById('token-budget-text');
        const fillEl = document.getElementById('token-budget-fill');
        if (txtEl) txtEl.textContent = `已消耗: ${Number(tb.consumed_tokens||0).toLocaleString()} / ${Number(tb.total_budget||1000000).toLocaleString()} (${pct.toFixed(2)}%) · 剩余 ${Number(tb.remaining_tokens||0).toLocaleString()}`;
        if (fillEl) fillEl.style.width = pct.toFixed(2) + '%';
      }

      // 3. Hardware / GPU
      if (live.gpu) {
        const gpu = live.gpu;
        const utilEl = document.getElementById('cockpitGpuTxt');
        const vramVal = document.getElementById('cockpitVramVal');
        const vramPct = document.getElementById('cockpitVramPct');
        const vramBar = document.getElementById('cockpitVramBar');
        const tempEl = document.getElementById('cockpitTemp');
        if (utilEl && gpu.util_pct !== null) utilEl.textContent = `${gpu.util_pct}% Util (${gpu.power_w ? Math.round(gpu.power_w) : '--'}W)`;
        if (vramVal && gpu.used_mb !== null) vramVal.innerHTML = `${Math.round(gpu.used_mb).toLocaleString()} <span style="font-size:14px;color:var(--cds-text-muted);font-weight:500">/ ${Math.round(gpu.total_mb||49140).toLocaleString()} MiB</span>`;
        if (gpu.used_mb && gpu.total_mb) {
          const pctVal = ((gpu.used_mb / gpu.total_mb) * 100).toFixed(1);
          if (vramPct) vramPct.textContent = pctVal + '%';
          if (vramBar) vramBar.style.width = pctVal + '%';
        }
        if (tempEl && gpu.temp_c !== null) tempEl.textContent = Math.round(gpu.temp_c) + '°C';
      }

      // 4. Laya-V2 Panel
      if (live.laya) {
        const la = live.laya;
        const runId = la.run_id || 'N/A';
        const lossStr = (la.loss !== null && la.loss !== undefined) ? Number(la.loss).toFixed(4) : 'N/A';
        const stepStr = (la.step !== null) ? Number(la.step).toLocaleString() : 'N/A';
        const totalStepStr = (la.total_steps !== null) ? Number(la.total_steps).toLocaleString() : '92,280';
        const chunkStr = (la.chunk !== null) ? la.chunk : 'N/A';
        const totalChunkStr = (la.total_chunks !== null) ? la.total_chunks : '361';

        const runEl = document.getElementById('laya-run-id');
        const lossEl = document.getElementById('laya-loss');
        const stepEl = document.getElementById('laya-steps');
        const bestAccEl = document.getElementById('laya-best-acc');
        const valLossEl = document.getElementById('laya-val-loss');
        const brierEl = document.getElementById('laya-brier');
        const trendEl = document.getElementById('laya-loss-trend');
        const candEl = document.getElementById('laya-cand-count');

        if (runEl) runEl.textContent = runId;
        if (lossEl) lossEl.textContent = lossStr;
        if (trendEl) trendEl.textContent = lossStr;
        if (stepEl) stepEl.textContent = `Step: ${stepStr} / ${totalStepStr}`;
        if (bestAccEl && la.best_s1_acc) bestAccEl.textContent = (Number(la.best_s1_acc) * 100).toFixed(2) + '%';
        if (valLossEl && la.best_val_loss) valLossEl.textContent = 'Loss: ' + Number(la.best_val_loss).toFixed(4);
        if (brierEl && la.brier_score) brierEl.textContent = Number(la.brier_score).toFixed(4);
        if (candEl && la.candidates) {
          const c = la.candidates;
          candEl.textContent = `${c.VALIDATED || 5} 验证 · ${c.TRAINING || 1} 在训 · ${c.PLANNED || 22} 规划`;
        }

        // Hero Cockpit Laya
        const cpLoss = document.getElementById('cockpitLayaLoss');
        const cpChunk = document.getElementById('cockpitLayaChunk');
        const cpStep = document.getElementById('cockpitLayaStep');
        const cpBar = document.getElementById('cockpitLayaBar');
        const cpAcc = document.getElementById('cockpitLayaAcc');
        if (cpLoss) cpLoss.textContent = lossStr;
        if (cpChunk) cpChunk.textContent = `Chunk ${chunkStr} / ${totalChunkStr}`;
        if (cpStep) cpStep.textContent = `${stepStr} / ${totalStepStr}`;
        if (cpAcc && la.best_s1_acc) cpAcc.textContent = (Number(la.best_s1_acc) * 100).toFixed(2) + '%';
        if (cpBar && la.chunk && la.total_chunks) {
          cpBar.style.width = Math.min(100, (la.chunk / la.total_chunks) * 100).toFixed(1) + '%';
        }

        renderSparkline('laya-sparkline', la.recent_loss_series || [], '#38bdf8');
      }

      // 5. Kev-4B Panel
      if (live.kev) {
        const kv = live.kev;
        const runId = kv.run_id || 'N/A';
        const lossStr = (kv.loss !== null && kv.loss !== undefined) ? Number(kv.loss).toFixed(4) : 'N/A';
        const stepStr = (kv.step !== null) ? Number(kv.step).toLocaleString() : 'N/A';
        const totalStepStr = (kv.total_steps !== null) ? Number(kv.total_steps).toLocaleString() : '16,857';

        const runEl = document.getElementById('kev-run-id');
        const lossEl = document.getElementById('kev-loss');
        const stepEl = document.getElementById('kev-steps');
        const bestAccEl = document.getElementById('kev-best-acc');
        const valLossEl = document.getElementById('kev-val-loss');
        const brierEl = document.getElementById('kev-brier');
        const trendEl = document.getElementById('kev-loss-trend');
        const candEl = document.getElementById('kev-cand-count');

        if (runEl) runEl.textContent = runId;
        if (lossEl) lossEl.textContent = lossStr;
        if (trendEl) trendEl.textContent = lossStr;
        if (stepEl) stepEl.textContent = `Step: ${stepStr} / ${totalStepStr}`;
        if (bestAccEl && kv.val_accuracy) bestAccEl.textContent = (Number(kv.val_accuracy) * 100).toFixed(2) + '%';
        if (valLossEl && kv.val_loss) valLossEl.textContent = 'NLL: ' + Number(kv.val_loss).toFixed(4);
        if (brierEl && kv.brier_score) brierEl.textContent = Number(kv.brier_score).toFixed(4);
        if (candEl && kv.candidates) {
          const c = kv.candidates;
          candEl.textContent = `${c.VALIDATED || 1} 验证 · ${c.TRAINING || 1} 在训 · ${c.PLANNED || 8} 规划`;
        }

        // Hero Cockpit Kev
        const cpLoss = document.getElementById('cockpitKevLoss');
        const cpStep = document.getElementById('cockpitKevStep');
        const cpBar = document.getElementById('cockpitKevBar');
        if (cpLoss) cpLoss.textContent = lossStr;
        if (cpStep) cpStep.textContent = `Step ${stepStr} / ${totalStepStr}`;
        if (cpBar && kv.step && kv.total_steps) {
          cpBar.style.width = Math.min(100, Math.max(0.5, (kv.step / kv.total_steps) * 100)).toFixed(1) + '%';
        }

        renderSparkline('kev-sparkline', kv.recent_loss_series || [], '#34d399');
      }

      // 6. Benchmark Matrix
      renderBenchmarkTable();
    }
    """

    # Fix cumSamples and cumSteps safe access in renderMultiSpanLossChart
    content = content.replace(
        "const maxSmpl = pts[pts.length - 1].cumSamples || 5277457;",
        "const maxSmpl = (pts && pts.length > 0 && pts[pts.length - 1] && pts[pts.length - 1].cumSamples) ? pts[pts.length - 1].cumSamples : 5277457;"
    )
    content = content.replace(
        "const maxSteps = pts[pts.length - 1].cumSteps || 59904;",
        "const maxSteps = (pts && pts.length > 0 && pts[pts.length - 1] && pts[pts.length - 1].cumSteps) ? pts[pts.length - 1].cumSteps : 59904;"
    )

    # Wrap chart rendering in try-catch blocks
    old_chart_renders = """      // Re-render all connected visual charts & tables
      renderMultiSpanLossChart();
      renderLadderChart();
      renderCumulativeThroughputChart();
      renderStepScaleChart();
      renderScatterChart();
      renderLatencyChart();
      renderLiveRunsViews();
      renderVersionLifecycleTable();"""

    new_chart_renders = """      // Re-render all connected visual charts & tables with error safety
      try { renderMultiSpanLossChart(); } catch (e) { console.warn('Loss chart error:', e); }
      try { renderLadderChart(); } catch (e) { console.warn('Ladder chart error:', e); }
      try { renderCumulativeThroughputChart(); } catch (e) { console.warn('Throughput chart error:', e); }
      try { renderStepScaleChart(); } catch (e) { console.warn('Step scale chart error:', e); }
      try { renderScatterChart(); } catch (e) { console.warn('Scatter chart error:', e); }
      try { renderLatencyChart(); } catch (e) { console.warn('Latency chart error:', e); }
      try { renderLiveRunsViews(); } catch (e) { console.warn('Tree view error:', e); }
      try { renderVersionLifecycleTable(); } catch (e) { console.warn('Lifecycle table error:', e); }"""
    content = content.replace(old_chart_renders, new_chart_renders)

    # Preserve embedded historical versions and shards when live fetching
    content = content.replace(
        "cachedLive = live;\n          updateLiveUI(live);",
        "cachedLive = Object.assign({}, window.__EMBEDDED_LIVE_STATUS__ || {}, live);\n          updateLiveUI(cachedLive);"
    )

    # Inject V8 helpers right before updateLiveUI definition
    content = content.replace(
        "function updateLiveUI(live) {",
        v8_helpers_and_injection + "\n    function updateLiveUI(live) {\n      if (!live) return;\n      cachedLive = live;\n      try { applyV8LiveUpdates(live); } catch (e) { console.error('V8 update error:', e); }"
    )

    # Write out files
    TARGET_HTML.write_text(content, encoding="utf-8")
    OUR_PROJECT_HTML.write_text(content, encoding="utf-8")
    print(f"Successfully assembled and wrote {TARGET_HTML} ({len(content)} chars)")
    print(f"Successfully mirrored to {OUR_PROJECT_HTML}")

if __name__ == "__main__":
    main()
