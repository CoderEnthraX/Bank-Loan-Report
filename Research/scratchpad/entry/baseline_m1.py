"""bars_M1.pkl for kit.baseline('M1'): every 3rd M1 bar (not Sunday, warm), long and short at market, stop 1.8 ATR; minimal columns."""
import sys, pickle, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import data, outcomes, dataset
b = data.load('M1'); n = b['n']
i = np.flatnonzero(~np.isnan(b['atr']) & (b['utc_wd'] != 6) & (np.arange(n) > 60) & (np.arange(n) < n - 5))[::3]
A = b['atr'][i]; C = b['C'][i]
ol = outcomes.simulate('M1', i, np.ones(len(i), np.int8), C, C - 1.8 * A, mode=1)
os_ = outcomes.simulate('M1', i, -np.ones(len(i), np.int8), C, C + 1.8 * A, mode=1)
f = pd.DataFrame(dict(i=i, split=dataset.split_of(b['utc'][i]), mfeL=ol['mfe_m'], mfeS=os_['mfe_m'], cost=b['SP'][i] / (1.8 * A), year=b['year'][i]))
pickle.dump(f, open('%s/entry/bars_M1.pkl' % S, 'wb')); print('M1 baseline bars', len(f))
