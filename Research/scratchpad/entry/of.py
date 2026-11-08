"""Entry research kit, part 7: ORDER FLOW from TICK VOLUME (FxPro / OANDA gold have no real bid/ask volume; TradingView's
order-flow tools on XAUUSD are tick-volume estimates too, so this is what the user can compute on his charts).

- Delta per 1-minute bar: tick rule  TV x sign(C - O)  and CLV  TV x (2C - H - L) / (H - L). Per chart bar = sum of its minutes.
  Session CVD = running sum since the session start (server day, like the indicator's VWAP).
- Volume profile per session: every minute's tick volume spread evenly over its high-low range in $0.50 bins.
  POC, value area 70 % (VAH / VAL): developing (up to the chart bar's close) and the prior session (final).
  RVP (relative volume at price) = bin volume / mean volume of the traded bins of that profile: LVN about < 0.5, HVN about > 1.5.

API (all causal, i = chart bar index, decided at its close):
  f = flow(tf)                    -> dict of per-bar arrays: vol, dtk, dcl (bar delta, tick / CLV), cvd_tk, cvd_cl (session CVD),
                                     dpoc, dvah, dval (developing), ppoc, pvah, pval (prior session), sid (session id), sfirst
  rvp(tf, i, prices, 'dev'|'prior')               -> relative volume at each price
  path_rvp(tf, i, p0, p1, 'dev'|'prior')          -> (min, max, mean) RVP over the bins between p0 and p1 (e.g. entry -> TP1)
  store(tf)                                        -> per-session final histograms: base, nb, off, flat (bin k price = (base+k+0.5)*W)
python3 -I of.py build   -> caches entry/of_TF.npz for H1 M15 M5 M1."""
import os, sys, numpy as np
from numba import njit
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
if S + '/entry' not in sys.path: sys.path.insert(0, S + '/entry')
import data
W = 0.5; VA = 0.70

@njit(cache=True)
def _m1_delta(O, H, L, C, TV):
    n = len(C); dt = np.zeros(n); dc = np.zeros(n)
    for k in range(n):
        v = TV[k]
        if C[k] > O[k]: dt[k] = v
        elif C[k] < O[k]: dt[k] = -v
        r = H[k] - L[k]
        if r > 0: dc[k] = v * (2.0 * C[k] - H[k] - L[k]) / r
    return dt, dc

@njit(cache=True)
def _va(hist, frac):
    nb = len(hist); tot = hist.sum()
    if tot <= 0: return -1, -1, -1
    poc = np.argmax(hist); lo = poc; hi = poc; acc = hist[poc]
    while acc < frac * tot:
        up = hist[hi + 1] if hi + 1 < nb else -1.0
        dn = hist[lo - 1] if lo - 1 >= 0 else -1.0
        if up < 0 and dn < 0: break
        if up >= dn: hi += 1; acc += up
        else: lo -= 1; acc += dn
    return poc, lo, hi

@njit(cache=True)
def _add(hist, base, h, l, v, w):
    b0 = int(np.floor(l / w)) - base; b1 = int(np.floor(h / w)) - base
    if b0 < 0: b0 = 0
    if b1 > len(hist) - 1: b1 = len(hist) - 1
    cnt = b1 - b0 + 1
    if cnt <= 0: return
    x = v / cnt
    for q in range(b0, b1 + 1): hist[q] += x

@njit(cache=True)
def _profiles(sfirst, slast, lo, hi, H1, L1, TV1, w, frac):
    nS = len(sfirst); nC = len(lo)
    base = np.zeros(nS, np.int64); nb = np.zeros(nS, np.int64); off = np.zeros(nS + 1, np.int64)
    for s in range(nS):
        a = lo[sfirst[s]]; b = hi[slast[s]]
        if b <= a: base[s] = 0; nb[s] = 1
        else:
            mn = L1[a:b].min(); mx = H1[a:b].max()
            base[s] = int(np.floor(mn / w)); nb[s] = int(np.floor(mx / w)) - base[s] + 1
        off[s + 1] = off[s] + nb[s]
    flat = np.zeros(off[nS])
    dpoc = np.full(nC, np.nan); dvah = np.full(nC, np.nan); dval = np.full(nC, np.nan)
    fpoc = np.full(nS, np.nan); fvah = np.full(nS, np.nan); fval = np.full(nS, np.nan)
    for s in range(nS):
        hist = flat[off[s]:off[s + 1]]; m = lo[sfirst[s]]
        for j in range(sfirst[s], slast[s] + 1):
            while m < hi[j]:
                _add(hist, base[s], H1[m], L1[m], TV1[m], w); m += 1
            p, a_, b_ = _va(hist, frac)
            if p >= 0:
                dpoc[j] = (base[s] + p + 0.5) * w; dval[j] = (base[s] + a_) * w; dvah[j] = (base[s] + b_ + 1) * w
        p, a_, b_ = _va(hist, frac)
        if p >= 0:
            fpoc[s] = (base[s] + p + 0.5) * w; fval[s] = (base[s] + a_) * w; fvah[s] = (base[s] + b_ + 1) * w
    return base, nb, off, flat, dpoc, dvah, dval, fpoc, fvah, fval

_F = {}
def flow(tf):
    if tf in _F: return _F[tf]
    f = '%s/entry/of_%s.npz' % (S, tf)
    if os.path.exists(f):
        _F[tf] = dict(np.load(f)); return _F[tf]
    b = data.load(tf); m = data.load('M1'); lo, hi = data.m1_map(tf)
    dt1, dc1 = _m1_delta(m['O'], m['H'], m['L'], m['C'], m['TV'])
    ct = np.r_[0.0, np.cumsum(dt1)]; cc = np.r_[0.0, np.cumsum(dc1)]; cv = np.r_[0.0, np.cumsum(m['TV'])]
    dtk = ct[hi] - ct[lo]; dcl = cc[hi] - cc[lo]; vol = cv[hi] - cv[lo]
    sid = np.cumsum(b['ds']) - 1
    sfirst = np.flatnonzero(b['ds']); slast = np.r_[sfirst[1:] - 1, b['n'] - 1]
    # session CVD (reset at the session start)
    def scum(x):
        c = np.cumsum(x); return c - np.r_[0.0, c][sfirst][sid]
    base, nb, off, flat, dpoc, dvah, dval, fpoc, fvah, fval = _profiles(sfirst, slast, lo, hi, m['H'], m['L'], m['TV'], W, VA)
    prev = sid - 1; okp = prev >= 0; pi = np.maximum(prev, 0)
    out = dict(vol=vol, dtk=dtk, dcl=dcl, cvd_tk=scum(dtk), cvd_cl=scum(dcl), dpoc=dpoc, dvah=dvah, dval=dval,
               ppoc=np.where(okp, fpoc[pi], np.nan), pvah=np.where(okp, fvah[pi], np.nan), pval=np.where(okp, fval[pi], np.nan),
               sid=sid, sfirst=sfirst, slast=slast, base=base, nb=nb, off=off, flat=flat, lo=lo, hi=hi)
    np.savez(f, **out); _F[tf] = out; return out

def store(tf):
    f = flow(tf); return dict(base=f['base'], nb=f['nb'], off=f['off'], flat=f['flat'], W=W)

@njit(cache=True)
def _dev_hist_query(order, ii, sid, sfirst, lo, hi, base, nb, H1, L1, TV1, w, p0, p1, out_min, out_max, out_mean, single):
    """developing profile at bar ii[q] (sorted by `order`): RVP at p0 (single) or min / max / mean RVP over bins between p0 and p1"""
    curS = -1; m = 0; hist = np.zeros(1)
    for t in range(len(order)):
        q = order[t]; j = ii[q]; s = sid[j]
        if s != curS:
            curS = s; hist = np.zeros(nb[s]); m = lo[sfirst[s]]
        while m < hi[j]:
            _add(hist, base[s], H1[m], L1[m], TV1[m], w); m += 1
        traded = hist[hist > 0]
        mean = traded.mean() if len(traded) else np.nan
        k0 = int(np.floor(p0[q] / w)) - base[s]; k1 = int(np.floor(p1[q] / w)) - base[s]
        if single:
            out_min[q] = (hist[k0] / mean) if (0 <= k0 < nb[s] and mean > 0) else 0.0
            continue
        a = min(k0, k1); b_ = max(k0, k1); mn = 1e18; mx = -1.0; sm = 0.0; c = 0
        for k in range(a, b_ + 1):
            r = (hist[k] / mean) if (0 <= k < nb[s] and mean > 0) else 0.0
            mn = min(mn, r); mx = max(mx, r); sm += r; c += 1
        out_min[q] = mn; out_max[q] = mx; out_mean[q] = sm / c if c else np.nan

@njit(cache=True)
def _prior_query(ii, sid, base, nb, off, flat, w, p0, p1, out_min, out_max, out_mean, single):
    for q in range(len(ii)):
        s = sid[ii[q]] - 1
        if s < 0:
            out_min[q] = np.nan; out_max[q] = np.nan; out_mean[q] = np.nan; continue
        hist = flat[off[s]:off[s + 1]]; traded = hist[hist > 0]
        mean = traded.mean() if len(traded) else np.nan
        k0 = int(np.floor(p0[q] / w)) - base[s]; k1 = int(np.floor(p1[q] / w)) - base[s]
        if single:
            out_min[q] = (hist[k0] / mean) if (0 <= k0 < nb[s] and mean > 0) else 0.0
            continue
        a = min(k0, k1); b_ = max(k0, k1); mn = 1e18; mx = -1.0; sm = 0.0; c = 0
        for k in range(a, b_ + 1):
            r = (hist[k] / mean) if (0 <= k < nb[s] and mean > 0) else 0.0
            mn = min(mn, r); mx = max(mx, r); sm += r; c += 1
        out_min[q] = mn; out_max[q] = mx; out_mean[q] = sm / c if c else np.nan

def _query(tf, i, p0, p1, which, single):
    f = flow(tf); m = data.load('M1')
    i = np.asarray(i, np.int64); p0 = np.asarray(p0, float); p1 = np.asarray(p0 if p1 is None else p1, float)
    n = len(i); a = np.full(n, np.nan); b = np.full(n, np.nan); c = np.full(n, np.nan)
    if which == 'dev':
        order = np.argsort(i, kind='stable')
        _dev_hist_query(order, i, f['sid'], f['sfirst'], f['lo'], f['hi'], f['base'], f['nb'], m['H'], m['L'], m['TV'], W, p0, p1, a, b, c, single)
    else:
        _prior_query(i, f['sid'], f['base'], f['nb'], f['off'], f['flat'], W, p0, p1, a, b, c, single)
    return a if single else (a, b, c)

def rvp(tf, i, prices, which='dev'):
    return _query(tf, i, prices, None, which, True)

def path_rvp(tf, i, p0, p1, which='dev'):
    return _query(tf, i, p0, p1, which, False)

if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'build':
    for tf in ('H1', 'M15', 'M5', 'M1'):
        f = flow(tf); b = data.load(tf)
        ok = ~np.isnan(f['dpoc'])
        inside = (f['dpoc'][ok] >= b['L'][ok].min()) & (f['dval'][ok] <= f['dpoc'][ok]) & (f['dpoc'][ok] <= f['dvah'][ok])
        print(tf, 'bars', b['n'], 'vol check', np.allclose(f['vol'], np.r_[f['vol']]), 'VAL<=POC<=VAH', inside.mean(),
              'delta tick/clv corr %.2f' % np.corrcoef(f['dtk'], f['dcl'])[0, 1])
