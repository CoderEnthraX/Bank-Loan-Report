"""Directional predictability per feature: for each quintile (cuts on train) the long edge, the short edge and D = (long - short) / 2
(avg pts over TP1-TP4). Features are signed for the long side. Train and valid side by side; test untouched."""
import sys, pickle, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import ev
def edge(m):
    m = m[~np.isnan(m)]
    if len(m) == 0: return np.nan
    return np.mean([(np.mean(m >= r - 1e-9) - b) * 100 for r, b in zip(ev.TPR, ev.BASE)])
SK = {'i', 'split', 'mfeL', 'mfeS', 'cost', 'year', 'month'}
for tf in sys.argv[1:]:
    f = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb'))
    tr = f[f.split == 'train']; va = f[f.split == 'valid']
    print('== %s bars train %d valid %d | all: long %+.2f short %+.2f (train)  long %+.2f short %+.2f (valid)' % (
        tf, len(tr), len(va), edge(tr.mfeL.values), edge(tr.mfeS.values), edge(va.mfeL.values), edge(va.mfeS.values)))
    rows = []
    for col in f.columns:
        if col in SK: continue
        x = tr[col].dropna()
        if x.nunique() < 2: continue
        edges = (np.sort(x.unique())[1:] - 1e-9) if x.nunique() <= 24 else np.unique(np.quantile(x, [0.2, 0.4, 0.6, 0.8]))
        Dt = []; Dv = []
        for part, out in ((tr, Dt), (va, Dv)):
            q = np.digitize(part[col].to_numpy(), edges)
            for k in range(len(edges) + 1):
                m = q == k
                out.append(((edge(part.mfeL.values[m]) - edge(part.mfeS.values[m])) / 2, m.sum()))
        dt = np.array([a for a, n in Dt]); dv = np.array([a for a, n in Dv])
        okk = ~np.isnan(dt) & ~np.isnan(dv)
        rho = np.corrcoef(dt[okk], dv[okk])[0, 1] if okk.sum() >= 3 else np.nan
        spread_t = np.nanmax(dt) - np.nanmin(dt); spread_v = np.nanmax(dv) - np.nanmin(dv)
        rows.append((rho * min(spread_t, spread_v), col, rho, dt, dv, edges))
    rows.sort(key=lambda r: -np.nan_to_num(r[0]))
    for sc, col, rho, dt, dv, edges in rows[:14]:
        lab = ' '.join('%.3g' % e for e in edges) if len(edges) <= 6 else '%d buckets' % (len(edges) + 1)
        print('  %-15s rho %+.2f | D train %s | D valid %s | cuts %s' % (col, rho, ' '.join('%+5.1f' % v for v in dt), ' '.join('%+5.1f' % v for v in dv), lab))
