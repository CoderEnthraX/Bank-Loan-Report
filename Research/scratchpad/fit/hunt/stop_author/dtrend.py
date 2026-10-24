"""daily-trend (HTF) bias candidates: at snapshots (table BIAS) and at the 80 trades (first-of-session subset)."""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from dlib import *
from tightdata import TRADES
def ema(x, n):
    a = 2 / (n + 1); o = []; s = None
    for v in x: s = v if s is None else a * v + (1 - a) * s; o.append(s)
    return o
def dfe(P, i, merge=False):
    out, idx = sessions(P, merge); k = idx[i]
    C = [x['c'] for x in out[:k]]  # completed sessions
    dr = [x['h'] - x['l'] for x in out[max(0, k - 14):k]]; da = sum(dr) / len(dr)
    c = P['C'][i]
    f = {}
    for n in (5, 9, 10, 20):
        e = ema(C, n)[-1]; s = sum(C[-n:]) / n
        f[f'pc_e{n}'] = (C[-1] - e) / da; f[f'c_e{n}'] = (c - e) / da; f[f'pc_s{n}'] = (C[-1] - s) / da; f[f'c_s{n}'] = (c - s) / da
        Cl = C + [c]; f[f'cl_e{n}'] = (c - ema(Cl, n)[-1]) / da  # developing daily close incl. today
    f['e5_20'] = (ema(C, 5)[-1] - ema(C, 20)[-1]) / da; f['e9_20'] = (ema(C, 9)[-1] - ema(C, 20)[-1]) / da; f['s5_20'] = (sum(C[-5:]) / 5 - sum(C[-20:]) / 20) / da
    f['e9sl'] = (ema(C, 9)[-1] - ema(C, 9)[-2]) / da; f['e20sl'] = (ema(C, 20)[-1] - ema(C, 20)[-2]) / da
    f['c5'] = (C[-1] - C[-6]) / da; f['c3'] = (C[-1] - C[-4]) / da; f['c2'] = (C[-1] - C[-3]) / da
    return f
if __name__ == '__main__':
    SN = [('CRUDE','2026-10-09 13:40','BEAR'),('EURUSD','2026-10-12 12:50','BEAR'),('GC','2026-10-12 12:55','NEUT'),
          ('NASDAQ','2026-10-12 12:45','NEUT'),('NASDAQ','2026-10-09 13:40','NEUT'),('NIFTY','2026-10-12 12:40','BEAR'),
          ('SENSEX','2026-10-12 12:40','BEAR'),('US30','2026-10-12 12:50','NEUT?')]
    rows = []
    for s, t, b in SN:
        P = prepare(s); i = P['T'].index(t); rows.append((f'{s:6s} {t[5:]} {b:5s}', dfe(P, i)))
    ks = list(rows[0][1])
    for k in ks: print(f'{k:8s}', ' '.join(f'{r[1][k]:+6.2f}' for r in rows))
    print(' ' * 9 + ' '.join(r[0][:6] for r in rows))
