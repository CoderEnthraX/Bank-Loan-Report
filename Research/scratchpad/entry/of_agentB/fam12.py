"""F1 absorption at value-area edges; F2 failed auction at prior VA edges + 80% rule."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L
TFS = sys.argv[1:] or ['M15', 'M5']
for tf in TFS:
    x = L.ctx(tf); a = x['atr']; H, Lo, C, O = x['H'], x['L'], x['C'], x['O']; cl = L.clv(x)
    gap = {'M15': 4, 'M5': 12, 'H1': 2, 'M1': 60}[tf]
    rng = (H - Lo) / a
    # ---------- F1 absorption ----------
    for lev in ('p', 'd'):
        vah = x[lev + 'vah']; val = x[lev + 'val']; poc = x[lev + 'poc']
        ok = L.base_ok(x, 0 if lev == 'p' else 180) & ~np.isnan(vah)
        heavy = (x['rvol_t'] >= 1.5) & (rng <= 1.3)
        for dz in (0, 1):
            # long: low trades through VAL, close back above VAL, close in upper part, poc above
            cL = ok & heavy & (Lo <= val) & (C > val) & (cl > 0.2) & (poc > C + 0.5 * a)
            cS = ok & heavy & (H >= vah) & (C < vah) & (cl < -0.2) & (poc < C - 0.5 * a)
            if dz:   # delta shows the aggressor pushing INTO the level (absorbed)
                cL &= x['dtk'] < 0; cS &= x['dtk'] > 0
            i = np.r_[np.flatnonzero(cL), np.flatnonzero(cS)]; d = np.r_[np.ones(cL.sum(), int), -np.ones(cS.sum(), int)]
            o = np.argsort(i); i, d = L.declust(i[o], d[o], gap)
            st = np.where(d == 1, Lo[i], H[i])
            L.variants(tf, i, d, 'F1 absorb %sVA%s' % (lev, ' +opp.delta' if dz else ''), 'F1 absorption', struct=st)
    # ---------- F2 failed auction at prior VA edge ----------
    pvah, pval, ppoc = x['pvah'], x['pval'], x['ppoc']
    ok = L.base_ok(x, 0) & ~np.isnan(pvah)
    for conf in (0, 1):
        # probe beyond the edge (bar or previous 2 bars) and close back inside; conf=1: previous bar CLOSED outside (accepted, then failed)
        hi3 = np.maximum.reduce([H, np.r_[np.nan, H[:-1]], np.r_[np.nan, np.nan, H[:-2]]])
        lo3 = np.minimum.reduce([Lo, np.r_[np.nan, Lo[:-1]], np.r_[np.nan, np.nan, Lo[:-2]]])
        Cp = np.r_[np.nan, C[:-1]]
        cS = ok & (hi3 > pvah + 0.2 * a) & (C < pvah) & (ppoc < C - 0.5 * a)
        cL = ok & (lo3 < pval - 0.2 * a) & (C > pval) & (ppoc > C + 0.5 * a)
        if conf: cS &= Cp > pvah; cL &= Cp < pval
        i = np.r_[np.flatnonzero(cL), np.flatnonzero(cS)]; d = np.r_[np.ones(cL.sum(), int), -np.ones(cS.sum(), int)]
        o = np.argsort(i); i, d = L.declust(i[o], d[o], gap)
        st = np.where(d == 1, lo3[i], hi3[i])
        L.variants(tf, i, d, 'F2 failVA%s' % (' accepted' if conf else ''), 'F2 failed auction', struct=st)
    # ---------- F2b 80% rule ----------
    N = {'M15': 2, 'M5': 6, 'H1': 1, 'M1': 30}[tf]
    for anchor in ('sess', 'ny0930'):
        if anchor == 'sess':
            first = x['ds'].astype(bool)
        else:
            first = (x['ny_min'] == 570)
        # open of the anchor bar outside prior VA, remembered through the session
        sid = x['sid']; n = x['n']
        aopen = np.full(n, np.nan); aidx = np.full(n, -1)
        fi = np.flatnonzero(first)
        last_s = -1; cur = np.nan; ci = -1
        sidf = sid[fi]
        mark = np.zeros(n, int); mark[fi] = 1
        import pandas as pd
        s_open = pd.Series(np.where(first, O, np.nan)).groupby(sid).ffill().to_numpy()
        s_idx = pd.Series(np.where(first, np.arange(n), np.nan)).groupby(sid).ffill().to_numpy()
        after = ~np.isnan(s_idx)
        below = after & (s_open < pval); above = after & (s_open > pvah)
        inside = (C > pval) & (C < pvah)
        k = np.ones(n, bool)
        for q in range(N): k &= np.r_[np.zeros(q, bool), inside[:n - q]]
        ok2 = ok & after & k & ((pvah - pval) > 1.0 * a)
        cL = ok2 & below; cS = ok2 & above
        # first occurrence per session per direction
        def firstps(c):
            idx = np.flatnonzero(c); s = sid[idx]; keep = np.r_[True, s[1:] != s[:-1]]; return idx[keep]
        iL = firstps(cL); iS = firstps(cS)
        i = np.r_[iL, iS]; d = np.r_[np.ones(len(iL), int), -np.ones(len(iS), int)]; o = np.argsort(i); i, d = i[o], d[o]
        # structural stop: extreme of the last N+2 bars
        lo_n = np.array([Lo[max(j - N - 1, 0):j + 1].min() for j in i]); hi_n = np.array([H[max(j - N - 1, 0):j + 1].max() for j in i])
        st = np.where(d == 1, lo_n, hi_n)
        L.variants(tf, i, d, 'F2 80pct %s' % anchor, 'F2 80% rule', struct=st)
