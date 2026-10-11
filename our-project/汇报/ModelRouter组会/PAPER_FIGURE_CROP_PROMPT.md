# 本地 Agent 提示词｜裁剪真实论文 Figure

你现在只负责为 ModelRouter 组会 PPT 补齐**真实论文 Figure 截图**，不要制作 PPT，也不要开展深度研究。

## 先读取
- `our-project/汇报/ModelRouter组会/PAPER_NOTES_AND_FIGURES.md`
- `our-project/汇报/ModelRouter组会/assets/paper-figures/README.md`
- `our-project/planning/GROUP_MEETING_PPT_OUTLINE.md`（v7 10 页版）
- 仓库 `research/task-level-cost-routing/literature/pdfs/` 内已有的 PDF

## 要裁的图

1. **P0 INFRAMIND Fig.2**｜https://arxiv.org/pdf/2606.11440｜Traditional MAS vs InfraMind 架构；预计 PDF 物理 p.2，**必须核实**。
2. **P0 TwinRouterBench Fig.1**｜https://arxiv.org/pdf/2605.18859｜Static Track vs Live Dynamic Track；预计 PDF 物理 p.2，**必须核实**。
3. **P1 PROGROUTER Fig.2**｜https://arxiv.org/pdf/2608.25992｜Progress-guided workflow / routing；物理页未知，**必须查 Figure caption**。这张图在 10 页主讲中为附录备用，不阻塞正文制作。

## 执行规则

- 优先使用仓库 PDF；不存在时才下载对应**官方 PDF**。逐篇核对论文标题、Figure 编号、完整 caption、PDF **物理页码**（第一页算 p01，不能直接拿印刷页码代替）。
- 以原 PDF 页面渲染后裁剪，建议 250–300 DPI。保留完整 Figure、图例、箭头、坐标和必要文字，边缘少量留白。图注可在 README 原样记录，不必强行挤进图片。
- **不使用 AI 生图，不临摹，不重绘，不修改原 Figure 的任何文字或结构**；保持原比例。逐张打开 PNG 目视检查，不清楚则重新渲染/裁剪。
- 输出到 `our-project/汇报/ModelRouter组会/assets/paper-figures/`：
  - `inframind_fig2_pNN.png`
  - `twinrouterbench_fig1_pNN.png`
  - `progrouter_fig2_pNN.png`
  其中 NN 是核对后的 PDF 物理页码。
- 更新 `assets/paper-figures/README.md`：官方来源 URL、Fig. 编号、真实物理页、图注、PNG 相对路径、视觉检查状态。不得覆盖已有真实 PNG。
- 如果预期 Fig. 与 PDF 实际内容不符，先报告差异，**不要拿别的图冒充**。
- 最后给出每张 PNG 的预览，并逐条列出：论文｜Fig.｜PDF 物理页｜保存路径｜caption｜检查状态。没有完成的项目明确标为未完成。
- 不做训练、付费 API、整页 PPT 生成、深度研究、PR/CI 或无关工程任务。

## 验收标准

至少 P0 的两张 PNG 可以直接嵌入 v7 P03、P09，真实 Figure 可辨认，README 与实际路径一致。P1 的 PROGROUTER 图允许稍后补齐。