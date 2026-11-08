"""C3: fade the indicator's signal when it points away from the developing POC and price is already far from it."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, signals
GAP = {'M15': 4, 'M5': 12, 'H1': 2, 'M1': 60}

def c3_sig(tf, pct=80, min_sess=180, gap=0, ref='dpoc', near=False, src='sig', body=0.8):
    x = L.ctx(tf); a = x['atr']; C = x['C']; ok = L.base_ok(x, min_sess)
    r = x[ref] if ref != 'vwap' else x['V']
    dist = (C - r) / a
    k = np.percentile(np.abs(dist[ok & (x['split'] == 'train') & ~np.isnan(dist)]), pct)
    if src == 'sig':
        s = signals.raw(tf); i = s['i'].astype(np.int64); d = s['d'].astype(np.int64); keep = ~s['both']
        i, d = i[keep], d[keep]
    else:   # generic impulse bar: body >= body*ATR, close in the outer 25% of the range
        rng = x['H'] - x['L']; bd = x['C'] - x['O']; cl = L.clv(x)
        up = (bd >= body * a) & (cl >= 0.5); dn = (-bd >= body * a) & (cl <= -0.5)
        i = np.flatnonzero(up | dn); d = np.where(up[i], 1, -1)
    m = ok[i] & ~np.isnan(dist[i]) & (np.sign(dist[i]) == d)
    m &= (np.abs(dist[i]) < k) if near else (np.abs(dist[i]) >= k)
    i, d = i[m], -d[m]                         # opposite trade
    if gap: i, d = L.declust(i, d, gap)
    return x, i, d, k

def go(tf, x, i, d, name, kind='mkt', k_atr=1.8):
    e, st, mode = L.orders(x, i, d, kind, 'atr', k_atr=k_atr)
    return L.run(tf, i, d, e, st, mode=mode, window=3, name=name, family='C3')

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        g = GAP[tf]
        x, i, d, k = c3_sig(tf, 80, gap=g); go(tf, x, i, d, 'C3 p80 declust%d mkt' % g)
        for pct in (70, 90, 95):
            x, i, d, k = c3_sig(tf, pct, gap=g); go(tf, x, i, d, 'C3 p%d(k%.1f) declust mkt' % (pct, k))
        x, i, d, k = c3_sig(tf, 80, gap=g)
        for ka in (1.2, 2.5): go(tf, x, i, d, 'C3 p80 declust mkt atr%.1f' % ka, k_atr=ka)
        x, i, d, k = c3_sig(tf, 80, gap=g, min_sess=0); go(tf, x, i, d, 'C3 p80 declust minsess0 mkt')
        x, i, d, k = c3_sig(tf, 80, gap=g, near=True); go(tf, x, i, d, 'C3ctrl NEAR POC (<p80) OPP mkt')
        x, i, d, k = c3_sig(tf, 80, gap=g, ref='vwap'); go(tf, x, i, d, 'C3 VWAP-dist p80 declust mkt')
        x, i, d, k = c3_sig(tf, 80, gap=g, ref='ppoc'); go(tf, x, i, d, 'C3 priorPOC-dist p80 declust mkt')
        for bd in (0.8, 1.2):
            x, i, d, k = c3_sig(tf, 80, gap=g, src='bar', body=bd); go(tf, x, i, d, 'C3gen impulse bar %.1fATR away p80 OPP mkt' % bd)
