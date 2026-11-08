"""Independent re-derivation of agent B's C1: fade the indicator's raw signal at market when the signal bar opens 12:00-17:59 New York
time (next bar without a gap), stop 1.8 ATR. Train / valid only. Plus clock-shift placebo, per-year, window sensitivity, other TFs."""
import sys, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import kit, data, signals, placebo, dataset
def c1(tf, a=720, b_=1080, stop_atr=1.8, **sp):
    bb = data.load(tf); s = signals.raw(tf, **sp); i = s['i']; d = -s['d'].astype(int)       # the opposite trade
    ny = kit.local_min(tf, 'ny')[i]
    nogap = np.r_[bb['utc'][1:] - bb['utc'][:-1] == 60 * bb['tfmin'], False][i]
    keep = (ny >= a) & (ny < b_) & nogap
    i, d = i[keep], d[keep]; C = bb['C'][i]; A = bb['atr'][i]
    return i, d, C, C - d * stop_atr * A
for tf in ('M5', 'M1', 'M15'):
    i, d, e, st = c1(tf)
    kit.evaluate(tf, i, d, e, st, mode=1, name='%s C1 fade NY 12-18' % tf)
# placebo on M5: same rule with the NY clock shifted (window kept, signals re-selected)
bb = data.load('M5'); s = signals.raw('M5'); i = s['i']; d = -s['d'].astype(int)
nogap = np.r_[bb['utc'][1:] - bb['utc'][:-1] == 300, False][i]
i, d = i[nogap], d[nogap]; C = bb['C'][i]; A = bb['atr'][i]
print('M5 C1 placebo (clock shifted by 2..22 h):')
placebo.run('M5', i, d, C, C - d * 1.8 * A, 1, 1, lambda m, dd: (m >= 720) & (m < 1080), shifts=range(2, 23))
# per year and window sensitivity on M5
for (a, b_) in ((720, 1080), (660, 1080), (780, 1020), (720, 900), (900, 1080), (720, 1260)):
    i2, d2, e2, st2 = c1('M5', a, b_)
    r = kit.evaluate('M5', i2, d2, e2, st2, mode=1, quiet=True)
    print('window NY %02d:%02d-%02d:%02d  train L/S %+5.2f/%+5.2f  valid L/S %+5.2f/%+5.2f  n/mo %.0f' % (a // 60, a % 60, b_ // 60, b_ % 60,
          r[('train', 'long')]['avg_excess'], r[('train', 'short')]['avg_excess'], r[('valid', 'long')]['avg_excess'], r[('valid', 'short')]['avg_excess'],
          r[('train', 'both')]['per_month']))
i, d, e, st = c1('M5'); o = kit.outcomes_of('M5', i, d, e, st, 1, 1); bl = kit.baseline('M5')
yr = data.load('M5')['year'][i]; sp = dataset.split_of(data.load('M5')['utc'][i]); mfe = o['mfe_m']
for y in (2021, 2022, 2023, 2024, 2025):
    out = []
    for dd in (1, -1):
        m = (yr == y) & (d == dd) & (sp != 'test')
        hit = np.array([np.mean(mfe[m] >= r - 1e-9) for r in kit.TPR]) * 100
        ref = bl[('train' if y <= 2023 else 'valid', dd)]
        out.append('%+5.2f (n %4d)' % (np.mean(hit - ref), m.sum()))
    print('  %d  long %s   short %s' % (y, out[0], out[1]))
