"""Rule mining with day-clustered inference. Every bar x direction (market, stop 1.8 ATR). Score per bar = mean over TP1-TP4 of hit
minus the no-edge rate, minus the mean of random bars of the same direction in the same split (= excess, drift-neutral).
Conditions: one feature quintile (cuts from train), the NY hour, or a feature quintile x NY 3-hour block. Each day = one observation
(per-day mean of the cell's scores), t = mean / se across days. Rank on train t, report valid. Test untouched."""
import sys, pickle, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data
TPR = kit.TPR; B = kit.BASE.mean()
tf = sys.argv[1]; TOP = int(sys.argv[2]) if len(sys.argv) > 2 else 40
f = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb')); f = f[f.split != 'test'].reset_index(drop=True)
b = data.load(tf); ny = kit.local_min(tf, 'ny')[f.i.to_numpy()]
f['nyh'] = ny // 60; f['ny3'] = ny // 180
f['day'] = (b['utc'][f.i.to_numpy()] + 6 * 3600) // 86400          # trading day (shifted so the 18:00 NY reopen starts a day)
def score(m):
    return np.mean([(m >= r - 1e-9).astype(float) for r in TPR], axis=0) - B
sL = score(f.mfeL.to_numpy()); sS = score(f.mfeS.to_numpy())
for sp in ('train', 'valid'):
    m = (f.split == sp).to_numpy(); sL[m] -= np.nanmean(sL[m]); sS[m] -= np.nanmean(sS[m])
f['xL'] = sL * 100; f['xS'] = sS * 100
feats = [c for c in f.columns if c not in ('i', 'split', 'mfeL', 'mfeS', 'cost', 'year', 'month', 'ist_min', 'utc_hour', 'nyh', 'ny3', 'day', 'xL', 'xS')]
tr = f.split == 'train'
for c in feats:
    x = f.loc[tr, c].dropna()
    cuts = np.unique(np.quantile(x, [0.2, 0.4, 0.6, 0.8])) if x.nunique() > 8 else np.sort(x.unique())[1:] - 1e-9
    f['q_' + c] = np.where(f[c].isna(), -1, np.digitize(f[c].fillna(0).to_numpy(), cuts))
conds = [('nyh', None)] + [('q_' + c, None) for c in feats] + [('q_' + c, 'ny3') for c in feats]
def cell_stats(g, col):
    """per-bar mean (the tradable average) with a day-clustered standard error"""
    x = g[col].to_numpy(); n = len(x)
    if n < 3: return np.nan, np.nan, 0, n
    mu = x.mean(); r = pd.Series(x - mu).groupby(g['day'].to_numpy()).sum().to_numpy()
    return mu, np.sqrt((r ** 2).sum()) / n, len(r), n
rows = []
for a, bb in conds:
    keys = [a] + ([bb] if bb else [])
    for key, g in f[tr].groupby(keys):
        if not isinstance(key, tuple): key = (key,)
        if key[0] == -1: continue
        for side, col in (('long', 'xL'), ('short', 'xS')):
            mu, se, nd, nb = cell_stats(g, col)
            if nd < 150 or not np.isfinite(se) or se == 0: continue
            rows.append((mu / se, mu, nd, nb, keys, key, side, col))
rows.sort(key=lambda r: -r[0])
print('%s: %d cells x side tested on train; top %d by train t (day-clustered); valid = same cell in 2024-01..2025-06' % (tf, len(rows), TOP))
va = f[f.split == 'valid']
for t, mu, nd, nb, keys, key, side, col in rows[:TOP]:
    g = va
    for k_, v_ in zip(keys, key): g = g[g[k_] == v_]
    vm, vse, vnd, vnb = cell_stats(g, col) if len(g) > 10 else (np.nan, np.nan, 0, 0)
    lab = ' & '.join('%s=%s' % (k_, v_) for k_, v_ in zip(keys, key))
    print('%-42s %-5s train %+5.2f (t %4.1f, %4d days, %5.1f bars/day) | valid %+5.2f (t %4.1f, %4d days)' % (lab, side, mu, t, nd, nb / nd, vm, vm / vse if vse else np.nan, vnd))
