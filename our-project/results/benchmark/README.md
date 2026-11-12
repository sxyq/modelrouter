# Terminal-Bench正式2.0与历史2.1结果

## 2026-11-12 · Model-only全量执行与Token统计

正式数据集为`terminal-bench@2.0`，89题，Commit `69671fbaac6d67a7ef0dfec016cc38a64ef7a77c`。训练数据与Benchmark分开保存；这里的通过来自原Harbor完整Agent及官方Verifier。

[Model-only批次](rq1/terminal-bench-2.0/20261112-v9-model-only/review.md)沿同一入口执行89题×24组×seed43：Laya/Kev原始及11-11训练版，教师OFF/ON，固定Low/High/Max，每次仅在同档位三个真实模型中选模型。两道历史已观察任务优先执行，旧seed43联合选择结果直接引用作配对，其他87题的联合选择配对尚缺。旧89题seed42比较使用11-08训练版，版本和seed分别保留。

18:38台北公开快照：396/2136位置结束，53通过、8失败、335缺评分；2运行、1738未开始，17题有结束记录。已报告模型+教师4,440,557 Token，346次请求缺用量；已知模型参考费$1.22088631、教师$0.01127140，实际缓存读取2,794,048 Token。58次Luna Low教师请求；Router本地另报告3,508,964输入/34,622输出Token，0次决策缺用量。Router累计墙钟9647.529秒、CPU6110.589秒、GPU锁等待2177.449秒，批次首末跨度26299.658秒；时间分项分别列出。

本批316个连接拒绝记录发生在原控制SSH断开、17898代理停止监听后。18:31按本机Clash实际mixed-port=17897恢复同一代理，元数据HTTP200，新请求已有响应。原观察进程已退出，脚本现接上原Controller；保留原失败与费用，矩阵结束后只沿原机制恢复一次相应位置。[87题联合成对接续](../../experiments/configs/v9_joint_paired.json)已排在其后，八个主组共696位置，复用两道旧seed43联合题，能力快照直接读取本批保存配置。

19:05网络接续：Luna/GLM/Terra原域名改走现有TCP出口，元数据均HTTP200，gcode-to-text的Luna High/Max已返回文本并执行工具。单批代理连接跟随现有接续持有进程结束而退出，原观察输出接回同一controller.log。18:58快照412位置结束，53通过/9有效失败/349缺Reward，1个uvx缺失原0另列；API已报告4,542,691 Token、360请求缺用量、已知模型+教师参考费$1.23820567。原结果与网络变更分别登记，后续终局由原Verifier写出。

唯一[配对汇总](rq1/terminal-bench-2.0/20261112-v9-model-only/metrics/comparisons.json)已纳入Model-only同档位的原始/训练、教师OFF/ON及固定模型对照，记录实际评分与费用齐全的任务/seed。两优先题中，训练Kev OFF联合/Model-only Low、High、Max均2/2通过，模型+教师参考费分别为$0.02944120 / $0.03871960、$0.04624140、$0.26640480。训练Kev ON联合/Model-only High、Max均2/2，参考费分别为$0.03183710 / $0.05734710、$0.30910010；ON Low仅一对费用齐全，单列该题。Laya原始OFF的联合/Model-only Low、High均2/2，参考费$0.03605180 / $0.00242127、$0.00463366。完整实收及Router/工具/资源USD缺项保持UNKNOWN。

原8个官方零分保存实际任务评价；Provider与Verifier异常分别保留缺评分。modernize-scientific-stack零分含官方测试执行现代化脚本超时，任务代码效率与VM资源的贡献尚缺分离结果。原Agent超时且官方Reward1同时登记。生成方法版本仍为b9fba0a4488731c76718221e0572e5e7f2e8f936；现有矩阵继续使用原Controller2373109。

固定执行脚本为`our-project/code/cli/run_rq1_a6000.py`，调用原Harbor批量入口、共享GPU锁、原用户Docker及官方Verifier，每1200秒汇总一次；单次批次结束后退出。凭据从唯一600权限文件经SSH输入/memfd读取。启动命令：

```bash
python3 our-project/code/cli/run_rq1_a6000.py our-project/experiments/configs/v9_model_only.json
```

接上当前批次并顺序完成已授权接续，使用同一脚本的`--attach-pid 2373109 --recover-infrastructure`及两个配置参数：先`v9_model_only.json`，再`v9_joint_paired.json`。接入模式复用已恢复的17898代理；常规启动从Clash `/configs`读取当前端口，不再使用旧7897。观察进程退出码实际传播；原任务进程不因报告更新重启。

仅重连当前批次的代理使用同一脚本的`--proxy-for-pid 2806615`；它不创建Episode或读取模型Key，单次SSH与当前接续进程绑定，每1200秒观察退出条件，结束后关闭连接。

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
