import sys, os, json, subprocess, importlib, time
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
STATE = os.path.join(BASE, 'state.json')
OUT = os.path.join(BASE, 'out')
sys.path.insert(0, os.path.join(BASE, 'content'))
ACC = os.environ.get('REPLIZ_ACCOUNT_ID', '')
AUTH = ['-u', f"{os.environ['REPLIZ_ACCESS_KEY']}:{os.environ['REPLIZ_SECRET_KEY']}"] if os.environ.get('REPLIZ_ACCESS_KEY') and os.environ.get('REPLIZ_SECRET_KEY') else []
SLOTS_UTC = ["00:00","02:00","04:00","06:00","08:00","10:00","12:00","14:00"]  # 07..21 WIB
def load(): return json.load(open(STATE)) if os.path.exists(STATE) else {}
def save(s): json.dump(s, open(STATE,'w'), indent=1)
def sh(a, **k):
    # Basic Auth hanya untuk api.repliz.com. URL presigned storage tidak boleh memakai Authorization.
    if a and a[0] == 'curl' and AUTH and any(str(x).startswith('https://api.repliz.com') for x in a):
        a = [a[0]] + AUTH + list(a[1:])
    return subprocess.run(a, capture_output=True, text=True, timeout=120, **k)

def upload(path, name):
    sz = os.path.getsize(path)
    for attempt in range(3):
        try:
            r = sh(['curl','-sS','-X','POST','-H','Content-Type: application/json','-d',json.dumps({'filename':name,'size':sz,'mimetype':'image/jpeg'}),'https://api.repliz.com/public/storage/file/init'])
            d = json.loads(r.stdout)
            p = sh(['curl','-sS','-X','PUT','-H','Content-Type: image/jpeg','--data-binary','@'+path,'-w','%{http_code}',d['upload']])
            assert p.stdout.strip().endswith('200'), p.stdout[-200:]
            c = sh(['curl','-sS','-o','/dev/null','-w','%{http_code}','-X','POST',f"https://api.repliz.com/public/storage/file/{d['id']}/complete"])
            assert c.stdout.strip().startswith('2'), c.stdout
            return d['url']
        except Exception as e:
            err = e; time.sleep(2)
    raise err

def run_day(modname, date, skip_slots=(), start_n=0, do_schedule=True):
    mod = importlib.import_module(modname)
    state = load()
    slots = [s for i, s in enumerate(SLOTS_UTC) if i not in skip_slots]
    assert len(mod.DAY) <= len(slots), (len(mod.DAY), len(slots))
    for j, c in enumerate(mod.DAY):
        c['n'] = start_n + j
        slug = c['slug']
        if state.get(slug, {}).get('scheduleId'): print('skip', slug); continue
        d = os.path.join(OUT, slug)
        files = build(c, d)
        r = subprocess.run(['node', os.path.join(BASE,'render.js')] + files, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        jpgs = [f.replace('.html','.jpg') for f in files]
        st = state.get(slug, {})
        urls = st.get('urls') or []
        if len(urls) != 11:
            with ThreadPoolExecutor(4) as ex:
                urls = list(ex.map(lambda a: upload(a[1], f"{slug}-{a[0]:02d}.jpg"), enumerate(jpgs, start=1)))
            state[slug] = {'urls': urls}; save(state)
        if not do_schedule: continue
        at = f"{date}T{slots[j]}:00.000Z"
        body = {"accountId": ACC, "type": "album", "title": c['title'].replace('*',''), "description": caption(c),
                "medias": [{"type":"image","url":u} for u in urls], "scheduleAt": at}
        r = sh(['curl','-sS','-X','POST','-H','Content-Type: application/json','-d',json.dumps(body),'-w','\n%{http_code}','https://api.repliz.com/public/schedule'])
        out, code = r.stdout.rsplit('\n',1)
        assert code.strip() == '201', (slug, code, out[:300])
        state[slug].update({'scheduleId': json.loads(out)['scheduleId'], 'scheduleAt': at}); save(state)
        print('OK', slug, at, state[slug]['scheduleId'], flush=True)

if __name__ == '__main__':
    assert ACC, 'Set REPLIZ_ACCOUNT_ID'
    mod, date = sys.argv[1], sys.argv[2]
    skip = tuple(int(x) for x in sys.argv[3].split(',')) if len(sys.argv) > 3 and sys.argv[3] else ()
    start = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    dry = len(sys.argv) > 5 and sys.argv[5] == 'nosched'
    run_day(mod, date, skip, start, not dry)
