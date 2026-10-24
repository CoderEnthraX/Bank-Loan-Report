import sys, itertools
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from engine2 import prepare
from tightdata import TRADES
from esub import ev_ok
from daily2 import daily2, dayidx2
EVS = {'core': (), 'vsl': ('vsl',), 'vw+vsl': ('vw', 'vsl'), 'all-but-first-sun': ('vw', 'mom', 'vsl'), 'E1': ('vw', 'mom', 'vsl', 'first', 'sun')}
def feats(P, i, d, t):
    Dd = daily2(P); k = dayidx2(P, i); pd = Dd[k - 1]; td = Dd[k]; p2 = Dd[k - 2]; A = P[('atr', 14)][i]; c = P['C'][i]; e = t['entry']
    r = lambda x: d * (c - x) / A
    return {'c-pdO': r(pd['o']), 'c-pdC': r(pd['c']), 'c-pdMid': r((pd['h'] + pd['l']) / 2), 'c-pdVW': r(pd['vw']), 'c-p2C': r(p2['c']), 'c-tdO': r(td['o']),
            'pdBody': d * (pd['c'] - pd['o']) / A, 'pd2': d * (pd['c'] - p2['c']) / A, 'c-pdFar': r(pd['l'] if d > 0 else pd['h']), 'c-pdNear': r(pd['h'] if d > 0 else pd['l']),
            'e-pdO': d * (e - pd['o']) / A, 'tdO-pdO': d * (td['o'] - pd['o']) / A, 'tdO-pdC': d * (td['o'] - pd['c']) / A}
rows = []
for t in TRADES:
    P = prepare(t['sym']); i = t['arm_i']; d = t['d']; ds = i - P['sinceStart'][i]
    fd = {name: not any(ev_ok(P, j, d, inc) for j in range(ds, i)) for name, inc in EVS.items()}
    rows.append((t, fd, feats(P, i, d, t)))
y = [t['tight'] for t, _, _ in rows]
print('first-of-day only:', {n: (sum(1 for (t, fd, f) in rows if fd[n] and t['tight']), sum(1 for (t, fd, f) in rows if fd[n] and not t['tight'])) for n in EVS})
res = []
for n in EVS:
    for k in rows[0][2]:
        vals = sorted({f[k] for _, _, f in rows})
        for th in vals:
            for sg in (1, -1):
                p = [fd[n] and sg * f[k] <= sg * th for _, fd, f in rows]
                tp = sum(a and b for a, b in zip(p, y)); fp = sum(a and not b for a, b in zip(p, y))
                res.append((8 - tp + fp, fp, n, k, '<=' if sg > 0 else '>=', round(th, 2), [f"{t['sym']} {t['fill'][5:]}" for a, (t, _, _) in zip(p, rows) if a != t['tight']]))
res.sort(key=lambda x: x[:2]); seen = set()
for r in res:
    if (r[2], r[3]) in seen: continue
    seen.add((r[2], r[3])); print(r)
    if len(seen) > 30: break
