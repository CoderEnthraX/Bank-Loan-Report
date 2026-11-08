"""F4 POC reversion / migration; F5 delta / CVD rules."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, pandas as pd, oflib as L
from numba import njit

@njit(cache=True)
def ext_idx(H, Lo, sid):
    """index of the bar that set the running session high / low BEFORE bar i (-1 at session start)"""
    n = len(H); ih = np.full(n, -1); il = np.full(n, -1); ch = -1; cl = -1
    for i in range(n):
        if i == 0 or sid[i] != sid[i - 1]: ch = -1; cl = -1
        ih[i] = ch; il[i] = cl
        if ch < 0 or H[i] > H[ch]: ch = i
        if cl < 0 or Lo[i] < Lo[cl]: cl = i
    return ih, il

TFS = sys.argv[1:] or ['M15', 'M5']
for tf in TFS:
    x = L.ctx(tf); a = x['atr']; H, Lo, C, O = x['H'], x['L'], x['C'], x['O']; cl = L.clv(x); n = x['n']
    gap = {'M15': 4, 'M5': 12, 'H1': 2, 'M1': 60}[tf]; hb = 120 // x['tfmin']   # bars in 2 hours
    ok = L.base_ok(x, 180)
    # ---------- F4a POC reversion ----------
    for lev in ('d', 'p'):
        poc = x[lev + 'poc']; dist = (C - poc) / a
        k = np.nanpercentile(np.abs(dist[ok]), 90)
        for trig in (0, 1):
            cL = ok & (dist <= -k); cS = ok & (dist >= k)
            if trig: cL &= (C > O) & (cl > 0.3); cS &= (C < O) & (cl < -0.3)
            i, d = L.pack(cL, cS, gap)
            L.variants(tf, i, d, 'F4 POCrev %sPOC k%.1f%s' % (lev, k, ' +revbar' if trig else ''), 'F4 POC', struct=np.where(d == 1, Lo[i], H[i]))
    # ---------- F4b POC migration trend + pullback to dev POC ----------
    poc = x['dpoc']; mig = (poc - np.r_[np.full(hb, np.nan), poc[:-hb]]) / a
    same = x['sid'] == np.r_[np.full(hb, -1), x['sid'][:-hb]]
    cL = ok & same & (mig >= 1.5) & (Lo <= poc + 0.2 * a) & (C > poc) & (cl > 0)
    cS = ok & same & (mig <= -1.5) & (H >= poc - 0.2 * a) & (C < poc) & (cl < 0)
    i, d = L.pack(cL, cS, gap)
    L.variants(tf, i, d, 'F4 POCmig pullback', 'F4 POC', struct=np.where(d == 1, Lo[i], H[i]))
    # POC migration alone as trend (market in the direction of migration), first per 2 h
    cL = ok & same & (mig >= 1.5); cS = ok & same & (mig <= -1.5)
    i, d = L.pack(cL, cS, hb)
    L.variants(tf, i, d, 'F4 POCmig trend', 'F4 POC', struct=np.where(d == 1, Lo[i], H[i]), stops=('atr',))
    # ---------- F5a CVD divergence at a new session high / low ----------
    ih, il = ext_idx(H, Lo, x['sid'])
    for dk in ('cvd_tk', 'cvd_cl'):
        cvd = x[dk]
        nh = ok & (ih >= 0) & (H > x['shp']) & (np.arange(n) - ih >= 6)
        nl = ok & (il >= 0) & (Lo < x['slp']) & (np.arange(n) - il >= 6)
        divS = nh & (cvd < cvd[np.maximum(ih, 0)]); divL = nl & (cvd > cvd[np.maximum(il, 0)])
        for rej in (0, 1):
            cS = divS & ((cl < 0) if rej else True); cL = divL & ((cl > 0) if rej else True)
            i, d = L.pack(cL, cS, gap)
            L.variants(tf, i, d, 'F5 CVDdiv %s%s' % (dk[-2:], ' +rej' if rej else ''), 'F5 delta/CVD', struct=np.where(d == 1, Lo[i], H[i]))
        if dk == 'cvd_tk':   # control: new extreme after pullback WITH CVD confirmation, faded the same way
            cS = nh & ~(cvd < cvd[np.maximum(ih, 0)]); cL = nl & ~(cvd > cvd[np.maximum(il, 0)])
            i, d = L.pack(cL, cS, gap)
            L.variants(tf, i, d, 'F5 CVDconfirm fade (ctrl)', 'F5 delta/CVD', struct=np.where(d == 1, Lo[i], H[i]))
            L.variants(tf, i, -d, 'F5 CVDconfirm follow', 'F5 delta/CVD', struct=np.where(-d == 1, Lo[i], H[i]))
    # ---------- F5b delta flip after a sweep of the session low/high ----------
    dt = x['dtk']
    nl = ok & (il >= 0) & (Lo < x['slp']) & (np.arange(n) - il >= 6) & (dt < 0)
    nh = ok & (ih >= 0) & (H > x['shp']) & (np.arange(n) - ih >= 6) & (dt > 0)
    cL = np.zeros(n, bool); cS = np.zeros(n, bool); sL = np.full(n, np.nan); sS = np.full(n, np.nan)
    for k in range(1, 4):
        kL = np.r_[np.zeros(k, bool), nl[:-k]]; kS = np.r_[np.zeros(k, bool), nh[:-k]]
        Hk = np.r_[np.full(k, np.nan), H[:-k]]; Lk = np.r_[np.full(k, np.nan), Lo[:-k]]
        fL = ok & kL & (dt > 0) & (C > Hk) & (Lo >= Lk - 1e-9); fS = ok & kS & (dt < 0) & (C < Lk) & (H <= Hk + 1e-9)
        sL = np.where(fL & ~cL, Lk, sL); sS = np.where(fS & ~cS, Hk, sS); cL |= fL; cS |= fS
    i, d = L.pack(cL, cS, gap)
    L.variants(tf, i, d, 'F5 deltaflip after sweep', 'F5 delta/CVD', struct=np.where(d == 1, sL[i], sS[i]))
    # ---------- F5c climax volume at the session extreme, delta opposite vs aligned ----------
    ext_l = ok & (Lo <= x['slp']); ext_h = ok & (H >= x['shp']); big = x['rvol_t'] >= 2.0
    for lab, cL, cS in (('opp delta', ext_l & big & (dt > 0), ext_h & big & (dt < 0)),
                        ('aligned delta (ctrl)', ext_l & big & (dt < 0), ext_h & big & (dt > 0))):
        i, d = L.pack(cL, cS, gap)
        L.variants(tf, i, d, 'F5 climax %s' % lab, 'F5 delta/CVD', struct=np.where(d == 1, Lo[i], H[i]))
    # ---------- F5d initial balance (NY 09:30-10:30) breakout with CVD agreement ----------
    ny = x['ny_min']; ibm = (ny >= 570) & (ny < 630)
    ibh, ibl, last = A_wr = L.A.win_range(x, ibm)
    rth = (ny >= 570) & (ny < 960)
    rc = pd.Series(np.where(rth, dt, 0.0)).groupby(x['tday']).cumsum().to_numpy()
    okb = L.base_ok(x, 0) & rth & (ny >= 630) & ~np.isnan(ibh)
    upb = okb & (C > ibh); dnb = okb & (C < ibl)
    def firstday(c):
        idx = np.flatnonzero(c); k = x['tday'][idx]; keep = np.r_[True, k[1:] != k[:-1]]; return idx[keep]
    iu = firstday(upb); idn = firstday(dnb)
    i = np.r_[iu, idn]; d = np.r_[np.ones(len(iu), int), -np.ones(len(idn), int)]; o = np.argsort(i); i, d = i[o], d[o]
    mid = (ibh[i] + ibl[i]) / 2
    agree = np.sign(rc[i]) == d
    for lab, m in (('CVD agree', agree), ('CVD disagree', ~agree)):
        L.variants(tf, i[m], d[m], 'F5 IBbrk %s' % lab, 'F5 delta/CVD', struct=mid[m])
