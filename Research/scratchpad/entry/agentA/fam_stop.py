"""generic stop entries: (a) random bars, stop order at C -/+ k ATR; (b) N-bar low / high breakdown stop orders (Donchian), every bar sampled"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, numpy as np, pandas as pd
FAM = 'stopgen'
rng = np.random.default_rng(11)
for tf in sys.argv[1].split(','):
    b = lib.ctx(tf); H, L, C, A = b['H'], b['L'], b['C'], b['atr']; ok = b['ok'] & (b['ny_wd'] < 5) & (b['split'] != 'test')
    pool = np.flatnonzero(ok); i = np.sort(rng.choice(pool, 12000, replace=False)); a = A[i]
    for k in (0.3, 1.0):
        i2 = np.r_[i, i]; d2 = np.r_[np.ones(len(i)), -np.ones(len(i))].astype(int); a2 = np.r_[a, a]
        e = np.r_[C[i] + k * a, C[i] - k * a]
        lib.run(tf, i2, d2, e, e - d2 * 1.8 * a2, 2, window=4, name='random stop-entry C+-%.1fATR 1.8ATR' % k, family=FAM, K=1)
    for N in (6, 24):
        hh = pd.Series(H).rolling(N).max().to_numpy(); ll = pd.Series(L).rolling(N).min().to_numpy()
        i2 = np.r_[i, i]; d2 = np.r_[np.ones(len(i)), -np.ones(len(i))].astype(int); a2 = np.r_[a, a]
        e = np.r_[hh[i] + 0.05 * a, ll[i] - 0.05 * a]
        lib.run(tf, i2, d2, e, e - d2 * 1.8 * a2, 2, window=4, name='random-bar %d-bar hi/lo stop-entry 1.8ATR' % N, family=FAM, K=1)
