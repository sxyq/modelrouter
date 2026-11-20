# Terminal-Bench正式2.0与历史2.1结果

## 当前结果 · 2026-11-20 08:21–08:33 台北

三批由 A6000 现行分析器连续导出；各批报告、指标和 `trials/` 来自对应导出。下方较早时刻的记录保留为历史。

| 批次 | 已结束／计划 | 有效 Reward 1／0 | 缺有效评分 | 评分依赖故障 | 运行／未首跑 | 已报 API Token | 模型＋教师已知参考费 USD | 费用未知请求 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Model-only](rq1/terminal-bench-2.0/20261112-v9-model-only/review.md) | 2082／2136 | 373／210 | 1467 | 32 | 1／53 | 204184371 | 41.65840893 | 2224 |
| [Seed43 联合](rq1/terminal-bench-2.0/20261112-v9-joint-paired/review.md) | 261／957 | 99／57 | 105 | 0 | 0／696 | 143404387 | 15.32542777 | 196 |
| [Seed42 历史](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md) | 1513／1513 | 391／422 | 648 | 52 | 0／0 | 444893675 | 50.62987761 | 1408 |

有效 1、有效 0、缺有效评分、评分依赖故障四列合计为本次快照的已结束位置。Token 和参考费累计已结束 Trial；每题最后一次独立运行见各批 `metrics/per_episode.csv` 的 `latest_trial_*`。供应商实收、Router、工具和共享资源美元费用仍缺项。一个策略完整运行全部 89 题的 Token 尚缺用量齐全的整轮记录。

Model-only已覆盖87／89题；85题的24组均有结束记录，单策略最多48/89题有有效Reward。八个Laya/Kev版本和教师开关均含Low／High／Max。联合已结束位置均为固定模型，696个动态Router位置未首跑。原排除的Model-only48、联合22个位置保留在分母。

GLM新凭据更新后请求已HTTP200；将A6000现存Luna账号绑定切到配置中的`luna-colink`后，完整Episode生成及教师调用均HTTP200。`winning-avg-corewars`三种Kev原始教师开关组取得官方1／0／0，训练Kev OFF Low另取得官方1；同题结果留在逐题Trial。旧Codegoai 401与精确GLM模型404保留原记录，不改模型名或转发。

### `winning-avg-corewars`：Luna账号恢复后的完整Episode

| 策略 | 官方Reward | 已报Token | 已知参考费USD | Luna执行请求 | Luna教师请求／消费决策 |
|---|---:|---:|---:|---:|---:|
| Kev原始 ON Low | 0 | 34,023 | 0.00222230 | 8/8 HTTP 200，Effort匹配 | 1／4，HTTP 200、Low匹配 |
| Kev原始 ON High | 0 | 135,056 | 0.00909432 | 14/14 HTTP 200，Effort匹配 | 3／8，HTTP 200、Low匹配 |
| Kev原始 ON Max | 1 | 146,692 | 0.01424792 | 12/12 HTTP 200，Effort匹配 | 3／4，HTTP 200、Low匹配 |

三题独立Trial共315,771个已报Token、$0.02556454已知参考费；有效结果1通过／2失败，全部无额外请求重试。Max完成任务且该单题开教师配置成功，Low与High虽正常执行仍未通过；单题结果不代表全矩阵方法差异。训练Kev OFF Low的同题Episode仍在运行。

旧账户故障接续新增一个已观察格式：Colink 403 的 `insufficient balance` 文本此前被原恢复入口漏选，现与原有 `INSUFFICIENT_BALANCE`／`SUBSCRIPTION_NOT_FOUND` 一起识别。仍由原 `--restored-provider` 按同题、策略和 Seed 创建独立恢复 Trial，已有有效官方评分不再运行。

Provider每请求最多额外100次同参数重试已部署，并受原任务期限限制。三批累计额外重试9724／2332／2681次。Seed42固定恢复Controller `3122030`正常退出；Model-only和Native Worker继续，有限队列随后处理技术恢复及联合Router。

自02:38快照起，Seed42新增6个通过、10个失败。Model-only `train-fasttext`训练Kev的OFF Low、OFF Max、ON Low／High／Max五个位置得1，OFF High得0。ON High／Max分别报告508522／1933086 Token及$0.10442760／$0.38496440参考费。ComfyUI空闲模型释放后GPU降至1436MiB，服务和锁保留；两个原始Kev Episode首次路由后因Luna 401结束。

Model-only `video-processing／训练Kev OFF Low/High`新增两个有效官方0：62391／68614 Token、$0.03912860／$0.04059960模型参考费，费用未知请求均为0。GLM精确模型404保留为无质量分技术记录。

11月20日00:12发现17898反向代理无监听，旧Mac代理包装反复报`No user exists for uid 501`；已结束两个失效代理包装，沿原脚本恢复连接，六个在途请求继续，随后收到上游502。01:34确认唯一私有配置的GLM凭据比四个原内存对象更新，仅将`glm-colink`条目同步至原memfd，保持精确模型、档位、参数与期限；后续完整Episode已恢复HTTP200。凭据数值不进入结果文件。

自11月19日23:26快照新增历史有效1／0为5／12。通过为`mcmc-sampling-stan Max`、`schemelike-metacircular-eval Low`、`distribution-search Low/High/Max`；有效失败为`compile-compcert Low/High/Max`、`schemelike-metacircular-eval High/Max`、`bn-fit-modify Low/High/Max`、`circuit-fibsqrt Low/High/Max`、`fix-ocaml-gc Low`。原失败尝试及费用保留，已有有效0不再运行。

21:58以后，Model-only 新增 `reshard-c4-data／训练 Kev OFF/ON Low/High/Max` 六个官方1；历史恢复新增 `llm-inference-batching-scheduler High/Max`、`mcmc-sampling-stan Low/High` 四个官方1，及 `mailman Low/Max`、`make-mips-interpreter High`、`mteb-retrieve Low/High` 五个有效官方0。每次恢复的用量和费用在原逐题表中单列，旧故障记录保留。

自18:47快照新增历史有效1／0为12／14。通过为 GLM 的 `code-from-image Low`、`constraints-scheduling Low/High/Max`、`financial-document-processor Low`、`custom-memory-heap-crash High/Max`、`dna-insert High/Max`、`feal-differential-cryptanalysis Low`、`feal-linear-cryptanalysis Low/Max`。有效失败为 `tune-mjcf Low/High/Max`、`caffe-cifar-10 Low/Max`、`code-from-image Max`、`dna-assembly Low/High/Max`、`extract-moves-from-video Low/High/Max`、`filter-js-from-html Low`、`llm-inference-batching-scheduler Low`。原故障及恢复费用分别保留，不再运行有效失败。Model-only 新增两个通过：`portfolio-optimization／训练 Laya OFF Max` 和 `regex-chess／训练 Kev OFF Low`；六个失败为 portfolio-optimization 的训练 Kev OFF/ON Low/High、regex-chess 的训练 Kev ON Low，以及 reshard-c4-data 的训练 Laya OFF Max。

### 本轮五次独立恢复

| 任务／GLM 档位 | 有效 Reward | 原 Verifier | 本次已报 Token | 本次已知参考费 USD | 费用未知请求 | Harbor 秒 |
|---|---:|---:|---:|---:|---:|---:|
| adaptive-rejection-sampler／Low | 缺分：请求重试到期 | 0 | 388392 | 0.03997555 | 2 | 1015.172599 |
| write-compressor／Low | 0 | 0 | 16740 | 0.00437345 | 1 | 1036.729581 |
| write-compressor／High | 0 | 0 | 456380 | 0.03647342 | 1 | 1026.159315 |
| write-compressor／Max | 0 | 0 | 990 | 0.00016530 | 1 | 1035.338945 |
| large-scale-text-editing／High | 0 | 0 | 800286 | 0.05064648 | 1 | 1277.977672 |

五次合计 1662788 已报 Token、$0.13163420 已知参考费，六次请求费用未知。后四项均在原 Agent 时限结束并取得有效官方 0，保留终局。新增 Model-only 完整通过为 `portfolio-optimization／原始 Laya ON Max`：39 次生成全选 GLM Max，官方 1、804991 已报 Token、$0.04212749 已知参考费、1478.349717 秒；10 次教师请求、短评消费 0，13 次请求费用未知。同批 `mteb-leaderboard／训练 Kev ON High` 新增官方 0；两项独立 Trial 见逐题目录。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

## 2026-11-19 12:00 台北 · 新增技术中断

Model-only 已结束 1899／2136，官方 1／0 为 356／189，缺分 1334，另有评分依赖故障 20。两次新结束的运行已从 GPU 等待进入生成，随后因 Colink 403 或 Codegoai 401 结束。Seed42 中三次 Terra High 恢复运行在原时限内连续收到 502，原 Verifier 记录为 0，实验质量列记接口中断。三次已报告 221,236 Token，已知模型参考费 $0.13623520，各有一次请求费用未知。联合批次的有效成绩维持 99／57，动态策略仍待首跑。

## 2026-11-19 11:24 台北 · 官方结果与接口状态

| 批次 | 已结束／计划 | 有效 Reward 1／0 | 缺分／评分依赖故障 | 运行／未首跑 | 模型＋教师已知参考费 USD | 费用未知请求 |
|---|---:|---:|---:|---:|---:|---:|
| Model-only（10:57） | 1897／2136 | 356／189 | 1332／20 | 1／238 | 33.49232752 | 1897 |
| Seed43 联合 | 261／957 | 99／57 | 105／0 | 0／696 | 15.32542777 | 196 |
| Seed42 历史（11:24） | 1513／1513 | 364／377 | 716／56 | 0／0 | 46.65940340 | 1288 |

Seed42 的 1513 个位置均已有结束记录，其中 741 个有有效官方评分。Seed43 联合批次已结束的 261 个位置均为固定模型，696 个待首跑位置为动态联合路由，含此前排除的 22 个位置。Model-only 的待首跑数含此前排除的 48 个位置。

Seed42 的 `fix-ocaml-gc／Terra High` 于 11:21 取得 [官方 Reward 1](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/trials/fix-ocaml-gc/terra_high/42/official_result.json)。本次 74 次生成均为 HTTP 200，返回模型及 High 档与请求一致，额外重试 0。完整任务耗时 3552.615275 秒，模型共报 6,500,117 Token，含缓存读入 5,743,744 Token，模型参考费 $1.15204420。供应商实收及资源费仍未知。

Colink 的新 GLM 凭据已与 A6000 队列内存配置核对一致，11:09 实际生成仍返回 HTTP 403 `INSUFFICIENT_BALANCE`。Codegoai 的 Luna 生成在 10:55 返回 HTTP 401 `Invalid token`，教师使用同一供应商。接口中断保留为技术记录。

## 2026-11-19 10:43 台北 · Colink账户余额与批次进度

GLM私有凭据已更新至唯一0600配置，A6000活动队列中的凭据与之相同。真实Colink生成请求返回HTTP 403 `INSUFFICIENT_BALANCE`；新增尝试无官方Reward，不计作模型质量失败，也不再重复发起。Model-only最近汇总10:30为1895/2136：Reward 1/0为356/189，无有效Reward1330、Verifier依赖缺项20、运行0、未开始241；模型与教师参考费$33.49232752、费用未知请求1895。Seed43联合最近汇总03:29为261/957：99/57/105、未开始696，参考费$15.32542777、费用未知请求196。Seed42历史批次10:42汇总1509/1513：363/377/713、依赖缺项56、运行3、未开始1；参考费$45.50735920、费用未知请求1265。GLM恢复位置保持缺分；Model-only及Seed42各有Harbor容器仍在执行。

## 2026-11-19 08:49–08:51 · A6000原队列快照

| 批次 | 已结束／计划 | 官方1 | 官方0 | 缺分 | Verifier依赖缺项 | 运行 | 未首跑 | 已知模型＋教师参考费USD | 请求费用未知 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Model-only | 1892／2136 | 354 | 193 | 1313 | 32 | 2 | 242 | 32.11756632 | 1876 |
| 联合 | 261／957 | 99 | 57 | 105 | 0 | 0 | 696 | 15.32542777 | 196 |
| 历史Seed42 | 1509／1513 | 359 | 374 | 720 | 56 | 3 | 1 | 45.19441491 | 1162 |

Model-only有48个原矩阵位置、联合有22个原矩阵位置已从本轮及后续恢复队列排除；分母保留原矩阵，因此未首跑数包含这些位置。两题所有过往Trial与结果保留，不再发起新Episode。历史技术恢复期间四个原Harbor Episode正在执行，队列2630763仍运行。

自06:16快照后，历史批次另取得25个有效官方评分：12个Reward 1、13个Reward 0；新增有效Episode合计9,382,752已报API Token、已知模型参考费$0.70741649，另有15条请求的费用未知。另一个`qemu-startup／GLM Max`位置因生成请求在原任务时限内超时，原Verifier虽然写0，该位置仍记为接口故障、没有有效质量分。

新增通过：`model-extraction-relu-logits／GLM High`、`password-recovery／GLM High/Max`、`prove-plus-comm／GLM Low/Max`、`pypi-server／GLM High/Max`、`pytorch-model-recovery／GLM Low/High/Max`、`qemu-startup／GLM High`、`regex-log／GLM Low`。

新增有效失败：`polyglot-c-py／GLM Low`、`polyglot-rust-c／GLM High/Max`、`pytorch-model-cli／GLM Low/High/Max`、`qemu-alpine-ssh／GLM Low/High/Max`、`qemu-startup／GLM Low`、`query-optimize／GLM High/Max`、`raman-fitting／GLM Low`。每个位置的单次Trial、Token、已知参考费、费用缺项与Harbor时间见历史批次逐题CSV及Trial目录。

## 2026-11-19 06:15前 · Colink订阅恢复历史快照

| 批次／台北时刻 | 已结束／计划 | 官方1 | 官方0 | 缺分 | 评分依赖故障 | 运行 | 待首跑 | 已知模型和教师参考USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Model-only／06:15 | 1880／2136 | 350 | 193 | 1305 | 32 | 2 | 254 | 30.78120818 |
| 联合／06:14 | 261／957 | 99 | 57 | 105 | 0 | 0 | 696 | 15.32542777 |
| 历史Seed42／06:16 | 1509／1513 | 338 | 361 | 748 | 62 | 4 | 0 | 44.07746163 |

Colink新凭据已用于GLM完整Episode，Low／High／Max三档均有实际工具调用。五个原始403响应明确为`SUBSCRIPTION_NOT_FOUND`的Seed43位置进入单次技术恢复。`llm-inference-batching-scheduler`的原始Laya OFF、训练Laya OFF／ON，以及`mailman`的原始Laya OFF／ON均为固定Max的Model-only路由，原位置仍无有效评分。Luna／Codegoai生成接口最近记录仍为401。Terra／Jiji已在原Harbor取得官方结果。三批分别有1849、196和1124条请求费用未知，供应商实收及资源美元费用缺项。

新增Episode／恢复均排除`vulnerable-secret`和`break-filter-js-from-html`，原历史日志和评分保留。两题对应Model-only的48个、联合的22个计划位置不执行；表内仍保留正式矩阵分母，故“待首跑”也包含这些排除位置。

### 06:14–06:16 Model-only完整Episode

fix-ocaml-gc／原始Laya OFF Model-only Max／Seed43取得Harbor官方1，Trial3698ecf4-928e-49fa-afc2-932815ea882b，原断言1/1通过。126次生成均请求GLM Max，返回Effort未报告；2次额外重试，本次6918671已报API Token、$0.26481256已知模型参考费、2次请求用量与费用缺项。Provider已报缓存读取6513472 Token、8次请求未报缓存；Router墙钟144.187932秒，GPU等待0.016230秒，Harbor4442.840521秒。

同题原始Laya ON Max的原Verifier也写1，Harbor因NonZeroAgentExitCodeError保留无有效评分。该次先完成65条GLM Max生成，随后1条Luna Max请求401中断；14条Luna Low教师请求均401，短评消费0。原Verifier1、Harbor空值、2117162已报Token、$0.10121368已知参考费、16条请求费用缺项及2254.950625秒均分别保留。

历史Seed42本轮新纳入6个有效1及1个有效0如下。表内Token、参考费与墙钟取各自单次Episode，原失败尝试另存。

| 固定GLM策略／任务 | 官方Reward | 本次已报API Token | 本次已知参考USD | 费用缺项请求 | Harbor秒 |
|---|---:|---:|---:|---:|---:|
| Low／merge-diff-arc-agi-task | 1 | 66078 | 0.00425038 | 0 | 257.551132 |
| High／merge-diff-arc-agi-task | 1 | 242240 | 0.02131848 | 0 | 539.115923 |
| Max／merge-diff-arc-agi-task | 1 | 389104 | 0.02991372 | 0 | 472.129068 |
| Max／model-extraction-relu-logits | 1 | 616350 | 0.06138191 | 2 | 1024.524686 |
| Max／multi-source-data-merger | 1 | 272924 | 0.01836808 | 0 | 430.144449 |
| Max／nginx-request-logging | 1 | 55334 | 0.00608804 | 0 | 210.965136 |
| High／make-doom-for-mips | 0 | 2264141 | 0.10372820 | 1 | 1065.754425 |

make-doom-for-mips Low／Max的原Verifier均0，现有分析列PROVIDER_RETRY_DEADLINE：此前各一条502已重试恢复为200，末次单次读取分别在6.693秒／77.546秒到原期限。两档分别完成52／32次生成，末次各一次读取超时。原0、恢复成功的早期502、末次时限及质量空值均保留，延迟贡献沿实际记录区分。

05:55四个Seed42旧uvx故障已加入有限队列2492278：GLM Low的overfull-hbox、adaptive-rejection-sampler、cobol-modernization及GLM High的build-pmars。原bin/uv与bin/uvx现均存在、可执行，相同依赖机制已有完整成功Episode。四个位置此前都有一次无有效评分的恢复记录，普通批次会跳过；现等待固定阶段2253174自然结束后沿原--task／--strategy入口各接续一次。另三个同类旧恢复位置属于Luna的adaptive-rejection-sampler Low／High／Max，仍有渠道401，保留无分。其余55个历史评分依赖故障尚无本轮恢复标记，继续沿原普通恢复入口处理。

05:22至05:43历史Seed42新增以下七个有效官方结果，均由原Verifier给分，原恢复入口对这七项返回None，保留终局。Token与参考费均取本次独立Episode。

| GLM任务／档位 | 官方Reward | 原断言通过 | 本次已报API Token | 本次已知参考USD | 本次费用缺项请求 |
|---|---:|---:|---:|---:|---:|
| headless-terminal／High | 1 | 7／7 | 943998 | 0.05963380 | 1 |
| headless-terminal／Max | 0 | 6／7 | 915786 | 0.05990997 | 1 |
| largest-eigenval／High | 0 | 21／27 | 716751 | 0.06292392 | 1 |
| largest-eigenval／Max | 0 | 20／27 | 752129 | 0.05901461 | 0 |
| log-summary-date-ranges／Low | 1 | 2／2 | 10165 | 0.00114170 | 0 |
| log-summary-date-ranges／High | 1 | 2／2 | 92646 | 0.00915795 | 0 |
| log-summary-date-ranges／Max | 1 | 2／2 | 46368 | 0.00443302 | 0 |

headless-terminal Max的失败为任务内localhost:8000后台服务连接拒绝。largest-eigenval两档分别有6和7个原速度断言未通过；High出现50μs对49μs的失败，Max出现252μs对111μs的失败。原性能成绩保持0，执行环境与实现各自的耗时贡献缺测。

### 同题训练前后：05:21快照

以下为Model-only、Seed43、双方均有有效官方评分的配对。通过数和费用均按原始版／训练版排列。费用列仅使用双方单次API参考费齐全的子集，该子集的通过数另列；供应商实收、Router、工具与资源美元费用仍缺项。教师ON表示配置开启，实际短评消费单独统计。

| Router／教师／固定档位 | 有分配对数 | 原始／训练通过数 | 单次费用齐全配对数 | 费用子集原始／训练通过数 | 原始／训练单次API参考费合计USD |
|---|---:|---:|---:|---:|---:|
| Laya OFF Low | 14 | 7／5 | 13 | 7／5 | 0.06187902／0.05304593 |
| Laya OFF High | 13 | 10／9 | 11 | 9／8 | 0.05885040／0.07103216 |
| Laya OFF Max | 12 | 8／10 | 5 | 4／5 | 0.11812642／0.07792263 |
| Laya ON Low | 13 | 9／6 | 9 | 7／5 | 0.04502892／0.03214226 |
| Laya ON High | 13 | 8／6 | 9 | 7／6 | 0.05598340／0.05650303 |
| Laya ON Max | 16 | 10／9 | 6 | 4／4 | 0.15511911／0.12221184 |
| Kev OFF Low | 12 | 2／9 | 12 | 2／9 | 0.04807856／0.79889000 |
| Kev OFF High | 14 | 8／10 | 13 | 8／10 | 0.07696922／0.84692090 |
| Kev OFF Max | 11 | 6／5 | 9 | 4／5 | 0.12340202／1.72878820 |
| Kev ON Low | 12 | 5／10 | 9 | 4／8 | 0.02756582／0.47967580 |
| Kev ON High | 11 | 6／10 | 6 | 3／6 | 0.04774198／0.25828660 |
| Kev ON Max | 14 | 10／12 | 9 | 7／7 | 0.07880220／1.25152050 |

Kev OFF Low在同一12题中多完成7题，API参考费为原始版16.62倍。原始版105次生成全请求Luna Low，训练版152次生成全请求Terra Low，两侧模型切换均0；该12题的固定Terra Low完整对照尚缺，24次Episode的execution_environment字段均为空，物理VM模式缺测。Kev OFF Max在全部11个配对中少完成1题。Laya OFF Low在14个配对中少完成2题，Laya OFF Max在12个配对中多完成2题，各档位方向不同。当前272个有评分的教师ON位置中，191个有短评被Router消费、通过125个；81个没有消费短评、通过53个。教师配置、实际调用和短评消费保留独立字段。依据为本批metrics/per_episode.csv、metrics/comparisons.json及逐题原Harbor导出。

## 2026-11-19 · 继续执行后的官方结果与重试终局

台北时间11月19日快照如下。历史批次各位置均已有运行记录，待恢复的旧位置仍保留原Trial。

| 批次／时刻 | 计划 | 已结束 | 有效1 | 有效0 | 已结束缺分 | Verifier依赖故障 | 运行 | 待调度 | Trial | 已知模型及教师参考USD | 请求费用未知 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Model-only／04:29 | 2136 | 1860 | 344 | 193 | 1291 | 32 | 1 | 275 | 1861 | 30.04224232 | 1810 |
| Model×Effort联合／04:29 | 957 | 261 | 99 | 57 | 105 | 0 | 0 | 696 | 300 | 15.32542777 | 196 |
| 历史Seed42／04:30 | 1513 | 1509 | 316 | 350 | 781 | 62 | 4 | 0 | 2620 | 42.65496655 | 1106 |

Seed43固定阶段，GLM Low为42/74，Luna High为4/10，Terra High为53/72。分母是各策略取得有效评分的题数，每组计划87题。GLM Low与Terra High共同取得有效评分的63题中分别通过37题和46题。其中双方累计模型参考费均有记录的37题分别通过24题和30题，参考费分别为$0.44206083和$2.25330140。完整成本缺供应商实收及资源费，联合Router仍待正式结果。

### 单题单次运行用量

每个位置取最后一次有有效官方评分的Episode，同时要求该次模型与教师的Token齐全。缓存读取含在输入中，推理Token含在输出中。Router本地前向单独记录。以下费用为同一批选中Episode的模型与教师参考费中位数。

| 策略 | 用量齐全／有效评分 | 单次API Token中位数 | 单次API Token最小–最大 | 单次参考费中位数（USD） |
|---|---:|---:|---:|---:|
| Model-only各策略合计 | 393／537 | 70,157 | 5,952–978,893 | 0.01114928 |
| Seed43 GLM Low | 62／74 | 156,536 | 3,561–6,971,908 | 0.01044438 |
| Seed43 Luna High | 10／10 | 125,274 | 13,239–365,019 | 0.00603151 |
| Seed43 Terra High | 57／72 | 142,890 | 21,475–3,008,519 | 0.05493340 |
| 历史Seed42各策略合计 | 606／666 | 79,769 | 8,090–3,850,636 | 0.01032604 |

各批的metrics/per_episode.csv保留latest_trial_known_tokens和latest_trial_usage_unknown_requests，可直接查看每题单次已报Token及缺项。单次完整输入或输出有缺项时，对应字段保持空值。

以下每行是Seed43、固定Terra High的一次新独立完整Episode，均为原官方Reward1，请求与返回模型和High匹配。

| 任务 | 原断言通过 | 本次已报API Token | 已知模型参考USD | 额外重试 | Provider已报缓存读取Token | Harbor秒 |
|---|---:|---:|---:|---:|---:|---:|
| code-from-image | 2/2 | 223092 | 0.10942400 | 0 | 153600 | 516.401811 |
| custom-memory-heap-crash | 6/6 | 273895 | 0.13016700 | 0 | 181760 | 432.288186 |
| break-filter-js-from-html | 1/1 | 219178 | 0.14789000 | 2 | 154880 | 959.926754 |
| mteb-retrieve | 2/2 | 212851 | 0.10979260 | 1 | 138112 | 602.009708 |
| rstan-to-pystan | 6/6 | 2356762 | 0.38832200 | 0 | 2152960 | 1708.788725 |
| distribution-search | 4/4 | 106265 | 0.06879060 | 15 | 72832 | 854.161007 |
| mteb-leaderboard | 2/2 | 178506 | 0.10412920 | 19 | 99584 | 742.858221 |
| fix-ocaml-gc | 1/1 | 4477202 | 0.88156600 | 33 | 3856640 | 3601.666216 |
| pytorch-model-cli | 6/6 | 375086 | 0.19089160 | 0 | 275072 | 705.780305 |

九项合计8422837已报Token、$2.13097300已知模型参考费、70次额外重试；失败尝试实收、供应商账单及资源USD未知，物理KV共享未知。缓存数字按Provider实际报告读取，不与输入Token重复相加。新增正常有效失败还包括circuit-fibsqrt／Terra High（2/3断言）及portfolio-optimization／Terra High（3/4断言），原0保留。

circuit-fibsqrt／Seed43新增完整Episode如下。训练Laya Max的40次生成均请求GLM Max，返回Effort未报告。Kev三组均请求并返回Terra同档。四组fallback均false，原官方Verifier各执行3项断言。

| Model-only策略 | 官方Reward | 通过断言 | 本次已报API Token | 已知模型参考USD | 未知费用请求 | 额外重试 | Harbor秒 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 训练Laya ON Max | 1 | 3/3 | 3340892 | 0.15077049 | 10 | 0 | 2003.820276 |
| 训练Kev OFF High | 0 | 2/3 | 67961 | 0.07229620 | 2 | 2 | 542.916387 |
| 训练Kev ON Low | 0 | 2/3 | 153157 | 0.13558740 | 3 | 0 | 362.487033 |
| 训练Kev ON High | 0 | 2/3 | 129014 | 0.17761880 | 2 | 1 | 679.585762 |

Laya ON Max和Kev ON Low的教师分别10次及3次请求均401，Kev ON High发出1次教师请求。三者短评消费均为0。逐次请求、模型身份、重试及未知费用保存在本批trials目录。

bn-fit-modify／训练Kev／Model-only／Seed43三档完整Episode如下，全部生成请求与返回Terra及相同Effort。教师2／2／3次调用均401，短评消费各0次；失败请求和资源USD仍缺项。

| Effort／教师ON | 官方Reward | 通过断言 | 本次已报API Token | 已知模型参考USD | 额外重试 | 未知费用请求 | Provider已报缓存读取Token | Harbor秒 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Low | 0 | 8/9 | 58760 | 0.04806080 | 70 | 3 | 23936 | 2549.111579 |
| High | 1 | 9/9 | 119224 | 0.06593760 | 20 | 4 | 84992 | 1094.999891 |
| Max | 1 | 9/9 | 155261 | 0.13650180 | 31 | 6 | 96256 | 1735.115663 |

Low为正常有效失败，保留原0。High／Max两项成功与教师调用失败分别记录。

**100次额外重试已实际触顶。** bn-fit-modify训练Kev OFF Low／High各一条请求共101次尝试，最终attempt_index=100、RETRY_LIMIT。两项原Verifier均执行9项断言、写Reward0，Harbor因接口异常不认可有效质量评分，保留PROVIDER_REQUEST_FAILED；不将其计作模型能力0。Low／High分别36795／41956已报Token、$0.03738780／$0.02342400已知参考费、各1次请求费用未知、Harbor3629.606216／3606.610085秒。

**query-optimize仍缺官方评分。** Terra High原Episode正常提交后，原Verifier900秒超时。原镜像1CPU／2GiB只读诊断：参考SQL1.829秒完成，原始SQL823.925秒完成，均500行；SQLite3.45.1原生CLI及3.50.4评分运行时的对照保留。依赖预装9.986秒后，重建保存的最终文件并调用原Harbor Verifier，仍900.090秒超时；诊断无正式Episode Reward、资源USD未知。首轮缺容器日志目录的诊断失败、重试及清理记录均保留，未据此提升原任务成绩。

历史Seed42首批5个GLM技术恢复位置均取得有效官方评分。5条凭据描述符启动故障的原Trial保留。修复版本6eaee77a9e90ece40d4c0a3378eb1803d8bc26c1将凭据描述符绑定父PID。以下为恢复后各次完整Episode，额外重试均为0。

| 任务／请求档位 | 官方Reward | 通过断言 | 本次已报API Token | 已知模型参考USD | 请求费用缺项 |
|---|---:|---:|---:|---:|---:|
| configure-git-webserver／GLM Low | 0 | 0/1 | 90093 | 0.00638627 | 0 |
| adaptive-rejection-sampler／GLM High | 0 | 6/9 | 1044649 | 0.05919533 | 1 |
| adaptive-rejection-sampler／GLM Max | 0 | 5/9 | 838535 | 0.06354141 | 1 |
| cancel-async-tasks／GLM High | 1 | 6/6 | 595317 | 0.03794485 | 1 |
| cancel-async-tasks／GLM Max | 1 | 6/6 | 1277766 | 0.07791612 | 0 |

随后count-dataset-tokens／GLM Low、High均获官方1。qemu-alpine-ssh／Terra High获有效0，已报1010618 Token、$0.39315320已知参考费，1个请求费用缺项。固定并发4、Router并发2及每1200秒采集继续。

## 2026-11-19 · 新凭据后的官方任务结果

Colink凭据已更新到唯一0600私有配置与原控制器内存；GLM、Terra的实际生成和工具执行已恢复，Luna仍401/Invalid token。以下均为原Seed43策略位置的新独立Harbor Episode，0额外重试；旧Trial及费用完整保留。

| 任务／固定策略 | 官方Reward | 通过断言 | 本次API Token | 本次模型参考USD | Harbor秒 |
|---|---:|---:|---:|---:|---:|
| modernize-scientific-stack／GLM Low | 1 | 2/2 | 11030 | 0.00103893 | 129.639379 |
| pypi-server／Terra High | 1 | 1/1 | 112688 | 0.08142400 | 301.465327 |
| prove-plus-comm／Terra High | 1 | 4/4 | 126691 | 0.06974860 | 336.666307 |
| polyglot-rust-c／GLM Low | 1 | 1/1 | 181150 | 0.03521321 | 875.733494 |
| crack-7z-hash／GLM Low | 1 | 2/2 | 156829 | 0.00937014 | 405.902621 |
| overfull-hbox／GLM Low | 1 | 4/4 | 232336 | 0.01612408 | 625.056263 |

六项合计820724已报API Token、$0.21291896模型参考费，均无请求费用缺项；供应商实收及资源USD未知。表内仅列该次Episode。GLM后三项的Controller exit_code=2、Agent SUBMITTED、Harbor OFFICIAL_ARTIFACT_VERIFIED及Reward1全部按原记录保留。

Terra High两项首请求均由502重试至200并执行工具，随后仍到原任务期限，原官方0保留、质量单列接口故障。以下Token和费用为已知部分，各有1次请求费用缺项。

| 任务／Terra High | 原官方Reward | 质量评分 | 工具结果 | 额外重试 | 已报Token | 已知参考USD | Harbor秒 |
|---|---:|---|---:|---:|---:|---:|---:|
| polyglot-rust-c | 0 | PROVIDER_RETRY_DEADLINE | 4 | 15 | 27413 | 0.02725860 | 1011.913281 |
| polyglot-c-py | 0 | PROVIDER_RETRY_DEADLINE | 1 | 30 | 5461 | 0.00634500 | 1017.149216 |

训练Laya OFF Max的bn-fit-modify为正常有效失败：原Reward0、275377已报Token、$0.02339090参考费、0额外重试、Harbor742.499254秒。该有效0不进入技术恢复。

同题Seed43的训练Laya ON Max原Reward1，Trial bc560746-45f3-4a08-8cab-e02018c33a51；18次生成均请求GLM Max、200013已报Token、$0.01527039模型参考费、0额外重试、Harbor622.177327秒。GLM返回Effort未报告；Provider报告缓存读取163328 Token，物理KV共享未知。5次Luna教师请求均401、短评消费0、5次请求费用未知；该成功不归因教师干预。

11-18 23:59现行分析快照如下；“已结束缺分”不含正在恢复的位置。联合恢复中的4项保留各自旧Trial。

| 批次 | 计划位置 | 已结束 | 有效1 | 有效0 | 已结束缺分 | Verifier依赖故障 | 运行 | 未开始 | 原Harbor Trial | 已知参考USD | 请求费用未知 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Model-only | 2136 | 1818 | 341 | 188 | 1257 | 32 | 2 | 316 | 1819 | 27.49070775 | 1725 |
| Model×Effort联合 | 957 | 257 | 90 | 50 | 117 | 0 | 4 | 696 | 273 | 9.31858462 | 153 |
| 历史Seed42 | 1513 | 1513 | 308 | 342 | 797 | 66 | 0 | 0 | 2599 | 42.11526315 | 1098 |

费用按原试次累计已知模型与教师参考部分，仍缺供应商及资源实收；各策略及成对结果见两批`metrics/per_strategy.csv`、`per_episode.csv`和`comparisons.json`。全部89题的完整比较尚未完成。

分析212be725580150967149e1baa8125e157ba8fb95统一处理“本Episode已有生成重试，末次请求因原任务期限截断”的真实记录；三批各10／5／2个同Trial原有效0转为接口缺分，官方原始Reward不变。三批当前采集器2097071／2097072／2097073保持1200秒间隔。2057318继续query-optimize、torch-tensor-parallelism、tune-mjcf的四项固定恢复；1696641继续bn-fit-modify训练Kev OFF Low／High；2097543等待2057318后接续pytorch-model-cli／qemu-alpine-ssh Terra High，均沿原CLI、Seed43和原时限。

## 2026-11-18 18:06 · 原批次接续与渠道故障定位

18:06台北现行分析导出Model-only 1770/2136位置结束，339有效Reward1、195有效Reward0、1204缺分、32依赖故障另列；2运行、364未开始。1771原Trial，模型与教师已知参考费$26.88846586、1665请求费用未知、7844次额外重试（已结束Episode），另1次直连诊断消费未知。联合固定261/957、现265原Trial、146请求费用未知、1994次额外重试；历史1513位置保持原结果，696个联合Router位置待现有队列接续。

`compile-compcert`原始Laya六组均未执行工具。OFF Low/Max为81/79次GLM请求，ON Low/Max为68/63次GLM请求，分别额外重试80/78/67/62次后在原期限停止；两项High为Luna401、额外重试0。六组原Verifier均写0，质量表单列接口故障，费用未知。GLM原429正文为`group requests-per-minute limit exceeded`，原502正文为`Upstream access forbidden, please contact administrator`。逐尝试与独立Episode见本批`trials/compile-compcert/*/43/`。

16:26两项训练Laya OFF Low/High停在首个ROUTER_START，尚无生成请求；共享GPU锁为READ，H3扩散进程计算、GPU剩余629MiB。原Router等待显存并保留2400秒任务期限，原控制器1696641和有限接续1345012继续；GPU锁、H3任务与四套权重保持现行配置。

16:32现有分析提交a3dd87909260252205e45925ca822af480b96216已补部署，终止性401不再进入技术恢复队列；原始0和缺评分身份保持。三个现行采集进程1909073/1909074/1909081沿原目录每1200秒导出，原批次控制进程继续。

16:41显存自然释放至23455MiB，训练Laya OFF Low因首个Router未返回达到2400秒，原0单列资源故障；OFF High真实前向91.955毫秒、包含等待的路由墙钟1955.743秒，选Luna High后401、0额外重试、无有效Reward。两项均无工具执行，原队列随后接续OFF Max及ON Low。

17:29四项Seed43 Terra High独立恢复已结束，Controller1920505／持有1920499自然退出。每项34次HTTP502、33次额外重试后在原期限停止，0次生成、0工具；原Verifier全部执行并写Reward0，质量仍列PROVIDER_RETRY_DEADLINE，费用未知。原联合累计265个Trial，有效84/55及缺分122保持，原有限队列会复用这四项本轮恢复记录。

| 原位置任务 | 本次官方通过/失败断言 | 本次Harbor秒 | 本次Verifier秒 |
|---|---:|---:|---:|
| pypi-server | 0/1 | 981.310651 | 52.277454 |
| prove-plus-comm | 1/3 | 984.748705 | 47.701603 |
| pytorch-model-cli | 0/6 | 1061.207227 | 93.031077 |
| qemu-alpine-ssh | 0/1 | 942.780942 | 15.157137 |

四项新旧Episode身份、逐尝试、原断言及费用记录分别保存在联合批次`trials/<任务>/terra_high/43/`和`metrics/resource_observations.json`。

17:43使用原内存凭据对GET /v1/models分别读取原代理与A6000直连：Luna均401/Invalid token，GLM、Terra均200并列出精确模型ID；原生成接口仍返回GLM429/502、Terra502。模型列表、实际生成和官方Reward分列，Benchmark网络路径保持原配置。

17:57同一Terra Low/4096失败请求单次改用A6000直连诊断，2.991秒仍返回Cloudflare502、正文error code: 502。该次不执行工具，Token与费用未知，独立记录于Model-only资源文件，官方Episode成绩及费用列保持原范围；诊断未知消费另计，不填0美元。原Benchmark请求继续沿既有网络路径。

18:03训练Laya ON Max的compile-compcert原Episode结束：78次GLM Max请求、77次额外重试至原任务期限，0生成、0工具；原官方Reward0保存，质量列为PROVIDER_RETRY_DEADLINE，费用未知。

`mteb-retrieve`全部24组已结束。下表每行是训练Kev、Seed43的一次完整Episode，所有生成均使用Terra对应档位、请求与返回身份和档位一致、额外重试0；原官方Verifier每行执行2项断言。

| 教师/档位 | Reward | 通过断言 | 已报API Token | 已知模型参考USD | 未知费用请求 | Harbor秒 |
|---|---:|---:|---:|---:|---:|---:|
| OFF Low | 0 | 1/2 | 56848 | 0.04330160 | 0 | 359.080742 |
| OFF High | 1 | 2/2 | 301213 | 0.13190660 | 0 | 710.476240 |
| OFF Max | 1 | 2/2 | 292020 | 0.18467360 | 0 | 827.242378 |
| ON Low | 0 | 1/2 | 50726 | 0.02628360 | 2 | 304.751402 |
| ON High | 1 | 2/2 | 317918 | 0.13006360 | 3 | 736.524990 |
| ON Max | 1 | 2/2 | 320285 | 0.18646900 | 4 | 864.946085 |

ON的2/3/4次Luna教师请求全部401，短评消费均0；表中ON费用仅为已知模型部分，教师及完整成本未知。该题High与Max均成功，OFF High模型参考费比OFF Max低28.57%；当前记录无法归因教师收益。其余18组由12个GLM429/502到期和6个Luna401构成，原始0、故障和费用保留，质量不计模型失败。

13:17 `rstan-to-pystan`已有18组结束，16组因Luna HTTP401、2组因GLM HTTP502到任务期限而无Reward；当前2组继续运行。本地唯一配置与控制器内存凭据绑定一致，Luna/Terra/GLM各仅1个端点，无同模型备用；Luna 401没有可切换账户。401位置不重复发送相同凭据请求，GLM502按原请求与任务期限继续最多100次额外重试。逐项证据见本批`trials/mteb-retrieve/*/43/summary.json`、`trials/rstan-to-pystan/*/43/summary.json`与服务器原Episode记录。

## 2026-11-18 · 已同步公开中期结果（非终局）

沿原远端活跃观察者公开导出目录只增量同步、不删除本地文件：Model-only `20261112-v9-model-only`、Joint `20261112-v9-joint-paired`、历史 `20261108-v9-rq1-glm`。公开逐Episode、逐策略、逐任务、费用分解、配对比较、资源观察、事件与原Trial摘要均在各批次的`metrics/`、`trials/`、`events`及`review.md`；同步排除私有/raw目录，不含私有原始数据。原观察者仍活跃，以下为非终局快照，不能据此标批次完成。

Model-only截至12:07快照共2136位置：已结束1726，运行2，未开始408；有效Reward 1/0为339/191，1164缺有效评分，32个Verifier依赖失败另列，已保存1727个原Harbor Trial。已知模型与教师参考费合计$25.22174546，1594次请求费用未知。Joint共957位置：已结束261（87题×3固定参照），696个Router位置未开始；有效Reward 1/0为84/55，122缺有效评分，261个原Trial，已知模型与教师参考费$9.07206206，142次请求费用未知。历史批次89×17=1513位置全部结束，Reward 1/0为308/344，795缺有效评分，66个Verifier依赖失败另列，2599个原Trial；已知模型+教师参考费$42.11526315，1098次请求费用未知。实际供应商账单、Router/工具/CPU/GPU/VM美元成本均未知；已知参考费不是供应商实收或总成本，不能作最终净收益结论。

各批次的`metrics/per_strategy.csv`与`per_episode.csv`是当前策略和逐题证据；`comparisons.json`和Model-only的`review.md`按同任务seed43列出双侧均有效评分的配对、费用齐全子集及奖励/参考费差。只读有完整数据的配对；已报告的部分结果不外推到87/89题，也不取代待执行位置。Model-only比较的两道seed43历史任务结果可见其review中的`同题训练、教师与消融对照`表；当前联合批次在未开始前只有三项固定参照有新评分，696个主方法Router位置仍待原队列执行。

原图生成入口`rq1_figures.py`已在uv临时分析环境刷新三批PNG/SVG/PDF，以及Model-only两题配对图。联合批次真实CSV触发默认128KiB字段限制，已按项目惯例设置`csv.field_size_limit(sys.maxsize)`并成功重跑。两题配对图21/40组评分及参考费齐全，其余19组缺项；图中明确标注局部覆盖与完整现金成本未知，不能作为89题终局前沿。

## 2026-11-17 · 原矩阵接续与显存故障处理

11-18 00:01原SSH反向代理已恢复：服务器127.0.0.1:17898转至Mac原Clash17897，本机有限代理58053跟随1696641／1345012。两个在途MCMC请求此前各11次连接拒绝，恢复后继续同请求并收到上游429／502，最后沿原期限结束；首失败及未知费用保留。Luna、Terra、GLM现有同模型备用端点均0。当前唯一私有配置与在用描述符的Luna／Terra项一致，GLM账号URL、Key和实际request_model一致，配置展示名、优先级和enabled等字段有变化。

`make-mips-interpreter`训练Kev六组均出现请求Terra却返回`gpt-6-luna`的真实身份冲突；原Provider按MODEL_IDENTITY_MISMATCH结束并保存请求、响应与未知费用，质量列技术缺分。High的70f57191-a396-4fc4-8c3f-0c998fcf36d3首条返回Terra、第二条返回Luna；Max请求max返回xhigh亦保持原标签。原模型与档位未改，渠道需恢复精确模型服务。

`filter-js-from-html`训练Kev ON Max沿新版浏览器生命周期完成原测试：174.88秒、XSS断言通过／干净HTML断言失败、原Reward0。该题训练Kev ON三档均已有完整官方终局，旧OFF Low/High资源超时仍待原技术恢复，官方脚本和答案保持原版。

浏览器生命周期处理后，`filter-js-from-html`训练Kev ON High的1074c2aa-5535-4b34-bf1d-286703cecc83由原测试166.08秒完成，两项断言失败、Reward0；单次51701模型Token、$0.04158980参考费、2教师请求费用未知、Harbor552.017711秒、0生成重试。ON Low单次27261 Token、$0.01644740参考费、1教师请求费用未知、Harbor982.951811秒。两条有效0保留；真实恢复分类对它们返回None，旧OFF Low/High则返回VERIFIER_CHROMIUM_ORPHAN_RESOURCE_EXHAUSTION。

`filter-js-from-html`实际测试故障已定位：官方脚本先杀ChromeDriver再quit，Chromium子进程被PID1收养；在途容器达到1904进程、1.993/2GiB，cgroup记录30384次OOM、17次OOM kill，原测试停留在首项。d2620d8640f88222b6daea8dd40b882c452e3c4b仅为该题浏览器启动设置父进程退出信号SIGTERM，保持原测试与资源时限；在途容器20个已孤立的浏览器主进程退出，随后原官方测试完成。训练Kev ON Low的e5140947-25a4-490a-9afd-24688f29cc7f原Reward0、两断言失败、断言714.90秒；XSS过滤仍失败且干净HTML被改写，有效0保留。此前OFF Low/High的900秒超时继续无分，f3c83d235522c60b70caf44f98395e3957d02c22将该已定位故障接入原单位置恢复；当前内存中的有限3993622仍加载旧恢复函数，需在其进入恢复阶段前自然接续新入口。

`feal-linear-cryptanalysis`训练Kev六组均获原官方1；以下为Seed43独立完整Episode，生成额外重试均0。

| 配置 | 模型Token | 已知模型参考USD | 未知费用请求 | Harbor秒 |
|---|---:|---:|---:|---:|
| OFF Low | 208707 | 0.07762460 | 0 | 626.362551 |
| OFF High | 47669 | 0.03386740 | 0 | 237.606895 |
| OFF Max | 126618 | 0.09600440 | 0 | 508.298371 |
| ON Low | 215737 | 0.07372500 | 5 | 637.820816 |
| ON High | 47060 | 0.03127360 | 1 | 253.042948 |
| ON Max | 100806 | 0.08070360 | 2 | 480.598149 |

同题OFF High模型参考费用为Low的43.63%，墙钟为37.93%。差分／线性两题均保留各自完整终局；不同档位的费用和成功关系按实际任务分别比较。

差分密码分析训练Kev的ON High／Max亦取得原官方1：46002／106073模型Token、$0.04013160／$0.09623620模型参考费、450.074889／757.817575秒、0／2次额外重试，1／2请求费用未知。至此该题训练Kev六组均成功；教师短评消费按原日志记录，当前认证故障继续单列。

`feal-differential-cryptanalysis`／训练Kev／Seed43的OFF三档均原官方1、单项攻击断言通过；Low／High／Max分别49661／41568／659176模型Token，模型参考费$0.03716740／$0.03787760／$0.27876960，Harbor446.409173／433.467964／1353.125952秒，额外重试0／0／1、费用请求无缺测。Max与Low同题均成功，Max模型参考费用为Low的7.50倍。ON Low另获原官方1，32925 Token、$0.02726260模型参考费、394.074142秒、1请求费用未知；该次教师401、短评消费0。

`extract-moves-from-video`／训练Kev／Seed43，新Native1142336均返回真实CUDA决策、fallback=false。下表每行对应独立完整Trial，模型全部为Terra对应档位；Token包含该Episode所有生成请求的输入和输出。

| 配置 | 官方结果与质量分类 | 模型Token | 已知模型参考USD | 未知费用请求 | 生成／工具 | Harbor秒 |
|---|---|---:|---:|---:|---:|---:|
| OFF Low | 有效0、2断言失败 | 203999 | 0.05830380 | 0 | 24／24 | 812.267708 |
| OFF High | 原0、请求重试到期，质量缺分 | 618012 | 0.13196880 | 1 | 38／37 | 1893.163672 |
| OFF Max | 有效0、2断言失败 | 456194 | 0.11298520 | 0 | 24／59 | 1951.717678 |
| ON Low | 有效1、2断言全过 | 1152837 | 0.16672020 | 11 | 51／51 | 1559.667492 |
| ON High | 有效0、2断言失败 | 1059409 | 0.18414420 | 10 | 59／59 | 1903.539102 |
| ON Max | 有效0、2断言失败 | 1841639 | 0.28614940 | 9 | 61／71 | 1925.416782 |

五个原0的断言均因/app/solution.txt缺失失败；OFF High的最后请求未恢复，沿原技术恢复另存，另外四个有效0保留。ON三档教师请求11／10／9次均HTTP401，短评消费0；成绩按实际配置登记，教师效果尚无法归因。成功Low模型参考费为OFF Low的2.86倍，供应商和资源实收未知。

02:33末次终局导出：Model-only1632/2136结束，335有效1／183有效0／1082缺分／32依赖故障，2运行、502未开始；68/89题已结束全部24组。已知模型与教师参考费$21.86417166、1485请求费用未知、5936额外重试。联合261/957、84有效1／55有效0／122缺分，余696个Router位置按原队列接续。

MCMC采样题24组全部保存原终局：Laya12组GLM 429／502重试到原任务期限，原始Kev6组Luna401，训练Kev6组请求Terra返回Luna身份不符；均无有效质量分。原官方0、空Reward、每次响应和未知费用分别保留，完整24份公开summary已同步。随后mteb-retrieve两组仍在原服务器容器内执行。

10:24:35原Native入口切至Worker1142336／持有1142328，代码72cac7bbc7e9c72dd3bd8a25308a708a923ab986；旧闲置3708428／3708420退出。原权重、精度及输入保持，实际CUDA分配失败后按观测分配量等待共享显存，原任务期限继续有效；异常、次数、所需字节写入原日志。尚未遇到新版OOM事件，实际恢复效果待原任务触发。

2026-11-17 `code-from-image`／训练Kev OFF／Seed43：Low原官方0、两项断言均失败，High原官方1、两项全过；均0重试、0教师请求、模型费用无缺测。Low单次80292 Token、$0.02542160模型参考费、363.051578秒；High单次102268 Token、$0.02707040、455.964205秒。保留失败Low，不根据该题重新选择权重；完整供应商与资源费用未知。

2026-11-17 `code-from-image`训练Kev补齐：ON Low/High/Max均官方1，146476／157938／237616 Token、模型参考费$0.02346240／$0.02355080／$0.04964000，Harbor702.340897／659.919150／743.275536秒；三组各4次教师请求、0次短评消费。OFF Max官方1，274457 Token、$0.06271220、789.205727秒。原队列随后进入`constraints-scheduling`；这些结果均保存原始Episode。

### tune-mjcf · Model-only同题三档实际终局

以下为Seed43独立完整Episode；模型均为GLM，返回Effort未报告，完整账单未知。教师请求发出与实际短评消费分列。

| 策略 | 原官方结果 | 已报模型Token | 已知模型参考USD | 未知费用请求 | 生成／工具 | 教师请求／消费 | Harbor秒 |
|---|---|---:|---:|---:|---:|---:|---:|
| [原始Laya ON Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/laya_original_on_model_only_low/43/summary.json) | 0、1过3败 | 1022 | 0.00016135 | 2 | 2／1 | 0／0 | 1059.214431 |
| [原始Laya ON Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/laya_original_on_model_only_max/43/summary.json) | 1、4断言全过 | 255162 | 0.01837626 | 7 | 20／22 | 5／0 | 1105.180536 |
| [训练Laya ON Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/laya_trained_on_model_only_low/43/summary.json) | 1、4断言全过 | 138278 | 0.00734119 | 5 | 21／22 | 5／0 | 745.742216 |

原始Low首个请求遇到33次连接拒绝，累计等待871秒后恢复HTTP200/tool_calls；第二请求到原期限结束，原有效0保留。Max第14个请求遇到RemoteDisconnected，额外1次恢复工具生成；两个成功Episode的五次教师响应均401、消费0。训练OFF Low/High的Luna请求中断分别保留无有效评分及首次记录，沿原技术恢复；不将这两个位置补0。Max与训练Low的成绩来自实际生成及原Verifier，教师有效贡献尚缺可用短评对照。

训练Kev的同题结果如下，五个成功Episode均4项断言全过、0重试；均为单次Trial。成功组生成实际使用Terra对应档位，模型费用完整、供应商及资源实收未知。

| 教师与Effort | 原官方结果 | 单次模型Token | 模型参考USD | 教师请求／消费 | 生成／工具 | Harbor秒 |
|---|---|---:|---:|---:|---:|---:|
| [OFF Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/kev_trained_off_model_only_low/43/summary.json) | 1 | 59637 | 0.01709860 | 0／0 | 8／8 | 438.048112 |
| [OFF High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/kev_trained_off_model_only_high/43/summary.json) | 1 | 135413 | 0.02849540 | 0／0 | 15／17 | 551.775692 |
| [OFF Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/kev_trained_off_model_only_max/43/summary.json) | 1 | 174445 | 0.05986340 | 0／0 | 14／26 | 615.139110 |
| [ON Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/kev_trained_on_model_only_low/43/summary.json) | 1 | 153536 | 0.02514560 | 4／0 | 17／17 | 536.515907 |
| [ON High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/kev_trained_on_model_only_high/43/summary.json) | 1 | 152642 | 0.02957480 | 4／0 | 16／17 | 640.273473 |
| [ON Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/tune-mjcf/kev_trained_on_model_only_max/43/summary.json) | Luna401中断、缺有效分 | 12921已知 | 0.00696740已知 | 0／0 | 3／7 | 276.907258 |

OFF三档实报缓存读取49792／121088／150528 Token、各0缓存缺测，物理KV共享未知；Router墙钟97.063／164.537／162.415秒、实际GPU等待0.022／0.040／0.035秒。该题OFF三档同质量时Low模型参考费最低，Max为Low的3.50倍；ON Low/High的四条教师均401且未消费。ON Max先执行2次Terra Max，再选Luna Max并遇401，缺1请求费用；原始Kev六组也均Luna401缺分，训练前后仍缺两侧有分的同题比较。

最新导出末次终局2026-11-16T18:14:46.868959+00:00：Model-only1322/2136结束，300官方1、166官方0、824缺有效评分、32项Verifier依赖故障另列；1运行、813未开始。1323 Trial，模型与教师已知参考费$16.37566595、1032请求费用未知、4206额外重试。联合261/957保持84官方1、55官方0、122缺分、696 Router位置未开始；历史1513位置、2599 Trial保持308官方1、344官方0、795缺分及66项依赖故障。原有限队列仍等待Model-only结束，再执行技术恢复、联合Router及联合／历史恢复。

| caffe-cifar-10 Seed43已结束位置 | 评分状态 | 已报模型Token | 已知模型参考USD | 额外重试 | 单次Harbor秒 |
|---|---|---:|---:|---:|---:|
| [原Laya OFF Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_original_off_model_only_low/43/summary.json) | Luna请求故障、缺有效分 | 0 | 未知 | 0 | 117.732216 |
| [原Laya OFF High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_original_off_model_only_high/43/summary.json) | Luna请求故障、缺有效分 | 0 | 未知 | 0 | 121.649165 |
| [原Laya OFF Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_original_off_model_only_max/43/summary.json) | Router决策超时、缺有效分 | 20987 | 0.00302089已知 | 7 | 1307.673302 |
| [原Laya ON Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_original_on_model_only_low/43/summary.json) | Luna 401、缺有效分 | 0 | 未知 | 0 | 105.505917 |
| [原Laya ON High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_original_on_model_only_high/43/summary.json) | 首次生成前路由超时、缺有效分 | 0 | 未知 | 0 | 1301.860888 |
| [训练Laya OFF Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_trained_off_model_only_low/43/summary.json) | 首次生成前路由超时、缺有效分 | 0 | 未知 | 0 | 1299.298292 |
| [原Laya ON Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/caffe-cifar-10/laya_original_on_model_only_max/43/summary.json) | 首次生成前路由超时、缺有效分 | 0 | 未知 | 0 | 1303.308547 |

上述七项保存的原始`official_reward`均为0，任务质量单列技术故障；该段记录11-16现场。Caffe现24组已结束，其中Kev12组均因CUDA显存不足缺有效分，原始异常、Token与费用保留，沿原技术恢复入口接续。

11-16 11:22:56原联合固定261位置全部结束，闲置3205488／3575811退出；六任务固定恢复于12:00:58结束。3993622等待实际Model-only1696641，再按原顺序执行Model-only技术恢复、696联合Router及联合／历史恢复；前两题原有分结果直接复用。

以下为本次独立恢复Episode，Token与费用按该episode_id的原事件计量；位置累计费用仍在逐Episode表另列：

| Seed42固定Terra High恢复 | 官方结果 | 单次已报模型Token | 单次模型参考USD | 单次生成／工具结果 | Harbor秒 |
|---|---|---:|---:|---:|---:|
| [pytorch-model-cli](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/trials/pytorch-model-cli/terra_high/42/summary.json) | 1、6断言全过 | 103531 | 0.04923340 | 11／17 | 341.119623 |
| [torch-pipeline-parallelism](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/trials/torch-pipeline-parallelism/terra_high/42/summary.json) | 0、2过2败 | 519485 | 0.09868260 | 34／34 | 841.559595 |
| [query-optimize](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/trials/query-optimize/terra_high/42/summary.json) | 原Verifier超时、无分 | 64663 | 0.02393660 | 9／12 | 1158.164856 |

三个新Episode全部生成请求HTTP200、0重试，用量齐全；供应商与资源实收未知。Pipeline的lm_head反向梯度最大差0.03571479767560959，原断言2失败，保留有效0。Query原6包安装0.962秒后收集6测试，900秒Verifier结束前无测试结果；停点仍缺内部阶段记录，不据此手工评分。历史累计恢复266次、涉及196位置，原2333首次Trial保持。

[winning-avg-corewars／GLM Low](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/winning-avg-corewars/glm_low/43/summary.json)成为第4个输出额度终止位置：请求4096、返回报告128000输出/127999推理、length、0重试，单请求1905403.192毫秒；原Verifier0保留，质量单列PROVIDER_OUTPUT_BUDGET_EXCEEDED。该次已报603867 Token、模型参考$0.11520320、3263.207275秒；原恢复规则仍保留已评分0，不重跑。

逐策略质量、费用、缺测及全部尝试详见本批review.md与metrics/per_episode.csv。

三个GLM Low完整Episode的末次请求max_tokens=4096、thinking.enabled、stream=false，返回completion_tokens=128000、finish=length、0额外重试。已进入原官方Verifier；质量栏单列PROVIDER_OUTPUT_BUDGET_EXCEEDED，原Reward0及全部费用保留，原自动恢复理由仍为None。

| 完整Episode | 单次已报模型Token | 模型参考USD | Harbor秒 | 超额请求 |
|---|---:|---:|---:|---:|
| [custom-memory-heap-crash](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/custom-memory-heap-crash/glm_low/43/summary.json) | 160910 | 0.06779314 | 1781.260825 | 1 |
| [dna-assembly](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/dna-assembly/glm_low/43/summary.json) | 217850 | 0.07425886 | 2399.466770 | 2 |
| [protein-assembly](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/protein-assembly/glm_low/43/summary.json) | 736623 | 0.09387332 | 1792.998447 | 1 |

原请求参数符合[智谱现行max_tokens说明](https://docs.bigmodel.cn/cn/guide/start/concept-param)，实际渠道未落实4096；返回Effort、物理后端及供应商实收未知。当前三个批次分别记录99／32／239次超额输出请求，只有上述3个额度终止位置因此另列；正常额度内length原0保持。分析807行，观察123359／123360／123364已加载，公开汇总沿原.runtime导出，不采用旧Controller内存分类。

07:52读取原请求逐尝试：circuit-fibsqrt／Terra High／seed43的bddd548f共101个HTTP502，最后attempt_index=100、RETRY_LIMIT；保持High／4096，1次逻辑生成、0工具执行，Harbor3091.824703秒，原Verifier0保留、质量另列请求故障、用量及账单未知。sqlite-db-truncate／训练Kev OFF Low的33127bdf共33个HTTP502、额外32次后TASK_DEADLINE，未执行工具；原0单列技术故障。100次是上限，原任务时限仍实际生效。

| Seed43策略与完整Episode | 官方结果 | 已报模型Token | 已知模型参考USD | 未知费用请求 | 生成／工具结果 | Harbor秒 |
|---|---|---:|---:|---:|---:|---:|
| 固定GLM Low · [distribution-search](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/distribution-search/glm_low/43/summary.json) | Reward1 | 61571 | 0.00519298 | 0 | 10／10 | 307.655962 |
| 固定GLM Low · [circuit-fibsqrt](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/circuit-fibsqrt/glm_low/43/summary.json) | Reward0、2过1败 | 24309513 | 0.86166677 | 2 | 214／213 | 3717.727741 |
| 原始Laya OFF Max · [sqlite-with-gcov](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/sqlite-with-gcov/laya_original_off_model_only_max/43/summary.json) | Reward1 | 630540 | 0.03194931 | 0 | 42／55 | 1260.019631 |
| 原始Laya ON Max · [sqlite-with-gcov](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/sqlite-with-gcov/laya_original_on_model_only_max/43/summary.json) | Reward1 | 535611 | 0.02697806 | 5 | 31／50 | 1207.770084 |
| 训练Laya OFF Max · [sqlite-with-gcov](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/sqlite-with-gcov/laya_trained_off_model_only_max/43/summary.json) | Reward1 | 664280 | 0.03764832 | 2 | 36／64 | 988.808875 |
| 固定Terra High · [install-windows-3.11](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/install-windows-3.11/terra_high/43/summary.json) | Reward0 | 748312 | 0.12139280 | 0 | 44／44 | 1153.148129 |
| 固定GLM Low · [install-windows-3.11](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/install-windows-3.11/glm_low/43/summary.json) | Reward0 | 9953346 | 0.36045462 | 2 | 214／215 | 3719.577577 |
| 固定GLM Low · [mteb-leaderboard](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/mteb-leaderboard/glm_low/43/summary.json) | Reward0 | 341391 | 0.01760725 | 0 | 52／54 | 1600.047511 |
| 固定GLM Low · [portfolio-optimization](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/portfolio-optimization/glm_low/43/summary.json) | Reward1 | 149167 | 0.01042787 | 0 | 20／20 | 780.787958 |
| 固定Terra High · [regex-chess](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/regex-chess/terra_high/43/summary.json) | Reward1 | 88198 | 0.04795480 | 0 | 6／6 | 355.578624 |
| 固定GLM Low · [reshard-c4-data](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/reshard-c4-data/glm_low/43/summary.json) | Reward1 | 194477 | 0.01215579 | 1 | 24／27 | 766.649811 |

SQLite/gcov原始ON Max的5次教师请求均为HTTP401、new_api_error/invalid token，0额外重试、短评消费0；唯一配置与原Model-only/有限接续的Luna绑定相同。三组生成均选GLM Max并得到原官方1，返回Effort未报告；训练OFF已知模型费高于原始OFF，另2请求费用未知。Terra Windows44次、regex-chess6次均HTTP200且请求/返回模型及High一致，0重试；后者官方1，前者官方0，服务生成恢复与任务质量分列。

电路任务test_sqrt_fib失败，文件存在及尺寸两项通过；214次真实生成及213次工具执行后的有效0保留，不作技术恢复。SQLite/gcov的Model-only原始Laya Max全部42次生成选择GLM Max，实际官方Reward1；返回Effort未报告。已报Token是每次完整Episode中所有请求的输入加输出，包含重复上下文；缺用量或账单保持未知。

raman-fitting／训练Kev教师ON／seed43完整三档结果，额外重试均0；教师消费均0、教师费用未知，模型费用只列已知参考部分：

| Effort与完整Episode | 官方有效质量 | 原断言通过／失败 | 实际选择 | 已报模型API Token | 模型参考USD | 生成／工具结果 | Harbor秒 |
|---|---:|---:|---|---:|---:|---:|---:|
| [Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/raman-fitting/kev_trained_on_model_only_low/43/summary.json) | 1 | 3／0 | Terra Low | 57905 | 0.017749 | 8／8 | 330.452390 |
| [High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/raman-fitting/kev_trained_on_model_only_high/43/summary.json) | 缺分：生成403 | 1／2，原0保留 | Terra High、Luna High | 71848 | 0.0236424 | 10／9 | 966.932015 |
| [Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/raman-fitting/kev_trained_on_model_only_max/43/summary.json) | 0 | 1／2 | Terra Max | 174888 | 0.0928536 | 11／20 | 1151.020477 |

Max的G与2D峰值两项失败、有效0保留，模型参考费为Low的5.23倍；High第10条Luna生成403后结束，单独技术恢复。Low／High／Max的Router墙钟82.879958／103.521921／111.542919秒、GPU等待0.023336／0.025692／0.028904秒，教师请求2／3／3次，消费均0。03:51 Model-only教师ON已结束504位置：246实际消费短评、15发出教师请求但消费0、243未触发请求；没有把所有ON配置直接解释为有效教师干预。

新增两项Terra High／seed43完整Episode均获官方1，额外重试0、请求用量齐全；供应商和资源实收未知：

| 官方任务与完整Episode | 单次模型API Token | 模型参考USD | 生成／工具结果 | Harbor秒 |
|---|---:|---:|---:|---:|
| [FEAL差分密码分析](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/feal-differential-cryptanalysis/terra_high/43/summary.json) | 26838 | 0.0171108 | 4／4 | 354.964261 |
| [FEAL线性密码分析](rq1/terminal-bench-2.0/20261112-v9-joint-paired/trials/feal-linear-cryptanalysis/terra_high/43/summary.json) | 73172 | 0.0349608 | 7／7 | 207.012172 |

filter-js-from-html两条固定Seed43 Episode缺官方评分：Terra High的94690280、GLM Low的aa1287ab均在原900秒Verifier到期；24包分别安装1.41／1.76秒，2项测试已收集，内部阶段耗时未保存。该题历史17位置也均缺有效评分，其中8个VerifierTimeout、9个HTTP错误；当前Model-only原24组尚未开始。

沿原镜像alexgshaw/filter-js-from-html:20251031的一次网络／浏览器准备及一次原退出顺序观察：Selenium4.38.0、Chromium／Driver140.0.7339.127，417条外部XSS样例的原GitHub归档136398字节下载成功，浏览器真实启动；按原先kill再quit仅耗0.007877秒。两次准备均用1CPU／2GiB并自动移除容器，原镜像供原24组保留；这两项为依赖运行数据，完整Episode质量仍为空。下一实际任务的Verifier内部阶段与进程状态用于定位停点，不改测试或时限。

02:50现行分析e1cb909b补计未返回的Router墙钟：同一已结束Trial的ROUTER_START至AGENT_END；原始Laya ON Low／High实际899.873759／899.806012秒，原汇总均为0。CPU、GPU等待和传输细分缺测为空，Router用量缺测各1次；原官方评分及API费用保持。当前三个20分钟观察4041864／4041865／4041866沿相同目录导出。

constraints-scheduling／seed43同题两个固定策略均官方1、0额外重试；GLM原3断言全过，该题保持已观察身份。完整供应商和资源实收未知：

| 固定策略 | API Token | 模型参考USD | Harbor秒 |
|---|---:|---:|---:|
| GLM Low | 18084 | 0.00311024 | 914.282028 |
| Terra High | 21475 | 0.01035980 | 268.264976 |

raman-fitting／训练Laya OFF／Model-only Max／seed43的d57bf31d完整Episode：9次生成请求，8次GLM Max成功响应均为合法工具调用、10次工具结果；最后单次读超时达到原期限。原官方3断言均因/app/results.json缺失失败、Reward0保留；已报30868 API Token、1请求费用未知、1564.903406秒。GLM返回模型ID匹配，返回Effort未报告；该次延迟的模型与网络贡献未知。

01:36原17898代理已退出，重建同一转发后HTTPS200。02:00原主接续1700006已退出，闲置队列替换为3993622，等待实际Model-only1696641并明确接续原696个联合Router位置；三个当前源码观察每1200秒导出，02:22的98294已自然接管代理。模型与教师仍沿Provider最多额外100次同参数重试，原期限有效。三批总量及剩余位置见[项目现状](../../planning/PROJECT_STATUS.md)，逐尝试费用、失败和首次日志保留。

02:15新增资源事实：gpu.lock为共享READ锁，H3调度GPU46506MiB、Native396MiB、可用844MiB；raman-fitting的原始Laya教师ON Low／High均在路由返回前耗尽900秒、0生成请求，任务质量空值。已有10个该类缺分位置，按原Model-only技术恢复另存。

tune-mjcf／GLM Low／seed43的真实重试恢复：操作6经17次额外重试、操作8经2次额外重试后均HTTP200／tool_calls，同模型、Low、4096及原输入继续使用；原Episode完成19次工具结果。官方3过1失败，模型／参照平均模拟0.9689／0.9702秒，运行比99.87%高于原要求60%，任务Reward0保留。已报90572 API Token、2请求费用未知、完整1050.151585秒；官方断言41.65秒，参照未改及正确性均通过。

新增四个独立Episode取得官方1，均0额外重试、已报用量齐全；完整实收与资源费未知：

| 官方任务 | 固定策略 | 单次API Token | 参考USD | Harbor秒 |
|---|---|---:|---:|---:|
| vulnerable-secret | GLM Low | 26697 | 0.00201665 | 131.061448 |
| write-compressor | Terra High | 40391 | 0.01404060 | 163.377804 |
| break-filter-js-from-html | GLM Low | 44970 | 0.00652809 | 299.848437 |
| code-from-image | GLM Low | 369090 | 0.01913643 | 753.950518 |

write-compressor／GLM Low／seed43的新07d68a58为有效官方0，原测试3项均因/app/data.comp不存在失败，原失败不重跑；已报498378 API Token、1请求费用未知、完整1106.647503秒，完整参考费用为空。

联合Seed43新增两题固定模型对照；每行一次完整Episode、0额外重试、模型用量齐全，完整实收与资源费未知：

| 官方任务 | 固定策略 | Reward | 单次API Token | 参考USD | Harbor秒 |
|---|---|---:|---:|---:|---:|
| sparql-university | GLM Low | 0 | 302160 | 0.01179221 | 1037.150976 |
| sparql-university | Terra High | 1 | 145042 | 0.03639560 | 837.370931 |
| torch-pipeline-parallelism | GLM Low | 0 | 534662 | 0.02614088 | 1314.716340 |
| torch-pipeline-parallelism | Terra High | 1 | 58995 | 0.02819820 | 499.515814 |

pipeline的GLM原官方2过2失败，未提供position_embeddings；其有效0保留。Tensor／GLM Low的5109434f则因17898拒绝连接而无法安装APT与pytest、0断言，原0保留、任务质量空值，沿原技术恢复另存。

query-optimize训练Kev OFF三档均在首条Terra请求收到502，Low／High／Max额外重试31／32／32次，High另有一次TLS握手超时；0工具、无Reward、费用未知。ON Max的c5288b74同为33次502、0工具，原官方2过4失败并给0，任务质量单列技术故障。该次官方断言耗830.57秒；其他记录仍有原900秒无终局，SQL耗时的变化原因未知。原始错误与恢复身份见[资源记录](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)。

## 2026-11-15 · 原Verifier依赖与继续运行

23:11:54原VM切换KVM并恢复同一Controller，16核/40GiB和原任务条件保持；下表两条新Episode的EXECUTION_ENVIRONMENT均记录QEMU3832028、q35,accel=kvm，0额外重试、用量及参考费齐全。供应商、工具及资源实收未知。

| 官方任务 | 固定策略 | Reward | 单次API Token | 参考USD | Harbor秒 |
|---|---|---:|---:|---:|---:|
| nginx-request-logging | Terra High | 1 | 133652 | 0.05708400 | 373.042724 |
| password-recovery | Terra High | 1 | 144375 | 0.06887260 | 463.281778 |

KVM下query-optimize原始Kev OFF High/Max仍在官方首项900秒到期；原6包安装1.00/1.36秒、0工具，两条Luna额度故障与无Reward均保留。旧TCG及新KVM记录分别存储，SQL等待原因仍待定位。

后续读取实际SQLite 3.50.4查询计划：官方原查询1158字节，含3个相关标量子查询和反复SCAN s／SCAN s2；参照golden查询1140字节使用自动覆盖索引。运行中的官方测试容器CPU99.52%、内存99.66MiB，QEMU及其父cgroup的cpu.max均为max 100000。官方日志未分列两条参照SQL耗时；原SQL、测试、900秒及评分保持，未取得Reward的记录继续空值。Luna账号余额查询HTTP403，原账户额度管理权限缺失、备用0。

历史恢复按193个不同位置、248次尝试计数；这些位置最新为51个有效官方1、92个有效官方0、50个缺有效评分。后续恢复由原入口排除已有有效1/0，并对已执行100次机制的未变故障保留原记录。

21:00共享显存：qemu-startup训练Kev ON High／Max两条RuntimeError来自H3占39.02 GiB时的CUDA OOM，原Reward为空，现单列ROUTER_CUDA_OUT_OF_MEMORY。e05caa115ed00e68ba26abf9aed72847440b4fde部署实际模型字节等待与四原实体CPU预加载，原共享锁、时限和权重保持。20:54同一入口切换至3708428，query-optimize原始Laya OFF Max／ON Low真实CUDA前向971.376／976.715毫秒、fallback=false；两条旧故障的恢复结果仍待原队列。

Seed43新增完整任务结果；每行是一次独立Episode，均0额外请求重试、全部API用量及模型参考费已报告：

| 官方任务 | 固定策略 | Reward | 单次API Token | 已知参考费USD | 原Harbor秒 |
|---|---|---:|---:|---:|---:|
| cobol-modernization | GLM Low | 1 | 156242 | 0.01405127 | 658.341350 |
| cobol-modernization | Terra High | 1 | 230080 | 0.09227920 | 650.256645 |
| count-dataset-tokens | Luna High | 1 | 303631 | 0.00964934 | 1549.451421 |
| count-dataset-tokens | Terra High | 1 | 203548 | 0.09986800 | 1035.286717 |
| count-dataset-tokens | GLM Low | 0 | 134200 | 0.00723507 | 1863.041305 |
| merge-diff-arc-agi-task | GLM Low | 1 | 107467 | 0.00949893 | 731.181110 |
| merge-diff-arc-agi-task | Terra High | 1 | 243403 | 0.08158300 | 580.174031 |

count-dataset-tokens的Luna达到原Agent时限后仍获官方1；GLM在27次生成中重复启动安装和等待，最终原官方0。前者的真实模型/High返回匹配，后者的原时限与零分保留；实收、工具和资源费仍未知。cobol/Luna High为403技术终止，费用和用量未知，独立于表内有效成绩。

20:17现行46155662617507f354d85b9a3d7754c334e45cb3让正常4096耗尽保留Harbor原OutputTokenExceededError类别，并经原NonZero捕获路径执行Verifier；服务器实际包的原政策为AGENT_EXHAUSTED_BUDGET、reward_valid=true。真实新长度耗尽Episode仍待原矩阵，不额外发送已知相同失败请求。Luna同端点20:01的High请求completed且返回档位匹配，20:04教师请求仍403；额度故障没有概括为全部模型请求不可达。

19:43 Provider终止后官方评分路径已实际执行：cancel-async-tasks／Luna High／seed43的75dee28d原Verifier158.819613秒返回0；Harbor原非零退出错误政策将其列为未归类故障，质量栏继续空值、PROVIDER_REQUEST_FAILED单列。源码c81a6b8f9597af2eded1eebbb57fc2786afbe458保留真实失败状态、原时限及4096额度，长度耗尽不作网络重试。qemu-startup的原403返回pre_consume_token_quota_failed／token quota is insufficient，现有Luna凭据额度待恢复。

MTEB-retrieve的原Low／High零分由scikit-learn1.9.1和torchvision0.29.2下载超时造成，未执行断言。共享缓存已完成原pytest8.4.1／mteb1.36.8／CTRF0.3.5及其95个实际依赖，原解析出的scikit-learn1.9.1、torch2.15.0、torchvision0.29.2均保留；现行模块复用既有链接安装。MTEB-leaderboard五个固定恢复均取得有效官方0；MTEB-retrieve的Max、Xhigh、Terra亦为有效0，全部保留。reshard-c4-data四个Luna档位及Terra High恢复均取得官方1，原请求、费用与首次失败分开；详情沿历史逐Episode表。

15:39修复后Tensor／Terra High／seed42的[f6d172b1完整Episode](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/trials/torch-tensor-parallelism/terra_high/42/summary.json)已结束，原31包安装17.91秒，13项测试完成前5项后在900秒Verifier期限退出、无Reward。该次14生成请求、148378输入＋3266输出Token、0重试、$0.06207760 API参考费、1390.4198秒；原2次Trial及其费用分别保留，供应商和资源实收未知。依赖安装故障已消除，后续计算等待与生成代码贡献尚未分离。当前QEMU为q35,accel=tcg、16CPU／40GiB；宿主机/dev/kvm存在但syy无读写权限，sudo需密码，管理员设备授权仍缺。原运行条件与有效1/0保持。

14:49共享缓存已补齐官方Torch2.7.0、Transformers4.55.0及原pytest／CTRF共45包；原缓存只有2.7.1，pipeline四个固定恢复位置重复下载约1 GB并安装314—343秒，900秒Verifier到期时没有pytest会话输出。新源码`9b9458eacf683d66c9dde79feff85bdeb6082a46`已部署，两项Torch任务沿现有链接安装方式，原包、官方脚本和时限保持；完整新评分仍待执行。尾段3378616复用同一600权限memfd，等待3205488后恢复CLI、Caffe及两项Torch，五固定策略的有效1/0直接保留；只读观察3380730／3380780与代理等待335跟随新尾段，原主批和健康代理继续。

13:27部署`4b095e5e914f1ebabc850a7cf2724130cb941636`：删除CLI启动链里会触发官方镜像APT清理钩子的重复update；同官方镜像、同源、249个原版本推荐包已经0 B下载完成安装，临时容器自动移除。三项CLI恢复在600秒启动到期，High在410.254秒因183 MB重下载及libmbedcrypto7 HTTP502退出，四项Agent均未开始；完整新评分仍待接续。Caffe Xhigh的11e6497b原HTTP200实际为嵌套server_error/request_timeout、耗131.726秒，旧解析为error且0重试；新协议读取实际错误类型，原保存响应已解析为可重试，沿现有100次上限和原任务时限恢复。两项修复的完整Episode结果保持空值，详情见原[资源记录](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)。

PyTorch recovery／原始Laya／Model-only／教师ON／seed43已新增两条原官方Reward1，各5断言全通过。部署`24ee16e16fd000f3c35915724ee35c1fee5b76eb`后原31包符号链接安装21.97／24.09秒，原900秒Verifier时限保持。此前OFF Low／High安装524秒、pytest全过却无官方Reward的原记录继续空值；恢复另存，其他任务继续copy。下表每行都是一次完整Agent Episode，Token含教师、0额外重试、请求费用齐全；完整实收和资源USD未知。

| 请求Effort | 官方Reward | API Token | 模型＋教师参考USD | Harbor秒 | Verifier秒 | 实报缓存Token | 教师请求／消费决策 |
|---|---:|---:|---:|---:|---:|---:|---:|
| [High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_original_on_model_only_high/43/summary.json) | 1 | 92728 | 0.00462992 | 1236.957864 | 484.955602 | 67712 | 4／7 |
| [Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_original_on_model_only_max/43/summary.json) | 1 | 126182 | 0.00869508 | 1422.129829 | 545.536811 | 85248 | 5／4 |

两条17／18次生成均选择Luna对应档位；Router耗时18.461／19.718秒。历史四个CLI缺分优先恢复由有限3205488接续，已有Luna Max有效评分保留；CLI APT缓存下完整官方结果仍待运行。

同题训练Laya／seed43已完成五个独立Episode；下表全部0额外重试、请求消费齐全，仍沿原官方评分。

| 教师 | 固定Effort | 官方Reward | 断言通过／失败 | API Token | 参考USD | Harbor秒 | Verifier秒 | 实报缓存Token |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| OFF | [Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_trained_off_model_only_low/43/summary.json) | 0 | 1／4 | 105798 | 0.00302812 | 1062.990163 | 386.011757 | 93312 |
| OFF | [High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_trained_off_model_only_high/43/summary.json) | 1 | 5／0 | 181481 | 0.00571962 | 1829.313692 | 773.068765 | 157312 |
| OFF | [Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_trained_off_model_only_max/43/summary.json) | 1 | 5／0 | 161957 | 0.01017346 | 1588.327147 | 543.730255 | 126336 |
| ON | [Low](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_trained_on_model_only_low/43/summary.json) | 0 | 1／4 | 31430 | 0.00211812 | 768.786837 | 343.688458 | 17792 |
| ON | [High](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_trained_on_model_only_high/43/summary.json) | 1 | 5／0 | 64152 | 0.00441104 | 1091.029489 | 488.157664 | 38144 |
| ON | [Max](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-recovery/laya_trained_on_model_only_max/43/summary.json) | 1 | 5／0 | 208484 | 0.01226528 | 1635.199286 | 561.483209 | 已知153280；1请求缺值 |

Low的OFF／ON均缺少任务要求的/app/model.pt，有效0不重跑；ON Low的3条Luna短评进入4次决策。High两侧同为官方1，ON的4条短评进入7次决策，14次生成均选Luna High；ON相对OFF参考费减少22.88%、API Token减少64.65%、墙钟减少40.36%。生成模型与档位相同，教师效应与轨迹差异尚未分离。OFF High／Max的27／25次生成均选择Luna对应档位，原31包安装32.63／21.02秒。汇总源码3f57521fe0ddb5281fab9e71dbde75d2d894c0e8将29项缺CTRF报告明确列出，原11项无异常字段的日志已确认pytest下载TLS中断；其余记录保留原Agent时限异常字段，质量分母保持原范围。

10:23同一依赖目录的真实APT缓存完成249包：183211524字节包文件、19838946字节索引，临时准备容器已移除。新部署`f1828108ee189b94790ca84ebc81d7bae235ace0`在原CLI启动链复用签名包和索引，原版本、推荐依赖和600／900秒时限保持。此前无缓存预装的教师ON High／Max两项因600秒启动到期未开始Agent，均缺评分。现有限3195433优先四个历史固定CLI缺分位置，已有Luna Max有效评分保留；尚待新缓存下完整官方结果。

09:29新部署`1e42cfcd4045e08bdf71e87ab9c07678469adcfa`仅提前准备PyTorch CLI原Verifier四个系统包，原600秒环境启动、900秒Agent和900秒Verifier时限保持。训练Kev OFF Low原Agent改回deb.debian.org，Verifier下载124 MB耗时313秒，20个Python包安装20.29秒后到期、无Reward；原日志和费用保留，纳入原技术恢复。新部署后完整评分尚待原队列自然结束。

训练Kev OFF High的[完整Episode](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-cli/kev_trained_off_model_only_high/43/summary.json)获得官方1／6断言全通过；20次生成均选Terra High且返回匹配，0额外重试，231713 API Token、$0.08868740参考费、1649.580秒。同题同Seed的原始Kev OFF High也为官方1；训练版参考费33.19倍、Token7.61倍、墙钟增加21.04%，完整实收与资源USD仍未知。

历史regex-chess／seed42恢复：Terra High官方1／4断言全通过，已知1014871 API Token、$0.330015参考费、1请求消费未知、20次额外重试；Luna Max官方0／1断言通过3失败、1811182 API Token／$0.09110628／3993.733秒、0重试。video-processing／Luna Low亦获有效0／3过2失败，API32056 Token／$0.00218080／512.239秒，原失败不重跑。

2026-11-16 00:36当前源码[采集](rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)：Model-only结束980/2136位置，259通过、148有效失败、541缺有效评分、32依赖故障另列，2运行、1154未开始；981次已结束Trial，模型与教师已知参考费$14.53038187，598请求缺费用，2285次额外重试。联合114/957结束、45通过／29有效失败／40缺评分，4运行、839未开始，$3.67092664模型参考费、44请求缺费用、176额外重试。历史00:37采集为1513位置、2581次Trial，307通过、343有效失败、797缺评分、66依赖故障另列，$41.94341055模型与教师参考费、1083请求缺费用、765额外重试；193个不同位置共248次恢复尝试，原2333次首次Trial保留。 联合原两题seed43复用。

同题原始Kev／seed43六项现均取得完整官方评分，额外重试仅ON High为1次，其余0次；全部生成选择Luna对应档位。教师Low由官方0变1，High和Max均1；Max教师ON参考费比OFF减少20.07%，Low增加13.23%，High失败请求用量未知，完整API费用为空。训练Laya ON Max有24次生成、5条Luna短评进入9次决策，实际22次Luna Max与2次GLM Max、4次模型切换；0额外重试、原官方1，GLM返回档位未报告。

| 原始Kev固定Effort | OFF／ON官方Reward | OFF API Token | ON已知API Token | OFF参考USD | ON参考USD | OFF／ON Harbor秒 |
|---|---|---:|---:|---:|---|---|
| Low | 0／1 | 55719 | 45940 | 0.00301830 | 0.00341752 | 1149.130288／1172.906423 |
| High | 1／1 | 68712 | 70984；1请求缺值 | 0.00379064 | 完整未知 | 1321.411138／1521.086555 |
| Max | 1／1 | 78986 | 53610 | 0.00578036 | 0.00462036 | 1317.602951／1218.662072 |

训练Kev同题OFF Low／High也均取得官方1、5断言全过、各16次Terra生成、请求与返回档位匹配、0重试。Low为115800 API Token／$0.07301040／1136.175754秒，High为133413 API Token／$0.06613140／1100.046006秒；High与原始Kev同为1而参考费17.45倍，Low由原始0变1而参考费24.19倍。原始及训练权重、任务与Seed43保持，时间和生成轨迹的影响分别保留。

该题24位置已全部结束：17有效官方1、3有效0、4缺有效Harbor评分。原始Laya OFF Low／High的原reward.txt各为1，Harbor的verifier_result为空且记录VerifierTimeout，质量栏继续空值；另两项无Reward文件。训练Kev六组均为1，教师OFF／ON Max参考费$0.26273080／$0.17626360，分别479990／241969 API Token及1576.841558／1362.764096秒；ON有4条短评进入9次决策，0重试。OFF Max与原始Kev同为1，训练版参考费45.45倍。训练Kev ON High为120564 Token／$0.04423770／1082.017424秒，4条短评进入5次决策；ON Low为210170 Token／$0.06587840／1435.448578秒，7条短评进入11次决策。完整实收和资源USD仍未知。

query-optimize的Luna Max／Terra High恢复已完成APT及6包安装、收集6项官方测试，随后到900秒仍无终局，两项缺评分；SQL执行与CPU TCG耗时尚未分离。原日志、请求、费用与时限保留，沿原入口继续其他任务。

PyTorch CLI原始Kev／seed43六项独立完整Episode均获官方1、各6断言全通过、0额外请求重试；全部生成请求均选择Luna并返回相同Effort。下表每格对应一次完整任务，Token与参考费包含教师；供应商实收和完整资源费用未知。

| 固定Effort | OFF／ON官方成绩 | OFF API Token | ON API Token | OFF参考USD | ON参考USD | OFF秒 | ON秒 |
|---|---|---:|---:|---:|---:|---:|---:|
| Low | 1/1／1/1 | 42536 | 70317 | 0.00243552 | 0.00738554 | 1462.410 | 1363.091 |
| High | 1/1／1/1 | 30456 | 134173 | 0.00267200 | 0.00757378 | 1362.795 | 1870.816 |
| Max | 1/1／1/1 | 290242 | 90507 | 0.02582876 | 0.00739982 | 1923.992 | 1654.305 |

该题教师Low／High参考费增加203.24%／183.45%，Max减少71.35%；Low／Max墙钟缩短6.79%／14.02%，High增加37.28%。ON Low／High／Max的2／5／2次Luna短评分别进入2／5／5次决策，短评实际复用。89题的成对总体收益仍待原矩阵完成。

reshard-c4-data与build-pov-ray原镜像已通过Docker Hub官方registry.hub.docker.com恢复原alexgshaw标签，分别4,235,256,296／579,715,713字节；临时域名标签已移除、镜像层保留。前者五固定位置原TLS EOF，后者17历史位置原代理拒绝，Agent均未开始。现有限3205488已将两题与其余五项依赖／镜像恢复合并，固定4并发、Router2并发；原任务、Seed、时限及评分保持。

新增缺分实际来自只读UV缓存和解释器安装标记写入，未执行任务断言。现有环境类已改为母缓存只读绑定、每题元数据和107MiB解释器可写；不再复制6.0GiB全部依赖。三个精确NumPy／PyTorch缓存安装完成，原包版本和官方脚本保持；旧无断言Reward0另列依赖故障并进入同条件恢复。

缓存根软链接实际导致uv安装的os error 20；`71175861313c90def9f23b5bc3c3290d7c48e0e9`使用原Harbor逐目录只读挂载替换软链接，并以copy方式安装轮子，原官方脚本保持。break-filter-js-from-html／Luna High／seed42已完成52挂载的新Episode：有效Reward0、1断言失败、11991 API Token／$0.00182214参考费／398.950095秒；HTML未绕过过滤器，有效0保留。Controller1696641／历史固定恢复2509357并行推进，原Router两并发与固定四并发保持；3205488等待固定恢复结束后单独恢复Caffe Xhigh无评分项，再恢复已修复依赖、两项MTEB、reshard-c4-data及build-pov-ray位置并接续联合矩阵。H3／Router共享原GPU锁的真实同视频前向记录、原VM磁盘在线扩容及当前接续PID见[资源记录](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)。GLM仍按相同模型和档位最多额外100次请求重试至原期限。

pypi-server／seed43全部24组结束：Laya原始、训练及原始Kev各6组共18个官方1，额外重试均0；训练Kev六组累计186次额外重试、生成0次到原期限，原Verifier0保留、质量另列请求故障，费用未知。原始Laya OFF／ON High分别53044／54725 API Token、$0.00385200／$0.00497218参考费、534.423／517.475秒，ON High的2次Luna教师短评进入4次真实Router决策。原始OFF Max有20次GLM工具生成、132324 Token、$0.01906652、1099.075秒，返回Effort未报告。训练Laya ON Max有26生成请求／7教师、14次短评消费，最后GLM请求在原期限单次读超时，但原Verifier给1；该请求消费未知，完整模型费用为空。每项均保存原始完整Episode和官方评分。

两项MTEB官方镜像均已准备：mteb-retrieve 21,556,522,773字节、mteb-leaderboard 21,623,437,997字节，Linux/amd64、原alexgshaw标签。临时registry.hub.docker.com域名标签已移除，镜像层保留。各五个原固定技术故障位置等待现有限3031707接续；首次TLS EOF、原时限与Verifier保持。

f1ae75923db3479b0b8006165db4342ce3144eda已处理PyTorch CLI真实APT锁竞争与缺libGL.so.1。训练Laya／教师OFF／Low／seed43的[完整Episode](rq1/terminal-bench-2.0/20261112-v9-model-only/trials/pytorch-model-cli/laya_trained_off_model_only_low/43/summary.json)取得原官方Reward1、6断言全通过；41生成请求、0额外重试，405103已知API Token、$0.01924296已知参考费，1请求消费未知。完整墙钟2122.637秒；Agent原900秒到期后Verifier896.565秒完成，断言执行213.48秒。旧collecting阶段超时原因仍未知，原失败日志继续保留。

ab4dadb4e8dd4ad85913f9466e7222a846da1f7d只将PyTorch CLI原20包安装改为UV符号链接，其他任务继续copy。真实旧安装复制171／196秒，pytest收集时CPU执行、235240kB／16线程，CV2、NumPy及Torch已加载；UV等待该Python子进程。旧Low和训练Max的分钟级复制后无断言超时沿原入口记录VERIFIER_PACKAGE_COPY_TIMEOUT，已有官方1继续复用。新容器11a5d54bb2d5已确认symlink及libgl1 1.6.0-1，完整官方结果见下文；原包、评分和时限保持。唯一源码回退包保存链接变更前f1ae源码。

PyTorch CLI训练Laya／Model-only Max／教师ON／seed43的51264b19-5164-4310-a0ea-3f58cf24f0fc于07:33结束，原官方Reward1、6断言全通过；20个原包安装19秒，断言272.76秒，Verifier869.766秒，完整墙钟2098.123秒。23生成请求中22成功，18次选择GLM Max含1次原期限读超时、5次Luna Max均报告Max匹配；5次Luna Low教师请求进入13次Router决策。已报380851 API Token，1请求消费未知；已知模型与教师参考费$0.02842038，完整费用为空。已报缓存读取286016 Token、3记录未报，Router25.036秒、输入截断0。GLM返回Effort仍未报告，旧Luna Max→xhigh记录保持。新链接方式已取得完整官方结果，两项MTEB镜像原标签均已恢复、临时域名标签已移除。

pypi-server／原始Kev三档的教师费用对照如下；各组均单独完成Episode并获官方1，表内API Token包括教师。High／Max教师开启后的参考费分别减少40.04%／49.60%，Low增加3.45%；完整现金和资源费用仍未知。

| 固定请求Effort | OFF API Token | ON API Token | OFF参考USD | ON参考USD | OFF秒 | ON秒 |
|---|---:|---:|---:|---:|---:|---:|
| Low | 17509 | 11926 | 0.00150882 | 0.00156092 | 465.478 | 437.243 |
| High | 29211 | 13387 | 0.00274014 | 0.00164302 | 534.150 | 418.850 |
| Max | 71958 | 30009 | 0.00760772 | 0.00383410 | 779.433 | 551.458 |

852位置快照的486个缺有效评分中：352连接错误、39重试至原期限、26Provider响应异常、22其他Agent时限异常、11未记录异常、8Verifier超时、8HTTP异常、7路由决策超时、5首次路由超时、5环境启动超时、2提前断连、1JSON解析异常；31个评分依赖故障另列。统计来自逐Episode原字段，恢复队列仅处理技术故障。

dna-assembly／seed42的五个固定恢复Episode均已调用原Verifier。Luna Low／High／Max／Xhigh分别12／18／22／22次正常生成、0请求重试，取得有效官方0：Low／Max缺引物文件，High缺BsaI位点，Xhigh退火长度47超原45上限；Max／Xhigh到原1800秒，官方断言仍执行完成。Terra High首请求61次HTTP502、60次额外重试，生成0次到原1800秒，原Verifier0保留、质量单列请求故障。上述有效0不再次运行。

dna-insert／Luna Xhigh／seed42恢复后27次正常生成、28个工具结果、0请求重试，原Verifier因正向引物退火长度56超45给有效0；同题Terra High首请求62次502、61次额外重试、生成0次到原期限，原0另列请求故障。extract-moves-from-video／Luna High／seed42为5次正常生成、5个工具结果、0重试，缺solution.txt导致原2条断言失败、有效0。原失败尝试及此次各自独立Episode同时保存。

feal-linear-cryptanalysis／Luna High／seed42恢复Episode05771305-e9b2-4d0a-9d8b-c1156a0c665a获官方1，9次正常API请求、59887输入／2866输出、合计62753 Token，0重试、495.133437秒、新Episode参考费$0.00500250；三次独立尝试合计参考费$0.00803862，先前两次记录保留。供应商实收与资源美元价仍未知。

## 2026-11-14 · GPU共享并发与技术恢复

H3状态文件写入已纳入原锁，闲置Gateway按授权重启，原Model-only两项已在20:06自动接续。现有GPU锁文件保持，H3和Router前向共享读锁，训练和Breeze语音继续独占；原固定模型4并发、Router2并发。Gateway2495490、原生Router2496626运行，四权重及正式比较条件沿原配置。故障日志、实际进程接续、35条H3旧状态的保留位置及唯一回退包见原[资源记录](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)。

795个已结束位置中的466个缺有效评分按原异常类型为：连接错误352、Agent时限异常58、Provider响应异常26、HTTP异常8、Verifier时限异常8、提前断连2、JSON解析异常1、未记录异常11；20个依赖故障另列。原312个代理连接拒绝属于连接错误子集。恢复只处理实际技术故障，原101个有效官方0保留；当前GLM仍有503，模型请求保持原参数及最多额外100次重试、原任务时限。唯一私有配置与批次memfd相同，具体渠道后端原因未知。

22:45当前源码汇总：Model-only813/2136结束，211通过／107有效失败／475缺有效评分／20依赖故障；2运行、1321未开始。已知API参考费$10.70904116、522请求费用未知、额外重试1730次。polyglot-rust-c原始Kev教师OFF Low完成11次Luna Low生成、0重试、原官方0，API参考费$0.00690442；有效失败保留。当前源码的20分钟观察复用原同批导出目录ac90l478；原模型、Effort、权重、Seed43及时限保持。

该题训练Kev OFF Low／OFF High／ON Low新增官方Reward1，模型＋教师参考费分别$0.06138720／$0.02934720／$0.03223330，三条请求费用齐全、额外重试0；各次完整任务API Token60440／33808／59141，ON Low实际教师请求2次。OFF Low与High分别9／5次生成，保留各自原工具、请求与Verifier记录。

历史两个Luna High／seed42连接故障位置已独立恢复；下面只计各自新完整Episode，原失败记录和费用另存，完整实收与资源费用未知。

| 恢复任务 | 官方Reward | 官方断言通过／失败 | API Token | 新Episode参考USD |
|---|---:|---:|---:|---:|
| headless-terminal | 1 | 7／0 | 14849 | 0.00204818 |
| count-dataset-tokens | 0 | 0／1 | 394286 | 0.01317300 |

两项共45次正常Luna High请求、0额外重试、实报缓存读取316288 Token。count-dataset-tokens在原900秒后仍缺answer.txt，原Verifier有效0保留；Debian依赖下载虽较慢，原脚本最终完成并输出CTRF。固定模型恢复已沿原入口继续Luna Low/High/Max/Xhigh及Terra High的历史技术故障，最多4并发。14:35 UTC快照较本轮前2354次已结束Trial增加32次，取得19个有效1、12个有效0、1个评分下载超时；累计2386次Trial、277通过／269有效失败／869缺评分／94依赖故障，4项运行。旧1513位置身份和2333次首次Trial保留。当前汇总入口在恢复运行中保留旧已结束Trial与费用，尚未结束的时间记录不混入完成时长。seed42不写入seed43配对结果。

`model-extraction-relu-logits/Luna Xhigh`原Verifier停在NumPy2.3.1下载，900秒后无CTRF／Reward，Episode d513081b-042d-4dc8-85ec-dd7158853c8e日志保留。原依赖缓存已按原脚本精确参数安装7包；源码f97e614d0b944323ed5cee0669309e446f213e55识别被AgentTimeout记录覆盖的VerifierTimeout，并支持显式单题技术恢复。有限2624819等待当前固定恢复后执行该位置，再先跑联合剩余固定组，随后等待原Model-only及联合主批结束再做必要恢复；有效官方失败继续保留。

联合批次首题`modernize-scientific-stack`三个固定策略已完整执行至原结束条件并由原Verifier评分；Seed43，与本题现有Model-only24组同seed。下表为单题结果，完整87题批次仍剩954位置；[逐策略及费用报告](rq1/terminal-bench-2.0/20261112-v9-joint-paired/review.md)保存所有原评分和缺项。

| 固定模型／档位 | 官方Reward | 质量统计 | API Token | 已知参考USD | 额外请求重试 |
|---|---:|---|---:|---:|---:|
| Luna High | 1 | 有效通过 | 13239 | 0.00109950 | 0 |
| Terra High | 0 | 有效失败 | 35826 | 0.03971800 | 0 |
| GLM Low | 0 | 请求故障另列 | 未知 | 未知 | 22 |

Luna两条官方断言均通过；Terra一通过／一失败，`analyze_climate_modern.py`超过原测试内30秒，代码与CPU TCG资源贡献未分离。GLM同一个Low/4096请求23次503到原600秒任务截止，生成内容与工具均0，原Verifier两条断言失败；API消费未知，原0保留，进入一次独立恢复。Luna/Terra请求与返回均High，缓存实际报告7680／0 Token，教师关闭。现有同题Model-only为16通过／5有效失败／3缺评分；有效结果不重跑。原请求、工具、Verifier及结束日志均在本批私有Episode目录。

## 2026-11-13 · 请求重试与Router收尾

multi-source-data-merger训练Kev OFF Low的首个Terra Low/4096请求33次HTTP502、32次额外重试后停止，真实事件AGENT_PROVIDER_DEADLINE已触发。Episode fda90c54-b1f3-4ce4-afb8-c3f16825117b的原Verifier正常执行3条断言、全部失败；原0保留，质量单列技术故障并排入独立恢复。Agent896.767655秒、Verifier209.615364秒、Harbor1184.931551秒，请求用量与费用未知。此事件确认已部署的Provider截止异常分支能够继续原Verifier，长度耗尽分支仍待真实触发。

11-14 18:27本次源码汇总：Model-only795/2136位置结束，208通过/101有效失败/466缺有效评分/20依赖失败；0运行、1341未开始，其中2项GPU队列等待。已知模型与教师参考费$10.52758842，513请求费用未知，实际额外请求重试1451次。model-extraction-relu-logits训练Kev OFF Max的第三次生成连续6个HTTP524、各约126秒，6次额外重试后在原时限读超时；原Verifier0及失败断言保留，质量单列技术故障，排入一次独立恢复。该Episode已知10557 Token/$0.011877，完整费用未知；详细请求与阶段时间见本批资源记录。

polyglot-c-py全部24位置结束：4通过、4有效失败、16缺有效评分；原官方Reward1/0/缺失为4/19/1，故障原0另外保留。表中档位均为固定请求Effort。

| 实体／教师 | Low／High／Max结果 | 各档额外请求重试 |
|---|---|---|
| 原始 OFF | 0／故障／0 | 0／17／23 |
| 原始 ON | 故障／故障／故障 | 31／31／32 |
| 训练 OFF | 故障／故障／故障 | 31／32／32 |
| 训练 ON | 故障／故障／故障 | 31／32／32 |
| Kev原始 OFF | 0／路由等待／路由等待 | 0／0／0 |
| Kev原始 ON | 策略拒绝／0／1 | 0／0／0 |
| Kev训练 OFF | 1／1／路由等待 | 0／0／0 |
| Kev训练 ON | 首次路由等待／首次路由等待／1 | 0／0／0 |

十条未恢复的请求均在原任务时限内TASK_DEADLINE并调用原Verifier，原0保留、质量另列、排入独立恢复。除原始OFF High前17次生成成功外，其余九条均首个GLM请求未完成、工具0、教师0，教师效果未执行；失败消费未知。最新原始错误正文为`{"error":{"message":"Service temporarily unavailable","type":"api_error"}}`，取自既有私有响应。

原始OFF Max第五次生成的1个502/22个503在23次额外重试后恢复合法tool_calls；同请求重试等待571秒、尝试延迟74.044259秒，十次生成最终均COMPLETE。末端Agent到原900秒，原Verifier因目录多出cmain判0；Low亦因相同单文件断言判0，两条有效失败不重跑。High/Max已知API参考费$0.01794385/$0.01079634，两侧各1请求失败消费未知，完整费用未知；技术等待与生成/工具轨迹贡献未分离。

原始Kev OFF Low也因目录多出cmain而官方1条断言失败、Reward0；14次Luna Low生成/14工具结果、0额外重试、101154 Token、$0.01105324参考费、Harbor822.227022秒，有效失败保留。训练Laya ON Max的首个GLM请求32次额外重试后仍未恢复，原0及全部未知消费另存。

原始Kev OFF High/Max分别在工具结束后等待未返回的下一次路由780.463440/878.080158秒，原0保留、质量单列ROUTER_DECISION_TIMEOUT。训练Kev OFF Max也有长路由等待；教师ON Low/High首次路由均未返回，生成/教师请求0，原0另列。该题当前缺分为GLM请求故障10条、Router等待5条、Luna策略拒绝1条。

原始Kev ON Low第三个Luna请求的139个SSE事件最终返回invalid_prompt／invalid_request_error，提示内容策略拒绝，Usage缺失；原NON_RECOVERABLE与0重试保留，现有技术恢复入口不选择此记录。ON Max及训练Kev OFF Low/High完整任务官方1，API参考费分别$0.01657770/$0.03506880/$0.04717100，三条均0重试；原始ON High官方0保留。

最后训练Kev ON Max为be543617-606b-403a-b1b5-a8efa0b7bbb1，原官方1；15次Terra Max生成请求中14次完成、最后1次在原900秒末读超时，0额外重试，正常时限结束继续原Verifier。4次Luna Low短评均成功、实际用于5次路由决策，已知216266 API Token、71808已报缓存、1请求用量/费用未知；已知模型/教师参考费$0.23802240/$0.00162820，Harbor1170.415537秒。该题24次尝试已知参考费$0.43279893，13请求费用未知；完整账单与资源USD未知。

原队列进入polyglot-rust-c，原始Laya OFF Low/High/Max首个GLM请求分别31/32/32次额外重试后TASK_DEADLINE，原0保留、质量另列，三条用量和费用未知；教师ON Low/High在原GPU队列等待，Task计时尚未开始。

9d46b66e2d9c244d6c210d64be5166f07f7fdb4b沿原统计函数单列取消前长于本Episode已完成路由耗时的未返回决策；短余时耗尽和结束后才发起的请求仍保留原零分。当前Model-only7条长路由等待另列，原official_reward与全部费用保留；Doom为0通过/19有效失败/5缺分，merge-diff为15/6/3。历史1513位置与两题54位置沿当前源码重新汇总，结果与费用保持原数量。

nginx-request-logging训练Laya OFF Low正常结束、官方0，8断言2通过/6失败；任务内localhost:8080连接拒绝，Nginx安装与语法两项通过。原始与训练版同题同seed43，全部请求分别为10/15次Luna Low、端点均luna-codegoai、首请求六个正文参数完全相同；原始版官方1。两个完整Episode分别49084/109670 Token、参考费$0.00450576/$0.00819204、Harbor388.912267/497.939855秒，两侧0额外API重试。模型选择相同而后续轨迹不同，具体质量差异来源未分离；这条有效0不重跑。

该题24组全部结束：16通过、2有效失败、6请求故障原0另列。训练Kev教师OFF/ON三档均33个HTTP502、32次额外重试后达到原时限，六条请求费用未知，排入独立恢复。后续password-recovery原始Laya OFF Low原官方2断言全失败、Reward0；/app/recovered_passwords.txt缺失，13生成、0重试、134960 Token、$0.01128877参考费、Harbor378.71589秒，有效0保留。

password-recovery全部24位置结束、16通过/8有效失败、无缺有效评分；以下均为完整Episode、seed43、0额外API重试、API参考费齐全。

| 实体／教师／固定档位 | 官方Reward | API Token | 模型＋教师参考USD | Harbor秒 | 教师请求／短评使用决策 |
|---|---:|---:|---:|---:|---:|
| 原始 OFF Low | 0 | 134960 | 0.01128877 | 378.715890 | 0／0 |
| 原始 OFF High | 1 | 117362 | 0.00809921 | 447.013906 | 0／0 |
| 原始 OFF Max | 1 | 223952 | 0.02020042 | 623.651829 | 0／0 |
| 原始 ON Low | 1 | 60910 | 0.00546544 | 331.459769 | 3／5 |
| 原始 ON High | 1 | 84517 | 0.00800002 | 411.445076 | 2／5 |
| 原始 ON Max | 1 | 588012 | 0.03999828 | 887.744323 | 4／14 |
| 训练 OFF Low | 0 | 83478 | 0.00408152 | 400.012547 | 0／0 |
| 训练 OFF High | 0 | 122556 | 0.00791000 | 448.320913 | 0／0 |
| 训练 OFF Max | 1 | 302005 | 0.01838270 | 475.216602 | 0／0 |
| 训练 ON Low | 0 | 19191 | 0.00189742 | 277.406881 | 1／2 |
| 训练 ON High | 0 | 61845 | 0.00532439 | 388.382650 | 1／1 |
| 训练 ON Max | 1 | 234541 | 0.02072338 | 542.579877 | 3／3 |
| Kev原始 OFF Low | 0 | 171510 | 0.01270204 | 467.308276 | 0／0 |
| Kev原始 OFF High | 1 | 156225 | 0.01624290 | 513.534179 | 0／0 |
| Kev原始 OFF Max | 0 | 220444 | 0.02891968 | 1405.350197 | 0／0 |
| Kev原始 ON Low | 0 | 115516 | 0.00835176 | 432.950515 | 2／3 |
| Kev原始 ON High | 1 | 167215 | 0.01606294 | 528.023692 | 3／6 |
| Kev原始 ON Max | 1 | 191975 | 0.01789806 | 607.131856 | 2／6 |
| Kev训练 OFF Low | 1 | 86389 | 0.06765620 | 369.689422 | 0／0 |
| Kev训练 OFF High | 1 | 94832 | 0.07023440 | 380.818105 | 0／0 |
| Kev训练 OFF Max | 1 | 89681 | 0.07502180 | 385.023575 | 0／0 |
| Kev训练 ON Low | 1 | 71053 | 0.04749920 | 337.062432 | 2／2 |
| Kev训练 ON High | 1 | 80187 | 0.04518320 | 362.529680 | 2／6 |
| Kev训练 ON Max | 1 | 121988 | 0.08220670 | 449.958544 | 1／7 |

Laya原始版六组5通过、训练版六组2通过；训练OFF High、ON Low/High及原始Kev OFF Low均1断言通过/1失败，结果文件存在但未包含正确密码，24个位置均0额外API重试，费用齐全。Kev原始OFF Max与ON Low均1断言通过/1失败，结果文件未包含正确密码；Max Agent870.079981秒、Verifier448.008171秒，两个阶段分别在原900秒内，Harbor总时长1405.350197秒，官方0保持。训练OFF Max全部16次生成均为GLM Max，官方1。Laya生成只在Luna/GLM的同档位间选择。训练OFF Low的原Verifier1通过/1失败，结果文件存在但为空，有效0保留。Laya原始Max教师ON/OFF均通过，ON参考费增加98.01%、Harbor增加264.092494秒；Laya原始Low教师ON/OFF分别1/0，后续模型与工具轨迹不同，教师独立贡献未分离。

训练Kev六组全部选择Terra，55次生成请求及返回档位均匹配；OFF三档10/10/8次生成，ON三档8/9/10次生成，六个原官方Reward均1。原始Kev六组全部Luna，3通过/3失败；三档OFF/ON的API参考费分别$0.05786462/$0.04231276，训练版分别$0.21291240/$0.17488910。该题训练Kev通过更多且API参考费更高，Laya训练版通过更少；质量差异与模型选择、后续轨迹的贡献未分离。

该题24个Episode的已报告API Token合计3600344、参考费$0.63935043；教师26请求、短评使用60次决策。缓存实际报告读取1757248 Token、26请求未报，物理KV共享及供应商实收/Router/工具/资源USD未知。原队列已进入polyglot-c-py；原始Laya OFF Low官方1条断言失败，目录多出cmain违反单文件要求，Reward0保留；57023 Token、$0.00510388参考费、Harbor514.741335秒，0重试。

multi-source-data-merger全部24组已结束：20个官方1、4个请求故障原0另列，4个位置进入独立恢复队列。训练Kev ON High/Max分别在13/11次额外重试后取得官方1，Luna Low教师分别实际消费1/2次；MAX Episode为4e737241-bd5d-4d46-b04a-0fcc44366cdc，Harbor1223.295913秒、已知110588 Token，2请求用量/费用未知，已知模型/教师参考费$0.119308/$0.0004048。教师开关与渠道恢复的贡献未分离；原队列继续nginx-request-logging。下表为同一任务、seed43、Low/High/Max三个完整Episode，费用只列已知API参考部分。

| 实体／教师 | Low／High／Max | 三档已知API参考费USD | 费用未知请求 |
|---|---|---:|---:|
| Laya原始 OFF | 1／1／1 | 0.01151245 | 0 |
| Laya原始 ON | 1／1／1 | 0.04254487 | 0 |
| Laya训练 OFF | 1／1／1 | 0.01925404 | 0 |
| Laya训练 ON | 1／1／1 | 0.02540497 | 0 |
| Kev原始 OFF | 1／1／1 | 0.01801048 | 0 |
| Kev原始 ON | 1／1／1 | 0.01556472 | 0 |
| Kev训练 OFF | 故障（原0）／故障（原0）／故障（原0） | 未知 | 3 |
| Kev训练 ON | 故障（原0）／1／1 | 0.16372930 | 4 |

训练Kev OFF High/Max分别又出现33个HTTP502和32次额外重试，两条均触发真实AGENT_PROVIDER_DEADLINE并继续原Verifier；三个档位的原0及首次费用保持，质量单列请求故障，不记模型能力失败。Terra原渠道的站点200、无授权模型目录401、授权目录200且列出精确模型；生成错误正文为error code: 502。Mac直连和原TCP出口的站点/目录响应一致，网络配置保持；当前Registry没有可切换的有效Terra端点。生成后端原因及实收仍未知，原矩阵继续，四条位置沿原独立恢复队列。

model-extraction-relu-logits的24组已结束，10通过/12有效失败/2缺评分。训练Kev ON High为原官方1，7生成、2次Luna Low教师短评均进入Router，49222 Token、24960实报缓存、参考费$0.0311997、Harbor784.41181秒。ON Max第二次生成在13个502和1个503后恢复，同模型Max/4096参数保持，最后一次生成单次读取超时到原900秒；官方0保留，不恢复重跑。它已知19691 Token/$0.0113982，2请求费用未知，教师1次实际消费，Harbor1128.11048秒；中途技术等待与生成耗时对失败的贡献未分离。两项缺分分别为原始Kev OFF Max官方断言开始后Verifier超时，以及训练Kev OFF Max未恢复的请求故障。原队列已推进multi-source-data-merger。

Provider最多额外100次同请求重试已在正式请求路径生效，原任务时限及4096输出保持。最新[Model-only正式报告](rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)与逐Episode表保存实际重试、原始与恢复尝试、有效官方评分、缺评分和费用；批次仍按原矩阵推进，20分钟观察复用原控制进程。

`96d065e3e0564d0e2a610d3cb92d412823fdadb6`将Router客户端、排队及共享GPU等待约束到任务剩余时间。hf-model-inference训练Kev OFF High/Max原官方Reward1/0已写入后，收尾仍等待Router线程；仅替换等待锁的worker，两条原结果及费用保留，新任务已经接续。High的实际Token为203,004，模型参考费$0.114308；Max为21,411 Token/$0.026639，教师均OFF。原Harbor任务墙钟1124.269493/1105.229683秒，含CLI收尾的命令墙钟5787.671381/5226.806454秒，两项时间分别保存。

训练Kev ON Low/High两条新Episode在首个路由等待中耗尽900秒原Agent时限，生成请求0、路由返回0、CTRF缺失；保持无有效评分。同时间共享GPU锁由现有视频服务持有，原视频服务与Benchmark条件保持。资源和修复身份见[运行事实](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)。

当前Controller1696641、持有1696633继续原矩阵；1700006接续本批技术恢复及联合957，1700191每1200秒汇总，2024071等待后执行联合与历史技术恢复。2989c4ecb89aa4306710236d764ada2caf084783使历史25条GLM4096长度耗尽且跳过Verifier的位置进入一次独立Episode恢复；均无先前有效评分，尚无本轮100次请求重试规则下的恢复，早期恢复Job及seed42身份保持。正常长度耗尽不重试API请求。旧等待队列1704159退出后，凭据同一memfd继续由2024071持有。当前代理17649继续运行；等待交接18875沿现有CLI在其自然退出后接管，跟随1700006和2024071：SSH断线5秒后重接，30秒保活、连续3次无响应退出连接，认证及主机密钥错误结束，两个批次均退出后关闭。

```bash
python3 our-project/code/cli/run_rq1_a6000.py \
  our-project/experiments/configs/v9_model_only.json \
  --proxy-for-pid 1700006 2024071 --proxy-after-pid 17649
```

kv-store-grpc训练Laya OFF Low的同一个Luna Low/4096请求经历7次URLError，attempt_index=7返回HTTP200，原Agent继续工具执行并取得官方Reward1。GLM Max在30次额外重试后也返回合法工具调用，两次成功生成后达到900秒原时限，官方Reward0保留；失败尝试费用未知。该题训练Laya OFF Low/High/Max和ON Low/High均取得官方Reward1。

`e537e363c8a84c3669fc7bfd0dbfd5f2b57fe6f9`按真实逐请求记录区分超时前仍失败的生成重试：gpt2-codegolf原始Laya OFF Max、headless-terminal训练Kev OFF Max的原Verifier0保存在`official_reward`和原文件，质量汇总的`reward`为空，`technical_fault=PROVIDER_RETRY_DEADLINE`。正常完成请求后的有效失败和成功均复用。`0ddeb6482420f0629637fd540118f4bcbf24eff5`使原Harbor工具调用的等待时间取原工具时间与任务剩余时间的较小值；旧晚到工具日志和官方结果保留。

`fe2857938a1fce4bfebb0a7de10e1ac35db37297`统一新Job技术恢复、任务计时前共享GPU等待。首次交接遗漏两条线程子任务，上游原地恢复删除部分kv-store-grpc原Trial文件；缺失目录与配置无法从现存副本恢复，原事件、工具、请求和命令在[资源记录](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)逐项列出。后续恢复使用独立Job，保留全部现存记录。

`e4375ef4cd104d7d6d0f918a1e6fb9b9a6731027`将现行PIP_INDEX_URL用于每次原Harbor调用；清华源已安装官方要求的pytest8.4.1/pytest-json-ctrf0.3.5。largest-eigenval训练Kev OFF Low/High/Max均取得官方Reward1，原Trial墙钟542.738121/364.342884/989.729592秒，原测试脚本和断言保持。

`c1e55dd13897376e4e9b0d4ce22a8f1b771f4c7c`保存上述有限代理重接。log-summary-date-ranges训练Laya教师ON High/Max的首个GLM请求分别在27/20次额外重试后取得合法工具调用，原Agent继续执行，两条完整任务均为官方Reward1；费用包含成功请求参考费，失败尝试账单未知。

`3e1321fe371441081fcce69a664a2819464a38fe`在每次Harbor调用合并现行依赖映射。log-summary-date-ranges原始Kev ON Max、训练Kev OFF Low在原Episode补入原版本依赖后均官方1；训练Kev OFF High/Max沿新映射也均1。训练Kev ON Low/High的原0没有CTRF，uv仍访问pypi.org；现行UV_INDEX_URL和依赖env已改用清华源，恢复留在既有队列。

正常4096输出耗尽现由`274b683c68f0c26db281e7a1a8477f9fedf865cf`直接使用原Harbor的OutputTokenExceededError，错误策略为AGENT_EXHAUSTED_BUDGET/retry=false/grade=true，随后调用原Verifier；该请求不重试、不升额度，下一次真实发生后记录实际评分，旧未知终局保持。

uv索引修复后，log-summary-date-ranges训练Kev教师ON Max官方2/2断言通过、Reward1；模型与教师API125298 Token、$0.09735750参考费、用量缺项0、Harbor668.024798秒。该题24组已结束；Model-only矩阵已推进到make-doom-for-mips，全部数量沿原报告更新。

make-doom-for-mips原始Laya OFF High/Max同样在uv下载TLS中断后没有uvx和CTRF，原0另列。官方89题中82题使用精确uv0.9.5安装地址，现行运行配置统一将这82题接入原依赖目录，完整名单及原脚本来源在本批资源记录。原测试脚本和包版本参数保持；20:29两条在途原始Laya ON Low/High已经补入依赖，继续原任务，不重发已完成的工具命令。

`a4c961535dfbb37920a7c80a29bde3864533edb1`将Provider已记录TASK_DEADLINE的终止映射为原Harbor AgentTimeoutError，再调用原Verifier；原网络故障仍单列，未增加请求或时间。原始Laya OFF Low的第14次额外尝试503/TASK_DEADLINE后曾没有评分，原记录保持。正常4096输出耗尽保留原OutputTokenExceededError路径，两条新终止分支的实际验证沿下一次真实Episode记录。

make-doom-for-mips全部24组Model-only已结束，05:13当前分类为0通过、21有效失败、3缺有效评分；四个原任务截止时的单次读取超时恢复为原官方0，21条有效0不重跑。剩余2个依赖故障、1个旧HTTP503提前跳过Verifier。模型与教师已知参考费$1.66774970，9位置费用不完整，已报告12849099 API Token、14请求缺用量。原测试VM超时、frame.bmp缺失和帧比较失败均有原始记录；代码与TCG资源影响尚未分离。

11-14 00:21台北：merge-diff-arc-agi-task原始Laya OFF High官方5/5通过、Reward1，Max在原Agent900秒结束后官方0/5、Reward0；两条分别17/38次生成、0次额外重试、$0.01114506/$0.05922257模型参考费。ON Low/High尚在GPU锁前等待，Agent时限未开始。Model-only已结束651/2136，128通过/68有效失败/435缺评分/20依赖故障；模型与教师已知参考费$7.80484740，472请求费用未知。逐题结果与分母沿原正式报告更新。

01:12：ON Low/High后续进入Agent并自然结束，原Verifier在Ubuntu下载阶段耗尽900秒、断言未执行、Reward未知。现行apt镜像映射沿原环境类覆盖38个明确Ubuntu24.04且调用apt-get update的任务；USTC发行索引及原失败软件包HTTP200，下载0.226/0.142秒。源码2308ba82c1dcfcba44e309127b54a2a38b7f802b已部署。01:27训练Laya OFF Low完整Episode验证修复：6.8MB软件包4秒下载、原Verifier185.998秒、5断言2通过/3失败，官方Reward0；原始Laya ON Max亦官方0/5、Reward0。原下载失败日志、Token、费用及独立恢复身份保留，两个有效0不重跑。

03:07：merge-diff-arc-agi-task全部24组结束，15通过、7有效失败、2下载缺分；原队列继续model-extraction-relu-logits。下表每格为同一题、seed43的原官方Reward，费用为三档全部尝试的模型与教师参考费之和。

| Router实体与教师 | Low | High | Max | 三档已知API参考费USD |
|---|---:|---:|---:|---:|
| Laya原始 OFF | 0 | 1 | 0 | 0.07553253 |
| Laya原始 ON | 缺分 | 缺分 | 0 | 0.02948809，5请求费用未知 |
| Laya训练 OFF | 0 | 1 | 1 | 0.02297960 |
| Laya训练 ON | 1 | 0 | 1 | 0.02391444 |
| Kev原始 OFF | 0 | 1 | 1 | 0.01668420 |
| Kev原始 ON | 0 | 1 | 1 | 0.01935312 |
| Kev训练 OFF | 1 | 1 | 1 | 0.37179520 |
| Kev训练 ON | 1 | 1 | 1 | 0.29019720 |

该题训练Kev的High前后均通过，模型参考费$0.00496054→$0.08205140；Low从未通过变为通过。训练Kev教师ON保持三档通过，并降低三档已知API参考费；训练Laya教师ON令Low通过、High失败，Max仍通过。新训练Kev Low/High及教师ON各档均选Terra，OFF Max实际选过Luna和Terra；原始Kev六组均选Luna。两个Laya原始ON下载超时保留原记录并待独立恢复。完整实收及Router、工具、资源美元费用未知。

Model-only03:48快照已结束676/2136，143通过/76有效失败/437缺评分/20依赖失败；后续仍沿原队列执行。

hf-model-inference／GLM High／seed42的单项恢复已取得原官方Reward0，4条断言2通过/2失败；失败为Agent产生的localhost:5000接口连接拒绝，不再运行该有效0。两条早期无评分Trial和全部原消费保留，新Job为infrastructure-recovery-2，Episode4d854990-2cde-4b4a-8ce1-58b656368712；该次38生成/40工具结果、0额外API重试，352580输入+10326输出=362906 Token。缓存实际已报告295808 Token、3请求未报；推理已包含输出，不重复相加。原Agent900.052秒、Verifier274.839秒，新Episode参考费$0.02255304、三次尝试合计$0.02733079；请求High/4096、返回Effort未报告，所有38次返回tool_calls，新预算异常分支未触发。25个历史长度缺评分位置中1个恢复结束、24个仍在原队列。

历史1513位置现为258通过/257有效失败/895缺评分/103依赖失败，2354个Harbor Trial；原2333 Trial身份保持。已知模型与教师$35.62336373，1050请求费用未知；完整实收和资源美元费用继续缺失。

04:29：model-extraction-relu-logits训练Laya OFF High的最后一次GLM High/4096请求经历23次HTTP503后返回tool_calls，模型及档位保持；原900秒终止及原Verifier继续生效，官方Reward1。失败尝试缺用量/费用，完整参考费为空；本批已知模型与教师$8.74583274，478请求费用未知。Model-only680结束、145通过/78有效失败/437缺评分/20依赖失败，当前2子任务在途、1454尚未派发。

05:13：训练Laya OFF Max的同次GLM Max/4096请求17次503后返回tool_calls，原官方Reward1；ON Low也取得1、$0.00537924参考费。ON Max末次请求仅剩约55秒，单次读取超时后原任务900秒结束、官方0保持，不作恢复重跑。7311981e3578af888ddc1afc9909f375415e80d9同批保留7个这种任务时限0，重复503等已观察技术故障仍单列；等待原因未分离。当前源码collect-only汇总686结束、147通过/88有效失败/431缺评分/20依赖失败，API参考已知$8.82566382、480请求费用未知。老观察进程内存分类仍旧，公开结果沿原导出目录采用当前源码汇总。

## 2026-11-12 · Model-only全量执行与Token统计

[RQ1部分帕雷托图与40组状态](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/pareto_review.md)按openssl-selfsigned-cert、regex-log同两题、seed43、原始及11-11微调实体绘制；21组评分与API费用齐全，另19组缺项。费用累计全部尝试的模型＋教师参考费，完整现金费用保持未知。[逐点数据](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/pareto_points.csv)保存来源、版本与缺项；沿原`rq1_figures.py <本批目录> --pareto`更新图表。

正式数据集为`terminal-bench@2.0`，89题，Commit `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`。训练数据与Benchmark分开保存；这里的通过来自原Harbor完整Agent及官方Verifier。

[Model-only批次](rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)沿同一入口执行89题×24组×seed43：Laya/Kev原始及11-11训练版，教师OFF/ON，固定Low/High/Max，每次仅在同档位三个真实模型中选模型。两道历史已观察任务优先执行，旧seed43联合选择结果直接引用作配对，其他87题的联合选择配对尚缺。旧89题seed42比较使用11-08训练版，版本和seed分别保留。

21:59台北公开快照：458/2136位置结束，63通过、11有效失败、373缺Reward、11个Verifier依赖失败原0另列；2运行、1676未开始。20/89题有结束记录，19题已结束全部24策略。已报告模型+教师输入7,544,340、输出509,218，合计8,053,558 Token；394次请求缺用量。已知模型参考费$2.30393366、教师$0.01786016，合计$2.32179382；实际缓存读取5,398,848 Token。Router本地另报告5,140,119输入/59,236输出Token，资源美元单价未知。后续数量沿本批报告和逐Episode表更新。

本批316个连接拒绝记录发生在原控制SSH断开、17898代理停止监听后。18:31按本机Clash实际mixed-port=17897恢复同一代理，新请求已有响应。矩阵结束后沿原机制恢复一次相应位置，并处理fix-git、gcode-to-text、git-leak-recovery中uvx下载失败且无CTRF的原0；有CTRF的有效失败保持，全部尝试和费用保留。[87题联合成对接续](../../experiments/configs/v9_joint_paired.json)已排在其后，能力快照直接读取本批保存配置。

19:05网络接续：Luna/GLM/Terra原域名改走现有TCP出口；后续Debian/Ubuntu及uv初址也沿该出口，官方Release与uv实际跳转目标HTTP200。单批代理连接跟随现有接续持有进程结束而退出，原观察输出接回同一controller.log；原任务、Verifier与模型身份保持。

gcode-to-text训练Kev Model-only、Teacher OFF：High实际执行2条断言、1通过/1失败，完整任务Reward0；1064.318775秒、26生成/26工具结果、模型参考费$0.15098180，26次费用齐全，实际请求/返回均Terra High。Low的原0来自Debian官方下载502、uvx未安装，测试断言未执行；783.051197秒、20生成/20工具结果、$0.07798260保留，任务质量另列。此前Luna High/Max均INCOMPLETE_RESPONSE、缺Reward。后续87题为八联合主组696位置＋三固定参照261位置，共957；固定参照GLM Low/Luna High/Terra High先四并发、再两并发Router，复用原两题seed43结果。

唯一[配对汇总](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/comparisons.json)已纳入Model-only同档位的原始/训练、教师OFF/ON及固定模型对照，记录实际评分与费用齐全的任务/seed。两优先题中，训练Kev OFF联合/Model-only Low、High、Max均2/2通过，模型+教师参考费分别为$0.02944120 / $0.03871960、$0.04624140、$0.26640480。训练Kev ON联合/Model-only High、Max均2/2，参考费分别为$0.03183710 / $0.05734710、$0.30910010；ON Low仅一对费用齐全，单列该题。Laya原始OFF的联合/Model-only Low、High均2/2，参考费$0.03605180 / $0.00242127、$0.00463366。完整实收及Router/工具/资源USD缺项保持UNKNOWN。

git-leak-recovery新增三组训练Kev完整通过，CTRF各5条断言全部通过；所有请求参考费齐全。金额含模型与实际教师请求，墙钟为原Harbor Trial。

| Model-only策略 | Reward | 生成/工具 | 教师请求 | 墙钟秒 | 已知参考费USD |
|---|---:|---:|---:|---:|---:|
| Kev训练 OFF Max | 1 | 15/58 | 0 | 998.052763 | 0.16573660 |
| Kev训练 ON High | 1 | 8/16 | 2 | 568.403828 | 0.03641570 |
| Kev训练 ON Max | 1 | 17/65 | 4 | 1252.111846 | 0.16013990 |

同题ON High与ON Max均通过，参考费相差$0.12372420、墙钟相差683.708018秒；教师均ON，差异变量为Effort。Low及OFF High的原0含下载失败、没有CTRF，另列。

Provider与Verifier异常分别保留缺评分。modernize-scientific-stack零分含官方测试执行现代化脚本超时，任务代码效率与VM资源的贡献尚缺分离结果。新git-multibranch原始Laya OFF Low完整通过，OFF High在900秒Verifier超时后缺Reward；原终局保持。其apt索引用时738秒，最后停在Python下载阶段；Mac官方索引直连更快，A6000经相同出口仍在30秒传输时限后仅取得部分字节。远端直连返回HTML、已有7890返回502，域名恢复原TCP出口；具体限速环节未知，实际字节与时间见[资源记录](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/resource_observations.json)，没有增加Episode恢复范围。生成方法版本仍为b9fba0a4488731c76718221e0572e5e7f2e8f936；原Controller2373109继续。

固定执行脚本为`our-project/code/cli/run_rq1_a6000.py`，调用原Harbor批量入口、共享GPU锁、原用户Docker及官方Verifier，每1200秒汇总一次；单次批次结束后退出。凭据从唯一600权限文件经SSH输入/memfd读取。启动命令：

```bash
python3 our-project/code/cli/run_rq1_a6000.py our-project/experiments/configs/v9_model_only.json
```

接上当前批次并顺序完成已授权接续，使用同一脚本的`--attach-pid 2373109 --recover-infrastructure`及两个配置参数：先`v9_model_only.json`，再`v9_joint_paired.json`。接入模式复用已恢复的17898代理；常规启动从Clash `/configs`读取当前端口，不再使用旧7897。观察进程退出码实际传播；原任务进程不因报告更新重启。

仅重连代理使用同一脚本的`--proxy-for-pid`，进程参数取当前实际批次；`--proxy-after-pid`等待现有本机代理自然退出。它不创建Episode或读取模型Key，每1200秒观察远端接续进程，均结束后关闭连接，连接故障在同一入口重接。

已完成批次的逐请求用量已重新聚合到原`metrics/per_episode.csv`和`per_strategy.csv`。`known_prompt_tokens`与`known_completion_tokens`合计已报告Token，`usage_unknown_requests`记录缺用量请求；旧完整用量字段仍在任一请求缺值时保持空值。模型、教师和全部已发生尝试均纳入；Reasoning包含在输出内，缓存读取包含在输入内，各只计一次。

| 已结束批次 | 任务/策略位置 | 已报告输入Token | 已报告输出Token | 合计 | 缺用量请求 |
|---|---:|---:|---:|---:|---:|
| 11-08全量：89题×17策略 | 1513 | 222,158,587 | 6,585,204 | 228,743,791 | 1028 |
| 11-11关联：2题×27策略 | 54 | 2,805,948 | 325,179 | 3,131,127 | 12 |

每个Router在旧全量89题的一次批次，API模型+教师已报告Token如下；数值包含失败与恢复尝试，完整用量仍缺列出的请求。两训练版对应11-08实体。

| Router | 教师 | 已报告Token | 缺用量请求 |
|---|---|---:|---:|
| Laya原始 | OFF | 1,800,940 | 104 |
| Laya原始 | ON | 1,584,642 | 108 |
| Laya训练 | OFF | 904,973 | 110 |
| Laya训练 | ON | 1,391,048 | 111 |
| Kev原始 | OFF | 4,107,166 | 47 |
| Kev原始 | ON | 4,206,669 | 57 |
| Kev训练 | OFF | 18,751,846 | 56 |
| Kev训练 | ON | 23,488,559 | 68 |

Router自身原生前向另记：旧全量4813次已报告34,619,004输入/1,158,807输出Token，11-11关联196次已报告1,216,085输入/23,867输出Token；这部分对应A6000本地计算，美元费率未知。示例完整Episode：11-11训练Kev ON在`openssl-selfsigned-cert`官方Reward1，模型+教师26,374输入/1,313输出=27,687 Token，参考费$0.01004740，官方墙钟396.359101秒；无缺用量请求。

旧全量所有1513位置均已结束，原始Reward为256个1、358个0、899缺值。统一分析从原Verifier日志定位101个`uvx`未安装且无CTRF测试报告的位置，原零分保留并单列，有效质量比较为256通过/257失败；完整89题评分齐全的Router组为0。供应商实收、Router、工具和资源USD缺失，完整费用未知。

## 2026-11-12 · 新联合训练与关联完整比较

[本批终局](rq1/terminal-bench-2.0/20261111-v9-joint-followup/review.md)为2个历史已观察任务×27策略×seed43：54位置、74个Trial全部结束，42通过/2失败/10缺评分，模型+教师已知参考费$0.73402850、12请求费用未知。固定四并发、Router两并发；新18更新Laya/Kev、原始版、教师开关、开始/阶段/逐生成及T/M/H共同执行原Harbor/Verifier。

同题最后Episode参考费：固定Luna High $0.00757392，新训练Laya ON $0.02466572、Kev OFF/ON $0.02944120/$0.03183710，均2/2通过。新Kev主组全选Terra Medium，原始Kev全选Luna Low；Laya ON训练前后2/2且参考费下降26.10%，累计墙钟增加593.650秒。原Verifier安装失败的20个0保留在原尝试，不计任务质量；最终2个0来自日期匹配断言。

完整实收与资源USD未知；实际缓存读1,964,032 Token，Router截断0，Luna Low教师32请求/45次消费。任务容器、Router socket、控制与20分钟观察脚本、临时反向代理均已结束，实验镜像配置保留。图表和逐任务费用在同一批次，不合并到下方89题seed42结果。

## 正式2.0 RQ1全量尝试已结束

[当前批次](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md)采用官方`terminal-bench@2.0`、Commit `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`，89题×17策略×seed42=1513位置。固定组含GLM/Luna Low、High、Max，Terra High、单独Luna Xhigh及规则；八Router组为四实体各Teacher OFF/ON。固定四并发、Router两并发，共享原GPU锁和原生Adapter worker，不新增训练或替换Serving。

11-11末次汇总：全部位置结束，官方Reward 1/0为256/358、899缺评分；2339条Harbor命令、2333个原Trial。已知模型+教师参考费$35.11821871，1036请求缺费用；真实执行跨度68.51小时。以下首批与连接过程按原日期保留，当前每策略通过率、分母、费用和缺项以终局报告为准。四条实际H截断输入的收尾编码见同批`metrics/h_encoding_followup.json`，原Episode结果保持原编码版本。

逐Episode官方Reward、失败类型、请求/返回身份、实际缓存读取、参考费与墙钟集中在同目录`trials/`及`metrics/`。完整现金费用与资源美元价仍缺。任务集合和权重事前确定，31题历史暴露与58题未历史暴露分别保留，未评分不填0。

运行期间收集沿原`modelrouter.benchmark rq1 … --collect-only --export-dir <临时公开目录>`：从原私有Harbor记录派生结果，公开输出独立于活跃父进程写入；传回本批目录后删除该临时目录。未指定`--export-dir`时保留原输出位置。

固定批次等待沿同一入口的`--watch-pids <原Router父PID> <原恢复父PID> --watch-interval 1200`：立即收集一次，此后每20分钟收集一次；两父进程均退出后收集末次并退出。等待使用异步计时，独立临时公开目录复用到底，不创建新Episode、模型worker或定时服务。原批次并发、断点继续和官方执行链不变。

```bash
LITELLM_LOCAL_MODEL_COST_MAP=true .runtime/benchmark-venv/bin/python -m modelrouter.benchmark rq1 \
  our-project/experiments/configs/rq1_terminal_bench_2_0.json \
  --source-revision cb4371da0635d9d550314b6703af4cbe87f0b714 \
  --collect-only
```

沿同一入口的`--recover-infrastructure`补充一次恢复尝试：仅选代理连接被拒绝，或已准备镜像的`hf-model-inference`及`custom-memory-heap-crash`环境启动超时，以及后者已记录的Docker匿名认证EOF；此前须没有成功生成、教师响应或工具结果。两镜像的实际准备结果见当前批次`metrics/resource_observations.json`。固定阶段已结束，Router等待共享GPU时先推进不占GPU的固定策略恢复；恢复过程用`--export-dir`写入临时公开目录，避免与原Router批次同时写同一报告。原Job和Trial留在原目录，新Job使用`--infrastructure-recovery-1`后缀；已有恢复尝试的位置不再次选入。终局采用最后结束的Trial，费用与墙钟累计所有尝试。

每20分钟从原Harbor记录更新的[最新结果主表](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/review.md)保存已结束、运行、未开始位置，以及各策略的官方Reward、评分通过率、参考费和缺费请求数。缓存、Router时间与完整Harbor命令墙钟见同批[策略表](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/metrics/per_strategy.csv)，本入口直接引用，不重复维护当前数字。累计时间是并发尝试时长之和，官方Trial已含在命令墙钟内。供应商实收、Router、工具、CPU/GPU及VM美元价未知。

官方`fix-git`原始Laya OFF已通过，298.091351秒，实际生成使用Terra High。原始Laya ON、训练Laya OFF/ON三臂的GLM High请求均HTTP 502，没有Reward或Usage；原错误仅为`Bad Gateway`，未保存上游响应正文，渠道内部原因缺失，实际费用未知。三个失败保持原记录，不转为零分，不作为档位不受支持的事实。

`fix-git`训练Kev Teacher OFF/ON均官方1、各13生成和50工具结果；模型加教师参考费$0.07920780/$0.09862970，没有未知请求费。官方Episode为596.696061/667.536163秒，Harbor命令为601.806151/672.663908秒；ON有3次教师请求、7次短评消费。该题开启教师保持同质量，增加参考费$0.01942190和命令用时70.857757秒。

`fix-code-vulnerability`四个Laya策略均官方1，费用均齐全：原始OFF为491.818299秒/$0.00738869，原始ON为575.556032秒/$0.02143155，训练OFF为300.713174秒/$0.01723708，训练ON为339.941982秒/$0.04613512。以上秒数为官方Episode，美元为模型加教师参考费。同题质量相同，训练版用时更短而参考费更高；各权重开启教师均增加用时和参考费。

`git-leak-recovery`四个Laya策略均官方1，模型加教师参考费齐全。原始OFF/ON、训练OFF/ON分别为$0.00226377/$0.00564311/$0.00335081/$0.01556503，Harbor命令407.941813/345.929856/391.074953/437.946094秒。原始版开启教师用时减少62.011957秒、参考费增加$0.00337934；训练版开启教师用时增加46.871141秒、参考费增加$0.01221422。各教师开关下训练版参考费均高于原始版，官方质量相同。

完整墙钟沿原`COMMAND_END.duration_ms`登记为`harness_command_wall_s`，官方Trial时间仍为`attempts_wall_s`；对照表追加同题的命令墙钟差值。`crack-7z-hash`训练Kev Teacher ON的原Verifier给1，官方Episode1104.737195秒，Harbor命令2074.480310秒；15生成、4教师请求、3次教师短评消费、24工具结果，已知模型$0.09041620、教师$0.00102230、1请求费未知、无输入截断。900秒AgentTimeout后仍有Router调用等待共享GPU，记录Router1663.982069秒、直接GPU锁等待1462.092615秒。数据库WAL原始Laya Teacher ON官方0，命令1436.662496秒，官方Episode1184.042602秒；没有实际生成或工具结果。原Agent、Provider、Verifier、权重和预算保持该批方法版本。

数据库WAL训练Kev同权重对照：Teacher OFF官方0，Episode1206.456754秒、Harbor命令1212.082614秒，没有生成请求；Teacher ON官方1，Episode561.315797秒、命令566.870387秒，8生成、2教师请求、4次短评消费，已知模型$0.05027400、教师$0.00083160、无未知请求费。实际生成覆盖不同，教师与共享执行等待各自的贡献仍缺分离后的结果。

新增完整任务结果：原始Kev Teacher ON通过`cobol-modernization`，11生成、3教师请求、5次教师短评消费、14工具结果、825.191309秒；模型$0.01084208、教师$0.00151440。训练Kev Teacher ON同题21生成、6教师请求、9次消费、25工具结果、1084.022053秒，AgentTimeout后原Verifier仍给1；模型$0.10402240、教师$0.00344550。两者没有未知请求费或输入截断，同质量下训练版参考费为原始版约8.70倍。两个OFF没有官方Reward，教师收益暂缺该题成对结果。恢复后的HF任务GLM Low、Luna High、Terra High通过；全部原环境失败计入累计尝试时长。

当前同题有效评分比较直接读取[统一对照表](rq1/terminal-bench-2.0/20261108-v9-rq1-glm/metrics/comparisons.json)：分别保存Luna档位、固定与Router、原始与训练、教师OFF/ON的成对通过数、费用及时间差值。费用齐全对与评分对分别登记；终局保持同一方法与事前权重。

首批全部17策略已结束的8题中，合并各权重Teacher OFF/ON的实际路由决策：原始Laya选择GLM/Luna/Terra各66/10/26次，训练Laya各72/7/19次，均为High。原始Kev的108次均为Luna Low；训练Kev的185次均为Terra，其中152 Max、24 Low、4 Medium、4 None、1 High。当前Kev表现为单模型集中选择；15个合法登记动作的存在不能解释为15种动作均已实际选用。逐决策原记录保存在本批`trials/*/*/42/events.jsonl`和`metrics/per_episode.csv`，汇总字段为`selected_action_counts`。

## 历史Terminal-Bench 2.1.0

统计截至2026-11-08，使用本地保存的原Harbor记录，不新增运行。Benchmark为 **Terminal-Bench 2.1.0，共89题**，上游版本 `7131e4375048a0e408a8fb404b5f499d726b695b`。任务清单见[原manifest](../../../router_data/terminal_bench_manifest.json)，逐次原结果保留在[iterations](../iterations/)。

**Single-Agent；Luna/GLM-5.3-Flash/Terra；Model×Native Effort；完整T/M/H；AA精确档位能力；缓存连续性；Luna教师；Laya/Kev原始与最终训练版；A6000原Harbor；完整任务质量—总成本净收益。**

## 做过什么、多少题还没运行

| 实际成果 | 数量 | 含义 |
|---|---:|---|
| 官方任务总数 | 89 | 原manifest的8 canary、24 external_dev、57 final_test |
| Agent尝试过的任务 | 29 | 含固定模型、神经Router、规则及历史模型池 |
| 有Agent官方Reward的任务 | 22 | 至少一次原Verifier给出1或0 |
| Agent尝试但没有Reward的任务 | 7 | 已运行事件保留；终局字段缺失 |
| 尚无Agent运行的任务 | 60 | 58题完全未运行，另2题只有Oracle参考解 |
| 神经Router参与尝试的任务 | 25 | 历史版本及当前版本分别留在原批次 |
| 全部Harbor记录 | 198 | 187个Agent、11个Oracle，按trial_id去重 |
| Agent记录中的Reward 1 / 0 / 缺失 | 67 / 39 / 81 | 多次运行、多策略、多模型池，不合成当前方法Pass率 |

只有Oracle参考解的两题为 `break-filter-js-from-html` 和 `cancel-async-tasks`。29题Agent尝试加上这两题，共31题有Harbor记录；58题没有任何Harbor记录。

之前的工作包含公开数据整理、静态Router评价、真实步骤监督、Laya/Kev训练、Provider工具生成、T/M/H编码测量，以及上述完整任务尝试。完整任务通过使用原官方Reward，静态预测指标保留在[训练报告](../training/training_research.md)。模拟图表归在本文末尾的历史区。

| 原任务用途 | 总题 | Agent尝试 | 有官方Reward | 尚无Agent尝试 |
|---|---:|---:|---:|---:|
| canary | 8 | 2 | 2 | 6 |
| external_dev | 24 | 16 | 13 | 8 |
| final_test | 57 | 11 | 7 | 46 |
| 合计 | 89 | 29 | 22 | 60 |

已经运行的final_test任务保留已观察身份，后续训练与选权重不使用其终局。

## 当前GLM池的整套Agent任务成果

当前确定的原始版本为 `models/laya-421m`、`models/kev-4b-adapter`，训练代表为 `runs/V9-K3-GLM-LAYA-20261108`、`runs/V9-K3-GLM-KEV-20261108`，两者各完成17次更新。三题比较用 `constraints-scheduling`、`sanitize-git-repo`、`large-scale-text-editing`；constraints的Router在CPU执行，后两题在GPU执行。两版本在独立评价前按事前单Epoch规则确定。

执行链是 **Harbor → ModelRouterMiniSweAgent → DefaultAgent → 原官方Verifier**。下表统计整套Agent做完任务得到的Reward。Pass率分母为有1或0的任务，缺Reward单列；同时列出三题中已通过的题数。

| 方法 | 三题已通过 | 官方Reward Pass率 | Reward 0 | 缺Reward | 模型+教师参考费合计USD | 单Episode平均墙钟秒 |
|---|---:|---:|---:|---:|---:|---:|
| Laya原始+教师 | 2/3 | 2/3＝66.7% | 1 | 0 | 完整未知；已知0.13532442 | 1331.6 |
| Laya训练+教师 | 1/3 | 1/3＝33.3% | 2 | 0 | 完整未知；已知0.11108159 | 1209.9 |
| Kev原始+教师 | 1/3 | 1/2＝50.0% | 1 | 1 | 0.03250188 | 1559.3 |
| Kev训练+教师 | 1/3 | 1/2＝50.0% | 1 | 1 | 完整未知；已知0.17776966 | 1298.1 |
| 固定Luna High | 2/3 | 2/2＝100.0% | 0 | 1 | 0.03825362 | 1060.5 |
| 固定Terra High | 2/3 | 2/3＝66.7% | 1 | 0 | 0.13476200 | 1028.6 |
| 固定GLM Low | 2/3 | 2/3＝66.7% | 1 | 0 | 0.08262495 | 1124.4 |
| 规则 | 1/3 | 1/2＝50.0% | 1 | 1 | 完整未知；已知0.07531212 | 862.5 |

sanitize的Kev两臂采用实际故障处理后的 `20261108-v9-sanitize-kev-network` 完整Episode；此前设备、运行时和网络失败不覆盖，均在[49条结果](../iterations/20261108-v9-k3-training/episode_results.json)中。原始和训练Kev在constraints触及1200秒Agent时限，但原Verifier仍给1。large-scale-text-editing原始Kev及固定Luna的Verifier超时；训练Kev因Terra请求none、返回medium终止，无Reward。

参考费合计包含失败和缺Reward任务已知模型/教师支出；其中Laya两版的text各有一请求用量未知，训练Kev的constraints有一请求用量未知。供应商实收、Router/工具/CPU/GPU/VM/训练资源美元价均缺，**完整任务总成本与现金净收益字段为未知**。墙钟包含原Episode环境、Agent和Verifier，不以模型请求时长代替。

### 逐题Reward与参考费用

单元格格式为 `Reward；USD`，缺Reward写明原因。参考费保留原记录精度；`已知`表示另有请求费用缺失。

| 方法 | constraints-scheduling | sanitize-git-repo | large-scale-text-editing |
|---|---|---|---|
| Laya原始+教师 | 1；$0.01053198 | 1；$0.06904899 | 0；已知$0.05574345 |
| Laya训练+教师 | 1；$0.01409152 | 0；$0.03659973 | 0；已知$0.06039034 |
| Kev原始+教师 | 1；$0.00227770 | 0；$0.01131672 | 无Reward，Verifier超时；$0.01890746 |
| Kev训练+教师 | 1；已知$0.02600102 | 0；$0.10385564 | 无Reward，返回档位不符；$0.04791300 |
| 固定Luna High | 1；$0.00128734 | 1；$0.02496080 | 无Reward，Verifier超时；$0.01200548 |
| 固定Terra High | 1；$0.01625040 | 1；$0.05738020 | 0；$0.06113140 |
| 固定GLM Low | 1；$0.00806607 | 1；$0.03307485 | 0；$0.04148403 |
| 规则 | 1；$0.00697112 | 无Reward，上游流错误；已知$0.03126942 | 0；$0.03707158 |

GLM High/Max目前只在constraints有此三题比较的记录，均1，参考费$0.00712319/$0.00968241；另外两题未运行这两档。教师关闭在constraints的训练Laya/Kev为1/0，参考费$0.00418989/$0.02869620；sanitize和text的教师关闭臂未运行。

AA使用同批v7快照，130公开指标；GLM Low/High缺测、Max有独立成绩，GLM返回Effort未报告。最近49尝试共68次Luna教师成功短评、实际报告缓存读取5,572,672 Token，66记录缺读取数；560次消息前缀连续、端点变化及未知物理KV共享分别保存。全批已知模型+教师参考费$1.45700272，范围含开发、完整比较与实际故障处理，不能用它代替某个Router的三题费用。

当前任务结果中，Laya训练版由原始2/3通过降为1/3；Kev两版均1题通过、1题失败、1题缺Reward。尚未取得新池训练的质量—总成本净收益。最终T/M/H编码去重后的四实体前向已完成，**该输入版本的完整Episode为0**，原三题结果仍使用各自保存的旧输入版本。

## 89题逐项清单

`有Reward`含通过或官方0；`无Reward`是已经尝试但没有终局；`仅Oracle`尚无Agent尝试；`未运行`无任何Harbor记录。Reward列按Agent记录填写，不包含Oracle。逐题原迭代及trial_id可从[75批次索引](../README.md#全项目迭代目录索引)和各目录 `official_trials.jsonl`追溯。

| 官方任务ID | 原用途 | Agent次数 | Router次数 | Reward 1 / 0 / 缺失 | 状态 |
|---|---|---:|---:|---|---|
| adaptive-rejection-sampler | canary | 0 | 0 | 0 / 0 / 0 | 未运行 |
| bn-fit-modify | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| break-filter-js-from-html | canary | 0 | 0 | 0 / 0 / 0 | 仅Oracle |
| build-cython-ext | external_dev | 2 | 1 | 0 / 0 / 2 | 无Reward |
| build-pmars | external_dev | 2 | 1 | 0 / 0 / 2 | 无Reward |
| build-pov-ray | external_dev | 2 | 1 | 1 / 1 / 0 | 有Reward |
| caffe-cifar-10 | canary | 0 | 0 | 0 / 0 / 0 | 未运行 |
| cancel-async-tasks | canary | 0 | 0 | 0 / 0 / 0 | 仅Oracle |
| chess-best-move | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| circuit-fibsqrt | external_dev | 10 | 2 | 0 / 4 / 6 | 有Reward |
| cobol-modernization | external_dev | 6 | 1 | 2 / 1 / 3 | 有Reward |
| code-from-image | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| compile-compcert | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| configure-git-webserver | external_dev | 4 | 2 | 1 / 2 / 1 | 有Reward |
| constraints-scheduling | final_test | 12 | 6 | 11 / 1 / 0 | 有Reward |
| count-dataset-tokens | canary | 0 | 0 | 0 / 0 / 0 | 未运行 |
| crack-7z-hash | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| custom-memory-heap-crash | external_dev | 3 | 1 | 0 / 1 / 2 | 有Reward |
| db-wal-recovery | canary | 1 | 1 | 1 / 0 / 0 | 有Reward |
| distribution-search | external_dev | 5 | 3 | 3 / 1 / 1 | 有Reward |
| dna-assembly | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| dna-insert | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| extract-elf | external_dev | 7 | 2 | 1 / 2 / 4 | 有Reward |
| extract-moves-from-video | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| feal-differential-cryptanalysis | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| feal-linear-cryptanalysis | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| filter-js-from-html | external_dev | 4 | 2 | 0 / 2 / 2 | 有Reward |
| financial-document-processor | external_dev | 2 | 1 | 1 / 0 / 1 | 有Reward |
| fix-code-vulnerability | final_test | 2 | 0 | 0 / 0 / 2 | 无Reward |
| fix-git | canary | 4 | 4 | 3 / 0 / 1 | 有Reward |
| fix-ocaml-gc | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| gcode-to-text | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| git-leak-recovery | external_dev | 11 | 4 | 7 / 0 / 4 | 有Reward |
| git-multibranch | external_dev | 37 | 25 | 11 / 9 / 17 | 有Reward |
| gpt2-codegolf | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| headless-terminal | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| hf-model-inference | external_dev | 2 | 1 | 2 / 0 / 0 | 有Reward |
| install-windows-3.11 | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| kv-store-grpc | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| large-scale-text-editing | final_test | 8 | 4 | 0 / 5 / 3 | 有Reward |
| largest-eigenval | canary | 0 | 0 | 0 / 0 / 0 | 未运行 |
| llm-inference-batching-scheduler | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| log-summary-date-ranges | final_test | 1 | 0 | 0 / 0 / 1 | 无Reward |
| mailman | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| make-doom-for-mips | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| make-mips-interpreter | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| mcmc-sampling-stan | external_dev | 0 | 0 | 0 / 0 / 0 | 未运行 |
| merge-diff-arc-agi-task | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| model-extraction-relu-logits | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| modernize-scientific-stack | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| mteb-leaderboard | external_dev | 2 | 1 | 0 / 1 / 1 | 有Reward |
| mteb-retrieve | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| multi-source-data-merger | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| nginx-request-logging | final_test | 1 | 0 | 0 / 0 / 1 | 无Reward |
| openssl-selfsigned-cert | final_test | 9 | 5 | 7 / 0 / 2 | 有Reward |
| overfull-hbox | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| password-recovery | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| path-tracing | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| path-tracing-reverse | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| polyglot-c-py | final_test | 10 | 3 | 2 / 4 / 4 | 有Reward |
| polyglot-rust-c | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| portfolio-optimization | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| protein-assembly | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| prove-plus-comm | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| pypi-server | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| pytorch-model-cli | external_dev | 2 | 1 | 0 / 0 / 2 | 无Reward |
| pytorch-model-recovery | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| qemu-alpine-ssh | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| qemu-startup | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| query-optimize | final_test | 3 | 0 | 0 / 0 / 3 | 无Reward |
| raman-fitting | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| regex-chess | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| regex-log | final_test | 9 | 5 | 5 / 1 / 3 | 有Reward |
| reshard-c4-data | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| rstan-to-pystan | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| sam-cell-seg | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| sanitize-git-repo | final_test | 16 | 12 | 4 / 3 / 9 | 有Reward |
| schemelike-metacircular-eval | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| sparql-university | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| sqlite-db-truncate | final_test | 10 | 6 | 5 / 1 / 4 | 有Reward |
| sqlite-with-gcov | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| torch-pipeline-parallelism | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| torch-tensor-parallelism | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| train-fasttext | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| tune-mjcf | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| video-processing | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| vulnerable-secret | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| winning-avg-corewars | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |
| write-compressor | final_test | 0 | 0 | 0 / 0 / 0 | 未运行 |

## 历史结果来源

本目录原RQ1、RQ3图表与CSV，以及相邻 `benchmarks/` 中的RQ2、RQ4、RQ5，仅供开发与版式参考。原数值保留，当前官方成果从上述原Harbor读取。

| 内容 | 来源 | 标签 |
|---|---|---|
| RQ1 | 无官方Verifier的历史Episode，部分费用与速度为预设值 | Unverified |
| RQ2 | 按模型池写入的模拟成功率 | Synthetic |
| RQ3 | 源码中的G0–G3示例矩阵 | Synthetic |
| RQ4 | 配置中预填的70.2%等数值 | Synthetic |
| RQ5 | 预填成功率、费用与0.72示例边界 | Synthetic |

官方来源导出沿原 `python -m modelrouter.benchmark export`，写入对应迭代目录 `analysis/`。未运行项目保持 `NOT_EVALUATED`。
