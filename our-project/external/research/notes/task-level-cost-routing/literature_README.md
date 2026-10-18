# 任务级成本路由文献库

更新时间：2026-09-16

## 目录

```text
literature/
├── manifest.json       # 54 篇论文的来源、分类、年月和本地 PDF
├── index.md            # 可复核的完整论文索引
├── evidence/
│   └── direct-evidence.md  # 19 篇直接相关论文的正文证据和差异判断
└── pdfs/               # 54 份本地 PDF，按编号命名
```

## 分组

| 分组 | 数量 | 作用 |
|---|---:|---|
| direct | 19 | Agent 路由、任务级路由、成本评测和执行前/执行中选择 |
| method | 18 | 查询级路由、模型×推理策略、预算和预测方法 |
| system | 8 | Agent 编排、KV 缓存、服务和模型分配 |
| benchmark | 9 | SWE、工具交互、网页/桌面 Agent 和 test-time compute |

## 证据状态

- 54/54：原文 PDF 已下载到本地，并通过文件类型核对。
- 19/19：直接相关论文已读取 PDF 首页及方法/引言相关段落，摘要和方法结论记录在 `evidence/direct-evidence.md`。
- 54/54：索引链接和本地 PDF 路径已由 `verify_evidence_table.py` 校验。
- “已下载”不等于“每个实验数字都已逐表复核”；写论文时仍应按具体论断回到对应 PDF 页码。

## 重要更正

CASTER 的正确 arXiv 编号是 `2601.19793`。`2602.19793` 实际对应材料学论文，错误文件已移除，清单和本地文件已换成正确版本。

## 使用建议

1. 写 Related Work 时优先读 `direct-evidence.md` 的前 19 篇。
2. 写模型×推理档位方法时读 20–37 篇。
3. 设计缓存、服务和商用接口时读 38–45 篇，并对照 `../implementation/IMPLEMENTATION_RESEARCH.md`。
4. 设计实验任务集时读 46–54 篇。

## 来源边界

论文 PDF、官方会议页和 arXiv 页面用于学术证据；GitHub 仓库、许可证和源码用于实现证据。开源代码的许可证不自动覆盖模型权重、数据集、API 或第三方依赖。
