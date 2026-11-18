import re, json, os, subprocess, html, sys
BASE = os.path.dirname(os.path.abspath(__file__))

def load_scenes():
    s = open(os.path.join(BASE, 'scenes.html'), encoding='utf-8').read()
    return re.findall(r'<svg class="scene".*?</svg>', s, re.S)
SCENES = load_scenes()

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#000}
.s{width:1080px;height:1350px;position:relative;overflow:hidden;background:#05070b;font-family:'Inter Display','Inter',sans-serif;color:#fff}
.s svg.scene{position:absolute;inset:0;width:1080px;height:1350px}
.vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,transparent 35%,rgba(0,0,0,.75) 100%)}
.fade{position:absolute;left:0;right:0;bottom:0;height:640px;background:linear-gradient(to top,#030406 18%,rgba(3,4,6,.85) 50%,transparent)}
.grain{position:absolute;inset:0;opacity:.22;mix-blend-mode:overlay;pointer-events:none}
.kick{position:absolute;left:70px;top:62px;font-size:24px;font-weight:800;letter-spacing:7px;color:#ffb21a;text-transform:uppercase;max-width:760px}
.idx{position:absolute;right:70px;top:62px;font-size:24px;font-weight:700;letter-spacing:4px;opacity:.7}
.txt{position:absolute;left:70px;right:70px;bottom:120px}
h1{font-weight:900;text-transform:uppercase;letter-spacing:-5px;line-height:.92}
h1 em,h2 em{font-style:normal;color:#ffb21a}
.sub{margin-top:30px;font-size:36px;font-weight:500;line-height:1.3;opacity:.88;max-width:900px}
.swipe{position:absolute;right:70px;bottom:52px;font-size:24px;letter-spacing:4px;font-weight:700;opacity:.65}
.bg{position:absolute;inset:0}
.ghost{position:absolute;right:-30px;top:120px;font-weight:900;font-size:520px;letter-spacing:-24px;line-height:.8;opacity:.07;color:#fff}
.bar{width:110px;height:10px;background:#ffb21a;margin-bottom:46px}
.c{position:absolute;left:70px;right:70px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center;padding-bottom:40px}
h2{font-weight:900;text-transform:uppercase;letter-spacing:-4px;line-height:.95;margin-bottom:44px}
.body{font-size:54px;line-height:1.36;font-weight:500;color:#ece9e2;letter-spacing:-.4px}
.prog{position:absolute;left:70px;right:70px;bottom:64px;display:flex;gap:8px}
.prog i{flex:1;height:6px;background:rgba(255,255,255,.18);border-radius:3px}
.prog i.on{background:#ffb21a}
.q{margin-top:56px;padding:34px 40px;border:3px solid #ffb21a;border-radius:24px;font-size:42px;font-weight:700;line-height:1.3;letter-spacing:-.5px}
.pills{margin-top:36px;display:flex;gap:16px;flex-wrap:wrap}
.pills span{padding:14px 30px;border-radius:50px;font-size:30px;font-weight:800;background:#ffb21a;color:#0b0b0d}
.pills span.o{background:transparent;color:#fff;border:3px solid #fff}
"""
THEMES = [
 "radial-gradient(ellipse at 85% 10%,rgba(60,120,200,.42),transparent 55%),linear-gradient(160deg,#08111d,#05070b)",
 "radial-gradient(ellipse at 10% 90%,rgba(255,150,40,.35),transparent 55%),linear-gradient(200deg,#120d08,#05070b)",
 "radial-gradient(ellipse at 80% 85%,rgba(190,40,40,.33),transparent 55%),linear-gradient(170deg,#12090b,#05070b)",
 "radial-gradient(ellipse at 15% 15%,rgba(40,160,150,.33),transparent 55%),linear-gradient(190deg,#08130f,#05070b)",
]
GRAIN = '<svg class="grain" width="1080" height="1350"><rect width="1080" height="1350" filter="url(#gr)"/></svg>'
DEFS = '<svg width="0" height="0" style="position:absolute"><defs><filter id="gr"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/><feColorMatrix values="0 0 0 0 .5  0 0 0 0 .5  0 0 0 0 .5  0 0 0 1.2 -.1"/></filter><filter id="bl"><feGaussianBlur stdDeviation="5"/></filter></defs></svg>'

def em(t):
    t = html.escape(t, quote=False)
    return re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)

def page(inner):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{DEFS}{inner}</body></html>'

def prog(i, n=11):
    return '<div class="prog">' + ''.join(f'<i class="{"on" if k<=i else ""}"></i>' for k in range(1, n+1)) + '</div>'

def cover(c, v):
    total = c.get('total', 11)
    fade_style = 'height:980px;background:linear-gradient(to top,#030406 40%,rgba(3,4,6,.92) 62%,rgba(3,4,6,.5) 82%,transparent)' if c.get('hook') else ''
    if c.get('hook'):
        plain = re.sub(r'\*', '', c['hook'])
        n = len(plain)
        fs = 108 if n < 55 else 96 if n < 75 else 86 if n < 95 else 78
        title_html = f'<h1 style="font-size:{fs}px;text-transform:none;letter-spacing:-3px;line-height:1.04">{em(c["hook"])}</h1>'
    else:
        plain = re.sub(r'\*', '', c['title'])
        fs = 132 if len(plain) < 26 else 112 if len(plain) < 38 else 96
        title_html = f'<h1 style="font-size:{fs}px">{em(c["title"])}</h1>'
    return page(f'''<div class="s">{SCENES[v % len(SCENES)]}<div class="vig"></div><div class="fade" style="{fade_style}"></div>{GRAIN}
<div class="kick">ELIT GLOBAL · {html.escape(c["cat"])}</div><div class="idx">1/{total}</div>
<div class="txt">{title_html}<div class="sub">{html.escape(c["sub"])}</div></div><div class="swipe">GESER →</div></div>''')

def content(c, i, head, body):
    th = THEMES[(i + c['n']) % len(THEMES)]
    plain = re.sub(r'\*', '', head)
    fs = 140 if len(plain) < 14 else 116 if len(plain) < 22 else 96
    return page(f'''<div class="s"><div class="bg" style="background:{th}"></div><div class="ghost">{i-1:02d}</div><div class="vig"></div>{GRAIN}
<div class="kick">{html.escape(c["cat"])} · {html.escape(c["short"])}</div><div class="idx">{i}/11</div>
<div class="c"><div class="bar"></div><h2 style="font-size:{fs}px">{em(head)}</h2><div class="body">{em(body)}</div></div>{prog(i)}</div>''')

def closing(c):
    th = THEMES[c['n'] % len(THEMES)]
    return page(f'''<div class="s"><div class="bg" style="background:{th}"></div><div class="ghost" style="font-size:420px">?</div><div class="vig"></div>{GRAIN}
<div class="kick">{html.escape(c["cat"])} · KESIMPULAN</div><div class="idx">11/11</div>
<div class="c"><div class="bar"></div><h2 style="font-size:120px">{em("Ke*simpulan*")}</h2><div class="body">{em(c["take"])}</div>
<div class="q">{html.escape(c["q"])}</div><div class="pills"><span>Simpan</span><span>Bagikan</span><span class="o">Komentar 👇</span></div></div>{prog(11)}</div>''')

def build(c, outdir):
    os.makedirs(outdir, exist_ok=True)
    files = []
    def w(name, h):
        p = os.path.join(outdir, name + '.html'); open(p, 'w', encoding='utf-8').write(h); files.append(p)
    w('s01', cover(c, c['n']))
    for k, (h, b) in enumerate(c['slides'], start=2):
        w(f's{k:02d}', content(c, k, h, b))
    w('s11', closing(c))
    return files

def caption(c):
    q = c['q']
    if c.get('hook'):
        h = re.sub(r'\*', '', c['hook'])
        return f"{h}\n\n{c['sub']}\n\nSwipe sampai slide terakhir 👉\n{q}\n\n{c['tags']}"
    return f"{c['sub']}\n\nSwipe sampai slide terakhir 👉\n{q}\n\n{c['tags']}"

def mk(slug, cat, short, title, sub, tags, slides, take, q):
    assert len(slides) == 9, (slug, len(slides))
    return dict(slug=slug, cat=cat, short=short, title=title, sub=sub, tags=tags, slides=slides, take=take, q=q)
