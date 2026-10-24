import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ev import ev, fmt
import m as M
from grid import GRID
start = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
log = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[2] if len(sys.argv) > 2 else 'cd.log'), 'a')
cfg = dict(start); cache = {}
def E(c):
    k = json.dumps(c, sort_keys=True)
    if k not in cache: cache[k] = ev(c)
    return cache[k]
base = E(cfg); print('start', cfg, fmt(base), file=log, flush=True)
for sweep in range(4):
    improved = False
    for k, vals in GRID.items():
        cur = cfg.get(k, M.IN[k]); best = (E(cfg)['obj'], cur)
        res = []
        for v in vals:
            c = dict(cfg); c[k] = v
            if v == M.IN[k]: c.pop(k)
            r = E(c); res.append((v, r))
            if r['obj'] > best[0]: best = (r['obj'], v)
        line = ' '.join(f"{v}:{r['obj']}" for v, r in res)
        print(f'sweep{sweep} {k}: {line}', file=log, flush=True)
        if best[1] != cur:
            if best[1] == M.IN[k]: cfg.pop(k, None)
            else: cfg[k] = best[1]
            improved = True; print(f'  -> {k}={best[1]}  {fmt(E(cfg))}  cfg={json.dumps(cfg)}', file=log, flush=True)
    if not improved: break
print('FINAL', json.dumps(cfg), fmt(E(cfg)), sorted(E(cfg)['bad']), file=log, flush=True)
