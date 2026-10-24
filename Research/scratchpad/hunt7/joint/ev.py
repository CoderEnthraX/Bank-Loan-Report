"""Evaluator: same subprocesses + OBJ formula as xl/score_all.py, plus the mismatch item set. Cached in cache.jsonl."""
import os, sys, json, re, subprocess
from concurrent.futures import ThreadPoolExecutor
J = os.path.dirname(os.path.abspath(__file__)); S = os.path.dirname(os.path.dirname(J)); X = os.path.join(S, 'xl')
MOD = os.path.join(J, 'j.py')
NEW = {"slopeCross": True, "minOpenBars": 0, "cooldownBars": 1, "dayStopR": 0, "tightOut": True, "erMin": 0.2}
CF = os.path.join(J, 'cache.jsonl'); CACHE = {}
if os.path.exists(CF):
    for l in open(CF):
        try: d = json.loads(l); CACHE[d['k']] = d
        except Exception: pass
def key(cfg): return json.dumps(cfg, sort_keys=True)
def _run(cmd, cwd=X): return subprocess.run(['python3', '-I'] + cmd, cwd=cwd, capture_output=True, text=True, timeout=900).stdout
def _eval(cfg):
    o = json.dumps(cfg)
    a = _run(['score2.py', MOD, o, 'd']); b = _run(['score3.py', MOD, o, 'd'])
    eb = [_run([x, MOD, o]) for x in ('extrasB.py', 'extrasNF.py', 'extrasNG.py')]
    md = _run([os.path.join(S, 'hunt4', 'modelday.py'), o, MOD], cwd=os.path.join(S, 'hunt4')).replace('modelday', '')
    A = eval(a.split('(80):')[1].split('\n')[0])
    def bl(txt, k):
        m = re.search(k + r'.*?time-matched (\d+), missed (\d+), stop correct (\d+)/(\d+)', txt); return int(m.group(1)), int(m.group(3))
    b1 = bl(a, 'SENSEX\\+CRUDE'); b2 = bl(b, 'NIFTY on'); b3 = bl(b, 'NATGAS on')
    pb = [x.count('PROVABLE') for x in eb]
    m = re.search(r'matched (\d+) / 6', md); mdn = int(m.group(1)) if m else -1
    obj = 3 * A['exact'] - 2 * A['miss'] - 2 * A['extra'] + sum(b1) + sum(b2) + sum(b3) - 2 * sum(pb) + 3 * mdn
    items = []
    for l in a.splitlines():
        l = l.strip()
        if l.startswith('A ') and not l.startswith('A screen'): items.append(l)
        if l.startswith('B STOP') or l.startswith('B MISS'): items.append(re.sub(r' model .*', '', l))
    sec = ''
    for l in b.splitlines():
        if l.startswith('NIFTY on'): sec = 'NF'
        if l.startswith('NATGAS on'): sec = 'NG'
        l = l.strip()
        if l.startswith('STOP') or l.startswith('MISS'): items.append(sec + ' ' + ' '.join(l.split()[:5]))
    for x in eb:
        for l in x.splitlines():
            if 'PROVABLE' in l: items.append('PROV ' + l.split('|')[0].replace('PROVABLE-EXTRA ', '').strip())
    line = f"A {A['exact']}/{A['miss']}/{A['extra']} | B1 {b1[0]} st{b1[1]} p{pb[0]} | B2 {b2[0]} st{b2[1]} p{pb[1]} | B3 {b3[0]} st{b3[1]} p{pb[2]} | MD {mdn} | OBJ {obj}"
    return dict(k=key(cfg), obj=obj, A=[A['exact'], A['miss'], A['extra']], md=mdn, line=line, items=sorted(items))
def ev(cfg):
    k = key(cfg)
    if k in CACHE: return CACHE[k]
    try: r = _eval(cfg)
    except Exception as ex:
        o = json.dumps(cfg); er = subprocess.run(['python3', '-I', 'score2.py', MOD, o], cwd=X, capture_output=True, text=True, timeout=900).stderr[-600:]
        open(os.path.join(J, 'errors.log'), 'a').write(k + '\n' + er + '\n')
        r = dict(k=k, obj=-999, A=[0, 99, 99], md=-1, line='ERROR ' + er.strip().splitlines()[-1] if er.strip() else 'ERROR', items=[])
    CACHE[k] = r
    with open(CF, 'a') as f: f.write(json.dumps(r) + '\n')
    return r
def evmany(cfgs, w=4):
    todo = [c for c in cfgs if key(c) not in CACHE]
    with ThreadPoolExecutor(w) as ex: list(ex.map(ev, todo))
    return [CACHE[key(c)] for c in cfgs]
def ok(r): return r['A'][0] >= 80 and r['A'][1] == 0 and r['A'][2] <= 1 and r['md'] == 6
def diff(r, base):
    s, b = set(r['items']), set(base['items'])
    return dict(fixed=sorted(b - s), broke=sorted(s - b))
if __name__ == '__main__':
    cfg = dict(NEW); cfg.update(json.loads(sys.argv[1]) if len(sys.argv) > 1 else {})
    r = ev(cfg); base = ev(NEW); print(r['line']); d = diff(r, base)
    for x in d['fixed']: print('  + fixed', x)
    for x in d['broke']: print('  - broke', x)
