# ModelRouter v7 生图 PPT 工作区

> 本目录是**10 页 / 每页独立 16:9 图像**的制作工作区。论文截图从 `../assets/paper-figures/` 以 Git blob 原样复制到本目录；**原图没有 AI 重绘、修改或重编码**。当前 `assets/paper-figures/` 共 18 张 PNG。

## 风格与生成规则

- 每一页生成**一张独立 1920×1080、16:9 的完整幻灯片画面**；不能在一张图里放两页或四宫格的“幻灯片预览”。
- 统一暖纸白 `#f5f3ee`、白卡 `#fffefa`、墨色 `#17202a`、锈红 `#b45739`、青绿 `#2e766b`、蓝 `#4b7795`、金 `#bd8a36`；标题偏衬线，中文正文清晰；留白充分。
- 生成式视觉只负责背景、氛围、图框、抽象示意；真实论文 Figure 使用本目录 PNG **作为原图直接嵌入**，不允许模型临摹、改写图中文字/箭头/数字。
- 图上只保留标题、一句主张、至多 2–3 个短标注。数据、公式、架构箭头、中文关键术语优先矢量/文本层，防止生图拼写失真。
- 论文页可以包含两张**论文 Figure**，但仍然是一页**完整 16:9 幻灯片**；不得把两张完整幻灯片拼在一张图中。
- 严禁伪造训练结果、动态 Agent 评测结果。Kev-4B 和 Laya-421M 是替代的 typed-choice routers，生成式 LLM 才执行任务。

## 10 页使用图索引

| 页 | 主题 | 本目录论文截图 |
|---:|---|---|
| 01 | ModelRouter 封面 | 原创生成视觉 |
| 02 | 任务级成本 | `cats_cost_definition_p04.png`；可选 `price_reversal_eq2_p04.png` |
| 03 | Gateway × INFRAMIND | `gateway_fig2_p03.png` + `inframind_fig2_p02.png` |
| 04 | SWE-Router × TACIT-Switch | `swe_router_flow.png` + `tacit_switch_flow.png` |
| 05 | Model × native effort 研究缺口 | `rtr_fig1_p02.png` |
| 06 | ModelRouter 主流程 | 原创生成视觉 + 矢量流程图 |
| 07 | 八组状态 / Kev vs Laya | 原创生成视觉 + 矢量状态卡 |
| 08 | 数据与冷启动 | 原创生成视觉 + 真实数据 |
| 09 | 静态 vs 动态 Agent 评测 | `twinrouterbench_fig1_p02.png` |
| 10 | 进度与导师决策 | 原创生成视觉 |

**附录备用**：`progrouter_fig2_p04.png`、`mtrouter_fig2_p04.png`、`opensquilla_fig2_p06.png` 等均已放入本目录。

## 素材来源与真实截图核验

- 原始截图及完整来源：[`../assets/paper-figures/README.md`](../assets/paper-figures/README.md)
- PPT v7：[`../../../planning/GROUP_MEETING_PPT_OUTLINE.md`](../../../planning/GROUP_MEETING_PPT_OUTLINE.md)
- 旧汇报播放器：`汇报/汇报一/PPT/deck.html`；旧图片在 `汇报/汇报一/PPT/assets/deck-images/`。
- 三张新增已裁剪：INFRAMIND Fig.2 p.2 / PROGROUTER Fig.2 p.4 / TwinRouterBench Fig.1 p.2。
- **当前制作状态**：仅已准备素材与版式规范；若后续使用外部生成工具，必须记录其输出位置，不能把生成任务已启动当作 PNG 已完成。
