"""Author-style stop choices, static classification on 80 trades (pred tight = stop/ATR < 1.4):
 (a) structure: stop beyond N-bar swing (incl. disp bar) + buf, clamped to [0.9, 1.8] ATR
 (b) risk cap: if 1.8*ATR > cap (% of price) -> half stop; if 1.8 ATR in ticks > cap -> half
 (c) structure-if-nearer: if swing stop distance < 1.8 ATR use max(0.9 ATR, candle extreme) else 1.8"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
from tightdata import TRADES
def ev(fn):
    ok = 0; tp = fp = 0
    for t in TRADES:
        P = get(t['sym']); i = t['arm_i']; A = P[('atr', 14)][i]; d = t['d']
        dist = fn(P, i, d, t['entry'], A) / A
        pr = dist < 1.4
        ok += pr == t['tight']; tp += pr and t['tight']; fp += pr and not t['tight']
    return ok, tp, fp
res = []
for N in (1, 2, 3, 5, 8, 10, 15, 20):
    for buf in (0.0, 0.1, 0.25, 0.5):
        def fa(P, i, d, e, A, N=N, buf=buf):
            s0 = min(P['L'][i - N + 1:i + 1]) - buf * A if d > 0 else max(P['H'][i - N + 1:i + 1]) + buf * A
            return min(max(d * (e - s0), 0.9 * A), 1.8 * A)
        res.append(('swingclamp N=%d buf=%.2f' % (N, buf),) + ev(fa))
        for lim in (1.0, 1.2, 1.5, 1.8):
            def fc(P, i, d, e, A, N=N, buf=buf, lim=lim):
                s0 = min(P['L'][i - N + 1:i + 1]) - buf * A if d > 0 else max(P['H'][i - N + 1:i + 1]) + buf * A
                return 0.9 * A if d * (e - s0) < lim * A else 1.8 * A
            res.append(('swing-nearer N=%d buf=%.2f lim=%.1f' % (N, buf, lim),) + ev(fc))
for cap in (0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0):
    def fb(P, i, d, e, A, cap=cap): return 0.9 * A if 1.8 * A / P['C'][i] * 100 > cap else 1.8 * A
    def fb2(P, i, d, e, A, cap=cap): return 0.9 * A if 1.8 * A / P['C'][i] * 100 < cap else 1.8 * A
    res.append(('pctcap> %.2f%%' % cap,) + ev(fb)); res.append(('pctcap< %.2f%%' % cap,) + ev(fb2))
for tk in (50, 100, 200, 300, 500, 1000, 2000, 5000):
    def ft(P, i, d, e, A, tk=tk): return 0.9 * A if 1.8 * A / P['mt'] > tk else 1.8 * A
    res.append(('tickcap>%d' % tk,) + ev(ft))
res.sort(key=lambda x: -x[1])
for r in res[:15]: print(r)
print('baseline all-1.8: 72/80')
