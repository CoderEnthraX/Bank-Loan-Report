"""no-edge reference: random bars, random direction, market entry at the bar close, stop 1.8 ATR (also 0.9 / 3 / 4 ATR); TP hit rates on the M1 path"""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import data, outcomes
rng = np.random.default_rng(7)
TP = (0.6, 1.0, 1.5, 2.0)
for tf in ('H1', 'M15', 'M5', 'M1'):
    b = data.load(tf); n = b['n']
    ok = np.flatnonzero(~np.isnan(b['atr']) & (b['utc_wd'] != 6))
    i = np.sort(rng.choice(ok[ok < n - 10], size=min(60000, len(ok) // 2), replace=False))
    for sm in (1.8, 4.0):
        for dname, d in (('long', np.ones(len(i), np.int8)), ('short', -np.ones(len(i), np.int8)), ('random', rng.choice([-1, 1], len(i)).astype(np.int8))):
            e = b['C'][i]; st = e - d * sm * b['atr'][i]
            o = outcomes.simulate(tf, i, d, e, st, mode=1)
            f = o['fill_m1'] >= 0; mfe = o['mfe_m'][f]
            cost = (b['SP'][i] / (sm * b['atr'][i]))[f]
            print('%-4s stop %.1f ATR %-6s n %6d  ' % (tf, sm, dname, f.sum()) + '  '.join('TP%d %.1f%%' % (k + 1, 100 * np.mean(mfe >= r - 1e-9)) for k, r in enumerate(TP)) +
                  '   spread %.3fR' % np.median(cost))
