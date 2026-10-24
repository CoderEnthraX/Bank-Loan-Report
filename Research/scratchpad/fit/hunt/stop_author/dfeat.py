"""daily-context features for all 80 trades; search single thresholds within the first-of-session subset."""
import sys, pickle
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from dlib import *
from tightdata import TRADES
def ema(x, n):
    a = 2 / (n + 1); o = []; s = None
    for v in x: s = v if s is None else a * v + (1 - a) * s; o.append(s)
    return o
rowsout = []
for t in TRADES:
    P = prepare(t['sym']); P.setdefault(('atr', 14), rma(P['tr'], 14)); i = t['arm_i']; d = t['d']; A = P[('atr', 14)][i]
    f = dict(sym=t['sym'], fill=t['fill'], d=d, tight=t['tight'])
    for m in (False, True):
        out, idx = sessions(P, m); k = idx[i]; s0, s1, s2, s3 = out[k], out[k - 1], out[k - 2], out[k - 3]
        tg = 'M' if m else 'U'
        dr = [x['h'] - x['l'] for x in out[:k]]; datr = sum(dr[-14:]) / len(dr[-14:])
        dtr = [max(out[j]['h'] - out[j]['l'], abs(out[j]['h'] - out[j - 1]['c']), abs(out[j]['l'] - out[j - 1]['c'])) for j in range(1, k)]
        datr2 = rma(dtr, 14)[-1] if len(dtr) >= 14 else None
        C = [x['c'] for x in out[:k]]
        e9, e20 = ema(C, 9), ema(C, 20); sma20 = sum(C[-20:]) / 20; sma5 = sum(C[-5:]) / 5
        r1 = s1['h'] - s1['l']
        # prev session final vwap
        pv = P['V'][s1['b'] - 1]
        c = P['C'][i]; hi = max(P['H'][s0['a']:i + 1]); lo = min(P['L'][s0['a']:i + 1])
        g = {
            'pdb': d * (s1['c'] - s1['o']) / A, 'pdbR': d * (s1['c'] - s1['o']) / r1, 'pdbD': d * (s1['c'] - s1['o']) / datr,
            'pdc2c': d * (s1['c'] - s2['c']) / A, 'pdc2cD': d * (s1['c'] - s2['c']) / datr,
            'pdclv': d * (2 * s1['c'] - s1['h'] - s1['l']) / r1, 'pdcv': d * (s1['c'] - pv) / A,
            'ppdb': d * (s2['c'] - s2['o']) / A, 'ppdc2c': d * (s2['c'] - s3['c']) / A, 'two': d * (s1['c'] - s2['o']) / A,
            'gap': d * (s0['o'] - s1['c']) / A, 'opd_o': d * (s0['o'] - s1['o']) / A, 'opos': d * (2 * s0['o'] - s1['h'] - s1['l']) / r1,
            'c_pdc': d * (c - s1['c']) / A, 'c_pdo': d * (c - s1['o']) / A, 'c_pdm': d * (2 * c - s1['h'] - s1['l']) / r1,
            'c_pdh': (c - s1['h']) / A if d > 0 else (s1['l'] - c) / A, 'c_pdl': (c - s1['l']) / A if d > 0 else (s1['h'] - c) / A,
            'c_open': d * (c - s0['o']) / A, 'brkPD': int((hi > s1['h']) if d > 0 else (lo < s1['l'])), 'brkPDo': int((lo < s1['l']) if d > 0 else (hi > s1['h'])),
            'pdc_e9': d * (s1['c'] - e9[-1]) / datr, 'pdc_e20': d * (s1['c'] - e20[-1]) / datr, 'pdc_s20': d * (s1['c'] - sma20) / datr, 'pdc_s5': d * (s1['c'] - sma5) / datr,
            'e9_20': d * (e9[-1] - e20[-1]) / datr, 'c_e20': d * (c - e20[-1]) / datr, 'c_s20': d * (c - sma20) / datr,
            'pdbD2': d * (s1['c'] - s1['o']) / datr2 if datr2 else 0, 'pdrA': r1 / A, 'pdrD': r1 / datr,
            'ss': i - s0['a'], 'pdlen': s1['b'] - s1['a'],
        }
        for kk, v in g.items(): f[tg + '_' + kk] = v
    for ex, nm in ((('vsl',), 'C'), (('vsl', 'vw', 'mom'), 'E'), ((), 'K'), (('vsl', 'vw'), 'W')):
        for m in (False, True):
            f[f'np{nm}{"M" if m else "U"}'] = nprior(P, i, d, m, ex)
    rowsout.append(f)
pickle.dump(rowsout, open(sys.argv[0].replace('.py', '.pkl'), 'wb'))
