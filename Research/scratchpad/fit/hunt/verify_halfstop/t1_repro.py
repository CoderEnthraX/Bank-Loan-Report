import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from own_impl import *
from tightdata import TRADES
import numpy as np
# sanity: own ATR / session starts vs shared
for s in SYMS:
    D = data(s); P = D['P']; A = np.array([np.nan if x is None else x for x in P[('atr', 14)]]) if ('atr',14) in P else None
    from engine import rma
    A = np.array([np.nan if x is None else x for x in rma(P['tr'], 14)])
    print(s, 'atr maxdiff', np.nanmax(np.abs(A - D['atr'])), 'daystart equal', (D['ds'] == np.array(P['daystart'])).all(), 'nsess', len(D['st']))
ok = 0; bad = []
cache = {}
for t in TRADES:
    D = data(t['sym']); sg = impulses(D); net = sess_nets(D, sg)
    i = t['arm_i']; tg = is_tight(D, sg, net, i, t['d'])
    dist = stop_dist(D, i, t['d'], t['entry'], tg)
    pred = dist / D['atr'][i] < 1.4
    if pred == t['tight']: ok += 1
    else: bad.append((t['sym'], t['fill'], t['tight']))
print('OWN stop classification', ok, '/', len(TRADES), bad)
