"""step 6: is the narrow-prior-VA effect specific to the indicator's signals? Apply the same condition (prior-session VA width / ATR
<= the signals' train tercile) to RANDOM market entries on every bar (bars_TF.pkl, stop 1.8 ATR): excess of long / short vs all bars.
Also generic breakouts: bars closing beyond the 6-bar high / low in that direction (same universe as the indicator's break test)."""
import sys, pickle; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, kit, data, of, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
TPR = kit.TPR
for tf in sys.argv[1:]:
    g = pickle.load(open('%s/entry/bars_%s.pkl' % (lib.S, tf), 'rb')); g = g[g.split != 'test']
    b = data.load(tf); f = of.flow(tf); i = g.i.to_numpy()
    pv_all = (f['pvah'] - f['pval']) / b['atr']; pv = pv_all[i]
    df = lib.ds(tf); F = lib.feats(tf); tr = ((df.split == 'train') & df.filled).to_numpy(); thr = np.nanquantile(F.pva_w_a.to_numpy()[tr], 1 / 3)
    bl = kit.baseline(tf); sp = g.split.to_numpy()
    H, L, C = b['H'], b['L'], b['C']
    hh = pd.Series(H).rolling(6).max().shift(1).to_numpy()[i]; ll = pd.Series(L).rolling(6).min().shift(1).to_numpy()[i]
    print('=====', tf, 'threshold pva_w_a <= %.2f; share of bars below: %.2f' % (thr, np.nanmean(pv <= thr)))
    for lab, cond in (('random all bars', np.ones(len(g), bool)), ('random narrow VA', pv <= thr), ('random wide VA', pv > thr)):
        for brk in (False, True):
            out = []
            for s_ in ('train', 'valid'):
                for d, col in ((1, 'mfeL'), (-1, 'mfeS')):
                    m = cond & (sp == s_)
                    if brk: m &= (C[i] > hh) if d == 1 else (C[i] < ll)
                    x = g[col].to_numpy()[m]; x = x[~np.isnan(x)]
                    hit = np.array([np.mean(x >= r - 1e-9) for r in TPR]) * 100
                    out.append('%s %s %+5.2f (n %d)' % (s_[:2], 'L' if d == 1 else 'S', np.mean(hit - bl[(s_, d)]), len(x)))
            print('%-18s %-14s | %s' % (lab, 'breakout bars' if brk else 'every bar', ' | '.join(out)))
