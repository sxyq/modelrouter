# 真实K=3首批Harbor开发执行：两模型身份有效，净收益尚未成立

**负责人后续说明**：hy4与hy4-preview是同一个模型，当前Provider已将这对名称作为允许返回别名，仍发送hy4并保留实际返回hy4-preview，不使用单后端映射。下文严格名称相等导致的身份问题属于当时执行事实，不再作为当前模型不可用的依据；两条旧HY4轨迹已在动作执行前结束，原Reward仍null，不能据名称说明改为任务成功。本批实际16次Router前向；候选仅Luna low／Terra low／HY4默认，没有Max，不能据此评价同模型档位选择。原数据集实际为Terminal-Bench 2.1，不是2.0。

## 1. 整体目标与本批范围

负责人正式转向真实K=3 Luna／HY4／Terra、Model×Native Effort、缓存连续性、Laya／Kev原始与训练代表、GPT-6 Luna教师，以及含全部开销的完整Episode收益。起点main为7631b5fd12bc3518c74a0cb22b0892b370d3b05d。旧40条K=2监督、旧STEP、Val及完整任务没有重做或改成联合标签。

复用Terminal-Bench 2.1、Harbor 0.24.0、Mini-SWE-agent 2.4.6、原PolicyModel、原任务镜像及Evaluator。extract-elf与git-leak-recovery都是已开发暴露任务，不作盲评价、不入Train。五策略×两任务共10个主实验位置，seed42、15步、每次输出4096，原Agent／Verifier各900秒，教师关闭。所有工具和验证在A6000 syy用户Docker，4核／8GiB TCG；Router用CPU，没有抢GPU或替换Serving。

公开指标见[summary.json](summary.json)、[episodes.json](episodes.json)、[router_versions.json](router_versions.json)。完整请求、响应、工具正文、账本及原Trial仍在本地受保护结果位置，不发布。历史研究入口为[results/README.md](../../README.md)。

## 2. 实际模型与档位

| 请求模型 | 实际渠道 | 协议／首批动作 | 返回事实 |
|---|---|---|---|
| gpt-6-luna | luna-codegoai／codegoai.com | Responses／low | 身份诊断保存响应及21次完整Agent生成均返回精确ID；另有2次无完整结果 |
| gpt-6.1-terra | terra-jiji／www.jiji.cc | Responses／low | 身份诊断保存响应及13次完整Agent生成均返回精确ID |
| hy4 | hy4-oranexa／oranexa.top | Chat Completions／参数省略 | 诊断及两任务均返回hy4-preview，不能当正式HY4；身份不符的工具动作未执行 |

初次诊断有两项共享Registry初始化错误，发生在HTTP前；Luna强制SSE和Terra合法error:null又使本地解析异常。复用保存响应恢复两项身份与用量，没有重发这两个诊断。三模型诊断实际生成请求各一次。诊断Luna／Terra的HTTP状态未保存，不能由completed推填200；后续Agent真实状态另有记录。

34次匹配身份的完整Agent生成均由供应商返回low。这个返回字段不是计算强度的独立证明。本批执行动作集合只有Luna low、Terra low和HY4默认；当前默认Registry的13组合不代表13组合都已实测。HY4 none仅表示不传思考参数，不表示关闭思考。没有开展同模型low／medium对照。

Luna／Terra发布上下文1050000、输出上限128000；HY4官方TokenHub参考1024000／64000，渠道容量及多模态未实测。模型价格沿已登记官方短上下文参考，HY4及三渠道实收未知；不能宣称已建立低／中／高实际经济排序。

原初始能力快照沿用了Luna的旧jiji标签，但真实请求一直绑定luna-codegoai。运行中更新标签导致第二任务三项启动前ValidationError，均无模型请求；恢复原快照标签后，只接续这三项，原失败目录仍在。最终Registry的当前Luna渠道名称已改为codegoai，不改写原输入或轨迹。

## 3. 原官方完整任务结果

“—”表示原Reward不存在，不能计模型失败。参考费用只按保存Usage与配置费率计算，不是供应商实收；缺失请求费用不填零。

| 任务 | 策略 | 官方Reward | 已知模型参考USD | 完整墙钟秒 | Router秒 |
|---|---|---:|---:|---:|---:|
| extract-elf | 固定Luna | — | 0.00241494，非完整费用 | 119.92 | 0 |
| extract-elf | 固定HY4 | — | 未知 | 39.97 | 0 |
| extract-elf | 固定Terra | 0 | 0.03379760 | 287.27 | 0 |
| extract-elf | Laya F05-e01 | — | 0.00019270，非完整费用 | 90.62 | 9.71 |
| extract-elf | Kev R11 | 1 | 0.00175840 | 536.26 | 311.88 |
| git-leak-recovery | 固定Luna | 1 | 0.00102252 | 208.60 | 0 |
| git-leak-recovery | 固定HY4 | — | 未知 | 45.53 | 0 |
| git-leak-recovery | 固定Terra | 1 | 0.01002740 | 214.39 | 0 |
| git-leak-recovery | Laya F05-e01 | 1 | 0.00216876 | 257.67 | 13.98 |
| git-leak-recovery | Kev R11 | 1 | 0.00753403 | 520.26 | 285.41 |

六个原Reward／CTRF均已由原Harbor实际生成，五通过、一业务失败，不是“成功率5/10”或稳定成功率5/6。Terra的extract-elf两项业务验证为1过1败：输出未覆盖官方要求的参考值比例，是真实业务失败。Luna的同题response.failed与Laya的无完整SSE终止响应没有原Verifier，分别保留UNKNOWN；后者未报告输出预算耗尽，不能推测为档位质量失败。两项HY4身份不符同样UNKNOWN。

真实Agent请求38次，34次完整匹配身份、2次preview、2次用量不完整；54次工具执行，4次工具非零退出，不能仅因退出0宣称业务修复。另有3项启动前Trial及10条早期CLI参数错误记录，没有重复收费生成。官方Evaluator未修改，未对缺Reward终态补造奖励。

## 4. Router原始与训练代表

| 架构／版本 | 精确服务器实体 | 相同首个真实输入动作 | 首次含启动秒／纯前向秒 |
|---|---|---|---:|
| Laya原始可执行版 | models/laya-421m | Luna low | 8.081／0.659 |
| Laya训练代表 | runs/MR-FULL-GRADED-P0-DATA-REPAIR-20261012/F05/checkpoints/epoch_01 | Luna low | 8.169／1.094 |
| Kev导入原始版 | models/kev-4b-adapter | Luna low | 73.454／25.711 |
| Kev训练代表 | runs/KEV-V8-COVERAGE-R11/checkpoint | Luna low | 66.476／29.971 |

四个版本真实CPU前向成功，无本地权重、无合成概率。Laya原始版已有官方有效Head；Kev起点是项目微调前官方导入Adapter，不是裸Qwen基座。R11与在线导入Kev不是同一Adapter；以精确路径识别，通用base_revision不能唯一标识版本。

F05-e01和R11只是事前暂定开发代表，不能确认当前K=3最优。旧固定Val中F05与F11配方不同，旧STEP只对应原Sol／Luna；没有据本批已看结果选择新父Encoder、神经训练或Serving版本。四次前向改变概率但不改变动作，不证明训练贡献。

原Pointer按完整action_id返回模型、档位及概率。实际输入包含新模型卡和价格参考，不包含候选动作后的验证；候选Marker与返回组合对应。首个输入Laya原始版512编码Token、丢701状态Token，F05版1024、丢189；Kev编码1046并返回89输出Token。截断有直接记录，但没有证明它是选择错误原因，也没有做未授权摘要实验。

两个动态策略共16次原权重前向，全选Luna low、切换0，累计CPU路由620.979秒。Laya两题分别2／5次；Kev分别4／5次。加载、纯前向和墙钟分别存于episodes.json，CPU结果不等于GPU部署性能。

## 5. 缓存、费用与教师

Agent已知输入＋输出322322 Token，已报告缓存读取180115；加三次身份诊断为345373已知Token，参考费已知部分合计$0.06117485。未报告的生成用量、部分缓存写入、HY4费率、全部供应商实收及CPU／GPU／VM美元费用仍未知。Reasoning是output的子集，不重复相加。

同模型连续请求既出现缓存命中，也出现0命中。新continuity沿原Hook／Serializer记录前后选择与请求模型、渠道、上次输入Token、前缀连续性、读写缓存；第二任务已有真实记录。没有为第一任务补造这些新字段。真实重发Token、跨模型物理KV共享和额外切换费用保持null。供应商报告缓存读取是观察，不是缓存因素的因果消融。

git-leak-recovery四个有效策略同获1，固定Luna参考费最低。Laya比固定Luna多$0.00114624并增加13.983秒路由；Kev多$0.00651151并增加285.407秒路由，不能宣称动态净收益。Kev在extract-elf通过但固定Luna遭供应商异常，不能据此把通过归因于模型选择；它也只是全选Luna。冷热环境与不同实际轨迹不能被拼接成收益。

教师已统一为真实API GPT-6 Luna low，保留原摘要职责与费用记录。本批教师关闭、触发0，没有教师效果对照。模型／Router未全部正常，未机械增加原始Router完整Episode、更多Effort或教师组合。真实K=3正式联合监督新增0，旧40条保持。

## 6. 原训练、空间与运行资源

原38组实际run记录25完成；queue.completed_runs仅22的旧登记不能代替实际记录。F15物理epoch_01仍61180/122360，model、optim_state及recovery_state保留；旧63996日志不当新保存点。

本批沿原入口及原GPU锁尝试接续。前台等待进程在SSH断开后消失；随后单个用户级托管队列曾有效等待锁，之后也消失。可读日志仅有启动，未取得退出原因或新计算更新，最新无队列／Worker，不能称安全接续成功。没有抢占ComfyUI、停止合法作业、添加重启循环或定时任务。

实际删除完成组F05／F11各epoch_01、F12／F13／F14各epoch_01与epoch_02的8份optim_state.pt，合计26947303464字节（25.10 GiB）。删除项无法直接恢复原优化器；全部模型参数、结果、竞争版本、原始与代表版本、F15恢复及未来父实体保留。由于新池最优未确定，没有删除其他唯一竞争模型，不宣称只剩四个权重。

Serving保持原PID327621、F05-e01及导入Kev，health正常；只有研究源码更新，无重启或权重替换。本批最终用户容器0，9镜像保留，其中新增extract-elf／git-leak-recovery有明确下一阶段用途。VM磁盘、socket与原7镜像未删。原验证资料已取回，本批VM临时Mac路径日志副本及临时转发清理，原私人证据保留。

## 7. 科研判断与五RQ缺口

当前取得的是首批真实请求、工具、官方完整终局、原始与训练版本前向、真实缓存观察及开销证据。三模型配置已接入，但HY4正式身份未成立，所以不是有效三模型质量排序。

没有证明原始与训练Router的完整Agent差异、同模型档位质量差异、跨模型缓存因果收益、独立条件分工或完整净收益。两题都是开发观察，不能当全流程未见泛化。当前数据不支持自动STEP011；旧权重能输出组合不代表已学会新池。

RQ1仍缺三有效身份的完整成本反事实与独立净收益；RQ2缺HY4费率及有限真实Effort；RQ3缺获批后的任务／自然转折真实轨迹，旧删调用子集不作实测；RQ4原始／训练、教师及T/M/H／监督正式矩阵仍未完成，Demo仍模拟；RQ5缺事前独立不同工作负载边界。研究应继续真实K=3，不回到单后端映射或只追K=2标签数量。

## 8. 下一批关联执行

完整提示词见[next_execution.md](next_execution.md)。优先：有效HY4身份及有价值的完整反事实；首批正常后有限原始版／档位／教师与缓存对照；原队列终止来源和合法新联合监督、独立选择。任务级与自然转折新增正式臂仍需负责人明确批准，Serving不自动替换。发布仅包含必要源码、脱敏结果及实质变化规划，私人响应、账本、Key和权重不提交。
