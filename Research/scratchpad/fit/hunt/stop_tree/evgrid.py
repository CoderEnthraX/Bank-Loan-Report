"""Grid over the EVENT definition used for 'first-of-session' and for prev-session net counts, x prev-against definition.
Errors over all 80 trades.  numpy per symbol."""
import sys, os, itertools, pickle, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from fbase import base
from pbank import sess_def
from tightdata import TRADES
SYMS = sorted(set(t['sym'] for t in TRADES))
PD = {}
for s in SYMS:
    P = base(s); n = len(P['C'])
    O, H, L, C = (np.array(P[k], float) for k in 'OHLC')
    V = np.array([v if v is not None else np.nan for v in P['V']])
    A = np.array([a if a is not None else np.nan for a in P[('atr', 14)]])
    ss = np.array(P['sinceStart'])
    PD[s] = dict(P=P, n=n, O=O, H=H, L=L, C=C, V=V, A=A, ss=ss)


def roll_ext(x, N, fn, sess_start=None):
    """prior-N-bar max/min (bars j-N..j-1); if sess_start given, restricted to bars >= session start (nan if none)"""
    n = len(x); out = np.full(n, np.nan)
    for j in range(1, n):
        a = max(0, j - N)
        if sess_start is not None: a = max(a, sess_start[j])
        if a < j: out[j] = fn(x[a:j])
    return out


CACHE = {}
def events(s, rng=0.8, body=55, clos=25, brk=10, brkmode='x', vsl=True, vw=False, mom=0.0):
    key = (s, rng, body, clos, brk, brkmode, vsl, vw, mom)
    if key in CACHE: return CACHE[key]
    D = PD[s]; O, H, L, C, V, A, ss = D['O'], D['H'], D['L'], D['C'], D['V'], D['A'], D['ss']
    n = D['n']; r = H - L; bd = np.abs(C - O)
    with np.errstate(invalid='ignore', divide='ignore'):
        base_ok = (r > 0) & (r >= rng * A) & (bd / np.where(r > 0, r, 1) * 100 >= body) & ~np.isnan(A)
        base_ok[:11] = False
        out = np.zeros(n, int)
        for d in (1, -1):
            ok = base_ok & (d * (C - O) > 0)
            ok &= (((H - C) if d > 0 else (C - L)) / np.where(r > 0, r, 1) * 100 <= clos)
            if brk:
                kk = ('ext', s, brk, brkmode, d)
                if kk not in CACHE:
                    st = (np.arange(n) - ss) if brkmode == 's' else None
                    CACHE[kk] = roll_ext(H if d > 0 else L, brk, np.max if d > 0 else np.min, st)
                ext = CACHE[kk]
                cond = (C > ext) if d > 0 else (C < ext)
                if brkmode == 's': cond = np.where(np.isnan(ext), True, cond)   # first bar of session: no prior session bars
                ok &= cond
            if vsl:
                Vl = np.concatenate([np.full(3, np.nan), V[:-3]])
                ok &= (ss < 3) | (d * (V - Vl) > 0)
            if vw: ok &= d * (C - V) > 0
            if mom:
                Cl = np.concatenate([np.full(10, np.nan), C[:-10]])
                ok &= d * (C - Cl) >= mom * A
            out[ok & (out == 0)] = d
    CACHE[key] = out; return out


def trade_feats(t, ev, sdef='R'):
    s = t['sym']; D = PD[s]; P = D['P']; i = t['arm_i']; d = t['d']
    S, idx = sess_def(P, sdef); k = idx[i]; a = S[k][0]
    first = not np.any(ev[a:i] == d)
    if k < 1: return first, np.nan, np.nan, np.nan, np.nan
    pa, pb = S[k - 1]; A = D['A'][i]
    body = d * (D['C'][pb - 1] - D['O'][pa]) / A
    net = d * ev[pa:pb].sum()
    gap = d * (D['O'][a] - D['C'][pb - 1]) / A
    ph, pl = D['H'][pa:pb].max(), D['L'][pa:pb].min()
    oloc = ((D['O'][a] - pl) / (ph - pl)) if d > 0 else ((ph - D['O'][a]) / (ph - pl))
    return first, body, net, gap, oloc


if __name__ == '__main__':
    y = np.array([t['tight'] for t in TRADES])
    GRID = dict(rng=[0.0, 0.5, 0.8, 1.0], body=[0, 50, 55, 60], clos=[100, 25, 30], brk=[0, 3, 5, 10, 20],
                brkmode=['x', 's'], vsl=[True, False], vw=[False, True], mom=[0.0, 0.85])
    res = []
    keys = list(GRID)
    for combo in itertools.product(*GRID.values()):
        cfg = dict(zip(keys, combo))
        if cfg['brk'] == 0 and cfg['brkmode'] == 's': continue
        for sdef in ('R', 'M'):
            rows = [trade_feats(t, events(t['sym'], **cfg), sdef) for t in TRADES]
            F = np.array([r[0] for r in rows]); body = np.array([r[1] for r in rows]); net = np.array([r[2] for r in rows])
            gap = np.array([r[3] for r in rows]); oloc = np.array([r[4] for r in rows])
            nf = int(F.sum()); ft = int((F & y).sum())
            for nm, cond in (('body<-1', body < -1), ('body<0', body < 0), ('net<=-1', net <= -1), ('net<=-2', net <= -2), ('net<=-3', net <= -3), ('net<=-4', net <= -4),
                             ('body<-1&gap>-1', (body < -1) & (gap > -1)), ('net<=-2&gap>-1', (net <= -2) & (gap > -1)), ('net<=-3&gap>-1', (net <= -3) & (gap > -1)),
                             ('body<-1&oloc>0', (body < -1) & (oloc > 0)), ('net<=-2&oloc>0', (net <= -2) & (oloc > 0)), ('net<=-3&oloc>0', (net <= -3) & (oloc > 0))):
                pred = F & np.nan_to_num(cond, nan=0).astype(bool)
                tp = int((pred & y).sum()); fp = int((pred & ~y).sum())
                res.append((8 - tp + fp, tp, fp, nf, ft, sdef, nm, cfg))
    res.sort(key=lambda r: (r[0], -r[1]))
    pickle.dump(res, open(os.path.join(HERE, 'evgrid.pkl'), 'wb'))
    import collections
    print('error histogram', sorted(collections.Counter(r[0] for r in res).items()))
    for r in res[:60]: print(r)
