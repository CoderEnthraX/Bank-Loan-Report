"""step 6b: is it the VOLUME PROFILE or just a narrow prior day? prior-session high-low range / ATR (no volume needed) vs the prior VA
width / ATR, and the profile shape VA width / prior range. Signals (ds) on 4 TFs + generic breakout bars on M5 / M15."""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, kit, data, of, features, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
TPR = kit.TPR
def prior_range(tf):
    b = data.load(tf); ss = features.sessions(tf); sid = ss['sid']; ok = sid >= 1; p = np.maximum(sid - 1, 0)
    return np.where(ok, ss['dH'][p] - ss['dL'][p], np.nan)
for tf in sys.argv[1:]:
    b = data.load(tf); f = of.flow(tf); pr = prior_range(tf)
    va_a = (f['pvah'] - f['pval']) / b['atr']; pr_a = pr / b['atr']; shape = (f['pvah'] - f['pval']) / pr
    df = lib.ds(tf); i = df.i.to_numpy(); tr = ((df.split == 'train') & df.filled).to_numpy(); print('=====', tf)
    print('corr (train signals) VA/ATR vs range/ATR: %.2f' % pd.Series(va_a[i][tr]).corr(pd.Series(pr_a[i][tr]), method='spearman'))
    for nm, x in (('prior VA width / ATR', va_a[i]), ('prior RANGE / ATR (no volume)', pr_a[i]), ('VA width / prior range', shape[i])):
        q1, q2 = np.nanquantile(x[tr], [1 / 3, 2 / 3])
        lib.stats(tf, x <= q1, df, 'low  ' + nm, tag='ctrl6'); lib.stats(tf, x >= q2, df, 'high ' + nm, tag='ctrl6')
    # VA within range terciles
    x = pr_a[i]; q1, q2 = np.nanquantile(x[tr], [1 / 3, 2 / 3]); v = va_a[i]
    for lab, mm in (('lo', x <= q1), ('mid', (x > q1) & (x < q2)), ('hi', x >= q2)):
        md = np.nanmedian(v[mm & tr])
        lib.stats(tf, mm & (v <= md), df, 'range/ATR %s & VA/ATR <= med' % lab, tag='ctrl6'); lib.stats(tf, mm & (v > md), df, 'range/ATR %s & VA/ATR > med' % lab, tag='ctrl6')
