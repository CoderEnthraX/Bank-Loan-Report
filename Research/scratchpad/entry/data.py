"""Entry research kit, part 1: gold bars as numpy arrays (cached .npz), the engine's session / week / month VWAPs, sigma, ATR.
Times: utc = int64 seconds (bar open, UTC); srv day start = the engine's session start (new server date)."""
import os, pickle, datetime
import numpy as np
from numba import njit
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
EP = datetime.datetime(1970, 1, 1)
TFMIN = {'M1': 1, 'M5': 5, 'M15': 15, 'H1': 60}

def _cache(tf):
    f = '%s/entry/cache_%s.npz' % (S, tf)
    if not os.path.exists(f):
        d = pickle.load(open('%s/gold/data/%s.pkl' % (S, tf), 'rb'))
        utc = np.array([int((t - EP).total_seconds()) for t in d['utc']], dtype=np.int64)
        srv = np.array([int((t - EP).total_seconds()) for t in d['srv']], dtype=np.int64)
        np.savez(f, utc=utc, srv=srv, O=np.array(d['O']), H=np.array(d['H']), L=np.array(d['L']), C=np.array(d['C']),
                 TV=np.array(d['TV'], dtype=np.float64), SP=np.array(d['SP'], dtype=np.float64) * 0.01)
    return dict(np.load(f))

@njit(cache=True)
def rma(x, n):
    o = np.full(len(x), np.nan); s = 0.0
    for i in range(len(x)):
        if i < n - 1: continue
        if i == n - 1: s = x[:n].mean()
        else: s = (s * (n - 1) + x[i]) / n
        o[i] = s
    return o

@njit(cache=True)
def anchored_vwap(H, L, C, W, anchor):
    n = len(C); V = np.empty(n); SD = np.empty(n); cnt = np.empty(n, np.int64)
    sw = s1 = s2 = 0.0; k = 0
    for i in range(n):
        if anchor[i]: sw = s1 = s2 = 0.0; k = 0
        else: k += 1
        tp = (H[i] + L[i] + C[i]) / 3.0; w = W[i]
        sw += w; s1 += w * tp; s2 += w * tp * tp
        V[i] = s1 / sw; SD[i] = np.sqrt(max(s2 / sw - (s1 / sw) ** 2, 0.0)); cnt[i] = k
    return V, SD, cnt

_D = {}
def load(tf):
    """bars + engine series for one timeframe"""
    if tf in _D: return _D[tf]
    d = _cache(tf); n = len(d['O'])
    O, H, L, C = d['O'], d['H'], d['L'], d['C']
    sday = d['srv'] // 86400
    ds = np.ones(n, bool); ds[1:] = sday[1:] != sday[:-1]                       # new server date = session start (engine 'daystart')
    srvdt = d['srv'].astype('datetime64[s]')
    yr = srvdt.astype('datetime64[Y]').astype(int); mo = srvdt.astype('datetime64[M]').astype(int)
    wk = ((d['srv'] // 86400) + 3) // 7                                          # ISO week number proxy (weeks start Monday)
    an_w = ds.copy(); an_w[1:] &= wk[1:] != wk[:-1]
    an_m = ds.copy(); an_m[1:] &= mo[1:] != mo[:-1]
    W = np.where(d['TV'] > 0, d['TV'], 1.0)
    tr = np.empty(n); tr[0] = H[0] - L[0]
    tr[1:] = np.maximum(H[1:] - L[1:], np.maximum(np.abs(H[1:] - C[:-1]), np.abs(L[1:] - C[:-1])))
    V, SD, vb = anchored_vwap(H, L, C, W, ds)
    Vw, SDw, _ = anchored_vwap(H, L, C, W, an_w)
    Vm, SDm, _ = anchored_vwap(H, L, C, W, an_m)
    ist = d['utc'] + 19800
    out = dict(d, n=n, ds=ds, W=W, tr=tr, atr=rma(tr, 14), V=V, SD=SD, vb=vb, Vw=Vw, SDw=SDw, Vm=Vm, SDm=SDm,
               ist=ist, ist_min=(ist // 60) % 1440, ist_wd=((ist // 86400) + 3) % 7, utc_wd=((d['utc'] // 86400) + 3) % 7,
               utc_min=(d['utc'] // 60) % 1440, year=yr + 1970, month=mo % 12 + 1, tfmin=TFMIN[tf], tf=tf)
    _D[tf] = out; return out

def m1_map(tf):
    """for every bar of tf: the first M1 index inside it and the first M1 index of the next bar (M1 bars cover [utc, utc + tfmin))"""
    b = load(tf); m = load('M1')
    lo = np.searchsorted(m['utc'], b['utc'], 'left'); hi = np.searchsorted(m['utc'], b['utc'] + 60 * b['tfmin'], 'left')
    return lo, hi
