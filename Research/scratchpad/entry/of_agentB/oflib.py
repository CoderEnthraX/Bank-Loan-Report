"""of_agentB helpers: reuse agentA/lib (ctx, placebo at same NY hour, run) but write rows to of_agentB/rows.jsonl.
OF context per tf: of.flow arrays + session high/low so far (excluding current bar), prior session H/L, IB (first NY hour 09:30-10:30)."""
import os, sys
os.environ.setdefault('NUMBA_NUM_THREADS', '2')
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
for p in (S + '/entry', S + '/entry/agentA'):
    if p not in sys.path: sys.path.insert(0, p)
import numpy as np, json
import kit, data, of
import lib as A
D = S + '/entry/of_agentB'
A.OUT = D + '/rows.jsonl'
_X = {}

def ctx(tf):
    if tf in _X: return _X[tf]
    b = A.ctx(tf); f = of.flow(tf)
    n = b['n']; H, L = b['H'], b['L']; sid = f['sid']
    # session high/low BEFORE the current bar (running), and including it
    sh = np.empty(n); sl = np.empty(n); shp = np.full(n, np.nan); slp = np.full(n, np.nan)
    import pandas as pd
    g = pd.Series(H).groupby(sid).cummax().to_numpy(); h = pd.Series(L).groupby(sid).cummin().to_numpy()
    sh[:] = g; sl[:] = h
    prev_same = np.r_[False, sid[1:] == sid[:-1]]
    shp[1:] = np.where(prev_same[1:], g[:-1], np.nan); slp[1:] = np.where(prev_same[1:], h[:-1], np.nan)
    # prior session final high / low
    sfirst, slast = f['sfirst'], f['slast']
    fh = g[slast]; fl = h[slast]
    psh = np.where(sid > 0, fh[np.maximum(sid - 1, 0)], np.nan); psl = np.where(sid > 0, fl[np.maximum(sid - 1, 0)], np.nan)
    vma = pd.Series(f['vol']).rolling(50, min_periods=20).mean().shift(1).to_numpy()
    # same-time-of-day volume norm: mean vol over previous 20 sessions at the same NY minute bucket
    nyb = b['ny_min'] // b['tfmin']
    vt = pd.Series(f['vol']).groupby(nyb).transform(lambda s: s.rolling(20, min_periods=5).mean().shift(1)).to_numpy()
    x = dict(b); x.update({k: f[k] for k in ('vol', 'dtk', 'dcl', 'cvd_tk', 'cvd_cl', 'dpoc', 'dvah', 'dval', 'ppoc', 'pvah', 'pval', 'sid')})
    x.update(sh=sh, sl=sl, shp=shp, slp=slp, psh=psh, psl=psl, vma=vma, vtod=vt, rvol=f['vol'] / vma, rvol_t=f['vol'] / vt)
    _X[tf] = x; return x

def run(tf, i, d, entry, stop, mode=1, window=5, name='', family='', K=3, show=True):
    i = np.asarray(i, np.int64)
    return A.run(tf, i, d, entry, stop, mode=mode, window=window, name=name, family=family, K=K, save=True, show=show)

def orders(x, i, d, kind, stop_kind, struct=None, k_atr=1.8, off=0.05):
    """build entry/stop/mode. kind 'mkt' (C[i]) or 'stp' (signal bar extreme +off ATR, window 3). stop_kind 'atr' (k_atr ATR from entry)
    or 'struct' (struct price -/+ 0.1 ATR, clipped to 0.5..3 ATR)."""
    i = np.asarray(i, np.int64); d = np.asarray(d, np.int64); a = x['atr'][i]
    if kind == 'mkt':
        e = x['C'][i].copy(); mode = 1
    else:
        e = np.where(d == 1, x['H'][i] + off * a, x['L'][i] - off * a); mode = 2
    if stop_kind == 'atr':
        st = e - d * k_atr * a
    else:
        st = np.asarray(struct, float) - d * 0.1 * a
        r = d * (e - st); r = np.clip(r, 0.5 * a, 3.0 * a); st = e - d * r
    return e, st, mode

def variants(tf, i, d, name, family, struct=None, kinds=('mkt', 'stp'), stops=('atr', 'struct'), show=True):
    x = ctx(tf); out = []
    for k in kinds:
        for s in stops:
            if s == 'struct' and struct is None: continue
            e, st, mode = orders(x, i, d, k, s, struct)
            out.append(run(tf, i, d, e, st, mode=mode, window=3, name='%s %s %s' % (name, k, s), family=family, show=show))
    return out

def declust(i, d, gap):
    """per direction: keep signals at least gap bars after the previous kept one of the same direction"""
    i = np.asarray(i, np.int64); d = np.asarray(d, np.int64); I = []; Dd = []
    for dd in (1, -1):
        k = A.decluster(i[d == dd], gap); I.append(k); Dd.append(np.full(len(k), dd))
    I = np.concatenate(I); Dd = np.concatenate(Dd); o = np.argsort(I, kind='stable')
    return I[o], Dd[o]

def base_ok(x, min_sess_min=0):
    return x['ok'] & (x['split'] != 'test') & (x['vb'] * x['tfmin'] >= min_sess_min) & (x['ny_wd'] < 5)

def clv(x):
    r = x['H'] - x['L']; return np.where(r > 0, (2 * x['C'] - x['H'] - x['L']) / np.where(r > 0, r, 1), 0.0)

from numba import njit
@njit(cache=True)
def _comp_query(ii, sid, base, nb, off, flat, K, p0, p1, w, omin, omax, omean, oat):
    for q in range(len(ii)):
        s = sid[ii[q]]
        if s - K < 0:
            omin[q] = np.nan; omax[q] = np.nan; omean[q] = np.nan; oat[q] = np.nan; continue
        g0 = 1 << 60; g1 = -1
        for t in range(s - K, s):
            g0 = min(g0, base[t]); g1 = max(g1, base[t] + nb[t])
        h = np.zeros(g1 - g0)
        for t in range(s - K, s):
            for k in range(nb[t]): h[base[t] - g0 + k] += flat[off[t] + k]
        tot = 0.0; c = 0
        for k in range(len(h)):
            if h[k] > 0: tot += h[k]; c += 1
        mean = tot / c if c > 0 else np.nan
        k0 = int(np.floor(p0[q] / w)) - g0; k1 = int(np.floor(p1[q] / w)) - g0
        oat[q] = h[k0] / mean if 0 <= k0 < len(h) else 0.0
        a = min(k0, k1); b = max(k0, k1); mn = 1e18; mx = -1.0; sm = 0.0; cc = 0
        for k in range(a, b + 1):
            r = h[k] / mean if 0 <= k < len(h) else 0.0
            mn = min(mn, r); mx = max(mx, r); sm += r; cc += 1
        omin[q] = mn; omax[q] = mx; omean[q] = sm / cc

def comp_rvp(tf, i, p0, p1=None, K=5):
    """composite profile of the K previous sessions: (rvp at p0, min, max, mean rvp over p0..p1)"""
    f = of.flow(tf); i = np.asarray(i, np.int64); p0 = np.asarray(p0, float); p1 = p0 if p1 is None else np.asarray(p1, float)
    n = len(i); a, b, c, e = (np.full(n, np.nan) for _ in range(4))
    _comp_query(i, f['sid'], f['base'], f['nb'], f['off'], f['flat'], K, p0, p1, of.W, a, b, c, e)
    return e, a, b, c

def pack(cL, cS, gap):
    i = np.r_[np.flatnonzero(cL), np.flatnonzero(cS)]; d = np.r_[np.ones(int(cL.sum()), int), -np.ones(int(cS.sum()), int)]
    o = np.argsort(i, kind='stable'); return declust(i[o], d[o], gap)

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
