"""All numbers for the entry-accuracy workbook (train / valid / test). Output: entry/report_data.json"""
import sys, json, numpy as np, pandas as pd
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/entry'); sys.path.insert(0, S + '/gold')
import kit, data, signals, outcomes, dataset, finalists, exact, pickle
SPL = ('train', 'valid', 'test'); OUT = {}
def hitrow(mfe):
    mfe = mfe[~np.isnan(mfe)]
    return [float(np.mean(mfe >= r - 1e-9) * 100) for r in kit.TPR], int(len(mfe))
# A. random entries per TF / split / side
OUT['random'] = {}
for tf in ('M1', 'M5', 'M15', 'H1'):
    bl = kit.baseline(tf); f = pickle.load(open('%s/entry/bars_%s.pkl' % (S, tf), 'rb'))
    for sp in SPL:
        for d, col in ((1, 'mfeL'), (-1, 'mfeS')):
            h, n = hitrow(f[f.split == sp][col].to_numpy())
            OUT['random']['%s|%s|%d' % (tf, sp, d)] = dict(hit=h, n=n)
# B. raw signals (limit, as the indicator) and E. finalists: kit.evaluate dicts
def ev_rows(tf, i, d, e, st, mode, win):
    r = kit.evaluate(tf, i, d, e, st, mode=mode, window=win, allow_test=True, quiet=True)
    return {'%s|%s' % k: {kk: (vv.tolist() if hasattr(vv, 'tolist') else vv) for kk, vv in v.items()} for k, v in r.items()}
OUT['raw'] = {tf: ev_rows(tf, *finalists.gen_indicator(tf)) for tf in ('M1', 'M5', 'M15', 'H1')}
OUT['finalists'] = []
for name, tf, fn in finalists.FINALISTS:
    if name.startswith('ref: indicator'): continue
    OUT['finalists'].append(dict(name=name, tf=tf, res=ev_rows(tf, *fn())))
# C/D. exact engine: default settings and the user's v4.0 settings (exit TP4 so every TP is visible), chart convention + 1-min path
import user_base
OUT['exact'] = {}
for tf in ('M5', 'M15', 'H1', 'M1'):
    for nm, o in (('default', {}), ('v4.0 settings', user_base.USER)):
        if nm != 'default' and tf in ('H1', 'M1'): continue
        df = exact.trades(tf, dict(o))
        for sp in SPL:
            m = df[(df.split == sp) & ~df.ghost]
            OUT['exact']['%s|%s|%s' % (tf, nm, sp)] = dict(n=int(len(m)), per_month=float(len(m) / kit.MONTHS[sp]),
                hit_chart=[float(m['hit%d' % k].mean() * 100) for k in range(1, 5)], hit_m1=hitrow(m.mfe_m.to_numpy())[0])
# F. New York hour x year (drift-neutral D = (long - short) / 2 minus that year's mean), M15 every bar
f = pickle.load(open('%s/entry/bars_M15.pkl' % S, 'rb')); b = data.load('M15')
nyh = kit.local_min('M15', 'ny')[f.i.to_numpy()] // 60
t = b['utc'][f.i.to_numpy()].astype('datetime64[s]')
per = np.where(t < np.datetime64('2022-01-01'), '2021', np.where(t < np.datetime64('2023-01-01'), '2022', np.where(t < np.datetime64('2024-01-01'), '2023',
      np.where(t < np.datetime64('2025-01-01'), '2024', np.where(t < np.datetime64('2025-07-01'), '2025 H1', 'test 25H2-26')))))
def edge(x): return float(np.mean([(np.mean(x >= r - 1e-9) - bb) * 100 for r, bb in zip(kit.TPR, kit.BASE)])) if len(x) else float('nan')
OUT['season'] = {}
for p in ('2021', '2022', '2023', '2024', '2025 H1', 'test 25H2-26'):
    g = per == p; L = f.mfeL.to_numpy(); Sx = f.mfeS.to_numpy()
    base = (edge(L[g]) - edge(Sx[g])) / 2
    OUT['season'][p] = [((edge(L[g & (nyh == h)]) - edge(Sx[g & (nyh == h)])) / 2 - base) if (g & (nyh == h)).sum() > 50 else None for h in range(24)]
# G. adverse selection of the retest limit (same signals: limit fills vs market entry split by fill), all periods
OUT['adverse'] = {}
for tf in ('M5', 'M15', 'H1'):
    bb_ = data.load(tf); s = signals.raw(tf); i, d = s['i'], s['d']; A = bb_['atr'][i]
    lim = outcomes.simulate(tf, i, d, s['entry'], s['entry'] - d * 1.8 * A, mode=0)
    mkt = outcomes.simulate(tf, i, d, bb_['C'][i], bb_['C'][i] - d * 1.8 * A, mode=1)
    fl = lim['fill_m1'] >= 0
    OUT['adverse'][tf] = dict(limit_filled=hitrow(lim['mfe_m'][fl]), market_all=hitrow(mkt['mfe_m']), market_if_filled=hitrow(mkt['mfe_m'][fl]),
                              market_if_not_filled=hitrow(mkt['mfe_m'][~fl]))
json.dump(OUT, open('%s/entry/report_data.json' % S, 'w'), default=float)
print('saved', list(OUT))
