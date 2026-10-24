"""Exhaustive rule search on bank.pkl: tight (8) vs normal (72).
(a) single thresholds + single-feature intervals, (b) all 2-feature AND / OR threshold rules (exact for <= MAXERR errors via
atom pruning), (c) depth-2 trees (root split x best split in each child).  Margin of a cut = gap between the nearest
trades on either side of the threshold / feature spread (P90-P10 over the 80 trades).  Usage: search.py [perm_seed]"""
import os, sys, pickle, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
B = pickle.load(open(os.path.join(HERE, sys.argv[2] if len(sys.argv) > 2 else 'bank.pkl'), 'rb'))
names, X, y0, trades = B['names'], B['X'], B['y'], B['trades']
n, F = X.shape
seed = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] != '-' else None
y = y0.copy()
if seed is not None:
    rng = np.random.default_rng(seed); y = np.zeros(n, bool); y[rng.choice(n, int(y0.sum()), replace=False)] = True
ORD = np.argsort(X, axis=0, kind='stable'); XS = np.take_along_axis(X, ORD, 0)
VALID = np.ones((n + 1, F), bool); VALID[1:n] = XS[1:] > XS[:-1]
p90, p10 = np.percentile(X, 90, axis=0), np.percentile(X, 10, axis=0)
SPREAD = p90 - p10; sd = X.std(axis=0); SPREAD = np.where(SPREAD > 0, SPREAD, np.where(sd > 0, sd, 1.0))
lab = lambda t: f"{t['sym']} {t['fill']} {'L' if t['d'] > 0 else 'S'}"


def cut_value(j, k):
    return (XS[k - 1, j] + XS[k, j]) / 2 if 0 < k < n else (-np.inf if k == 0 else np.inf)


def gaps(mask):
    """subset gap at every cut k (F columns): next masked value at/after k minus previous masked value before k, / spread"""
    MS = mask[ORD]
    idx = np.where(MS, np.arange(n)[:, None], -1); prev = np.maximum.accumulate(idx, axis=0)          # last masked index <= r
    idx2 = np.where(MS, np.arange(n)[:, None], n); nxt = np.minimum.accumulate(idx2[::-1], axis=0)[::-1]  # first masked >= r
    G = np.full((n + 1, F), np.inf)
    pv = prev[:-1]; nx = nxt[1:]                       # for cut k (1..n-1): prev masked <= k-1, next masked >= k
    ok = (pv >= 0) & (nx < n)
    cols = np.arange(F)[None, :]
    lo = XS[np.clip(pv, 0, n - 1), cols]; hi = XS[np.clip(nx, 0, n - 1), cols]
    G[1:n] = np.where(ok, (hi - lo) / SPREAD, np.inf)
    return G


def best_split(mask, yy=None):
    """best single split restricted to subset mask. returns (err, margin, j, k, dir) ; dir +1 = tight if x > cut"""
    yy = y if yy is None else yy
    YS = (yy & mask)[ORD]; NS = (~yy & mask)[ORD]
    tc = np.vstack([np.zeros((1, F)), np.cumsum(YS, 0)]); nc = np.vstack([np.zeros((1, F)), np.cumsum(NS, 0)])
    Tt, Nt = tc[-1], nc[-1]
    ehi = tc + (Nt - nc); elo = (Tt - tc) + nc
    G = gaps(mask); Gc = np.minimum(G, 9.99)
    best = None
    for e, dr in ((ehi, 1), (elo, -1)):
        e = np.where(VALID, e, np.inf)
        key = e * 100 - Gc
        r = np.unravel_index(np.argmin(key), key.shape)
        cand = (e[r], G[r], r[1], r[0], dr)
        if best is None or cand[0] * 100 - min(cand[1], 9.99) < best[0] * 100 - min(best[1], 9.99): best = cand
    return best


def atom_mask(j, k, dr):
    m = np.zeros(n, bool)
    if dr > 0: m[ORD[k:, j]] = True
    else: m[ORD[:k, j]] = True
    return m


def describe(j, k, dr):
    return f"{names[j]} {'>' if dr > 0 else '<'} {cut_value(j, k):.4g}"


def wrong(pred):
    return [('FN ' if y[q] else 'FP ') + lab(trades[q]) for q in range(n) if pred[q] != y[q]]


out = []
P = lambda *a: out.append(' '.join(str(x) for x in a))
ALL = np.ones(n, bool); GALL = gaps(ALL)
# ---------------- (a) singles
YS = y[ORD]; tc = np.vstack([np.zeros((1, F)), np.cumsum(YS, 0)]); nc = np.vstack([np.zeros((1, F)), np.cumsum(~YS, 0)])
Tt, Nt = y.sum(), (~y).sum()
ehi = np.where(VALID, tc + (Nt - nc), np.inf); elo = np.where(VALID, (Tt - tc) + nc, np.inf)
singles = []
for j in range(F):
    for e, dr in ((ehi, 1), (elo, -1)):
        k = int(np.argmin(e[:, j] * 100 - np.minimum(GALL[:, j], 9.99)))
        singles.append((e[k, j], -GALL[k, j], j, k, dr))
singles.sort()
P('== (a) SINGLE THRESHOLDS: best 15 (err, margin)')
for e, g, j, k, dr in singles[:15]:
    P(f'  err {int(e)} margin {-g:.3f}  {describe(j, k, dr)}  wrong={wrong(atom_mask(j, k, dr))}')
# intervals: tight iff lo < x <= hi (cuts k1 < k2) -> err = FN outside + FP inside
ints = []
for j in range(F):
    t_ = tc[:, j]; n_ = nc[:, j]; vk = np.where(VALID[:, j])[0]
    for a_ in vk:
        for b_ in vk[vk > a_]:
            e = (Tt - (t_[b_] - t_[a_])) + (n_[b_] - n_[a_])
            if e <= 4: ints.append((e, -min(GALL[a_, j], GALL[b_, j]), j, a_, b_))
ints.sort()
P('== (a2) SINGLE-FEATURE INTERVALS (tight iff lo < x < hi): best 15')
for e, g, j, a_, b_ in ints[:15]:
    m = np.zeros(n, bool); m[ORD[a_:b_, j]] = True
    P(f'  err {int(e)} margin {-g:.3f}  {cut_value(j, a_):.4g} < {names[j]} < {cut_value(j, b_):.4g}  wrong={wrong(m)}')
# ---------------- (b) pairs via pruned atoms
MAXERR = 2
andA = []; orA = []
for j in range(F):
    for dr in (1, -1):
        # AND atoms: most restrictive cut covering all but the r most extreme tight (r = 0..MAXERR)
        e_col = None
        col = YS[:, j] if dr > 0 else YS[::-1, j]
        pos = np.where(col)[0]
        for r_ in range(MAXERR + 1):
            p = pos[r_]
            k = p if dr > 0 else n - p
            # move to a valid cut at or before p (dr>0) such that the tight at p stays included
            if dr > 0:
                while k > 0 and not VALID[k, j]: k -= 1
            else:
                while k < n and not VALID[k, j]: k += 1
            andA.append((j, k, dr))
        colN = (~YS[:, j]) if dr > 0 else (~YS[::-1, j])
        posN = np.where(colN)[0]
        for r_ in range(MAXERR + 1):
            p = posN[-(r_ + 1)]  # (r_+1)-th most extreme normal on the predicted side
            k = p + 1 if dr > 0 else n - p - 1
            if dr > 0:
                while k < n and not VALID[k, j]: k += 1
            else:
                while k > 0 and not VALID[k, j]: k -= 1
            orA.append((j, k, dr))
andA = sorted(set(andA)); orA = sorted(set(orA))
def mats(atoms):
    M = np.array([atom_mask(*a) for a in atoms]); g = np.array([GALL[k, j] for j, k, dr in atoms])
    return M, g
res = {}
for nm, atoms, op in (('AND', andA, 'and'), ('OR', orA, 'or')):
    M, g = mats(atoms); Mt = M[:, y].astype(np.int32); Mn = M[:, ~y].astype(np.int32)
    It = Mt @ Mt.T; In = Mn @ Mn.T
    st = Mt.sum(1); sn = Mn.sum(1)
    if op == 'and': TP = It; FP = In
    else: TP = st[:, None] + st[None, :] - It; FP = sn[:, None] + sn[None, :] - In
    E = (Tt - TP) + FP
    jj = np.array([a[0] for a in atoms]); same = jj[:, None] == jj[None, :]
    E = np.where(same, 999, E); iu = np.triu_indices(len(atoms), 1)
    ev = E[iu]; sel = np.where(ev <= MAXERR)[0]
    L_ = []
    for s in sel:
        a, b = iu[0][s], iu[1][s]; L_.append((int(ev[s]), -min(g[a], g[b]), a, b))
    L_.sort(); res[nm] = (L_, atoms, M)
    cnt = [sum(1 for x in L_ if x[0] == e) for e in range(MAXERR + 1)]
    P(f'== (b) 2-FEATURE {nm} rules: count by errors 0/1/2 = {cnt}; top 25 by (err, margin)')
    for e, g_, a, b in L_[:25]:
        pred = (M[a] & M[b]) if op == 'and' else (M[a] | M[b])
        P(f'  err {e} margin {-g_:.3f}  {describe(*atoms[a])}  {nm}  {describe(*atoms[b])}  wrong={wrong(pred)}')
# ---------------- (c) depth-2 trees
seen = {}; trees = []
for j in range(F):
    for k in range(1, n):
        if not VALID[k, j]: continue
        m = np.zeros(n, bool); m[ORD[k:, j]] = True
        kb = m.tobytes()
        if kb in seen: continue
        seen[kb] = 1
        bl = best_split(~m); br = best_split(m)
        e = bl[0] + br[0]
        mg = min(GALL[k, j], bl[1] if bl[3] not in (0, n) else np.inf, br[1] if br[3] not in (0, n) else np.inf)
        trees.append((e, -mg, j, k, bl, br))
trees.sort(key=lambda t: (t[0], t[1]))
cnt = [sum(1 for t in trees if t[0] == e) for e in range(4)]
P(f'== (c) DEPTH-2 TREES: {len(trees)} root partitions; count by errors 0/1/2/3 = {cnt}; top 25')
def cdesc(b):
    e, g, j, k, dr = b
    if k == 0: return 'ALL TIGHT' if dr > 0 else 'ALL NORMAL'
    if k == n: return 'ALL NORMAL' if dr > 0 else 'ALL TIGHT'
    return f'[{describe(j, k, dr)} -> tight] (m {g:.3f})'
def tpred(t):
    e, g, j, k, bl, br = t
    m = np.zeros(n, bool); m[ORD[k:, j]] = True
    pl = atom_mask(bl[2], bl[3], bl[4]); pr = atom_mask(br[2], br[3], br[4])
    return np.where(m, pr, pl)
for t in trees[:25]:
    e, g, j, k, bl, br = t
    P(f'  err {int(e)} margin {-g:.3f}  ROOT {names[j]} > {cut_value(j, k):.4g}:  no: {cdesc(bl)}  yes: {cdesc(br)}  wrong={wrong(tpred(t))}')
best = dict(single=singles[0][0], interval=ints[0][0] if ints else 99, interval_m=round(max([-x[1] for x in ints if x[0]==ints[0][0]]),3) if ints else None, AND=res['AND'][0][0][0] if res['AND'][0] else 99,
            OR=res['OR'][0][0][0] if res['OR'][0] else 99, tree=trees[0][0])
# best margins among zero/one-error rules
def bm(L_, e0):
    v = [-x[1] for x in L_ if x[0] <= e0]; return max(v) if v else None
mg = dict(AND0=bm(res['AND'][0], 0), AND1=bm(res['AND'][0], 1), OR0=bm(res['OR'][0], 0), OR1=bm(res['OR'][0], 1),
          tree0=max([-t[1] for t in trees if t[0] == 0], default=None), tree1=max([-t[1] for t in trees if t[0] <= 1], default=None))
P('SUMMARY seed', seed, 'best errors', best, 'best margins', {k: (round(v, 3) if v is not None else None) for k, v in mg.items()})
print('\n'.join(out) if seed is None else out[-1])
if seed is None: pickle.dump(dict(singles=singles[:200], ints=ints[:200], AND=res['AND'][0][:500], ORr=res['OR'][0][:500], andA=andA, orA=orA, trees=trees[:500]), open(os.path.join(HERE, 'search_res.pkl'), 'wb'))
