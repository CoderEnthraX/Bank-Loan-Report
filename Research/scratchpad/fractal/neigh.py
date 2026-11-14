"""One-step neighbours of a pick in the stage-2 grid (PM 0 and PM 2): R / DD and every-year-positive."""
import numpy as np, sys, os
import ana1
tf = sys.argv[1]; pick = [float(x) for x in sys.argv[2].split(',')]   # r, l, off, tp, sl, be, sv
os.environ['STAGE'] = '2'; a = ana1.load(tf); os.environ['STAGE'] = '2h'; b = ana1.load(tf)
p = a['prm'][:, :7]
G = [sorted(set(np.round(p[:, j], 6))) for j in range(7)]
def find(v):
    m = np.all(np.isclose(p, v), axis=1); i = np.flatnonzero(m)
    return i[0] if len(i) else None
i0 = find(pick); names = ['right', 'left', 'offset', 'TP', 'SL', 'BE', 'salvage']
print('pick %s: R %+.1f DD %.1f (high-first %+.1f DD %.1f)' % (sys.argv[2], a['R'][i0], a['dd'][i0], b['R'][i0], b['dd'][i0]))
for j in range(7):
    g = G[j]; k = g.index(round(pick[j], 6))
    for kk in (k - 1, k + 1):
        if 0 <= kk < len(g):
            v = list(pick); v[j] = g[kk]; i = find(v)
            if i is None: continue
            print('  %-8s %7.2f -> %7.2f | R %+7.1f DD %5.1f R/DD %5.1f years+ %s | high-first R %+7.1f DD %5.1f years+ %s' % (
                names[j], pick[j], g[kk], a['R'][i], a['dd'][i], a['R'][i] / max(a['dd'][i], 1), (a['yR'][i] > 0).all(), b['R'][i], b['dd'][i], (b['yR'][i] > 0).all()))
