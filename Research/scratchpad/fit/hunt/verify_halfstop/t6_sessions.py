import sys, os
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from own_impl import *
from tightdata import TRADES
tiny = []
for s in SYMS:
    D = data(s); st = list(D['st']) + [len(D['c'])]
    for k in range(len(st) - 1):
        L = st[k + 1] - st[k]
        if L < 20: tiny.append((s, D['T'][st[k]], L))
print('sessions with <20 bars:', tiny)
# prev-session length / current-session position for the 8 tight and 14 non-tight first-impulse trades
for t in TRADES:
    D = data(t['sym']); k = D['sess'][t['arm_i']]
    if k == 0: print('trade in session 0', t['sym'], t['fill'])
    pl = D['st'][k] - D['st'][k - 1]
    if pl < 40: print('short prev session', t['sym'], t['fill'], pl, t['tight'])
print('tight trades: bars since session start at arm:', [(t['sym'], int(data(t['sym'])['since'][t['arm_i']])) for t in TRADES if t['tight']])
