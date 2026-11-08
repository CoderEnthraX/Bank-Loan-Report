"""Univariate screen: per timeframe and feature, quintiles fixed on TRAIN; average edge (pts over TP1-TP4) per quintile on train and on
valid; a feature is interesting when the same quintile pattern shows in both. Test data are not touched."""
import sys, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import ev
SKIP = {'i', 'utc', 'split', 'entry', 'stop', 'fill_bar', 'fill_m1', 'mfe_c', 'stop_c', 'exit_c', 'mfe_m', 'stop_m', 'exit_m', 't1_m',
        'filled', 'engine', 'cost_fill', 'year', 'month'}
def edge_by(df, col, edges):
    q = np.digitize(df[col].to_numpy(), edges)
    out = []
    for k in range(len(edges) + 1):
        sub = df[q == k]; s = ev.stats(sub, cost=None)
        out.append((s['avg_edge'], s['n']))
    return out
rows = []
for tf in sys.argv[1:]:
    df = ev.load(tf); tr = df[df.split == 'train']; va = df[df.split == 'valid']
    print('== %s  train %s' % (tf, ev.line('all', tr))); print('== %s  valid %s' % (tf, ev.line('all', va)))
    for col in df.columns:
        if col in SKIP: continue
        x = tr[col].dropna()
        if x.nunique() < 2: continue
        if x.nunique() <= 8:
            edges = np.sort(x.unique())[1:] - 1e-9
        else:
            edges = np.unique(np.quantile(x, [0.2, 0.4, 0.6, 0.8]))
        a = edge_by(tr, col, edges); b = edge_by(va, col, edges)
        ea = np.array([v for v, n in a]); eb = np.array([v for v, n in b]); na = np.array([n for v, n in a]); nb = np.array([n for v, n in b])
        okk = (na >= 30) & (nb >= 30)
        if okk.sum() < 2: continue
        rho = np.corrcoef(ea[okk], eb[okk])[0, 1] if okk.sum() >= 3 else np.nan
        best = np.nanargmax(np.where(okk, ea, -np.inf))
        rows.append((tf, col, ea[best], eb[best], rho, na[best], nb[best], ea, eb, edges))
rows.sort(key=lambda r: -min(r[2], r[3]))
print('\nfeature (tf): best train quintile edge -> same quintile in valid | rho(train, valid) over quintiles | quintile edges train / valid')
for tf, col, a, b, rho, na, nb, ea, eb, edges in rows[:60]:
    print('%-4s %-16s %+5.2f -> %+5.2f  rho %+.2f  n %5d/%5d | %s | %s | cuts %s' % (tf, col, a, b, rho, na, nb, ' '.join('%+5.1f' % v for v in ea),
          ' '.join('%+5.1f' % v for v in eb), ' '.join('%.3g' % e for e in edges)))
