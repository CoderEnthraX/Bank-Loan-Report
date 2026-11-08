import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentB')
import numpy as np, oflib as L, c3, kit
rng = np.random.default_rng(7)
def boot(tf, src='sig'):
    x, i, d, k = c3.c3_sig(tf, 80, gap=c3.GAP[tf], src=src)
    e, st, mode = L.orders(x, i, d, 'mkt', 'atr')
    o = kit.outcomes_of(tf, i, d, e, st, mode, 3); bl = kit.baseline(tf)
    sp = x['split'][i]; mo = (x['year'][i] * 12 + x['month'][i])
    hit = (o['mfe_m'][:, None] >= kit.TPR[None, :] - 1e-9) * 100.0
    for s in ('train', 'valid'):
        for dd, lab in ((1, 'L'), (-1, 'S'), (0, 'both')):
            m = (sp == s) & (o['fill_m1'] >= 0) & ((d == dd) if dd else True)
            ref = np.array([bl[(s, int(q))] for q in d[m]])
            ex = (hit[m] - ref).mean(1); mm = mo[m]; um = np.unique(mm)
            idx = {u: np.flatnonzero(mm == u) for u in um}
            bs = [np.mean(np.concatenate([ex[idx[u]] for u in rng.choice(um, len(um))])) for _ in range(2000)]
            print('%s %-5s %-6s %-4s n %5d avg excess %+5.2f  month-block se %.2f  z %.2f  P(<=0) %.4f' % (tf, src, s, lab, m.sum(), ex.mean(), np.std(bs), ex.mean() / np.std(bs), np.mean(np.array(bs) <= 0)))
boot('M5'); boot('M5', 'bar'); boot('H1')
