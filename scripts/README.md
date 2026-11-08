# 脚本目录职责

本目录保留现有命令路径，按实际代码用途分类。旧报告中的PID只描述当时进程，当前训练与Serving状态见[项目现状](../our-project/planning/PROJECT_STATUS.md)。

## 现有看板入口

| 脚本 | 实际职责 |
|---|---|
| `fetch_live_status.py` | 委托`modelrouter.telemetry.fetch_live_status`，从现有事实生成状态 |
| `serve_dashboard.py` | 现有只读HTTP看板入口，提供`our-project/dashboard/` |
| `build_clean_chart_dashboard.py` | 返回已有看板路径，不再生成第二套模板 |
| `build_clean_dashboard.py`、`build_upgraded_dashboard.py`、`generate_cds_dashboard.py` | 委托上述同一看板入口 |

## 历史研究与展示

| 脚本 | 保留用途 |
|---|---|
| `benchmark_ollama_impact.py` | 原F05与本地Ollama单/双并发资源干扰实验，非当前K=3任务评测 |
| `val_benchmark_compare.py` | 原Laya静态Val比较，非完整Agent任务结果 |
| `jev_laya_kev_typed_demo_v2.py` | 根目录具名展示工具的保留命令路径，非Harbor正式实现 |
| `oneshot_f05_to_f03_handover.py` | 2026-10-18历史一次性交接材料，原PIDs不作当前状态；原归档同时在`our-project/docs/operations/legacy/` |

## 既有浏览器工具

`capture_dashboard_screenshots.py`保存看板截图；`verify_dashboard_browser.py`读取已有看板与JSON响应。两者不是Terminal-Bench评分器。

当前完整任务只有 **Harbor → ModelRouterMiniSweAgent → DefaultAgent → 原官方Verifier** 一条执行链，入口在`modelrouter.benchmark`。89题进度、当前Router Pass率及任务费用见[完整任务结果](../our-project/results/benchmark/README.md)。本目录分类不启动上述脚本或新增常驻执行。
