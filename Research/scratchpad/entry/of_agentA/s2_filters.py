"""step 2: signal-bar order flow and profile-location FILTERS (decided at the signal bar's close). Tercile screen (train thresholds)
of every OF feature (keep top third / bottom third) + categorical rules. All rows -> rows.jsonl"""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, numpy as np, warnings; warnings.filterwarnings('ignore')
for tf in sys.argv[1:]:
    df = lib.ds(tf); F = lib.feats(tf); print('=====', tf)
    for c in F.columns:
        if c.startswith('pnew') or c.startswith('loc_'): continue
        if tf == 'M1' and c in ('d_pct',): continue
        lib.tercile_screen(tf, F[c].to_numpy(), c, df)
    print('--- categorical')
    for c in ('loc_e_prior', 'loc_c_prior', 'loc_e_dev', 'loc_c_dev'):
        for v in (1, 0, -1): lib.stats(tf, F[c].to_numpy() == v, df, '%s == %d' % (c, v), tag='cat')
    for c in ('rvp_e_prior', 'rvp_e_dev', 'rvp_s_prior', 'rvp_s_dev', 'p1_max_prior', 'p4_max_prior', 'ps_max_prior', 'ps_max_dev'):
        x = F[c].to_numpy()
        lib.stats(tf, x < 0.5, df, '%s < 0.5 (LVN)' % c, tag='cat'); lib.stats(tf, x > 1.5, df, '%s > 1.5 (HVN)' % c, tag='cat')
    dp = F.d_pct.to_numpy()
    lib.stats(tf, dp > 0, df, 'delta agrees (d_pct > 0)', tag='cat'); lib.stats(tf, dp <= 0, df, 'delta disagrees (d_pct <= 0)', tag='cat')
    div = (F.pnew20.to_numpy() == 1) & (F.cvd_new20.to_numpy() <= 0)
    lib.stats(tf, div, df, 'CVD divergence 20 (price new, CVD not)', tag='cat'); lib.stats(tf, ~div, df, 'no CVD divergence 20', tag='cat')
    vt = F.v_tod.to_numpy(); er = F.eff_res.to_numpy()
    lib.stats(tf, vt > 2, df, 'climax volume v_tod > 2', tag='cat'); lib.stats(tf, vt < 0.8, df, 'low volume v_tod < 0.8', tag='cat')
    lib.stats(tf, er > 1.5, df, 'absorption eff_res > 1.5', tag='cat')
    sc = F.scvd_pct.to_numpy()
    lib.stats(tf, sc > 0, df, 'session CVD agrees', tag='cat'); lib.stats(tf, sc <= 0, df, 'session CVD disagrees', tag='cat')
