"""Coordinate descent on OBJ over option groups. usage: cd.py <name> '<start json overrides on j.py defaults>' [strict]"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ev, groups
name = sys.argv[1]; start = json.loads(sys.argv[2]); strict = 'strict' in sys.argv
G = groups.G()
from j import IN
def full(over): c = dict(over); return c
def norm(cfg):
    # drop keys equal to j.py defaults so cache keys are canonical
    return {k: v for k, v in sorted(cfg.items()) if IN.get(k, object()) != v}
def feas(r): return r['md'] == 6 and (not strict or ev.ok(r))
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'progress.md')
def log(s):
    print(s, flush=True); open(P, 'a').write(s + '\n')
cur = norm(start); best = ev.ev(cur)
log(f'[{name}] start {json.dumps(cur)} -> {best["line"]}')
it = 0
while True:
    it += 1; cands = []
    for gn, alts in G.items():
        for a in alts:
            c = dict(IN); c.update(cur); c.update(a); c = norm(c)
            if c != cur: cands.append((gn, a, c))
    res = ev.evmany([c for _, _, c in cands])
    imp = [(r['obj'], gn, a, c, r) for (gn, a, c), r in zip(cands, res) if feas(r) and r['obj'] > best['obj']]
    top = sorted(((r['obj'], gn, json.dumps(a)) for (gn, a, c), r in zip(cands, res) if feas(r)), reverse=True)[:8]
    log(f'[{name}] iter {it}: {len(cands)} cands; top feasible: ' + '; '.join(f'{o} {g} {a}' for o, g, a in top))
    if not imp: break
    imp.sort(key=lambda x: -x[0]); o, gn, a, c, r = imp[0]
    log(f'[{name}] iter {it} ACCEPT {gn} {json.dumps(a)} -> {r["line"]}')
    cur, best = c, r
log(f'[{name}] FINAL {json.dumps(cur)} -> {best["line"]}')
