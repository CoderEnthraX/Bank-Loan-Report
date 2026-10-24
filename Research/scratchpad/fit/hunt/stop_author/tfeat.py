"""Feature table on the 80 GT trades at the displacement bar; single-feature separation search."""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
from tightdata import TRADES
rows = []
for t in TRADES:
    P = get(t['sym']); i = t['arm_i']; d = t['d']
    f = feats(P, i); r = dict(sym=t['sym'], fill=t['fill'], d=d, tight=t['tight'])
    for k, v in f.items():
        r[k] = v
    for k in ('spr', 'cv', 'cvs', 'vsl3', 'vsl10', 'ce20', 'e2050', 'e50200', 'e921', 'ce200', 'ce50', 'lr20', 'lr50', 'ers14'):
        r['d_' + k] = d * f[k]
    for m in (15, 30, 60, 120, 240):
        h = htf_series(P, m)[i]
        if h is None: continue
        r[f'h{m}_adx'] = h['adx']; r[f'h{m}_dspr'] = d * h['spr']; r[f'h{m}_chop'] = h['chop']; r[f'h{m}_er'] = h['er']; r[f'h{m}_ders'] = d * h['ers']
        r[f'h{m}_ddir'] = d * h['dirc']; r[f'h{m}_de2050'] = d * h['e2050']; r[f'h{m}_dce20'] = d * h['ce20']
    rows.append(r)
pickle.dump(rows, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/tfeat.pkl', 'wb'))
keys = [k for k in rows[0] if k not in ('sym', 'fill', 'd', 'tight')]
res = []
for k in keys:
    vals = [(r.get(k), r['tight']) for r in rows if r.get(k) is not None]
    xs = sorted(set(v for v, _ in vals))
    best = None
    for th in xs:
        for side in (1, -1):
            pred = [(side * (v - th) >= 0) for v, _ in vals]
            tp = sum(1 for p, (_, y) in zip(pred, vals) if p and y); fp = sum(1 for p, (_, y) in zip(pred, vals) if p and not y)
            fn = sum(1 for p, (_, y) in zip(pred, vals) if not p and y)
            err = fp + fn
            if best is None or err < best[0]: best = (err, tp, fp, fn, th, side)
    # also best covering all 8
    tv = [v for v, y in vals if y]; lo, hi = min(tv), max(tv)
    fpin = sum(1 for v, y in vals if not y and lo <= v <= hi)
    res.append((best[0], k, best, lo, hi, fpin))
res.sort()
for e, k, b, lo, hi, fpin in res[:40]:
    print(f"{k:12s} err {e} tp {b[1]} fp {b[2]} fn {b[3]} th {b[4]:.3f} side {b[5]:+d} | 8-cover [{lo:.2f},{hi:.2f}] normals inside {fpin}")
