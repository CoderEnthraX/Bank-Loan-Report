"""The 80 original trades with their displacement (arm) bar and stop type. TRADES: list of dicts
sym, fill (IST), arm (IST), arm_i (bar index), fill_i, d (+1/-1), entry, stop (measured), stopR (stop distance / ATR14 at arm),
tight (True for the 8 trades whose stop is ~0.9 ATR instead of 1.8 ATR), exit, out ('tp4'|'stop'|'open')."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt
from engine2 import prepare
from engine import rma
tr, _ = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
TRADES = []
for t in sorted(tr, key=lambda t: (t['sym'], t['fill'])):
    P = prepare(t['sym']); T = P['T']; O, H, L, C = P['O'], P['H'], P['L'], P['C']
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    A = P[('atr', 14)]
    if t['fill'] not in T or not t['entry'] or not t['stop']: continue
    fi = T.index(t['fill']); d = t['d']; best = None
    for k in range(1, 10):
        j = fi - k; mid = (O[j] + C[j]) / 2
        lv = max(H[j - 6:j]) if d > 0 else min(L[j - 6:j]); e = max(mid, lv) if d > 0 else min(mid, lv)
        brk = C[j] > max(H[j - 10:j]) if d > 0 else C[j] < min(L[j - 10:j])
        sc = abs(e - t['entry']) / A[j] + (0 if brk else 0.5) + 0.01 * k
        if best is None or sc < best[0]: best = (sc, j)
    j = best[1]; sr = d * (t['entry'] - t['stop']) / A[j]
    TRADES.append(dict(sym=t['sym'], fill=t['fill'], arm=T[j], arm_i=j, fill_i=fi, d=d, entry=t['entry'], stop=t['stop'], stopR=sr,
                       tight=sr < 1.4, exit=t['exit'], out=t['out']))
if __name__ == '__main__':
    for t in TRADES: print(t['sym'], t['fill'], t['arm'], t['d'], 'TIGHT' if t['tight'] else '     ', round(t['stopR'], 2), t['out'])
    print(len(TRADES), 'trades,', sum(t['tight'] for t in TRADES), 'tight')
