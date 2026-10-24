"""Quintile screen of causal features on baseline trades (arm bar). TRAIN shown, TEST shown alongside for info only."""
import sys, pickle
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/research'); sys.path.insert(0, S + '/research/chop'); import lib, chopfeat
tr = pickle.load(open(S + '/research/chop/base.pkl', 'rb'))
tn, te = lib.split(tr)
names = [k for k in chopfeat.feats('GC') if not k.endswith('_S')]
for nm in names:
    v = [(chopfeat.get(x['sym'], nm, x['arm'], x['dir']), x) for x in tn]; v = [p for p in v if p[0] is not None]; v.sort(key=lambda p: p[0])
    q = len(v) // 5; cuts = [v[k * q][0] for k in range(1, 5)]
    out = []
    for k in range(5):
        g = v[k * q:(k + 1) * q] if k < 4 else v[4 * q:]; out.append(sum(p[1]['res'] for p in g) / len(g))
    w = [(chopfeat.get(x['sym'], nm, x['arm'], x['dir']), x) for x in te]; w = [p for p in w if p[0] is not None]
    bins = [[] for _ in range(5)]
    for f, x in w: bins[sum(f >= c for c in cuts)].append(x['res'])
    o2 = [sum(b) / len(b) if b else float('nan') for b in bins]
    print(f"{nm:10s} cuts {' '.join('%7.3g' % c for c in cuts)} | TRAIN q1..q5 E2 {' '.join('%+.2f' % e for e in out)} | TEST {' '.join('%+.2f' % e for e in o2)} (n {' '.join(str(len(b)) for b in bins)})")
