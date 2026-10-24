"""Exhaustive search on the first-of-session subset (pbank.pkl): singles, AND pairs, OR pairs with 0 (or <=1) errors.
margin = gap between the threshold-side tight extreme and the nearest normal, divided by the feature's P90-P10 spread over the subset.
Usage: psearch.py [subsetkey=first_vsl_M] [bank=pbank.pkl] [prefix-filter]"""
import os, sys, pickle, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SUBK = sys.argv[1] if len(sys.argv) > 1 else 'first_vsl_M'
BANK = sys.argv[2] if len(sys.argv) > 2 else 'pbank.pkl'
PF = sys.argv[3] if len(sys.argv) > 3 else ''
B = pickle.load(open(os.path.join(HERE, BANK), 'rb'))
sub = [(t, f) for t, f in B if f.get(SUBK, 1.0) == 1.0]
keys = sorted(set(k for _, f in sub for k in f if not k.startswith('first_') and k.startswith(PF)))
keys = [k for k in keys if all(k in f and f[k] == f[k] for _, f in sub)]
X = np.array([[f[k] for k in keys] for _, f in sub], float); y = np.array([t['tight'] for t, _ in sub])
# drop constant / duplicate columns
keep = []; seen = set()
for j in range(X.shape[1]):
    col = X[:, j]
    if col.max() == col.min(): continue
    sig = tuple(np.argsort(col, kind='stable')) + tuple(np.sort(col) > np.sort(col).min())
    keep.append(j)
X = X[:, keep]; keys = [keys[j] for j in keep]
n, F = X.shape
sp = np.percentile(X, 90, 0) - np.percentile(X, 10, 0); sp = np.where(sp > 0, sp, X.std(0)); sp = np.where(sp > 0, sp, 1)
lab = lambda t: f"{t['sym']} {t['fill']} {'L' if t['d'] > 0 else 'S'}"
print(f'subset {SUBK}: {n} trades ({y.sum()} tight), {F} features')
T, N = y, ~y
res = {'single': [], 'and': [], 'or': [], 'single1': []}
# ---- singles: tight iff s*x <= t
for j in range(F):
    for s in (1, -1):
        z = s * X[:, j]; t = z[T].max(); fp = int((z[N] <= t).sum())
        if fp == 0:
            res['single'].append(((z[N].min() - t) / sp[j], keys[j], s, s * t, s * z[N].min()))
        # best with errors: try every tight value as threshold
        best = None
        for tt in np.unique(z):
            e = int((z[T] > tt).sum() + (z[N] <= tt).sum())
            if best is None or e < best[0]: best = (e, tt)
        res['single1'].append((best[0], keys[j], s, s * best[1]))
res['single'].sort(reverse=True); res['single1'].sort()
print('\n== zero-error singles:', len(res['single']))
for m, k, s, t, nn in res['single'][:30]:
    print(f'  {k} {"<=" if s > 0 else ">="} {t:.4g}  (nearest normal {nn:.4g}) margin {m:.3f}')
print('\n== best singles (min errors):')
for e, k, s, t in res['single1'][:25]:
    print(f'  err {e}: {k} {"<=" if s > 0 else ">="} {t:.4g}')
# ---- pairs
Z = np.concatenate([X, -X], 1); KS = [(k, 1) for k in keys] + [(k, -1) for k in keys]; SPZ = np.concatenate([sp, sp])
tmax = Z[T].max(0)                       # AND thresholds
inA = Z[N] <= tmax                       # normals passing atom (nN x 2F)
nmin = Z[N].min(0)                        # OR thresholds (strict)
covO = Z[T] < nmin                        # tights covered by atom (nT x 2F)
cand_and = []; cand_or = []
for a in range(2 * F):
    ka = KS[a]
    for b in range(a + 1, 2 * F):
        kb = KS[b]
        if kb[0] == ka[0]: continue
        fpm = inA[:, a] & inA[:, b]; fp = int(fpm.sum())
        if fp <= 1:
            if fp == 0:
                # margins: for normals passing b, gap in a; for normals passing a, gap in b
                za = Z[N][inA[:, b], a]; zb = Z[N][inA[:, a], b]
                ma = (za.min() - tmax[a]) / SPZ[a] if za.size else np.inf
                mb = (zb.min() - tmax[b]) / SPZ[b] if zb.size else np.inf
                if np.isinf(ma) or np.isinf(mb): continue     # single feature suffices
                cand_and.append((min(ma, mb), 0, ka, kb, tmax[a] * ka[1], tmax[b] * kb[1], ma, mb, ''))
            else:
                w = [lab(t) for (t, _), m in zip([x for x, yy in zip(sub, y) if not yy], fpm) if m]
                cand_and.append((-1, 1, ka, kb, tmax[a] * ka[1], tmax[b] * kb[1], 0, 0, w[0]))
        cov = covO[:, a] | covO[:, b]; fn = int((~cov).sum())
        if fn <= 1:
            if covO[:, a].all() or covO[:, b].all(): continue
            ta = Z[T][cov & ~covO[:, b], a]; tb = Z[T][cov & ~covO[:, a], b]
            ma = (nmin[a] - ta.max()) / SPZ[a] if ta.size else np.inf; mb = (nmin[b] - tb.max()) / SPZ[b] if tb.size else np.inf
            if fn == 0:
                cand_or.append((min(ma, mb), 0, ka, kb, nmin[a] * ka[1], nmin[b] * kb[1], ma, mb, ''))
            else:
                w = [lab(t) for (t, _), m in zip([x for x, yy in zip(sub, y) if yy], ~cov) if m]
                cand_or.append((-1, 1, ka, kb, nmin[a] * ka[1], nmin[b] * kb[1], ma, mb, w[0]))
op = lambda s: '<=' if s > 0 else '>='
opo = lambda s: '<' if s > 0 else '>'
for nm, C, o in (('AND', cand_and, op), ('OR', cand_or, opo)):
    z0 = sorted([c for c in C if c[1] == 0], key=lambda c: -c[0]); z1 = [c for c in C if c[1] == 1]
    print(f'\n== {nm} pairs: {len(z0)} zero-error, {len(z1)} one-error')
    for c in z0[:40]:
        print(f'  m={c[0]:.3f}  {c[2][0]} {o(c[2][1])} {c[4]:.4g}  {nm}  {c[3][0]} {o(c[3][1])} {c[5]:.4g}   (m_a {c[6]:.3f}, m_b {c[7]:.3f})')
pickle.dump(dict(keys=keys, X=X, y=y, sub=sub, single=res['single'], single1=res['single1'], AND=cand_and, OR=cand_or),
            open(os.path.join(HERE, f'psearch_{SUBK}.pkl'), 'wb'))
