# ModelRouter V9 · 真实模型、教师与有效监督

本轮从 e28872fc69604ab082eab5b703d7674073fb4356 接续；原 mini-SWE-agent 2.4.6 / Harbor 0.24.0 不变。没有重跑 fix-git/db-wal Alias 任务，没有新训练或 Serving 权重替换。

## 真实访问与同初始状态结果

Sol 原生 Responses、项目 jiji Luna Chat Completions 已实调 low，请求/返回身份匹配；Flash 两账户 POST 均 model_not_found，档位未知，未用27B代替。文档 Sol 支持 low/medium/high/xhigh/max，Luna 另有 none；本轮只实调 low。

公开 Dev extract-elf 的初始两消息、工具 Schema、mini 配置和候选动作直接相等；seed42、30步、输出4096、教师关闭、AA v4。后续历史由各自行动产生，供应商内部上下文未知。

| 动作 | 请求/工具 | 原结果 | 全部调用模型费 USD |
| --- | ---: | --- | ---: |
| Sol low | 13/10，全部身份匹配 | 原900秒超时；Docker socket在Verifier准备时消失，官方reward未知 | 0.3912934 |
| Luna low | 8/10，全部身份匹配 | 官方reward0、CTRF1/2；覆盖0.00%，要求75% | 0.00447894 |

Sol原Trial保存12响应/0.3480004USD；一条截止前发送、Trial结束后返回的响应0.043293USD另有事件，全部13调用计入0.3912934USD。3次截断中2次4096输出全reasoning，1次reasoning2070/4096。Sol/Luna Trial时间970.478263/522.321635秒，Agent时间900.056730/473.451437秒；共享Token账本串行等待、Docker中断使其不能用作纯速度或完整Episode质量偏好。

两次模型费合计0.39577234USD，供应商实收及资源USD未知。均为固定动作策略，没有新的神经Router效果证据。精确条件、每候选Token/缓存/费用、终局与资格见 [episode_comparison.json](episode_comparison.json)。

原COBOL首Sol19调用/0.5584418USD因归档缺selected_model_id而无Verifier，字段已在原Provider补齐；原因处理后一次Sol15调用/0.421543USD因原30秒工具窗口而无Verifier。COBOL Luna虽reward1/CTRF3/3，但7调用有3次旧型号返回，不作纯Luna样本，3次费用仍未知。没有第三次COBOL运行。同T0的jiji Luna单生成未执行该前缀工具，无偏好标签，见 [generation_prefix_comparison.json](generation_prefix_comparison.json)。

## 教师

旧五失败正文空、length、reasoning=output=1024；JSON Object不能避免reasoning用尽额度。新真实Sol长前缀low/2048也为空，费用0.0305085USD；另有错误Chat入口/超时两次Usage未知。

原Assessor只摘要观察事实，两个固定参考仅输入首尾摘录，移除重复消息，工具最多1600字符；low/4096、context8000，首次约3生成、后续至少间隔3，验证/重复错误优先阶段变化。旧短评随信号变化清除，原formatter保留截止步/阶段；不改变Agent计划、执行工具或指定模型。

新真实step3前缀完整三字段JSON：input1462、output1528含reasoning1435、cache读0/写1459、41.768707秒、0.0189335USD。只验证到教师输出，未执行新Router或工具，不计旧Trial。旧观察触发重算3/7/10而非旧3/5/6/7/8，不等于三次新请求或收益。新短评价格仍约为本次Luna Episode的4.23倍，未证明稳定可靠或净收益。见 [teacher_analysis.json](teacher_analysis.json)。

## 数据与费用

原390/v1实体不变；原54个Open-SWE终局已对应，8个resolved=-1不作失败。唯一新training_view为382行，Train196/Val186，四条旧教师和两固定参考保留；S1候选顺序及人类偏好不改名。旧13214候选与390重合，不算新增独立样本；RouterBench35102为旧池Oracle且许可未明。Open-SWE/smith只提供合法轨迹、工具/恢复与已知终局；AA只作特征。

当前同初始状态动作尝试2、可信Verifier终局1、超时记录1；Model选择、Model×Effort选择、同模型Effort对照、完整三模型对照和Train新选择标签均0。没有成功候选，不把低价失败者标最优或把未知reward写成0；不将Dev改成Train。

原调用日志直接使用Provider已算出的请求模型费率，并保留缓存缺值；仅本轮65个已保存响应条目更新，旧OpenRouter估价/raw Usage保留，新增调用计数0。已知模型费小计1.43331375USD，3次型号不匹配的价格及4次无Usage访问/教师失败金额未知，完整费用和全部供应商账单未知。见 [cost_accounting.json](cost_accounting.json)。

AA固定20261031T072548885180Z-v4：Sol/Luna Max各10项，Intelligence v5.0原分54.5087338138148/27.7552004938153；low/none/托管Flash及Coding/Agentic综合指数缺测。本轮未再次刷新，不借用其他变体成绩。

## 训练、清理与剩余事项

F14已停止，原Run failed/NON_FINITE_LOSS、原队列PAUSED_RUN_FAILED；cursor/Epoch1/曲线/权重保留，未启动F15。台北18:27:28 Serving healthy、原PID/启动时间不变，仍F05/epoch_01与Kev导入适配器。接续代表F11-e01/R11、旧V9负结果保留；没有新的Train选择监督，不启动微调。

Laya继续使用原encoder/head学习率与freeze_encoder，Kev为LoRA/pointer head，head_lr=0沿用主lr。后续真实Train同状态动作结果才作新choice目标，旧S1偏好保留；教师截止前短评及AA卡经原serializer进入输入。收益通过原固定Val的S1四指标与真实Dev Episode判断，不重复旧配方或承诺指标不退步。

Docker已恢复，仅删除本轮停止的Sol容器extract-elf__f7xxagt__env-main-1及其专用网络，没有具名卷；原日志、响应、轨迹和训练数据保留，三个原临时compose目录已自然消失，没有新模型请求。临时容器文件不保留，原镜像可重建环境。原异常未改写。

剩余核心工作：Flash精确型号访问；可用于Train的同状态真实动作/终局比较与Native Effort对照；教师费用相对任务收益；基于真实监督的Laya/Kev接续与动态Router Dev证据。五RQ、八图十二表和正式结果格不变。含机器路径的原运行配置及私人账本只在本机保留。
