# Terminal-Bench正式2.0与历史2.1结果

## 2026-11-13 · 请求重试与Router收尾

multi-source-data-merger训练Kev OFF Low的首个Terra Low/4096请求33次HTTP502、32次额外重试后停止，真实事件AGENT_PROVIDER_DEADLINE已触发。Episode fda90c54-b1f3-4ce4-afb8-c3f16825117b的原Verifier正常执行3条断言、全部失败；原0保留，质量单列技术故障并排入独立恢复。Agent896.767655秒、Verifier209.615364秒、Harbor1184.931551秒，请求用量与费用未知。此事件确认已部署的Provider截止异常分支能够继续原Verifier，长度耗尽分支仍待真实触发。

11-14 13:16本次源码汇总：Model-only771/2136位置结束，204通过/103有效失败/444缺有效评分/20依赖失败；2运行、1363未派发。已知模型与教师参考费$10.12863356，499请求费用未知，实际额外请求重试1072次。model-extraction-relu-logits训练Kev OFF Max的第三次生成连续6个HTTP524、各约126秒，6次额外重试后在原时限读超时；原Verifier0及失败断言保留，质量单列技术故障，排入一次独立恢复。该Episode已知10557 Token/$0.011877，完整费用未知；详细请求与阶段时间见本批资源记录。

polyglot-c-py原始Laya OFF三档已结束：Low/Max为有效官方0，High为请求故障原0另列。High第18次生成连续18个503、17次额外重试后TASK_DEADLINE，原Verifier仍执行，排入独立恢复。Max第五次生成的1个502/22个503在23次额外重试后返回合法tool_calls；该同请求重试等待571秒、尝试延迟74.044259秒，末端Agent到原900秒且目录多出cmain，原官方0保留、不重跑。已知API参考费High/Max为$0.01794385/$0.01079634，两侧各1请求失败消费未知，完整费用未知；技术等待与生成/工具轨迹贡献未分离。

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
