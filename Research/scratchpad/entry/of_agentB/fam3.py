"""F1b loose absorption; F3 LVN / HVN on the composite profile (5 previous sessions)."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L
TFS = sys.argv[1:] or ['M15', 'M5']
for tf in TFS:
    x = L.ctx(tf); a = x['atr']; H, Lo, C, O = x['H'], x['L'], x['C'], x['O']; cl = L.clv(x); n = x['n']
    gap = {'M15': 4, 'M5': 12, 'H1': 2, 'M1': 60}[tf]
    # ---- F1b loose absorption ----
    for lev in ('p', 'd'):
        vah = x[lev + 'vah']; val = x[lev + 'val']; poc = x[lev + 'poc']
        ok = L.base_ok(x, 0 if lev == 'p' else 180) & ~np.isnan(vah) & (x['rvol_t'] >= 1.2)
        cL = ok & (Lo <= val) & (C > val) & (cl > 0) & (poc > C + 0.3 * a)
        cS = ok & (H >= vah) & (C < vah) & (cl < 0) & (poc < C - 0.3 * a)
        i, d = L.pack(cL, cS, gap)
        L.variants(tf, i, d, 'F1b absorbL %sVA' % lev, 'F1 absorption', struct=np.where(d == 1, Lo[i], H[i]))
    # ---- F3 candidates ----
    ok = L.base_ok(x, 0)
    N = 12
    import pandas as pd
    hh = pd.Series(H).rolling(N).max().shift(1).to_numpy(); ll = pd.Series(Lo).rolling(N).min().shift(1).to_numpy()
    # (a) breakout of the N-bar range, path ahead (C -> C +- 2 ATR) LVN vs HVN on the composite profile
    bL = ok & (C > hh); bS = ok & (C < ll)
    i, d = L.pack(bL, bS, gap)
    _, mn, mx, mean = L.comp_rvp(tf, i, C[i], C[i] + d * 2.0 * a[i])
    print(tf, 'breakouts', len(i), 'path mean rvp quantiles', np.nanpercentile(mean, [10, 25, 50, 75, 90]).round(2))
    for lab, m in (('LVN ahead', mean < 0.5), ('HVN ahead', mean > 1.2), ('all', np.ones(len(i), bool))):
        st = np.where(d == 1, Lo[i], H[i])
        L.variants(tf, i[m], d[m], 'F3 brk%d %s' % (N, lab), 'F3 LVN/HVN', struct=st[m])
    # (b) LVN rejection: probe into thin volume (extreme bin rvp < 0.4), close back in thick volume (rvp >= 1.0), rejection close
    pS = ok & (H >= hh) & (cl < -0.2); pL = ok & (Lo <= ll) & (cl > 0.2)
    i, d = L.pack(pL, pS, gap)
    ext = np.where(d == 1, Lo[i], H[i])
    r_ext, *_ = L.comp_rvp(tf, i, ext); r_c, *_ = L.comp_rvp(tf, i, C[i])
    m = (r_ext < 0.4) & (r_c >= 1.0)
    L.variants(tf, i[m], d[m], 'F3 LVN reject', 'F3 LVN/HVN', struct=ext[m])
    # (c) HVN support/resistance: after a 6-bar move of >= 1 ATR into the bar, its extreme sits in an HVN (rvp >= 1.5), rejection close
    mv = C - np.r_[np.full(6, np.nan), C[:-6]]
    hL = ok & (mv < -1.0 * a) & (cl > 0.3); hS = ok & (mv > 1.0 * a) & (cl < -0.3)
    i, d = L.pack(hL, hS, gap)
    ext = np.where(d == 1, Lo[i], H[i]); r_ext, *_ = L.comp_rvp(tf, i, ext)
    m = r_ext >= 1.5
    L.variants(tf, i[m], d[m], 'F3 HVN hold', 'F3 LVN/HVN', struct=ext[m])
    L.variants(tf, i[~m], d[~m], 'F3 nonHVN hold (ctrl)', 'F3 LVN/HVN', struct=ext[~m])
