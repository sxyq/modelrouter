"""三轮：把图元（层条/注意力线/token/概率条）再加狠一档，投影才看得见。"""
from pathlib import Path

ROOT = Path(r"D:\Project\路由\modelrouter\汇报\汇报三 第二个版本\interactive")

COMMON = [
    # 注意力连线终点更实
    ("@keyframes arcSweep { from { opacity: 0; stroke-width: .2; } to { opacity: var(--arc, .40); stroke-width: .65; } }",
     "@keyframes arcSweep { from { opacity: 0; stroke-width: .2; } to { opacity: var(--arc, .55); stroke-width: .85; } }"),
    (".bar-bg { fill: #E5DECD; }", ".bar-bg { fill: #D6CDB2; }"),
    (".bar-score { fill: #8A3F22; }", ".bar-score { fill: #7A351A; }"),
    (".bar-noul { fill: #B0842E; }", ".bar-noul { fill: #8E6A24; }"),
    (".tok.q { fill: #FAF1EB; stroke: #A87A62; }", ".tok.q { fill: #F5E4D8; stroke: #9C6244; }"),
    (".tok.o { fill: #FBF5E8; stroke: #BFA469; }", ".tok.o { fill: #F7EAD0; stroke: #A8823C; }"),
]

P06 = [
    (".mesh path { stroke: #155E58; fill: none; stroke-width: .6; opacity: .22; }",
     ".mesh path { stroke: #0F4E49; fill: none; stroke-width: .8; opacity: .5; --arc: .58; }"),
    (".tok { fill: #F1F5F3; stroke: #8DBDB6; stroke-width: .8; }",
     ".tok { fill: #E6EEEA; stroke: #5F9A93; stroke-width: .9; }"),
    (".lyr { fill: #C3DBD5; stroke: #79AFA6; stroke-width: .8; }",
     ".lyr { fill: #6FA9A0; stroke: #2C6E67; stroke-width: .9; }"),
    (".vector rect { fill: #C2DCD6; stroke: #8FC0B8; stroke-width: .6; }",
     ".vector rect { fill: #6FA9A0; stroke: #2C6E67; stroke-width: .6; }"),
]

P07 = [
    (".causal path { stroke: #8A3F22; fill: none; stroke-width: .6; opacity: .24; }",
     ".causal path { stroke: #7A351A; fill: none; stroke-width: .8; opacity: .5; --arc: .62; }"),
    (".tok { fill: #F8F1EA; stroke: #E0C9BB; stroke-width: .8; }",
     ".tok { fill: #F2E2D6; stroke: #9C6244; stroke-width: .9; }"),
    (".lyr-a { fill: #E3BFA3; stroke: #AC7B5D; stroke-width: .8; }",
     ".lyr-a { fill: #D9A57F; stroke: #8A5334; stroke-width: .9; }"),
    (".lyr-b { fill: #C2DCD6; stroke: #6FB0A8; stroke-width: .8; }",
     ".lyr-b { fill: #6FA9A0; stroke: #2C6E67; stroke-width: .9; }"),
    (".lora-mat { fill: #FFFDF9; stroke: #9E5F3F; stroke-width: 1; }",
     ".lora-mat { fill: #FFFDF9; stroke: #8A4E30; stroke-width: 1.3; }"),
    (".logit { fill: #D9A48E; }", ".logit { fill: #9C5F41; }"),
]


def apply(path, rules):
    text = path.read_text(encoding="utf-8")
    for old, new in rules:
        if old not in text:
            print(f"  [MISS] {path.name}: {old[:56]!r}")
            continue
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


apply(ROOT / "P06.html", COMMON + P06)
apply(ROOT / "P07.html", COMMON + P07)
print("done")
