"""step 5b: is 'narrow prior value area' (pva_w_a = prior-session VA width / ATR) an order-flow effect or the ATR regime?
compare: pva_w_a low tercile; kit atr_d high tercile (ATR / daily ATR); pva_w_d = VA width / prior daily ATR (profile shape only);
pva_w_a low within atr_d terciles. All 4 TFs, thresholds = train terciles."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, numpy as np, warnings; warnings.filterwarnings('ignore')
for tf in sys.argv[1:]:
    df = lib.ds(tf); F = lib.feats(tf); tr = ((df.split == 'train') & df.filled).to_numpy(); print('=====', tf)
    pv = F.pva_w_a.to_numpy(); ad = df.atr_d.to_numpy(); pvd = pv * ad; ar = df.atr_r100.to_numpy()
    print('corr(pva_w_a, atr_d) %.2f  corr(log pva_w_a, log atr_d) %.2f  corr(pva_w_d, atr_d) %.2f' % (
        np.corrcoef(pv[tr], ad[tr])[0, 1], np.corrcoef(np.log(pv[tr]), np.log(ad[tr]))[0, 1], np.corrcoef(pvd[tr], ad[tr])[0, 1]))
    t = lambda x, q: np.nanquantile(x[tr], q)
    lib.stats(tf, pv <= t(pv, 1 / 3), df, 'pva_w_a <= q1/3 (narrow prior VA / ATR)', tag='pva')
    lib.stats(tf, ad >= t(ad, 2 / 3), df, 'CONTROL atr_d >= q2/3 (kit)', tag='ctrl')
    lib.stats(tf, ar >= t(ar, 2 / 3), df, 'CONTROL atr_r100 >= q2/3 (kit)', tag='ctrl')
    lib.stats(tf, pvd <= t(pvd, 1 / 3), df, 'pva_w_d <= q1/3 (VA width / daily ATR)', tag='pva')
    lib.stats(tf, pvd >= t(pvd, 2 / 3), df, 'pva_w_d >= q2/3', tag='pva')
    qa, qb = t(ad, 1 / 3), t(ad, 2 / 3)
    for lab, mm in (('lo', ad <= qa), ('mid', (ad > qa) & (ad < qb)), ('hi', ad >= qb)):
        x = pv[mm & tr]; m2 = np.nanmedian(x)
        lib.stats(tf, mm & (pv <= m2), df, 'atr_d %s & pva_w_a <= med(within)' % lab, tag='ctrl')
        lib.stats(tf, mm & (pv > m2), df, 'atr_d %s & pva_w_a > med(within)' % lab, tag='ctrl')
