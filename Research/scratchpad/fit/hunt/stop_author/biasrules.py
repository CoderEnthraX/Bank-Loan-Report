"""Static evaluation of author-style BIAS rules on the 80 trades: tight iff counter-bias (bias == -d) or not-with-bias (bias != d)."""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
from tightdata import TRADES
rows = pickle.load(open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author/tfeat.pkl', 'rb'))
def sgn(x, th): return 1 if x > th else (-1 if x < -th else 0)
res = []
for m in (30, 60, 120, 240):
    for hk in ('dspr', 'de2050', 'dce20', 'ders', 'ddir'):
        for hth in (0, 2, 5, 10) if hk == 'dspr' else ((0, 0.25, 0.5, 1) if hk != 'ddir' else (0,)):
            for lk in ('d_spr', 'd_cv', 'd_e2050', 'none'):
                for lth in ((0, 4, 5) if lk == 'd_spr' else (0,)):
                    for mode in ('against', 'notwith', 'htfagainst_ltfwith'):
                        tp = fp = 0
                        for r in rows:
                            h = r.get(f'h{m}_{hk}')
                            if h is None: continue
                            hs = sgn(h, hth); ls = 1 if lk == 'none' else sgn(r[lk], lth)   # in trade direction units
                            bias = hs if (lk == 'none' or hs == ls) else 0               # +1 = with trade, -1 = against
                            if mode == 'against': pred = bias == -1
                            elif mode == 'notwith': pred = bias != 1
                            else: pred = hs == -1 and ls == 1
                            if pred and r['tight']: tp += 1
                            elif pred: fp += 1
                        res.append((8 - tp + fp, tp, fp, m, hk, hth, lk, lth, mode))
res.sort()
for x in res[:25]: print(x)
