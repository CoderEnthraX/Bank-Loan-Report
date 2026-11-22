"""Alternative selection: z-score of the 2021-23 edge (A + B pooled), requiring a positive edge in both A and B and >= nmin train trades;
then the test edges of the top-k. Run: python3 -I selz.py TF [nmin]"""
import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr')
import analyze as A
tf = int(sys.argv[1]); nmin = int(sys.argv[2]) if len(sys.argv) > 2 else 150
res = A.load(tf)
for X in (0.5, 1.0, 1.5):
    rnd = 1 / (1 + X)
    zs = []; te = []
    for kw, lv, fl, post, m in res:
        na, nb = m['A_n_%g' % X], m['B_n_%g' % X]
        if na + nb < nmin or na == 0 or nb == 0:
            zs.append(-9); te.append(np.nan); continue
        acc = (m['A_acc_%g' % X] * na + m['B_acc_%g' % X] * nb) / (na + nb)
        z = (acc - rnd) / np.sqrt(rnd * (1 - rnd) / (na + nb))
        ok = m['A_acc_%g' % X] > rnd and m['B_acc_%g' % X] > rnd
        zs.append(z if ok else -9)
        te.append(m['T_acc_%g' % X] - rnd if m['T_n_%g' % X] >= 30 else np.nan)
    zs = np.array(zs); te = np.array(te); o = np.argsort(-zs)
    el = zs > -9
    print('TF %d X %.1f: eligible %d, all-eligible mean test edge %+.2f | top10 %+.2f (%.0f%% >0) top50 %+.2f top200 %+.2f | best z %.2f' % (
        tf, X, el.sum(), 100 * np.nanmean(te[el]), 100 * np.nanmean(te[o[:10]]), 100 * np.nanmean(te[o[:10]] > 0), 100 * np.nanmean(te[o[:50]]), 100 * np.nanmean(te[o[:200]]), zs[o[0]]))
