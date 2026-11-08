"""Entry research kit, part 4: causal features at the signal bar's close (only data known then). Direction-signed features are
multiplied by d (positive = in favour of the trade)."""
import numpy as np, pandas as pd
from numba import njit
import data

@njit(cache=True)
def _session_stats(O, H, L, C, ds):
    n = len(C); sid = np.empty(n, np.int64); sO = np.empty(n); sH = np.empty(n); sL = np.empty(n)
    k = -1; h = l = o = 0.0
    for i in range(n):
        if ds[i]: k += 1; o = O[i]; h = H[i]; l = L[i]
        else: h = max(h, H[i]); l = min(l, L[i])
        sid[i] = k; sO[i] = o; sH[i] = h; sL[i] = l
    return sid, sO, sH, sL

@njit(cache=True)
def _since_touch(H, L, V):
    n = len(H); tl = np.empty(n, np.int64); ts = np.empty(n, np.int64); a = 10 ** 6; b = 10 ** 6
    for i in range(n):
        a = 0 if L[i] <= V[i] else a + 1; b = 0 if H[i] >= V[i] else b + 1
        tl[i] = a; ts[i] = b
    return tl, ts

@njit(cache=True)
def _consec(O, C):
    n = len(C); up = np.zeros(n, np.int64); dn = np.zeros(n, np.int64)
    for i in range(1, n):
        up[i] = up[i - 1] + 1 if C[i - 1] > O[i - 1] else 0       # bullish bars in a row BEFORE bar i
        dn[i] = dn[i - 1] + 1 if C[i - 1] < O[i - 1] else 0
    return up, dn

@njit(cache=True)
def _ema(x, n):
    o = np.empty(len(x)); a = 2.0 / (n + 1); s = x[0]
    for i in range(len(x)):
        s = x[i] if i == 0 else a * x[i] + (1 - a) * s; o[i] = s
    return o

def _rollmax(x, w):
    s = pd.Series(x); return s.rolling(w, min_periods=1).max().shift(1).to_numpy()
def _rollmin(x, w):
    s = pd.Series(x); return s.rolling(w, min_periods=1).min().shift(1).to_numpy()
def _rollmean(x, w):
    s = pd.Series(x); return s.rolling(w, min_periods=1).mean().shift(1).to_numpy()

_SESS = {}
def sessions(tf):
    """per session (server date): open / high / low / close and a daily ATR(14) over completed sessions"""
    if tf in _SESS: return _SESS[tf]
    b = data.load(tf); sid, sO, sH, sL = _session_stats(b['O'], b['H'], b['L'], b['C'], b['ds'])
    ns = sid[-1] + 1; last = np.searchsorted(sid, np.arange(ns), 'right') - 1
    dO = sO[last]; dH = sH[last]; dL = sL[last]; dC = b['C'][last]
    dtr = np.empty(ns); dtr[0] = dH[0] - dL[0]; dtr[1:] = np.maximum(dH[1:] - dL[1:], np.maximum(abs(dH[1:] - dC[:-1]), abs(dL[1:] - dC[:-1])))
    datr = data.rma(dtr, 14)
    out = dict(sid=sid, sO=sO, sH=sH, sL=sL, dO=dO, dH=dH, dL=dL, dC=dC, datr=datr, dema20=_ema(dC, 20), dema50=_ema(dC, 50))
    _SESS[tf] = out; return out

def h1_context(tf):
    """for every bar of tf: index of the last H1 bar closed at the bar's close (or -1)"""
    b = data.load(tf); h = data.load('H1')
    close_t = b['utc'] + 60 * b['tfmin']
    return np.searchsorted(h['utc'] + 3600, close_t, 'right') - 1

def build(tf, s):
    """s = signals.raw(tf) (or any dict with i, d, entry, stop): DataFrame of features"""
    b = data.load(tf); i = s['i']; d = s['d'].astype(np.float64)
    O, H, L, C, A, V, SD = b['O'], b['H'], b['L'], b['C'], b['atr'], b['V'], b['SD']
    ss = sessions(tf); sid = ss['sid'][i]
    prev = sid - 1                                              # last completed session
    ok1 = prev >= 0
    pc = lambda arr, k: np.where(sid - k >= 0, arr[np.maximum(sid - k, 0)], np.nan)
    datr = pc(ss['datr'], 1)
    f = {}
    f['dir'] = d
    f['year'] = b['year'][i]; f['month'] = b['month'][i]
    f['utc_hour'] = b['utc_min'][i] // 60 + 0.0; f['utc_wd'] = b['utc_wd'][i] + 0.0
    f['ist_min'] = b['ist_min'][i] + 0.0
    # ---- trend / drift (signed) ----
    for k in (1, 3, 5, 10, 20):
        f['trend_d%d' % k] = d * (C[i] - pc(ss['dC'], k)) / datr
    f['ema20_d'] = d * (C[i] - pc(ss['dema20'], 1)) / datr
    f['ema50_d'] = d * (C[i] - pc(ss['dema50'], 1)) / datr
    f['ema20_slope'] = d * (pc(ss['dema20'], 1) - pc(ss['dema20'], 6)) / datr
    f['vwm_a'] = d * (C[i] - b['Vm'][i]) / A[i]; f['vwm_z'] = d * (C[i] - b['Vm'][i]) / np.where(b['SDm'][i] > 0, b['SDm'][i], np.nan)
    f['vww_a'] = d * (C[i] - b['Vw'][i]) / A[i]; f['vww_z'] = d * (C[i] - b['Vw'][i]) / np.where(b['SDw'][i] > 0, b['SDw'][i], np.nan)
    if tf != 'H1':
        h = data.load('H1'); hi = h1_context(tf)[i]; hC = h['C']; hA = h['atr']; he20 = _ema(hC, 20); he50 = _ema(hC, 50)
        okh = hi >= 12
        hk = np.maximum(hi, 12)
        f['h1_ret4'] = np.where(okh, d * (C[i] - hC[hk - 4]) / hA[hk], np.nan)
        f['h1_ret12'] = np.where(okh, d * (C[i] - hC[hk - 12]) / hA[hk], np.nan)
        f['h1_ema20'] = np.where(okh, d * (C[i] - he20[hk]) / hA[hk], np.nan)
        f['h1_ema20_slope'] = np.where(okh, d * (he20[hk] - he20[hk - 3]) / hA[hk], np.nan)
        f['h1_ema50'] = np.where(okh, d * (C[i] - he50[hk]) / hA[hk], np.nan)
        f['atr_vs_h1'] = A[i] / hA[hk]
    # ---- session / VWAP ----
    f['vwd_a'] = d * (C[i] - V[i]) / A[i]
    f['vwd_z'] = d * (C[i] - V[i]) / np.where(SD[i] > 0, SD[i], np.nan)
    for k in (3, 10, 20):
        f['vslope%d' % k] = d * (V[i] - V[np.maximum(i - k, 0)]) / A[i]
    f['vb'] = b['vb'][i] + 0.0
    rng_s = ss['sH'][i] - ss['sL'][i]
    pos = np.where(rng_s > 0, (C[i] - ss['sL'][i]) / np.where(rng_s > 0, rng_s, 1), 0.5)
    f['sess_pos'] = np.where(d > 0, pos, 1 - pos)
    f['sess_rng_d'] = rng_s / datr
    f['sess_move'] = d * (C[i] - ss['sO'][i]) / A[i]
    pdH = pc(ss['dH'], 1); pdL = pc(ss['dL'], 1); pdC = pc(ss['dC'], 1)
    f['pd_brk'] = np.where(d > 0, C[i] - pdH, pdL - C[i]) / A[i]
    f['pd_pos'] = np.where(d > 0, (C[i] - pdL) / (pdH - pdL), (pdH - C[i]) / (pdH - pdL))
    f['gap_d'] = d * (ss['sO'][i] - pdC) / datr
    f['pd_dir'] = d * np.sign(pdC - pc(ss['dO'], 1))
    tl, ts = _since_touch(H, L, V)
    f['since_vw_touch'] = np.where(d > 0, tl[i], ts[i]) + 0.0
    f['new_sess_ext'] = np.where(d > 0, H[i] >= ss['sH'][i] - 1e-9, L[i] <= ss['sL'][i] + 1e-9).astype(float)
    # ---- signal candle / momentum ----
    rng = H[i] - L[i]
    f['rng_a'] = rng / A[i]
    f['body_p'] = np.abs(C[i] - O[i]) / np.where(rng > 0, rng, np.nan)
    f['close_p'] = np.where(d > 0, (C[i] - L[i]), (H[i] - C[i])) / np.where(rng > 0, rng, np.nan)
    f['brk_a'] = np.where(d > 0, C[i] - s['sigH'], s['sigL'] - C[i]) / A[i]
    f['mom10_a'] = d * (C[i] - C[np.maximum(i - 10, 0)]) / A[i]
    f['mom30_a'] = d * (C[i] - C[np.maximum(i - 30, 0)]) / A[i]
    f['er10'] = d * s['er']
    tvm = _rollmean(b['TV'], 20)
    f['vol_r'] = b['TV'][i] / np.where(tvm[i] > 0, tvm[i], np.nan)
    up, dn = _consec(O, C)
    f['consec'] = np.where(d > 0, up[i], dn[i]) + 0.0
    f['comp20'] = (_rollmax(H, 20)[i] - _rollmin(L, 20)[i]) / A[i]
    f['comp50'] = (_rollmax(H, 50)[i] - _rollmin(L, 50)[i]) / A[i]
    a100 = data.rma(b['tr'], 100)
    f['atr_r100'] = A[i] / a100[i]
    f['atr_d'] = A[i] / datr
    f['prev_net'] = d * s['prevNet']
    # signals nearby (raw universe): bars since the previous raw signal in the same / opposite direction
    ii = i.astype(np.int64); same = np.full(len(ii), 1e6); opp = np.full(len(ii), 1e6)
    lastL = lastS = -10 ** 9
    for k in range(len(ii)):
        if d[k] > 0: same[k] = ii[k] - lastL; opp[k] = ii[k] - lastS
        else: same[k] = ii[k] - lastS; opp[k] = ii[k] - lastL
        if d[k] > 0: lastL = ii[k]
        else: lastS = ii[k]
    f['since_same'] = np.minimum(same, 1e4); f['since_opp'] = np.minimum(opp, 1e4)
    # ---- entry geometry ----
    risk = d * (s['entry'] - s['stop'])
    f['depth_a'] = d * (C[i] - s['entry']) / A[i]
    f['risk_a'] = risk / A[i]
    f['half'] = s['half'].astype(float)
    f['cost_r'] = b['SP'][i] / risk
    f['ent_vw_a'] = d * (s['entry'] - V[i]) / A[i]
    f['stop_vw_a'] = d * (s['stop'] - V[i]) / A[i]
    f['spread_a'] = b['SP'][i] / A[i]
    return pd.DataFrame(f)
