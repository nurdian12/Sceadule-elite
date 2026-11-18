import sys, os, json, subprocess, re, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rehook import *
assert ACC, 'Set REPLIZ_ACCOUNT_ID'
from concurrent.futures import ThreadPoolExecutor
DONE = os.path.join(BASE, 'rehook_state.json')
done = json.load(open(DONE)) if os.path.exists(DONE) else {}
state = json.load(open(os.path.join(BASE, 'state.json')))
cs = load_carousels()
ids = {slug: v['scheduleId'] for slug, v in state.items() if v.get('scheduleId')}

def get(sid):
    r = sh(['curl', '-sS', f'https://api.repliz.com/public/schedule/{sid}'])
    return json.loads(r.stdout)

now = datetime.now(timezone.utc)
todo = []
for slug, sid in ids.items():
    d = get(sid)
    at = datetime.fromisoformat(d['scheduleAt'].replace('Z', '+00:00'))
    if d['status'] != 'pending' or at < now + timedelta(minutes=10):
        print('lewati', slug, d['status'], d['scheduleAt']); continue
    todo.append((d['scheduleAt'], slug, sid, d))
todo.sort()
print(len(todo), 'jadwal akan diperbarui', flush=True)

def work(item):
    at, slug, sid, d = item
    if done.get(slug): return slug, 'sudah'
    c = cs[slug]
    jpg = os.path.join(OUT_DIR, slug, 'h01.jpg')
    url = upload(jpg, f"{slug}-hook.jpg")
    medias = [{"type": "image", "url": url}] + [{"type": m['type'], "url": m['url']} for m in d['medias'][1:]]
    body = {"accountId": ACC, "type": d['type'], "title": re.sub(r'\*', '', c['hook']), "description": caption(c),
            "medias": medias, "scheduleAt": d['scheduleAt']}
    r = sh(['curl', '-sS', '-X', 'PUT', '-H', 'Content-Type: application/json', '-d', json.dumps(body), '-w', '\n%{http_code}', f'https://api.repliz.com/public/schedule/{sid}'])
    out, code = r.stdout.rsplit('\n', 1)
    if not code.strip().startswith('2'): return slug, f'GAGAL {code} {out[:200]}'
    chk = get(sid)
    ok = chk['medias'][0]['url'] == url and chk['status'] == 'pending' and chk['scheduleAt'] == d['scheduleAt'] and len(chk['medias']) == len(medias)
    if ok: done[slug] = True; json.dump(done, open(DONE, 'w'))
    return slug, 'OK' if ok else 'VERIFIKASI GAGAL'

with ThreadPoolExecutor(3) as ex:
    for slug, res in ex.map(work, todo):
        print(res, slug, flush=True)
print('SELESAI', sum(1 for v in done.values() if v), 'diperbarui')
