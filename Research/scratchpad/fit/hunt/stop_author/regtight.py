"""Regime label (RANGING = CHOP14>=61.8; TRENDING = ADX>=t [& 240m ADX>=h]; else TRANSITION) at displacement bar / bar before / fill bar vs tight."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
from tightdata import TRADES
from collections import Counter
def lab(P, i, t, h, rc=61.8):
    f = feats(P, i)
    if f['chop14'] >= rc: return 'R'
    if f['adx'] >= t and (h is None or htf_series(P, 240)[i]['adx'] >= h): return 'T'
    return 'X'
for where in ('arm', 'arm-1', 'fill'):
    for t, h in ((20, None), (25, None), (30, None), (25, 35), (20, 30)):
        c = Counter()
        for tr in TRADES:
            P = get(tr['sym']); i = tr['arm_i'] if where == 'arm' else (tr['arm_i'] - 1 if where == 'arm-1' else P['T'].index(tr['fill']))
            c[(lab(P, i, t, h), tr['tight'])] += 1
        print(where, 'ADX>=', t, '240mADX>=', h, ' '.join(f"{L}: {c[(L,True)]}T/{c[(L,False)]}N" for L in 'RXT'))
