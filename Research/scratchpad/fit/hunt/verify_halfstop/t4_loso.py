import sys, os, pickle
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from t5_grid import *
res = pickle.load(open(os.path.join(H, 'grid.pkl'), 'rb'))
symarr = np.array(syms)
CL = (0.8, 55, 25, 10, True, 3)
def perr(f, dp, NET): return ((f & (dp <= -NET) & ok_dist) != lab)   # per-trade error vector
# per-symbol facts
print('sym  n_trades n_tight  errors(claimed NET3)')
for s in SYMS:
    m = symarr == s; e = perr(res[CL]['f'], res[CL]['dp'], 3)
    print(f'{s:7s} {m.sum():3d} {lab[m].sum():3d}  {e[m].sum()}')
# (b) drop-one: NET plateau on the other 7 symbols (claimed impulse def)
print('drop-one-symbol NET plateau (claimed impulse def): errors on remaining trades for NET 1..7')
f, dp = res[CL]['f'], res[CL]['dp']
for s in SYMS:
    m = symarr != s
    print(f'  drop {s:7s}', [int(perr(f, dp, N)[m].sum()) for N in range(1, 8)])
# (c) held-out fit: choose params on 7 symbols by classification, test on held-out
print('held-out fit over grid x NET1..6 (30000 rules): train-optimal set -> held-out errors')
tot_tie_mean = 0; tot_claimed = 0; tot_rand = 0
for s in SYMS:
    m = symarr != s; best = -1; cands = []
    for v, r in res.items():
        for N in range(1, 7):
            e = perr(r['f'], r['dp'], N); tr_e = int(e[m].sum()); te_e = int(e[~m].sum())
            if best < 0 or tr_e < best: best = tr_e; cands = []
            if tr_e == best: cands.append((v, N, te_e))
    te = np.array([c[2] for c in cands])
    cl_e = int(perr(f, dp, 3)[~m].sum()); cl_tr = int(perr(f, dp, 3)[m].sum())
    inclaimed = any(c[0] == CL and c[1] == 3 for c in cands)
    print(f'  hold out {s:7s}: train-min errors {best} (claimed rule train errors {cl_tr}) n_opt_configs {len(cands)}  held-out errors min/mean/max {te.min()}/{te.mean():.2f}/{te.max()} ; held-out trades {int((~m).sum())}, claimed held-out errors {cl_e}')
    tot_rand += te.mean(); tot_claimed += cl_e
print('sum over held-out symbols of expected errors for train-selected rule:', round(tot_rand, 2), '/80 ; claimed rule:', tot_claimed)
