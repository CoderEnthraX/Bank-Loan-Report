"""Screen location features on the BASELINE trade list, TRAIN only (feature taken at the signal/arm bar)."""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/location')
import lib, feats
tr = lib.run_all(); tn, te = lib.split(tr)
for x in tr:
    F = feats.compute(x['sym'])
    for nm in feats.NAMES: x[nm] = feats.feature(F, nm, x['arm'], x['dir'])
    x['entD'] = x['dir'] * (F['C'][x['arm']] - x['entry']) / x['atr']      # how far the limit sits behind the signal close
def m(v): return sum(v) / len(v) if v else float('nan')
def st(s): return len(s), m([x['res'] for x in s]), m([x['hit1'] for x in s]), m([1.0 if x['hit1'] else -1.0 for x in s]), m([1.5 if x['hit15'] else -1.0 for x in s])
names = feats.NAMES + ['entD']
if len(sys.argv) > 1: names = sys.argv[1].split(',')
nvar = 0; best = []
for nm in names:
    v = sorted(x[nm] for x in tn if x[nm] is not None)
    if len(v) < 100: print(nm, 'too few'); continue
    q = [v[int(len(v) * k / 5)] for k in range(1, 5)]
    rows = []
    for k in range(5):
        lo = -1e18 if k == 0 else q[k - 1]; hi = 1e18 if k == 4 else q[k]
        s = [x for x in tn if x[nm] is not None and lo <= x[nm] < hi]; rows.append('%5.2f|n%3d E2%+.2f h1 %.0f%%' % ((lo if k else v[0]), *st(s)[:3]))
    print('%-9s' % nm, '  '.join(r.replace('h1 ', 'h1 ') for r in rows))
    # threshold cut search: keep x<=thr or x>=thr (None kept), keep>=60% of TRAIN
    for p in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]:
        for side in ('le', 'ge'):
            thr = v[int(len(v) * (1 - p))] if side == 'le' else v[int(len(v) * p)]
            keep = [x for x in tn if x[nm] is None or (x[nm] <= thr if side == 'le' else x[nm] >= thr)]
            nvar += 1
            n, e2, h1, e1, e15 = st(keep)
            best.append((e2, nm, side, thr, n, e1, e15))
best.sort(reverse=True)
print('variants screened', nvar, 'TRAIN base', st(tn))
seen = set()
for b in best:
    if b[1] in seen: continue
    seen.add(b[1]); print('  %-9s %s %+.3f  n=%d  E2 %+.3f E1 %+.3f E15 %+.3f' % (b[1], b[2], b[3], b[4], b[0], b[5], b[6]))
