# 历史结果来源

这里的 RQ1、RQ3 图表与 CSV，以及相邻 `benchmarks/` 中的 RQ2、RQ4、RQ5，仅供开发与版式参考，不支持论文结论。

| 内容 | 来源 | 标签 |
| --- | --- | --- |
| RQ1 | 无官方 Verifier 的历史 Episode，部分费用与速度为预设值 | Unverified |
| RQ2 | 按模型池写入的模拟成功率 | Synthetic |
| RQ3 | 源码中的 G0–G3 示例矩阵 | Synthetic |
| RQ4 | 配置中预填的 70.2% 等数值 | Synthetic |
| RQ5 | 预填成功率、费用与 0.72 示例边界 | Synthetic |

原有数值保留。新的官方来源数据由 `python -m modelrouter.benchmark export` 从原始 Harbor Trial 读取，写入对应迭代目录的 `analysis/`。缺少真实实验的项目保持 `NOT_EVALUATED`，不补造记录。
