"""Re-rank AND/OR pair rules with CONDITIONAL margins: margin of atom b measured only on trades where atom a holds (AND)
or fails (OR), and vice versa; gap/(P90-P10).  Penalised score = errors + 1.0*(margin<0.05) + 0.5*(margin<0.10).
Usage: post.py bank.pkl search_res.pkl"""
import sys, os, pickle
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
B = pickle.load(open(os.path.join(HERE, sys.argv[1]), 'rb')); R = pickle.load(open(os.path.join(HERE, sys.argv[2]), 'rb'))
names, X, y, trades = B['names'], B['X'], B['y'], B['trades']; n, F = X.shape
ORD = np.argsort(X, axis=0, kind='stable'); XS = np.take_along_axis(X, ORD, 0)
SP = np.percentile(X, 90, 0) - np.percentile(X, 10, 0); sd = X.std(0); SP = np.where(SP > 0, SP, np.where(sd > 0, sd, 1.0))
def cut(j, k): return (XS[k - 1, j] + XS[k, j]) / 2 if 0 < k < n else (-np.inf if k == 0 else np.inf)
def amask(j, k, dr):
    m = np.zeros(n, bool)
    if dr > 0: m[ORD[k:, j]] = True
    else: m[ORD[:k, j]] = True
    return m
def cond_gap(j, k, dr, sub):
    """widest gap around cut k of feature j among trades in sub, keeping the same partition of sub; returns (gap/spread, lo, hi)"""
    v = X[sub, j]; c = cut(j, k)
    below = v[v < c]; above = v[v > c]
    if len(below) == 0 or len(above) == 0: return np.inf, None, None
    return (above.min() - below.max()) / SP[j], below.max(), above.min()
lab = lambda q: f"{trades[q]['sym']} {trades[q]['fill']} {'L' if trades[q]['d'] > 0 else 'S'}"
rows = []
for nm, key, atoms in (('AND', 'AND', R['andA']), ('OR', 'ORr', R['orA'])):
    for e, g, a, b in R[key]:
        A_, B_ = atoms[a], atoms[b]; ma, mb = amask(*A_), amask(*B_)
        if nm == 'AND': sa, sb = mb, ma; pred = ma & mb
        else: sa, sb = ~mb, ~ma; pred = ma | mb
        ga = cond_gap(*A_, sa); gb = cond_gap(*B_, sb); m = min(ga[0], gb[0])
        ps = e + 1.0 * (m < 0.05) + 0.5 * (m < 0.10)
        desc = f"{names[A_[0]]} {'>' if A_[2] > 0 else '<'} {cut(A_[0], A_[1]):.4g} [gap {ga[1]}..{ga[2]}]  {nm}  {names[B_[0]]} {'>' if B_[2] > 0 else '<'} {cut(B_[0], B_[1]):.4g} [gap {gb[1]}..{gb[2]}]"
        rows.append((ps, e, -m, desc, [('FN ' if y[q] else 'FP ') + lab(q) for q in range(n) if pred[q] != y[q]]))
rows.sort(key=lambda r: (r[0], r[1], r[2]))
for r in rows[:40]:
    print(f'pscore {r[0]:.1f} err {r[1]} condMargin {-r[2]:.3f}  {r[3]}  wrong={r[4]}')
