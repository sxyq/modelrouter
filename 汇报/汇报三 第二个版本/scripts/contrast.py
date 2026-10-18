"""一次性提高 P06/P07 两页的对比度：加深描边、加深小字、降低灰度。"""
import re
from pathlib import Path

ROOT = Path(r"D:\Project\路由\modelrouter\汇报\汇报三 第二个版本\interactive")

FONT = [
    (".f-h  { font-family: var(--mono); font-size: 9px; letter-spacing: 1.1px; fill: #A39C8C; }",
     ".f-h  { font-family: var(--mono); font-size: 9.5px; letter-spacing: 1.1px; fill: #8A8272; }"),
    (".f-b  { font-family: var(--sans); font-size: 11px; font-weight: 700; fill: #2A2A24; }",
     ".f-b  { font-family: var(--sans); font-size: 11.5px; font-weight: 700; fill: #2A2A24; }"),
    (".f-b2 { font-family: var(--sans); font-size: 10px; font-weight: 700; fill: #2A2A24; }",
     ".f-b2 { font-family: var(--sans); font-size: 10.5px; font-weight: 700; fill: #2A2A24; }"),
    (".f-t  { font-family: var(--sans); font-size: 9.4px; fill: #57544B; }",
     ".f-t  { font-family: var(--sans); font-size: 9.8px; fill: #4A463C; }"),
    (".f-m  { font-family: var(--mono); font-size: 8.4px; fill: #8A857A; }",
     ".f-m  { font-family: var(--mono); font-size: 8.8px; fill: #6C6759; }"),
    (".f-mm { font-family: var(--mono); font-size: 7.4px; fill: #8A857A; }",
     ".f-mm { font-family: var(--mono); font-size: 8px; fill: #635E52; }"),
    (".f-n  { font-family: var(--sans); font-size: 9px; fill: #6E6A63; }",
     ".f-n  { font-family: var(--sans); font-size: 9.4px; fill: #5C584D; }"),
]

HEX = [
    ("#E2DBCB", "#CDC3AE"),  # 卡片描边
    ("#E4C9B9", "#D3AC9A"),
    ("#E3D2AE", "#D2BC85"),
    ("#B7D8D3", "#93C7C0"),
    ("#E0BFB0", "#CEA291"),
    ("#DFCFA9", "#CDB784"),
    ("#CBDDD9", "#A9CCC6"),
    ("#E3C7B8", "#D3AE9C"),
    ("#E9F1EF", "#D8E8E4"),
    ("#BFD8D3", "#97C4BD"),
    ("#F3E3D5", "#EED7C4"),
    ("#DDBCA8", "#C79A80"),
    ("#DCEBE8", "#C2DCD6"),
    ("#EFEAE0", "#E5DECD"),
    ("#E3BFAF", "#D9A48E"),
    ("#2E8A82", "#1E726B"),
    ("#BF6042", "#A04E32"),
    ("#B9B2A2", "#8F887A"),
    ("#C9AF9E", "#B08A72"),
    ("#8FC3BE", "#5FA8A1"),
    ("#DDBCA8", "#C08A66"),
    ("#E7D3C6", "#D9B7A5"),
    ("#E7D8B6", "#D9C28C"),
    ("#4C7F79", "#2E6E69"),
    ("#A9532F", "#A04A28"),
    ("#8E6A24", "#7A5A1A"),
    ("#6B665C", "#55504A"),
    ("#6F686A", "#5A5355"),
    ("#8A857A", "#635E52"),
]

# 相对独立的行级替换（避免误伤）
PAGES = {
    "P06.html": [
        (".grp { opacity: .58; transition: opacity .38s ease; }",
         ".grp { opacity: .78; transition: opacity .38s ease; }"),
        ("opacity: .42; }", "opacity: .5; }"),
        ("stroke-width: .55; opacity: .16; }", "stroke-width: .6; opacity: .22; }"),
        ("0%, 100% { opacity: .07; } 50% { opacity: .42; }",
         "0%, 100% { opacity: .10; } 50% { opacity: .50; }"),
        ("fill: #DCEBE8; stroke: #B7D3CE;", "fill: #C2DCD6; stroke: #8FC0B8;"),
    ],
    "P07.html": [
        (".grp { opacity: .58; transition: opacity .38s ease; }",
         ".grp { opacity: .78; transition: opacity .38s ease; }"),
        ("opacity: .42; }", "opacity: .5; }"),
        ("stroke-width: .55; opacity: .18; }", "stroke-width: .6; opacity: .24; }"),
        ("0%, 100% { opacity: .08; } 50% { opacity: .40; }",
         "0%, 100% { opacity: .10; } 50% { opacity: .48; }"),
        ("stroke-width: 1.1; fill: none; stroke-dasharray: 4 4; opacity: .55; }",
         "stroke-width: 1.2; fill: none; stroke-dasharray: 4 4; opacity: .72; }"),
        ("fill: #F3E3D5; stroke: #DDBCA8;", "fill: #EED7C4; stroke: #C79A80;"),
        ("fill: #DCEBE8; stroke: #B7D8D3;", "fill: #C2DCD6; stroke: #93C7C0;"),
        (".lora-mat { fill: #FFFDF9; stroke: #C98E74;", ".lora-mat { fill: #FFFDF9; stroke: #B4714F;"),
    ],
}

BASE = [
    ("--body: #5E5B52;", "--body: #4A463D;"),
    ("--muted: #8A857A;", "--muted: #7A7466;"),
    ("--line: #E7E0D3;", "--line: #DCD2BF;"),
    ("font-size: 12.1px; line-height: 1.62; color: var(--body);",
     "font-size: 12.4px; line-height: 1.62; color: var(--body);"),
    ("color: var(--muted);\n  text-transform: uppercase;", "color: #57544A;\n  text-transform: uppercase;"),
    (".panel-caption b {\n    color: var(--teal);", ".panel-caption b {\n    color: #1B6A63;"),
    ("color: #4A473F;\n  background: transparent;", "color: #3B382F;\n  background: transparent;"),
    ("background: #F4F0E6;\n  border-color: #D8D0BF;", "background: #EFE9DA;\n  border-color: #C8BDA6;"),
    ("gap: 16px;\n  font-size: 10.5px;\n  color: #6B675C;", "gap: 16px;\n  font-size: 10.8px;\n  color: #57544A;"),
    ("letter-spacing: .12em;\n  color: #969082;", "letter-spacing: .12em;\n  color: #7C7668;"),
    ("border-radius: 10px;\n  background: #DED7C8;", "border-radius: 10px;\n  background: #CFC4AC;"),
    ("font-size: 12.5px; font-weight: 700; letter-spacing: .04em;",
     "font-size: 13px; font-weight: 700; letter-spacing: .04em;"),
]


def apply(path, rules, label):
    text = path.read_text(encoding="utf-8")
    for old, new in rules:
        n = text.count(old)
        if n == 0:
            print(f"  [MISS] {label}: {old[:60]!r}")
            continue
        text = text.replace(old, new)
        print(f"  [ok x{n}] {label}: {old[:44]!r}")
    path.write_text(text, encoding="utf-8")


print("base.css")
apply(ROOT / "base.css", BASE, "base")

for name, rules in PAGES.items():
    print(name)
    apply(ROOT / name, FONT + rules + [(a, b) for a, b in HEX], name)

print("done")
