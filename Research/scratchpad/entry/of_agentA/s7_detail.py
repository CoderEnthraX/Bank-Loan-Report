"""step 7: candidates in detail: per-TP hit / excess (train, valid, long, short), per-year excess (random baseline per year and
direction from bars_TF.pkl), trades / month, E per TP after spread, and a shuffle placebo (condition values permuted within
split x direction, 2000 times): how often does a random subset of the same size reach all four cells > 0 with min cell >= observed?"""
import sys, pickle, json; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, kit, data, of, features, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
TPR = kit.TPR
def year_base(tf):
    g = pickle.load(open('%s/entry/bars_%s.pkl' % (lib.S, tf), 'rb')); b = data.load(tf)
    t = b['utc'][g.i.to_numpy()].astype('datetime64[s]'); yr = t.astype('datetime64[Y]').astype(int) + 1970
    yk = np.where((yr == 2025) & (t < np.datetime64('2025-07-01')), 2025, np.where(yr == 2025, -1, yr))
    out = {}
    for y in (2021, 2022, 2023, 2024, 2025):
        for d, col in ((1, 'mfeL'), (-1, 'mfeS')):
            x = g[col].to_numpy()[yk == y]; x = x[~np.isnan(x)]; out[(y, d)] = np.array([np.mean(x >= r - 1e-9) for r in TPR]) * 100
    return out
def prior_range(tf):
    ss = features.sessions(tf); sid = ss['sid']; p = np.maximum(sid - 1, 0)
    return np.where(sid >= 1, ss['dH'][p] - ss['dL'][p], np.nan)
def cvdnew(tf, df, F): return F.cvd_new20.to_numpy() > 0
RES = {}
def detail(tf, keep, name, df):
    print('\n######', name, tf)
    r = lib.stats(tf, keep, df, name, tag='cand')
    for s_ in ('train', 'valid'):
        for lab in ('long', 'short', 'both'):
            x = r['%s_%s' % (s_, lab)]
            print('  %-5s %-5s n %5d (%5.1f/mo) hit %s | excess %s avg %+5.2f (se %.1f) | E after spread %s' % (s_, lab, x['n'], x['pm'],
                  ' '.join('%5.1f' % v for v in x['hit']), ' '.join('%+5.1f' % v for v in x['exk']), x['ex'], x['se'], ' '.join('%+.3f' % v for v in x['E'])))
    yb = year_base(tf); b = data.load(tf); t = df.utc.to_numpy().astype('datetime64[s]'); yr = t.astype('datetime64[Y]').astype(int) + 1970
    mfe = df.mfe_m.to_numpy(); d = df.dir.to_numpy(); fil = df.filled.to_numpy(); py = {}
    line = '  per-year avg excess (L / S / n):'
    for y in (2021, 2022, 2023, 2024, 2025):
        cells = []
        for dd in (1, -1):
            m = keep & fil & (yr == y) & (d == dd)
            h = np.array([np.mean(mfe[m] >= r_ - 1e-9) for r_ in TPR]) * 100
            cells.append(float(np.mean(h - yb[(y, dd)]))); cells.append(int(m.sum()))
            m0 = fil & (yr == y) & (d == dd); h0 = np.array([np.mean(mfe[m0] >= r_ - 1e-9) for r_ in TPR]) * 100
            cells.append(float(np.mean(h0 - yb[(y, dd)])))
        py[y] = cells
        line += ' | %d%s L %+5.2f S %+5.2f (n %d/%d; all-signals L %+5.2f S %+5.2f)' % (y, 'H1' if y == 2025 else '', cells[0], cells[3], cells[1], cells[4], cells[2], cells[5])
    print(line.replace(' | ', '\n    '))
    # shuffle placebo
    rng = np.random.default_rng(0); sp = df.split.to_numpy(); obs = min(r[k]['ex'] for k in ('train_long', 'train_short', 'valid_long', 'valid_short'))
    bl = kit.baseline(tf); hits = (mfe[:, None] >= TPR[None, :] - 1e-9); cnt = 0; Ntr = 2000
    groups = [(np.flatnonzero(fil & (sp == s_) & (d == dd)), s_, dd) for s_ in ('train', 'valid') for dd in (1, -1)]
    for it in range(Ntr):
        mins = []
        for idx, s_, dd in groups:
            k = int(keep[idx].sum()); sel = rng.choice(idx, k, replace=False)
            mins.append(np.mean(hits[sel].mean(0) * 100 - bl[(s_, dd)]))
        if min(mins) >= obs: cnt += 1
    print('  shuffle placebo: P(random same-size subset has all 4 cells >= %.2f) = %.4f' % (obs, cnt / Ntr))
    RES[name + ' ' + tf] = dict(stats=r, per_year=py, placebo_p=cnt / Ntr, min_cell=obs)
for tf in ('M5', 'M15', 'M1', 'H1'):
    df = lib.ds(tf); F = lib.feats(tf); tr = ((df.split == 'train') & df.filled).to_numpy(); b = data.load(tf); i = df.i.to_numpy()
    va = F.pva_w_a.to_numpy(); thr = np.nanquantile(va[tr], 1 / 3)
    pr = prior_range(tf)[i] / b['atr'][i]; thr_r = np.nanquantile(pr[tr], 1 / 3)
    print('\n================', tf, 'thresholds: VA width <= %.2f ATR, prior range <= %.2f ATR' % (thr, thr_r))
    detail(tf, va <= thr, 'C1 narrow prior VA', df)
    if tf in ('M5', 'M15'):
        detail(tf, pr <= thr_r, 'C1b narrow prior RANGE (no volume)', df)
        detail(tf, (va <= thr) & cvdnew(tf, df, F), 'C2 narrow prior VA & CVD confirms 20-bar extreme', df)
    if tf == 'M15':
        def rank_tr(x): ref = np.sort(x[tr & ~np.isnan(x)]); return np.searchsorted(ref, x) / len(ref)
        FC = np.mean([rank_tr(F[c].to_numpy()) for c in ('cvd_new20', 'cvd5_pct', 'pre5_pct', 'v_r20')], 0)
        hv = np.nanmax(np.c_[F.ps_max_prior, F.p4_max_prior], 1)
        detail(tf, (FC >= np.quantile(FC[tr], 0.5)) & ~(hv >= 1.5), 'C3 flow-confirm FC4>=med & no prior HVN', df)
json.dump(RES, open('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA/detail.json', 'w'), default=float)
