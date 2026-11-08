"""step 4: LightGBM on the indicator's filled signals: kit features (~55) vs kit + order-flow (40) vs order-flow only.
Train 2021-23, score valid 2024-01..2025-06. Label TP2 (+1R before the stop). AUC (all / long / short), and the excess of the
top 10 / 20 / 30 % of valid scores (thresholds = quantiles of the TRAIN scores out-of-fold, so they are fixed before valid)."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, numpy as np, pandas as pd, lightgbm as lgb, warnings; warnings.filterwarnings('ignore')
from sklearn.metrics import roc_auc_score
P = dict(objective='binary', learning_rate=0.03, num_leaves=15, min_data_in_leaf=200, feature_fraction=0.7, bagging_fraction=0.7,
         bagging_freq=1, lambda_l2=10.0, verbose=-1, num_threads=2)
DROP = ['i', 'utc', 'split', 'entry', 'stop', 'fill_bar', 'fill_m1', 'mfe_c', 'stop_c', 'exit_c', 'mfe_m', 'stop_m', 'exit_m', 't1_m',
        'filled', 'engine', 'cost_fill', 'year', 'month', 'ist_min', 'utc_hour', 'fill_delay']
for tf in sys.argv[1:]:
    df = lib.ds(tf); F = lib.feats(tf); fil = df.filled.to_numpy(); tr = (df.split == 'train').to_numpy(); va = (df.split == 'valid').to_numpy()
    y = (df.mfe_m.to_numpy() >= 1.0 - 1e-9).astype(int); dd = df.dir.to_numpy()
    base = df.drop(columns=[c for c in DROP if c in df]); ofc = F.drop(columns=['pnew6'])
    sets = {'kit': base, 'kit+OF': pd.concat([base, ofc], axis=1), 'OF+dir': pd.concat([df[['dir']], ofc], axis=1)}
    print('=====', tf, 'train filled', (tr & fil).sum(), 'valid filled', (va & fil).sum())
    for nm, X in sets.items():
        aucs = []; pv = np.zeros(len(df)); ptr_oof = np.full(len(df), np.nan)
        for seed in range(3):
            p = dict(P, seed=seed)
            m = lgb.train(p, lgb.Dataset(X[tr & fil], y[tr & fil]), 300)
            pv += m.predict(X) / 3
            # out-of-fold train scores (3 folds by time) for the selection thresholds
            idx = np.flatnonzero(tr & fil); folds = np.array_split(idx, 3)
            for k in range(3):
                trn = np.concatenate([folds[j] for j in range(3) if j != k])
                mk = lgb.train(p, lgb.Dataset(X.iloc[trn], y[trn]), 300)
                ptr_oof[folds[k]] = (0 if seed == 0 else ptr_oof[folds[k]]) + mk.predict(X.iloc[folds[k]]) / 3
        a_all = roc_auc_score(y[va & fil], pv[va & fil]); a_l = roc_auc_score(y[va & fil & (dd > 0)], pv[va & fil & (dd > 0)])
        a_s = roc_auc_score(y[va & fil & (dd < 0)], pv[va & fil & (dd < 0)]); a_oof = roc_auc_score(y[tr & fil], ptr_oof[tr & fil])
        print('%-7s %s  AUC train-OOF %.3f | valid all %.3f long %.3f short %.3f' % (nm, tf, a_oof, a_all, a_l, a_s))
        imp = sorted(zip(m.feature_importance('gain'), X.columns), reverse=True)[:10]
        print('        top features:', ', '.join(c for g, c in imp))
        score = np.where(tr, ptr_oof, pv)
        for q in (0.9, 0.8, 0.7):
            thr = np.nanquantile(ptr_oof[tr & fil], q)
            lib.stats(tf, score >= thr, df, 'LGBM %s top %d%%' % (nm, round((1 - q) * 100)), tag='lgbm')
        lib.stats(tf, score <= np.nanquantile(ptr_oof[tr & fil], 0.3), df, 'LGBM %s bottom 30%%' % nm, tag='lgbm')
