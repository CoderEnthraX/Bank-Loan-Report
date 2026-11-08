import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentA')
import lib, kit, numpy as np, candA, candB
rng = np.random.default_rng(3)
def boot(tag, tf, i, d, e, st, mode, win, B=2000):
    b = lib.ctx(tf); o = kit.outcomes_of(tf, i, d, e, st, mode, win); f = o['fill_m1'] >= 0; bl = kit.baseline(tf)
    sp = b['split'][i]; day = b['tday'][i]
    for s_ in ('train', 'valid'):
        m = f & (sp == s_); mfe = o['mfe_m'][m]; dd = d[m]; dy = day[m]
        ref = np.where(dd[:, None] == 1, bl[(s_, 1)], bl[(s_, -1)])
        x = ((mfe[:, None] >= kit.TPR - 1e-9) * 100 - ref).mean(axis=1)    # per-trade avg excess over the 4 TPs
        ud, inv = np.unique(dy, return_inverse=True); sums = np.bincount(inv, x); cnt = np.bincount(inv)
        bs = []
        for _ in range(B):
            k = rng.integers(0, len(ud), len(ud)); bs.append(sums[k].sum() / cnt[k].sum())
        bs = np.array(bs)
        print('%-8s %-5s n %4d avg excess %+.2f  day-bootstrap se %.2f  z %.2f  P(<=0) %.3f' % (tag, s_, m.sum(), x.mean(), bs.std(), x.mean() / bs.std(), np.mean(bs <= 0)))
for tf in ('M15', 'M5'):
    b, i, d, e, a, win, H, Lo = candA.sigs(tf); boot('A ' + tf, tf, i, d, e, e - d * 1.8 * a, 2, win)
for tf in ('M15', 'M5'):
    b, i, d = candB.sigs(tf); H, L, A = b['H'], b['L'], b['atr']; a = A[i]
    ext = np.where(d == 1, L[i], H[i]); e = np.where(d == 1, H[i] + 0.05 * a, L[i] - 0.05 * a)
    st = np.where(d == 1, np.minimum(ext - 0.1 * a, e - 0.5 * a), np.maximum(ext + 0.1 * a, e + 0.5 * a))
    boot('B ' + tf, tf, i, d, e, st, 2, 3)
