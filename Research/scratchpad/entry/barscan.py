"""Where is gold's direction predictable? Every bar (not Sunday, warm): a long and a short at market (entry = bar close, filled on the
next bar), stop 1.8 ATR, TP hits on the 1-minute path. Saves entry/bars_TF.pkl with the long / short MFE and context features
(signed for the LONG side; for the short side the signed ones flip)."""
import sys, pickle, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import data, outcomes, features, dataset
SIGNED = None
for tf in sys.argv[1:]:
    b = data.load(tf); n = b['n']
    i = np.flatnonzero(~np.isnan(b['atr']) & (b['utc_wd'] != 6) & (np.arange(n) > 60) & (np.arange(n) < n - 5))
    A = b['atr'][i]; C = b['C'][i]
    ol = outcomes.simulate(tf, i, np.ones(len(i), np.int8), C, C - 1.8 * A, mode=1)
    os_ = outcomes.simulate(tf, i, -np.ones(len(i), np.int8), C, C + 1.8 * A, mode=1)
    H, L = b['H'], b['L']
    sigH = pd.Series(H).rolling(6).max().shift(1).to_numpy()[i]; sigL = pd.Series(L).rolling(6).min().shift(1).to_numpy()[i]
    s = dict(i=i, d=np.ones(len(i), np.int8), entry=C, stop=C - 1.8 * A, sigH=sigH, sigL=sigL, er=np.zeros(len(i)), prevNet=np.zeros(len(i)),
             half=np.zeros(len(i), bool))
    f = features.build(tf, s)
    drop = [c for c in ('dir', 'brk_a', 'er10', 'prev_net', 'since_same', 'since_opp', 'depth_a', 'risk_a', 'half', 'cost_r', 'ent_vw_a', 'stop_vw_a') if c in f]
    f = f.drop(columns=drop)
    f['i'] = i; f['split'] = dataset.split_of(b['utc'][i])
    f['mfeL'] = ol['mfe_m']; f['mfeS'] = os_['mfe_m']; f['cost'] = b['SP'][i] / (1.8 * A)
    f['bull_bar'] = (b['C'][i] > b['O'][i]).astype(float)
    pickle.dump(f, open('%s/entry/bars_%s.pkl' % (S, tf), 'wb'))
    print(tf, len(f))
