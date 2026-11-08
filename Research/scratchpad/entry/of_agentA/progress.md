# of_agentA progress (order flow as filter / confirmation of the indicator's signals)
## Step 0 (done): read kit. ds_TF.pkl = signals.raw, stop_h, mode 0 window 5 -> outcomes (mfe_m). Fill delay: ~70% fill at bar i+1,
so chart-bar cancel rules reach few trades -> also do M1-level cancel (decided at each 1-minute close before the fill minute).
Plan: lib.py (OF features + fast subset stats vs kit.baseline) -> step1 verify vs kit.evaluate -> step2 pre-registered signal-bar
and profile filters -> step3 pullback cancel rules -> step4 LightGBM -> step5 combos + M1/H1 -> step6 detail + results.md
## Step 1 (done): lib.py (feats(tf) -> feats_TF.pkl, 40 OF features aligned with ds(tf) non-test rows; cancel(); stats()).
lib.stats on all signals == kit.evaluate exactly. Baseline excess (tr L/S, va L/S): M5 -1.07/-0.95/-0.54/+0.77; M15 -0.90/-0.10/-2.61/-1.87;
M1 -2.56/-2.88/-1.67/-2.12; H1 -6.60/-1.38/-2.28/-1.03. Note: M1 bar delta degenerate (d_pct=1 always). Dev profile above entry mostly
empty (new prices) -> prior-profile path RVP more informative. rows.jsonl collects every variant (tag=base/terc/cat/...).
Next: step 2 = signal-bar + profile filters (tercile screen of all 38 features, categorical rules) on M5/M15.
## Step 2 (done): s2_filters.py M5 M15 -> s2_M5_M15.out (105 variants per TF: 33 features x hi/lo tercile + 39 categorical).
PASS4: M5 1/105 (pva_w_a<=7.49: +1.71/+0.80/+1.28/+4.19; on M15 the same feature is 2/4 -> not robust), M15 1/105 (dcl_pct>=0.252:
+0.75/+4.60/+0.31/+2.32; on M5 dcl_pct hi is NEGATIVE -> not robust). Far below the 1/16 noise rate because the base is negative.
lift.py (hi-lo tercile diff, 8 cells = 2 TF x tr/va x L/S): only cvd_new20 (CVD confirms the 20-bar price extreme) 8/8 same sign
(M5 +0.36 +3.57 +2.47 +1.93; M15 +0.50 +2.47 +5.70 +0.96); 7/8: cvd5_pct, pre5_pct, v_r20 (flow agrees / higher volume) and
prior-profile HVN (ps_max_prior, rvp_s_prior, p4_max_prior: HVN near entry/stop/path = worse, mainly M15 valid -5..-10, train ~-1).
Categorical (delta agrees, VA inside/outside, LVN/HVN at entry, absorption, climax) = noise, no consistent sign.
Next: step 3 pullback cancel rules (lib.cancel, M1-level and chart-close) + diagnostic of pullback stats at fill.
## Step 3 (done): s3_pullback.py M5 M15 -> s3_M5_M15.out. 16 cancel rules per TF (pullback vol rate > 1/0.7/0.5, delta against >0.3/0.5,
quiet <0.3, delta in favour >0.3/0.5; at 1-minute closes and at chart-bar closes): 0 PASS4 on M5 and M15; none beats the base by
more than ~0.5 pt in a consistent way. Diagnostic at fill (state, not a rule): low-volume pullback ("no supply") is NOT better
(M5 low tercile tr -0.33 va -2.71 vs high tercile tr +1.79 va -0.48; M15 low tercile va -3.94). Pullback delta against: no pattern.
Next: step 4 LightGBM (ds features + OF features), valid AUC, top-decile excess.
## Step 4 (done): s4_lgbm.py M5 M15 -> s4_M5_M15.out (3 seeds, 300 rounds, num_threads 2; thresholds from train out-of-fold scores).
Valid AUC (TP2 label): M5 kit 0.501, kit+OF 0.506, OF+dir 0.511 (short 0.532); train-OOF 0.514-0.517. M15 kit 0.492, kit+OF 0.485,
OF+dir 0.500 (OOF 0.49-0.50 = nothing). M5 OF+dir top 20% PASS4 (tr +2.10/+0.67, va +1.73/+1.11, 45.6/mo) but top 10% / 30% fail;
M5 kit+OF top 10% 3/4 (va L -0.89); M15 every LGBM top bucket negative in valid. => AUC does not rise above ~0.51.
Next: step 5 composite flow-confirmation score + prior-HVN avoidance + combos, then M1/H1 confirmation, per-year.
## Step 5 (done): s5_combo.py M5 M15 M1 H1 -> s5.out. Flow-confirmation composite FC4 (rank-mean of cvd_new20, cvd5_pct, pre5_pct, v_r20,
selected after seeing valid): M5 >=median 3/4 (tr L -1.10), M15 3/4 (va S -3.18), M1 and H1 NO improvement vs base -> not confirmed.
Corr FC4 with mom10 0.34-0.43 (partly momentum). Prior-HVN avoidance (no prior-profile HVN >=1.5 between stop and TP4): M15 PASS4
(+0.41/+1.15/+0.57/+2.68, 38/mo) but M5 ~= base, M1/H1 no. Combos: FC4>=med & no prior-HVN M15 PASS4 (21/mo) but M5 3/4, M1/H1 fail;
FC4>=med & narrow prior VA (pva_w_a <= train q1/3): M5 PASS4 (+0.25/+2.31/+2.01/+5.61, 44/mo), M15 fail, M1/H1 much better than base.
Suspect pva_w_a = volatility regime (prior VA width / current ATR ~ 1/atr_d). Next: step 5b check pva_w_a vs atr_d control on 4 TFs.
## Step 5b (done): s5b_pva.py -> s5b.out. pva_w_a <= q1/3: M5 PASS4 (+1.63/+0.83/+1.28/+4.17, 86/mo); M15 2/4; M1/H1 lift vs base.
Within kit atr_d terciles, narrow pva_w_a beats wide in 11/12 M5 cells, 11/12 M1, 9/12 M15 -> not just the ATR regime.
pva_w_d = VA width / prior daily ATR (profile shape only, post hoc): low tercile beats high tercile in 14/16 cells (4 TFs x 4).
Next: step 6 = is it signal-specific? (narrow-VA filter on random market entries, bars_M5.pkl), then detail of candidates.
## Step 6 (done): s6_random.py -> s6.out. Narrow prior VA does NOTHING for random entries on every bar (|excess| <= 0.4, M5/M15),
but lifts generic breakouts (market at close beyond the 6-bar high/low): M5 narrow +0.36/+0.63/+2.06/+1.83 (n ~8k/4k per dir) vs
wide -1.78/-2.57/-0.45/+0.50; M15 narrow +1.55/+1.30/+2.04/-0.34 vs wide -1.05/-2.27/-1.21/+1.53 -> breakout x compression interaction.
Next: step 6b control = prior session RANGE / ATR (no volume) vs VA width / ATR, and VA width / prior range (profile shape).
## Step 6b (done): s6b_ctrl.py -> s6b.out. corr(VA/ATR, prior range/ATR) 0.82-0.89. Prior RANGE/ATR low tercile (no volume) on M5 is
PASS4 too (+1.84/+0.65/+1.89/+2.70) ~= VA version (+1.63/+0.83/+1.28/+4.17). Within range terciles, narrow VA beats wide VA in
~27/36 cells (M5/M15/M1) -> the profile adds a little beyond the plain narrow prior day; most of the effect = compression context.
Next: step 7 detail of candidates (per TP, per year, E after spread, shuffle placebo): C1 M5 narrow prior VA; C1b prior range control;
C2 C1 & cvd_new20>0; C3 M15 FC4>=med & no prior-HVN.
## Step 7 (done): s7_detail.py -> s7.out, detail.json. C1 M5 narrow prior VA (VAH-VAL <= 7.52 x ATR14): 84/mo train, PASS4
tr +1.63/+0.83 va +1.28/+4.17, per-year 9/10 year x dir cells > 0 (2021 S -1.58), shuffle placebo p < 0.0005 (0/2000) single-test;
E after spread train -0.09..-0.06 R, valid +0.00..+0.06. C1b (prior range <= 16.8 ATR, no volume) ~same (PASS4, 10/10? 2021 S -1.86).
C2 C1 & cvd_new20>0 M5 PASS4 but no better than C1 (fewer trades). C1 on M15 FAILS (-1.77/-0.58/+1.03/-2.92, placebo 0.35), M1 lifts vs
base but negative, H1 noise. C3 M15 FC4>=med & no prior-HVN PASS4 (+0.61/+2.63/+5.59/+0.88, 20/mo, placebo 0.002) but not on M5/M1/H1.
Next: step 8 = results.md (table from rows.jsonl via make_table.py, candidates, conclusion).
## Step 8 (done): results.md written (head.md + table.md). TASK COMPLETE.
