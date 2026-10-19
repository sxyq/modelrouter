/* Agent experiments use their own status file; training widgets remain unchanged. */
(() => {
  const panel = document.createElement('section');
  panel.id = 'agent-benchmark-live';
  panel.style.cssText = 'margin:20px 28px;padding:20px;background:var(--cds-s1,#181714);border:1px solid var(--cds-border,#2c2924);border-radius:12px;overflow:auto';
  const title = document.createElement('h2');
  title.textContent = 'Agent Benchmark · 官方 Trial';
  title.style.cssText = 'font-size:18px;margin:0 0 8px';
  const summary = document.createElement('p');
  const output = document.createElement('pre');
  output.style.cssText = 'white-space:pre-wrap;overflow-wrap:anywhere;font:12px/1.8 ui-monospace,monospace;color:var(--cds-text-secondary,#c4bcb0)';
  const note = document.createElement('p');
  note.textContent = 'N/A 表示尚无真实观测。配置价格估算与服务商账单分开显示。历史 RQ1–RQ5 图表为 Unverified / Synthetic，不代表正式实验发现。';
  panel.append(title, summary, output, note);
  const header = document.querySelector('header');
  header.after(panel);
  const show = value => value === null || value === undefined ? 'N/A' : typeof value === 'number' ? Number(value.toFixed(3)).toString() : String(value);
  async function refresh() {
    try {
      const response = await fetch('agent_benchmark_status.json', {cache: 'no-store'});
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const m = await response.json();
      const current = m.current || m.last_unit || {};
      const trial = m.current_trial || {};
      const call = m.last_generator || {};
      const age = (Date.now() - Date.parse(m.timestamp)) / 1000;
      summary.textContent = `${m.status} · ${m.iteration_id} · ${m.finished_units}/${m.total_units} · ${age > 30 ? '记录已过期' : '更新于'} ${new Date(m.timestamp).toLocaleString('zh-CN')} · ${show(age)} 秒前`;
      const modelLines = Object.entries(m.models || {}).map(([name, value]) => `${name}: TTFT P50/P95 ${show(value.ttft_p50_ms)}/${show(value.ttft_p95_ms)} ms · ${show(value.output_tokens_per_s)} Tokens/s（整请求）· ${show(value.stream_output_tokens_per_s_estimate)} Tokens/s（TTFT 后估算）`);
      const routerLines = Object.entries(m.router_latency_ms || {}).map(([name, value]) => `${name}: 路由 P50/P95 ${show(value.p50)}/${show(value.p95)} ms (n=${value.n})`);
      output.textContent = [
        `Job ID ${show(trial.job_id)} · Trial ID ${show(trial.trial_id)} · Job ${current.job_name || '—'}`,
        `Task ${current.task_id || trial.task_id || '—'} · Policy ${current.policy || '—'}`,
        `Step ${show(call.step)} · Model ${call.returned_model || call.model || '—'} · Effort ${call.effort || '—'}`,
        `官方 Verifier ${m.verified_trials} · 成功 ${m.successes} · 成功率 ${show(m.success_rate)}`,
        `Trial ${trial.status || 'NOT_EVALUATED'} · Verifier 来源 ${show(trial.verifier_path)} · Reward ${show(trial.reward)}`,
        `Token ${show(m.generator_tokens)} · 生成费用估算 $${show(m.generator_cost_usd)} · 完整实际费用 $${show(m.complete_cost_usd)}`,
        ...modelLines, ...routerLines,
        `工具耗时 P50/P95 ${show(m.tool_exec_p50_ms)}/${show(m.tool_exec_p95_ms)} ms`,
        `最近工具 Exit ${show(m.last_tool?.exit_code)} · ${show(m.last_tool?.duration_ms)} ms`,
        `Episode P50/P95 ${show(m.episode_p50_s)}/${show(m.episode_p95_s)} s · Episode/h ${show(m.episodes_per_hour)}`,
        `每个成功任务实际费用 $${show(m.actual_cost_per_success_usd)}`,
        `最近事件 ${m.last_event ? m.last_event.event + ' · ' + (m.last_event.error || m.last_event.status || m.last_event.command_id || '') : '—'}`,
      ].join('\n');
    } catch (error) {
      summary.textContent = `尚无可读取的 Agent 实验状态：${error.message}`;
      output.textContent = '';
    }
  }
  refresh();
  setInterval(refresh, 10000);
})();
