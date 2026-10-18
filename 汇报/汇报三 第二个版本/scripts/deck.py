#!/usr/bin/env python3
"""Assemble slide PNGs and optional interactive HTML/SVG into a portable web deck.
Python stdlib only; Pillow, when available, improves palette detection.
"""
import argparse
import base64
import html
import json
import math
import re
import shutil
from collections import Counter
from statistics import median
from pathlib import Path
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile

DEFAULT = {
    "paper": "#f5f3ee",
    "surface": "#fffefa",
    "ink": "#17202a",
    "muted": "#66727d",
    "accent": "#2e766b",
    "line": "#d9d9d1",
}
ALLOWED_ROOTS = {"slides", "interactive", "assets"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
INTERACTIVE_EXTENSIONS = {".html", ".svg"}


def clamp(n, low=0, high=255):
    return int(max(low, min(high, round(n))))


def rgb(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ValueError(f"颜色必须是 #RRGGBB: {value!r}")
    return tuple(int(value[i:i+2], 16) for i in (1, 3, 5))


def hex_color(values):
    return "#" + "".join(f"{clamp(x):02x}" for x in values)


def mix(a, b, weight):
    aa, bb = rgb(a), rgb(b)
    return hex_color([aa[i] * (1-weight) + bb[i] * weight for i in range(3)])


def luminance(color):
    r, g, b = rgb(color)
    return 0.2126*r + 0.7152*g + 0.0722*b


def read_slide_backdrop(path):
    """Quantized dominant border color; gracefully falls back without Pillow."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(path) as original:
            image = original.convert("RGB")
            image.thumbnail((360, 240))
            w, h = image.size
            band = max(2, min(w, h)//28)
            px = image.load()
            samples = []
            for y in range(0, h, 2):
                for x in range(0, w, 2):
                    if x < band or x >= w-band or y < band or y >= h-band:
                        samples.append(px[x, y])
            if not samples:
                return None
            groups = Counter(tuple((c//16)*16 for c in p) for p in samples)
            common, _ = groups.most_common(1)[0]
            matched = [p for p in samples if all(abs(p[k]-common[k]) < 16 for k in range(3))]
            return hex_color([sum(p[k] for p in matched)/len(matched) for k in range(3)])
    except Exception:
        return None


def safe_source(project, raw):
    if not isinstance(raw, str) or not raw:
        raise ValueError("每页 src 必须是非空相对路径")
    p = Path(raw)
    if p.is_absolute() or ".." in p.parts or not p.parts or p.parts[0] not in ALLOWED_ROOTS:
        raise ValueError(f"不允许访问汇报工程之外的 src: {raw}")
    return project / p


MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml"}


def data_uri(path):
    mime = MIME.get(path.suffix.lower(), "application/octet-stream")
    return "data:%s;base64,%s" % (mime, base64.b64encode(path.read_bytes()).decode("ascii"))


CSS_URL = re.compile(r'url\(\s*([\'"]?)([^\'")]+)\1\s*\)')


def inline_page(page_path):
    """把交互页及其本地 CSS/JS/图片全部内联，deck.html 单文件即可运行。"""
    text = page_path.read_text(encoding="utf-8")
    folder = page_path.parent

    def local(url):
        if re.match(r"^(?:[a-zA-Z]+:|//|#)", url):
            return None
        target = (folder / url)
        return target if target.is_file() else None

    def css_url(m):
        target = local(m.group(2).strip())
        return "url(%s)" % data_uri(target) if target else m.group(0)

    def link_repl(m):
        target = local(m.group(1))
        if not target or target.suffix.lower() != ".css":
            return m.group(0)
        css = target.read_text(encoding="utf-8")
        css = CSS_URL.sub(css_url, css)
        return "<style>\n%s\n</style>" % css

    def script_repl(m):
        target = local(m.group(1))
        if not target or target.suffix.lower() != ".js":
            return m.group(0)
        return "<script>\n%s\n</script>" % target.read_text(encoding="utf-8")

    def img_repl(m):
        target = local(m.group(2))
        return (m.group(1) + data_uri(target) + m.group(3)) if target else m.group(0)

    text = re.sub(r'<link\b[^>]*?href="([^"]+)"[^>]*>', link_repl, text, flags=re.I)
    text = re.sub(r'<script\b[^>]*?src="([^"]+)"[^>]*>\s*</script>', script_repl, text, flags=re.I)
    text = re.sub(r'(<img\b[^>]*?src=")([^"]+)(")', img_repl, text, flags=re.I)
    return text


def init_project(project, n, interactive, title):
    project.mkdir(parents=True, exist_ok=True)
    cfgfile = project / "deck.json"
    if cfgfile.exists():
        raise FileExistsError(f"已有配置，避免覆盖：{cfgfile}")
    for folder in ("slides", "interactive", "assets"):
        (project / folder).mkdir(exist_ok=True)
    slides = []
    for i in range(1, n+1):
        is_interactive = i in interactive
        slides.append({
            "no": i,
            "title": f"P{i:02d} · 请填写标题",
            "kind": "interactive" if is_interactive else "image",
            "src": f"interactive/P{i:02d}.html" if is_interactive else f"slides/P{i:02d}.png",
        })
    config = {
        "title": title,
        "subtitle": "研究进展汇报",
        "theme": {"mode": "auto", "accent": "#2e766b"},
        "slides": slides,
    }
    cfgfile.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已初始化 {cfgfile}，共 {n} 页，其中 {len(interactive)} 页预留交互内容。")


def resolve_theme(project, cfg):
    opts = cfg.get("theme", {})
    if not isinstance(opts, dict):
        raise ValueError("theme 应为对象")
    theme = DEFAULT.copy()
    if opts.get("mode", "auto") == "auto":
        backgrounds = []
        for slide in cfg["slides"]:
            if slide.get("kind") != "image":
                continue
            source = safe_source(project, slide["src"])
            if source.is_file():
                found = read_slide_backdrop(source)
                if found:
                    backgrounds.append(rgb(found))
        if backgrounds:
            # Deck-wide color represents the typical page, not just a dark cover.
            chosen = hex_color([median(p[k] for p in backgrounds) for k in range(3)])
            light = luminance(chosen) > 145
            theme["paper"] = chosen
            theme["surface"] = mix(chosen, "#ffffff" if light else "#000000", 0.10)
            theme["ink"] = "#17202a" if light else "#f7f7f4"
            theme["muted"] = "#66727d" if light else "#d3d9da"
            theme["line"] = mix(chosen, theme["ink"], .19)
    # Manual overrides have precedence, so mismatched theme can be aligned deliberately.
    for key in DEFAULT:
        value = opts.get(key)
        if value:
            rgb(value)
            theme[key] = value.lower()
    theme["hover"] = mix(theme["surface"], theme["ink"], .09)
    theme["pending"] = mix(theme["paper"], theme["ink"], .05)
    return theme


def create_deck_html(cfg, slides, theme):
    title = html.escape(str(cfg.get("title", "Research Deck")))
    subtitle = html.escape(str(cfg.get("subtitle", "研究汇报")))
    js_slides = json.dumps(slides, ensure_ascii=False).replace("</", "<\\/")
    js_theme = json.dumps(theme, ensure_ascii=False)
    css = "\n".join(f"--{k}:{v};" for k, v in theme.items())
    page = r'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>__TITLE__ · Research Deck</title>
<style>
:root { __VARS__ }
*{box-sizing:border-box} html,body{height:100%;margin:0}
body{background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,"PingFang SC","Microsoft YaHei",sans-serif;display:flex;flex-direction:column;overflow:hidden}
button{font:inherit;cursor:pointer;color:inherit}
header,footer{flex:none;display:flex;align-items:center;background:var(--surface);border-color:var(--line)}
header{height:51px;padding:0 17px;gap:14px;border-bottom:1px solid var(--line)}
.brand{flex:1;min-width:0;display:flex;align-items:baseline;gap:12px}
.brand small{font-size:10px;letter-spacing:.13em;text-transform:uppercase;font-weight:850;color:var(--accent)}
.brand strong{font-family:Georgia,"Songti SC",serif;font-size:16px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sub{max-width:300px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:var(--muted);font-size:12px}
.btn{border:1px solid var(--line);background:transparent;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:650}
.btn:hover:not(:disabled){background:var(--hover)}
main{flex:1;min-height:0;position:relative;background:var(--paper)}
.slide{position:absolute;inset:0;width:100%;height:100%;border:0;display:none;object-fit:contain;background:var(--paper)}
iframe.slide{inset:auto;transform-origin:top left}
.pending{position:absolute;inset:0;display:none;align-items:center;justify-content:center;text-align:center;padding:40px}
.pending-card{padding:40px 58px;border:1px dashed var(--line);border-radius:18px;background:var(--pending);max-width:680px}
.pending .num{font:500 60px Georgia,serif;opacity:.28}.pending h2{font-size:24px;margin:8px 0}
.pending p{font-size:14px;color:var(--muted);line-height:1.6}
footer{height:56px;padding:0 14px;gap:12px;border-top:1px solid var(--line)}
.nav{display:flex;align-items:center;gap:7px}.nav button{font-size:20px;min-width:38px;height:36px;padding:0}
.nav button:disabled{opacity:.28;cursor:default}
.counter{font-family:Georgia,serif;font-size:18px;font-variant-numeric:tabular-nums;white-space:nowrap}
.counter span{font:12px ui-sans-serif,sans-serif;color:var(--muted)}
.progress{flex:1;display:flex;justify-content:center;gap:5px;overflow:hidden}
.progress button{padding:0;border:0;background:transparent;width:24px;height:27px;display:flex;align-items:center}
.progress i{display:block;background:var(--line);border-radius:10px;width:100%;height:5px;transition:.18s}
.progress button.current i{background:var(--accent);height:15px}
.status{font-size:11px;color:var(--muted);white-space:nowrap}
.drawer{position:fixed;z-index:5;top:51px;bottom:56px;left:0;width:min(410px,90vw);padding:19px;overflow:auto;background:var(--surface);border-right:1px solid var(--line);box-shadow:0 10px 35px #0002;transform:translateX(-110%);transition:transform .18s}
.drawer.open{transform:translateX(0)}
.drawer h3{font-family:Georgia,"Songti SC",serif;font-size:20px;margin:0 0 16px}
.item{display:flex;width:100%;border:0;border-radius:10px;text-align:left;align-items:center;background:transparent;padding:12px 10px;gap:13px;font-size:13px}
.item:hover,.item.now{background:var(--hover)}.item .no{font:12px ui-monospace,monospace;color:var(--accent);min-width:24px}
.item .tx{flex:1}.item .hint{color:var(--muted);font-size:11px}
.scrim{display:none;position:fixed;inset:51px 0 56px;background:#0004;z-index:4}.scrim.open{display:block}
body.hide-chrome header,body.hide-chrome footer{display:none}
body.hide-chrome .drawer{top:0;bottom:0}body.hide-chrome .scrim{inset:0}
@media(max-width:750px){.sub,.status,.brand small{display:none}.progress button{width:13px}header{gap:6px}.brand strong{font-size:14px}}
</style></head>
<body>
<header><div class="brand"><small>RESEARCH DECK</small><strong>__TITLE__</strong><span class="sub">__SUBTITLE__</span></div>
<button class="btn" id="tocBtn">目录</button><button class="btn" id="hideBtn">隐藏边框</button><button class="btn" id="fsBtn">全屏</button></header>
<main id="stage"></main><div class="scrim" id="scrim"></div><aside class="drawer" id="drawer"><h3>页面目录</h3><div id="toc"></div></aside>
<footer><div class="nav"><button class="btn" id="prevBtn">‹</button><button class="btn" id="nextBtn">›</button></div>
<div class="counter" id="counter"></div><div class="progress" id="progress"></div><span class="status" id="status"></span></footer>
<script>
'use strict';
const SLIDES=__SLIDES__;
const THEME=__THEME__;
const stage=document.getElementById('stage');
const views=new Map();
let active=0;
const pad=n=>String(n).padStart(2,'0');
function makeView(s){
 let el;
 if(!s.ready){
   el=document.createElement('div');el.className='pending';
   const card=document.createElement('div');card.className='pending-card';
   const no=document.createElement('div');no.className='num';no.textContent=pad(s.no);card.append(no);
   const h=document.createElement('h2');h.textContent=s.title;card.append(h);
   const p=document.createElement('p');p.textContent=s.kind==='interactive'?'交互页面预留位 · 请将 HTML 或 SVG 放到约定路径后重新 build':'本页 PNG 尚未放入工程 · 请补齐后重新 build';card.append(p);
   el.append(card);
 }else if(s.kind==='image'){
   el=document.createElement('img');el.className='slide';el.alt=s.title;el.src=s.src;
 }else{
   el=document.createElement('iframe');el.className='slide';el.title=s.title;
   el.dataset.fw=(s.frame&&s.frame[0])||1280;el.dataset.fh=(s.frame&&s.frame[1])||720;
   if(s.html){el.srcdoc=s.html;}else{el.src=s.src;}
   el.addEventListener('load',()=>{try{el.contentWindow.postMessage({__deckTheme:THEME},'*');}catch(e){}});
 }
 if(!s.ready)el.className='pending';
 if(s.paper && s.kind==='image')el.style.background=s.paper;
 el.style.display='none';stage.append(el);return el;
}
function fitFrames(){
 const r=stage.getBoundingClientRect();
 views.forEach(el=>{if(el.tagName==='IFRAME'){
  const fw=Number(el.dataset.fw)||1280,fh=Number(el.dataset.fh)||720;
  const k=Math.min(r.width/fw,r.height/fh);
  el.style.width=fw+'px';el.style.height=fh+'px';
  el.style.left=((r.width-fw*k)/2)+'px';el.style.top=((r.height-fh*k)/2)+'px';
  el.style.transformOrigin='top left';
  el.style.transform='scale('+k+')';
 }});
}
function go(i,fromHash=false){
 i=Math.max(0,Math.min(SLIDES.length-1,i));active=i;
 const s=SLIDES[i];stage.style.background=s.paper||THEME.paper;
 if(!views.has(i))views.set(i,makeView(s));
 fitFrames();
 views.forEach((el,k)=>{el.style.display=k===i?(el.classList.contains('pending')?'flex':'block'):'none';});
 document.getElementById('counter').innerHTML=pad(i+1)+' <span>/ '+pad(SLIDES.length)+(s.no!==i+1?' · P'+pad(s.no):'')+'</span>';
 document.getElementById('prevBtn').disabled=i===0;
 document.getElementById('nextBtn').disabled=i===SLIDES.length-1;
 document.getElementById('status').textContent=s.ready?(s.kind==='interactive'?'交互页':'图片页'):(s.kind==='interactive'?'交互页待嵌入':'图片页待补齐');
 document.querySelectorAll('.progress button').forEach((el,j)=>el.classList.toggle('current',j===i));
 document.querySelectorAll('.item').forEach((el,j)=>el.classList.toggle('now',j===i));
 document.title='P'+pad(s.no)+' · '+s.title+' · __TITLE__';
 if(!fromHash)history.replaceState(null,'','#p'+s.no);
}
function toggleDrawer(force){const open=force===undefined?!document.getElementById('drawer').classList.contains('open'):force;
 document.getElementById('drawer').classList.toggle('open',open);document.getElementById('scrim').classList.toggle('open',open);}
SLIDES.forEach((s,i)=>{
 const b=document.createElement('button');b.title='P'+pad(s.no)+' '+s.title;
 b.innerHTML='<i></i>';b.addEventListener('click',()=>go(i));document.getElementById('progress').append(b);
 const el=document.createElement('button');el.className='item';
 const no=document.createElement('span');no.className='no';no.textContent=pad(s.no);
 const tx=document.createElement('span');tx.className='tx';tx.textContent=s.title;
 const info=document.createElement('span');info.className='hint';info.textContent=s.ready?(s.kind==='interactive'?'交互':'图片'):'待补齐';
 el.append(no,tx,info);el.addEventListener('click',()=>{go(i);toggleDrawer(false);});document.getElementById('toc').append(el);
});
document.getElementById('tocBtn').onclick=()=>toggleDrawer();
document.getElementById('scrim').onclick=()=>toggleDrawer(false);
document.getElementById('prevBtn').onclick=()=>go(active-1);
document.getElementById('nextBtn').onclick=()=>go(active+1);
document.getElementById('hideBtn').onclick=()=>{document.body.classList.toggle('hide-chrome');};
document.getElementById('fsBtn').onclick=()=>{if(document.fullscreenElement)document.exitFullscreen();else document.documentElement.requestFullscreen?.();};
window.addEventListener('keydown',e=>{
 if(e.ctrlKey||e.metaKey||e.altKey)return;
 if(['ArrowRight','ArrowDown','PageDown'].includes(e.key)){go(active+1);e.preventDefault();}
 else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){go(active-1);e.preventDefault();}
 else if(e.key==='Home'){go(0);}else if(e.key==='End'){go(SLIDES.length-1);}
 else if(e.key==='Escape'){toggleDrawer(false);}
 else if(e.key==='h'||e.key==='H'){document.body.classList.toggle('hide-chrome');}
 else if(e.key==='f'||e.key==='F'){document.getElementById('fsBtn').click();}
});
window.addEventListener('resize',()=>{fitFrames();});
window.addEventListener('message',e=>{
 const view=views.get(active);if(!view||view.tagName!=='IFRAME'||e.source!==view.contentWindow)return;
 const action=e.data&&e.data.__deck;
 if(action==='next')go(active+1);else if(action==='prev')go(active-1);
});
window.addEventListener('hashchange',()=>{const m=/^#p(\d+)$/.exec(location.hash);if(m){const at=SLIDES.findIndex(x=>x.no===Number(m[1]));if(at!==-1)go(at,true);}});
const hash=/^#p(\d+)$/.exec(location.hash);
const start=hash?SLIDES.findIndex(x=>x.no===Number(hash[1])):-1;
go(start>=0?start:0,true);
</script></body></html>'''
    return (page.replace("__TITLE__", title).replace("__SUBTITLE__", subtitle)
                .replace("__VARS__", css).replace("__SLIDES__", js_slides)
                .replace("__THEME__", js_theme))


def build(project, package=True):
    config_path = project / "deck.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"缺少 {config_path}；先 init 或放入 deck.json")
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    originals = cfg.get("slides", [])
    if not originals or not isinstance(originals, list):
        raise ValueError("deck.json.slides 至少要有一页")
    nums = [s.get("no") for s in originals]
    # 允许跳号（例如原图缺 P15，后续页仍保留 PNG 上印的 P16…P20 编号）：
    # 只要求递增、不重复、为正整数。
    if (len(set(nums)) != len(nums) or nums != sorted(nums)
            or any(not isinstance(n, int) or n < 1 for n in nums)):
        raise ValueError("slides 的 no 必须是递增、不重复的正整数（可跳号）")
    slides = []
    for item in originals:
        kind = item.get("kind")
        if kind not in ("image", "interactive"):
            raise ValueError(f"P{item['no']:02d} kind 只能是 image 或 interactive")
        source = safe_source(project, item.get("src"))
        suffix = source.suffix.lower()
        allowed = IMAGE_EXTENSIONS if kind == "image" else INTERACTIVE_EXTENSIONS
        if suffix not in allowed:
            raise ValueError(f"P{item['no']:02d} kind 与后缀不匹配：{source.name}")
        slides.append({
            "no": item["no"], "title": str(item.get("title") or f"P{item['no']:02d}"),
            "kind": kind, "src": source.relative_to(project).as_posix(), "ready": source.is_file(),
            "paper": read_slide_backdrop(source) if kind == "image" and source.is_file() else None,
            "frame": item.get("frame") or [1280, 720],
        })
    theme = resolve_theme(project, cfg)

    # 图片页直接以 base64 内嵌，deck.html 单文件即可显示全部静态页，
    # 不再依赖 slides/ 的本地相对路径（便于直接发给别人）。
    for slide in slides:
        if slide["kind"] != "image" or not slide["ready"]:
            continue
        source = project / slide["src"]
        mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".webp": "image/webp"}.get(source.suffix.lower(), "application/octet-stream")
        slide["file"] = slide["src"]
        slide["src"] = "data:%s;base64,%s" % (
            mime, base64.b64encode(source.read_bytes()).decode("ascii"))

    # 交互页（含 P16/P17）同样内联为 srcdoc：CSS / JS / 图片全部写进单文件，
    # 每次 build 都重新读取源文件，改完 P16/P17 重新构建即可生效。
    for slide in slides:
        if slide["kind"] != "interactive" or not slide["ready"]:
            continue
        source = project / slide["src"]
        slide["file"] = slide["src"]
        slide["html"] = inline_page(source)

    output = project / "dist"
    output.mkdir(exist_ok=True)
    # 复制交互页依赖，便于单独打开 interactive/*.html；slides/ 已全部 base64 内嵌，不再复制。
    # local_config.json 含内网服务地址，属于本地私有配置，任何时候都不进 dist/、不进 Git。
    PRIVATE = {"local_config.json"}
    for folder in ("interactive", "assets"):
        shutil.copytree(source := project / folder, output / folder, dirs_exist_ok=True,
                        ignore=lambda d, names: [n for n in names if n in PRIVATE])
    (output / "deck.html").write_text(create_deck_html(cfg, slides, theme), encoding="utf-8")
    (output / "README.txt").write_text(
        "打开 deck.html；Arrow Left/Right 翻页，F 全屏，H 隐藏/显示周边导航。\n"
        "HTML/SVG 交互页可在原工程 interactive/ 中完善，随后重新 build。\n"
        "若浏览器对 file:// 的交互页有安全限制，可在 dist 下执行 python -m http.server 8000。\n",
        encoding="utf-8")
    if package:
        bundle = project / "deck_bundle.zip"
        with ZipFile(bundle, "w", ZIP_DEFLATED, compresslevel=6) as archive:
            for file in sorted(output.rglob("*")):
                if file.is_file():
                    archive.write(file, file.relative_to(output).as_posix())
    pending = [f"P{s['no']:02d}({s['kind']})" for s in slides if not s["ready"]]
    print(f"完成：{output/'deck.html'}；已到位 {len(slides)-len(pending)}/{len(slides)} 页")
    print(f"周边主题：paper={theme['paper']} accent={theme['accent']} ink={theme['ink']}")
    if pending:
        print("预留/缺失页面："+", ".join(pending))
    if package:
        print(f"离线压缩包：{bundle}")


def main():
    parser = argparse.ArgumentParser(description="PNG + HTML/SVG 混合研究汇报播放器生成器")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="初始化一次性配置与约定目录")
    init.add_argument("project", type=Path)
    init.add_argument("--pages", type=int, default=10)
    init.add_argument("--interactive", default="", help="交互页号：3,8")
    init.add_argument("--title", default="研究进展汇报")
    builder = sub.add_parser("build", help="组装混合网页播放器")
    builder.add_argument("project", type=Path)
    builder.add_argument("--no-zip", action="store_true")
    args = parser.parse_args()
    if args.command == "init":
        if args.pages < 1:
            parser.error("页数必须大于 0")
        try:
            selected = {int(x.strip()) for x in args.interactive.split(",") if x.strip()}
        except ValueError:
            parser.error("--interactive 应为逗号分隔的页号，例如 3,8")
        if any(i<1 or i>args.pages for i in selected):
            parser.error("交互页号必须落在 1..pages 范围")
        init_project(args.project.resolve(), args.pages, selected, args.title)
    else:
        build(args.project.resolve(), package=not args.no_zip)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"失败：{exc}")
