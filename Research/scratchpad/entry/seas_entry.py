"""Seasonal entries alone: every bar in the window, market, stop 1.8 ATR: longs NY 13:00-16:59 / shorts NY 07:00-09:59.
Per-year excess (drift-neutral, vs random entries of the same direction that year) + the clock-shift placebo."""
import sys, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data, placebo, pickle
for tf in ('M15', 'M5'):
    b = kit.load(tf); n = b['n']; A = b['atr']; C = b['C']
    ok = ~np.isnan(A) & (b['utc_wd'] != 6) & (np.arange(n) > 60) & (np.arange(n) < n - 5)
    ny = kit.local_min(tf, 'ny')
    i = np.flatnonzero(ok); i = np.concatenate([i, i]); d = np.concatenate([np.ones(len(i) // 2), -np.ones(len(i) // 2)]).astype(int)
    keep = lambda m, dd: ((dd == 1) & (m >= 780) & (m < 1020)) | ((dd == -1) & (m >= 420) & (m < 600))
    print('== %s seasonal rule: long NY 13:00-16:59, short NY 07:00-09:59 (every bar)' % tf)
    pr = placebo.run(tf, i, d, C[i], C[i] - d * 1.8 * A[i], 1, 1, keep, shifts=range(2, 23, 2))
    # per-year excess of the kept bars (using the every-bar file: mfeL / mfeS)
    f = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb')); f = f[f.split != 'test']
    m_ = kit.local_min(tf, 'ny')[f.i.to_numpy()]; yr = np.where(f.year == 2025, 2025, f.year)
    def edge(x): return np.mean([(np.mean(x >= r - 1e-9)) * 100 for r in kit.TPR])
    for y in (2021, 2022, 2023, 2024, 2025):
        g = f[yr == y]; mm = m_[yr == y]
        L = g.mfeL.to_numpy(); Sx = g.mfeS.to_numpy()
        lw = (mm >= 780) & (mm < 1020); sw = (mm >= 420) & (mm < 600)
        print('   %d  long window excess %+5.2f (n %5d)   short window excess %+5.2f (n %5d)' % (y, edge(L[lw]) - edge(L), lw.sum(), edge(Sx[sw]) - edge(Sx), sw.sum()))
