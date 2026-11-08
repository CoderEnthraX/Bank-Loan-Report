import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, signals
for tf in ('M5', 'M15'):
    x = L.ctx(tf); a = x['atr']; C = x['C']; ok = L.base_ok(x, 180)
    dist = (C - x['dpoc']) / a
    k = np.percentile(np.abs(dist[ok & (x['split'] == 'train') & ~np.isnan(dist)]), 80)
    s = signals.raw(tf); i = s['i'].astype(np.int64); d = s['d'].astype(np.int64)
    m0 = ok[i] & ~s['both'] & ~np.isnan(dist[i]) & (np.abs(dist[i]) >= k)
    tow = m0 & (np.sign(dist[i]) == -d); away = m0 & (np.sign(dist[i]) == d)
    print(tf, 'k', round(k, 1), 'toward', tow.sum(), 'away', away.sum())
    for lab, m, dd in (('C1xSIG toward POC', tow, d), ('C1xSIG away -> OPP', away, -d)):
        ii = i[m]; di = dd[m]
        if lab.startswith('C1xSIG toward'):
            L.run(tf, ii, di, s['entry'][m], s['stop_h'][m], mode=0, window=5, name=lab + ' lim own', family='F6 combo')
        for kind in ('mkt', 'stp'):
            e, st, mode = L.orders(x, ii, di, kind, 'atr')
            L.run(tf, ii, di, e, st, mode=mode, window=3, name=lab + ' %s atr' % kind, family='F6 combo')
