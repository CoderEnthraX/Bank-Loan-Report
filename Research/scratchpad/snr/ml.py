"""Machine-learning check: can the order flow + context features tell winning Sniper signals from losing ones on unseen data?
Candidates: the Sniper engine in a permissive setting (aggression-only signals on both sides of the VWAP, no distance / cooldown limits; the
zone, absorption and delta features are still recorded), the default stop. Target: the signal reaches X R before its stop.
LightGBM fitted on 2021-22, early stopping on 2023, scored on 2024 - 2 Oct 2026: AUC, and the accuracy of the signals the model rates best.
Run: python3 -I ml.py TF -> ml_<tf>.pkl"""
import sys, pickle, numpy as np, datetime as dt
HERE = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/snr'
sys.path.insert(0, HERE)
import engine as E, evalx as V, outcome as O, featscan as FS
import lightgbm as lgb
from sklearn.metrics import roc_auc_score

T23 = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp())


def dataset(tf, kw):
    P = E.params(**kw)
    si, sd, se, ss, sf = E.run(tf, P, V.feat(tf))
    o = V.outc(tf, si, sd, se, ss, 0, False)
    fe = FS.sigfeat(tf, si, sd, sf)
    names = sorted(fe)
    Xm = np.column_stack([fe[k] for k in names]).astype(float)
    return Xm, names, o, si, sd


def run(tf):
    kw = dict(mode=1, vside=0, maxDist=0, cool=0, aggRatio=1.3 if tf >= 60 else 1.8)
    Xm, names, o, si, sd = dataset(tf, kw)
    t = o['t']; ok = o['filled'] & (o['end'] >= 0)
    A = ok & (t < T23); B = ok & (t >= T23) & (t < O.TEST0); T = ok & (t >= O.TEST0)
    out = dict(tf=tf, n=(int(A.sum()), int(B.sum()), int(T.sum())), names=names, res={})
    for X in (0.5, 1.0, 1.5):
        y = (o['mfe'] >= X - 1e-12).astype(int)
        rnd = 1 / (1 + X)
        params = dict(objective='binary', learning_rate=0.03, num_leaves=15, min_data_in_leaf=80, feature_fraction=0.7, bagging_fraction=0.8,
                      bagging_freq=1, lambda_l2=5.0, verbose=-1, seed=7)
        dA = lgb.Dataset(Xm[A], y[A]); dB = lgb.Dataset(Xm[B], y[B], reference=dA)
        m = lgb.train(params, dA, num_boost_round=1500, valid_sets=[dB], callbacks=[lgb.early_stopping(100, verbose=False)])
        pB = m.predict(Xm[B], num_iteration=m.best_iteration); pT = m.predict(Xm[T], num_iteration=m.best_iteration)
        aucB = roc_auc_score(y[B], pB); aucT = roc_auc_score(y[T], pT)
        rows = []
        for q in (0.5, 0.2, 0.1, 0.05):
            thr = np.quantile(pB, 1 - q)                     # the threshold set on 2023, applied to 2024-26
            sel = pT >= thr
            rows.append((q, int(sel.sum()), y[T][sel].mean() if sel.sum() else np.nan))
        imp = sorted(zip(m.feature_importance('gain'), names), reverse=True)[:12]
        out['res'][X] = dict(aucB=aucB, aucT=aucT, base=(y[A].mean(), y[B].mean(), y[T].mean()), rnd=rnd, top=rows, imp=imp, iters=m.best_iteration)
        print('TF %d X %.1f: candidates A %d B %d T %d | base acc %.1f / %.1f / %.1f%% (random %.1f%%) | AUC 2023 %.3f, TEST %.3f | best-rated (thr from 2023): %s | iters %d' % (
            tf, X, A.sum(), B.sum(), T.sum(), 100 * y[A].mean(), 100 * y[B].mean(), 100 * y[T].mean(), 100 * rnd, aucB, aucT,
            ' '.join('top%d%%: %.1f%% (%d)' % (100 * q, 100 * a, n) for q, n, a in rows), m.best_iteration), flush=True)
        print('   most used features:', ', '.join('%s' % n for g, n in imp[:8]), flush=True)
    pickle.dump(out, open(HERE + '/ml_%d.pkl' % tf, 'wb'))


if __name__ == '__main__':
    run(int(sys.argv[1]))
