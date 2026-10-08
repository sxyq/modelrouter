# ModelRouter

ModelRouter 是面向长程 Agent 任务的模型、推理档位与成本研究项目。

仓库分为两部分：

- `our-project/`：本项目的研究报告、文献笔记、清洗数据、汇总数据和规划文档。
- `external-projects/`：外部项目的来源登记，仅用于说明文献和实验参考，不包含外部仓库源码。

原始服务器日志、凭据、浏览器调试文件和外部仓库源码不纳入本仓库。
## 当前研究入口（2026-10-09 起）

原先集中在研究报告和实现规划中的信息现拆分为三份持续维护的文档：

1. **[Planning Memory · 研究协作记忆](our-project/planning/PLANNING_MEMORY.md)**：供 Planning Agent 与本地 Execution Agent 交接；保存已确认决策、状态、任务台账和 Git 协作规则。
2. **[Project Status · 当前条件与执行路线](our-project/planning/PROJECT_STATUS.md)**：面向项目负责人，汇总环境、数据、代码状态、阻塞、实验计划与验收。
3. **[Research Overview · 研究总纲与相关工作](our-project/planning/RESEARCH_OVERVIEW.md)**：研究问题、文献定位、Kev-4B 架构、状态/动作定义、任务级评测和消融。

上述三份是**当前方案**；`our-project/planning/IMPLEMENTATION_RESEARCH.md` 和 `our-project/literature/report.md` 保留为**历史研究证据**，其 admission-only / GBDT 方案不是当前主方法。

**协作流程**：ChatGPT = Planning Agent；本地 Agent = Execution Agent。每个任务结束必须核对并同步三份文档，附测试证据及 Git commit/PR；不得向公开仓库提交私人服务器地址、密钥或原始会话内容。
