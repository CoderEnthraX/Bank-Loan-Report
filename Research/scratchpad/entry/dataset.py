"""Entry research kit, part 5: one table per timeframe: every raw signal (default engine settings), its features, its fill and its
outcome (1-minute path and chart convention), the split (train 2021-23 / valid 2024-01..2025-06 / test 2025-07..), and whether the
real engine (ref_g, default settings) took it. python3 -I dataset.py TF ... -> entry/ds_TF.pkl"""
import sys, pickle, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/entry'); sys.path.insert(0, S + '/gold')
import data, signals, outcomes, features
TPR = (0.6, 1.0, 1.5, 2.0)
SPLIT = (np.datetime64('2024-01-01'), np.datetime64('2025-07-01'))

def split_of(utc):
    t = utc.astype('datetime64[s]')
    return np.where(t < SPLIT[0], 'train', np.where(t < SPLIT[1], 'valid', 'test'))

def table(tf, sig=None, stop_key='stop_h', mode=0, window=5, engine=True):
    s = sig or signals.raw(tf)
    st = s[stop_key]; s2 = dict(s, stop=st)
    o = outcomes.simulate(tf, s['i'], s['d'], s['entry'], st, mode=mode, window=window)
    df = features.build(tf, s2)
    b = data.load(tf)
    df['i'] = s['i']; df['utc'] = b['utc'][s['i']]; df['split'] = split_of(b['utc'][s['i']])
    df['entry'] = s['entry']; df['stop'] = st
    for k, v in o.items(): df[k] = v
    df['filled'] = df['fill_m1'] >= 0
    df['fill_delay'] = np.where(df['fill_bar'] >= 0, df['fill_bar'] - df['i'], -1)
    risk = s['d'] * (s['entry'] - st)
    fb = np.maximum(df['fill_bar'].to_numpy(), 0)
    df['cost_fill'] = b['SP'][fb] / risk
    if engine:
        import geng, ref_g
        taken = {(x['arm'], x['dir']) for x in ref_g.run(tf, {}) if x['exit'] is not None}
        df['engine'] = [(int(a), int(c)) in taken for a, c in zip(s['i'], s['d'])]
    return df

if __name__ == '__main__':
    for tf in sys.argv[1:]:
        df = table(tf)
        pickle.dump(df, open('%s/entry/ds_%s.pkl' % (S, tf), 'wb'))
        f = df[df.filled]
        print(tf, len(df), 'signals', len(f), 'filled', f.engine.sum() if 'engine' in f else '', 'taken by the engine', dict(f.split.value_counts()))
