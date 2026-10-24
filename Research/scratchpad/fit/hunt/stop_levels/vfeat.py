import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from lv import *
def vfeat(P, i, d, entry, A):
    recover(P['sym']); sessions(P)
    vol = P['vol']; s = P['sess'][i]; g = {}
    v = vol[i] if vol[i] is not None else 0
    prev = [x for x in vol[s:i] if x is not None]
    for N in (1, 2, 3, 5, 10, 20, 50):
        pv = prev[-N:]
        if pv and sum(pv) > 0: g[f'rv{N}'] = v / (sum(pv)/len(pv))
    sp = [x for x in vol[s:i+1] if x is not None]
    if sp: g['rvsess'] = v / (sum(sp)/len(sp)); g['vshare'] = v / sum(sp)
    g['vwapjump'] = d*(P['V'][i]-P['V'][i-1])/A
    g['since'] = P['sinceStart'][i]
    return g
if __name__ == '__main__':
    rows = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]
        rows.append((t, vfeat(P, i, t['d'], t['entry'], A)))
    keys = sorted({k for _, x in rows for k in x})
    for k in keys:
        vals = sorted([(x.get(k), t['tight'], t) for t, x in rows if x.get(k) is not None], key=lambda r: r[0])
        print(k, ' '.join(('T' if tg else '.') for _, tg, _ in vals))
        print('   tight vals', [round(v, 2) for v, tg, _ in vals if tg], 'n', len(vals))
