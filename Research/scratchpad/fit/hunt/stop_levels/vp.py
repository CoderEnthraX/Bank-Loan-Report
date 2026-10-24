"""Market-profile levels: prior-session and developing TPO / volume POC, VAH, VAL (70%), prior-session VWAP close."""
import sys, itertools; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
def profile(P, a, b, A, wvol):
    """bars a..b-1; bins of width A/4; each bar spreads weight uniformly over its range"""
    H, L = P['H'], P['L']; lo = min(L[a:b]); hi = max(H[a:b]); w = max(A/4, 1e-12)
    nb = int((hi-lo)/w)+1; prof = [0.0]*nb
    for j in range(a, b):
        k0 = int((L[j]-lo)/w); k1 = int((H[j]-lo)/w); wt = (P['vol'][j] or 0) if wvol else 1.0
        for k in range(k0, k1+1): prof[k] += wt/(k1-k0+1)
    poc = max(range(nb), key=lambda k: prof[k]); tot = sum(prof); lo_k = hi_k = poc; acc = prof[poc]
    while acc < 0.7*tot and (lo_k > 0 or hi_k < nb-1):
        up = prof[hi_k+1] if hi_k < nb-1 else -1; dn = prof[lo_k-1] if lo_k > 0 else -1
        if up >= dn: hi_k += 1; acc += up
        else: lo_k -= 1; acc += dn
    c = lambda k: lo + (k+0.5)*w
    return c(poc), c(hi_k)+w/2, c(lo_k)-w/2
def vpfeat(P, i, d, entry, A):
    sessions(P); recover(P['sym']); s = P['sess'][i]; st = P['starts']; k = st.index(s); g = {}
    nx = lambda v: d*(v-entry)/A
    if k > 0:
        a = st[k-1]
        for wv in (0, 1):
            poc, vah, val = profile(P, a, s, A, wv); t = 'v' if wv else 't'
            g[f'p{t}poc'] = nx(poc); g[f'p{t}vaf'] = nx(vah if d > 0 else val); g[f'p{t}vaa'] = nx(val if d > 0 else vah)
        g['pvwap'] = nx(P['V'][s-1])
    if i - s >= 3:
        for wv in (0, 1):
            poc, vah, val = profile(P, s, i, A, wv); t = 'v' if wv else 't'
            g[f'd{t}poc'] = nx(poc); g[f'd{t}vaf'] = nx(vah if d > 0 else val); g[f'd{t}vaa'] = nx(val if d > 0 else vah)
    return g
if __name__ == '__main__':
    rows = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
        rows.append((t, vpfeat(P, i, t['d'], t['entry'], A)))
    keys = sorted({k for _, x in rows for k in x}); res = []
    for k in keys:
        vals = [(x.get(k), t['tight']) for t, x in rows if x.get(k) is not None]
        vs = sorted(set(v for v, _ in vals)); cuts = [-1e9] + [(a+b)/2 for a, b in zip(vs, vs[1:])] + [1e9]
        best = None
        for a, b in itertools.combinations(cuts, 2):
            tp = sum(1 for v, tg in vals if tg and a < v < b); fp = sum(1 for v, tg in vals if not tg and a < v < b)
            if best is None or tp - fp > best[0]: best = (tp - fp, tp, fp, a, b)
        z = {zn: (sum(1 for v, tg in vals if tg and a < v < b), sum(1 for v, tg in vals if not tg and a < v < b)) for zn, (a, b) in {'stop18': (-1.8, 0), 'tgt36': (0, 3.6)}.items()}
        ntt = sum(1 for v, tg in vals if tg)
        print(f'   {k:8s} n={len(vals)} (tight {ntt}) best {best[1]}/{ntt} tight, {best[2]} normal in ({best[3]:.2f},{best[4]:.2f})  zones(tight,normal) {z}')
    for t, x in rows:
        if t['sym'] in ('NIFTY','SENSEX') and t['arm'].startswith('2026-10-09 10'): print(t['sym'], {k: round(v, 2) for k, v in x.items()})
