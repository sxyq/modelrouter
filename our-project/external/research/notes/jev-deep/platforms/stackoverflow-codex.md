# Stack Overflow / Codex Docs 平台调研：TypeSafe Jev 与 OpenAI Codex 接入

- 平台：stackOverflow + OpenAI Codex 官方文档 + TypeSafe / OpenRouter 社区资料
- 调研层级：tier 2/3，community，deep
- 目标：如何把 TypeSafe Jev（或 Jev 类决策模型）接到 OpenAI Codex / Codex CLI
- 查询日期：2026-09-29
- 脚本：`fast_search.py`（stackoverflow / ddgs）
- 直接抓取：`developers.openai.com`、`openai/codex`、`docs.typesafe.ai`、`openrouter.ai`、GitHub discussions

---

## 结论

Jev 不能作为 Codex 的 `model_provider` 直接替换 coder 模型。TypeSafe 官方文档明确：Jev 不是 chat / 代码补全模型，也没有 `model = "jev-latest"` 这种配置；其 HTTP 接口是 typed-decision 接口，不是 chat completions，也不是 Codex 当前自定义 provider 所要求的 Responses API。

Codex 本身对「OpenAI 兼容的自定义 provider」支持是确认的：在用户级 `~/.codex/config.toml` 里用 `[model_providers.<id>]` 配 `base_url`、`env_key`、`wire_api`。当前官方配置参考把 `wire_api` 写成仅支持 `"responses"`。因此「把 Jev 端点填进 `base_url`」在协议层不成立。

可落地的接入方式是旁路：Codex 继续跑正常 LLM；Jev 作为决策层，通过 TypeSafe agent skill、Codex hooks（`PermissionRequest` / `PreToolUse`）、MCP 工具或应用侧 SDK 调用。OpenRouter 有覆盖 Codex CLI 的官方 cookbook，这是目前最完整的社区 + 官方文档交叉证据。

「为 Codex agent 微调 Q&A」在本轮没有找到官方路径。TypeSafe 写明 Jev 不按客户数据做 fine-tune / LoRA，领域适配走 `state` + `instructions` + `criteria`。OpenAI fine-tuning 是 API 模型侧能力，与 Codex 自定义 provider 不是同一条链路。

---

## 核查范围

| 来源 | 动作 | 结果 |
| --- | --- | --- |
| Stack Overflow `fast_search.py` | 多组 provider / Jev / fine-tune 查询 | 多数为空；仅泛词 `codex CLI`、`Jev`、`OpenAI fine-tuning API` 有结果，且与 model_provider / Jev 接入无关 |
| DDGS `fast_search.py` | 本地 Python 3.9 SSL 协议失败 | 改用 `r.jina.ai` 代理抓取 |
| OpenAI Codex docs | `config.md`、`config-advanced`、`config-sample`、`config-reference`、`hooks` | 取得正式 provider / hook 配置片段 |
| openai/codex | GitHub discussions #864 / #4686 / #924 / #44453 / #6241 | 社区 provider 与 base_url 经验 |
| TypeSafe docs | introduction、system-one、api、models、coding-agents、agent-skill、quickstart | 确认 Jev 接口形态与官方接入建议 |
| OpenRouter | typesafe 模型页、Jev guide、Decisions API、auto-approve cookbook | 确认 OpenAI 兼容路由与 Codex hook 方案 |
| awesome-typesafe-jev | 社区项目索引 | 发现 Codex / agent 侧 Jev 工具，非 provider 配置 |

Stack Overflow 侧没有找到「codex CLI custom model provider」「codex model_providers config.toml」「Jev codex integration」「Jev model API OpenAI compatible」等查询的有效社区回答。社区证据主要来自 GitHub discussions 与 OpenRouter 文档。

---

## 已确认事项

### 1. Codex 自定义 model provider：官方支持，配置形态确认

配置位置：`~/.codex/config.toml`（或 `CODEX_HOME`）。官方 advanced config 给出的正式写法：

```toml
model = "gpt-6.1-sol"
model_provider = "proxy"

[model_providers.proxy]
name = "OpenAI using LLM proxy"
base_url = "http://proxy.example.com"
env_key = "OPENAI_API_KEY"

[model_providers.local_ollama]
name = "Ollama"
base_url = "http://localhost:11434/v1"

[model_providers.mistral]
name = "Mistral"
base_url = "https://api.mistral.ai/v1"
env_key = "MISTRAL_API_KEY"
```

官方约束：

- 内建 provider id 保留：`openai`、`ollama`、`lmstudio`、`amazon-bedrock`。自定义 provider 不得占用这些 id。
- 若只改内置 OpenAI 的上游地址，用 `openai_base_url`，不要再写 `[model_providers.openai]`：

```toml
openai_base_url = "https://us.api.openai.com/v1"
```

- 项目级 `.codex/config.toml` 会忽略 `model_provider`、`model_providers`、`openai_base_url` 等会改凭据与上游的键；这些必须写在用户级配置。
- CLI 可覆盖任意键：

```bash
codex --model gpt-6.1-sol
codex --config model='"gpt-6.1-sol"'
codex -c model_providers.<selected>.base_url=http://127.0.0.1:PORT/v1
```

- 本地开源模型走 `--oss` / `--local-provider` / `oss_provider = "ollama"`，而不是把 Ollama 模型名塞进普通 provider。

配置参考（config-reference）对自定义 provider 字段的说明：

| 字段 | 官方含义 |
| --- | --- |
| `model_providers.<id>` | 自定义 provider 表；`openai` / `ollama` / `lmstudio` 保留 |
| `name` | 展示名 |
| `base_url` | API base URL |
| `env_key` | 读取 API key 的环境变量名 |
| `wire_api` | 协议；当前文档写明仅支持 `"responses"`，且为默认值 |
| `http_headers` / `env_http_headers` | 静态或环境变量注入的 HTTP 头 |
| `query_params` | 追加 query 参数 |
| `auth.command` 等 | 外部命令取 bearer token；不可与 `env_key` 等混用 |
| `request_max_retries` / `stream_max_retries` / `stream_idle_timeout_ms` | 重试与流空闲超时 |
| `supports_websockets` | 是否支持 Responses API 的 WebSocket 传输 |
| `supports_standalone_web_search` | 独立 web search 能力广告位，默认 false |

官方 sample config 中本地 provider 示例也写成：

```toml
[model_providers.local_ollama]
name = "Ollama"
base_url = "http://localhost:11434/v1"
wire_api = "responses"
```

### 2. 「OpenAI 兼容 base URL」在 Codex 里的真实含义

社区讨论 #44453（Why OPENAI_BASE_URL does not redirect a Codex that has a config.toml）确认：

- Codex 解析上游时优先看 `model_providers.<name>.base_url`。
- 已存在 provider 配置时，导出 `OPENAI_BASE_URL` 不会改写 Codex 的实际请求地址。
- 运行时覆盖要用：

```bash
codex -c model_providers.<selected>.base_url=http://127.0.0.1:PORT/v1
```

- 社区作者同时指出，ChatGPT 登录模式下 ChatGPT backend 只是默认值；显式 provider `base_url` 仍可覆盖，两条路径线协议都是 Responses。

因此「OpenAI 兼容」在 Codex 当前语境里，主要指能讲 Responses API 的上游（或代理、Azure 风格网关、vLLM 若提供 Responses 兼容层）。纯 chat-completions-only 端点与官方 `wire_api = "responses"` 约束不一致。

### 3. Jev 本体：typed decision API，不是 Codex 可替换的 chat model

TypeSafe 官方文档结论：

| 项目 | 官方事实 |
| --- | --- |
| 产品定位 | Jev 是 TypeSafe 的 flagship System One 模型；做快速、结构化、软件可直接消费的决策 |
| 问题类型 | Choice / Score / Noul |
| 返回 | typed answer + probabilities + confidence（Noul 主要是 yes 概率） |
| 官方 HTTP 接口 | `POST https://api.typesafe.ai/v1/systemone` |
| 请求形状 | `state` + `model`（如 `jev-latest`）+ `questions` map |
| 是否 chat / 代码补全 | 否 |
| 是否可把 Codex 的模型改成 Jev | 官方 coding-agents 页明确否定：不存在 `model: "jev-latest"` 这种配置 |
| 官方接入建议 | 安装 TypeSafe agent skill，让 Codex 会写使用 TypeSafe 的代码；不要替换 coder 模型 |
| 模型 / 定价（文档页） | `jev-1.13.0` / alias `jev-latest`；输入计费，输出免费；context 约 64k，`state`+最长 question 约 32k |
| fine-tune | 文档写明不按客户数据做 fine-tune / LoRA；同一套权重服务所有账户 |
| 领域适配方式 | 把资料放进 `state`；把领域规则写进 `instructions` / `criteria`；把大判断拆成原子 question，在代码里合并 |

官方 quickstart 的最小 curl：

```bash
curl -X POST https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $TYPESAFE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "state": "Hi, I've been trying to connect my Stripe account for 3 days...",
  "model": "jev-latest",
  "questions": {
    "urgency": {
      "type": "noul",
      "instructions": "Does this message express urgency?"
    }
  }
}
EOF
```

API 错误语义（官方）：

| 状态 | 含义 |
| --- | --- |
| 401 | key 缺失或无效 |
| 422 | 请求体校验失败 |
| 429 | 超限 |
| 529 | TypeSafe 过载 |

官方 coding-agents 页还给出目标对照表：若目标是「替换 coding agent 背后的模型」，官方答复是继续用 LLM agent，把 Jev 单独用于需要快速校准决策的位置。

### 4. OpenRouter 上的 Jev：有 OpenAI 兼容入口，但决策面仍不是 chat completions

OpenRouter 文档页列出的 Typesafe 模型：

| 模型 ID | 说明 |
| --- | --- |
| `typesafe/jev-router` | 描述为按请求选模型与 reasoning effort 的 router；模型页示例走 OpenRouter chat surface |
| `~typesafe/jev-latest` | 跟踪最新 Jev |
| `typesafe/jev-1.13` | 当前 1.13 系列；$0.042 / M input tokens；output free |

Jev 在 OpenRouter 上的两个正式决策入口：

| Surface | Endpoint | 用途 |
| --- | --- | --- |
| Decisions API | `POST https://openrouter.ai/api/alpha/decisions` | HTTP / TS / Python / Go SDK |
| System One API | `POST https://openrouter.ai/api/v1/systemone` | TypeSafe JS/Python SDK 换 base URL 使用 |

Decisions API 请求示例（官方）：

```bash
curl --request POST \
  --url https://openrouter.ai/api/alpha/decisions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "typesafe/jev-1.13",
  "questions": {
    "is_bug": {
      "type": "noul",
      "instructions": "Is the customer reporting a software defect?",
      "criteria": {
        "false": "...",
        "true": "..."
      }
    }
  },
  "state": { "ticket": "..." }
}'
```

需要分清两件事：

1. OpenRouter 整站对很多模型提供 OpenAI 兼容 chat completions / Responses surface。
2. Jev 的正式决策面是 Decisions / System One，不是「把 decision JSON 塞进 chat messages」。

社区资源索引 `AbdelStark/awesome-typesafe-jev` 对 OpenRouter 用法的表述是：用 OpenRouter key 和 decisions request shape，不要把这些 questions 发给 chat-completions API。

`typesafe/jev-router` 的模型页展示了 chat.completions 风格调用样例。从描述看它更像「用 Jev 做路由的模型/router 产品」，与 `POST /v1/systemone` 的 decision API 不是同一接口。把它直接写进 Codex `[model_providers]` 是否可用，本轮未在官方文档中确认。

### 5. TypeSafe 官方给出的 Codex 接入路径：skill + 旁路决策，不是 provider

TypeSafe agent skill 文档写明覆盖 Claude Code、Codex 和其他 skill 环境。

安装方式（官方）：

```bash
# Claude Code
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai

# 其他 agent，含 Codex 等
npx skills add typesafe-ai/skills --skill typesafe-ai
```

skill 作用：给 coding agent 提供 TypeSafe API、primitives、patterns 上下文，让它写出正确的 TypeSafe 调用代码。skill 本身不改 Codex 的 `model_provider`。

GitHub 上的官方 skill 仓库：`typesafe-ai/skills`，路径 `skills/typesafe-ai/SKILL.md`。

### 6. 社区方案：Codex hooks + Jev，这是目前最完整的可落地模式

OpenRouter cookbook：`Auto-Approve Coding Agent Permission Prompts with Jev`，明确覆盖 Codex CLI。

模式：

1. 代码里保留高风险命令静态名单（递归删除、force push、硬重置、提权、发布部署、凭据文件、把字符串再丢给 shell/解释器的写法）。命中名单的请求不调 Jev，直接回到人工提示。
2. 其余 shell 请求调用 Jev 的两个 Noul：命令是否可撤销、是否服务于当前任务。
3. 所有问到的概率都达到阈值（示例 `APPROVE_AT = 0.9`）才自动放行。
4. 任何不确定、超时、错误、概率异常，都保持 Codex 原有提示流程。错误时多一次人工确认，而不是多跑一条命令。

Codex hooks 官方文档确认 `PermissionRequest`：

- 触发条件：Codex 即将请求审批，例如 shell 提权。
- 输入字段：`cwd`、`tool_name`、`tool_input`，以及 Codex 特有的 `turn_id`；`Bash` 的命令在 `tool_input.command`。
- 放行输出：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "allow"
    }
  }
}
```

- 拒绝输出：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": {
      "behavior": "deny",
      "message": "Blocked by repository policy."
    }
  }
}
```

- 多个匹配 hook 同时有决策时，任一 `deny` 优先。
- 不要返回 `updatedInput` / `updatedPermissions` / `interrupt`；文档写明这些字段保留且会 fail closed。
- 非受管 hook 必须在 CLI 里经 `/hooks` 审阅并信任后才会运行。

`PreToolUse` 也能在工具执行前拒绝：

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by hook."
  }
}
```

OpenRouter cookbook 对 Codex 的实操注意点：

- Codex 的 `tool_input.description` 常是审批问题本身，例如「May I run git add ... outside the sandbox?」，不适合直接当「任务文本」喂给 Jev。
- 示例脚本用 Codex 的 `turn_id` 识别这种情况，只问 reversibility。
- 作者记录：在 Codex CLI 0.155.1 中，用审批问题当 task 时，`serves_task` 可能只有约 0.54，导致几乎不自动放行；这正是阈值逻辑要处理的偏差。
- 仓库侧注册点：`.codex/hooks.json` 或 `~/.codex/config.toml` / `~/.codex/hooks.json`。

hooks 注册示例（官方文档形态）：

```json
{
  "hooks": {
    "PermissionRequest": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "bun /absolute/path/jev-permission-hook.ts",
            "timeout": 30,
            "statusMessage": "Asking Jev about reversibility"
          }
        ]
      }
    ]
  }
}
```

等价 TOML：

```toml
[[hooks.PermissionRequest]]
matcher = "^Bash$"

[[hooks.PermissionRequest.hooks]]
type = "command"
command = "bun /absolute/path/jev-permission-hook.ts"
timeout = 30
statusMessage = "Asking Jev about reversibility"
```

### 7. 社区讨论里的 provider / 本地模型经验

| 讨论 | 结论 |
| --- | --- |
| #864 Getting Codex Working with Ollama | 本地模型能连上，但弱模型在 `apply_patch` 等工具调用上会把 JSON 原样吐回；提问者最终结论是 CLI 没问题，需要更强模型 |
| #4686 when running with ollama, tools dont work | 问题存在，社区未给出已确认解法 |
| #924 Are other provider's models supported? | 早期社区用过 `codex --provider gemini/deepseek/ollama` 等形态；与当前正式 config 语法有版本差异，不能直接当现行配置照抄 |
| #6241 multiple models for the same model_providers | 同一 provider 表下，模型选择在顶层 `model` / `model_provider` 处理 |
| #44453 OPENAI_BASE_URL | 见上文；config.toml 的 `base_url` 优先级高于环境变量 |

这些讨论支持「Codex 可以打第三方 base URL」，同时支持「协议能力与模型工具调用能力决定成败，不是只填个 URL 就行」。

### 8. Jev 类决策模型的替代实现路径

TypeSafe 仓库提供 `system-one-adapter-python`：用 OpenAI / Anthropic / Gemini 等 LLM 实现与 `typesafe_sdk` 相同的 `system_one(state, questions)` 接口。

要点：

- 这是「LLM 模拟 System One 接口」，不是把 Jev 本体接进 Codex provider。
- 自定义 OpenAI 兼容端点默认走 Chat Completions，可显式 `api="responses"`。
- 用途偏对比与实验，不是官方推荐的 Codex 接入方式。

若目标是「Jev-like 决策层 + Codex coder」，该 adapter 说明了应用侧可怎么组织 typed question；它本身仍不会让 Codex 把决策模型当成 coder model。

---

## 社区项目索引（发现，非官方保证）

来自 `awesome-typesafe-jev` 的相关条目：

| 项目 | 作用 | 与 Codex 关系 |
| --- | --- | --- |
| TypeSafe Agent Skills（官方） | Codex / Claude Code 用的 TypeSafe 技能 | 官方推荐主路径 |
| OpenRouter auto-approve cookbook | Codex / Claude Code / Cursor / OpenCode 的 permission hook + Jev | 官方文档级方案 |
| `suenot/codex-jev-router` | 曾做 Jev 选模型的 subagent router；现主推本地证据检索 MCP | 维护者已不推荐安装旧路由路径；基准还显示 Jev 路由未必比单一强模型便宜 |
| `0xNatoshi/jev-codex-router` | 本地 Codex Router 扩展，问 Jev 模型档位与思考深度 | 社区实验，未见官方背书 |
| `formulahendry/jev-acp` | Jev 决策 ACP agent | 非 Codex provider |
| `blakestone-x/jev-mcp` | 把 Jev 能力暴露成 MCP 工具 | 更接近「旁路工具」而非 model_provider |
| `typesafe-ai/system-one-adapter-python` | LLM 实现 System One 接口 | 实验 / 对比 |
| Canny 等 | Codex hooks 记账 + 可选 Jev advisory 判断 | 旁路 |

---

## 训练 / 微调相关

| 问题 | 本轮结论 | 证据级别 |
| --- | --- | --- |
| 能否 fine-tune Jev 以适配自己的 Codex 场景 | 不能。TypeSafe 文档写明不按客户数据 fine-tune / LoRA；同一权重服务所有账户 | 官方文档确认 |
| TypeSafe 领域适配怎么做 | `state` 放资料；`instructions` / `criteria` 写规则；拆原子 question；阈值在代码里 | 官方文档确认 |
| OpenAI fine-tuning 能否产出「Codex 专用决策模型」 | 未找到官方 Codex 文档把 fine-tune 模型接进 `model_providers` 的路径。OpenAI fine-tuning 文档属于 API / model optimization 链路 | 未确认为 Codex 产品路径 |
| Stack Overflow 上的 fine-tune / codex agent Q&A | 基本为空；仅命中 2023 年 GPT-3 无监督 fine-tune 提问，与本目标无关 | 已确认无有效 SO 答案 |
| 「Jev-like」能否靠微调一个 chat model 来做 | 技术上可做 LLM 分类/评分，但那是另一套工程；TypeSafe 体系走 calibrated decision + request-time 适配，不是客户微调权重 | 部分推断 |

---

## 可执行路径（按优先级）

### 路径 A：Codex 保持正常 coder 模型 + Jev 作为权限/决策旁路（推荐）

适用：想在 Codex 里用 Jev 做审批放行、风险判断、路由，而不是替换 coding model。

步骤：

1. Codex 正常登录，继续使用 ChatGPT / API coder 模型。
2. 取得 Jev 调用凭据：
   - TypeSafe 直连：`TYPESAFE_API_KEY` → `POST https://api.typesafe.ai/v1/systemone`
   - 或 OpenRouter：`OPENROUTER_API_KEY` → `POST https://openrouter.ai/api/alpha/decisions`
3. 实现一个小 hook 脚本：读 stdin JSON，静态名单优先，否则调用 Jev 的 Noul/Choice/Score，按阈值返回 allow / deny / 不表态。
4. 在 `~/.codex/config.toml` 或项目 `.codex/hooks.json` 注册 `PermissionRequest`（也可加 `PreToolUse`）。
5. 在 CLI 用 `/hooks` 审阅并信任新 hook。
6. 从低风险命令开始试跑；阈值从 0.9 起，再按误放行/误提示调整。

验收标准：

- 静态名单命令不触发 Jev。
- Jev 高置信时提示消失，命令按原审批策略执行。
- Jev 出错、超时、低置信时仍出现原提示，而不是自动放行。
- 不覆盖 Codex 自身 deny 规则。

禁止范围：

- 不要把 `model_provider` 指到 Jev 的 `/v1/systemone`。
- 不要用 hook 输出去改写本不该由 hook 改的权限边界。

### 路径 B：TypeSafe agent skill，让 Codex 写「会调用 Jev 的代码」

适用：目标是在自己的应用里集成 Jev，而不是让 Codex 自己变成 Jev agent。

步骤：

1. `npx skills add typesafe-ai/skills --skill typesafe-ai`，或手动安装 `skills/typesafe-ai`。
2. 提示 Codex「use the TypeSafe skill」。
3. 用官方 docs / cookbooks 驱动实现；问题与阈值集中放在单一代码文件，便于人工审阅。

### 路径 C：自定义 provider 接入真正的 Responses API 上游（与 Jev 无关，但满足「接自定义模型」诉求）

适用：真正要把 coder 模型换成 vLLM / 代理 / Azure 等。

步骤：

1. 确认上游实现的是 Responses API，或提供能被 Codex 接受的 Responses 兼容层。
2. 用户级 `~/.codex/config.toml`：

```toml
model_provider = "local"
model = "<your-model-id>"

[model_providers.local]
name = "Local Responses-compatible"
base_url = "http://127.0.0.1:8000/v1"
env_key = "LOCAL_API_KEY"
wire_api = "responses"
```

3. 或只改内置 OpenAI 上游：

```toml
openai_base_url = "https://your-proxy.example.com/v1"
```

4. 运行：

```bash
codex
codex --model <your-model-id>
codex -c model_providers.local.base_url=http://127.0.0.1:8000/v1
```

风险：社区经验表明弱模型在工具调用上会失败；协议兼容不等于 agent 可用。

### 路径 D：MCP 工具形态

适用：想让 Codex 在会话里主动调用「decision 工具」。

- 用 Codex `mcp_servers` 配置本地或 HTTP MCP。
- 把 Jev 的 Choice/Score/Noul 封装成工具。
- 这仍是旁路工具，不是 model_provider。

官方 MCP 文档确认 Codex 支持 STDIO 与 Streamable HTTP MCP，并写在 `config.toml`。

---

## 错误与排错清单

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 把 Jev base URL 写进 `[model_providers]` 后请求形状不对 | Jev 是 systemone / decisions，不是 chat 或 Responses chat | 改走 hook / MCP / 应用 SDK |
| `wire_api = "chat"` 或旧示例失效 | 当前配置参考写明仅 `"responses"` | 按现行 config-reference；需要 chat 时先确认上游是否有 Responses 层 |
| 导出 `OPENAI_BASE_URL` 后流量没变 | config.toml 中已有 provider `base_url` 优先 | 用 `codex -c model_providers.<id>.base_url=...`，或直接改用户级 config |
| 项目 `.codex/config.toml` 里改 provider 不生效 | 项目层忽略这些键 | 写到 `~/.codex/config.toml` |
| 自定义 provider id 被拒或行为异常 | 占用了 `openai` / `ollama` / `lmstudio` 等保留 id | 换成 `proxy` / `local` 等 id |
| Jev API 401 | key 无效或 header 不对 | 核对 `Authorization: Bearer` |
| Jev API 422 | questions / state 形状不对 | 按 API 参考补齐 `type`、`instructions`、`criteria` |
| Jev API 429 / 529 | 超限或过载 | SDK 默认 backoff；HTTP 直连要自行退避 |
| hook 不执行 | 非受管 hook 未信任 | CLI `/hooks` 审阅信任 |
| hook 返回 allow 后 Codex 仍失败 | hook 用了保留字段，或 deny 优先 | 只返回官方允许的 `decision.behavior` |
| Ollama / 本地模型连上但工具调用坏掉 | 模型能力不足，不是 provider 配置唯一问题 | 换更强模型；参考 discussion #864 |
| `serves_task` 一直偏低 | Codex 把审批问题写进 `tool_input.description` | 按 cookbook 用 `turn_id` 判定，只问 reversibility |
| 想用 `typesafe/jev-1.13` 走 chat completions | 官方索引明确不要这样发 | 改 Decisions / System One endpoint |
| 想 fine-tune Jev | 产品不提供客户数据 fine-tune | 改 request-time 适配 |

---

## 证据与限制

### 强证据

- Codex provider / wire_api / 项目层忽略规则：OpenAI Codex config-advanced、config-sample、config-reference。
- Codex `PermissionRequest` / `PreToolUse` 输出契约：OpenAI Codex hooks 文档。
- Jev API 形态、非 chat 定位、不提供客户 fine-tune：TypeSafe introduction、system-one、api、models、coding-agents。
- OpenRouter Decisions / System One endpoint 与 Codex hook cookbook：OpenRouter 官方文档。
- OPENAI_BASE_URL 与 config.toml 优先级：openai/codex discussion #44453。

### 弱证据 / 发现级

- `typesafe/jev-router` 是否能作为 Codex `model_providers` 的 `model` 使用：仅有 OpenRouter 模型页 chat 示例，未见 Codex 官方确认。
- 社区 `codex-jev-router` 等项目效果：多为实验，维护者自己已下调旧路由路径。
- Stack Overflow 对 provider / Jev 接入：基本无有效命中。

### 工具限制

- `fast_search.py --provider ddgs` 在本机 Python 3.9 报 TLS 协议错误，未能产出 DDGS 结果。
- `developers.openai.com` 直连有 403，正文经 `r.jina.ai` 代理读取；仓库内 `docs/config.md` 已改为指向站外文档。
- GitHub code search API 未登录返回 401，未能做源码级全局检索。
- 未在本机对真实 Codex 实例做接入验证；报告是文档与社区证据汇总。

---

## 未确认事项、风险与未修改对象

### 未确认

1. `typesafe/jev-router` 在 OpenRouter Responses surface 下，是否满足 Codex `wire_api = "responses"` 的完整工具调用与流式要求。
2. 当前社区里是否存在任何「把 `/v1/systemone` 包装成 Responses 兼容 coder」的生产方案；本轮未找到。
3. OpenAI 官方是否计划让 Codex 的 model_providers 支持非 Responses 的 typed-decision 协议；现行文档未写。
4. 「fine-tune 一个 decision model 再接进 Codex」的端到端官方流程；未找到。
5. Stack Overflow 上是否有更长尾、带 `openai-codex` 标签的 provider 问答；本轮多组查询为空，可能存在检索面限制。

### 风险

- 把 decision API 当 chat provider 接入，几乎必然在请求形状与流式行为上失败。
- 用 hook 自动放行命令时，静态名单必须先于模型判断；模型只做「可撤销 / 是否服务任务」这类窄判断。
- 项目级 hook 只在项目被信任时加载；不可信任项目里 hook 不会替你兜底。
- 弱模型接 Codex 会在工具调用阶段失败，排错时容易误判成 provider 配置问题。

### 本轮未修改对象

本轮未修改文件，仅进行了查询、核查或验证。  
唯一新增/写入：调研报告本身。

报告路径：`/Users/sunyiyang/Desktop/Project/路由/research/jev-deep/platforms/stackoverflow-codex.md`

未触碰：`~/.codex/config.toml`、`~/.codex/hooks.json`、本机 Codex 安装、任何 Jev / OpenRouter 密钥、源码仓库。

---

## 最终建议

如果目标是「Codex 用 Jev 做决策」，推荐路径 A：正常 coder 模型 + Codex `PermissionRequest` / `PreToolUse` hook + Jev Decisions/System One API。官方 hooks 文档和 OpenRouter cookbook 已给出输入输出契约与阈值策略。

如果目标是「Codex 自己变成 Jev agent」，官方结论是否定的；TypeSafe 明确没有 `model = "jev-latest"` 这种 provider 配置。

如果目标只是「Codex 接自定义模型」，路径 C 成立：用户级 `model_providers.<id>` + `base_url` + `wire_api = "responses"`；这与 Jev 接入是两条线，不要混写。
