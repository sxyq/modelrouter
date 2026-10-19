# ModelRouter 官方 Benchmark 运行说明

更新日期：2026-10-19。当前正式 Agent 评测状态：`BLOCKED / NOT_EVALUATED`。

## 当前证据

唯一 Python 环境为 `.runtime/benchmark-venv`，已安装 Harbor 0.24.0 与 mini-swe-agent 2.4.6。

本轮只调用了一次 Oracle。Harbor 返回退出码 1，用时 2.21 秒，原因是 Mac 没有可用 Docker。没有官方 Job ID、Trial ID、Verifier 或 Reward，也没有生成模型调用。原始日志保存在：

`our-project/results/iterations/20261019-v10-oracle/commands/`

记录器曾在命令结束时发生参数重名错误；现有日志已用于收尾，未再次启动 Oracle。该轮的 `resume_state.json`、`review.md` 与 `next_iteration.json` 已保存。

A6000 已有 Docker 29.4.1、RootlessKit 2.3.6、Rootless 安装工具、slirp4netns 和 fuse-overlayfs。个人账户有 subuid/subgid 范围，但宿主没有 `newuidmap`、`newgidmap`；真实 `rootlesskit true` 报 UID/GID 映射失败。个人 daemon 与 socket 均未创建，安装工具的 `install` 未执行，未下载镜像。官方说明要求宿主提供具有相应权限的 uidmap 工具：[Docker Rootless](https://docs.docker.com/engine/security/rootless/)。本轮授权限定个人用户空间，因此安装分支保留 `BLOCKED`，未使用 sudo 或改动宿主权限。

## 唯一入口

从仓库根目录调用：

```bash
.runtime/benchmark-venv/bin/python -m modelrouter.benchmark preflight
.runtime/benchmark-venv/bin/python -m modelrouter.benchmark run --task fix-git --agent oracle --iteration-dir our-project/results/iterations/NEW_ITERATION
.runtime/benchmark-venv/bin/python -m modelrouter.benchmark watch our-project/results/iterations/NEW_ITERATION
.runtime/benchmark-venv/bin/python -m modelrouter.benchmark resume our-project/results/iterations/NEW_ITERATION
.runtime/benchmark-venv/bin/python -m modelrouter.benchmark summarize our-project/results/iterations/NEW_ITERATION
.runtime/benchmark-venv/bin/python -m modelrouter.benchmark export our-project/results/iterations/NEW_ITERATION
```

`run` 默认实际执行；只查看计划需添加 `--dry-run`。上述 `NEW_ITERATION` 是待替换的示例目录。当前环境原因未解决前，不重复运行已失败的 Oracle。

`preflight`、`run` 与 `resume` 共用私人运行配置中的 `docker_host` 和 `DOCKER_HOST`，可以使用 `--docker-host` 覆盖。个人 socket 必须属于实际运行 Harbor 的机器；Mac 上的 `unix://` 路径不会自动连接远端个人 daemon。私人地址放在不入库的 `our-project/experiments/configs/benchmark_runtime.json`。当前没有可用的个人 socket，勿将示例路径视作已部署环境。

原 `run_official_harbor_trial.py` 仅委托同一 CLI。没有另一套 Agent 循环或独立执行器。

Harbor 0.24.0 推荐使用 `-a module:Class` 或 `--agent module:Class`。项目类为 `modelrouter.benchmark.harbor_agent:ModelRouterMiniSweAgent`。`--agent-import-path module:Class` 仍被支持，但已弃用且在普通帮助中隐藏。旧参数与 `-a` 均已通过官方 `--print-config`，退出码为 0；该操作只解析配置，不启动沙箱或调用模型。固定原生实验使用 Harbor 内置 `mini-swe-agent`；动态策略实验使用项目适配类。两个真实模型阶段均尚未运行。

密钥沿用本机配置，不写进命令行和本登记文件。正式运行仍受现有 Token 总限制约束。

## 数据与协议

完整逐字段登记在 `our-project/experiments/manifests/benchmark_registry.json`。每项包含来源、版本、执行器、数据、评分器、Agent 支持、命令与实测状态。

| Benchmark | 本轮数据实测 | 结果口径与当前状态 |
| --- | --- | --- |
| Terminal-Bench 2.1 | Harbor 加载本地 89 题 | Agent 官方 Trial；当前无评分 |
| SWE-bench Verified | 加载 500 个任务引用；下载并加载 `django__django-15098` | Harbor 适配与原始 patch 评测分别登记；尚未执行任务 |
| Aider Polyglot | 加载 225 个任务引用；下载并加载 `polyglot_java_zipper` | Harbor 适配使用原任务测试；尚未执行任务 |
| TwinRouterBench | 970 条静态样本加载并完成固定档位评分 | 静态档位准确率；动态轨道另用 SWE-bench，尚未执行 |
| LLMRouterBench | A6000 原有 700 个 JSON；读取其中 3 个、共 180 条记录 | 查询级模型评分与费用；官方 Python loader 和对照实验尚未执行 |

SWE-bench 和 Aider 的任务由上游 Harbor `TaskClient` 下载，沿用其标准缓存：

- `<harbor-task-cache>/django__django-15098`
- `<harbor-task-cache>/polyglot_java_zipper`

实际注册表使用 `aider-polyglot@1.0`。部分上游说明中的 `aider_polyglot` 是旧写法。

TwinRouterBench 的静态 `passed` 表示所选档位达到标签要求；不能转成 Agent 完成任务的比例。其静态费用包含预设或估计的 Token 数量。LLMRouterBench 已有 `score` 是历史评分，读取 JSON 不等于重新运行原评分器。

## 工件解析与验证

解析器读取 Harbor 0.24.0 原始 `config.json`、`lock.json`、`result.json`，并关联 Verifier 文件、ATIF 与原生 mini 轨迹。它保留官方 ID、任务版本与 Git SHA、输入输出 Token、记录费用、阶段耗时与完整 Episode 耗时。没有测量的字段保持 `null`。

运行中缺少完整工件的 Trial 仍显示为 `NOT_EVALUATED`。评分为 0 的真实 Trial 是已评分失败；缺少评分文件不能写成 0。多指标 JSON 保留原字段，不擅自换算成功率。

此前解析测试的 19 项通过记录仅属于开发证据。远端 main 已删除独立解析测试文件，本轮接受删除，没有恢复；此前日志仍在原迭代目录。新增 Docker 目标和续跑接口的窄测为 16 项通过、12 项未选，用时 9.14 秒，没有调用 Docker 或付费模型。

环境和数据摘要：`our-project/results/iterations/20261019-v10-integration/harbor_evidence.json`。

命令、退出码和耗时：`our-project/results/iterations/20261019-v10-integration/harbor_commands.jsonl`。

## 下一步

先解决真实沙箱访问，再依次运行 Oracle、原生 mini、动态 mini、Canary 与 Dev 对照。保留同一任务与官方原版 Verifier。Sealed Test 仍等待负责人明确确认。当前没有 RQ1–RQ5 的新增官方 Agent 结果。

## V10 本地执行补充

`run --canary` 的任务顺序已包含 Oracle 单题、原生 mini 单题、项目适配 mini 单题及 Canary；`run --dev` 先接续同样的单题阶段与 Canary，再运行 Dev。相同任务、策略和 seed 不重复加入计划。正式运行读取本地上游 Terminal-Bench 2.1 tasks，来源 Git SHA 为 `7131e4375048a0e408a8fb404b5f499d726b695b`，不依赖未确认的在线名称解析。

两种 mini 使用同一上游 prompt、30 步和配置价 $3 单题限制；生成请求使用 Chat Completions。原生 mini 经临时 HTTP 转发调用现有 Provider，真实 Key 留在宿主，转发凭据只在该次运行内有效。转发记录上游 TTFT；下游接收完整响应的时间另属网络与缓冲耗时。Token/s 同时区分整请求均速与 TTFT 后估算。

`resume` 先读取此前计划。Docker 原因仍在时只返回原有问题，保留 Job，不再次调用同样的失败任务。其他错误需要记录真实解决依据后继续；当前未实现所有错误类型的自动恢复。终端执行每 10 秒写本地状态，上传现有 8765 看板的独立 JSON，训练区域与服务不变。

`export` 从官方 Trial、Agent 元数据和事件输出 Fig.3–8、Table 3–11 的 JSON/CSV 输入。RQ2 需要 `pool_id/pool_k`，RQ3 需要 `granularity`，RQ4 需要对应消融字段和 `checkpoint_id`，RQ5 需要运行前 workload 标签。缺数据保持空表；费用未知保持 `null`，不拟合预设收益边界。当前只验证了统计函数与导出通路，尚无完整正式消融实验与论文图形。

结束的官方 Trial 由现有 `collect_trials` 接入 Episode Ledger，来源仍是原始 `result.json`，按 Trial ID 去重，不复制另一套 Episode。无原版 Verifier 的记录保持 `NOT_EVALUATED`；Router fallback 单独标识并排除正式神经 Router 结果。Provider 探测事件与 Benchmark 指标分开计算。官方 Oracle、原生 mini、动态 mini 的实际 Trial 数目前均为 0。
