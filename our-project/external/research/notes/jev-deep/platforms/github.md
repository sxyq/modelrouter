# GitHub platform report: TypeSafe AI Jev decision model

- platform_id: github
- tier: 1
- scene: open-source
- depth: deep
- research date: 2026-09-29 / 2026-09-30
- scope: public GitHub only; no tokens; no private-repo cloning
- report path: `/Users/sunyiyang/Desktop/Project/路由/research/jev-deep/platforms/github.md`

---

## 1. Identity

Jev is TypeSafe AI's flagship System One model for typed decisions. It takes unstructured state plus typed questions and returns typed answers with probabilities, rather than generating free text. Primitives observed in official and community docs:

| Primitive | Meaning | Return |
| --- | --- | --- |
| `choice` | one option from a known set | chosen value + probabilities + confidence |
| `score` | position on an ordered rubric | probability-weighted score + legend + probabilities + confidence |
| `noul` | probability a statement is true | probability in `[0,1]` |

Hosted access facts (from Anil-matcha/awesome-jev-by-typesafe, which cites TypeSafe docs):

- Endpoint: `POST https://api.typesafe.ai/v1/systemone`
- Alias / version: `jev-latest` / `jev-1.13.0`
- Listed price: `$0.042 / 1M` input tokens; output tokens listed as free
- Context: `64k` tokens per request; docs also mention `32k` for state plus longest question
- Modality: text only
- Official SDKs: Python (`typesafe-sdk`), TypeScript (`@typesafe-ai/sdk`)
- Gateways: Vercel AI Gateway (`typesafe-ai/jev`), Cloudflare Workers AI (`typesafe/jev`)
- Official agent skill: documented for Claude Code, Codex, and other coding agents

**Official GitHub org inventory (github.com/typesafe-ai, 11 public repos):**

| Repo | License | Stars (discovery) | Role |
| --- | --- | --- | --- |
| `typesafe-sdk-python` | MIT | 252 | Official Python SDK |
| `typesafe-sdk-js` | MIT | 257 | Official TypeScript/JS SDK |
| `system-one-adapter-python` | MIT | 345 | Drop-in TypeSafeClient backed by LLM APIs |
| `skills` | MIT | 2.4k | Official agent skills for TypeSafe/System One |
| `WorkflowEvals` | Apache-2.0 | 1 | Public eval workflow code |
| `n8n-nodes-typesafe-ai` | MIT | 1 | n8n integration |
| `daggerverse` | Apache-2.0 | 23 | Dagger modules collection |
| `pulumi-clickhouse` | Apache-2.0 | 3 | ClickHouse Pulumi provider |
| `typesafe-ai.github.io` | n/a (site) | 2 | Docs site |
| `LLaDA` | MIT | 12 | Official PyTorch for "Large Language Diffusion Models" (not Jev training) |
| `vllm` | Apache-2.0 | 3 | Upstream vLLM fork/mirror (not Jev-specific) |

**Key official finding:** there is **no public TypeSafe repo for Jev training code, model weights, or a Jev architecture release**. Official artifacts are SDKs, adapter, agent skill, evals, and integrations. Jev is accessed as a hosted API.

---

## 2. Repos table

Stars are discovery signals only, not quality proof. License is from the repo LICENSE badge/file where confirmed via README page.

### 2.1 Official TypeSafe

| URL | Role | License | Train-related content |
| --- | --- | --- | --- |
| https://github.com/typesafe-ai/typesafe-sdk-python | Official Python SDK | MIT | Client only; no training |
| https://github.com/typesafe-ai/typesafe-sdk-js | Official JS/TS SDK | MIT | Client only; no training |
| https://github.com/typesafe-ai/system-one-adapter-python | Official adapter: same `system_one` API backed by OpenAI/Anthropic/Gemini or OpenAI-compatible endpoints | MIT | No training; useful for "System One-shaped API without TypeSafe Jev" |
| https://github.com/typesafe-ai/skills | Official agent skills; install via Claude Code plugin or `npx skills add typesafe-ai/skills --skill typesafe-ai` | MIT | SKILL.md teaches workflow design; explicitly covers Codex and other agents |
| https://github.com/typesafe-ai/WorkflowEvals | Public eval workflow code | Apache-2.0 | Eval, not model training |

### 2.2 Community discovery indexes (awesome lists)

| URL | Role | License | Train-related content |
| --- | --- | --- | --- |
| https://github.com/yibie/awesome-jev | Largest field guide (~2k stars); category files + agent tags (Codex, Claude Code, Pi, MCP) | No LICENSE seen on README page (CONTRIBUTING only) | Index only; no training code |
| https://github.com/Anil-matcha/awesome-jev-by-typesafe | Evidence-backed use cases, patterns, official SDK links, agent-skill path | MIT | API/SDK usage; no training |
| https://github.com/v-modal/awesome-jev-tools | Tools index for Jev | not confirmed here | Index |
| https://github.com/cobanov/awesome-jev | Source-backed ecosystem list | not confirmed here | Index |
| https://github.com/AnotiaWang/awesome-jev | Broad index | not confirmed here | Index |
| https://github.com/AbdelStark/awesome-typesafe-jev | Field guide incl. SDKs, demos, agent tools, evaluations | not confirmed here | Index |
| https://github.com/walidboulanouar/awesome-jev-use-cases | Use-case catalog, CC0 claim | CC0 (from search excerpt) | Index |

Note: `yibie/awesome-jev` itself warns that listings are not endorsements and that same-day bulk submissions may be unproven.

### 2.3 Open / reimplementation / fine-tuneable Jev-like systems

| URL | Role | License | Train-related content |
| --- | --- | --- | --- |
| https://github.com/jaredpalmer/kev | **Trainable Jev-like family** on Qwen3.5/3.8; System One API drop-in; open weights on HF | Apache-2.0 | Full training entrypoint `kev.train`, fine-tune skill, Modal deploy, model cards, eval suites, HF weights |
| https://github.com/featherless-ai/simple-jev | Turn any open model into a classifier/Jev endpoint via next-token logits; public demo API | Apache-2.0 | **RFDT** fine-tune pipeline (`RFDT/prepare.py`, `train.py`, `export.py`); LoRA or full-weight; teacher labeling |
| https://github.com/nokia-applied-research/AnyJev | Any LLM → Jev-style decision model; typed decisions + calibrated probabilities; **no training** required for L0 | Apache-2.0 | Closed-form head fit with 100–300 labels (not gradient training); vLLM serve; open-source method |
| https://github.com/TheoLeeCJ/SemIf-OpenJev | Semantic ifs from open models (formerly OpenJev); direct option-logit readout on a 3090 | MIT | Inference + temperature calibration; no model training required; browser WebGPU demo |
| https://github.com/NandhaKishorM/laya | Non-autoregressive System 1 decision engine; open weights; RLCD training against proper scoring rules | Apache-2.0 | Open checkpoints `convaiinnovations/laya*`; fine-tune notebook; Jev-compatible `POST /v1/systemone` HTTP server |
| https://github.com/xingwudao/OpenJev | Independent Jev-inspired System One decision API; mock server + Python/TS SDKs | not confirmed here | Real inference planned; mock only for now |
| https://github.com/razorback16/openjev | Open Jev-compatible System One decision server on DiffusionGemma | not confirmed here | Serving open model in Jev-like shape |
| https://github.com/Hangzhi/diffusion-jev-sglang | Visual Jev-style classification: DiffusionGemma/SGLang server for image labels with Choice | not confirmed here | SGLang serving; training not detailed in search |
| https://github.com/FogMoe/necro | Abandoned Qwen3.5-0.8B LoRA experiments for Jev-like typed judgments | not confirmed here | Datasets, adapters, eval, retrospective; marked abandoned |
| https://github.com/turlockmike/decide-lab | Independent eval / calibration / LoRA of fastino/GLiNER2.5-Decide with Jev comparison harness | not confirmed here | Community eval + LoRA, not official |
| https://github.com/Brandsma/semif-conlang-lora | LoRA fine-tune of a small SemIf/Jev-like model on a made-up grammar | not confirmed here | Experiment |
| https://github.com/mpuig/system-one | Open-source System One decision model; calibrated choice/score/noul on small fine-tuned open models; MLX local; Jev-compatible API | not confirmed here | Fine-tune + audited experiment log |
| https://github.com/Bring-AI/JevNext | Algorithmic layer adding numerical control to Jev-like models | not confirmed here | Post-processing, not training |
| https://github.com/jaredpalmer/kev (HF collection) | Weights: Kev-0.8B / 4B / 9B / 27B | Apache-2.0 | Pretrained adapters + pointer heads; temperature fitted per checkpoint |

Related open model/dataset references seen in community docs:

- `LocalLLaMA/typed-decisions` — Hugging Face dataset used by AnyJev and community benches
- `jaredpalmer/kev-suites` — HF frozen eval suites for Kev
- `convaiinnovations/laya`, `laya-multilingual`, `laya-typed-decisions` — Laya open weights
- `Qwen/Qwen3.5-*`, `Qwen/Qwen3.8-27B`, `google/gemma-4-*` — common open bases used by community reimplementations

### 2.4 Codex / agent integrations

| URL | Role | License | Notes |
| --- | --- | --- | --- |
| https://github.com/typesafe-ai/skills | Official agent skill; install for Claude Code, Codex, skills.sh agents | MIT | SKILL.md points to live docs as source of truth; no training |
| https://github.com/suenot/codex-jev-router | Codex MCP evidence tools; optional Laya selector; historical Jev routing left in tree but **not recommended** | MIT | Default path is deterministic search, no Jev key required |
| https://github.com/miniLV/Jev-Auto-Router | Experimental per-call Codex GPT model/effort routing via TypeSafe Jev + local Responses proxy | Apache-2.0 | Explicitly prototype; real paired eval still incomplete |
| https://github.com/Protocol-Lattice/harness-router | Framework-agnostic tool router; MCP + Codex skill/hook integrations | not confirmed here | Jev for ambiguous choices; deterministic fast path otherwise |
| https://github.com/gargpratyush/jev-router, ruban-24/switchboard, xinyao27/jevonian, yuyang2230/jev-agent-skill, etc. | Community routers / skills / guards for Claude Code, Pi, Codex, MCP | various | Listed in yibie/awesome-jev agent tags |

---

## 3. Training evidence

### 3.1 Official Jev: no public training path

Confirmed from `typesafe-ai` org listing and official SDK/skill repos:

- No repo named like `jev-train`, `jev-model`, `jev-weights`, or architecture release.
- No HF official TypeSafe Jev weights found via public GitHub search.
- `system-one-adapter-python` exists precisely so developers can run a System One-shaped client against OpenAI/Anthropic/Gemini or any OpenAI-compatible endpoint — an official way to **not** use the Jev model while keeping the same call shape.
- TypeSafe docs claims (via awesome lists): customer requests/responses are not used to train models; data-handling and enterprise retention terms still need current confirmation outside GitHub.
- Training of the hosted Jev model itself is not open-sourced. Community write-ups about "Jev architecture unmasked" (cited by Kev: `archerhume.com/posts/jevs-architecture-unmasked`) are third-party reverse-engineering write-ups, not official training code.

**Conclusion:** on GitHub, official TypeSafe is **SDK + API + adapter + agent skill + evals**. There is **no official open training code or open Jev weights**.

### 3.2 Strong community training path: Kev (jaredpalmer/kev)

Best-documented trainable Jev-like stack found.

Evidence from README:

- Architecture: rank-16 LoRA adapter + small pointer head on Qwen3.5/3.8 bases.
- Public weights on Hugging Face: `jaredpalmer/kev-0.8b`, `kev-4b`, `kev-9b`, `kev-27b`.
- Training entrypoint: `python -m kev.train --data train.jsonl --base Qwen/... --init_from jaredpalmer/kev-4b ...`
- Dataset format: JSONL of `state` + `questions` with `label` per question (choice option name, noul true/false, score level index).
- Base training set name: `decision-v7` (10k examples from ten public datasets + generated policy/rule examples). Model cards list each stage.
- Fine-tune cost claim: Kev-4B fine-tune ≈ `$1` on H100 via Modal; example support workload 1,050 records improved 67.7% → 73.6% accuracy and raised automatable share at 5% error budget from 34% → 48%.
- Coding-agent path: `npx skills add jaredpalmer/kev@kev-finetune` runs interview → data prep → training → temperature fit → eval → deploy.
- Serve: `uv run python -m kev.serve --run jaredpalmer/kev-4b --port 8009` exposes `POST /v1/systemone`.
- TypeSafe Python SDK works unchanged against Kev when `base_url` points at the local server (`api_key="local"`).
- License: Apache-2.0; Qwen bases also Apache-2.0; training datasets keep their own licenses (see model cards).
- Important caveat: "No Jev outputs were used for training." Kev is Jev-like, not a distillation of TypeSafe Jev.
- Limitations documented: knowledge questions trail Jev (MMLU 0.74 vs Jev 0.90 for Kev-9B); fine-tuning can hurt some tasks (e.g. date arithmetic); training used ≤384 state tokens while serving accepts up to 65k; option order can still flip answers.

### 3.3 Community path without deep training: simple-jev + RFDT

Evidence from `featherless-ai/simple-jev` README + RFDT README:

- Inference approach: shared prompt + prefill-only scoring of allowed answer-token logits; no decode, no JSON generation.
- API shape inspired by TypeSafe: `POST /v1/classifier` (alias `/v1/systemone`); Choice / Score / Noul.
- Public demo API available without auth (2k-token context, 2 RPS).
- **RFDT** = Really Fancy Decision Training:
  - `prepare.py`: validate records, optional teacher labeling via OpenAI-compatible `/chat/completions`.
  - `train.py`: selected-label cross-entropy on answer-token logits; LoRA or full-weight; `torchrun` multi-GPU.
  - `export.py`: merge LoRA for the HF server.
  - Loss trains only the logits at the last real prompt token, restricted to allowed answer labels.
- Models referenced: Qwen3.5-0.8B, Qwen3.8-27B, Gemma 4 26B-A4B, Laya typed-decisions via `convaiinnovations/laya`.
- License: Apache-2.0.
- README explicitly states Simple Jev does **not** reproduce TypeSafe's model architecture or training.

### 3.4 AnyJev: no gradient training

Evidence from `nokia-applied-research/AnyJev`:

- Claim: "typed decisions, real probabilities, no training."
- L0: zero-label, averages option-order bias over K rotations.
- L1: 100–500 labels → temperature scaling.
- L2: 100–300 labels → closed-form head on hidden states; model weights untouched; head re-estimates mean/scale from unlabeled traffic.
- Serving: `python -m anyjev.truncate ...` then `vllm serve` with embed task; `python -m anyjev.pipeline <model>` one-command path.
- Ships heads for five Qwen3 models in `anyjev-heads/`.
- Authors: Nokia Sunnyvale + Tencent Hunyuan; explicit "Not affiliated with TypeSafe AI or Jev."
- License: Apache-2.0; datasets keep their own licenses (`THIRD_PARTY.md`).
- Published comparison table (vendor/community-reported, not independently rerun here): L2 heads on Qwen3-1.7B/4B/8B/30B/32B vs TypeSafe Jev 0.727 and fine-tuned Laya 0.768 on LocalLLaMA/typed-decisions.

### 3.5 SemIf-OpenJev: open inference + calibration, not Jev training

Evidence from `TheoLeeCJ/SemIf-OpenJev`:

- Reproduces the **interface pattern** with open models; explicitly does not reproduce Jev's undisclosed model or training.
- Direct typed option logits from one forward pass; no answer token, no JSON repair.
- Backends: PyTorch/CUDA, MLX/MPS, llama.cpp CPU GGUF, EXL3 27B bridge, WebGPU browser demo.
- Per-workload temperature calibration (e.g. WANLI ECE 0.208 → 0.069 out of fold).
- Models are external (Qwen, MiniCPM5); weights not bundled; project code MIT.
- Stars ~4.6k; independent of TypeSafe.

### 3.6 Laya: open non-autoregressive System 1 engine with public weights and fine-tune path

Evidence from `NandhaKishorM/laya`:

- Architecture claim: non-autoregressive decision engine trained with RLCD against strictly proper scoring rules; ModernBERT-large / mmBERT bases.
- Open weights on Hugging Face under `convaiinnovations/laya*`.
- Fine-tune notebook: `notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb` (dataset build → train → calibration temps → eval → push Hub). Claimed typed-decisions benchmark: base English 0.362 → fine-tuned 0.766.
- Self-host HTTP server: `laya-serve` implements `POST /v1/systemone` on the same wire protocol as TypeSafe Jev; answer payload schema-identical enough that existing Jev clients can repoint `baseUrl`.
- Differences from hosted Jev documented: option budget vs Jev's 255; score levels need descriptions; `choice`/`score` confidence is 1−normalized entropy, not Jev's formula — thresholds do not transfer directly.
- License: Apache-2.0.
- Related community projects: `mizorewww/laya-mlx` (MLX runtime, ~6.6k stars), `aovestdipaperino/laya-rust`, `yibie/laya-jev-lab`.

### 3.7 Abandoned / weaker training experiments

- `FogMoe/necro`: abandoned Qwen3.5 LoRA experiments for Jev-like judgments; includes datasets, adapters, eval, retrospective. Low stars; useful as a negative result, not a production path.
- `turlockmike/decide-lab`: independent eval + LoRA of GLiNER2.5-Decide with Jev comparison harness.
- `Brandsma/semif-conlang-lora`: small SemIf/Jev-like LoRA on constructed grammar.
- `mpuig/system-one`: open-source System One model on Apple Silicon with MLX; "Jev-compatible API"; low stars; experimental.

### 3.8 Dataset / eval signals useful for training Jev-like models

| Artifact | Source | Use |
| --- | --- | --- |
| `decision-v7` / transfer suites | jaredpalmer/kev + HF `jaredpalmer/kev-suites` | Public decision training data + locked transfer evals |
| `LocalLLaMA/typed-decisions` | Hugging Face | Community typed-decisions eval/training dataset |
| TypeSafe public evals | `evals.typesafe.ai` | Public comparison cases (SemIf/Kev cite these) |
| Kev JSONL format | jaredpalmer/kev README | Ready-made fine-tune data schema |
| RFDT JSONL format | simple-jev RFDT | Ready-made fine-tune data schema for answer-token training |

---

## 4. Codex / API hints

### 4.1 Official path (hosted Jev)

1. Get a TypeSafe API key from the TypeSafe console (outside GitHub).
2. Install official skill for agents:
   - Claude Code: `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`
   - Other agents: `npx skills add typesafe-ai/skills --skill typesafe-ai`
3. Or call the HTTP API directly: `POST https://api.typesafe.ai/v1/systemone` with `state` + `questions`.
4. Python quickstart from official SDK:
   ```python
   from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
   with TypeSafeClient() as client:
       response = client.system_one(state=..., questions={...})
   ```
5. Agent-skill SKILL.md (`typesafe-ai/skills`) tells agents to read live docs (`docs.typesafe.ai/llms.txt`, `.md` pages) as source of truth and to design Choice/Score/Noul questions with code owning thresholds and side effects.
6. Anil-matcha list records official agent-skill docs at `https://docs.typesafe.ai/agent-skill` covering Claude Code, Codex, and other coding agents.

### 4.2 Self-hosted / Jev-compatible API path (for Codex or any agent)

Several open stacks expose a **Jev-shaped System One HTTP API**:

| Stack | Serve entrypoint | License | Trainable? |
| --- | --- | --- | --- |
| Kev | `python -m kev.serve --run jaredpalmer/kev-4b --port 8009` → `POST /v1/systemone` | Apache-2.0 | Yes (`kev.train`) |
| Laya | `laya-serve` → `POST /v1/systemone` | Apache-2.0 | Yes (notebook + open weights) |
| Simple Jev | `python hf-server/hf_server.py --model ...` → `POST /v1/classifier` (alias `/v1/systemone`) | Apache-2.0 | Yes (RFDT) |
| AnyJev | `python -m anyjev.pipeline <model>` / vLLM embed server | Apache-2.0 | Closed-form head only |
| system-one-adapter-python | Python client that reimplements `system_one` on OpenAI/Anthropic/Gemini | MIT | No (uses other LLMs) |

Point the TypeSafe Python SDK at a local server:

```python
client = TypeSafeClient(api_key="local", base_url="http://127.0.0.1:8009", model="kev-latest")
```

This is the cleanest way to put a **Jev-like** model behind an API that Codex/agents already know how to call, without TypeSafe credentials.

### 4.3 Codex-specific community integrations

| Project | What it does | Status |
| --- | --- | --- |
| `typesafe-ai/skills` | Official skill install path for Codex and other agents | Active, MIT |
| `suenot/codex-jev-router` | Codex MCP tools for workspace evidence search; optional Laya selector | Active; **author no longer recommends** Jev subagent routing after mixed cost results |
| `miniLV/Jev-Auto-Router` | Per-call Codex Responses routing: Jev Choice picks (model, reasoning.effort); local proxy; Router Compass audit | Prototype; Apache-2.0; README warns not production-ready |
| `Protocol-Lattice/harness-router` | Tool router with Codex skill/hook + MCP | Community |
| Awesome-list Codex tags | `suenot/codex-jev-router`, `miniLV/Jev-Auto-Router`, `thruwire/foreman`, `leonaaardob/fast-dev-compaction`, `yikangy873-gif/jev-desktop`, `wy-coliney/jev-browser-use` | Discovery index |

### 4.4 Path summary for "put a Jev or Jev-like model behind an API for Codex"

**Option A — Hosted TypeSafe Jev (official)**  
Need TypeSafe account + API key. Use official SDK or skill. No local training. Cost/limits from TypeSafe docs (dynamic; re-verify). Best when you want the real Jev calibration/quality claims.

**Option B — Self-host Kev (best trainable Jev-like)**  
Apache-2.0 weights + training code + TypeSystem One-compatible server. Fine-tune on your domain labels; deploy via Modal or local GPU; point Codex/agents at `/v1/systemone`. No TypeSafe credentials required.

**Option C — Self-host Laya**  
Open non-autoregressive System 1 engine with Jev-compatible HTTP server. Faster local latency claims (tens of ms on GPU). Fine-tune notebook exists. Confidence formulas differ from Jev; re-calibrate thresholds.

**Option D — Simple Jev + RFDT**  
Use any open model as a typed decision endpoint via logits scoring; optionally fine-tune with RFDT. Good for "no new model family, just a decision layer on existing weights."

**Option E — AnyJev / SemIf**  
No or minimal training; good for rapid typed-decision prototypes and calibration studies on open LLMs.

---

## 5. Gaps and risks

1. **No official open Jev weights or training code.** GitHub cannot answer "how TypeSafe trained Jev" with official materials. Architecture notes circulating publicly are third-party reverse-engineering.
2. **Official org has no model-card repo for Jev.** Version/pricing/limits live in TypeSafe docs/console, not GitHub; they can change without a GitHub commit.
3. **Many awesome lists are discovery indexes, not verified quality.** Stars and same-day bulk repos can coexist with thin code. `yibie/awesome-jev` explicitly warns about this.
4. **License of the Jev model itself is not a GitHub LICENSE.** Hosted model terms sit in TypeSafe ToS / docs, not in an open weights license. Community reimplementations are separately licensed (mostly MIT/Apache-2.0).
5. **Open training data licenses vary.** Kev model cards and AnyJev `THIRD_PARTY.md` note dataset licenses; training on third-party data for redistribution needs review.
6. **Confidence formulas differ across stacks.** Laya documents that its `choice`/`score` confidence is 1−normalized entropy, not Jev's `(n·p_max−1)/(n−1)`. Thresholds do not transfer blindly.
7. **Some Codex routing projects report mixed or negative cost results.** `suenot/codex-jev-router` found Jev-selected children more expensive than a single high-effort agent in its benchmark; the author pivoted away from recommending Jev routing.
8. **Rate limits on unauthenticated GitHub Search** interrupted several query variants (`Jev model training code`, `kev Jev-like Qwen train`, `Visual Jev github`, `Jev codex integration` returned partial/empty). Coverage improved via alternative queries and direct README fetches; some niche Visual Jev repos remain thin in the search record.
9. **"Visual Jev" is not an official TypeSafe product name found on GitHub.** Community projects use Jev-style visual classification (e.g. DiffusionGemma servers, vision validation experiments in simple-jev) rather than a single official Visual Jev repo.
10. **Private repos / tokens not accessed** per constraint. Absence of a public official training repo is evidence about public GitHub, not proof that TypeSafe has no internal training code.

---

## 6. Stop reason

Stop condition met:

- Official vs community artifact map is clear.
- Training feasibility is clear: **no official open Jev training path**; multiple community paths exist (Kev, Laya, simple-jev RFDT, AnyJev heads, SemIf calibration).
- License constraints are clear at the repo level (official SDKs MIT; most community training stacks Apache-2.0 or MIT; hosted Jev model terms are not a GitHub open-weights license).
- Path to put a Jev or Jev-like model behind an API for Codex is documented: official hosted TypeSystem skill/API, or self-hosted Kev/Laya/Simple-Jev `/v1/systemone` servers that TypeSafe SDK clients and agent tools can call unchanged.

Residual risks: hosted Jev model terms/pricing not on GitHub; performance claims in community READMEs are self-reported and not independently reproduced in this pass; rate-limited search left some niche Visual Jev / open weights repos unverified.

---

## 7. Query coverage note

Scripts run via `fast_search.py --provider github` with these query variants (subset hit rate limits; all listed):

1. TypeSafe AI Jev github — ok
2. typesafe-ai jev — ok
3. awesome-jev typesafe — ok
4. Jev model training code — partial (rate limit)
5. Jev fine-tune LoRA — ok
6. simple-jev — ok
7. AnyJev typed decisions — ok
8. kev Jev-like Qwen train — partial; recovered via `kev jaredpalmer`
9. Visual Jev github — partial; recovered via `Visual Jev model`
10. Jev SDK agent tool — ok
11. Jev codex integration — unavailable (403); recovered via awesome-list Codex tags + `codex-jev-router`
12. Jev open weights license — not re-run after rate limit; inferred from LICENSE badges on fetched READMEs
13. how to train a Jev style model — covered by kev / RFDT / Laya / AnyJev READMEs
14. Jev decision model API OpenAI compatible — covered by system-one-adapter-python + kev + simple-jev
15. Jev train dataset — covered by decision-v7 / LocalLLaMA/typed-decisions / RFDT examples
16. jaredpalmer kev Qwen — rate-limited; covered by kev README
17. typesafe-ai organization — ok (org repo list)
18. SemIf-OpenJev / SemIf OpenJev — ok
19. LocalLLaMA typed-decisions / Laya typed decisions / OpenJev System One — ok

READMEs fetched via WebFetch: `yibie/awesome-jev`, `Anil-matcha/awesome-jev-by-typesafe`, `featherless-ai/simple-jev`, `nokia-applied-research/AnyJev`, `typesafe-ai/typesafe-sdk-python`, `typesafe-ai/system-one-adapter-python`, `typesafe-ai/skills`, `typesafe-ai` org repos, `jaredpalmer/kev`, `TheoLeeCJ/SemIf-OpenJev`, `suenot/codex-jev-router`, `NandhaKishorM/laya`, `miniLV/Jev-Auto-Router`, plus raw `yibie/awesome-jev` README and RFDT README.
