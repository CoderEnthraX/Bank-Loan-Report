"""Predictability ceiling: LightGBM trained on 2021-23, scored on 2024-01..2025-06 (test untouched).
(a) every bar, long and short models: label = TP2 (+1R) before the 1.8 ATR stop; (b) the indicator's filled signals.
Reports AUC and the TP1-TP4 hit rates of the top 10 / 20 / 30 % of scores vs all, per direction."""
import sys, pickle, numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score
from zoneinfo import ZoneInfo
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'; sys.path.insert(0, S + '/entry')
import ev, data
NY = ZoneInfo('America/New_York')
def nyh(utc):
    s = pd.to_datetime(utc, unit='s', utc=True).tz_convert(NY); return (s.hour * 60 + s.minute).to_numpy()
def hitline(m):
    h = [(np.mean(m >= r - 1e-9)) * 100 for r in ev.TPR]
    return ' '.join('%5.1f' % x for x in h) + '  (avg edge %+5.2f)' % np.mean(np.array(h) - ev.BASE * 100)
P = dict(objective='binary', learning_rate=0.03, num_leaves=15, min_data_in_leaf=400, feature_fraction=0.7, bagging_fraction=0.7,
         bagging_freq=1, lambda_l2=10.0, verbose=-1, num_threads=4)
def fit_eval(name, Xtr, ytr, Xva, yva, mva, rounds=300):
    m = lgb.train(P, lgb.Dataset(Xtr, ytr), rounds)
    p = m.predict(Xva); auc = roc_auc_score(yva, p)
    print('  %-28s AUC valid %.3f   all   %s' % (name, auc, hitline(mva)))
    for q in (0.9, 0.8, 0.7):
        sel = p >= np.quantile(p, q)
        print('  %-28s           top %2d%% %s' % ('', round((1 - q) * 100), hitline(mva[sel])))
    imp = sorted(zip(m.feature_importance('gain'), Xtr.columns), reverse=True)[:8]
    print('  %-28s top features: %s' % ('', ', '.join('%s' % c for g, c in imp)))
    return m
mode = sys.argv[1]
for tf in sys.argv[2:]:
    b = data.load(tf)
    if mode == 'bars':
        f = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb'))
        f['ny_min'] = nyh(b['utc'][f.i.to_numpy()])
        X = f.drop(columns=['i', 'split', 'mfeL', 'mfeS', 'cost', 'year', 'month', 'ist_min', 'utc_hour'])
        tr = (f.split == 'train').to_numpy(); va = (f.split == 'valid').to_numpy()
        print('== %s every bar (%d train, %d valid)' % (tf, tr.sum(), va.sum()))
        for side, col in (('long', 'mfeL'), ('short', 'mfeS')):
            y = (f[col].to_numpy() >= 1.0 - 1e-9).astype(int)
            fit_eval(side, X[tr], y[tr], X[va], y[va], f[col].to_numpy()[va])
    else:
        f = ev.load(tf); f['ny_min'] = nyh(f.utc.to_numpy())
        drop = ['i', 'utc', 'split', 'entry', 'stop', 'fill_bar', 'fill_m1', 'mfe_c', 'stop_c', 'exit_c', 'mfe_m', 'stop_m', 'exit_m', 't1_m',
                'filled', 'engine', 'cost_fill', 'year', 'month', 'ist_min', 'utc_hour', 'fill_delay']
        X = f.drop(columns=[c for c in drop if c in f]); y = (f.mfe_m.to_numpy() >= 1.0 - 1e-9).astype(int)
        tr = (f.split == 'train').to_numpy(); va = (f.split == 'valid').to_numpy()
        print('== %s indicator signals, filled (%d train, %d valid)' % (tf, tr.sum(), va.sum()))
        for side, dm in (('both', np.ones(len(f), bool)), ('long', f.dir.to_numpy() > 0), ('short', f.dir.to_numpy() < 0)):
            if side == 'both': fit_eval('signals ' + side, X[tr], y[tr], X[va], y[va], f.mfe_m.to_numpy()[va])
            else:
                mva = f.mfe_m.to_numpy()[va & dm]; print('  %-28s valid all %s' % ('signals ' + side, hitline(mva)))
