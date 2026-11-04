# V9：新修复状态、局部质量差异与独立关系负结果

## 1. 科研目标与本轮重点

在真实动作前Modify/Recover状态中，学习Sol/Luna的质量优先、费用次之选择，并在未见完整Agent任务中获得净收益。本轮完成现有候选恢复、扩展来源、四组成对采集、009/010及原A/B17/B4评价、训练与完整Dev条件判断；没有重复旧STEP、旧四任务请求或旧Dev。

## 2. 最新实际进度

起点main为`359611280e85be98df766c76f01e904fcd5d177e`。公开数字见[summary](summary.json)，逐请求见[request_audit](request_audit.json)，来源和恢复见[source_selection](source_selection.json)，模型结果见[model_evaluation](model_evaluation.json)。本轮发布提交的完整SHA以GitHub main及最终回复为准。

复用现有2500条Qwen轨迹分片及原资格/环境索引，得到1516个粗截止、455任务资格记录，其中139任务为合法L4 Train、19任务没有记录到仓库L1–L3 Train暴露；这些数量不等于有效修复状态数。九任务恢复268条原工具动作。最终四个有可信剩余固定故障的状态事前分为Train两项、仓库留出两项；替换依据原验证或来源问题，发生在候选生成前，不依据赢家。

8个有效200/tool_calls生成，教师0，均真实执行；2个先前HTTP400无动作/未知用量记录保留。8候选固定结果均可信、均未完成。新增正式偏好0，原36保持：步骤质量19、步骤等质量费用8、任务费用9。本轮新增两个Train关系观察、两个独立关系观察，以及一个Train局部严格优势；这些都未进入拟合或梯度。

原`prepare.py::build_offline_prefix_input`把顺序对齐的tool_call_id写入返回的消息深拷贝；原`development.py::run_development`传递对齐来源并实际使用返回消息。Shep原两次400后，同状态各补一次200动作，原响应体未保存，不能声称读到了供应商具体拒绝理由。单步Agent异常不再运行无意义Verifier，`resolved=null`；完整Episode路径保持。原Provider/账户池本轮未改，未更改Code Generation工程。

8次新Checkpoint真实GPU前向，无窗口截断；32632本地编码Token，前向合计3.095秒，含首次冷前向2.220秒，其余约112–138毫秒；含模型载入的分析段12.879秒，过程allocated峰值2.027GB。它们不是商业生成Token，也不是完整动态Episode费用。

## 3. K=2与五RQ的缺口

K=2仍缺两项核心证据：可靠的未见质量—费用条件选择；独立完整Agent质量—总费用净收益。本轮没有补齐任何一项。

V9五RQ仍需真实完整任务证据：RQ1总体效果，RQ2模型池成员/K，RQ3任务拆分，RQ4动作/信息/监督系统消融，RQ5工作负载适用边界。Inspect正式步骤、Native Effort、K3正式监督仍0。本轮低Effort是请求配置，不是Effort标签。

## 4. 下一步前三项及优先级

1. 用已保存的真实失败/修复集合，定义能保留P2P恢复、F2P修复和回归差异的最小局部质量分析目标，同时明确不等于完整一步赢家。
2. 对事前Train状态研究当前源码/失败信息的可用表达，并增加不同修复机制的合法Train质量观察；保持独立用途，不凭本轮两留出调参或预设009 Encoder。
3. 在新的事前留出任务确认同一方法有质量优势和同等可信质量费用机会后，才进入新Harbor三策略完整对照。当前不运行。

完整接续范围见[next_execution](next_execution.md)，本轮已经授权的采集和评价没有留给该工作包。

## 5. 新状态及实际模型结果

| 任务、用途 | 当前阶段 | 固定范围起点 | Sol | Luna | 真实信息 |
|---|---|---:|---:|---:|---|
| Shep69，Train | Modify | 15/16 | 15/16 | 15/16 | Sol改两业务文件；Luna读取；目标失败未改善 |
| Narwhals1948，Train | Recover | 8/10 | 9/10 | 8/10 | Sol恢复一个初始P2P失败，无新回归；目标F2P仍失败 |
| pgmpy878，仓库留出 | Verify | 41/42 | 41/42 | 41/42 | Sol改业务文件，`test_check_model`仍失败 |
| Sacred765，仓库留出 | Recover | 20/21 | 20/21 | 20/21 | 两者改业务文件，`test_save_config`仍失败 |

四对实际Router输入逐字段相同，同快照、同Schema、同固定测试，候选环境独立；生成后才注入原测试补丁，参考修复不进入输入。所有正式准备结果均为`NO_VERIFIED_ACTION`。Narwhals是`STRICT_MULTIDIMENSIONAL_DOMINANCE`辅助关系，其他三项无局部改善。没有新的F2P修复，也没有新的正式质量或费用赢家。

Shep、pgmpy、Sacred的固定失败ID分别保留在各public_comparison的局部集合中。pgmpy原整条命令另有14项范围外失败；Sacred有15项范围外失败，Sol的目标失败还变为旧`collections`接口错误，Luna仍是结果断言不符。固定范围结果不代替整条命令或Episode成功。

PHP-Scoper935/935、UglifyJS63/63、Celebrate35/35固定范围全过，均未收费。node-dev先12/28、16 UNKNOWN；无下载争用时21通过/1失败/6 UNKNOWN，进程清理失败使后续留队；两次`--init`均仍在双重重启等待，手工停止后各12/28、16 UNKNOWN。源码测试不改，根因未确定，不记成模型失败。BaseUI原Jest523项中468过/55失败，上游`parse_log_js_4`不识别U+2715的✕，返回385固定通过/1 UNKNOWN，并有重名判读问题；保留原日志，不收费或改上游Parser制造赢家，以Sacred替代。Apiflask候选涉及修改目录与导入目录不同，未选用。

Sacred原pip构建依赖等待通过本轮临时网络代理解决；原editable安装、PyYAML完成，受依赖影响的YAML生成原命令补执行成功，第一失败不覆盖。只改该任务容器，随后同快照比较。Narwhals第57条只读复现退出与原记录不同，之后业务写入及最后错误继续恢复，差异单列；公开轨迹完整运行时版本仍未知，不声称与原运行环境字节相同。

Shep/Sacred/pgmpy资格仅L4 Train；在既定祖先L1–L3训练范围中未记录仓库暴露，且未匹配旧步骤Train任务。Narwhals仓库已有Train L1 329/L2 541/L3 179行，只能称新任务/Head外观察。PHP/node祖先L2暴露保持；BaseUI另有Val/Test仓库记录，不能称全部历史评价未见。

| 方法 | 009：Shep / Narwhals / pgmpy / Sacred | 010：Shep / Narwhals / pgmpy / Sacred | 新留出关系正确 |
|---|---|---|---|
| 原生模型 | Sol / Sol / Sol / Luna | Sol / Luna / Sol / Luna | 无独立关系输出 |
| A单赢家参照 | Sol / Luna / Sol / Luna | Sol / Luna / Sol / Luna | 无独立关系输出 |
| B17 | Sol / Sol / Sol / Luna | Sol / Luna / Sol / Sol | 两Encoder各0/2 |
| B4 | Sol / Sol / Sol / Luna | Sol / Luna / Sol / Luna | 两Encoder各0/2 |

A仅用原21条正式Train，B17原17条，B4原22条关系Train，ridge=1，无参数搜索、新状态拟合或梯度。B17不能表达NEITHER；B4虽包含该类，却四新状态均误判为单方通过或双方通过，两新留出各0/2，原旧两留出0/2不改写。单赢家A不输出完整质量关系，不能给它虚构关系准确率。

四状态没有正式赢家，正式动作、质量胜负及费用胜负准确率均null。固定Sol与固定Luna的本次候选当步完成均0/4，不能从中计算赢家正确率或整任务成功率。009在Narwhals选择Sol与局部优势一致，010不一致，A均不一致；B009一致、B010不一致。这是单个祖先仓库已见的Train候选辅助结果，不是独立双向泛化。

## 6. 独立判断与未知事项

确实找到当前Modify（Shep），同时得到新的Recover局部质量差异（Narwhals），没有取得新正式修复赢家。多维局部差异被完整通过/未完成目标压成同一NEITHER，这是本轮直接证明的目标信息损失；新Train只有一条局部P2P严格优势，尚不足以支持一次有意义的原Trainer更新。

原20条S1训练材料为14质量/6费用，质量Sol9/Luna5；阶段字段为Verify11/Modify5/Recover1/未知3。加入原Chai后参照正式Train21、B4关系22，NEITHER仅1。名义Modify及类别数量不证明修复机会或可迁移规律。新原生选择不是恒选单模型，但关系预测依然错误；不能把问题唯一归为统一费用偏置。

Router仍只保留6000字符任务/工具摘要，长写命令中段不在摘要中，末次错误保留且8前向没有Token窗口丢弃。这证明表达有取舍，不能证明遗漏内容导致本轮选择错误。样本信息与目标局限有实证，状态表达贡献仍未能单独确定；本轮没有新的完整Agent运行，不能把失败唯一归因于在线动态闭环。

因此不启动STEP011，不重跑原Trainer/Val，不替Serving，不扩完整Dev。旧009费用能力、旧mpmath负结果、010训练20/20和旧完整动态无净收益记录保持。此决定是依照本轮负结果完成条件判断，不是技术不可行或遗漏执行。

已知生成328913输入+3740输出=332653 Token，参考模型费$0.368502；reasoning含在输出只计一次。两400用量、供应商实收、资源USD、商业服务内部物理请求次数及整卡峰值未知。请求/返回模型身份匹配，但未独立确认供应商物理权重身份。CPU TCG、SSH、原验证与Router分析时间分别保留，不与原生Docker性能混合，不用失败更便宜宣称收益。

## 7. 通俗解释

这次把四个真实尚有故障的状态完整比较了，并发现Sol能在其中一个状态恢复更多测试；但两模型都没有把任何一个状态全部修好。Router又把新留出误判为可以通过。我们取得了有边界的局部质量证据和明确负结果，没有得到新正式赢家，没有训练新模型，也没有证明跨任务动态净收益。

## 8. 下一批完整关联工作包

见[next_execution.md](next_execution.md)。源码问题已沿原入口处理，私人原请求/响应/测试/特征留原服务器目录；公开只包含本报告、脱敏汇总和方法评价。资源清理与实际Serving状态见[cleanup.json](cleanup.json)。
