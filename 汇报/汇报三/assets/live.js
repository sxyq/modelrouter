/* ============================================================
   ModelRouter P16/P17 共享运行层（中文面试版）
   所有概率、期望等级、P(真) 一律直接取自服务端响应字段，
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
    config: null,
    lastPair: null,
    inflight: false,
    lastError: null,
    logs: [],
  };

  const logSubs = [];
  let logSeq = 0;

  function pushLog(rec) {
    rec.seq = ++logSeq;
    S.logs.push(rec);
    if (S.logs.length > 300) S.logs.shift();
    logSubs.forEach(fn => { try { fn(S.logs); } catch (e) {} });
  }

  function onLog(fn) {
    logSubs.push(fn);
    try { fn(S.logs); } catch (e) {}
  }

  /* ---------------- 选项中文短标签 ---------------- */
  const LABELS = {
    cheap_fast: '轻量快速',
    mid_balanced: '均衡中档',
    strong_deep: '旗舰深度',
    small_model: '小模型',
    mid_model: '中模型',
    large_model: '大模型',
    retry_same: '原样重试',
    escalate: '升级处理',
    ask_human: '转人工确认',
    patch_now: '立即热修',
    rollback: '滚动回滚',
    observe: '继续观察',
    single_agent: '单智能体',
    multi_agent: '多智能体',
    human_loop: '人机协同'
  };

  function labelFor(key) {
    if (key == null) return '—';
    return LABELS[key] || String(key);
  }

  /* ---------------- 预设场景（中文，6 个 + 随机） ---------------- */
  const PRESETS = {
    software_repair: {
      label: '软件缺陷修复',
      note: '单元测试失败 · 内存残留旧状态',
      icon: '①',
      state: {
        task_domain: '软件工程',
        step_index: 3,
        context_chars: 1240,
        prior_tool_calls_count: 2,
        prior_error_signals_count: 1,
        prompt: '单元测试 test_refresh_token 在令牌轮换后返回 401；进程内存中仍保留过期的用户标识，缓存与数据库不一致。'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: '这一步应该交给哪一档模型处理？',
          criteria: {
            cheap_fast: '轻量快速：小参数模型，成本低，不做长推理',
            mid_balanced: '均衡中档：中等模型，给予适度推理预算',
            strong_deep: '旗舰深度：前沿模型，高推理档位，长链路分析'
          }
        },
        q_score: {
          type: 'score',
          instructions: '评估这一步的修复难度。',
          criteria: ['很简单', '较简单', '中等', '较困难', '非常困难']
        },
        q_noul: {
          type: 'noul',
          instructions: '下一步是否可能复用前缀缓存？'
        }
      }
    },

    model_effort_routing: {
      label: '模型 × 推理档位',
      note: '联合选择模型档位与推理预算',
      icon: '②',
      state: {
        task_domain: '智能体路由',
        step_index: 7,
        context_chars: 8600,
        prior_tool_calls_count: 9,
        prior_error_signals_count: 0,
        prompt: '长程规划任务进行到第 7 步，历史工具返回约 8600 字符；需要为下一次工具调用联合选择模型档位与原生推理强度。'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: '为下一次调用选择模型档位与推理强度的组合。',
          criteria: {
            cheap_fast: '轻量快速：小模型 + 关闭推理',
            mid_balanced: '均衡中档：中等模型 + 中等推理',
            strong_deep: '旗舰深度：强模型 + 高强度推理'
          }
        },
        q_score: {
          type: 'score',
          instructions: '评估下一次调用的推理负荷。',
          criteria: ['几乎为零', '较轻', '中等', '较重', '极重']
        },
        q_noul: {
          type: 'noul',
          instructions: '本次调用的前缀能否直接复用上一次的缓存？'
        }
      }
    },

    production_ops: {
      label: '生产故障处置',
      note: '发布后延迟翻倍 · 多服务超时',
      icon: '③',
      state: {
        task_domain: '生产运维',
        step_index: 2,
        context_chars: 2150,
        prior_tool_calls_count: 1,
        prior_error_signals_count: 3,
        prompt: '告警：配置发布后 p99 延迟翻倍，两个下游服务出现超时；缓存层对三个服务返回过期令牌。'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: '当前处置步骤应该用哪一档模型？',
          criteria: {
            cheap_fast: '轻量快速：快速扫一遍日志',
            mid_balanced: '均衡中档：关联多个信号做判断',
            strong_deep: '旗舰深度：完整因果分析'
          }
        },
        q_score: {
          type: 'score',
          instructions: '评估这一步的操作风险。',
          criteria: ['可忽略', '较低', '中等', '较高', '严重']
        },
        q_noul: {
          type: 'noul',
          instructions: '这次故障是否可能在不升级的情况下自行恢复？'
        }
      }
    },

    multi_agent: {
      label: '多智能体协作',
      note: '子任务分工与角色选择',
      icon: '④',
      state: {
        task_domain: '多智能体协作',
        step_index: 5,
        context_chars: 4300,
        prior_tool_calls_count: 6,
        prior_error_signals_count: 2,
        prompt: '主控智能体已拆出三个子任务：检索、改写、校验；其中校验子任务连续两次返回格式错误，需要决定下一步角色分配。'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: '校验子任务接下来由谁承担？',
          criteria: {
            single_agent: '单智能体：继续由当前角色完成',
            multi_agent: '多智能体：拆给专门校验角色',
            human_loop: '人机协同：关键结论交人工确认'
          }
        },
        q_score: {
          type: 'score',
          instructions: '评估继续自动化的风险。',
          criteria: ['无风险', '低风险', '中等', '偏高', '高风险']
        },
        q_noul: {
          type: 'noul',
          instructions: '这次拆分会带来可观的并行收益吗？'
        }
      }
    },

    long_context: {
      label: '长文档理解',
      note: '超长上下文 · 抽取统一结论',
      icon: '⑤',
      state: {
        task_domain: '文档理解',
        step_index: 12,
        context_chars: 42000,
        prior_tool_calls_count: 14,
        prior_error_signals_count: 0,
        prompt: '需要在一份四万余字符的技术方案中定位三处相互矛盾的容量假设，并给出统一后的结论。'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: '这一步应使用哪一档模型？',
          criteria: {
            cheap_fast: '轻量快速：先做粗略定位',
            mid_balanced: '均衡中档：逐段比对',
            strong_deep: '旗舰深度：全篇一致性推理'
          }
        },
        q_score: {
          type: 'score',
          instructions: '评估这一步的上下文压力。',
          criteria: ['很小', '较小', '中等', '较大', '极大']
        },
        q_noul: {
          type: 'noul',
          instructions: '后续步骤能否复用已读入的长前缀？'
        }
      }
    },

    code_review: {
      label: '代码审查',
      note: '并发改动 · 潜在竞态',
      icon: '⑥',
      state: {
        task_domain: '代码审查',
        step_index: 1,
        context_chars: 3800,
        prior_tool_calls_count: 0,
        prior_error_signals_count: 0,
        prompt: '本次合并请求改动了订单状态机与库存扣减的加锁顺序，需要判断是否存在并发竞态与死锁风险。'
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: '这次审查用哪一档模型？',
          criteria: {
            cheap_fast: '轻量快速：只看风格与明显缺陷',
            mid_balanced: '均衡中档：检查逻辑与边界',
            strong_deep: '旗舰深度：并发与死锁推理'
          }
        },
        q_score: {
          type: 'score',
          instructions: '评估这次改动的审查难度。',
          criteria: ['很简单', '较简单', '中等', '较困难', '非常困难']
        },
        q_noul: {
          type: 'noul',
          instructions: '这次改动是否可能影响线上已有的订单流程？'
        }
      }
    }
  };

  /* ---------------- 随机示例生成 ---------------- */
  const RANDOM = {
    domains: ['软件工程', '生产运维', '数据分析', '智能体路由', '文档理解', '代码审查', '客户支持'],
    subjects: ['单元测试', '接口网关', '缓存层', '消息队列', '调度器', '检索服务', '计费模块', '权限中间件'],
    symptoms: [
      '在流量高峰后返回 502',
      '连续三次超时并触发重试风暴',
      '出现偶发的数据不一致',
      '响应延迟从 120ms 升到 900ms',
      '返回了过期的配置快照',
      '在并发写入时丢失更新'
    ],
    actions: ['定位根因', '决定是否回滚', '拆分下一步子任务', '判断是否需要升级处理', '给出修复方案', '评估影响范围'],
    choiceSets: [
      {
        criteria: { cheap_fast: '轻量快速：小模型，低成本，短推理', mid_balanced: '均衡中档：中等模型，适度推理', strong_deep: '旗舰深度：强模型，长链路推理' },
        question: '下一步应该交给哪一档模型？'
      },
      {
        criteria: { retry_same: '原样重试：保持当前策略再试一次', escalate: '升级处理：换更强模型或更高推理档', ask_human: '转人工确认：由人做最终判断' },
        question: '下一步采取哪种处理方式？'
      },
      {
        criteria: { patch_now: '立即热修：先把线上影响压下去', rollback: '滚动回滚：退回上一个稳定版本', observe: '继续观察：先补齐监控再决定' },
        question: '当前应该先做哪件事？'
      }
    ],
    scoreSets: [
      { criteria: ['很简单', '较简单', '中等', '较困难', '非常困难'], question: '评估这一步的难度。' },
      { criteria: ['可忽略', '较低', '中等', '较高', '严重'], question: '评估这一步的风险。' },
      { criteria: ['几乎为零', '较轻', '中等', '较重', '极重'], question: '评估这一次的推理负荷。' }
    ],
    noulSets: [
      '下一步是否可能复用前缀缓存？',
      '这次处理是否可能在无人介入下完成？',
      '当前判断是否依赖了过期的上下文？'
    ]
  };

  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

  function randomScenario() {
    const subject = pick(RANDOM.subjects);
    const symptom = pick(RANDOM.symptoms);
    const action = pick(RANDOM.actions);
    const choiceSet = pick(RANDOM.choiceSets);
    const scoreSet = pick(RANDOM.scoreSets);

    return {
      label: '随机示例',
      note: `${subject} · ${symptom}`,
      icon: '✦',
      random: true,
      state: {
        task_domain: pick(RANDOM.domains),
        step_index: randInt(1, 14),
        context_chars: randInt(600, 48000),
        prior_tool_calls_count: randInt(0, 15),
        prior_error_signals_count: randInt(0, 5),
        prompt: `${subject}${symptom}，需要${action}。`
      },
      questions: {
        q_choice: {
          type: 'choice',
          instructions: choiceSet.question,
          criteria: { ...choiceSet.criteria }
        },
        q_score: {
          type: 'score',
          instructions: scoreSet.question,
          criteria: [...scoreSet.criteria]
        },
        q_noul: {
          type: 'noul',
          instructions: pick(RANDOM.noulSets)
        }
      }
    };
  }

  /* ---------------- 工具 ---------------- */
  function clone(v) { return JSON.parse(JSON.stringify(v)); }

  function fmtTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    const pad = n => String(n).padStart(2, '0');
    return `${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
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

  /**
   * 把一次请求拆成两段：
   *   infer  服务端自报的模型前向耗时（decision_latency_ms）
   *   net    客户端总耗时减去推理耗时（本机到服务端往返 + 排队 + 序列化）
   *   total  客户端实测总耗时
   */
  function splitTiming(payload, clientMs) {
    const infer = typeof payload?.decision_latency_ms === 'number' ? payload.decision_latency_ms : null;
    const total = typeof clientMs === 'number' ? clientMs
      : (typeof payload?.bridge_elapsed_ms === 'number' ? payload.bridge_elapsed_ms : null);
    if (infer == null && total == null) return { infer: null, net: null, total: null };
    if (infer == null) return { infer: null, net: null, total };
    if (total == null) return { infer, net: null, total: infer };
    return { infer, net: Math.max(0, total - infer), total };
  }

  function fmtChars(n) {
    if (typeof n !== 'number') return '—';
    if (n >= 10000) return `${(n / 1000).toFixed(1)}k`;
    return String(n);
  }

  async function request(path, options = {}, timeoutMs = 200000) {
    const t0 = performance.now();
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), timeoutMs);
    let result;
    try {
      const resp = await fetch(S.apiBase + path, {
        ...options,
        signal: ctrl.signal,
        headers: { 'Accept': 'application/json', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) }
      });
      const text = await resp.text();
      let payload = null;
      try { payload = text ? JSON.parse(text) : null; } catch { payload = { detail: text }; }
      result = { ok: resp.ok, status: resp.status, payload };
    } catch (err) {
      const name = err?.name === 'AbortError' ? 'TIMEOUT' : 'NETWORK_UNREACHABLE';
      result = { ok: false, status: 0, payload: { detail: `${name}: ${err?.message || err}`, error_class: name } };
    } finally {
      clearTimeout(timer);
    }
    const ms = Math.round(performance.now() - t0);
    result.elapsedMs = ms;
    pushLog({
      at: new Date(),
      method: (options.method || 'GET').toUpperCase(),
      path,
      status: result.status,
      ok: result.ok,
      ms,
      bytes: result.payload ? JSON.stringify(result.payload).length : 0,
      error: result.ok ? null : (result.payload?.error_class || 'ERROR'),
    });
    return result;
  }

  async function config() {
    const r = await request('/config', {}, 6000);
    if (r.ok) S.config = r.payload;
    return r;
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
    if (Array.isArray(p.detail)) return p.detail.map(d => `${(d.loc || []).join('.')}: ${d.msg}`).join('；');
    return JSON.stringify(p).slice(0, 600);
  }

  const ERROR_TITLES = {
    NETWORK_UNREACHABLE: '无法连接演示服务',
    UPSTREAM_UNREACHABLE: '与 A6000 的连接已断开',
    MODEL_UNAVAILABLE: '模型尚未加载',
    INFERENCE_FAILED: '推理失败',
    TIMEOUT: '请求超时',
    REQUEST_REJECTED: '请求被拒绝',
    PARTIAL: '两侧模型只成功了一侧',
    UNKNOWN: '未知错误'
  };

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
    return { ...r, family, request: body, reading: r.ok ? r.payload : null, clientMs: r.elapsedMs };
  }

  async function runPair(state, questions, testId) {
    const body = { state, questions, families: ['laya', 'kev'] };
    if (testId) body.test_id = testId;
    const r = await request('/pair', { method: 'POST', body: JSON.stringify(body) }, 260000);
    if (r.ok || r.status === 207) S.lastPair = r.payload;
    return r;
  }

  async function commitPair(testId, state, questions, results, startedAt) {
    const body = { test_id: testId, state, questions, results, started_at: startedAt };
    const r = await request('/pair/commit', { method: 'POST', body: JSON.stringify(body) }, 30000);
    if (r.ok) S.lastPair = r.payload;
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
    return list.find(m => (m.family || '').toLowerCase() === family) || null;
  }

  function checkpointLabel(family) {
    const m = modelMeta(family);
    if (!m) return '—';
    return `${m.run_id} · ${shortId(m.checkpoint_id)}`;
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
    PRESETS, S, LABELS,
    get apiBase() { return S.apiBase; },
    setApiBase(v) { S.apiBase = v.replace(/\/+$/, ''); },
    health, models, config, latest, runOne, runPair, commitPair, newTestId, randomScenario,
    modelMeta, checkpointLabel, onLog, pushLog,
    request, classify, errorText, ERROR_TITLES, splitTiming,
    clone, fmtTime, fmtPct, fmtNum, fmtShort: shortId, fmtChars, shortId,
    labelFor,
    toast, setDot
  };
})();

window.MR = MR;
