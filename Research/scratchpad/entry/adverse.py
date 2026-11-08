"""Adverse selection of the retest limit: the same raw signals entered (a) at market at the signal close, (b) by the model limit;
(a) split by whether the limit would have filled. Stop = same distance in ATR as the engine's normal stop (1.8 ATR) for both."""
import sys, numpy as np
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import data, signals, outcomes, ev, pandas as pd
for tf in ('H1', 'M15', 'M5'):
    b = data.load(tf); s = signals.raw(tf); i, d = s['i'], s['d']; A = b['atr'][i]
    sp = b['split'] if 'split' in b else None
    t = b['utc'][i].astype('datetime64[s]'); trn = t < np.datetime64('2025-07-01')       # train + valid only
    lim = outcomes.simulate(tf, i, d, s['entry'], s['entry'] - d * 1.8 * A, mode=0)
    mkt = outcomes.simulate(tf, i, d, b['C'][i], b['C'][i] - d * 1.8 * A, mode=1)
    def show(name, o, m):
        mfe = o['mfe_m'][m & (o['fill_m1'] >= 0)]
        hit = [(mfe >= r - 1e-9).mean() * 100 for r in ev.TPR]
        print('  %-44s n %6d  ' % (name, len(mfe)) + ' '.join('TP%d %5.1f' % (k + 1, h) for k, h in enumerate(hit)) +
              '  avg edge %+5.2f' % np.mean(np.array(hit) - ev.BASE * 100))
    print(tf)
    filled = lim['fill_m1'] >= 0
    show('limit (model entry), filled', lim, trn)
    show('market at signal close, all signals', mkt, trn)
    show('market, signals whose limit FILLED', mkt, trn & filled)
    show('market, signals whose limit did NOT fill', mkt, trn & ~filled)
