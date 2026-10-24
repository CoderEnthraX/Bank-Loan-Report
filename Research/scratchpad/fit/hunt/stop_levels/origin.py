"""'origin of the move' structure stop: stop = clamp(dist(entry, origin), 0.9A, 1.8A); count predicted tight vs actual over all 80"""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_levels')
from dispser import *
def origins(P, i, d):
    O,H,L,C,V = P['O'],P['H'],P['L'],P['C'],P['V']; sessions(P); s = P['sess'][i]; g = {}
    ext = (lambda a, b: min(L[a:b+1])) if d > 0 else (lambda a, b: max(H[a:b+1]))
    # a) run of same-colour bars ending at i
    j = i
    while j-1 >= 0 and d*(C[j-1]-O[j-1]) > 0: j -= 1
    g['run_col'] = ext(j, i)
    # a2) run allowing dojis
    j = i
    while j-1 >= 0 and d*(C[j-1]-O[j-1]) >= 0: j -= 1
    g['run_col0'] = ext(j, i)
    # b) run of closes on the trade side of VWAP
    j = i
    while j-1 >= s and V[j-1] is not None and d*(C[j-1]-V[j-1]) > 0: j -= 1
    g['run_vw'] = ext(max(j-1, s), i)
    g['run_vw_in'] = ext(j, i)
    # c) since last opposite displacement / last same displacement
    ds = dser(P)
    j = i-1
    while j > 0 and ds[j] != -d: j -= 1
    g['since_opp'] = ext(j, i)
    # d) run of higher lows (long) / lower highs (short)
    j = i
    while j-1 >= 0 and (L[j] > L[j-1] if d > 0 else H[j] < H[j-1]): j -= 1
    g['run_hl'] = ext(j, i)
    j = i
    while j-1 >= 0 and (C[j] > C[j-1] if d > 0 else C[j] < C[j-1]): j -= 1
    g['run_cc'] = ext(j, i)
    g['run_cc1'] = ext(max(j-1,0), i)
    # e) since the bar that made the broken 10-bar extreme
    w = list(range(i-10, i)); k = max(w, key=lambda x: H[x]) if d > 0 else min(w, key=lambda x: L[x])
    g['since_brk'] = ext(k, i)
    # f) consolidation broken: extreme of the 10 bars (opposite side)
    for N in (3, 5, 10, 20):
        g[f'box{N}'] = ext(i-N, i-1)
    return g
if __name__ == '__main__':
    import collections
    res = collections.defaultdict(lambda: [0, [], []])
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; A = P[('atr',14)][i]; d = t['d']; e = t['entry']
        for k, lvl in origins(P, i, d).items():
            for buf in (0.0, 0.1, 0.2):
                dist = d*(e-lvl)/A + buf
                for lo, hi in ((0.9, 1.8),):
                    pr = min(max(dist, lo), hi)
                    r = res[(k, buf)]
                    ok = abs(pr - t['stopR']) < 0.12
                    r[0] += ok
                    if not ok: (r[1] if t['tight'] else r[2]).append(f"{t['sym']} {t['arm']} pred {pr:.2f} act {t['stopR']:.2f}")
    for (k, buf), (ok, bt, bn) in sorted(res.items(), key=lambda kv: -kv[1][0]):
        print(f'{k:10s} buf {buf}: match {ok}/80  tight wrong {len(bt)}  normal wrong {len(bn)}  {bt[:3]}')
