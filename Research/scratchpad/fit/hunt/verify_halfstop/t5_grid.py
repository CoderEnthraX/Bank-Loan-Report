import sys, os, itertools, pickle, time
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from own_impl import *
from tightdata import TRADES
from engine import rma
for s in SYMS: data(s)['P'].setdefault(('atr', 14), rma(data(s)['P']['tr'], 14))
GRID = dict(disp=[0.6, 0.7, 0.8, 0.9, 1.0], body=[45, 50, 55, 60, 65], close=[15, 20, 25, 30, 35], brk=[6, 8, 10, 12, 14], wick=[True, False], vslag=[0, 2, 3, 4])
BASE = dict(disp=0.8, body=55, close=25, brk=10, wick=True, vslag=3)
tdA = {}; lab = np.array([t['tight'] for t in TRADES]); dirs = np.array([t['d'] for t in TRADES])
ok_dist = np.array([stop_dist(data(t['sym']), t['arm_i'], t['d'], t['entry'], True) / data(t['sym'])['atr'][t['arm_i']] < 1.4 for t in TRADES])
ks = np.array([data(t['sym'])['sess'][t['arm_i']] for t in TRADES]); syms = [t['sym'] for t in TRADES]
def trade_feats(cfg):
    """per trade: first flag, d*prevNet ; plus per-symbol net vectors"""
    f = np.zeros(len(TRADES), bool); dp = np.zeros(len(TRADES), int); nets = {}
    for s in SYMS:
        D = data(s); sg = impulses(D, **cfg); nets[s] = sess_nets(D, sg); D['_sg'] = sg
    for n, t in enumerate(TRADES):
        D = data(t['sym']); sg = D['_sg']; i = t['arm_i']; k = ks[n]; d = t['d']
        f[n] = k > 0 and not (sg[D['st'][k]:i] == d).any()
        dp[n] = d * nets[t['sym']][k - 1] if k > 0 else 0
    return f, dp, nets
def score_net(f, dp, NET): return int(((f & (dp <= -NET) & ok_dist) == lab).sum())
if __name__ == '__main__':
    keys = list(GRID); res = {}
    t0 = time.time()
    for vals in itertools.product(*GRID.values()):
        cfg = dict(zip(keys, vals)); f, dp, nets = trade_feats(cfg)
        res[vals] = dict(f=f, dp=dp, sc={N: score_net(f, dp, N) for N in range(1, 7)})
    print('grid configs', len(res), 'time', round(time.time() - t0, 1))
    pickle.dump(res, open(os.path.join(H, 'grid.pkl'), 'wb'))
