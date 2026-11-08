"""family 3: session VWAP: reclaim / reject after N bars on one side, pullback to VWAP / 1 sigma with the VWAP slope, 2-2.5 sigma fades"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, pandas as pd
FAM = 'vwap'
def runs_side(x):
    """number of consecutive bars (ending at i) with x True"""
    out = np.zeros(len(x), np.int64); c = 0
    for k in range(len(x)):
        c = c + 1 if x[k] else 0; out[k] = c
    return out

def go(tf, name, Lmask, Smask, gap, stops):
    b = lib.ctx(tf); H, L, C, A = b['H'], b['L'], b['C'], b['atr']
    il = lib.decluster(np.flatnonzero(Lmask & b['ok']), gap); is_ = lib.decluster(np.flatnonzero(Smask & b['ok']), gap)
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int); c = C[i]; a = A[i]
    for sname, st in stops(b, i, d, c, a):
        lib.run(tf, i, d, c, st, 1, name=name + ' ' + sname, family=FAM)

def atr_stop(k):
    return lambda b, i, d, c, a: [('%.1fATR' % k, c - d * k * a)]

for tf in sys.argv[1].split(','):
    b = lib.ctx(tf); H, L, C, O, A, V, SD = b['H'], b['L'], b['C'], b['O'], b['atr'], b['V'], b['SD']
    per_h = 60 // b['tfmin']; gap = per_h
    sess = (b['vb'] >= 2 * per_h) & (b['ny_wd'] < 5)
    below = C < V; above = C > V
    rb = runs_side(below); ra = runs_side(above)
    pb = np.r_[0, rb[:-1]]; pa = np.r_[0, ra[:-1]]
    def struct(N):
        def f(b, i, d, c, a):
            lo = pd.Series(L).rolling(N + 1).min().to_numpy()[i]; hi = pd.Series(H).rolling(N + 1).max().to_numpy()[i]
            st = np.where(d == 1, np.minimum(lo - 0.1 * a, c - 0.5 * a), np.maximum(hi + 0.1 * a, c + 0.5 * a))
            return [('1.8ATR', c - d * 1.8 * a), ('stop=swing', st)]
        return f
    for N in ((6, 12) if tf != 'H1' else (4, 8)):
        Nb = N if tf == 'M5' else max(3, N // 2)
        go(tf, 'VWAP reclaim after %d bars' % Nb, sess & above & (pb >= Nb), sess & below & (pa >= Nb), gap, struct(Nb))
        # reject: on one side for N bars, poke through VWAP and close back -> continue
        rejS = sess & (pb >= Nb) & (H > V) & (C < V); rejL = sess & (pa >= Nb) & (L < V) & (C > V)
        def ext(b, i, d, c, a):
            e = np.where(d == 1, L[i], H[i]); st = np.where(d == 1, np.minimum(e - 0.1 * a, c - 0.5 * a), np.maximum(e + 0.1 * a, c + 0.5 * a))
            return [('1.8ATR', c - d * 1.8 * a), ('stop=ext', st)]
        go(tf, 'VWAP reject after %d bars' % Nb, rejL, rejS, gap, ext)
    # pullback with slope
    slope = (V - np.r_[np.full(2 * per_h, np.nan), V[:-2 * per_h]]) / A
    ra12 = pd.Series(above.astype(float)).rolling(per_h * 2).mean().to_numpy(); rb12 = pd.Series(below.astype(float)).rolling(per_h * 2).mean().to_numpy()
    for th in (0.5, 1.0):
        pL = sess & (slope > th) & (np.r_[0, ra12[:-1]] >= 0.8) & (L <= V) & (C > V)
        pS = sess & (slope < -th) & (np.r_[0, rb12[:-1]] >= 0.8) & (H >= V) & (C < V)
        go(tf, 'VWAP pullback slope>%.1fATR/2h' % th, pL, pS, gap, struct(3))
        u1 = V + SD; d1 = V - SD
        pL = sess & (slope > th) & (np.r_[0, ra12[:-1]] >= 0.8) & (L <= u1) & (C > u1) & (np.r_[0, C[:-1]] > np.r_[0, u1[:-1]])
        pS = sess & (slope < -th) & (np.r_[0, rb12[:-1]] >= 0.8) & (H >= d1) & (C < d1) & (np.r_[0, C[:-1]] < np.r_[0, d1[:-1]])
        go(tf, 'VWAP 1sig pullback slope>%.1f' % th, pL, pS, gap, struct(3))
    # sigma fades
    z = (C - V) / np.where(SD > 0, SD, np.nan); pz = np.r_[0, z[:-1]]
    sd_ok = SD > 0.5 * A
    for k in (2.0, 2.5):
        go(tf, 'VWAP %.1fsig fade (first close beyond)' % k, sess & sd_ok & (z < -k) & (pz >= -k), sess & sd_ok & (z > k) & (pz <= k), gap,
           lambda b, i, d, c, a: [('1.8ATR', c - d * 1.8 * a), ('3ATR', c - d * 3 * a)])
        go(tf, 'VWAP %.1fsig fade (close back inside)' % k, sess & sd_ok & (z > -k) & (pz <= -k), sess & sd_ok & (z < k) & (pz >= k), gap,
           lambda b, i, d, c, a: [('1.8ATR', c - d * 1.8 * a)])
