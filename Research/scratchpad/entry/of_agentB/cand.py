"""Sensitivity of C1 (fade far from the developing POC) and C2 (CVD divergence at a new session extreme, stop entry)."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L
ext_idx = L.ext_idx
GAP = {'M15': 4, 'M5': 12, 'H1': 2, 'M1': 60}

def c1_sig(tf, pct=90, ref='dpoc', norm='atr', min_sess=180, gap=None, trig=0):
    x = L.ctx(tf); a = x['atr']; C = x['C']; ok = L.base_ok(x, min_sess)
    r = x[ref] if ref != 'vwap' else x['V']
    sc = a if norm == 'atr' else np.where(x['SD'] > 0, x['SD'], np.nan)
    dist = (C - r) / sc
    tr = ok & (x['split'] == 'train') & ~np.isnan(dist)
    k = np.percentile(np.abs(dist[tr]), pct)               # threshold from TRAIN only
    cL = ok & (dist <= -k); cS = ok & (dist >= k)
    if trig:
        cl = L.clv(x); cL &= (C > x['O']) & (cl > 0.3); cS &= (C < x['O']) & (cl < -0.3)
    i, d = L.pack(cL, cS, gap or GAP[tf]); return x, i, d, k

def c2_sig(tf, dk='cvd_cl', m=6, min_sess=180, gap=None):
    x = L.ctx(tf); H, Lo = x['H'], x['L']; n = x['n']; ok = L.base_ok(x, min_sess); cvd = x[dk]
    ih, il = ext_idx(H, Lo, x['sid'])
    nh = ok & (ih >= 0) & (H > x['shp']) & (np.arange(n) - ih >= m)
    nl = ok & (il >= 0) & (Lo < x['slp']) & (np.arange(n) - il >= m)
    cS = nh & (cvd < cvd[np.maximum(ih, 0)]); cL = nl & (cvd > cvd[np.maximum(il, 0)])
    i, d = L.pack(cL, cS, gap or GAP[tf]); return x, i, d

def go(tf, x, i, d, name, kind, stop, k_atr=1.8):
    e, st, mode = L.orders(x, i, d, kind, stop, struct=np.where(d == 1, x['L'][i], x['H'][i]), k_atr=k_atr)
    return L.run(tf, i, d, e, st, mode=mode, window=3, name=name, family='cand')

if __name__ == '__main__':
    what = sys.argv[1]; tfs = sys.argv[2:]
    for tf in tfs:
        if what == 'c1':
            for pct in (80, 85, 90, 95):
                x, i, d, k = c1_sig(tf, pct)
                go(tf, x, i, d, 'C1 dPOC p%d(k%.1f) mkt atr' % (pct, k), 'mkt', 'atr')
            x, i, d, k = c1_sig(tf, 90)
            for ka in (1.2, 2.5): go(tf, x, i, d, 'C1 dPOC p90 mkt atr%.1f' % ka, 'mkt', 'atr', ka)
            go(tf, x, i, d, 'C1 dPOC p90 stp atr', 'stp', 'atr')
            for ms in (0, 360):
                x, i, d, k = c1_sig(tf, 90, min_sess=ms); go(tf, x, i, d, 'C1 dPOC p90 minsess%d mkt atr' % ms, 'mkt', 'atr')
            for g in (GAP[tf] // 2, GAP[tf] * 2):
                x, i, d, k = c1_sig(tf, 90, gap=g); go(tf, x, i, d, 'C1 dPOC p90 gap%d mkt atr' % g, 'mkt', 'atr')
            x, i, d, k = c1_sig(tf, 90, norm='sd'); go(tf, x, i, d, 'C1 dPOC p90 /SD(k%.1f) mkt atr' % k, 'mkt', 'atr')
            x, i, d, k = c1_sig(tf, 90, ref='vwap'); go(tf, x, i, d, 'C1ctrl VWAP p90 mkt atr', 'mkt', 'atr')
            x, i, d, k = c1_sig(tf, 90, ref='ppoc'); go(tf, x, i, d, 'C1 pPOC p90 mkt atr', 'mkt', 'atr')
        else:
            for dk in ('cvd_cl', 'cvd_tk'):
                for m in (3, 6, 12):
                    x, i, d = c2_sig(tf, dk, m)
                    for stop in ('struct', 'atr'):
                        go(tf, x, i, d, 'C2 div %s m%d stp %s' % (dk[-2:], m, stop), 'stp', stop)
            x, i, d = c2_sig(tf, 'cvd_cl', 6, min_sess=0); go(tf, x, i, d, 'C2 div cl m6 minsess0 stp struct', 'stp', 'struct')
