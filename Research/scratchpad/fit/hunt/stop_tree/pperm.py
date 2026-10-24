"""Chance baseline on the subset: dedupe features by rank pattern, then count zero-error AND/OR pairs and best margins for
real labels vs random 8-of-n labelings.  Usage: pperm.py SUBK NPERM"""
import os, sys, pickle, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SUBK = sys.argv[1]; NP = int(sys.argv[2])
r = pickle.load(open(os.path.join(HERE, f'psearch_{SUBK}.pkl'), 'rb'))
X, y, keys = r['X'], r['y'], r['keys']
n, F = X.shape
# dedupe by rank pattern
pat = {}
for j in range(F):
    rk = tuple(np.searchsorted(np.unique(X[:, j]), X[:, j]))
    pat.setdefault(rk, []).append(j)
cols = [v[0] for v in pat.values()]
Xd = X[:, cols]; sp = np.percentile(Xd, 90, 0) - np.percentile(Xd, 10, 0); sp = np.where(sp > 0, sp, 1)
print(f'{F} features -> {len(cols)} distinct rank patterns')
def stats(y):
    T, N = y, ~y
    Z = np.concatenate([Xd, -Xd], 1); S = np.concatenate([sp, sp]); m = Z.shape[1]
    tmax = Z[T].max(0); inA = Z[N] <= tmax; nmin = Z[N].min(0); cov = Z[T] < nmin
    single = int((inA.sum(0) == 0).sum())
    # AND: fp = normals passing both
    fpAND = inA.T.astype(int) @ inA.astype(int)
    nA = int(((fpAND == 0).sum() - (np.diag(fpAND) == 0).sum()) // 2)
    covOR = cov.T.astype(int) @ cov.astype(int)   # tights covered by both
    cs = cov.sum(0)
    union = cs[:, None] + cs[None, :] - covOR
    nO = int(((union == T.sum()).sum() - (np.diag(union) == T.sum()).sum()) // 2)
    # best AND margin (approx: min of both one-sided gaps)
    best = 0.0
    idx = np.argwhere(np.triu(fpAND == 0, 1))
    for a, b in idx[:20000]:
        za = Z[N][inA[:, b], a]; zb = Z[N][inA[:, a], b]
        if za.size == 0 or zb.size == 0: continue
        mm = min((za.min() - tmax[a]) / S[a], (zb.min() - tmax[b]) / S[b]); best = max(best, mm)
    return single, nA, nO, best
print('REAL', stats(y))
rng = np.random.default_rng(1)
out = []
for p in range(NP):
    yy = np.zeros(n, bool); yy[rng.choice(n, int(y.sum()), replace=False)] = True
    s = stats(yy); out.append(s); print('perm', p, s)
o = np.array(out)
print('perm mean singles %.2f ANDpairs %.1f ORpairs %.1f bestANDmargin %.3f ; frac perms with >=1 zero-err AND: %.2f' % (o[:, 0].mean(), o[:, 1].mean(), o[:, 2].mean(), o[:, 3].mean(), (o[:, 1] > 0).mean()))
