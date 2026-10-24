"""Pairwise plateau search: from base, take all single moves with obj >= base-tol, try every pair. usage: pairs.py name '<base>' tol"""
import sys, json, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ev, groups
from j import IN
name, base, tol = sys.argv[1], json.loads(sys.argv[2]), int(sys.argv[3])
def norm(c): return {k: v for k, v in sorted(c.items()) if IN.get(k, object()) != v}
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'progress.md')
def log(s): print(s, flush=True); open(P, 'a').write(s + '\n')
b = dict(IN); b.update(base); b = norm(b); B = ev.ev(b); G = groups.G()
singles = []
for gn, alts in G.items():
    for a in alts:
        c = dict(IN); c.update(b); c.update(a); c = norm(c)
        if c != b: singles.append((gn, a, c))
rs = ev.evmany([c for _, _, c in singles])
keep = [(gn, a) for (gn, a, c), r in zip(singles, rs) if r['md'] == 6 and r['obj'] >= B['obj'] - tol]
log(f'[{name}] pairs base {B["line"]}; {len(keep)} near-plateau singles (tol {tol})')
cands = []
for (g1, a1), (g2, a2) in itertools.combinations(keep, 2):
    if g1 == g2: continue
    c = dict(IN); c.update(b); c.update(a1); c.update(a2); cands.append((g1, a1, g2, a2, norm(c)))
rs = ev.evmany([x[4] for x in cands])
top = sorted(zip(rs, cands), key=lambda x: -x[0]['obj'])[:10]
for r, (g1, a1, g2, a2, c) in top:
    log(f'[{name}] pair {g1} {json.dumps(a1)} + {g2} {json.dumps(a2)} -> {r["line"]}')
