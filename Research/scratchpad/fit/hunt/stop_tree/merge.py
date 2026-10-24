"""Merge my bank (feat.pkl) with the sibling banks (stop_volatility/merged.pkl -> V_, stop_levels/feat2.pkl -> L_) into
bank.pkl = dict(names, X (80xF numpy), y, trades, src). Drops features that induce the same set of splits as an earlier one
(monotone / anti-monotone transforms), constant features, and non-numeric ones."""
import os, pickle, sys, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); HUNT = os.path.dirname(HERE)
mine = pickle.load(open(os.path.join(HERE, 'feat.pkl'), 'rb'))
key = lambda t: (t['sym'], t['fill'])
banks = [('', {key(t): f for t, f in mine})]
for pre, path in (('V_', 'stop_volatility/merged.pkl'), ('L_', 'stop_levels/feat2.pkl')):
    try:
        banks.append((pre, {key(t): f for t, f in pickle.load(open(os.path.join(HUNT, path), 'rb'))}))
    except Exception as e:
        print('skip', path, e)
trades = [t for t, _ in mine]
names = []; cols = []; src = []
for pre, B in banks:
    ks = list(B[key(trades[0])].keys())
    for k in ks:
        try:
            col = [float(B[key(t)][k]) for t in trades]
        except Exception:
            continue
        names.append(pre + k); cols.append(col); src.append(pre or 'mine')
X = np.array(cols, dtype=float).T
y = np.array([t['tight'] for t in trades], dtype=bool)
# NaN -> sentinel below the minimum
for j in range(X.shape[1]):
    c = X[:, j]; m = np.isnan(c)
    if m.any(): c[m] = (np.nanmin(c) if (~m).any() else 0) - 1e6
keep = []; seen = set()
for j in range(X.shape[1]):
    c = X[:, j]
    if np.all(c == c[0]): continue
    # split signature: rank with ties
    u, inv = np.unique(c, return_inverse=True)
    sig = tuple(inv); rsig = tuple(len(u) - 1 - inv)
    if sig in seen or rsig in seen: continue
    seen.add(sig); keep.append(j)
names = [names[j] for j in keep]; X = X[:, keep]; src = [src[j] for j in keep]
pickle.dump(dict(names=names, X=X, y=y, trades=trades, src=src), open(os.path.join(HERE, 'bank.pkl'), 'wb'))
import collections
print('features kept', len(names), collections.Counter(src))
