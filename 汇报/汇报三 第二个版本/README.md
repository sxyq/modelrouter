# 汇报三（第二个版本）· 混合网页播放器

19 页演示：静态页保留原 PNG，P06 / P07 为本次新建的动态架构图，P16 / P17 复用原「汇报三」的真实推理演示。**P15 已移除**，页序为 P01–P14 + P16–P20。

## 打开方式

| 入口 | 说明 |
| --- | --- |
| `dist/deck.html` | **唯一推荐入口**。单文件，17 张 PNG 与 4 个交互页全部 base64 / srcdoc 内嵌，不依赖 `slides/`、`interactive/` 的相对路径 |
| `interactive/P06.html`、`P07.html` | 单独打开架构页（需与 `base.css`、`shell.js` 同目录） |
| `interactive/P16.html`、`P17.html` | 单独打开真实推理演示（需 `assets/live.css`、`live.js`，并启动下面的桥接服务） |

播放器快捷键：`←` / `→` 翻页，`F` 全屏，`H` 隐藏周边导航，`目录` 可跳页。

## P16 / P17 的真实推理

两页的数值来自 A6000 上的 `POST /system-one`，前端不预置、不重算。**代码与依赖已全部迁移到本目录**，原 `汇报/汇报三/` 可以删除。

```bash
cd "汇报/汇报三 第二个版本"
python assets/bridge_server.py            # 默认 127.0.0.1:8775
```

- 前端默认桥接地址已改为 `http://127.0.0.1:8775/api`（`assets/live.js` 的 `DEFAULT_BRIDGE`）。
- 上游地址读取 `assets/local_config.json`（本地私有，不提交），当前为 A6000 内网地址。
- 候选模型池为 2026-10 核实的真实档位：GPT-6 Astra（low/medium/high/xhigh/max）、Claude Sonnet 5.5（同五档）、DeepSeek V4.1 Flash（low/high/max），共 13 个「模型 × 推理档位」组合；P16 可选单模型三档或联合 13 档一起决策。
- **服务不可用时的降级**：头部显示「A6000 演示服务未启动」，两张结果卡显示「尚未推理 · 本页不预置任何概率数值」，不会出现假数据；服务恢复后点头部「刷新状态」或直接点运行即可。
- `runs/` 已随迁移一并带过来（最近一轮 `pair_*.json`），P17 打开即可看到上一轮结果；服务每次对比会继续写入这里。
- 目录内自包含：`interactive/P16.html`、`P17.html`（互为跳转）、`assets/live.css`、`live.js`、`bridge_server.py`、`local_config.json`、`live-evidence.json`。

## P06 / P07 动态架构图

两页均为 1280×720 原生页面，四列栅格一致，便于对照讲解：

- P06：`A 输入拼接 → B ModernBERT-large 双向编码 → C 类型化决策头 → D 三路输出`
- P07：`A 同一请求契约 → B Qwen3.5-4B 冻结基座 + LoRA → C Pointer Head 候选打分 → D Softmax 类型化输出`

每页 4 个 step：`上一步 / 下一步 / 自动播放 / 重置`，键盘 `←` `→`、空格暂停、`R` 重置；在 step 4 再按 `→` 会直接翻到下一页。左侧四张说明卡与各自原 PNG 的文案逐字一致，step 切换时对应卡片同步抬起。

图内数字均来自项目文档：Laya-421M（ModernBERT-large，28 层 / 1024 维 / 8192 ctx）；Kev-4B（Qwen3.5-4B-Base，32 层 = 24 Gated DeltaNet + 8 Full Attention，LoRA r=16 α=32，约 33.8M 可训练参数 ≈ 0.8%，prefill 单次前向）。概率条只是结构示意，页内已标注。

## 重新构建

```bash
cd "汇报/汇报三 第二个版本"
python scripts/deck.py build .
```

构建会重新读取 `interactive/P06/P07/P16/P17.html`，把 CSS / JS / 图片内联进 `dist/deck.html`。
P16 / P17 随时改动，改完重新 build 即可，无需改 `deck.json`。

- `deck.json` 控制页序、标题、类型、主题色；P16 / P17 的 `frame` 为 1440×810（这两页按 16:9 桌面尺寸排版，播放器按该尺寸渲染后整体缩放，避免被压扁）。
- 单页自检：`node scripts/shot.cjs`（需 `NODE_PATH` 指向带 `playwright-core` 的目录），截图输出到 `shots/`。

## 换一台电脑跑起来

```bash
git pull                       # 或 git clone <repo> 后进入 汇报/汇报三 第二个版本
python scripts/deck.py build . # 生成 dist/deck.html（纯标准库，无需 pip 装任何东西）
```

然后双击 `dist/deck.html`：`←` `→` 翻页，`F` 全屏，`H` 隐藏周边导航，右上角「目录」跳页。仓库里已带一份 `dist/deck.html`，不重新 build 也能直接打开。

- 静态页与 P06 / P07 完全离线可用，不需要网络、不需要 GPU。
- P16 / P17 要出真实推理，另需两步：
  1. `python assets/bridge_server.py`（默认 `127.0.0.1:8775`）；
  2. 新建 `assets/local_config.json` 写上上游地址——该文件含内网信息，**不在 Git 里**，需按现场环境自己建：
     ```json
     { "upstream": "http://<A6000 地址>:8000" }
     ```
  上游连不上时，两页显示「演示服务未启动 / 尚未推理」，不会出现假数据。

## 页面状态

- 共 **19 页**，全部到位（19 / 19）。
- P15 不存在：原图本来就没有，已从 `deck.json` 移除，不占用页位。
- 由于 P16–P20 的 PNG 图内印有 `P16…P20` 页码，页号不重排：`deck.json` 的 `no` 允许跳号。播放器底部计数显示「当前第几页 / 19 · P16」这样的形式，既给出播放顺序也不和图上页码打架；`#p16` 这类锚点仍按图内页码定位。
- `deck_bundle.zip` 为同一份 `dist/` 的离线包。
