"""candidate B sensitivity: previous-day high/low sweep (bar H > PDH, C < PDH -> short; mirror long), confirmation stop entry through the
sweep bar's other extreme within W bars, stop beyond the sweep extreme"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, pandas as pd
from fam_sweep import prev_day_hl
lib.OUT = lib.A + '/rows_cand.jsonl'

def sigs(tf, t0=0, t1=1440, first=True, depth=0.0):
    b = lib.ctx(tf); H, L, C = b['H'], b['L'], b['C']; A = b['atr']; nm = b['ny_min']
    pdh, pdl = prev_day_hl(b)
    win = (b['ny_wd'] < 5) & (((nm >= t0) & (nm < t1)) if t0 < t1 else ((nm >= t0) | (nm < t1))) & b['ok']
    S = win & ~np.isnan(pdh) & (H > pdh + depth * A) & (C < pdh)
    Lg = win & ~np.isnan(pdl) & (L < pdl - depth * A) & (C > pdl)
    if first: is_ = lib.first_per_day(b, S); il = lib.first_per_day(b, Lg)
    else: is_ = lib.decluster(np.flatnonzero(S), 60 // b['tfmin']); il = lib.decluster(np.flatnonzero(Lg), 60 // b['tfmin'])
    i = np.r_[il, is_]; d = np.r_[np.ones(len(il)), -np.ones(len(is_))].astype(int)
    return b, i, d

def go(tf, tag, t0=0, t1=1440, first=True, depth=0.0, W=3, buf=0.05, sbuf=0.1, stop='ext', k=1.8, entry='stop'):
    b, i, d = sigs(tf, t0, t1, first, depth); H, L, C, A = b['H'], b['L'], b['C'], b['atr']; a = A[i]
    ext = np.where(d == 1, L[i], H[i])
    e = np.where(d == 1, H[i] + buf * a, L[i] - buf * a) if entry == 'stop' else C[i]
    if stop == 'ext': st = np.where(d == 1, np.minimum(ext - sbuf * a, e - 0.5 * a), np.maximum(ext + sbuf * a, e + 0.5 * a))
    else: st = e - d * k * a
    name = 'B %s %02d-%02d %s depth%.1f W%d buf%.2f %s %s' % (tag, t0 // 60, t1 // 60, 'first' if first else 'all', depth, W, buf,
                                                           ('ext+%.1f' % sbuf) if stop == 'ext' else '%.1fATR' % k, entry)
    return lib.run(tf, i, d, e, st, 2 if entry == 'stop' else 1, window=W, name=name, family='candB')

if __name__ == '__main__':
    for tf in sys.argv[1].split(','):
        go(tf, 'base')
        for W in (1, 6): go(tf, 'W', W=W)
        go(tf, 'buf', buf=0.25)
        go(tf, 'sbuf', sbuf=0.4)
        go(tf, 'atrstop', stop='atr')
        go(tf, 'atrstop3', stop='atr', k=3.0)
        go(tf, 'all', first=False)
        go(tf, 'depth', depth=0.3)
        go(tf, 'time', t0=180, t1=720)
        go(tf, 'time', t0=720, t1=1020)
        go(tf, 'time', t0=1080, t1=180)
