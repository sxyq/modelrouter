# ModelRouter

ModelRouter 是面向长程 Agent 任务的模型、推理档位与成本研究项目。

仓库分为两部分：

- `our-project/`：本项目的研究报告、文献笔记、清洗数据、汇总数据和规划文档。
- `external-projects/`：外部项目的来源登记，仅用于说明文献和实验参考，不包含外部仓库源码。

**训练数据/Provider 政策唯一详细台账**：[DATA_SOURCE_AND_POLICY_REGISTRY.md](our-project/data/DATA_SOURCE_AND_POLICY_REGISTRY.md)：公开轨迹、静态模型比较、KV Cache、长记忆、多 Agent、时间/预算、国内外 Provider 能力与缓存/定价政策，包含来源状态、选择栏及未来数据清洗质量合同。**具体选择批准仍以 EXPERIMENT_QA.md 为准；台账是来源登记，不代表已下载或获准训练。**

原始服务器日志、凭据、浏览器调试文件和外部仓库源码不纳入本仓库。
## 当前研究与跨对话恢复入口

**每次新开 ChatGPT 对话先读取 GitHub `main` 当前 HEAD 的以下四份正式文档**，不依赖旧会话摘要或写死的 SHA：

1. **[PROJECT_STATUS.md · 唯一实时状态源](our-project/planning/PROJECT_STATUS.md)**：当前阶段、任务、授权、阻塞及唯一下一行动。
2. **[EXPERIMENT_QA.md · 问答批准记录](our-project/planning/EXPERIMENT_QA.md)**：实验 Q-ID、用户明确确认的决策、未答事项及影响。
3. **[PLANNING_MEMORY.md · 长期交接与新会话启动提示词](our-project/planning/PLANNING_MEMORY.md)**：长期研究决定、历史、Agent 协作规范；第 10 节包含**长期通用的新窗口启动提示词**。
4. **[RESEARCH_OVERVIEW.md · 研究方法与证据](our-project/planning/RESEARCH_OVERVIEW.md)**：学术问题、Kev 路线、假设、数据与评测方法。

**恢复顺序**：远端 `main` HEAD → Status → Q&A → Memory → Research。当前任务必须由最新版 Status 确定；未批准推荐不能当成决定；历史章节不能覆盖最新进度。如 GitHub 不可访问，请用户提供这四份文件。

旧 `our-project/planning/IMPLEMENTATION_RESEARCH.md` 与 `our-project/literature/report.md` 仅是历史参考，不代表现在唯一实现方案。坚持一个研究主线，不因开启新聊天而新建重复工程链。

**协作**：ChatGPT = Planning Agent，本地 Agent = Execution Agent。默认直接 `main`，本地频繁 commit，按会话/里程碑或最长 24 小时 push，不要求 PR。任务或决定发生真实变化时按职责更新相关文档；不把本地未推送状态误认为 GitHub 已同步，不声称可以自动获知服务器实时状态。公开仓库不得提交私人地址、密钥或原始私人日志。
