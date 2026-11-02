# ModelRouter V9 · 真实质量监督与独立动态对照执行记录

接续 main `12cbea5d2e6771aa94b502838dae7d7519e84eb4`。已复用 Code Generation 四个 Luna 账户，完成五组成对比较、一个真实 Modify 质量赢家、STEP_003 训练及一个独立 Dev 任务的三策略官方对照。动态收益尚未证明。数字见 [summary](summary.json)，本次发布 SHA 见 Git 历史与最终回报。

## 1. 整体科研目标

让 Router 根据真实 Agent 决策前状态选择更合适的模型，在独立任务中取得质量—成本收益。本轮先取得实际动作质量标签，再沿原 Trainer 更新参数，最后比较固定 Sol、固定 Luna 与动态 Router；任务环境、参数更新和实际选择效果分别报告。

服务器、GPU、训练与付费模型授权已使用；预计需要约一亿付费 Token 时才通知，该数不是使用目标或默认预算。共享 GPU 协调、健康训练、原 Serving 与私人凭据继续保留。

## 2. 当前真实进度

### 账户与正式源码

[Provider 结果](provider_validation.json)保留账户补充前一次 `GROUP_DISABLED` 403；它不代表当前账户状态。随后从 Code Generation 正式 `ProviderRegistry` 读取四个现有 Luna 账户，全部实际完整返回 `gpt-6-luna`：aihope、codegoai、colink、qidian7。aihope 也在新 Dev 中完整返回 `gpt-6.1-sol`。证据范围为精确请求/返回 ID，没有查看供应商物理权重。

只修改两个正式源码：

- `our-project/code/src/modelrouter/providers/provider.py`：复用原账户加载及健康/负载/延迟排序；发生本轮已见 HTTP 或不完整响应时换同模型账户，不重试同一失败端点，不换候选模型。每次物理请求仍单独计量，失败与未知用量保留。用量文件锁仅覆盖写入，不再把整个网络请求串行化。
- `our-project/code/src/modelrouter/benchmark/harbor_agent.py`：传递原配置中的流式选择与账户尝试信息。Luna 发生空 SSE 后针对性诊断非流式，最新固定 Luna Dev 使用非流式；其他默认仍为流式。

私人配置只引用现有账户工程及 Sol 端点，没有复制 Key、改 Code Generation 工程或改供应商权限。原 Alias 路径保留，本轮真实比较没有用 Alias 替代 Sol/Luna。

### 五组成对比较与一个合法新标签

同组原历史、初始故障代码、工具接口和原测试范围一致，教师关闭；当前动作、未来反馈和参考补丁未进入决策前输入。候选独立 Docker 执行，原测试在正式评价前保持原内容。[新赢家比较](t15-async-timeout-diff-modify/comparison.json)与各分支 observation 保存逐项 PASS/FAIL/ERROR/SKIP/UNKNOWN 和动作文件。

| 状态 | Sol 原范围通过 | Luna 原范围通过 | Train 结果 |
|---|---:|---:|---|
| Records：原 Luna cutoff12 | 23/24 | 23/24 | 双方未完成，无标签 |
| async-timeout：原 Luna cutoff8 | 29/32 | 29/32 | 双方未完成，无标签 |
| async-timeout：观察文件/版本后的下一 Modify | 29/32 | 29/32 | 双方未完成，无标签 |
| async-timeout：再观察 git diff 的 Modify | 29/32 | 32/32 | 新增 Luna 质量赢家1 |
| PyBaMM：原 cutoff27，Test 观察 | 6/6 | 6/6 | 不进入 Train |

四个 Train 状态来自两个已有任务，不是四个新独立任务。async-timeout 新赢家真实修改 `async_timeout/__init__.py`，原 F2P3 全部恢复、P2P29 全部保持；Sol 只继续读取，没有新代码修改。双方参考模型费 Luna 0.000376015 / Sol 0.012323 USD。新增仍为原 `STEP_LEVEL_PREFERENCE`、`MODEL_ONLY`，没有引入局部进展目标。

PyBaMM 两方均修改 `pybamm/util.py` 和 `pybamm/parameters/parameter_values.py`，原六项全通过；参考模型费 Luna 0.002379175 / Sol 0.048316 USD。原固定 Test/L3 身份不因本次结果改为 Train；这组仅说明原状态可以真实执行。16 条历史工具重放退出码对应，不声称历史输出字节完全一致。原缺失的 tool_call_id 只在传输副本按记录顺序关联。

现有来源关系保留：PyBaMM 30 条 Test/L3 引用；Argo 121 条 Train/L2 引用但本机原镜像缺失；Gym 轨迹许可未声明，仍仅观察。不重做上一轮四组完整任务关联，也不为了本轮大量下载 Argo 环境。

### 新训练与真实 CPU 输出

[训练材料摘要](training_delta/summary.json)：原19偏好/74行保留，新质量行1，累计20偏好（任务级9、步骤级11），实际训练75行。原 Prepare/Serialize 生成新增行，沿原 `run_sweep_experiment` 和共享 GPU 文件锁完成 `V9_LAYA_STEP_003-e01`；父 STEP_002，1轮、10次 pointer head 更新，Encoder 未更新，教师0。训练75行均实际输入、完整状态/能力卡75。

| 模型 | 固定 Val561 Accuracy | Loss | Brier | ECE |
|---|---:|---:|---:|---:|
| F11-e01：沿用原结果 | 0.6898 | 0.5941 | 0.4085 | 0.0378 |
| STEP_002-e01：沿用原结果 | 0.6898 | 0.5941 | 0.4085 | 0.0383 |
| STEP_003-e01：本轮 | 0.6898 | 0.5940 | 0.4084 | 0.0376 |

训练9.819秒、Val12.776秒、保存2.080秒，整轮24.708秒，GPU峰值2487.53 MiB。846196996字节权重仅留服务器原 runs 目录；本机只取回 [run 元数据](laya_step_training.json)。

对新增赢家状态用原 CPU Adapter 分别前向一次，[结果](cpu_router_comparison.json)：

| 模型 | Sol概率 | 实际选择 | 前向秒 |
|---|---:|---|---:|
| F11 | 0.5640 | Sol | 1.169 |
| STEP_002 | 0.5587 | Sol | 7.414 |
| STEP_003 | 0.5589 | Sol | 7.654 |

三次均 `fallback=false`，但正确质量赢家是 Luna；新模型尚未学会这条选择。原 STEP_001 字节仍未找到，STEP_003不冒充恢复。Serving 未替换，Kev/F14未重训。

### 一个独立 Dev 的官方三策略对照

[Dev 结果](dev/summary.json)保留共9个 Episode：前两批6个账户/传输失败没有原 Verifier 终局，不算模型质量败者。依据已发生的问题调整账户与用量锁后，同一 `distribution-search` 原环境完成三策略，上游 Harbor Docker 隔离及未修改官方 Evaluator 均生成真实奖励/CTRF。Dev 不进入 Train。

| 策略 | 完整生成 | reward | Episode模型参考费 USD | Job墙钟秒 |
|---|---:|---:|---:|---:|
| 固定 Sol | 3 | 1 | 0.018070600 | 166.208 |
| 固定 Luna | 11 | 1 | 0.005740635 | 235.985 |
| 动态 STEP_003 | 3 | 1 | 0.015223300 | 161.303 |

新批次全部请求/返回 ID 对应、Usage完整、Provider异常0、fallback0。动态 Inspect2/Modify1均选Sol，切换0；Router总段41.289秒，其中初始化30.021秒、前向10.566秒，初始化1次/复用2次，两次复用前向外共21.062毫秒。

三策略该题均成功。动态比本次固定Sol参考模型费低，但候选选择没有改变，采样/缓存差异不能归因于 Router 改善；动态仍比固定Luna贵。这一个独立题不能代表整个 Dev 成功率或完整 V9 收益。

## 3. 当前还剩多少核心工作

当前执行中的账户、真实动作比较、新标签准备、最小训练和独立官方对照已完成，仍有三块核心研究工作：

1. 扩大真正 Train 的步骤质量覆盖；Modify有效1、Inspect有效0，一条新标签不足以支撑泛化。
2. 让训练后的实际输出对应质量赢家，再用更多独立任务量化候选选择带来的质量—完整成本收益；本轮未证明动态收益。
3. 完成论文所需的范围与证据，包括真实K3、Native Effort、教师净收益及跨任务结论。当前K3/Effort目标仍0。

Gym许可、Argo本机镜像及原STEP_001实体分别是来源资料、环境和历史资产缺口，不写成技术不可行，也不妨碍本轮已完成的真实比较。

## 4. 下一步三项具体任务

第一：在已有镜像和真正Train任务中寻找未比较、具有新修改机会的状态，按原严格一步目标采集质量差异；使用现有Sol/Luna账户池和原测试，不重采相同失败状态。

第二：分析当前新增赢家仍被选成Sol的输入与训练输出，在原Trainer内采用已有合法监督开展有依据的更新；明确需要更多标签还是更新训练参数，不以相同Accuracy宣称成功，不自动替Serving。

第三：取得实际更合理的选择后，用更多独立Dev任务比较固定Sol/固定Luna/动态，记录完整Episode用量、未知实收和Router开销；K3/Effort扩展与Inspect独立信息价值定义另按实际方法范围推进，不混入旧S1。

## 5. 实际结果与下一轮建议

本轮物理请求58（Sol35、Luna23）；完整返回50，其中Agent49、诊断1；成对生成10，可信比较5（Train4/Test观察1）；原记录中的工具完成事件48。非流式15，教师0。原范围验证20加官方Dev3，共23；真实CPU前向12（人工三版本3、三批动态Dev共9）。

8次Usage未知。已知输入455741、输出含reasoning41940，已知合计497681 Token，已知模型参考费0.632776675 USD；完整总用量、完整总费及供应商实收均未知，不补0。Reasoning只计一次。非流式诊断先因传输中带保存轨迹的exit记录返回400，原失败保留；只在诊断副本移除exit后完整返回，没有给产品添加额外过滤路径。

Luna现可用；新增合法质量赢家1、有效Modify1/Inspect0；新训练1；完整独立Dev三策略均成功，但动态收益未证明。当前没有需要用户再提供费用许可或账户的执行依赖。下一轮应围绕稀疏步骤质量与新模型仍选错展开，而不是继续重复账户探测或环境参考验证。

局部修复进展及Inspect信息价值仍是独立方法建议：前者需固定原测试ID完整状态、可比较修复集合且无新P2P回归；后者可将两候选的真实读取结果交给同一固定Sol后续一次修复，再用相同原范围及完整费用衡量。未将这些建议当作已有训练目标。

## 6. 通俗解释与保存

环境能运行，表示模型可以真正改代码并由原测试评价；Router参数已更新，表示新合法标签实际进入训练且权重保存；Router选择更好，要看它是否选中实际赢家，并在独立任务上带来收益。本轮前两件已发生，第三件仍未证明。

最后已记录服务器取样时间为2026-11-03 01:15:49（台北）：健康F14继续活跃，原Serving health200、两模型loaded/verified；服务未重启，健康训练未终止。本任务Docker容器均结束，临时脚本/派生输入已清理，完整训练材料、原失败和私人响应留原位置。

公开提交只含两处源码、规划、脱敏摘要、原测试报告及训练/CPU元数据；私人Key/配置/账本/raw响应、完整历史材料和物理权重不提交。用户Trainer/tests、原19/74、历史删除及Fig.2保留；没有额外测试、模拟、未来调度、PR或CI。
