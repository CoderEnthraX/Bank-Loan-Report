"""step 5: (a) composite FLOW CONFIRMATION score (the features with a consistent sign in step 2: cvd_new20, cvd5_pct, pre5_pct, v_r20;
NOTE: chosen after seeing valid -> valid is no longer clean for it; M1 / H1 and train years are the remaining checks);
(b) is it just price momentum? same keep on mom10_a / mom30_a / er10 and FC within momentum terciles; (c) prior-profile HVN
avoidance; (d) combinations. Thresholds = train quantiles per TF."""
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/entry/of_agentA')
import lib, numpy as np, pandas as pd, warnings; warnings.filterwarnings('ignore')
def rank_tr(x, tr):
    ref = np.sort(x[tr & ~np.isnan(x)]); return np.searchsorted(ref, x) / len(ref)
for tf in sys.argv[1:]:
    df = lib.ds(tf); F = lib.feats(tf); tr = ((df.split == 'train') & df.filled).to_numpy(); print('=====', tf)
    cols = ['cvd_new20', 'cvd5_pct', 'pre5_pct', 'v_r20'] if tf != 'M1' else ['cvd_new20', 'cvd5_pct', 'pre5_pct', 'v_r20']
    FC = np.mean([rank_tr(F[c].to_numpy(), tr) for c in cols], 0)
    FCd = np.mean([rank_tr(F[c].to_numpy(), tr) for c in cols[:3]], 0)          # delta-only version (no volume)
    for q in (0.5, 0.67):
        t = np.quantile(FC[tr], q); lib.stats(tf, FC >= t, df, 'FC4 score >= train q%.2f' % q, tag='combo')
        t = np.quantile(FCd[tr], q); lib.stats(tf, FCd >= t, df, 'FC3 (delta only) >= train q%.2f' % q, tag='combo')
    t = np.quantile(FC[tr], 0.33); lib.stats(tf, FC <= t, df, 'FC4 score <= q0.33 (should be bad)', tag='combo')
    lib.stats(tf, F.cvd_new20.to_numpy() > 0, df, 'CVD confirms 20-bar extreme (cvd_new20>0)', tag='combo')
    # momentum controls (kit features)
    for c in ('mom10_a', 'mom30_a', 'er10'):
        x = df[c].to_numpy(); t = np.quantile(x[tr], 0.5); lib.stats(tf, x >= t, df, 'CONTROL %s >= train median' % c, tag='ctrl')
    m30 = df.mom30_a.to_numpy(); qa, qb = np.quantile(m30[tr], [1 / 3, 2 / 3]); tm = np.quantile(FC[tr], 0.5)
    for lab, mm in (('lo', m30 <= qa), ('mid', (m30 > qa) & (m30 < qb)), ('hi', m30 >= qb)):
        lib.stats(tf, mm & (FC >= tm), df, 'mom30 %s & FC4 >= med' % lab, tag='ctrl'); lib.stats(tf, mm & (FC < tm), df, 'mom30 %s & FC4 < med' % lab, tag='ctrl')
    print('corr FC4 vs mom10/mom30/er10 (train):', [round(np.corrcoef(FC[tr], df[c].to_numpy()[tr])[0, 1], 2) for c in ('mom10_a', 'mom30_a', 'er10')])
    # prior-profile HVN avoidance
    hv = np.nanmax(np.c_[F.ps_max_prior, F.p4_max_prior], 1)
    lib.stats(tf, ~(hv >= 1.5), df, 'no prior-HVN entry..stop..TP4 (max<1.5)', tag='combo')
    lib.stats(tf, ~(F.ps_max_prior.to_numpy() >= 1.5), df, 'no prior-HVN entry..stop', tag='combo')
    lib.stats(tf, ~(F.rvp_e_prior.to_numpy() >= 1.0), df, 'entry not at prior HVN (rvp<1)', tag='combo')
    t = np.quantile(FC[tr], 0.5)
    lib.stats(tf, (FC >= t) & ~(hv >= 1.5), df, 'FC4>=med & no prior-HVN', tag='combo')
    lib.stats(tf, (F.cvd_new20.to_numpy() > 0) & ~(hv >= 1.5), df, 'cvd_new20>0 & no prior-HVN', tag='combo')
    lib.stats(tf, (FC >= t) & (F.loc_e_prior.to_numpy() == 1), df, 'FC4>=med & entry beyond prior VA', tag='combo')
    pv = F.pva_w_a.to_numpy(); tp = np.nanquantile(pv[tr], 1 / 3)
    lib.stats(tf, (FC >= t) & (pv <= tp), df, 'FC4>=med & narrow prior VA', tag='combo')
