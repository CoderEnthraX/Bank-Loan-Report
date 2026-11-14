"""Strategy 12 pick: robustness (path modes, costs 0.40), one-step neighbours in the M1 grid (both path modes), overlap with 1-11, years."""
import sys, os, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fractal')
import ana1, engine as EN
from final11 import ALL
B = EN.load()
for _k in ('t', 'O', 'H', 'L', 'C'): B['M1_' + _k] = B[_k]
P = ('M1', 45, 200, -0.05, 0.75, 3.0, 0.2, 0.0)
t1 = B['t']
for tag, pm, cost in (('path rule', 0, 0.23), ('low first', 1, 0.23), ('high first', 2, 0.23), ('costs 0.40', 0, 0.40)):
    tr = EN.run(B, 'M1', *P, pm=pm); st = EN.stats(tr, P[4], cost); rs = np.bincount(tr[:, 4].astype(int), minlength=5)
    yrs = [EN.stats(tr, P[4], cost, t=t1, y0=y, y1=y)['R'] for y in range(2021, 2027)]
    print('%-11s trades %4d win %4.1f%% PF %.2f | %+6.1fR (%+6.1f%%) DD %4.1fR | TP %d SL %d BE %d SALV %d | years %s' % (tag, st['n'], st['win'], st['pf'], st['R'], st['pct'], st['ddR'], rs[1], rs[2], rs[3], rs[4], ' '.join('%+.1f' % x for x in yrs)))
tr = EN.run(B, 'M1', *P); et = t1[tr[:, 0].astype(int)]
ent = np.sort(np.concatenate([t1[EN.run(B, 'M1', *q)[:, 0].astype(int)] for q in ALL]))
j = np.searchsorted(ent, et); near = np.zeros(len(et), bool)
for d in (-1, 0):
    jj = np.clip(j + d, 0, len(ent) - 1); near |= np.abs(ent[jj] - et) <= 3600
print('entries within 1 hour of an entry of strategies 1-11: %.0f%%' % (100 * near.mean()))
os.environ['STAGE'] = 'M1'; a = ana1.load('M1'); os.environ['STAGE'] = 'M1h'; b = ana1.load('M1')
pr = a['prm'][:, :7]; pick = [45, 200, -0.05, 3.0, 0.75, 0.2, 0.0]
G = [sorted(set(np.round(pr[:, k], 6))) for k in range(7)]
def find(v):
    m = np.all(np.isclose(pr, v), axis=1); i = np.flatnonzero(m); return i[0] if len(i) else None
i0 = find(pick); print('grid row: R %+.1f DD %.1f | high-first R %+.1f DD %.1f' % (a['R'][i0], a['dd'][i0], b['R'][i0], b['dd'][i0]))
names = ['right', 'left', 'offset', 'TP', 'SL', 'BE', 'salvage']
for k in range(7):
    g = G[k]; q = g.index(round(pick[k], 6))
    for qq in (q - 1, q + 1):
        if 0 <= qq < len(g):
            v = list(pick); v[k] = g[qq]; i = find(v)
            if i is None: continue
            print('  %-8s %7.2f -> %7.2f | R %+7.1f DD %5.1f years+ %s | high-first R %+7.1f DD %5.1f years+ %s' % (names[k], pick[k], g[qq], a['R'][i], a['dd'][i], (a['yR'][i] > 0).all(), b['R'][i], b['dd'][i], (b['yR'][i] > 0).all()))
