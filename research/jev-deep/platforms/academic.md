# Academic Platform Report: TypeSafe AI Jev Model

platform_id=academic, tier=1, scene=academic, depth=deep  
Research goal: how TypeSafe AI's Jev model is made and trained; training data / architecture / hyperparameters; scientific evidence.  
Search script + WebFetch on arXiv abstracts and HTML full text. Report written 2026 (session context).

---

## 1. Identity confirmation

| Claim | Status | Evidence |
| --- | --- | --- |
| Jev is TypeSafe AI's System One decision model | Confirmed | Multiple papers + vendor blog |
| Answers natural-language questions with typed choices, binary judgments, scores/probabilities | Confirmed | Choice / Noul / Score interfaces |
| Released 2026-09-15, early access | Confirmed | TypeSafe blog + Jev in the Wild |
| Hosted commercial model, version jev-1.13.0 as of 2026-09-20 | Confirmed | Just Ask Jev reproducibility |
| Training method named RLCD (reinforcement learning for calibrated decisions) | Confirmed | Just Ask Jev + TypeSafe blog |
| Official paper-level training recipe (data, architecture, hyperparameters) | **Not found** | See Gaps |

**What Jev is, in short.** Jev is a non-generative "System One" model: unstructured state in, type-safe structured decisions out. A request holds a `state` (string or JSON) and a list of typed questions. Answers are calibrated probabilities over declared options, not free text. Interfaces:

- **Choice**: categorical distribution + argmax over options (vendor: up to 255 options; high cardinality uses a 2-stage score-then-choose path)
- **Noul**: binary judgment, returns P(yes)
- **Score**: ordinal levels, returns level distribution / expected level

One call can carry many independent questions about the same state. Papers describe it as a "typed classifier that returns probabilities over permitted answers without generating text."

**Naming.** "System One" from Kahneman's Thinking Fast and Slow; "Jev" from William Stanley Jevons (vendor FAQ). Founder Diogo Almeida states prior OpenAI work on instruction-following methods (related to ChatGPT); TypeSafe was in stealth ~2 years before release.

---

## 2. Key papers table

| # | Title | arXiv id | URL | Authors (if available) | What it establishes |
| --- | --- | --- | --- | --- | --- |
| 1 | Visual Jev: Accurate and Efficient Decisions from Shared Visual Context | 2609.25845 | https://arxiv.org/abs/2609.25845 | Guanxu Yu, Yuhang Yao (Independent Research / CMU alumnus) | **Independent, fully reproducible** Visual Jev training recipe: Qwen3-VL + LoRA answer SFT + LM-head probability readout. Full hyperparameters in Appendix C. |
| 2 | Just Ask Jev: Reinforcement Learning for Calibrated Decisions as a Zero-Shot Detector of AI Alignment Failures | 2609.29429 | https://arxiv.org/abs/2609.29429 | Ruoqi Guo, Yi Liu, Gelei Deng, Yuekang Li, Lida Zhao, Yutao Wu, Simin Chen, Ying Zhang, Leo Yu Zhang | Confirms Jev = TypeSafe's RLCD model; documents API request schema; uses jev-1.13.0; zero-shot alignment detection; cites TypeSafe docs (docs.typesafe.ai) for RLCD definition, not a training paper. |
| 3 | Jev in the Wild: A Data-Driven Analysis of the Jev Model's Functionality, Applications and Ecosystem | 2609.30216 | https://arxiv.org/abs/2609.30216 | Guoming Ling, Muen Xue, Zijian Ye | Identity + ecosystem: 2,170 GitHub projects as of 2026-09-22; release date 2026-09-15; Choice 81% / Noul 72% / Score 45% interface adoption; decision-purpose taxonomy. |
| 4 | Decide, Don't Generate: Competitive Dimensional ABSA with Jev's Typed Decisions | 2609.35293 | https://arxiv.org/abs/2609.35293 | Yiqun Zhang, Peidong Wang, Zihan Wang, Shi Feng | Official Jev used as a **frozen** model (no backbone tuning); 488 CPU-fitted coefficients; rubric scores + label probabilities + yes/no; SemEval-2026 ABSA results. |
| 5 | Do System One Decisions Add Up? A Study of Probabilistic Coherence | 2609.33971 | https://arxiv.org/abs/2609.33971 | Saman Sarker Joy | Jev + English Laya checkpoint probability coherence limits: mean category-level TV 0.219–0.349 for Jev; reconstruction can drop accuracy by ~22.9 points on CLINC150. |
| 6 | Laya as a Typed Probabilistic Assessor: An Independent Reproduction and a Preregistered Study... | 2609.33843 | https://arxiv.org/abs/2609.33843 | Gowthamkumar Nandakishore (no TypeSafe affiliation) | Related TypeSafe System One model **Laya**: shipped checkpoint is 421M-param ModernBERT-large, typed choice/noul/score; accuracy 0.767 reproduced; **under-confident** (ECE 0.214). Architecture clue for the System One family, not for Jev itself. |
| 7 | Decision Hijacking: Prompt Injection Attacks on Jev's Typed Probabilistic Decisions | 2609.28613 | https://arxiv.org/abs/2609.28613 | Tiantong Wu, Wei Yang Bryan Lim | Security: schema outputs change but do not eliminate prompt-injection risk; adaptive attacks raise success 1.8%→3.5%. |
| 8 | JEV vs. LLMs as Rubric Judges: Cheaper, Faster, and Wrong in the Same Places | 2609.29769 | https://arxiv.org/abs/2609.29769 | Delip Rao, Chris Callison-Burch | Jev as rubric judge: accuracy often comparable to flash-tier LLM judges; 29–325x cheaper; correlated errors limit cascade gains. |
| 9 | Jev Matches 7B Language Models for Speech-Neuroprosthesis Rescoring | 2609.33538 | https://arxiv.org/abs/2609.33538 | Gabriele Cinà | Application: typed rescoring of candidate sentences; WER competitive with OPT-6.7B / Qwen2.5-7B; $0.07/1k sentences, no GPU; hosted latency 62 ms provider-side. |
| 10 | Replacing Large Language Models with Jev Decision Models for Low-Latency Edge Service Orchestration | 2609.22753 | https://arxiv.org/abs/2609.22753 | Delong Li, Xu Wang, Haochen Gong, Rui Lang, Guangsheng Yu | Application: edge admission; median decision latency −22.7% to −64.5% vs fastest LLM; API fees per correct decision lower on 4-field intent inputs. |
| 11 | Jev-Mobile: Jev as an Executor for Mobile GUI Agents | 2609.30186 | https://arxiv.org/abs/2609.30186 | (see arXiv) | Application: low-frequency VLM planning + high-frequency Jev execution for mobile GUI agents. |
| 12 | this-that-model-1.0: A typed decision model that decides in 30 ms, for a millionth of a cent | 2609.23886 | https://arxiv.org/abs/2609.23886 | Zehua Cheng, Wei Dai, Jiahao Sun | **Open-source competitor** for typed decision models: 2B params, hidden-state readout restricted to declared options; compares against hosted Jev (accuracy 0.765 / Brier 0.133 on third-party cohort). Training-transfer limits documented. |
| 13 | Calibrated Decision Models for Autonomous Penetration-Testing Harnesses: JEV and Laya as System One Decision Layers... | 2609.28940 | https://arxiv.org/abs/2609.28940 | (see arXiv) | Application: System One decision layers (JEV + Laya) for pentest agent verification/severity. |
| 14 | Jev for Scientific Decisions: Evaluating Semantic Choices and Their Consequences | 2609.24965 | https://arxiv.org/abs/2609.24965 | B. Deng, S. Fan, H. Zhang, X. Xie (cited in Jev in the Wild) | Application: semantic choice harness for scientific workflows; Jev as semantic decision component. |
| 15 | Same Scores, Different Decisions: Evaluating JEV and Language Models for Legal Document Understanding | 2609.27678 | https://arxiv.org/abs/2609.27678 | (see arXiv) | Application: ContractNLI multi-judgment comparison vs nine LMs; cost/time/repeat-stability. |
| 16 | JEV as a Judge for Agent Trace Security... | 2609.34862 | https://arxiv.org/abs/2609.34862 | (see arXiv) | Application: typed decision model for retrospective agent-trace risk classification vs generative judges (5,219 trajectories). |
| 17 | Introducing System One Models & Jev (vendor blog) | — | https://typesafe.ai/blog/introducing-system-one-models-and-jev | Diogo Almeida, TypeSafe | Official announcement: RLCD, new architecture + parallel sampler, 70–500 ms, $0.042/MTok input, output free; FAQ lists training-data question but **does not disclose** the data recipe in the public page body retrieved. |
| 18 | TypeSafe documentation: Jev and the System One API | — | https://docs.typesafe.ai | TypeSafe AI | Cited by Just Ask Jev as the source for RLCD / API / request format / known weaknesses. Not an arXiv training paper. |

---

## 3. Training / making evidence

### 3.1 Official Jev (TypeSafe) — training is **opaque at paper level**

**What is documented (vendor + papers):**

- Method name: **RLCD = reinforcement learning for calibrated decisions**. Calibrated means: among decisions assigned probability p, a fraction close to p is correct (Just Ask Jev §2, citing TypeSafe AI 2026).
- Explicit distinction: this RLCD is **not** "reinforcement learning from contrastive distillation" (Yang et al., arXiv 2307.12950), which shares the acronym (Just Ask Jev footnote).
- Vendor claim: "new model architecture, parallel sampler for maximum efficiency, and training method we call Reinforcement Learning for Calibrated Decisions (RLCD)" (TypeSafe blog).
- Output objective framing: optimize for calibrated decisions with "epistemically honest probabilities," contrasted with RLHF / RLVR.
- Sampling: parallel generation of all typed outputs in one query (vendor).
- Request format (from Just Ask Jev appendix, citing TypeSafe docs): `{state, questions}` where questions map id → `{type, instructions[, criteria]}`. Noul → P(yes); Choice → argmax + distribution + confidence; Score → expected level + level distribution. Multiple questions share one call.
- Known weaknesses listed by developer docs (as reported in Just Ask Jev): **indirect meaning** and **adversarial content**.
- Version pinning: all Just Ask Jev runs resolved to **jev-1.13.0**; API accepts versioned IDs; vendor states no retention period.

**What is NOT documented in arXiv papers or the public blog body retrieved:**

| Item | Status |
| --- | --- |
| Training corpus size / sources / labeling | Not disclosed ("Where does our training data come from?" is a FAQ heading; answer body not present in retrieved page) |
| Base backbone architecture / parameter count for Jev | Not disclosed for Jev |
| RL algorithm details (reward design, offline vs online, preference data, etc.) | Not disclosed beyond the name RLCD |
| Frozen vs finetuned internal design for official Jev | Not disclosed; external papers treat it as a hosted black box |
| Probability readout mechanism for official Jev | Not disclosed; independent Visual Jev uses LM-head candidate logits (see below) |
| Hyperparameters (LR, batch, steps, optimizer) | Not disclosed |
| Training compute / hardware | Not disclosed |

**Conclusion on official training:** Scientific evidence confirms *that* Jev is trained with RLCD and *what* the API returns; it does **not** document a reproducible training recipe. Independent papers consistently treat official Jev as a commercial hosted model.

### 3.2 Independent / related training evidence (usable as "how one could train such a model")

#### A. Visual Jev (arXiv 2609.25845) — full independent recipe

This is the strongest paper-level training evidence for a Jev-*style* decision model.

| Component | Fact |
| --- | --- |
| Backbone | Qwen3-VL-4B-Instruct (bfloat16); 8B comparison uses Qwen3-VL-8B |
| Vision tower | **Frozen** |
| Adaptation | **LoRA on language tower** attention + MLP projections: r=16, α=32, dropout 0.05 |
| Training objective | **Answer SFT**: ordinary next-token cross-entropy on full vocabulary at a fixed `Answer:` readout position |
| Training data | 30,416 GQA Choice items + 9,000 SNLI-VE Claim items |
| Option handling | Choice examples vary K from 2 to 8; option order shuffled; distractors from same-type answers |
| Budget | 3,000 updates; batch size 8; gradient checkpointing |
| Optimizer | AdamW; cosine schedule; 100 warm-up steps |
| Learning rate | 1e-4 for LoRA; 1e-3 for diagnostic heads |
| Grad clipping | 1.0 |
| Visual-token budget | 196 (448×448) |
| Probability readout | Softmax over **candidate option-letter token logits** from the existing LM head, normalized only over valid options |
| Typed-head controls | Matched Choice (16-slot) / Claim (3-way) heads in float32 (largest setup 33.1M trainable params) — **no consistent accuracy advantage** over LM-head readout |
| Evidence-sufficiency head | Trained on grey-fill occlusion; detects missing evidence well (AUROC ~0.969) but does **not** improve decision quality |
| Hardware / time | 1× NVIDIA RTX 5090 32 GB; PyTorch 2.14 CUDA 13.0; ~45 min per variant; peak memory 14.4 GiB |
| Result | Macro accuracy 0.706 → 0.761 (4B answer SFT); gains concentrated on trained families (GQA, SNLI-VE); held-out TextVQA/TallyQA barely change |
| Serving | Shared visual prefix + batched isolated question suffixes; N=32: 8.9× faster warm amortized time vs independent serial; typed heads not required |

**Design conclusion from Visual Jev:** adapt the backbone for quality; keep LM-head candidate-token readout; share prefix + batch suffixes for efficiency. Do not add specialized decision heads unless data/budget forces it.

#### B. Related TypeSafe System One model: Laya (arXiv 2609.33843)

- Shipped **Laya Typed-Decisions checkpoint**: **421M-parameter ModernBERT-large** assessor answering typed choice/noul/score questions over workflow state.
- Official card accuracy reproduced: 0.767 vs 0.766.
- Calibration: uniformly **under-confident** (signed confidence-accuracy gap −0.214; ECE 0.214); a disjoint temperature T=0.469 cuts held-out ECE 0.204 → 0.037.
- Author has no affiliation with TypeSafe or the dataset publisher.
- **Inference for Jev:** Laya is a different checkpoint in the same product family; ModernBERT architecture is evidence about the *family*, not proof of Jev's backbone.

#### C. Open-source typed decision model: this-that-model-1.0 (arXiv 2609.23886)

- 2B-parameter typed decision model; answer read from **hidden state at a designated position**, restricted to caller-declared option set; no text generation; all questions in one forward pass.
- 30.9 ms on one laptop GPU; 0 output tokens.
- On a third-party cohort of 68 questions: accuracy 0.941 / Brier 0.042 vs hosted Jev 0.765 / 0.133 on same items (paper's comparison; not an official Jev eval).
- Documented failure mode: multi-step arithmetic (0.560 vs ~0.98–1.00 for hosted models); second training round improved 5 target families, transferred to 0 of 13 others.
- Open-sourced: https://huggingface.co/flock-io/this-that-model-1.0
- **Useful as a training blueprint** for non-generative typed decision models when official TypeSafe data/recipe is unavailable.

#### D. How one could train a Jev-like model (synthesis of paper evidence)

1. **先定接口约束**: state + typed questions (Noul / Choice / Score); outputs are distributions over declared options, never free strings.
2. **Start from a strong instruction-tuned LM** (text) or **VLM** (vision). Independent work uses Qwen3-VL; related open work uses a 2B encoder-style decision model; related TypeSafe Laya is ModernBERT-large 421M.
3. **Supervise decisions, not generation**:
   - Visual Jev: answer SFT on option-letter tokens at a fixed readout position.
   - Alternative control: typed classification heads with CE over slots (Visual Jev found no gain vs LM-head at tested budget).
4. **Train on task-family data you care about** (Visual Jev: GQA + SNLI-VE; gains do not transfer broadly to held-out families).
5. **Read probabilities from a fixed readout**: LM-head candidate logits softmax-normalized over options (Visual Jev), or hidden-state restricted to option set (this-that-model).
6. **If you want "calibrated decisions" like vendor RLCD**: public papers do not specify the RL reward/data; closest public ingredients are (a) answer-supervised SFT + post-hoc calibration, (b) temperature/isotonic calibration on held-out data (Laya paper), (c) threshold fitting on 10 labeled items (Just Ask Jev recipe). Full RLCD reproduction is **not possible from public academic sources**.
7. **Budget reference (Visual Jev)**: ~39k decision examples, 3k LoRA updates, one RTX 5090, under an hour.

---

## 4. Probability readout and calibration evidence

| Finding | Source | Detail |
| --- | --- | --- |
| Official Jev returns calibrated probabilities over permitted answers | Just Ask Jev, JEV vs LLMs, ABSA | Typed classifier, non-generative |
| Independent Visual Jev uses LM-head candidate logits, not typed heads | 2609.25845 | Matched typed-head control: no consistent accuracy advantage |
| Jev probabilities rank well but can miscalibrate as thresholds | Just Ask Jev | Median ECE 0.168 vs null 0.074; threshold fitting on 10 labels lifts F1 0.706→0.793 |
| Label-free prior-shift correction fails for Jev | Just Ask Jev | EM prior-shift correction does not help; selective prediction by confidence works |
| Probabilistic coherence fails when decisions are decomposed | 2609.33971 | Jev TV 0.219–0.349; reconstruction can hurt accuracy significantly |
| Laya (related) is under-confident | 2609.33843 | Direction opposite of vendor card framing; temperature calibration helps |
| Prompt injection shifts action probabilities | 2609.28613 | Rarely selects attacker target without adaptive optimization; override markers help |

---

## 5. Notable applications (paper-level)

| Domain | Paper | Role of Jev |
| --- | --- | --- |
| Vision decisions (many questions / image) | Visual Jev 2609.25845 | Shared prefix + batched typed questions |
| Speech neuroprosthesis rescoring | 2609.33538 | Replace 7B LM rescoring with typed probability rescoring |
| Edge service orchestration / 6G | 2609.22753, 2609.23136 | Low-latency intent parsing and admission |
| Mobile GUI agents | Jev-Mobile 2609.30186 | High-frequency executor under slow VLM planner |
| ABSA / sentiment | 2609.35293 | Frozen typed decisions + CPU coefficient calibration |
| Alignment failure detection | Just Ask Jev 2609.29429 | Zero-shot multi-question detector; 63× cheaper than LLM judges |
| Rubric judging | 2609.29769 | Cheap first-stage judge; correlated errors with LLMs |
| Agent-trace security judging | 2609.34862 | Retrospective typed risk classification |
| Prompt-injection security | 2609.28613 | Attack surface of schema-defined decisions |
| Scientific semantic choices | 2609.24965 | Semantic decision harness before arithmetic |
| Legal ContractNLI | 2609.27678 | Multi-judgment cost/time comparison vs LMs |
| Pentest harness verification | 2609.28940 | System One layer for finding confirmation/severity |
| Ecosystem / routing / agents | Jev in the Wild 2609.30216 | 2,170 public projects; attribute judgment most common purpose; stars concentrated on routing/interface agents |

---

## 6. Gaps and limitations

1. **Official Jev training recipe is not in public academic literature.** No arXiv paper from TypeSafe describing data, architecture, RL algorithm details, or hyperparameters was found. Vendor blog + docs name RLCD and describe API/behavior only.
2. **FAQ "Where does our training data come from?"** exists on the vendor blog page structure but the retrieved page body did not include a concrete data disclosure.
3. **Backbone identity of official Jev is unknown.** Papers treat it as black-box API; Laya's ModernBERT and Visual Jev's Qwen-VL are related/independent, not official Jev architecture.
4. **RLCD algorithm details are missing publicly.** Academic papers define the *goal* (calibrated decisions) but not reward construction, data mix, or training loop.
5. **Calibration is not uniformly reliable** in independent studies (threshold ECE, coherence under decomposition, Laya underconfidence).
6. **Transfer is limited** for decision post-training concentrated on few task families (Visual Jev held-out tasks; this-that-model second-round transfer 0/13).
7. **Security:** typed outputs reduce but do not remove prompt-injection risk (Decision Hijacking).
8. **Most papers are September 2026 preprints** on a product released 2026-09-15; many are application evaluations, not training papers. OpenAlex endpoint was down (HTTP 503) during search; Crossref returned no Jev-specific academic training paper.
9. **Comparison caveats:** this-that-model vs Jev numbers come from a third-party cohort and a paper with an open-source release interest; vendor workflow evals use LLM-average references with acknowledged bias (blog nuances).

---

## 7. Source coverage

### Search queries run (arXiv via fast_search.py, limit 8 each)

- Jev TypeSafe decision model training
- Jev System One typed decisions
- Visual Jev training post-training
- TypeSafe AI Jev paper
- Jev model architecture probabilities rubric
- Jev in the wild ecosystem analysis
- Jev data recipe decision model
- Jev paper method experiment TypeSafe
- Jev vs language model decision
- reinforcement learning calibrated decisions RLCD Jev
- Jev low-latency decision API
- Jev judge agent security
- System One decision model TypeSafe AI foundation
- Laya decision model TypeSafe
- Jev decision model data architecture
- do system one decisions add up probabilistic coherence Jev
- Jev speech neuroprosthesis rescoring decision
- Jev edge service orchestration low latency
- Jev scientific decisions semantic choices
- Jev as judge agent trace security
- Jev legal document ContractNLI
- Jev-Mobile GUI agents executor
- Jev model card TypeSafe documentation
- Laya typed decisions ModernBERT calibration
- reinforcement learning for calibrated decisions
- TypeSafe AI decision model Jev architecture
- Jev paper method experiment
- Jev vs language model decision
- Jev edge service orchestration
- Jev low-latency decision API
- Jev judge agent security

### Other providers

- openalex: Jev TypeSafe decision model → HTTP 503, retry-after 60; no results
- crossref: Jev TypeSafe decision model training → executed in same call chain; no Jev-specific academic training paper returned in combined output

### Full-text / abstract fetches (WebFetch)

- arXiv abs+HTML: 2609.29429, 2609.25845, 2609.30216, 2609.35293, 2609.33843, 2609.33971, 2609.28613, 2609.33538, 2609.22753, 2609.23886, 2609.29769
- Vendor blog: https://typesafe.ai/blog/introducing-system-one-models-and-jev

### Evidence level

- Discovery metadata: most arXiv search hits
- Paper body / abstract details: Visual Jev full HTML (training + appendix), Just Ask Jev full HTML (API + RLCD framing), Jev in the Wild full HTML (ecosystem + apps), vendor blog (product claims)
- Not obtained: official TypeSafe training paper (does not appear to exist on arXiv)

---

## 8. Stop reason

**stop_reason:** Paper-level evidence reached for (1) what Jev is, (2) how related/independent models are made and trained (Visual Jev full recipe; Laya architecture clue; this-that-model open blueprint), (3) whether official Jev training is documented — **it is not** beyond the RLCD method name and API/behavior docs, (4) notable applications (multiple independent papers).

**Official training recipe remains opaque.** Public academic sources do not disclose Jev's training data, backbone, RLCD algorithm details, or hyperparameters. Anyone seeking to train a Jev-like system should follow Visual Jev / this-type-model style recipes for typed decision heads + probability readout, and treat vendor RLCD as a proprietary training method.

---

## 9. Top evidence lines (for parent agent)

1. **2609.29429 Just Ask Jev**: "Jev, a model trained with reinforcement learning for calibrated decisions (RLCD)" — "Jev, TypeSafe's RLCD model, answers many binary (Noul), categorical (Choice), and ordinal (Score) questions about one input, the state, in a single call." Cites TypeSafe docs, not a training paper. Version jev-1.13.0.
2. **2609.25845 Visual Jev**: Independent full recipe — Qwen3-VL-4B, frozen vision tower, LoRA r=16 α=32 on language tower, answer SFT on 30,416 GQA + 9,000 SNLI-VE items, 3k updates, batch 8, AdamW cosine, LR 1e-4; readout = softmax over candidate option-letter LM-head logits; typed heads not needed.
3. **2609.35293 ABSA**: Official Jev used as frozen model; rubric scores + label probabilities + yes/no; 488 coefficients fitted on CPU; no backbone tuning.
4. **2609.33843 Laya**: Related TypeSafe System One checkpoint is 421M ModernBERT-large; under-confident (ECE 0.214); accuracy 0.767 reproduced — architecture clue for the family, not official Jev.
5. **TypeSafe blog (2026-09-15)**: RLCD + new architecture + parallel sampler; 70–500 ms; $0.042/MTok input; training-data FAQ present without public data recipe in retrieved body.

---

*Report end.*
