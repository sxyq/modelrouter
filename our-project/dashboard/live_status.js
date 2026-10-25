/* The training page reads live JSON and historical shards; no embedded snapshots. */
(() => {
  'use strict';
  const COLORS = ['#d97757', '#2ea06f', '#5e89b8', '#d9943b', '#d85858', '#c4bcb0'];
  const DASHES = ['', '7 3', '2 3', '9 3 2 3'];
  const METRIC_GUIDE = {
    train_loss: ['训练误差，反映模型对训练样本的拟合程度', '低一些更好'],
    consumed_records: ['实际已经处理的训练记录数量，反映样本曝光进度', '高一些更好；不能单独代表质量'],
    learning_rate: ['优化器每次更新的步长，决定参数更新幅度', '没有固定高低好坏；看是否符合训练方案'],
    samples_per_s: ['单位时间处理的样本数，反映训练吞吐速度', '高一些更好；需结合硬件和批大小比较'],
    optimizer_updates: ['优化器实际更新次数，反映参数更新进度', '高一些表示进度更深；不能单独代表质量'],
    epoch_seconds: ['完成一个 Epoch 所用的时间，反映训练耗时', '低一些更好；需结合样本量比较'],
    optimizer_step_seconds: ['单个优化器 Step 的耗时，反映更新速度', '低一些更好'],
    loss: ['验证集上的预测误差，反映泛化误差', '低一些更好'],
    accuracy: ['验证集预测正确的比例', '高一些更好'],
    brier: ['概率预测的平方误差，衡量概率质量和校准情况', '低一些更好'],
    ece: ['预测置信度与实际正确率的校准偏差', '低一些更好'],
  };
  const COUNT_FIELDS = [
    ['planned_runs', '计划 Run'], ['observed_runs', '已观测 Run / 资产'], ['local_runs', '本地 Run'],
    ['executed_runs', '实际执行 Run'], ['local_completed_runs', '本地结束 Run'],
    ['metadata_only_runs', '仅状态记录 Run'], ['imported_assets', '导入资产'],
    ['running_runs', '在训 Run'], ['checkpoint_versions', 'Checkpoint 记录'], ['physical_checkpoints', '权重实体'],
    ['confirmed_saved_versions', '已知曾保存版本'],
    ['metadata_versions', '指标版本'], ['pruned_versions', '已移除实体'], ['unknown_missing_versions', '未知缺失'],
    ['train_curve_runs', '有 Loss 记录 Run（含 Epoch）'], ['step_curve_runs', '逐步曲线 Run'],
    ['epoch_only_runs', '仅 Epoch Run'], ['unrecorded_curve_runs', '无曲线记录 Run'],
  ];
  const num = value => typeof value === 'number' && Number.isFinite(value) ? value : null;
  const display = (value, digits) => {
    if (value === null || value === undefined || value === '') return 'N/A';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value !== 'number') return String(value);
    if (!Number.isFinite(value)) return 'N/A';
    return value.toLocaleString('zh-CN', digits === undefined ? {} : {minimumFractionDigits: digits, maximumFractionDigits: digits});
  };
  const esc = value => display(value).replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
  const present = value => value !== null && value !== undefined && value !== '';
  const identity = value => present(value) ? (typeof value === 'object' ? JSON.stringify(value) : String(value)) : null;
  const epochCount = run => Array.isArray(run.epochs) ? run.epochs.length : num(run.epochs);
  const supervisionCombo = run => run.supervision_classes?.length ? [...run.supervision_classes].sort().join(' + ') : null;
  const samplingKey = run => run.sampling ? JSON.stringify([run.sampling.mode ?? null,
    run.sampling.ratio_label ?? null, run.sampling.requested_ratios ?? null]) : null;
  const samplingText = run => display(run.sampling?.mode) + ' · ' + display(run.sampling?.ratio_label)
    + ' · 请求 ' + display(run.sampling?.requested_ratios);
  const filterValue = value => identity(value) ?? '__unknown__';
  function dateNumber(value) {
    if (!present(value)) return null;
    const result = typeof value === 'number' ? (value < 1e12 ? value * 1000 : value) : Date.parse(value);
    return Number.isFinite(result) ? result : null;
  }
  function dateText(value) {
    const stamp = dateNumber(value);
    return stamp === null ? 'N/A' : new Date(stamp).toLocaleString('zh-CN', {hour12: false});
  }
  function ageSeconds(value, now = Date.now()) {
    const stamp = dateNumber(value);
    return stamp === null ? null : (now - stamp) / 1000;
  }
  const seconds = value => num(value) === null ? 'N/A' : display(value, 1) + ' 秒';
  function liveObservation(live) {
    const timestamp = live.collected_at_iso ?? live.collected_at_unix ?? live.updated_at;
    const age = ageSeconds(timestamp);
    const status = live.connection_status === 'DISCONNECTED' || live.server_connected === false ? 'DISCONNECTED'
      : live.collector_source === 'local_a6000' && !live.history ? 'COLLECTOR_UPDATE_REQUIRED'
      : age === null || age > 30 ? 'DATA_STALE' : null;
    return {timestamp, age, status};
  }
  function runRecovery(run) {
    const fields = [['续跑', run.resumed_from ?? run.recovery_from], ['父版本', run.parent_checkpoint],
      ['父 Run', run.parent_run ?? run.parent_key], ['恢复', run.recovery], ['恢复段', run.segments ?? run.segment]];
    return fields.filter(([, value]) => present(value)).map(([label, value]) => label + ' ' + display(value)).join(' · ') || null;
  }
  function defaultAxis(run, points) {
    return /epoch/i.test(run.curve_granularity || '')
      || (points.length > 0 && points.every(p => num(p.step) === null) && points.some(p => num(p.epoch) !== null)) ? 'epoch' : 'step';
  }
  function hardwareMarkup(live, observation = liveObservation(live)) {
    const gpu = live.gpu || {}, disk = live.disk || {};
    const gib = bytes => num(bytes) === null ? 'N/A' : display(bytes / (1024 ** 3), 1);
    const processes = ['laya', 'kev'].map(family => {
      const process = live.process?.[family] || {}, model = live[family] || {};
      return family + ' PID ' + display(model.process_pid ?? process.train_pid)
        + ' · ' + (observation.status ? '上次观测时 ' : '') + seconds(model.elapsed_s ?? process.elapsed_s);
    });
    return '<span>GPU ' + esc(gpu.name) + ' · ' + esc(gpu.util_pct) + '% · ' + esc(gpu.used_mb) + ' / ' + esc(gpu.total_mb) + ' MiB</span><span>温度 ' + esc(gpu.temp_c) + ' °C · 功率 ' + esc(gpu.power_w) + ' W</span><span>磁盘 ' + gib(disk.used_bytes) + ' / ' + gib(disk.total_bytes) + ' GiB · 可用 ' + gib(disk.free_bytes) + ' GiB</span><span>' + processes.map(esc).join(' · ') + '</span>';
  }
  function trainingEtaMarkup(eta, observation = {}) {
    const totals = eta?.totals;
    const duration = value => seconds(value) + (num(value) !== null && value >= 3600 ? '（' + display(value / 3600, 1) + ' 小时）' : '');
    const range = duration(totals?.range_seconds?.[0]) + ' — ' + duration(totals?.range_seconds?.[1]);
    const fields = [['可执行计划 Run', totals?.planned_executable_runs],
      ['串行墙钟估算', duration(totals?.serial_wall_seconds)], ['墙钟下限估算', duration(totals?.lower_bound_wall_seconds)],
      ['墙钟估算范围', range], ['预计完成（本地时区）', dateText(totals?.estimated_finish_at)],
      ['估算观测时间', dateText(eta?.observed_at)]];
    const current = ['laya', 'kev'].map(family => {
      const run = eta?.current?.[family];
      return '<tr><td>' + esc(family) + '</td><td>' + esc(run?.run_id) + '</td><td>'
        + esc(duration(run?.remaining_training_seconds)) + '</td><td>' + esc(duration(run?.validation_seconds))
        + '<div class="sub">Val 估算依据：' + esc(run?.validation_method) + '</div>'
        + '</td><td>' + esc(dateText(run?.estimated_finish_at)) + '</td><td>' + esc(run?.method) + '</td></tr>';
    }).join('');
    const groups = eta?.groups?.map(group => '<tr><td>' + esc(group.group) + '</td><td>' + esc(group.count)
      + '</td><td>' + esc(duration(group.training_seconds)) + '</td><td>' + esc(duration(group.validation_seconds))
      + '</td><td>' + esc(duration(group.materialization_seconds)) + '</td><td>' + esc(group.remaining_records)
      + '</td><td>' + esc(group.method) + '</td></tr>').join('');
    const blocked = eta?.blocked?.map(group => '<tr><td>' + esc(group.group) + '</td><td>' + esc(group.count)
      + '</td><td>' + esc(group.reason) + '</td></tr>').join('');
    const assumptions = eta?.assumptions?.map(note => '<p>' + esc(note) + '</p>').join('');
    return '<summary>全局计划与 ETA · 可执行计划 ' + esc(totals?.planned_executable_runs)
      + ' · 预计完成 ' + esc(dateText(totals?.estimated_finish_at))
      + (observation.status ? ' · 上次估算 ' + esc(observation.status) : '') + '</summary><div class="inner">'
      + '<p class="sub">来源 live_status.json → training_eta · 全局计划独立于历史筛选。以下均为耗时估算；墙钟包含等待及其他阶段，不代表实测 GPU 活跃时长。预计完成时间按浏览器本地时区显示。</p>'
      + '<dl class="metadata">' + fields.map(([label, value]) => '<div><dt>' + esc(label) + '</dt><dd>' + esc(value) + '</dd></div>').join('') + '</dl>'
      + '<h3>当前 Run 剩余时间估算</h3><div class="table-wrap"><table><thead><tr><th>模型</th><th>Run</th><th>剩余训练</th><th>验证</th><th>预计完成</th><th>估算方法</th></tr></thead><tbody>' + current + '</tbody></table></div>'
      + '<h3 class="section">计划分组 · 耗时估算</h3><p class="sub">训练 / Val 合计已包含验证；Val 独立记录供参考，不重复相加。</p><div class="table-wrap"><table><thead><tr><th>分组</th><th>Run 数</th><th>训练 / Val 合计</th><th>Val（独立记录）</th><th>物化</th><th>剩余记录</th><th>估算方法</th></tr></thead><tbody>'
      + (groups || '<tr><td colspan="7">' + (eta?.groups ? '无分组记录' : 'N/A · 未提供分组') + '</td></tr>') + '</tbody></table></div>'
      + '<h3 class="section">待补条件的计划</h3><div class="table-wrap"><table><thead><tr><th>分组</th><th>Run 数</th><th>原因</th></tr></thead><tbody>'
      + (blocked || '<tr><td colspan="3">' + (eta?.blocked ? '无待补条件记录' : 'N/A · 未提供记录') + '</td></tr>') + '</tbody></table></div>'
      + '<h3 class="section">估算依据与适用条件</h3><div class="note muted">' + (assumptions || '<p>N/A · 未提供估算依据</p>') + '</div></div>';
  }
  function retentionMarkup(label, records) {
    const items = Array.isArray(records) ? records : null;
    const physical = items && items.every(item => typeof item.physical === 'boolean') ? items.filter(item => item.physical).length : null;
    const rows = items?.map(item => '<p><b>' + esc(item.checkpoint_id) + '</b> · ' + esc(item.run_id)
      + ' · ' + (item.physical === true ? '实体存在' : item.physical === false ? '实体不存在' : '实体 N/A')
      + ' · ' + esc(item.retention_status) + '</p>').join('');
    return '<div class="card"><h3>' + esc(label) + ' · ' + display(physical) + '/' + display(items?.length)
      + ' 实体/记录</h3><div class="retention-list">' + (rows || (items ? '<p class="muted">无记录</p>' : 'N/A')) + '</div></div>';
  }
  function comparisonText(value) {
    return value && typeof value === 'object' ? display(value.run_id) + ' · Epoch ' + display(value.epoch) + ' · ' + display(value.value) : 'N/A';
  }
  function censusMarkup(census) {
    const streams = ['S1', 'S2', 'S3'];
    const layers = Object.entries(census?.layers || {});
    const cells = row => streams.map(stream => '<td>' + esc(row?.[stream]) + '</td>').join('');
    const rows = layers.map(([layer, row]) => '<tr><td>' + esc(layer) + '</td><td>' + esc(row.total_records) + '</td><td>' + esc(row.distinct_units) + '</td>' + cells(row) + '</tr>').join('');
    return '<p class="sub">原始记录 ' + esc(census?.total_raw_records) + ' · 可用候选 ' + esc(census?.eligible_candidate_records)
      + '</p><div class="table-wrap"><table><thead><tr><th>数据层</th><th>记录</th><th>不同任务单元</th><th>S1</th><th>S2</th><th>S3</th></tr></thead><tbody>'
      + (rows || '<tr><td>N/A</td><td>N/A</td><td>N/A</td>' + cells(null) + '</tr>')
      + '<tr><td>监督记录总计</td><td>N/A</td><td>N/A</td>' + cells(census?.supervision) + '</tr></tbody></table></div>';
  }
  function validationSet(run, point = {}) {
    return point.validation_set ?? run.validation_set ?? (typeof run.validation === 'string' ? run.validation
      : run.validation?.validation_set ?? run.validation?.dataset ?? run.validation?.set_id);
  }
  function canOverlay(a, b) {
    return a.family === b.family && identity(a.protocol) !== null && identity(a.protocol) === identity(b.protocol);
  }
  function splitSeries(points, metric, axis) {
    const parts = [];
    let part = [], previous = null;
    for (const point of points) {
      const x = axis === 'timestamp' ? dateNumber(point.timestamp) : num(point[axis]);
      const y = num(point[metric]);
      if (x === null || y === null) {
        if (part.length) parts.push(part);
        part = []; previous = null; continue;
      }
      if (previous && (point.segment !== previous.segment || x < previous.x)) {
        if (part.length) parts.push(part);
        part = [];
      }
      part.push({x, y, point});
      previous = {x, segment: point.segment};
    }
    if (part.length) parts.push(part);
    return parts;
  }
  function validationGroups(records) {
    const groups = new Map();
    for (const record of records) {
      for (const point of record.validation || []) {
        const set = validationSet(record.run, point);
        const stream = point.stream;
        const protocol = point.protocol ?? record.run.protocol;
        const definition = point.loss_definition ?? record.run.loss_definition;
        const key = JSON.stringify([record.run.family, identity(protocol),
          identity(set) ?? record.run.key, identity(stream) ?? record.run.key,
          point.items ?? record.run.key, identity(definition), identity(protocol) === null ? record.run.key : null]);
        if (!groups.has(key)) groups.set(key, {protocol, validation_set: set, stream, items: point.items, loss_definition: definition, series: new Map()});
        const group = groups.get(key);
        if (!group.series.has(record.run.key)) group.series.set(record.run.key, {run: record.run, points: []});
        group.series.get(record.run.key).points.push(point);
      }
    }
    return [...groups.values()];
  }
  const labelForAxis = axis => ({step: 'Step', timestamp: '时间', consumed_records: '已消费记录', optimizer_updates: '优化器更新', epoch: 'Epoch'}[axis]);
  const axisTickText = (value, axis) => {
    if (axis === 'timestamp') return new Date(value).toLocaleTimeString('zh-CN', {hour12: false});
    const absolute = Math.abs(value);
    if (absolute >= 1000000) return (value / 1000000).toFixed(1).replace(/\.0$/, '') + 'M';
    if (absolute >= 1000) return (value / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    return display(Number(value.toPrecision(4)));
  };
  const metricGuide = metric => {
    const [meaning, direction] = METRIC_GUIDE[metric] || ['原始记录中的指标，具体含义见数据来源', '方向 N/A'];
    return '字段说明：' + meaning + '；方向：' + direction + '。';
  };
  function chartMarkup(title, series, metric, axis, note = '') {
    const plotted = series.map((s, i) => ({...s, color: COLORS[i % COLORS.length], dash: DASHES[i % DASHES.length], parts: splitSeries(s.points, metric, axis)}));
    const all = plotted.flatMap(s => s.parts.flat());
    if (!all.length) return '<div class="chart"><h3>' + esc(title) + '</h3><p class="metric-guide">' + esc(metricGuide(metric)) + '</p><div class="empty">N/A · 无此指标的真实记录</div><p class="sub">' + esc(note) + '</p></div>';
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const p of all) { minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x); minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y); }
    if (minX === maxX) { minX -= axis === 'timestamp' ? 1000 : .5; maxX += axis === 'timestamp' ? 1000 : .5; }
    const pad = (maxY - minY) * .08 || Math.abs(minY) * .05 || .1;
    minY -= pad; maxY += pad;
    const width = 680, height = 230, left = 58, right = 14, top = 12, bottom = 40;
    const x = value => left + (value - minX) / (maxX - minX) * (width - left - right);
    const y = value => height - bottom - (value - minY) / (maxY - minY) * (height - top - bottom);
    let drawing = '';
    const tickCount = 3;
    for (let i = 0; i <= tickCount; i++) {
      const yy = top + (height - top - bottom) * i / tickCount;
      const value = maxY - (maxY - minY) * i / tickCount;
      drawing += '<line x1="' + left + '" y1="' + yy + '" x2="' + (width - right) + '" y2="' + yy + '" stroke="#2c2924"/><text x="' + (left - 8) + '" y="' + (yy + 4) + '" text-anchor="end" fill="#8e867a" font-size="11">' + esc(Number(value.toPrecision(4))) + '</text>';
      const xx = left + (width - left - right) * i / tickCount;
      const xv = minX + (maxX - minX) * i / tickCount;
      const tick = axisTickText(xv, axis);
      drawing += '<text x="' + xx + '" y="' + (height - 23) + '" text-anchor="middle" fill="#8e867a" font-size="11">' + esc(tick) + '</text>';
    }
    for (const s of plotted) {
      for (const part of s.parts) {
        const path = part.map((p, i) => (i ? 'L' : 'M') + x(p.x).toFixed(2) + ',' + y(p.y).toFixed(2)).join(' ');
        drawing += '<path d="' + path + '" stroke="' + s.color + '" stroke-dasharray="' + s.dash + '" fill="none" stroke-width="1.5"><title>' + esc(s.run.run_id) + ' · ' + part.length + ' 个观测点 · 恢复段 ' + esc(part[0].point.segment) + '</title></path>';
        if (part.length <= 150) for (const p of part) drawing += '<circle cx="' + x(p.x).toFixed(2) + '" cy="' + y(p.y).toFixed(2) + '" r="2.5" fill="' + s.color + '"><title>' + esc(s.run.run_id) + ' · ' + esc(labelForAxis(axis)) + ' ' + esc(axis === 'timestamp' ? dateText(p.x) : p.x) + ' · ' + esc(metric) + ' ' + esc(p.y) + ' · ' + esc(p.point.source) + '</title></circle>';
      }
    }
    drawing += '<text x="' + ((left + width - right) / 2) + '" y="' + (height - 3) + '" text-anchor="middle" fill="#8e867a" font-size="11">' + esc(labelForAxis(axis)) + '</text>';
    const legend = plotted.map(s => '<span><i class="swatch" style="border-color:' + s.color + ';border-top-style:' + (s.dash ? 'dashed' : 'solid') + '"></i>' + esc(s.run.run_id) + ' · ' + esc(supervisionCombo(s.run)) + ' · ' + esc(samplingText(s.run)) + ' · ' + s.parts.reduce((n, p) => n + p.length, 0) + ' 点</span>').join('');
    return '<div class="chart"><h3>' + esc(title) + '</h3><p class="metric-guide">' + esc(metricGuide(metric)) + '</p><svg viewBox="0 0 ' + width + ' ' + height + '" role="img" aria-label="' + esc(title) + '">' + drawing + '</svg><div class="legend">' + legend + '</div><p class="sub">' + esc(note) + '</p></div>';
  }
  function liveCard(family, model, observation = {}) {
    const fields = [['Epoch', model.epoch], ['Chunk', model.chunk], ['Step', model.step],
      ['已消费记录', model.consumed_records], ['优化器更新', model.optimizer_updates], ['PID', model.process_pid],
      ['计划 Epoch / Chunk', display(model.planned_epochs) + ' / ' + display(model.total_chunks)],
      ['总 Step / 进度', display(model.total_steps) + ' / ' + (num(model.total_steps) > 0 && num(model.step) !== null ? display(100 * model.step / model.total_steps, 2) + '%' : 'N/A')],
      ['独立覆盖', model.distinct_units],
      [model.speed_scope ? '样本 / 秒（累计实测）' : '样本 / 秒（进度观测）', display(model.samples_per_s, 2)], ['训练耗时', seconds(model.training_seconds)]];
    const progressAge = ageSeconds(model.last_progress_at) ?? model.last_progress_age_s;
    const historical = observation.status;
    return '<article class="card live-card ' + family + '"' + (historical ? ' style="border-top-color:var(--cds-rose)"' : '') + '><div class="family-line"><h3>' + (family === 'laya' ? 'Laya' : 'Kev') + '</h3><span class="status' + (historical ? ' stale' : '') + '">' + esc(historical ?? model.status) + '</span></div><div class="run-id">' + esc(model.run_id) + '</div>'
      + (historical ? '<p class="sub">上次观测 ' + esc(dateText(observation.timestamp)) + ' · 以下数值非当前状态</p>' : '')
      + '<div class="loss">' + esc(display(model.loss, 4)) + '<small>训练 Loss ↓' + (present(model.loss_step) ? ' · 记录于 Step ' + esc(model.loss_step) : '') + '</small></div><dl class="metrics">' + fields.map(([label, value]) => '<div><dt>' + esc(label) + '</dt><dd>' + esc(value) + '</dd></div>').join('') + '</dl>'
      + (present(model.evaluation_status) ? '<p class="sub">验证 ' + esc(model.evaluation_status) + ' · 队列 ' + esc(model.queue_status) + (model.failure_reason ? ' · ' + esc(model.failure_reason) : '') + '</p>' : '')
      + (family === 'kev' ? '<p class="sub">固定 Val：Accuracy ' + esc(model.validation_metrics?.acc) + ' · NLL ' + esc(model.validation_metrics?.nll) + ' · Brier ' + esc(model.validation_metrics?.brier) + ' · ECE ' + esc(model.validation_metrics?.ece) + '</p><p class="sub">覆盖 ' + esc(model.validation_coverage?.evaluated_records) + ' / ' + esc(model.validation_coverage?.requested_records) + ' · 问题 ' + esc(model.validation_coverage?.evaluated_questions) + ' / ' + esc(model.validation_coverage?.requested_questions) + ' · 验证耗时 ' + esc(seconds(model.evaluation_seconds)) + ' · ' + esc(model.validation_device) + ' · attempt ' + esc(model.validation_attempt) + ' · 完成候选 ' + esc(model.completed_candidates) + '</p>'
        + '<p class="sub">' + (model.candidates || []).map(c => esc(c.candidate_id) + ' ' + esc(c.status)
          + (c.selection?.score != null ? ' · 内部评分 ' + esc(c.selection.score) : '')
          + (c.retention?.status ? ' · ' + esc(c.retention.status) + ' · 释放 ' + esc(c.retention.freed_bytes ?? 0) + ' B' : '')
          + (c.pending_reason || c.failure_reason ? ' · ' + esc(c.pending_reason || c.failure_reason) : '')).join('<br>') + '</p>' : '')
      + (model.speed_source ? '<p class="sub">吞吐来源 ' + esc(model.speed_source) + ' · Step ' + esc(model.speed_step) + ' · ' + esc(model.speed_scope) + '</p>' : '')
      + '<p class="sub">最后进度 ' + esc(dateText(model.last_progress_at)) + ' · ' + esc(seconds(progressAge)) + '前</p><p class="sub">' + (historical ? '上次观测时进程已运行 ' : '进程已运行 ') + esc(seconds(model.elapsed_s)) + '</p></article>';
  }
  function boot() {
    const el = id => document.getElementById(id);
    const state = {live: null, history: null, revision: null, cache: new Map(), selected: null, axisRun: null, overlays: new Set(), overlaySeededRun: null, render: 0, refreshing: false};
    const json = async path => {
      const response = await fetch(path, {cache: 'no-store'});
      if (!response.ok) throw new Error('HTTP ' + response.status + ' · ' + path);
      return response.json();
    };
    function renderLive(live) {
      const observation = liveObservation(live);
      el('connection').textContent = display(observation.status ?? live.connection_status)
        + (observation.age === null ? '' : ' · ' + display(observation.age, 0) + ' 秒前')
        + (live.error ? ' · 读取失败 ' + display(live.error) : '');
      el('connection').className = observation.status ? 'status stale' : 'status';
      el('collected').textContent = '采集于 ' + dateText(observation.timestamp);
      el('live-models').innerHTML = ['laya', 'kev'].map(f => liveCard(f, live[f] || {}, observation)).join('');
      el('hardware').innerHTML = hardwareMarkup(live, observation);
      el('training-eta').innerHTML = trainingEtaMarkup(live.training_eta, observation);
    }
    function renderCounts() {
      el('counts-head').innerHTML = '<tr><th>模型</th><th>记录 Epoch</th>' + COUNT_FIELDS.map(([, label]) => '<th>' + label + '</th>').join('') + '</tr>';
      el('counts-body').innerHTML = ['laya', 'kev'].map(family => {
        const runs = state.history.runs.filter(r => r.family === family);
        const epochs = runs.map(epochCount);
        const count = epochs.some(n => n === null) ? null : epochs.reduce((a, b) => a + b, 0);
        const c = state.history.counts?.[family] || {};
        return '<tr><td>' + esc(family) + '</td><td>' + esc(count) + '</td>' + COUNT_FIELDS.map(([field]) => '<td>' + esc(c[field]) + '</td>').join('') + '</tr>';
      }).join('');
    }
    function fillOptions(id, values, previous, label = display) {
      const options = new Map(values.map(value => [filterValue(value), label(value)]));
      el(id).innerHTML = '<option value="all">全部</option>' + [...options].map(([key, text]) => '<option value="' + esc(key) + '">' + esc(text) + '</option>').join('');
      if ([...el(id).options].some(o => o.value === previous)) el(id).value = previous;
    }
    function fillDataVolumes() {
      fillOptions('data-volume', state.history.runs.map(run => num(run.exposure?.[el('exposure-field').value])), el('data-volume').value);
    }
    function filteredRuns() {
      return (state.history?.runs || []).filter(run =>
        (el('family').value === 'all' || run.family === el('family').value)
        && (el('protocol').value === 'all' || filterValue(run.protocol) === el('protocol').value)
        && (el('supervision').value === 'all' || filterValue(supervisionCombo(run)) === el('supervision').value)
        && (el('sampling-ratio').value === 'all' || filterValue(samplingKey(run)) === el('sampling-ratio').value)
        && (el('training-stage').value === 'all' || filterValue(run.stage) === el('training-stage').value)
        && (el('data-volume').value === 'all' || filterValue(num(run.exposure?.[el('exposure-field').value])) === el('data-volume').value)
        && (el('run-status').value === 'all' || filterValue(run.status) === el('run-status').value)
        && (display(run.run_id) + ' ' + display(runRecovery(run))).toLowerCase().includes(el('search').value.toLowerCase()));
    }
    function renderRuns() {
      const runs = filteredRuns();
      if (!runs.some(run => run.key === state.selected)) state.selected = runs[0]?.key ?? null;
      el('run-count').textContent = runs.length + ' / ' + state.history.runs.length + ' Run';
      el('run-table').innerHTML = runs.map(run => '<tr class="' + (state.selected === run.key ? 'selected' : '') + '"><td><b>' + esc(run.run_id) + '</b><div class="sub">恢复 ' + esc(runRecovery(run)) + '</div></td><td>' + esc(run.family) + '</td><td>' + esc(supervisionCombo(run)) + '</td><td>' + esc(run.protocol) + '</td><td>' + esc(samplingText(run)) + '</td><td>' + esc(run.stage) + ' / ' + esc(run.status) + '</td><td>' + esc(num(run.exposure?.[el('exposure-field').value])) + '</td><td>' + esc(epochCount(run)) + '</td><td>' + esc(run.curve_points) + ' 点 / ' + esc(run.curve_granularity) + '</td><td>' + esc(validationSet(run)) + '</td><td>' + esc(dateText(run.started_at)) + '<br>' + esc(dateText(run.finished_at)) + '<br>' + esc(seconds(run.training_seconds)) + '</td><td><button data-run="' + esc(run.key) + '" type="button">查看曲线</button></td></tr>').join('') || '<tr><td colspan="12">无匹配 Run</td></tr>';
      el('selected-run').innerHTML = runs.map(run => '<option value="' + esc(run.key) + '">' + esc(run.family) + ' / ' + esc(run.run_id) + ' / ' + esc(run.protocol) + ' / ' + esc(supervisionCombo(run)) + ' / ' + esc(samplingText(run)) + '</option>').join('');
      if (state.selected) el('selected-run').value = state.selected;
    }
    function renderRetention() {
      const names = {old_core: '旧核心', new_core: '新核心', recovery: '恢复文件', parents: '父模型', global_best: '历史全局保留', unclassified: '未分类 / Pilot / 导入'};
      const retention = state.history.retention || {};
      el('pool-slots').textContent = '新池名额 ' + display(retention.new_pool_slots);
      el('retention').innerHTML = Object.entries(names).map(([key, label]) => retentionMarkup(label, retention[key])).join('');
    }
    function renderComparisons() {
      el('comparisons').innerHTML = (state.history.comparisons || []).map(c => '<div class="card"><h3>' + esc(c.family) + ' / ' + esc(c.protocol) + ' / ' + esc(c.supervision) + '</h3><p class="sub">验证集 ' + esc(c.validation_set) + ' · 指标 ' + esc(c.metric) + ' · 每个完成 Run 取该指标最佳 Epoch</p><p>最好 ' + esc(comparisonText(c.best)) + '</p><p>最差 ' + esc(comparisonText(c.worst)) + '</p></div>').join('') || '<p class="muted">N/A · 尚无可比较的同协议、同验证集记录。</p>';
    }
    function renderHistory() {
      renderCounts();
      fillOptions('protocol', state.history.runs.map(r => r.protocol), el('protocol').value);
      fillOptions('supervision', state.history.runs.map(supervisionCombo), el('supervision').value);
      const samplingLabels = new Map(state.history.runs.map(run => [samplingKey(run), samplingText(run)]));
      fillOptions('sampling-ratio', state.history.runs.map(samplingKey), el('sampling-ratio').value, key => samplingLabels.get(key));
      fillOptions('training-stage', state.history.runs.map(r => r.stage), el('training-stage').value);
      fillDataVolumes();
      fillOptions('run-status', state.history.runs.map(r => r.status), el('run-status').value);
      if (!state.history.runs.some(r => r.key === state.selected)) {
        const active = state.history.runs.find(r => state.live?.[r.family]?.run_id === r.run_id);
        state.selected = active?.key ?? state.history.runs.find(r => /RUNNING|TRAINING/.test(r.status))?.key ?? state.history.runs[0]?.key ?? null;
      }
      renderRuns(); renderRetention(); renderComparisons();
      el('data-census').innerHTML = censusMarkup(state.history.data_census);
      el('history-stamp').textContent = '生成于 ' + dateText(state.history.generated_at) + ' · revision ' + display(state.revision);
      el('limitations').innerHTML = (state.history.limitations || []).map(note => '<p>' + esc(note) + '</p>').join('') || '索引未报告额外限制。曲线只使用文件中真实点；缺失值与恢复段之间不连线。';
      el('limitations').innerHTML += '<p>未知范围：监督组合、采样模式、请求配比、各 stream 物化与累计训练、训练阶段、耗时及初始化无记录时显示 N/A；HISTORICAL_UNKNOWN 保留历史未知含义，不按 Run 名、计划 Epoch 或候选数量推算。</p>';
    }
    async function loadRun(run) {
      if (!run.curve_path) return {run, points: [], validation: [], exposure: run.exposure};
      if (!state.cache.has(run.curve_path)) state.cache.set(run.curve_path, json(run.curve_path));
      try { const detail = await state.cache.get(run.curve_path); return {...detail, run: {...detail.run, ...run}, exposure: run.exposure}; }
      catch (error) { state.cache.delete(run.curve_path); throw error; }
    }
    async function renderSelected() {
      const render = ++state.render;
      const run = state.history?.runs.find(r => r.key === state.selected);
      if (!run) {
        el('curve-status').textContent = 'N/A · 无匹配 Run';
        for (const id of ['run-metadata', 'overlay-list', 'train-charts', 'validation-charts', 'validation-table', 'exposure', 'checkpoint-table']) el(id).textContent = '';
        el('run-training-summary').innerHTML = '<tr><td colspan="9">N/A · 无匹配 Run</td></tr>';
        return;
      }
      const overlays = state.history.runs.filter(r => r.key !== run.key && canOverlay(run, r));
      if (state.overlaySeededRun !== run.key) {
        state.overlays = new Set(overlays.slice(0, 12).map(r => r.key));
        state.overlaySeededRun = run.key;
      }
      el('overlay-list').hidden = !el('overlay-toggle').checked;
      el('overlay-list').innerHTML = overlays.length
        ? '<div class="overlay-toolbar"><span class="muted">历史版本 ' + display(state.overlays.size) + ' / ' + display(overlays.length) + ' 个 · 默认前 12 个，可全部加入 · 不限配比</span><button type="button" data-overlay-action="all">全部加入</button><button type="button" data-overlay-action="none">清空</button></div>' + overlays.map(r => '<label><input data-overlay="' + esc(r.key) + '" type="checkbox" ' + (state.overlays.has(r.key) ? 'checked' : '') + '> ' + esc(r.run_id) + ' · ' + esc(supervisionCombo(r)) + ' · ' + esc(samplingText(r)) + ' · ' + esc(r.stage) + '</label>').join('')
        : '<span class="muted">无同协议 Run；未知协议不能合并比较。</span>';
      el('curve-status').textContent = '正在读取 ' + display(run.run_id);
      const selected = [run, ...(el('overlay-toggle').checked ? overlays.filter(r => state.overlays.has(r.key)) : [])];
      try {
        const records = await Promise.all(selected.map(loadRun));
        if (render !== state.render) return;
        const current = records[0];
        if (state.axisRun !== run.key) {
          el('curve-axis').value = defaultAxis(run, current.points);
          state.axisRun = run.key;
        }
        const segments = [...new Set(current.points.map(point => point.segment).filter(present))];
        const meta = [['Run', run.run_id], ['协议', run.protocol], ['监督组合', supervisionCombo(run)], ['训练阶段', run.stage], ['训练类型', run.training_kind], ['训练耗时', seconds(run.training_seconds)], ['初始化', run.initialization], ['来源', run.source], ['状态 / 恢复', display(run.status) + ' / ' + display(runRecovery({...run, ...current.run, segments: segments.length ? segments : run.segments}))], ['验证 / 队列', display(run.evaluation_status) + ' / ' + display(run.queue_status)], ['失败原因', run.failure_reason], ['粒度', run.curve_granularity], ['记录 Epoch', epochCount(run)], ['训练点', current.points.length], ['开始', dateText(run.started_at)], ['完成', dateText(run.finished_at)]];
        el('run-metadata').innerHTML = meta.map(([label, value]) => '<div><dt>' + esc(label) + '</dt><dd>' + esc(value) + '</dd></div>').join('');
        el('run-training-summary').innerHTML = records.map(record => {
          const r = record.run, s = r.sampling, e = record.exposure ?? r.exposure;
          return '<tr><td>' + esc(r.run_id) + '<br>' + esc(supervisionCombo(r)) + '</td><td>' + esc(s?.mode) + '<br>' + esc(s?.ratio_label) + '</td><td>' + esc(s?.requested_ratios) + '</td><td>' + esc(s?.materialized_per_epoch_by_stream) + '</td><td>' + esc(s?.trained_total_by_stream) + '</td><td>' + [e?.candidate_records, e?.materialized_records, e?.encoded_records].map(esc).join(' / ') + '</td><td>' + esc(e?.trained_records) + ' / ' + esc(e?.distinct_units) + '<div class="sub">' + esc(e?.trained_records_scope) + '<br>' + esc(e?.distinct_units_issue) + '</div></td><td>' + esc(r.stage) + '<br>' + esc(seconds(r.training_seconds)) + '</td><td>' + esc(r.initialization) + '<br>' + esc(r.source) + '</td></tr>';
        }).join('');
        el('train-charts').innerHTML = [['train_loss', '训练 Loss ↓'], ['consumed_records', '样本曝光 · 已消费记录'], ['learning_rate', '学习率'], ['samples_per_s', '样本 / 秒'], ['optimizer_updates', '优化器更新']].map(([metric, title]) => chartMarkup(title, records, metric, el('curve-axis').value, '全部真实观测点 · 缺失字段留空 · 恢复或计数重置时断开')).join('')
          + (run.family === 'kev'
            ? chartMarkup('优化器 Step 耗时 · 秒', records.map(r => ({...r, points: r.speed_points || []})), 'optimizer_step_seconds', 'step', '上游 training_metrics 原始计时；不以 batch 数推算样本吞吐')
            : chartMarkup('Epoch 完整耗时 · 秒', records.map(r => ({...r, points: r.speed_points || []})), 'epoch_seconds', 'epoch', '原始 Epoch 计时；未记录的 Epoch 显示 N/A'));
        const groups = validationGroups(records);
        el('validation-charts').innerHTML = groups.flatMap(group => ['loss', 'accuracy', 'brier', 'ece'].map(metric => {
          const series = [...group.series.values()];
          const axis = series.every(s => s.points.every(p => num(p.step) !== null)) ? 'step' : 'epoch';
          return chartMarkup(display(group.validation_set) + ' / ' + display(group.stream) + ' · ' + metric + (metric === 'accuracy' ? ' ↑' : ' ↓'), series, metric, axis, '协议 ' + display(group.protocol) + ' · 样本 ' + display(group.items) + ' · Loss 定义 ' + display(group.loss_definition) + ' · 未知验证集保持逐 Run 分开');
        })).join('') || '<div class="chart empty">N/A · 尚无验证记录</div>';
        el('validation-table').innerHTML = records.flatMap(record => (record.validation || []).map(v => '<tr><td>' + esc(record.run.run_id) + '</td><td>' + esc(validationSet(record.run, v)) + ' / ' + esc(v.stream) + '</td><td>' + esc(v.epoch) + ' / ' + esc(v.step) + '</td><td>' + esc(v.loss) + '</td><td>' + esc(v.accuracy) + '</td><td>' + esc(v.brier) + '</td><td>' + esc(v.ece) + '</td><td>' + esc(v.items) + '</td><td>' + esc(v.source) + '</td></tr>')).join('') || '<tr><td colspan="9">N/A</td></tr>';
        el('exposure').textContent = records.map(record => 'Run ' + display(record.run.run_id)
          + '\n来源 ' + display(record.run.source) + '\n监督 ' + display(record.run.supervision_classes)
          + '\n采样\n' + display(record.run.sampling) + '\n初始化\n' + display(record.run.initialization)
          + '\n数据暴露\n' + display(record.exposure ?? record.run.exposure)
          + '\n终端指标\n' + display(record.run.terminal_metrics)
          + '\n已知限制\n' + display(record.run.limitations)).join('\n\n');
        el('checkpoint-table').innerHTML = records.flatMap(record => (record.run.checkpoints || []).map(cp => '<tr><td>' + esc(record.run.run_id) + '</td><td>' + esc(cp.checkpoint_id) + '</td><td>' + esc(cp.epoch) + '</td><td>' + (cp.physical === true ? '存在' : cp.physical === false ? '不存在' : 'N/A') + '</td><td>' + (cp.ever_saved === true ? '是' : cp.ever_saved === false ? '否' : 'N/A') + '</td><td>' + esc(cp.retention_status) + '</td><td>' + esc(cp.path) + '<br>' + esc(cp.evidence) + '</td></tr>')).join('') || '<tr><td colspan="7">N/A</td></tr>';
        el('curve-status').textContent = display(run.run_id) + ' · ' + current.points.length + ' 训练点 · ' + (current.validation || []).length + ' 验证点';
      } catch (error) {
        if (render !== state.render) return;
        el('curve-status').textContent = 'N/A · ' + error.message;
        el('train-charts').innerHTML = '<div class="chart empty">N/A · 曲线文件不可读取</div>';
        el('validation-charts').innerHTML = ''; el('run-metadata').innerHTML = ''; el('validation-table').innerHTML = ''; el('exposure').textContent = ''; el('checkpoint-table').innerHTML = '';
        el('run-training-summary').innerHTML = '<tr><td colspan="9">N/A · 曲线文件不可读取</td></tr>';
      }
    }
    async function refresh(force = false) {
      if (state.refreshing) return;
      state.refreshing = true;
      try {
        const live = await json('live_status.json');
        state.live = live; renderLive(live);
        {
          const revision = live.history?.revision;
          if (force || !state.history || (present(revision) && state.revision !== revision)) {
            const history = await json('shards/training_history.json');
            state.history = history; state.revision = history.revision; state.cache.clear();
            renderHistory();
          } else {
            const selected = state.history.runs.find(r => r.key === state.selected);
            for (const run of state.history.runs) {
              if (/RUNNING|TRAINING/.test(run.status)) state.cache.delete(run.curve_path);
            }
          }
          await renderSelected();
        }
      } catch (error) {
        renderLive({...state.live, connection_status: 'DISCONNECTED', error: error.message});
        el('history-stamp').textContent = state.history ? '上次历史记录保留 · 当前读取失败' : 'N/A · 历史尚未加载';
      } finally { state.refreshing = false; }
      if (el('agent-secondary').open) await refreshAgent();
    }
    async function refreshAgent() {
      try {
        const m = await json('agent_benchmark_status.json');
        const current = m.current || m.last_unit || {}, trial = m.current_trial || {}, call = m.last_generator || {};
        const age = ageSeconds(m.timestamp);
        el('agent-status').textContent = display(m.status) + ' · ' + display(m.iteration_id) + ' · ' + display(m.finished_units) + '/' + display(m.total_units) + ' · ' + seconds(age) + '前' + (age !== null && age > 30 ? ' · 记录已过期' : '');
        const modelLines = Object.entries(m.models || {}).map(([name, v]) => name + ': TTFT P50/P95 ' + display(v.ttft_p50_ms) + '/' + display(v.ttft_p95_ms) + ' ms · ' + display(v.output_tokens_per_s) + ' Tokens/s（整请求）· ' + display(v.stream_output_tokens_per_s_estimate) + ' Tokens/s（TTFT 后估算）');
        const routerLines = Object.entries(m.router_latency_ms || {}).map(([name, v]) => name + ': P50/P95 ' + display(v.p50) + '/' + display(v.p95) + ' ms');
        el('agent-output').textContent = [
          '原因 ' + display(m.reason), 'Job / Trial ' + display(trial.job_id) + ' / ' + display(trial.trial_id),
          'Task / Policy ' + display(current.task_id ?? trial.task_id) + ' / ' + display(current.policy),
          'Step / Model / Effort ' + display(call.step) + ' / ' + display(call.returned_model ?? call.model) + ' / ' + display(call.effort),
          '官方 Verifier ' + display(m.verified_trials) + ' · 成功 ' + display(m.successes) + ' · 成功率 ' + display(m.success_rate),
          'Trial ' + display(trial.status ?? 'NOT_EVALUATED') + ' · 来源 ' + display(trial.verifier_path) + ' · Reward ' + display(trial.reward),
          'Token ' + display(m.generator_tokens) + ' · 配置价格估算 $' + display(m.generator_cost_usd) + ' · 实际费用 $' + display(m.complete_cost_usd),
          ...modelLines, ...routerLines,
          '工具 P50/P95 ' + display(m.tool_exec_p50_ms) + '/' + display(m.tool_exec_p95_ms) + ' ms',
          'Episode P50/P95 ' + display(m.episode_p50_s) + '/' + display(m.episode_p95_s) + ' s · Episode/h ' + display(m.episodes_per_hour),
          '每成功任务实际费用 $' + display(m.actual_cost_per_success_usd),
        ].join('\n');
      } catch (error) { el('agent-status').textContent = 'NOT_EVALUATED · ' + error.message; el('agent-output').textContent = ''; }
    }
    el('refresh').addEventListener('click', () => refresh(true));
    const applyFilters = () => { if (state.history) { renderRuns(); renderSelected(); } };
    for (const id of ['family', 'protocol', 'supervision', 'sampling-ratio', 'training-stage', 'run-status', 'data-volume']) el(id).addEventListener('change', applyFilters);
    el('exposure-field').addEventListener('change', () => { if (state.history) { el('data-volume').value = 'all'; fillDataVolumes(); applyFilters(); } });
    el('search').addEventListener('input', applyFilters);
    el('selected-run').addEventListener('change', () => { state.selected = el('selected-run').value; state.overlays.clear(); state.overlaySeededRun = null; renderRuns(); renderSelected(); });
    el('run-table').addEventListener('click', e => { const button = e.target.closest('[data-run]'); if (button) { state.selected = button.dataset.run; state.overlays.clear(); state.overlaySeededRun = null; renderRuns(); renderSelected(); } });
    el('overlay-toggle').addEventListener('change', renderSelected);
    el('overlay-list').addEventListener('click', e => {
      const action = e.target.closest('[data-overlay-action]')?.dataset.overlayAction;
      if (!action) return;
      const run = state.history?.runs.find(r => r.key === state.selected);
      const overlays = run ? state.history.runs.filter(r => r.key !== run.key && canOverlay(run, r)) : [];
      state.overlays = new Set(action === 'all' ? overlays.map(r => r.key) : []);
      renderSelected();
    });
    el('overlay-list').addEventListener('change', e => { const key = e.target.dataset.overlay; if (e.target.checked) state.overlays.add(key); else state.overlays.delete(key); renderSelected(); });
    el('curve-axis').addEventListener('change', renderSelected);
    el('agent-secondary').addEventListener('toggle', () => { if (el('agent-secondary').open) refreshAgent(); });
    renderLive({}); refresh(); setInterval(refresh, 10000);
    return {refresh, renderSelected, state};
  }
  const api = {COUNT_FIELDS, display, ageSeconds, splitSeries, validationGroups, canOverlay, epochCount, chartMarkup, liveCard,
    liveObservation, runRecovery, defaultAxis, hardwareMarkup, trainingEtaMarkup, retentionMarkup, comparisonText, censusMarkup, boot};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof window !== 'undefined') window.ModelRouterTrainingDashboard = api;
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, {once: true});
    else boot();
  }
})();
