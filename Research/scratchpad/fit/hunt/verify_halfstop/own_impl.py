"""Independent short re-implementation of the half-stop rule (numpy), straight from the task spec; uses only raw rows from engine.prepare."""
import sys, os
FIT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, FIT)
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv
from engine2 import prepare
SYMS = ['GC', 'CRUDE', 'NASDAQ', 'NIFTY', 'US30', 'SENSEX', 'EURUSD', 'ETH']
_D = {}
def data(sym):
    if sym in _D: return _D[sym]
    P = prepare(sym); R = P['rows']
    o = np.array([r['o'] for r in R]); h = np.array([r['h'] for r in R]); l = np.array([r['l'] for r in R]); c = np.array([r['c'] for r in R])
    v = np.array([np.nan if r['vwap'] is None else r['vwap'] for r in R])
    # own ATR14 (Wilder RMA seeded with SMA(14) of TR)
    pc = np.r_[np.nan, c[:-1]]; tr = np.maximum.reduce([h - l, np.abs(h - pc), np.abs(l - pc)]); tr[0] = h[0] - l[0]
    a = np.full(len(c), np.nan); a[13] = tr[:14].mean()
    for i in range(14, len(c)): a[i] = (a[i - 1] * 13 + tr[i]) / 14
    # own session starts: first bar of a VWAP reset (vwap == hlc3)
    hlc3 = (h + l + c) / 3; ds = np.zeros(len(c), bool); ds[0] = True
    ds[1:] = np.abs(v[1:] - hlc3[1:]) <= 1e-8 * np.maximum(1, np.abs(v[1:]))
    st = np.flatnonzero(ds); sess = np.cumsum(ds) - 1
    since = np.arange(len(c)) - st[sess]
    _D[sym] = dict(P=P, o=o, h=h, l=l, c=c, v=v, atr=a, ds=ds, st=st, sess=sess, since=since, T=P['T'])
    return _D[sym]
def impulses(D, disp=0.8, body=55, close=25, brk=10, wick=True, vslag=3):
    """sg[j] = +1 / -1 / 0 impulse by direction."""
    o, h, l, c, v, a, since = D['o'], D['h'], D['l'], D['c'], D['v'], D['atr'], D['since']
    n = len(c); rng = h - l
    pH = np.full(n, np.nan); pL = np.full(n, np.nan)
    w = swv(h, brk).max(axis=1); pH[brk:] = w[:n - brk]
    w = swv(l, brk).min(axis=1); pL[brk:] = w[:n - brk]
    big = (rng > 0) & (rng >= disp * a) & (np.abs(c - o) / np.where(rng > 0, rng, 1) * 100 >= body)
    up = big & (c > o) & ((h - c) / np.where(rng > 0, rng, 1) * 100 <= close) & ((h if wick else c) > pH)
    dn = big & (c < o) & ((c - l) / np.where(rng > 0, rng, 1) * 100 <= close) & ((l if wick else c) < pL)
    if vslag:
        sl = np.full(n, np.nan); sl[vslag:] = v[vslag:] - v[:-vslag]
        gate = since >= vslag
        up &= (~gate) | (sl > 0); dn &= (~gate) | (sl < 0)
    ok = np.arange(n) >= max(brk, 10) + 1
    up &= ok; dn &= ok
    return np.where(up, 1, np.where(dn, -1, 0))
def sess_nets(D, sg):
    ns = len(D['st']); net = np.zeros(ns, int)
    np.add.at(net, D['sess'], sg)
    return net
def is_tight(D, sg, net, i, d, NET=3):
    k = D['sess'][i]
    if k == 0: return False
    a = D['st'][k]
    if (sg[a:i] == d).any(): return False
    return d * net[k - 1] <= -NET
def stop_dist(D, i, d, entry, tight):
    A = D['atr'][i]
    if not tight: return 1.8 * A
    ext = D['l'][i] if d > 0 else D['h'][i]
    return max(0.9 * A, d * (entry - ext))
