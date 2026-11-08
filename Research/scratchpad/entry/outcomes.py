"""Entry research kit, part 3: fill and outcome of every signal on its own (no one-trade-at-a-time).
Two labels per signal: the engine's chart-bar convention (fill bar: stop only; then per bar stop first, else best price) and the
1-minute path (fill minute found inside the fill bar; then per minute stop first). Outcome = MFE in R before the stop, capped at maxR."""
import numpy as np
from numba import njit
import data

TOL = 0.01 * 0.001

@njit(cache=True)
def _sim(Oc, Hc, Lc, Cc, lo, hi, O1, H1, L1, ii, dd, ent, stp, mode, window, maxR, hor_c, hor_m):
    n = len(ii); nc = len(Hc); nm = len(H1)
    fb = np.full(n, -1, np.int64); fm = np.full(n, -1, np.int64)
    mfeC = np.full(n, np.nan); stC = np.zeros(n, np.bool_); xC = np.full(n, -1, np.int64)
    mfeM = np.full(n, np.nan); stM = np.zeros(n, np.bool_); xM = np.full(n, -1, np.int64)
    t1M = np.full(n, -1, np.int64)
    for s in range(n):
        i = ii[s]; d = dd[s]; e = ent[s]; st = stp[s]; risk = d * (e - st)
        if risk <= 0: continue
        # ---- fill on the chart bars ----
        j = -1
        for k in range(i + 1, min(i + 1 + window, nc)):
            if mode[s] == 1: j = k; break                                  # market: next bar
            if mode[s] == 0:                                                # limit: price trades back to the level
                if (d == 1 and Lc[k] <= e + TOL) or (d == -1 and Hc[k] >= e - TOL): j = k; break
            else:                                                           # stop entry: price trades through the level
                if (d == 1 and Hc[k] >= e - TOL) or (d == -1 and Lc[k] <= e + TOL): j = k; break
        if j < 0: continue
        fb[s] = j
        # ---- chart convention ----
        if (d == 1 and Lc[j] <= st + TOL) or (d == -1 and Hc[j] >= st - TOL):
            mfeC[s] = 0.0; stC[s] = True; xC[s] = j
        else:
            best = e; done = False
            for k in range(j + 1, min(j + 1 + hor_c, nc)):
                if (d == 1 and Lc[k] <= st + TOL) or (d == -1 and Hc[k] >= st - TOL):
                    stC[s] = True; xC[s] = k; done = True; break
                best = max(best, Hc[k]) if d == 1 else min(best, Lc[k])
                if d * (best - e) >= maxR * risk - TOL: xC[s] = k; done = True; break
            mfeC[s] = min(d * (best - e) / risk, maxR)
            if not done: xC[s] = -2
        # ---- 1-minute path ----
        m = -1
        for q in range(lo[j], hi[j]):
            if mode[s] == 1: m = q; break
            if mode[s] == 0:
                if (d == 1 and L1[q] <= e + TOL) or (d == -1 and H1[q] >= e - TOL): m = q; break
            else:
                if (d == 1 and H1[q] >= e - TOL) or (d == -1 and L1[q] <= e + TOL): m = q; break
        if m < 0: continue
        fm[s] = m
        if (d == 1 and L1[m] <= st + TOL) or (d == -1 and H1[m] >= st - TOL):
            mfeM[s] = 0.0; stM[s] = True; xM[s] = m; continue
        best = e; done = False
        for q in range(m + 1, min(m + 1 + hor_m, nm)):
            if (d == 1 and L1[q] <= st + TOL) or (d == -1 and H1[q] >= st - TOL):
                stM[s] = True; xM[s] = q; done = True; break
            best = max(best, H1[q]) if d == 1 else min(best, L1[q])
            if t1M[s] < 0 and d * (best - e) >= 0.6 * risk - TOL: t1M[s] = q - m
            if d * (best - e) >= maxR * risk - TOL: xM[s] = q; done = True; break
        mfeM[s] = min(d * (best - e) / risk, maxR)
        if not done: xM[s] = -2
    return fb, fm, mfeC, stC, xC, mfeM, stM, xM, t1M

def simulate(tf, i, d, entry, stop, mode=0, window=5, maxR=5.0, hor_days=60):
    """mode 0 limit / 1 market (entry = signal close, filled at the next bar) / 2 stop entry; arrays or scalars for mode"""
    b = data.load(tf); m = data.load('M1'); lo, hi = data.m1_map(tf)
    n = len(i); mode = np.broadcast_to(np.asarray(mode, np.int64), (n,)).copy()
    hor_c = int(hor_days * 1440 / b['tfmin']); hor_m = int(hor_days * 1440)
    r = _sim(b['O'], b['H'], b['L'], b['C'], lo, hi, m['O'], m['H'], m['L'], np.asarray(i, np.int64), np.asarray(d, np.int64),
             np.asarray(entry, np.float64), np.asarray(stop, np.float64), mode, window, maxR, hor_c, hor_m)
    k = ('fill_bar', 'fill_m1', 'mfe_c', 'stop_c', 'exit_c', 'mfe_m', 'stop_m', 'exit_m', 't1_m')
    return dict(zip(k, r))
