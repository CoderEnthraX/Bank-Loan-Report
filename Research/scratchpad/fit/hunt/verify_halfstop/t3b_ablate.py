import sys, os
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from own_impl import *
from tightdata import TRADES
from engine import rma
for s in SYMS: data(s)['P'].setdefault(('atr', 14), rma(data(s)['P']['tr'], 14))
def classify(fn):
    ok = 0
    for t in TRADES:
        D = data(t['sym']); sg = impulses(D); net = sess_nets(D, sg); i = t['arm_i']; d = t['d']; k = D['sess'][i]
        tg = fn(D, sg, net, i, d, k) if k > 0 else False
        pred = stop_dist(D, i, d, t['entry'], tg) / D['atr'][i] < 1.4
        ok += pred == t['tight']
    return ok
first_dir = lambda D, sg, i, d, k: not (sg[D['st'][k]:i] == d).any()
first_any = lambda D, sg, i, d, k: not (sg[D['st'][k]:i] != 0).any()
V = {
 'claimed (first same-dir, d*prev<=-3)': lambda D, sg, net, i, d, k: first_dir(D, sg, i, d, k) and d * net[k - 1] <= -3,
 'no first-impulse requirement': lambda D, sg, net, i, d, k: d * net[k - 1] <= -3,
 'no prevNet requirement (first same-dir only)': lambda D, sg, net, i, d, k: first_dir(D, sg, i, d, k),
 'first = first impulse in any direction': lambda D, sg, net, i, d, k: first_any(D, sg, i, d, k) and d * net[k - 1] <= -3,
 'sign flipped (d*prev>=+3)': lambda D, sg, net, i, d, k: first_dir(D, sg, i, d, k) and d * net[k - 1] >= 3,
 'prev net of 2 sessions ago': lambda D, sg, net, i, d, k: first_dir(D, sg, i, d, k) and k > 1 and d * net[k - 2] <= -3,
 'current-session net so far (not prev)': lambda D, sg, net, i, d, k: first_dir(D, sg, i, d, k) and d * sg[D['st'][k]:i].sum() <= -3,
 'never tight': lambda D, sg, net, i, d, k: False,
}
for n, f in V.items(): print(f'{classify(f)}/80  {n}')
