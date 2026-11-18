import sys, os, json, subprocess, importlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from hooks import HOOKS
from pipeline import upload, sh, ACC
from datetime import datetime, timezone, timedelta

DAYS = [("day01",0),("day02",7),("day03",15),("day04",23),("day05",31),("day06",39),("day06b",46),("day07",47),("day08",55),("day09",63),("day10",71),("day11",79),("day12",87),("day13",95)]
def load_carousels():
    out = {}
    for mod, start in DAYS:
        m = importlib.import_module(mod)
        for j, c in enumerate(m.DAY):
            c['n'] = start + j
            out[c['slug']] = c
    for k, c in out.items():
        c['hook'] = HOOKS[k]
    assert set(out) == set(HOOKS), (set(out) ^ set(HOOKS))
    return out

def render_covers(cs, only=None):
    files = []
    for slug, c in cs.items():
        if only and slug not in only: continue
        d = os.path.join(OUT_DIR, slug); os.makedirs(d, exist_ok=True)
        p = os.path.join(d, 'h01.html'); open(p, 'w', encoding='utf-8').write(cover(c, c['n']))
        files.append(p)
    r = subprocess.run(['node', os.path.join(BASE, 'render.js')] + files, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return files
OUT_DIR = os.path.join(BASE, 'out')

if __name__ == '__main__':
    cs = load_carousels()
    files = render_covers(cs)
    print(len(files), 'sampul dirender')
