"""二轮：再加深 P06/P07 对比度 + 注入分步计算动画。"""
from pathlib import Path

ROOT = Path(r"D:\Project\路由\modelrouter\汇报\汇报三 第二个版本\interactive")

# ── 1. 再加深一档 ───────────────────────────────────────
DEEP = [
    (".f-h  { font-family: var(--mono); font-size: 9.5px; letter-spacing: 1.1px; fill: #8A8272; }",
     ".f-h  { font-family: var(--mono); font-size: 10px; letter-spacing: 1.1px; fill: #6E675A; }"),
    (".f-t  { font-family: var(--sans); font-size: 9.8px; fill: #4A463C; }",
     ".f-t  { font-family: var(--sans); font-size: 9.8px; fill: #3D3A32; }"),
    (".f-m  { font-family: var(--mono); font-size: 8.8px; fill: #6C6759; }",
     ".f-m  { font-family: var(--mono); font-size: 8.8px; fill: #56514A; }"),
    (".f-mm { font-family: var(--mono); font-size: 8px; fill: #635E52; }",
     ".f-mm { font-family: var(--mono); font-size: 8px; fill: #514C41; }"),
    (".f-n  { font-family: var(--sans); font-size: 9.4px; fill: #5C584D; }",
     ".f-n  { font-family: var(--sans); font-size: 9.4px; fill: #4A463C; }"),
    (".grp { opacity: .78; transition: opacity .38s ease; }",
     ".grp { opacity: .84; transition: opacity .38s ease; }"),
    (".halo { fill: none; stroke: #24817A; stroke-width: 1; opacity: 0; transition: opacity .38s ease; }",
     ".halo { fill: none; stroke: #1B6A63; stroke-width: 1.5; opacity: 0; transition: opacity .38s ease; }"),
    ("opacity: .5; }", "opacity: .62; }"),
]

HEX2 = [
    ("#CDC3AE", "#B9AC91"), ("#D3AC9A", "#BE9078"), ("#D2BC85", "#BFA469"),
    ("#93C7C0", "#6FB0A8"), ("#CEA291", "#B98A75"), ("#CDB784", "#BFA469"),
    ("#A9CCC6", "#8DBDB6"), ("#BE8F79", "#A87A62"),
    ("#D8E8E4", "#C3DBD5"), ("#97C4BD", "#79AFA6"),
    ("#EED7C4", "#E3BFA3"), ("#C79A80", "#AC7B5D"),
    ("#A8CFC7", "#93C7BE"), ("#6AA9A0", "#4F948B"),
    ("#D8CFB8", "#C9C0A6"), ("#C4886C", "#AC7154"),
    ("#1E726B", "#155E58"), ("#A04E32", "#8A3F22"),
    ("#6E6959", "#5A5546"), ("#5FA8A1", "#4E9A92"),
    ("#C08A66", "#A87550"), ("#C79E88", "#B0826A"),
    ("#C2A468", "#AC8C4E"), ("#2E6E69", "#1F5A55"),
    ("#8E3F20", "#7A351A"), ("#654B14", "#553E10"),
    ("#46423B", "#3A372F"), ("#4A4446", "#3E393B"),
    ("#B4714F", "#9E5F3F"), ("#D3AE9C", "#BE8F79"),
]

BASE2 = [
    ("--body: #4A463D;", "--body: #3F3C34;"),
    ("--muted: #7A7466;", "--muted: #655E50;"),
    ("--line: #DCD2BF;", "--line: #CBC0A8;"),
    ("color: #57544A;\n  text-transform: uppercase;", "color: #4A463C;\n  text-transform: uppercase;"),
    ("color: #1B6A63;\n  font-weight: 700;", "color: #145C56;\n  font-weight: 700;"),
    ("color: #57544A;", "color: #4A463C;"),
    ("color: #3B382F;\n  background: transparent;", "color: #2E2B23;\n  background: transparent;"),
    ("background: #EFE9DA;\n  border-color: #C8BDA6;", "background: #EBE4D2;\n  border-color: #B5A98C;"),
    ("background: #CFC4AC;", "background: #BCAF93;"),
    ("color: #7C7668;", "color: #655E50;"),
]

# ── 2. 分步计算动画 ─────────────────────────────────────
def delays(selector, base, step, count, tail=None):
    lines = []
    for i in range(1, count + 1):
        d = base + step * (i - 1)
        lines.append(f"{selector}:nth-child({i}){{animation-delay:{d:.2f}s}}")
    if tail:
        lines.append(f"{selector}:nth-child(n+{count + 1}){{animation-delay:{tail:.2f}s}}")
    return "\n".join(lines)


ANIM = """
/* ── 分步计算：进入某一步时，该列自上而下依次“跳”出来 ── */
@keyframes seqIn { from { opacity: 0; transform: translateY(7px); } 60% { opacity: 1; } to { opacity: 1; transform: none; } }
@keyframes arcSweep { from { opacity: 0; stroke-width: .2; } to { opacity: var(--arc, .40); stroke-width: .65; } }
@keyframes barFill { from { opacity: .18; transform: scaleX(.3); } to { opacity: 1; transform: none; } }
@keyframes cellFill { from { opacity: 0; } to { opacity: 1; } }
@keyframes popIn { from { opacity: 0; transform: scale(.86); } to { opacity: 1; transform: none; } }

body[data-step="1"] #g-input > *,
body[data-step="2"] #g-enc > *,
body[data-step="3"] #g-head > *,
body[data-step="4"] #g-out > * {
  animation: seqIn .40s cubic-bezier(.22,1,.36,1) both;
}
#g-input > *:nth-child(1), #g-enc > *:nth-child(1), #g-head > *:nth-child(1), #g-out > *:nth-child(1) { animation-delay: 0s; }
#g-input > *:nth-child(2), #g-enc > *:nth-child(2), #g-head > *:nth-child(2), #g-out > *:nth-child(2) { animation-delay: .10s; }
#g-input > *:nth-child(3), #g-enc > *:nth-child(3), #g-head > *:nth-child(3), #g-out > *:nth-child(3) { animation-delay: .20s; }
#g-input > *:nth-child(4), #g-enc > *:nth-child(4), #g-head > *:nth-child(4), #g-out > *:nth-child(4) { animation-delay: .30s; }
#g-input > *:nth-child(5), #g-enc > *:nth-child(5), #g-head > *:nth-child(5), #g-out > *:nth-child(5) { animation-delay: .40s; }
#g-input > *:nth-child(6), #g-enc > *:nth-child(6), #g-head > *:nth-child(6), #g-out > *:nth-child(6) { animation-delay: .50s; }
#g-input > *:nth-child(7), #g-enc > *:nth-child(7), #g-head > *:nth-child(7), #g-out > *:nth-child(7) { animation-delay: .60s; }
#g-input > *:nth-child(8), #g-enc > *:nth-child(8), #g-head > *:nth-child(8), #g-out > *:nth-child(8) { animation-delay: .70s; }
#g-input > *:nth-child(9), #g-enc > *:nth-child(9), #g-head > *:nth-child(9), #g-out > *:nth-child(9) { animation-delay: .80s; }
#g-input > *:nth-child(n+10), #g-enc > *:nth-child(n+10), #g-head > *:nth-child(n+10), #g-out > *:nth-child(n+10) { animation-delay: .90s; }

/* Transformer 层：一层一层点亮 */
body[data-step="2"] .lyr,
body[data-step="2"] .lyr-a,
body[data-step="2"] .lyr-b { animation: barFill .34s ease-out both; transform-box: fill-box; transform-origin: left center; }
body[data-step="2"] .lyr:nth-child(2), body[data-step="2"] .lyr-a:nth-child(2), body[data-step="2"] .lyr-b:nth-child(2) { animation-delay: .30s; }
body[data-step="2"] .lyr:nth-child(3), body[data-step="2"] .lyr-a:nth-child(3), body[data-step="2"] .lyr-b:nth-child(3) { animation-delay: .46s; }
body[data-step="2"] .lyr:nth-child(4), body[data-step="2"] .lyr-a:nth-child(4), body[data-step="2"] .lyr-b:nth-child(4) { animation-delay: .62s; }
body[data-step="2"] .lyr:nth-child(5), body[data-step="2"] .lyr-a:nth-child(5), body[data-step="2"] .lyr-b:nth-child(5) { animation-delay: .78s; }
body[data-step="2"] .lyr:nth-child(6), body[data-step="2"] .lyr-a:nth-child(6), body[data-step="2"] .lyr-b:nth-child(6) { animation-delay: .94s; }

/* 池化向量：一格一格填充 */
body[data-step="2"] .vector rect { animation: cellFill .26s ease-out both; }
""" + delays("body[data-step=\"2\"] .vector rect", 1.05, 0.045, 16) + """

/* 注意力连线：一条一条扫过 */
body[data-step="2"] .mesh path { animation: arcSweep .42s ease-out both; }
body[data-step="1"] .causal path { animation: arcSweep .42s ease-out both; }
""" + delays("body[data-step=\"2\"] .mesh path", 0.62, 0.045, 28) + "\n" \
    + delays("body[data-step=\"1\"] .causal path", 0.62, 0.05, 16) + """

/* LoRA 矩阵与候选打分：逐个弹出 */
body[data-step="2"] .lora-mat { animation: popIn .34s cubic-bezier(.22,1.4,.36,1) both; }
body[data-step="2"] .lora-mat:nth-of-type(2) { animation-delay: .34s; }
body[data-step="3"] .logit { animation: barFill .3s ease-out both; transform-box: fill-box; transform-origin: left center; }
"""


def apply(path, rules):
    text = path.read_text(encoding="utf-8")
    for old, new in rules:
        n = text.count(old)
        if n == 0:
            print(f"  [MISS] {path.name}: {old[:52]!r}")
            continue
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


for name in ("P06.html", "P07.html"):
    p = ROOT / name
    apply(p, DEEP + HEX2)
    text = p.read_text(encoding="utf-8")   # 重新读取，避免覆盖上面的颜色改动
    if "分步计算：进入某一步时" not in text:
        text = text.replace("</style>", ANIM + "</style>", 1)
        p.write_text(text, encoding="utf-8")
        print(f"  [anim] {name} 已注入分步动画")
    else:
        print(f"  [skip] {name} 已有动画块")

apply(ROOT / "base.css", BASE2)
print("done")
