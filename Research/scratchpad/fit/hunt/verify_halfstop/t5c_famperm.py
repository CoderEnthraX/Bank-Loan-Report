import sys, os, itertools, time
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from t5_grid import *
rng = np.random.default_rng(777)
PERMS = 1000
idx = {}
for s in SYMS:
    K = len(data(s)['st']); idx[s] = np.argsort(rng.random((PERMS, K - 1)), axis=1)
keys = list(GRID); N = len(TRADES)
best_all = np.zeros(PERMS, int); best_net3 = np.zeros(PERMS, int); claimed = None
sym_arr = np.array(syms)
t0 = time.time()
for vals in itertools.product(*GRID.values()):
    cfg = dict(zip(keys, vals)); f, dp, nets = trade_feats(cfg)
    dpp = np.zeros((PERMS, N), int)
    for n, t in enumerate(TRADES):
        k = ks[n]
        if k > 0: dpp[:, n] = t['d'] * nets[t['sym']][:len(nets[t['sym']]) - 1][idx[t['sym']][:, k - 1]]
    base = f & ok_dist
    for NET in range(1, 7):
        sc = ((base[None, :] & (dpp <= -NET)) == lab[None, :]).sum(1)
        best_all = np.maximum(best_all, sc)
        if NET == 3: best_net3 = np.maximum(best_net3, sc)
        if vals == (0.8, 55, 25, 10, True, 3) and NET == 3: claimed = sc
print('time', round(time.time() - t0))
for nm, a in [('claimed config only (NET3)', claimed), ('max over 5000 impulse configs @NET=3', best_net3), ('max over 5000 configs x NET1..6 (30000)', best_all)]:
    print(f'{nm}: mean {a.mean():.1f} median {np.median(a):.0f} max {a.max()}  P(>=80)={np.mean(a>=80):.3f} P(>=79)={np.mean(a>=79):.3f} P(>=78)={np.mean(a>=78):.3f} P(>=77)={np.mean(a>=77):.3f}  (obs 80)')
