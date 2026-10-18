# ModelRouter · A6000 IP:端口看板部署与当前双模型训练科研验收
> 2026-10-19 01:24 CST 现场报告 + 当前 GitHub main `4c47209857e97e39b5de1fa71c9bf961327c8633` 核查。该文档是**执行要求/现场证据口径**，**不代表服务器 8765 已部署或此刻 SSH 状态已验证**。用户要求浏览器直接访问服务器 IP+端口、尽量减少页面文字但保留完整图表；现有本地 CC Switch/Key 不更改，唯一边界是不能 Git 上传敏感凭证。

## A. 当前状态及科研结果决策（严格区分同口径）

| 对象 | 2026-10-19 01:24 CST 执行报告 | 可报告判断 |
|---|---|---|
| Laya F06 421M | E1 Chunk 268/361，34,304/92,280 optimizer steps，曝光 2,195,456，train chunk loss 0.4906 | 训练推进；尚无 F06 E1 固定 S1/S2/S3 Val；Loss 下降不等于超过最佳基线 |
| Laya P0_B03 e02 | 固定 S1 561 条 Accuracy **68.63%**、Loss 0.6039 | 同口径历史最高已保留权重 |
| Laya F05 e01 Serving | 固定 S1 561 条 Accuracy **67.56%**、Loss 0.5978 | 当前上线的是 F05 不是历史最优，也不是 F06 |
| Kev C03 Qwen3.5-4B | 5,130/16,857 steps、20,520 records、近期 train loss 0.980–1.280 | 真实 LoRA 主训练在推进；没有此轮固定 2,437 Val、ECE/NLL/Brier 对照 |
| Kev old adapter Serving | 固定独立 Val 2,437 条 Accuracy **87.26%**、NLL 0.5162 | **不同于 Laya S1 561**；不得直接排名 |
| Kev V8 50-step | `v8_real_finetune.py` 实体加载旧 `head.pt`，真正更改了 `q/k` Pointer 参数；报告 V8 Choice 83.33%，Cache MSE 0.1329 | **单独 Pointer Head 辅助微调 Smoke/小样本实验**。源码每视图最多 100 Train / 30 Val，当前 50 steps，Embedding 使用 Qwen token embedding 平均池化、没有在此路径上执行完整 4B Transformer/LoRA 更新。未见在 Kev 固定 2,437 Val 上的同口径评测和部署兼容性验证；不能宣称 Kev 整体新数据已经带来收益 |
| Benchmark | Harbor Docker daemon 不可由 `syy` 访问，仍 `BLOCKED_PERMISSION_REQUIRED` | 不存在已完成真实官方 Trial；真实 API 烟测 ≠ 官方 Agent 评分 |

报告的“GPU 93%–98%、显存 20,399/49,140 MiB、85°C、285.7W”为采样快照，不足以认定双模型“零算力竞争”；须比较真实 steps/s、各 Run walltime。Kev Router 单请求 5,654.8ms 明显慢于 Laya 183.8ms，应独立分析 CPU/模型装载/缓存/健康检查、避免影响训练；单次延迟不能代表 P95。现有 GitHub `live_status.json`（20:30 CST 快照）明显落后于最新 01:24 现场报告，**不要将其显示为实时**。

## B. 必须部署到 A6000 的唯一看板（无需 Mac 作为服务器）

### B1. 唯一入口与访问目标

- A6000 项目根 `/home/syy/路由`；以 `/home/syy/路由/our-project/dashboard/` 作为**唯一服务器站点根目录**，不 Serve 仓库根 `/home/syy/路由`、`runs`、`models`、`data`、`.ssh` 或任何 API Key 目录。
- **目标内网地址**：`http://10.16.15.202:8765/`。此 10.16.* 是报告中的 **私有内网 IP**，仅当用户 Mac 在相同校园/LAN/VPN 且网络路由、主机防火墙允许才可通过 IP+端口访问；绝不假设外部公网可直连。先检测 `ip -4 addr` 和 Mac 到服务器网段的连通性，IP 若改变须提供真正可达地址。
- 不将既有 Port **8000 Router API** 强行对公网暴露；不改变原有模型 Serving 进程；Dashboard **8765** 应是独立只读服务，不提供训练启停、Shell、上传、模型调用或任意文件浏览入口。
- 先检查 `ss -lntp | grep ':8765'`，不可杀掉其他占用服务。部署仅用 CPU/RAM 和磁盘小文件，**不抢 GPU、不改变训练解释器/运行队列**。尽量使用已有运行库/服务能力，不叠加第二个长期 Watcher。

### B2. 数据采集器必须切换服务器本地源

现 `scripts/fetch_live_status.py` 是 Mac Collector：`fetch_server_data()` 运行 `ssh a6000`，`fetch_serving_data()` 读 `127.0.0.1:8000`，输出 `docs/training-dashboard/live_status.json` 及 `our-project/dashboard/live_status.json`。直接拷到 A6000 不等于能正常实时更新。

1. 在 **当前唯一 Collector** 添加 `--source local|ssh`（或复用同函数接口）明确区分两种数据路径：`local` 模式在 A6000 直接读取 `nvidia-smi`、`/proc`/进程状态、Laya F06 `cursor.json`、Kev C03 `cursor.json`/`train.log`、候选队列文件、`run.json`/`epoch_metrics.json`、本地 `http://127.0.0.1:8000/health`/`models`；`ssh` 模式留作 Mac 开发兼容。网络请求须有小超时与错误分类。
2. 只从真实文件/机器读当前值。特别区分 **last_poll_time** 与 **last_model_progress_at**：即使每 5 秒刷新 JSON，训练 Cursor 没有推进超过实际预期窗口时必须显式 `STALE`，不能凭 `updated_at` 变新证明模型仍在训；模型进程可能存在却无梯度更新的场景应给 `STALLED`。
3. Run/Epoch/Best Acc、Brier、NLL/CE 标签需从**物理 metrics + 固定 val 来源**动态读取；修复现有 GitHub `live_status.json` 的 Laya `best_s1_acc=0.6738` 与已确认 P0_B03 0.6863 不一致、F02/F04 Val Trend 可疑重复数值、F05 e02 与 e01 Serving 混用以及 Kev Val 样本集口径。
4. 更新 Live JSON 的过程用“临时文件写入 + `os.replace` 原子替换”，给 `Cache-Control: no-store` 或 UI 加时戳防缓存，输出只含指标/安全索引，不含权重文件、真实 API Key、服务器私有日志、客户 Prompt、Git Credential。历史 JS 分片中已公开或静态的数值明确标记 `HISTORICAL_STATIC`。
5. 复用现有 UI：左右对称 Laya/Kev 当前训练曲线、真正箭头流程图、38-Run 历史图、133 Checkpoint 版本树、基线比较、GPU时序、模型池/Token 定价与 STALE 标记。文字少，但**不删除图表和筛选**。外部基线 Mock/Host 与真实官方 Score 必须分开；C03 训练不显示 Kev C02 旧 Val 为当前结果。
6. 服务器采集器约 5–15 秒更新一次轻量指标，不扫描数 TB，不每 5 秒重新递归生成大型 checkpoint 资产索引；每个 Epoch/Checkpoint 结束才更新昂贵的历史指标汇总。

### B3. 运行方式与网络边界

- 服务器独立启动 **静态只读站点**（Python 标准库静态服务器或已有 Nginx 静态服务皆可），监听服务器实际内网接口的 IP:8765，不能只绑定 `127.0.0.1`。选择现有操作权限可运行的方式，不为了这个服务取得 Docker root 权限。
- **访问控制**：部署于可信内网或 VPN，按需要只允许负责人设备/网段访问该端口，并可加 HTTP 认证；若需跨不可信公网，必须采用受控 HTTPS 与认证，不能仅 `0.0.0.0:8765` 裸开。服务器上 Web 根目录必须只有已脱敏静态资产；小范围端口白名单，不开放 8000、SSH、Prometheus/debug 等其他服务。
- 采用单实例的受控用户级服务（已有 process manager / `systemd --user`，若有权限；否则受控 `nohup`），完成后实际 `ss -lntp`、`curl -I http://127.0.0.1:8765/`、`curl http://127.0.0.1:8765/live_status.json`；由 **用户 Mac 实际浏览器访问** `http://10.16.15.202:8765/`，记录响应码、截图、5–15s 训练进度变化。若 IP 私网路由或 firewall 阻挡，记录 NETWORK_BLOCKED 及具体原因，不宣称已向用户可达。
- 启动后测试重启自恢复、长时间数据刷新和训练不受影响；看板本机 8765 旧入口可以留兼容，但真实数据以 A6000 `our-project/dashboard/` 为唯一权威。
- 只提交无 Secret 的小型部署脚本与示例、systemd user unit / 配置、截图脱敏摘要、运维文档及 commit；不要把私有日志、原始结果或 Token/Key 写进 UI/仓库。

## C. 需并行推进的模型科学验收（不干预当前训练）

1. **Laya F06**：在当前 Epoch 0 结束后立即对冻结 561 条 S1 和合法 S2/S3 进行真正 Val，记录 accuracy、Val loss、Brier、ECE；与 **P0_B03 68.63% 同口径最佳** 和 **Serving F05 67.56%** 比较。未超出不伪报提升，训练继续至预定自然终点/最佳保存。
2. **Kev C03**：真实 16,857 steps 自然完成后运行冻结 2,437 Val（Accuracy/NLL/Brier/ECE），检查实体 head/LoRA/tokenizer 与恢复；接续 C04/C05/C07/C09 必须逐个真实验证科学变量，不仅构建队列文件。现 C03 未完成，当前 Kev Serving C02 与 C03 指标独立标注。
3. **Kev V8 辅助微调**：现 `v8_real_finetune.py` 只在 50 步、每视图 ~100 Train / ~30 Val 的独立 `q/k` Pointer Head 路径修改真实权重（使用非上下文化的 token embedding mean pooling），**没有验证完整 Qwen3.5-4B LoRA 加权训练**。把它标为 `POINTER_HEAD_V8_PILOT`，不能等同 4B 正式 V8 训练。应以真实 `kev.model.admit` 或等价生产态上下文表征连接训练；在固定原 Kev Val 及新增 V8 Val 上分别评估并进行 Serving 加载无回退短测试后才能晋级。另须有 Laya 独立新数据真实模型权重微调方案和证据，不得沿用旧 SHA256 Aux Smoke 当作 Laya 提升。
4. **Agent/Harbor**：Docker 权限仍是授权阻塞，不能假装官方 `AGENT_EVALUATED`。负责 Runner 需向管理员申请合法授权或采用已授权受限 sandbox；不因看板部署提升 Docker 权限。正式 RouteLLM/SR-KNN 必须来自真实上游合法算法/训练数据而非 prompt-length / step heuristic。
5. **限额与服务质量**：后续 benchmark 在当前 Kev 服务单次 5654.8ms 情况下应记录 P50/P95 和失败率，不靠一例断言稳定；Token 账本 391,634/1,000,000（报告快照）尚未证明并发原子预留，不能命名 `hard_gate_verified`。外部 API Key 不需重新安排，只保持不能 push 到 GitHub。

## D. 两位子代理与交付验收

**主 Agent**：确认 A6000 健康训练、只读观察、进行模型 Val 口径审核、统一 commit。**子 A**：部署服务器看板 8765、改 collector local/ssh 模式、浏览器/网络可达性和只读安全。**子 B**：固定验证与 V8 对照/源数据及 Serving 一致性；Benchmark/Docker 权限仍按既有单独计划，不以未授权环境无法跑官测阻断看板部署。

最终交付至少：**① 服务器上真实监听的 IP:8765 和可从 Mac 打开的页面；② 5–15 秒真实更新、STALE 判定与前端截图；③ 训练前后 PID/Steps 仍增长、Port 8000 不变；④ Laya F06 E1 与 Kev C03 当前独立固定 Val 的真实完成状态；⑤ Kev V8 Pilot vs 正式模型区分；⑥ 修订后的科研成绩表、图形化看板、Git SHA。** 没有实际浏览器验证，不能宣布“IP+端口部署完成”。

