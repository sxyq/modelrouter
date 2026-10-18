# P16 / P17 真实双模型决策 Demo

本目录只包含 **P16** 与 **P17** 两页真实交互展示，不包含其余 18 页。
两页均为原生 HTML/CSS/JavaScript，所有概率、期望索引与 P(True) 都来自 A6000
上真实运行的 `POST /system-one` 前向推理，**没有预置、模拟或前端重算的数值**。

---

## 1. 启动（二选一）

### A. 直连 A6000（当前环境已验证）

```bash
cd "汇报/汇报三"
python assets/bridge_server.py --port 8771
```

本地配置 `assets/local_config.json` 记录上游地址（**已被 .gitignore 排除，不提交**）。
若文件不存在，默认连 `http://127.0.0.1:8000`（SSH 隧道场景）。

### B. 经 SSH 隧道（Mac / 笔记本通用）

```bash
ssh -N -L 8000:127.0.0.1:8000 <你的 A6000 主机>
cd "汇报/汇报三"
python3 assets/bridge_server.py --port 8771 --upstream http://127.0.0.1:8000
```

启动后可先自检：

```bash
curl -s http://127.0.0.1:8771/api/health
curl -s http://127.0.0.1:8771/api/models
```

---

## 2. 打开与切换

| 入口 | 地址 | 说明 |
| --- | --- | --- |
| P16 | `http://127.0.0.1:8771/interactive/P16.html` | 真实三类型决策 Live Demo |
| P17 | `http://127.0.0.1:8771/interactive/P17.html` | 同一轮结果对比与解释 |
| 播放器 | `http://127.0.0.1:8771/dist/deck.html` | 16:9 全屏，→ / ← 翻页，F 全屏 |

- **P16 → P17**：右下角「P17 比较 →」，或按 `→`。
- **P17 → P16**：右下角「← P16」，或按 `←`。
- **P16 空态彩排**：加 `?fresh=1`，例如 `P16.html?fresh=1`，不自动恢复上一轮。
- **PPT 集成**：在 PPT 里放一个指向 `P16.html` 的超链接，放映时点击即进入浏览器；
  演示结束关闭浏览器窗口即回到 PPT 当前页。

> 若直接双击 `interactive/P16.html` 用 `file://` 打开，页面会尝试连
> `http://127.0.0.1:8771/api`，需先启动桥接服务（已开启 CORS）。

---

## 3. 页面操作

**P16**：三个英文预设（Software Repair / Model × Effort / Production Ops）→ 可改
`task_domain / step_index / context_chars / prior_tool_calls_count /
prior_error_signals_count / prompt`，以及 Choice、Score、Noul 三问的 instructions 与
选项；点击 `Run Laya` / `Run Kev` / `Compare Both`。底部可展开本次真实 Request/Response。

**P17**：自动读取 `Compare Both` 写入的同一轮 `test_id` 结果；「重新比较」会用
**同一份 State 与 Questions** 再发一轮，整轮替换而不是混轮。

---

## 4. 请求契约（实测）

```json
{
  "router_family": "laya | kev",
  "state": { "task_domain": "...", "step_index": 3, "context_chars": 1240,
             "prior_tool_calls_count": 2, "prior_error_signals_count": 1, "prompt": "..." },
  "questions": {
    "q_choice": { "type": "choice", "instructions": "...",
                  "criteria": { "opt_a": "description A", "opt_b": "description B" } },
    "q_score":  { "type": "score", "instructions": "...",
                  "criteria": ["trivial", "easy", "medium", "hard", "very_hard"] },
    "q_noul":   { "type": "noul", "instructions": "..." }
  }
}
```

要点：`choice.criteria` 必须是 **对象**（选项→描述），`score.criteria` 必须是
**数组**（等级名，从低到高）。这是 Kev 侧 TypeSafe `SystemOneRequest` 的强校验，
Laya 侧同样的形状也可用，因此两页共用一份请求体。

---

## 5. 交付物

| 文件 | 内容 |
| --- | --- |
| `interactive/P16.html` / `P17.html` | 两页可交互主体 |
| `assets/bridge_server.py` | 本地桥接：同源托管 + 转发 + 同轮配对 + 存档 |
| `assets/live.css` / `live.js` | 暖白主题与共享运行层 |
| `assets/live-evidence.json` | 三轮真实输出（已脱敏，无内网地址） |
| `assets/shots/*.png` | P16 / P17 / 原始 JSON / 断连等实拍截图 |
| `assets/video/*.webm` | 连续操作录屏（网络故障备用） |
| `dist/deck.html` + `deck_bundle.zip` | 两页播放器与离线包 |
| `runs/` | 每轮原始 Request/Response 存档（**本地保留，不提交**） |

复现截图与录屏：

```bash
export NODE_PATH="C:/Users/syy/.workbuddy/binaries/node/workspace/node_modules"
node scripts/record.cjs     # 两次真实比较 + 修改后比较 + 断连测试 + 录屏
node scripts/quickshot.cjs  # 仅刷新两张主截图
```

---

## 6. 科学解释边界（P17 已写明）

- 同一输入下两种架构可能选到同一选项，却给出不同概率分布；本次实测两者选到了不同选项。
- Score 的期望等级索引与 Noul 的 P(True) 是**不同指标**，不能相加、相减或互换。
- 延迟只代表本次部署环境与本次请求，不构成严格性能基准。
- 一次 Demo 不能证明任一模型在独立测试集上更准确。
- 模型自报 `confidence` 不等于真实任务成功率。

---

## 7. 已完成的真实验收

| 项目 | 结果 |
| --- | --- |
| Laya Choice / Score / Noul | ✅ 真实返回 |
| Kev Choice / Score / Noul | ✅ 真实返回 |
| 同 State 双模型并排 | ✅ `test_id` 一致 |
| 修改问题后再次比较 | ✅ 新 `test_id`，数值随之变化 |
| 断连状态 | ✅ 显示 `DISCONNECTED / NETWORK_UNREACHABLE` |
| 老 `/route` 接口 | ✅ 仍可用（本次实测 `selected=gpt-5`, fallback=false） |
| 训练进程 | ✅ 全程未重启；GPU 利用率与 uptime 持续，服务双模型 `inference_verified=true` |

详细的数值见 `assets/live-evidence.json` 与 `assets/shots/report2.json`。
