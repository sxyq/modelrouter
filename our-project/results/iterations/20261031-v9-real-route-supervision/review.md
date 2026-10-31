# V9 真实 K=2 路由监督采集结果

本轮取得2条允许训练的动作偏好：1条任务级成本偏好、1条步骤级即时修复偏好，均来自同一公开训练任务。完整三模型最优标签仍为0；没有启动训练或替换Serving权重。

## 任务、来源与条件

- 来源：已有TRA-002对应的[SWE-bench/SWE-smith](https://huggingface.co/datasets/SWE-bench/SWE-smith)训练任务`google__textfsm.c31b6007.func_pm_ctrl_shuffle__hjtsbxdc`；数据MIT，仓库Apache-2.0。
- 原镜像：`jyangballin/swesmith.x86_64.google_1776_textfsm.c31b6007`；镜像版本、初始任务快照、原始故障patch和96个用例ID见[environment.json](environment.json)、[task_source.json](task_source.json)。初始结果2失败/94通过。
- 与Canary8、Dev24、Final57的任务ID交集均0；89条元数据未发现TextFSM仓库、镜像或可识别派生题，现有382行视图也无该ID。该范围不能证明任意近重复不存在；没有读取Final答案或结果。
- 两候选为`gpt-6.1-sol:low`和`gpt-6-luna:low`，正式池仍保留Flash。使用原mini-SWE-agent 2.4.6的`DefaultAgent.run/step`和原生`DockerEnvironment`，每对初始消息、快照、Agent配置和工具协议相同；30步、输出4096，教师关闭。原生API分别为Responses和Chat Completions，供应商内部上下文与物理缓存是否相同未知。

## 任务级：两者独立完成，质量相等下的实测成本偏好

| 候选 | 生成/实际工具 | 原96项Verifier | 运行秒 | 模型费USD |
|---|---:|---|---:|---:|
| Sol low | 9/9 | 96通过，Submitted | 257.976794 | 0.1969126 |
| Luna low | 12/16 | 96通过，Submitted | 126.236596 | 0.00529922 |

两者全部请求/返回身份匹配。Agent自然生成的附加用例和临时复现文件保留在轨迹/patch中；终局另将各自源码patch应用到同一初始快照，排除Agent新增用例，执行原96项。两次均通过，见各Episode的`original_verifier.json/original_verification.txt`。没有重跑Agent或旧成功题。

因此本题可形成`TASK_LEVEL_PREFERENCE`：在相同已验证完成结果下，选择实测模型费更低的Luna low。没有任务级质量胜者，也不由单题推断稳定的速度、质量或成本优势；这不是正式Dev/Final成绩。

## 步骤级：真实过去相同，监督只覆盖一个native step

从上述Sol实际轨迹保留前缀6和7，通过原生环境重放已经发生的命令恢复快照；消息与状态只含该步之前的信息。两个候选各执行一次原`DefaultAgent.step`，之后恢复原测试文件并运行同一96项。

| 前缀 | 候选 | 新生成/新工具 | 一步后原Verifier | 秒 | 模型费USD |
|---|---|---:|---|---:|---:|
| 6 | Sol low | 1/1 | 2失败/94通过 | 75.756121 | 0.0320335 |
| 6 | Luna low | 1/1 | 2失败/94通过 | 19.051087 | 0.00212278 |
| 7 | Sol low | 1/1 | 96通过 | 26.676898 | 0.0256854 |
| 7 | Luna low | 1/1 | 2失败/94通过 | 19.984998 | 0.00069166 |

前缀6中Sol先增加用例，尚未改故障函数；Luna发出`apply_patch`，镜像没有此程序。两者均无即时完成，不为低价失败者生成选择标签，保留为`OBSERVED_OUTCOME_ONLY`。

前缀7中Sol用Python把`result=[]`移到循环之前，原96项通过；Luna再次使用不存在的`apply_patch`，源码未变。因此取得1条`STEP_LEVEL_PREFERENCE`，偏好Sol low满足“一步后原Verifier通过”的目标。其后完整Episode结果未知，不能复制任务级Luna胜负或声称Sol完整Episode优于Luna。

前缀6原指标将6条过去工具也算入7次调用，已依据本次1条原工具事件更新指标与原Ledger，仅更新两条记录，没有新增Episode或API计数。

## 有效训练材料

| 材料 | 数量 | 当前用途 |
|---|---:|---|
| `TASK_LEVEL_PREFERENCE` | 1 | 原始任务状态，质量相等下低模型费目标，Luna low |
| `STEP_LEVEL_PREFERENCE` | 1 | 前缀7，一步即时Verifier目标，Sol low |
| 已发生的候选结果 | 6 | `OBSERVED_OUTCOME_ONLY`，不混入choice目标 |
| 完整K=3最优动作/同模型不同Effort偏好 | 0/0 | Flash未访问，实际档位仅low |

[supervision.jsonl](supervision.jsonl)保留不同监督类型、候选、真实反馈、费用与来源；[training_delta/summary.json](training_delta/summary.json)由原`v9.training.prepare`生成2条S1格式目标，并明确跳过前缀6的无动作目标记录。原`serialize_training_record`实际消费两条，问题ID与instruction分别为任务级和步骤级，不共享同一种终局目标。

完整过去消息、教师是否存在、能力快照和候选集合均保留；候选结果、费用与偏好只在监督/来源部分，不进入决策前状态。新两条教师均null，绑定AA v4。原390实体和四条教师未改，已纠正未知终局的382行视图未重加工：复用Train196/Val186，加新选择目标2条可组合为Train198/Val186。两条来自1个任务，不能当2个独立任务或将旧13,214候选全部算为新增。

## 费用、时延、Flash与教师

25次真实生成共input385,895/output14,866 Token，output已含reasoning；模型费合计`0.26274516 USD`，全部调用已计原Provider/Ledger。已知缓存读288,836 Token，1次缓存读缺报、14次写缓存缺报，缺失保持null并按原计价规则处理。模型费使用请求型号的原Registry费率，来源见[request_model_rates.json](request_model_rates.json)；供应商实收与工具/容器/Router资源USD未知，不能当现金账单。

表中运行秒含原Agent及当次验证，容器创建和后续独立原Verifier耗时另见环境/Verifier记录；不把这些串行运行当纯模型速度比较。失败命令及其生成费用全部计入。

本轮两个现有账户`/models`均HTTP200，未列Flash；既有jiji 404/另一账户503的`model_not_found`证据仍在原实验，没有重复相同失败POST或替换成27B。真实动作空间明确K=2，Sol原生没有none。

教师本轮0请求/0费用；原单次有效Sol教师`0.0189335 USD`及低频触发规则保留，没有复跑。净收益需在独立真实Dev任务上用相同协议进行有无教师对照，完整费用和时延包含教师，不从一次成功短评推断收益。

## 训练与研究接续

台北20:42:35服务器实读：两组活动训练0，原队列`PAUSED_USER_REQUEST`。F01–F13及Kev R01–R16完训/固定Val完成，代表F11-e01/R11，Serving仍F05/epoch_01与原Kev导入适配器。旧F14非有限失败归档保留；遗留控制器尝试的新F14/F15在初始化报`UnboundLocalError`，F16在进入训练前停止，均无新更新。详细进度、前三及旧加训负结果见[原训练报告](../../training/training_research.md)。

新监督已有可消费格式，但只有1个任务、2条局部目标，没有同模型Effort差异，也没有新增教师条件监督。当前不启动新微调；Laya encoder/choice head与Kev LoRA/pointer head均未更新。后续保留旧S1原身份/偏好，沿原编码输入教师截止前短评与指定AA卡；明确保留状态内容和待更新参数，再用固定Val的Accuracy/Loss/Brier/ECE及独立真实Dev Episode判断收益，不重复已退步的旧V9配方。

AA仍固定`20261031T072548885180Z-v4`：Sol/Luna Max各10项，Intelligence v5.0为54.5087338138148/27.7552004938153；low/none/托管Flash及Coding/Agentic综合指数缺测，本轮未刷新。五RQ、八图十二表不变，本次训练材料不填正式效果表。

剩余研究工作是更多独立训练任务上的同条件候选反馈、可用Flash渠道、跨Effort真实目标、训练输入有效覆盖及独立Dev上的动态路由/教师净收益。原最终Test未执行，原固定Val前三不当最终分。

本轮源码、六份规划文档、训练报告和结果已同步A6000原目录；原训练序列化入口在服务器实际读取2条新目标，相对链接有效，没有加载权重或启动训练。三个临时TextFSM快照与采集目录已清理，官方基础镜像、任务源实体、真实响应、失败和训练记录保留，环境可据原镜像与记录重建。
