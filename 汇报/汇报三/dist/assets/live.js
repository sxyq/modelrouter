/* ============================================================
   ModelRouter P16/P17 共享运行层
   所有概率、期望索引、P(True) 一律直接取自服务端响应字段，
   前端不做任何重算、平滑或补值。
   ============================================================ */

const MR = (() => {
  const params = new URLSearchParams(location.search);

  const DEFAULT_BRIDGE = 'http://127.0.0.1:8771/api';
  const API_BASE = (() => {
    const explicit = params.get('api');
    if (explicit) return explicit.replace(/\/+$/, '');
    if (location.protocol === 'http:' || location.protocol === 'https:') return '/api';
    return DEFAULT_BRIDGE;
  })();

  const S = {
    apiBase: API_BASE,
    health: null,
    models: null,
    lastPair: null,
    inflight: false,
    lastError: null,
  };

  /* ---------------- 预设场景（英文，真实可改） ---------------- */
  const PRESETS = {
    software_repair: {
      label: 'Software Repair',
      note: 'Failing test · subtle state bug',
      state: {
        task_domain: 'software_engineering',
        step_index: 3,
        context_chars: 1240,
        prior_tool_calls_count: 2,
        prior_error_signals_count: 1,
        prompt: 'Unit test test_refresh_token fails with 401 after token rotation; the store keeps a stale user id in memory.'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: 'Which model and effort tier should handle the next step of this repair?',
          criteria: {
            cheap_fast: 'Small fast model, low cost, no extended reasoning',
            mid_balanced: 'Mid-tier model with a moderate reasoning budget',
            strong_deep: 'Frontier model with high native effort and long reasoning'
          }
        },
        q_score: {
          type: 'score',
          instructions: 'Rate how difficult this repair step is.',
          criteria: ['trivial', 'easy', 'medium', 'hard', 'very_hard']
        },
        q_noul: {
          type: 'noul',
          instructions: 'Is a KV cache reuse likely for the next step?'
        }
      }
    },
    model_effort_routing: {
      label: 'Model × Effort',
      note: 'Joint model tier and effort choice',
      state: {
        task_domain: 'agent_routing',
        step_index: 7,
        context_chars: 8600,
        prior_tool_calls_count: 9,
        prior_error_signals_count: 0,
        prompt: 'Long multi-step planning episode: choose a model tier and native reasoning effort for the next tool call.'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: 'Select the joint model tier and native effort for the next call.',
          criteria: {
            cheap_fast: 'Small model with effort none',
            mid_balanced: 'Mid-tier model with effort medium',
            strong_deep: 'Frontier model with effort high'
          }
        },
        q_score: {
          type: 'score',
          instructions: 'Rate the reasoning load of the next call.',
          criteria: ['minimal', 'light', 'moderate', 'heavy', 'extreme']
        },
        q_noul: {
          type: 'noul',
          instructions: 'Will the prefix be reused from the previous call?'
        }
      }
    },
    production_ops: {
      label: 'Production Ops',
      note: 'Incident triage under budget',
      state: {
        task_domain: 'production_operations',
        step_index: 2,
        context_chars: 2150,
        prior_tool_calls_count: 1,
        prior_error_signals_count: 3,
        prompt: 'Alert: p99 latency doubled after a config rollout. Two downstream services are timing out.'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: 'Which model tier should triage this incident step?',
          criteria: {
            cheap_fast: 'Cheap model for a quick log scan',
            mid_balanced: 'Mid-tier model to correlate several signals',
            strong_deep: 'Frontier model for a full causal analysis'
          }
        },
        q_score: {
          type: 'score',
          instructions: 'Rate the operational risk of this step.',
          criteria: ['negligible', 'low', 'moderate', 'high', 'severe']
        },
        q_noul: {
          type: 'noul',
          instructions: 'Is the incident likely to be resolved without escalation?'
        }
      }
    }
  };

  /* ---------------- 工具 ---------------- */
  function clone(v) { return JSON.parse(JSON.stringify(v)); }

  function fmtTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    const pad = n => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  function fmtPct(p, digits = 1) {
    if (typeof p !== 'number' || Number.isNaN(p)) return '—';
    return `${(p * 100).toFixed(digits)}%`;
  }

  function fmtNum(n, digits = 4) {
    if (typeof n !== 'number' || Number.isNaN(n)) return '—';
    return n.toFixed(digits);
  }

  function shortId(id) {
    if (!id) return '—';
    const s = String(id);
    return s.length > 16 ? s.slice(0, 12) + '…' : s;
  }

  async function request(path, options = {}, timeoutMs = 200000) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const resp = await fetch(S.apiBase + path, {
        ...options,
        signal: ctrl.signal,
        headers: { 'Accept': 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) }
      });
      const text = await resp.text();
      let payload = null;
      try { payload = text ? JSON.parse(text) : null; } catch { payload = { detail: text }; }
      return { ok: resp.ok, status: resp.status, payload };
    } catch (err) {
      const name = err?.name === 'AbortError' ? 'TIMEOUT' : 'NETWORK_UNREACHABLE';
      return { ok: false, status: 0, payload: { detail: `${name}: ${err?.message || err}`, error_class: name } };
    } finally {
      clearTimeout(timer);
    }
  }

  function classify(result) {
    if (!result) return 'UNKNOWN';
    if (result.payload?.error_class) return result.payload.error_class;
    if (result.status === 0) return 'NETWORK_UNREACHABLE';
    if (result.status === 503) return 'MODEL_UNAVAILABLE';
    if (result.status === 502) return 'UPSTREAM_UNREACHABLE';
    if (result.status >= 500) return 'INFERENCE_FAILED';
    if (result.status === 207) return 'PARTIAL';
    return result.ok ? 'OK' : 'REQUEST_REJECTED';
  }

  function errorText(result) {
    const p = result?.payload;
    if (!p) return '无返回内容';
    if (typeof p.detail === 'string') return p.detail;
    if (Array.isArray(p.detail)) return p.detail.map(d => `${(d.loc || []).join('.')}: ${d.msg}`).join('; ');
    return JSON.stringify(p).slice(0, 600);
  }

  /* ---------------- API ---------------- */
  async function health() {
    const r = await request('/health', {}, 8000);
    S.health = r.ok ? r.payload : null;
    return r;
  }

  async function models() {
    const r = await request('/models', {}, 8000);
    S.models = r.ok ? r.payload : null;
    return r;
  }

  async function latest() {
    const r = await request('/latest', {}, 8000);
    if (r.ok) S.lastPair = r.payload;
    return r;
  }

  async function runOne(family, state, questions, testId) {
    const body = { router_family: family, state, questions };
    if (testId) body.test_id = testId;
    const r = await request('/systemone', { method: 'POST', body: JSON.stringify(body) }, 200000);
    return { ...r, family, request: body, reading: r.ok ? r.payload : null };
  }

  async function runPair(state, questions, testId) {
    const body = { state, questions, families: ['laya', 'kev'] };
    if (testId) body.test_id = testId;
    const r = await request('/pair', { method: 'POST', body: JSON.stringify(body) }, 260000);
    if (r.ok || r.status === 207) {
      S.lastPair = r.payload;
    }
    return r;
  }

  function newTestId() {
    const d = new Date();
    const pad = n => String(n).padStart(2, '0');
    const stamp = `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}-${pad(d.getHours())}${pad(d.getMinutes())}${pad(d.getSeconds())}`;
    const rand = Math.random().toString(16).slice(2, 6).toUpperCase();
    return `MR-${stamp}-${rand}`;
  }

  /* ---------------- 模型元数据 ---------------- */
  function modelMeta(family) {
    const list = S.models?.models || [];
    const found = list.find(m => (m.family || '').toLowerCase() === family);
    return found || null;
  }

  function checkpointLabel(family) {
    const m = modelMeta(family);
    if (!m) return '—';
    const ck = m.checkpoint_id && m.checkpoint_id.length > 18
      ? m.checkpoint_id.slice(0, 12) + '…'
      : m.checkpoint_id;
    return `${m.run_id} · ${ck}`;
  }

  /* ---------------- UI 小工具 ---------------- */
  let toastTimer = null;
  function toast(msg, isErr = false) {
    let el = document.getElementById('toast');
    if (!el) {
      el = document.createElement('div');
      el.id = 'toast';
      el.className = 'toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.className = 'toast show' + (isErr ? ' err' : '');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.className = 'toast'; }, 4200);
  }

  function setDot(el, cls) {
    if (!el) return;
    el.className = 'dot ' + (cls || '');
  }

  return {
    PRESETS, S,
    get apiBase() { return S.apiBase; },
    setApiBase(v) { S.apiBase = v.replace(/\/+$/, ''); },
    health, models, latest, runOne, runPair, newTestId,
    modelMeta, checkpointLabel,
    request, classify, errorText,
    clone, fmtTime, fmtPct, fmtNum, shortId,
    toast, setDot
  };
})();

window.MR = MR;
