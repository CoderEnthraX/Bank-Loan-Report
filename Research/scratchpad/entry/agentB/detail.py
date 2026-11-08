"""step 7: full detail of the candidates: per-TP hit / excess (train, valid, L/S), E per TP after spread, per year, trades per month,
day-clustered bootstrap s.e., and a control: fade ANY bar that closes beyond the 6-bar high/low with a same-direction body (no filters)."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/agentB')
import numpy as np, pandas as pd, lib, data, signals, kit, dataset
from fade2 import fade_set

def boot_se(tf, i, d, entry, stop, mode=1, B=400, seed=3):
    """bootstrap over trading days (server sessions): s.e. of the avg hit over TP1-4, per split / direction"""
    b = data.load(tf); o = kit.outcomes_of(tf, i, d, entry, stop, mode, 5); f = o['fill_m1'] >= 0; mfe = o['mfe_m']
    sp = dataset.split_of(b['utc'][i]); day = b['srv'][i] // 86400; rng = np.random.default_rng(seed); out = {}
    for s_ in ('train', 'valid'):
        for dd in (1, -1):
            m = f & (sp == s_) & (d == dd)
            if m.sum() < 10: continue
            h = np.mean([mfe[m] >= r - 1e-9 for r in kit.TPR], axis=0) * 100      # per-trade avg hit over 4 TPs
            df = pd.DataFrame(dict(day=day[m], h=h)).groupby('day').h.agg(['sum', 'count'])
            S, N = df['sum'].to_numpy(), df['count'].to_numpy(); k = len(S)
            bs = [S[q].sum() / N[q].sum() for q in (rng.integers(0, k, k) for _ in range(B))]
            out[(s_, dd)] = (float(np.std(bs)), k, int(m.sum()), float(50 / np.sqrt(m.sum())))
    return out

def show(tf, i, d, entry, stop, mode, name):
    print('#### %s  [%s]' % (name, tf))
    r = lib.ev(tf, i, d, entry, stop, mode=mode, name=name, family='detail', log=False, show=False)['_res']
    for s_ in ('train', 'valid'):
        for lab in ('long', 'short', 'both'):
            x = r[(s_, lab)]
            print('  %-5s %-5s n %5d %6.1f/mo | hit %s | excess %s avg %+5.2f | E after spread TP1..4 %s' % (s_, lab, x['n'], x['per_month'],
                  ' '.join('%5.1f' % v for v in x['hit']), ' '.join('%+5.1f' % v for v in x['excess']), x['avg_excess'],
                  ' '.join('%+.3f' % v for v in x['E'])))
    lib.per_year(tf, i, d, entry, stop, mode, 5, name)
    for k, v in boot_se(tf, i, d, entry, stop, mode).items():
        print('  boot s.e. %s %s: %.2f (days %d, trades %d, naive %.2f)' % (k[0], 'L' if k[1] == 1 else 'S', *v))

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        if tf == 'M1': lib.m1_baseline()
        b = data.load(tf); C, A, O, H, L = b['C'], b['atr'], b['O'], b['H'], b['L']
        s, i, fd, m = fade_set(tf, 12, 18, True)
        show(tf, i, fd, C[i], C[i] - fd * 1.8 * A[i], 1, 'C1 FADE NY12-18 mkt 1.8ATR')
        s, i, fd, m = fade_set(tf, 12, 18, True, dispAtr=1.2)
        show(tf, i, fd, C[i], C[i] - fd * 1.8 * A[i], 1, 'C2 C1 + range>=1.2ATR')
        # control: plain 6-bar breakout bars (no indicator filters) in the same window, faded
        n = b['n']; sH = pd.Series(H).rolling(6).max().shift(1).to_numpy(); sL = pd.Series(L).rolling(6).min().shift(1).to_numpy()
        nym = kit.local_min(tf, 'ny'); cont = np.r_[np.diff(b['utc']) == 60 * b['tfmin'], False]
        win = (nym >= 720) & (nym < 1080) & cont & ~np.isnan(A) & (b['utc_wd'] != 6)
        up = win & (C > sH) & (C > O); dn = win & (C < sL) & (C < O)
        ii = np.r_[np.flatnonzero(up), np.flatnonzero(dn)]; dd = np.r_[-np.ones(up.sum(), np.int64), np.ones(dn.sum(), np.int64)]
        o = np.argsort(ii); ii, dd = ii[o], dd[o]
        lib.ev(tf, ii, dd, C[ii], C[ii] - dd * 1.8 * A[ii], mode=1, name='CONTROL fade any 6-bar brk NY12-18', family='detail')
        big = (H[ii] - L[ii]) >= 0.8 * A[ii]
        lib.ev(tf, ii[big], dd[big], C[ii[big]], C[ii[big]] - dd[big] * 1.8 * A[ii[big]], mode=1, name='CONTROL same, range>=0.8ATR', family='detail')
        if tf == 'M5':
            s = signals.raw(tf); J = __import__('pb').pb_bars(b, s, 5, 'lvl'); mm = J >= 0
