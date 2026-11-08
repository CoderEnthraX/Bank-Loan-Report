# Order flow as a filter / confirmation of the Auction Retest signals (gold, tick volume): results

Agent: of_agentA. Universe: `signals.raw(tf)`, retest limit `entry`, stop `stop_h`, kit.evaluate mode 0 window 5 (outcomes from
`ds_TF.pkl`, which matches kit.evaluate exactly). Filters and cancel rules only REMOVE trades, so kept trades keep their outcomes.
Excess = hit% minus random entries of the same direction and split (kit.baseline), averaged over TP1-TP4. TEST (2025-07..) never
loaded (`lib.ds` drops it). All order-flow inputs come from `of.py` (tick-rule / CLV delta from 1-minute candles, session CVD,
tick-volume profile with $0.50 bins, POC / VAH / VAL, RVP). Scripts: `s1_verify.py` .. `s7_detail.py`, helpers `lib.py`,
outputs `s*.out`, every variant in `rows.jsonl`, full table `table.md`. Everything ran in this one session (no sub-agents);
LightGBM / numba used 2 threads.

Baseline excess of all signals (train L / S, valid L / S): M5 -1.07 / -0.95 / -0.54 / +0.77; M15 -0.90 / -0.10 / -2.61 / -1.87;
M1 -2.56 / -2.88 / -1.67 / -2.12; H1 -6.60 / -1.38 / -2.28 / -1.03. A filter has to lift the signals above random in all four cells.

## Short answer

Tick-volume order flow does **not** separate winning from false signals. Signal-bar delta, CVD trend and divergence, absorption,
climax volume, where price sits relative to the value area, LVN / HVN at the entry, along the path or behind the stop, the pullback's
volume and delta (as cancel rules), and LightGBM with all of them added: every one of these is noise, or its sign flips between TFs.
One context effect holds up: **breakouts after a narrow prior session**, meaning a narrow prior value area relative to the current
ATR. On M5 it lifts TP1-TP4 by about 2 points in both train and valid. But most of it is the narrow prior DAY RANGE, which needs no
volume. It fails on M15, and it leaves E after spread negative in train. So it is a mild context filter at best, not an order-flow
edge.

## 1. Every variant (summary; the full 446-row table is appended at the end)

Count: M5 178 variants (7 PASS4), M15 178 (3 PASS4), M1 45 (0), H1 45 (0). That is 10 PASS4 rows out of 446. They cover 7 distinct
rules; the narrow-VA rule appears 3 times under different tags. All the variants are correlated, and every baseline is negative, so
the plain 1-in-16 noise rate overstates how often a noise rule passes here. Even so, 7 distinct passes out of about 440 is no more
than noise would give, unless a rule is confirmed some other way (other TFs, years, an independent universe). Only the
narrow-prior-session family gets partial confirmation.

| family (step) | variants | PASS4 | best / notable (train L, train S, valid L, valid S) | verdict |
|---|---:|---:|---|---|
| signal-bar delta % (tick / CLV), volume vs average and vs time of day, effort/result (absorption), climax, pre-signal delta, CVD 5/20, session CVD, CVD new-extreme (divergence) - terciles (2a) | 2x 30 | M15 1 (dcl_pct hi +0.75/+4.60/+0.31/+2.32) | the same dcl_pct hi on M5 is -0.38/-1.01/-1.46/-0.74 | noise; the sign flips between TFs |
| profile distances / RVP (POC, VAH/VAL, developing and prior, entry / stop RVP, path RVP to TP1 / TP4, stop path) - terciles (2a) | 2x 38 | M5 1 (pva_w_a lo) | see narrow prior VA below | only the narrow prior VA survives |
| categorical (2b): delta agrees / disagrees, CVD divergence 20, climax, low volume, absorption eff_res > 1.5, session CVD agrees, entry / close inside / above / below prior and developing VA, LVN (<0.5) / HVN (>1.5) at entry, at stop, on the path, behind the stop | 2x 37 | 0 | "no CVD divergence" M5 -1.26/-0.32/-0.13/+0.82 (base -1.07/-0.95/-0.54/+0.77) | noise (lifts under 1 pt) |
| lift test: hi minus lo tercile, same sign in 8/8 cells (2 TF x tr/va x L/S) | 33 features | - | only cvd_new20 (CVD confirms the 20-bar extreme) 8/8: lift M5 +0.36/+3.57/+2.47/+1.93, M15 +0.50/+2.47/+5.70/+0.96 | expected by chance about 0.26 of 33; absolute excess still under 0 |
| pullback CANCEL rules at 1-minute closes and at chart-bar closes (3b): pullback volume rate > 1/0.7/0.5, delta against > 0.3/0.5, quiet < 0.3, delta in favour > 0.3/0.5 | 2x 16 | 0 | best M5 "delta against > 0.3" -1.04/-1.11/-0.12/+1.43 | none; "low-volume pullback = no supply" is NOT better (diag: M5 low tercile va -2.71, M15 va -3.94) |
| LightGBM, ~55 kit features + 40 OF features (4) | 2x 12 | M5 1 (OF+dir top 20%: +2.10/+0.67/+1.73/+1.11) | valid AUC M5 kit 0.501 / kit+OF 0.506 / OF only 0.511; M15 0.492 / 0.485 / 0.500 | AUC does not rise above ~0.51; the M5 top 10% / 30% fail |
| flow-confirmation composite FC4 (cvd_new20, cvd5, pre5, v_r20; picked after seeing valid) (5) | 4 TF x 5 | 0 alone | M5 >= med -1.10/+1.24/+0.39/+1.48; M1 / H1 no lift | not confirmed on M1 / H1 |
| prior-HVN avoidance (no prior-profile bin with RVP >= 1.5 from stop to TP4) (5) | 4 TF x 3 | M15 1 (+0.41/+1.15/+0.57/+2.68) | M5 = base, M1 / H1 no lift | M15 only |
| combinations (5) | 4 TF x 5 | M5 1 (FC4 & narrow VA), M15 1 (FC4 & no prior-HVN) | see candidates | M15 C3 fragile |
| momentum / ATR / prior-range controls (5, 5b, 6b) | 4 TF x 29 | M5 2 (prior range lo; range lo & VA lo) | prior RANGE/ATR lo (no volume) M5 +1.84/+0.65/+1.89/+2.70 | the narrow-VA effect is mostly the narrow prior range |

## 2. Best candidates in detail

### C1 (best): M5, narrow prior value area
**Rule, decided at the signal bar's close:** take an indicator signal (raw, retest limit `entry`, stop `stop_h`, limit live 5 bars)
only if `(VAH_prior - VAL_prior) <= 7.5 x ATR(14)` on M5 at the signal bar. VAH/VAL = the 70 % value area of the PREVIOUS server-day
session's tick-volume profile ($0.50 bins, each 1-minute candle's tick volume spread evenly over its high-low range). The threshold
7.52 is the train lower tercile. In Pine: the prior day's VAH / VAL (e.g. from a volume-profile library or request.security_lower_tf),
fixed for the whole session.

| split | dir | n (per month) | hit TP1-TP4 % | excess TP1-TP4 | avg excess | E after spread at TP1..TP4 (R) |
|---|---|---|---|---|---:|---|
| train | long | 1472 (40.9) | 62.4 51.6 42.0 35.4 | +0.3 +1.9 +2.1 +2.3 | +1.63 (se 1.3) | -0.107 -0.073 -0.054 -0.043 |
| train | short | 1548 (43.0) | 64.1 50.4 40.2 34.5 | +1.5 +0.3 +0.2 +1.3 | +0.83 (se 1.3) | -0.077 -0.094 -0.096 -0.067 |
| train | both | 3020 (83.9) | 63.2 51.0 41.1 34.9 | +0.9 +1.1 +1.1 +1.8 | +1.22 (se 0.9) | -0.092 -0.084 -0.075 -0.056 |
| valid | long | 899 (49.9) | 65.5 53.6 45.4 38.0 | +1.2 +0.8 +2.0 +1.1 | +1.28 (se 1.7) | +0.013 +0.037 +0.099 +0.106 |
| valid | short | 729 (40.5) | 63.8 51.7 41.6 33.9 | +3.7 +4.7 +4.6 +3.7 | +4.17 (se 1.9) | -0.011 +0.003 +0.008 -0.015 |
| valid | both | 1628 (90.4) | 64.7 52.8 43.7 36.2 | +2.4 +2.5 +3.2 +2.3 | +2.58 (se 1.2) | +0.002 +0.022 +0.058 +0.052 |

Against all M5 signals (train hits 61.3/49.1/38.9/32.1, valid 62.3/50.7/40.8/33.7), every TP rises: train +1.9/+1.9/+2.2/+2.8 pts,
valid +2.4/+2.1/+2.9/+2.5 pts. About 1/3 of the signals are kept (84-90 a month).

Per-year average excess (random baseline per year and direction), long / short; all-signals in brackets:
2021 +2.20 / -1.58 (-1.97 / -0.69) | 2022 +2.15 / +2.79 (+0.11 / -0.45) | 2023 +0.55 / +1.70 (-1.30 / -1.78) |
2024 +1.18 / +2.67 (-0.54 / +0.11) | 2025H1 +1.49 / +6.52 (-0.53 / +2.09). 9 of the 10 year x direction cells are > 0, and C1 beats
all-signals in 9/10 (not 2021 short).

Supporting checks:
- Shuffle placebo (the condition permuted within split x direction, 2000 draws): no draw reached all four cells >= +0.83, so
  p < 0.0005 as a single test. With about 440 variants tested, Bonferroni puts it at p < ~0.2: suggestive, not proof.
- Not the ATR regime: within kit `atr_d` terciles, narrow VA beats wide VA in 11/12 M5 cells.
- Specific to breakouts: on random market entries on every bar the same condition does nothing (|excess| <= 0.4). On generic
  breakouts (close beyond the 6-bar high / low, about 8k train trades per direction) it lifts: narrow +0.36/+0.63/+2.06/+1.83 vs
  wide -1.78/-2.57/-0.45/+0.50.
- Against it: on M15 the same rule fails (-1.77/-0.58/+1.03/-2.92, placebo p 0.35). On M1 it lifts vs base (base -2.56/-2.88/-1.67/-2.12
  -> -1.15/-1.27/-1.77/+0.66) but stays negative. H1 is noise (n about 4 a month per direction).
- E after spread is still NEGATIVE in train (-0.11 to -0.04 R). Valid is about 0 to +0.06 R, and that is helped by the long drift. Not
  tradeable on its own.

### C1b (control, no volume needed): M5, narrow prior session RANGE
`(prior session high - low) <= 16.8 x ATR(14)` on M5. Train L/S +1.84 / +0.65, valid +1.89 / +2.70 (PASS4, 84/mo); hits train
62.9/51.0/41.4/35.0, valid 64.3/52.9/43.4/35.4. Per year L/S: 2021 +0.62/-1.86, 2022 +2.36/+3.04, 2023 +2.64/+1.02, 2024 +1.33/+1.01,
2025H1 +2.93/+5.79. E after spread train -0.09..-0.04 R, valid -0.00..+0.05 R. Same as C1, and it fails on M15 too (+1.10/+0.38/-1.31/-4.57).
Spearman corr(VA width, prior range) = 0.82-0.89. Within prior-range terciles, narrow VA still beats wide VA in about 27/36 cells
(M5 / M15 / M1), so the volume profile adds a small part on top of the narrow prior day.

### C3 (fragile): M15, flow confirmation and no prior HVN in the way
FC4 = mean of the train percentile ranks of four signal-bar features: cvd_new20 (CVD vs its 20-bar extreme), cvd5_pct (5-bar delta
% of volume), pre5_pct (delta of the 5 bars before the signal) and v_r20 (volume / 20-bar mean). Keep FC4 >= train median AND no
prior-session profile bin with RVP >= 1.5 between the stop and TP4.
Train L/S +0.61 / +2.63 (hits both 67.3/51.4/39.2/33.5, excess +4.8/+1.5/-0.5/+0.5), valid +5.59 / +0.88 (hits both 65.0/55.8/45.7/40.2);
20/mo train, 22/mo valid. E after spread train +0.005/-0.043/-0.091/-0.066, valid +0.018/+0.095/+0.119/+0.184. Per year L/S:
2021 +2.14/+7.60, 2022 +1.26/-4.05, 2023 -1.36/+4.90, 2024 +3.26/+2.29, 2025H1 +9.71/-1.65. Shuffle placebo p 0.002.
Not usable: its components were chosen after seeing valid, the same rule fails on M5 (3/4), M1 and H1, it is hard to code, and
only TP1 rises clearly in train (TP3 / TP4 do not).

## 3. Honest conclusion

1. Tick-volume order flow does not separate winning from false signals of the Auction Retest. Every pure order-flow idea the
   trader listed lifts or lowers the hit rates by under ~1-2 pts with a sign that flips between TF / split / direction: delta sign and
   size, CVD trend and divergence, absorption / effort vs result, exhaustion / climax volume, the pullback's volume and delta
   (including "no supply" low-volume pullbacks and cancel rules at every 1-minute close), POC / VAH / VAL location, LVN / HVN at the
   entry, on the path or behind the stop. LightGBM with 40 order-flow features stays at valid AUC 0.50-0.51.
2. The one robust-looking effect is context, not flow: a breakout after a narrow prior session (narrow prior value area / prior
   range relative to the current ATR) follows through more often. On M5 it lifts every TP by about 2 pts in train AND valid, longs
   and shorts, in 9/10 years. It also shows on generic breakouts (but not on random entries). It does not hold on M15, it is mostly
   reproduced without any volume (prior high-low range), and E after spread stays negative in train. At most it is a mild filter to
   combine with other edges. It is not a reason to adopt order-flow tools.
3. Multiple testing: 446 variants, 7 distinct PASS4 rules, about what noise gives. Only C1 / C1b have outside support (years,
   another universe, the M1 lift). The TEST period (2025-07..) is untouched. If anything goes to test, it should be C1 alone, as one
   pre-registered rule on M5 (threshold 7.5 ATR), with C1b as the no-volume control.

## Appendix: full variant table (from rows.jsonl via make_table.py; excess = average over TP1-TP4)
Variants counted (excluding baseline / diagnostics / candidate repeats): M5 178 (PASS4 7), M15 178 (PASS4 3), M1 45 (PASS4 0), H1 45 (PASS4 0)

**0 baseline (all signals)** (4 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| ALL signals (baseline) | M5 | 251.9 | -1.07 | -0.95 | -0.54 | +0.77 | 1/4 |
| ALL signals (baseline) | M15 | 90.6 | -0.90 | -0.10 | -2.61 | -1.87 | 0/4 |
| ALL signals (baseline) | M1 | 1182.5 | -2.56 | -2.88 | -1.67 | -2.12 | 0/4 |
| ALL signals (baseline) | H1 | 24.3 | -6.60 | -1.38 | -2.28 | -1.03 | 0/4 |

**2a signal-bar / profile features, tercile screen (train thresholds)** (136 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| d_pct >= 0.636 | M5 | 83.1 | -2.91 | +0.81 | -1.78 | +1.10 | 2/4 |
| d_pct <= 0.531 | M5 | 83.1 | +1.70 | -1.73 | -0.24 | +0.34 | 2/4 |
| dcl_pct >= 0.46 | M5 | 83.1 | -0.38 | -1.01 | -1.46 | -0.74 | 0/4 |
| dcl_pct <= 0.275 | M5 | 83.1 | -1.82 | -0.49 | -2.06 | +0.07 | 1/4 |
| v_r20 >= 1.26 | M5 | 83.1 | -0.50 | -0.31 | -0.24 | +1.20 | 1/4 |
| v_r20 <= 1.01 | M5 | 83.1 | -0.70 | -1.97 | -0.78 | -3.01 | 0/4 |
| v_tod >= 1.13 | M5 | 82.6 | -0.67 | -1.37 | +0.36 | +0.97 | 2/4 |
| v_tod <= 0.951 | M5 | 82.6 | -1.12 | -0.61 | -2.83 | +0.83 | 1/4 |
| eff_res >= 0.907 | M5 | 82.6 | -0.28 | -2.72 | +1.80 | -1.33 | 1/4 |
| eff_res <= 0.632 | M5 | 82.6 | -3.10 | -0.44 | -0.62 | +3.19 | 1/4 |
| vmax3_tod >= 1.18 | M5 | 82.6 | -0.21 | -1.49 | -0.14 | +1.00 | 1/4 |
| vmax3_tod <= 0.997 | M5 | 82.6 | -1.59 | -2.03 | -2.79 | +0.89 | 1/4 |
| cvd5_pct >= 0.305 | M5 | 83.1 | -1.90 | -0.77 | -0.58 | +1.83 | 1/4 |
| cvd5_pct <= 0.167 | M5 | 83.1 | -1.07 | -2.14 | -1.15 | +0.06 | 1/4 |
| cvd20_pct >= 0.133 | M5 | 83.1 | -1.58 | +0.13 | +0.78 | +2.11 | 3/4 |
| cvd20_pct <= 0.0558 | M5 | 83.1 | -1.54 | -2.22 | -1.55 | +0.81 | 1/4 |
| pre5_pct >= 0.207 | M5 | 83.1 | -0.34 | -0.95 | +0.70 | +0.55 | 2/4 |
| pre5_pct <= 0.0564 | M5 | 83.1 | -1.79 | -0.69 | -0.68 | -0.20 | 0/4 |
| scvd_pct >= 0.0543 | M5 | 83.1 | -0.09 | -0.59 | -1.46 | +1.90 | 1/4 |
| scvd_pct <= 0.0155 | M5 | 83.1 | -1.16 | -2.30 | -2.58 | +0.43 | 1/4 |
| scvd_cl_pct >= 0.036 | M5 | 83.1 | -1.71 | -1.07 | -0.49 | +1.92 | 1/4 |
| scvd_cl_pct <= 0.00346 | M5 | 83.1 | +0.04 | -2.55 | +0.51 | +1.80 | 3/4 |
| cvd_new6 >= 0.649 | M5 | 83.1 | -2.25 | +1.66 | -0.11 | +1.64 | 2/4 |
| cvd_new6 <= 0.23 | M5 | 83.1 | -0.21 | -2.34 | +1.02 | -1.56 | 1/4 |
| cvd_new20 >= 0.552 | M5 | 83.1 | -1.71 | +1.29 | +0.67 | +2.46 | 3/4 |
| cvd_new20 <= -0.0195 | M5 | 83.1 | -2.07 | -2.28 | -1.80 | +0.53 | 1/4 |
| e_ppoc_a >= 7.99 | M5 | 83.1 | -2.61 | -1.47 | -1.33 | -0.06 | 0/4 |
| e_ppoc_a <= 0.742 | M5 | 83.1 | +0.03 | -1.38 | -1.21 | +0.60 | 2/4 |
| e_dpoc_a >= 3.97 | M5 | 83.1 | -2.73 | -2.54 | -0.32 | -1.82 | 0/4 |
| e_dpoc_a <= 1.77 | M5 | 83.1 | -0.91 | +0.09 | -1.87 | +1.12 | 2/4 |
| e_pva_edge_a >= 5.98 | M5 | 83.1 | -3.34 | -1.98 | -1.92 | -0.99 | 0/4 |
| e_pva_edge_a <= 2.38 | M5 | 83.1 | -0.19 | -1.13 | -2.67 | +2.46 | 1/4 |
| e_dva_edge_a >= 1.93 | M5 | 83.1 | -2.76 | -0.67 | -0.12 | -1.33 | 0/4 |
| e_dva_edge_a <= 0.631 | M5 | 83.1 | +0.48 | +0.94 | -1.80 | +1.14 | 3/4 |
| pva_w_a >= 13.4 | M5 | 83.1 | -3.32 | -1.94 | -0.01 | -2.72 | 0/4 |
| pva_w_a <= 7.49 | M5 | 83.1 | +1.71 | +0.80 | +1.28 | +4.19 | **PASS4** |
| rvp_e_dev >= 0.87 | M5 | 83.1 | -2.21 | -0.48 | -0.59 | +0.84 | 1/4 |
| rvp_e_dev <= 0.274 | M5 | 83.1 | -1.37 | -1.93 | -0.28 | +3.66 | 1/4 |
| rvp_e_prior >= 1.1 | M5 | 83.1 | -1.07 | -0.87 | -2.71 | +1.59 | 1/4 |
| rvp_e_prior <= 0.112 | M5 | 83.1 | -0.50 | -0.06 | +1.31 | +1.04 | 2/4 |
| rvp_s_dev >= 1.77 | M5 | 83.1 | +0.40 | -0.48 | -1.03 | +1.70 | 2/4 |
| rvp_s_dev <= 0.982 | M5 | 83.1 | -1.50 | -0.71 | +0.74 | -0.21 | 1/4 |
| rvp_s_prior >= 1.23 | M5 | 83.1 | -1.67 | -0.81 | -0.08 | +1.63 | 1/4 |
| rvp_s_prior <= 0.253 | M5 | 83.1 | -1.23 | -0.22 | +1.47 | -0.15 | 1/4 |
| p1_max_dev >= 0.675 | M5 | 83.1 | -2.86 | -1.34 | -0.48 | -0.45 | 0/4 |
| p1_max_dev <= 0.166 | M5 | 83.1 | -1.31 | -2.15 | -1.04 | +2.87 | 1/4 |
| p1_mean_dev >= 0.425 | M5 | 83.1 | -2.06 | -0.74 | -1.37 | -0.53 | 0/4 |
| p1_mean_dev <= 0.0846 | M5 | 83.1 | -1.09 | -2.44 | -0.30 | +1.99 | 1/4 |
| p4_max_dev >= 0.712 | M5 | 83.1 | -2.40 | -1.55 | -0.81 | -1.06 | 0/4 |
| p4_max_dev <= 0.167 | M5 | 83.1 | -1.41 | -2.04 | -1.01 | +2.75 | 1/4 |
| p4_mean_dev >= 0.184 | M5 | 83.1 | -2.32 | -1.36 | -2.17 | -1.16 | 0/4 |
| p4_mean_dev <= 0.0296 | M5 | 83.1 | -1.43 | -2.41 | -0.63 | +2.60 | 1/4 |
| ps_max_dev >= 2.23 | M5 | 83.1 | -1.66 | +0.60 | -0.74 | +0.93 | 2/4 |
| ps_max_dev <= 1.39 | M5 | 83.1 | -0.66 | -2.38 | -0.32 | +1.31 | 1/4 |
| ps_mean_dev >= 1.57 | M5 | 83.1 | -0.86 | +0.13 | -1.35 | +0.91 | 2/4 |
| ps_mean_dev <= 0.917 | M5 | 83.1 | -1.19 | -2.32 | +1.33 | +1.67 | 2/4 |
| p1_max_prior >= 1.29 | M5 | 83.1 | -0.45 | -0.96 | -3.03 | +1.81 | 1/4 |
| p1_max_prior <= 0.142 | M5 | 83.1 | -0.76 | -0.30 | +0.78 | +1.51 | 2/4 |
| p1_mean_prior >= 1.04 | M5 | 83.1 | -0.46 | -0.52 | -1.97 | +2.27 | 1/4 |
| p1_mean_prior <= 0.089 | M5 | 83.1 | -0.96 | -0.06 | +0.44 | +1.83 | 2/4 |
| p4_max_prior >= 1.66 | M5 | 83.1 | -0.05 | -1.51 | -1.40 | +1.48 | 1/4 |
| p4_max_prior <= 0.225 | M5 | 83.1 | -1.13 | -0.24 | +0.66 | +2.53 | 2/4 |
| p4_mean_prior >= 0.929 | M5 | 83.1 | +0.05 | -1.30 | -1.41 | +0.38 | 2/4 |
| p4_mean_prior <= 0.0667 | M5 | 83.1 | -1.20 | -0.41 | +0.37 | +1.64 | 2/4 |
| ps_max_prior >= 1.69 | M5 | 83.1 | -1.45 | -1.18 | -1.76 | +2.03 | 1/4 |
| ps_max_prior <= 0.473 | M5 | 83.1 | -1.01 | -0.57 | +1.06 | +1.17 | 2/4 |
| ps_mean_prior >= 1.21 | M5 | 83.1 | -1.20 | -1.54 | -2.27 | +3.35 | 1/4 |
| ps_mean_prior <= 0.268 | M5 | 83.1 | -0.64 | -0.04 | +1.01 | +1.41 | 2/4 |
| d_pct >= 0.398 | M15 | 29.9 | -2.16 | +2.18 | -1.22 | -1.74 | 1/4 |
| d_pct <= 0.231 | M15 | 29.9 | -0.25 | -0.66 | -4.49 | -2.89 | 0/4 |
| dcl_pct >= 0.252 | M15 | 29.9 | +0.75 | +4.60 | +0.31 | +2.32 | **PASS4** |
| dcl_pct <= 0.135 | M15 | 29.9 | -1.58 | -2.24 | -5.85 | -0.38 | 0/4 |
| v_r20 >= 1.41 | M15 | 29.9 | -1.09 | +3.34 | +0.25 | -0.61 | 2/4 |
| v_r20 <= 1.09 | M15 | 29.9 | -0.93 | -2.26 | -3.76 | -3.37 | 0/4 |
| v_tod >= 1.13 | M15 | 29.8 | +0.55 | -0.96 | -2.63 | -3.27 | 1/4 |
| v_tod <= 0.961 | M15 | 29.8 | -3.33 | +1.33 | -5.42 | +1.16 | 2/4 |
| eff_res >= 0.87 | M15 | 29.8 | -0.62 | -3.74 | +0.29 | -1.46 | 1/4 |
| eff_res <= 0.607 | M15 | 29.8 | -0.44 | +4.94 | -3.53 | -0.89 | 1/4 |
| vmax3_tod >= 1.17 | M15 | 29.8 | -0.53 | -0.37 | -1.52 | -3.97 | 0/4 |
| vmax3_tod <= 0.996 | M15 | 29.8 | -2.59 | +0.93 | -6.81 | +2.43 | 2/4 |
| cvd5_pct >= 0.179 | M15 | 29.9 | +0.03 | +0.14 | -0.78 | -0.18 | 2/4 |
| cvd5_pct <= 0.0975 | M15 | 29.9 | -0.57 | -0.28 | -3.40 | -2.28 | 0/4 |
| cvd20_pct >= 0.0762 | M15 | 29.9 | -2.45 | -2.93 | +0.18 | +2.01 | 2/4 |
| cvd20_pct <= 0.0296 | M15 | 29.9 | +0.30 | +2.75 | -4.86 | -1.68 | 2/4 |
| pre5_pct >= 0.121 | M15 | 29.9 | +0.83 | -0.33 | +0.64 | -2.20 | 2/4 |
| pre5_pct <= 0.0334 | M15 | 29.9 | -2.24 | -1.17 | -6.63 | -3.88 | 0/4 |
| scvd_pct >= 0.0604 | M15 | 29.9 | -0.46 | -0.85 | -2.57 | +1.85 | 1/4 |
| scvd_pct <= 0.0204 | M15 | 29.9 | -1.27 | +0.55 | -2.12 | -3.21 | 1/4 |
| scvd_cl_pct >= 0.0388 | M15 | 29.9 | -0.37 | -0.13 | -0.52 | -1.55 | 0/4 |
| scvd_cl_pct <= 0.00634 | M15 | 29.9 | +0.27 | -2.53 | -6.93 | -2.74 | 1/4 |
| cvd_new6 >= 0.399 | M15 | 29.9 | -0.41 | +3.20 | +0.26 | +0.76 | 3/4 |
| cvd_new6 <= 0.159 | M15 | 29.9 | -1.31 | -1.96 | -4.82 | -2.59 | 0/4 |
| cvd_new20 >= 0.312 | M15 | 29.9 | -1.83 | +2.40 | +0.52 | -1.78 | 2/4 |
| cvd_new20 <= -0.0419 | M15 | 29.9 | -2.33 | -0.07 | -5.18 | -2.74 | 0/4 |
| e_ppoc_a >= 5.04 | M15 | 29.9 | +1.51 | +3.12 | -3.23 | -0.29 | 2/4 |
| e_ppoc_a <= 1.02 | M15 | 29.9 | -2.52 | -2.42 | -3.10 | -0.42 | 0/4 |
| e_dpoc_a >= 2.57 | M15 | 29.9 | -2.52 | -0.49 | +0.21 | -5.23 | 1/4 |
| e_dpoc_a <= 1.3 | M15 | 29.9 | -0.99 | -0.74 | -3.46 | -0.77 | 0/4 |
| e_pva_edge_a >= 3.48 | M15 | 29.9 | -2.03 | +1.68 | -2.21 | -0.21 | 1/4 |
| e_pva_edge_a <= 1.4 | M15 | 29.9 | -0.44 | -2.35 | -7.37 | -1.16 | 0/4 |
| e_dva_edge_a >= 1.22 | M15 | 29.9 | -1.14 | -0.57 | -1.41 | -5.42 | 0/4 |
| e_dva_edge_a <= 0.408 | M15 | 29.9 | -0.48 | +0.97 | -3.57 | -0.46 | 1/4 |
| pva_w_a >= 7.22 | M15 | 29.9 | -0.84 | -3.35 | -3.17 | +1.85 | 1/4 |
| pva_w_a <= 4.19 | M15 | 29.9 | -1.54 | -0.90 | +1.04 | -2.96 | 1/4 |
| rvp_e_dev >= 0.605 | M15 | 29.9 | -1.03 | -1.73 | -3.56 | +0.84 | 1/4 |
| rvp_e_dev <= 0.235 | M15 | 29.9 | -0.55 | +0.56 | -1.58 | -3.34 | 1/4 |
| rvp_e_prior >= 0.993 | M15 | 29.9 | -1.04 | +0.20 | -6.33 | -6.10 | 1/4 |
| rvp_e_prior <= 0.0548 | M15 | 29.9 | -1.03 | -0.69 | +0.96 | +1.23 | 2/4 |
| rvp_s_dev >= 1.7 | M15 | 29.9 | +0.85 | +0.56 | -5.77 | +0.00 | 2/4 |
| rvp_s_dev <= 0.862 | M15 | 29.9 | -1.74 | +0.63 | -0.20 | -4.42 | 1/4 |
| rvp_s_prior >= 1.28 | M15 | 29.9 | -2.06 | +0.22 | -6.46 | -4.55 | 1/4 |
| rvp_s_prior <= 0.3 | M15 | 29.9 | -2.03 | +0.70 | +1.73 | +1.17 | 3/4 |
| p1_max_dev >= 0.539 | M15 | 29.9 | -2.40 | +1.18 | -3.59 | +2.79 | 2/4 |
| p1_max_dev <= 0.217 | M15 | 29.9 | -0.51 | -1.75 | -0.88 | -4.81 | 0/4 |
| p1_mean_dev >= 0.238 | M15 | 29.9 | -1.29 | +0.95 | -4.76 | +0.54 | 2/4 |
| p1_mean_dev <= 0.0861 | M15 | 29.9 | -2.03 | -1.20 | -0.75 | -2.85 | 0/4 |
| p4_max_dev >= 0.549 | M15 | 29.9 | -2.17 | +0.87 | -4.29 | +2.60 | 2/4 |
| p4_max_dev <= 0.219 | M15 | 29.9 | -0.56 | -1.80 | -0.55 | -4.70 | 0/4 |
| p4_mean_dev >= 0.0821 | M15 | 29.9 | -1.32 | +1.09 | -4.60 | +0.57 | 2/4 |
| p4_mean_dev <= 0.0291 | M15 | 29.9 | -1.78 | -1.92 | -0.88 | -3.38 | 0/4 |
| ps_max_dev >= 2.53 | M15 | 29.9 | -1.12 | +2.04 | -5.01 | -0.69 | 1/4 |
| ps_max_dev <= 1.78 | M15 | 29.9 | -1.44 | -1.74 | +2.10 | -4.71 | 1/4 |
| ps_mean_dev >= 1.48 | M15 | 29.9 | -0.62 | -1.20 | -4.53 | +2.29 | 1/4 |
| ps_mean_dev <= 0.995 | M15 | 29.9 | -1.74 | -1.66 | +0.40 | -4.28 | 1/4 |
| p1_max_prior >= 1.3 | M15 | 29.9 | -0.98 | -0.73 | -4.46 | -6.65 | 0/4 |
| p1_max_prior <= 0.0634 | M15 | 29.9 | -1.19 | -0.28 | +0.17 | -0.46 | 1/4 |
| p1_mean_prior >= 0.913 | M15 | 29.9 | -1.73 | -1.98 | -4.33 | -7.17 | 0/4 |
| p1_mean_prior <= 0.021 | M15 | 29.9 | -0.89 | -0.21 | -0.12 | -0.79 | 0/4 |
| p4_max_prior >= 1.75 | M15 | 29.9 | -2.88 | -0.99 | -5.50 | -4.49 | 0/4 |
| p4_max_prior <= 0.0815 | M15 | 29.9 | -1.23 | +0.12 | -0.00 | -1.16 | 1/4 |
| p4_mean_prior >= 0.753 | M15 | 29.9 | -3.91 | +0.13 | -4.55 | -4.64 | 1/4 |
| p4_mean_prior <= 0.0097 | M15 | 29.9 | -1.22 | +0.07 | -0.41 | -1.20 | 1/4 |
| ps_max_prior >= 1.98 | M15 | 29.9 | -2.64 | -1.01 | -8.56 | -7.60 | 0/4 |
| ps_max_prior <= 0.736 | M15 | 29.9 | -0.58 | +1.27 | +1.60 | +1.13 | 3/4 |
| ps_mean_prior >= 1.22 | M15 | 29.9 | -1.18 | +0.96 | -7.67 | -7.54 | 1/4 |
| ps_mean_prior <= 0.336 | M15 | 29.9 | -0.06 | +0.83 | +1.38 | +0.15 | 3/4 |

**2b categorical order-flow / profile rules** (74 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| loc_e_prior == 1 | M5 | 119.4 | -1.90 | -0.58 | -0.04 | +0.88 | 1/4 |
| loc_e_prior == 0 | M5 | 100.7 | -1.54 | -1.98 | -0.81 | +0.96 | 1/4 |
| loc_e_prior == -1 | M5 | 31.6 | +3.91 | +0.72 | -2.45 | -0.04 | 2/4 |
| loc_c_prior == 1 | M5 | 125.2 | -2.04 | -0.75 | -0.30 | +1.30 | 1/4 |
| loc_c_prior == 0 | M5 | 97.4 | -1.22 | -1.75 | -0.64 | +0.79 | 1/4 |
| loc_c_prior == -1 | M5 | 29.0 | +3.98 | +0.69 | -1.73 | -0.96 | 2/4 |
| loc_e_dev == 1 | M5 | 177.4 | -0.47 | -0.91 | -0.04 | +0.75 | 1/4 |
| loc_e_dev == 0 | M5 | 74.4 | -2.47 | -1.05 | -1.88 | +0.82 | 1/4 |
| loc_e_dev == -1 | M5 | 0.0 | +nan | +nan | +nan | +nan | n/a |
| loc_c_dev == 1 | M5 | 202.6 | -0.71 | -0.81 | -0.01 | +0.88 | 1/4 |
| loc_c_dev == 0 | M5 | 49.2 | -2.57 | -1.56 | -2.90 | +0.39 | 1/4 |
| loc_c_dev == -1 | M5 | 0.0 | +nan | +nan | +nan | +nan | n/a |
| rvp_e_prior < 0.5 (LVN) | M5 | 120.0 | -1.46 | -0.70 | +0.34 | +1.07 | 2/4 |
| rvp_e_prior > 1.5 (HVN) | M5 | 56.1 | -1.57 | -0.17 | -0.73 | +2.58 | 1/4 |
| rvp_e_dev < 0.5 (LVN) | M5 | 123.9 | -1.37 | -0.95 | +0.15 | +2.01 | 2/4 |
| rvp_e_dev > 1.5 (HVN) | M5 | 36.3 | -1.86 | -0.18 | +2.17 | +0.36 | 2/4 |
| rvp_s_prior < 0.5 (LVN) | M5 | 105.4 | -1.32 | -0.57 | +0.94 | -0.79 | 1/4 |
| rvp_s_prior > 1.5 (HVN) | M5 | 64.0 | -1.24 | -0.48 | -0.78 | +0.50 | 1/4 |
| rvp_s_dev < 0.5 (LVN) | M5 | 36.6 | -0.85 | +0.84 | +0.85 | -2.94 | 2/4 |
| rvp_s_dev > 1.5 (HVN) | M5 | 112.3 | -0.27 | -0.15 | -1.26 | +0.41 | 1/4 |
| p1_max_prior < 0.5 (LVN) | M5 | 111.8 | -1.61 | -0.88 | +0.25 | +0.64 | 2/4 |
| p1_max_prior > 1.5 (HVN) | M5 | 69.0 | -0.47 | -0.81 | -1.05 | +1.26 | 1/4 |
| p4_max_prior < 0.5 (LVN) | M5 | 98.3 | -2.24 | -0.93 | +0.74 | +0.56 | 2/4 |
| p4_max_prior > 1.5 (HVN) | M5 | 93.0 | -0.27 | -1.12 | -0.86 | +0.95 | 1/4 |
| ps_max_prior < 0.5 (LVN) | M5 | 85.0 | -0.84 | -0.70 | +1.03 | +1.24 | 2/4 |
| ps_max_prior > 1.5 (HVN) | M5 | 95.9 | -1.66 | -1.29 | -1.12 | +1.46 | 1/4 |
| ps_max_dev < 0.5 (LVN) | M5 | 17.7 | -1.23 | +0.16 | +3.16 | -1.47 | too few |
| ps_max_dev > 1.5 (HVN) | M5 | 159.6 | -1.12 | -0.28 | -1.16 | +0.48 | 1/4 |
| delta agrees (d_pct > 0) | M5 | 245.5 | -1.07 | -1.00 | -0.46 | +0.75 | 1/4 |
| delta disagrees (d_pct <= 0) | M5 | 6.4 | -0.94 | +0.75 | -4.08 | +2.13 | too few |
| CVD divergence 20 (price new, CVD not) | M5 | 59.0 | -0.44 | -3.08 | -1.95 | +0.61 | 1/4 |
| no CVD divergence 20 | M5 | 192.9 | -1.26 | -0.32 | -0.13 | +0.82 | 1/4 |
| climax volume v_tod > 2 | M5 | 4.3 | -2.66 | +3.23 | -7.55 | -0.04 | too few |
| low volume v_tod < 0.8 | M5 | 36.5 | -0.37 | +1.76 | -2.57 | +3.24 | 2/4 |
| absorption eff_res > 1.5 | M5 | 8.2 | -0.22 | -3.26 | +1.23 | -0.78 | too few |
| session CVD agrees | M5 | 202.6 | -1.44 | -0.52 | -0.21 | +0.68 | 1/4 |
| session CVD disagrees | M5 | 49.3 | +0.52 | -2.70 | -2.49 | +1.03 | 2/4 |
| loc_e_prior == 1 | M15 | 46.6 | +0.77 | +1.61 | -1.69 | -0.89 | 2/4 |
| loc_e_prior == 0 | M15 | 33.9 | -3.16 | -1.55 | -2.83 | -6.38 | 0/4 |
| loc_e_prior == -1 | M15 | 10.0 | -1.16 | -2.95 | -8.07 | +8.98 | 1/4 |
| loc_c_prior == 1 | M15 | 49.6 | +0.95 | +1.89 | -2.08 | -1.43 | 2/4 |
| loc_c_prior == 0 | M15 | 32.4 | -3.98 | -2.59 | -1.70 | -5.87 | 0/4 |
| loc_c_prior == -1 | M15 | 8.6 | -0.21 | -2.02 | -9.92 | +9.91 | 1/4 |
| loc_e_dev == 1 | M15 | 74.3 | -0.46 | -0.44 | -2.37 | -2.84 | 0/4 |
| loc_e_dev == 0 | M15 | 16.2 | -2.78 | +1.55 | -3.62 | +2.90 | 2/4 |
| loc_e_dev == -1 | M15 | 0.0 | +nan | +nan | +nan | +nan | n/a |
| loc_c_dev == 1 | M15 | 82.4 | -0.72 | -0.36 | -2.62 | -2.91 | 0/4 |
| loc_c_dev == 0 | M15 | 8.1 | -2.67 | +2.54 | -2.57 | +8.79 | 2/4 |
| loc_c_dev == -1 | M15 | 0.0 | +nan | +nan | +nan | +nan | n/a |
| rvp_e_prior < 0.5 (LVN) | M15 | 45.6 | -0.68 | -0.17 | -0.00 | -0.23 | 0/4 |
| rvp_e_prior > 1.5 (HVN) | M15 | 18.1 | -1.85 | +0.15 | -4.44 | -8.41 | 1/4 |
| rvp_e_dev < 0.5 (LVN) | M15 | 53.2 | -1.21 | +0.69 | -2.14 | -2.68 | 1/4 |
| rvp_e_dev > 1.5 (HVN) | M15 | 5.0 | +2.70 | +9.08 | -1.88 | +7.17 | too few |
| rvp_s_prior < 0.5 (LVN) | M15 | 36.0 | -2.05 | -0.27 | +0.87 | +1.03 | 2/4 |
| rvp_s_prior > 1.5 (HVN) | M15 | 23.8 | -2.48 | -0.26 | -9.19 | -3.83 | 0/4 |
| rvp_s_dev < 0.5 (LVN) | M15 | 17.0 | -0.27 | +2.07 | -1.16 | -6.59 | 1/4 |
| rvp_s_dev > 1.5 (HVN) | M15 | 37.2 | +1.13 | -0.41 | -4.21 | -0.62 | 1/4 |
| p1_max_prior < 0.5 (LVN) | M15 | 40.9 | -0.61 | +0.30 | -0.06 | -0.75 | 1/4 |
| p1_max_prior > 1.5 (HVN) | M15 | 25.2 | -2.18 | -0.02 | -6.55 | -7.83 | 0/4 |
| p4_max_prior < 0.5 (LVN) | M15 | 36.6 | -1.02 | +1.44 | -0.37 | -2.29 | 1/4 |
| p4_max_prior > 1.5 (HVN) | M15 | 35.1 | -1.43 | -1.28 | -4.67 | -4.09 | 0/4 |
| ps_max_prior < 0.5 (LVN) | M15 | 25.6 | -0.50 | +1.06 | +1.87 | +0.45 | 3/4 |
| ps_max_prior > 1.5 (HVN) | M15 | 42.0 | -3.08 | +0.16 | -6.56 | -6.68 | 1/4 |
| ps_max_dev < 0.5 (LVN) | M15 | 3.1 | +5.51 | +5.94 | +10.90 | -3.66 | too few |
| ps_max_dev > 1.5 (HVN) | M15 | 69.3 | -0.68 | -0.14 | -4.23 | -0.82 | 0/4 |
| delta agrees (d_pct > 0) | M15 | 86.9 | -0.65 | -0.11 | -2.57 | -1.99 | 0/4 |
| delta disagrees (d_pct <= 0) | M15 | 3.7 | -6.21 | +0.18 | -3.80 | +0.56 | too few |
| CVD divergence 20 (price new, CVD not) | M15 | 23.5 | -1.16 | -1.29 | -5.06 | -3.04 | 0/4 |
| no CVD divergence 20 | M15 | 67.1 | -0.80 | +0.29 | -1.81 | -1.44 | 1/4 |
| climax volume v_tod > 2 | M15 | 1.2 | -10.35 | +20.29 | -2.96 | -9.49 | too few |
| low volume v_tod < 0.8 | M15 | 12.2 | -2.78 | +3.38 | -8.95 | -0.43 | 1/4 |
| absorption eff_res > 1.5 | M15 | 2.8 | -4.55 | +1.77 | +6.77 | +4.40 | too few |
| session CVD agrees | M15 | 76.0 | -1.08 | +0.56 | -2.26 | -1.30 | 1/4 |
| session CVD disagrees | M15 | 14.6 | +0.06 | -3.41 | -5.26 | -3.72 | 1/4 |

**3a pullback state at fill (diagnostic only, NOT a rule)** (18 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| DIAG fill in 1st minute | M5 | 84.8 | -1.69 | -1.35 | -0.53 | -1.41 | 0/4 |
| DIAG fill after 1-5 min | M5 | 102.6 | -1.06 | -1.89 | -0.37 | +3.51 | 1/4 |
| DIAG fill after >5 min | M5 | 64.5 | -0.30 | +1.07 | -0.85 | -0.62 | 1/4 |
| DIAG pb vol rate <= 0.94 (k>=3) | M5 | 35.0 | -1.82 | +1.29 | -3.83 | -1.16 | 1/4 |
| DIAG pb vol rate mid (k>=3) | M5 | 35.0 | -1.25 | -2.80 | +0.29 | -0.29 | 1/4 |
| DIAG pb vol rate >= 1.03 (k>=3) | M5 | 35.0 | +1.69 | +1.89 | +1.03 | -2.55 | 3/4 |
| DIAG pb delta against % <= -0.01 (k>=3) | M5 | 35.0 | -1.18 | +1.65 | -1.69 | -1.18 | 1/4 |
| DIAG pb delta against % mid (k>=3) | M5 | 35.0 | +1.64 | -0.33 | +2.59 | -2.66 | 2/4 |
| DIAG pb delta against % >= 0.22 (k>=3) | M5 | 35.0 | -1.83 | -1.03 | -2.92 | -0.22 | 0/4 |
| DIAG fill in 1st minute | M15 | 16.1 | +1.01 | -5.41 | -0.16 | -4.57 | 1/4 |
| DIAG fill after 1-5 min | M15 | 27.2 | -2.77 | -0.42 | -2.82 | +0.08 | 1/4 |
| DIAG fill after >5 min | M15 | 47.3 | -0.56 | +1.92 | -3.24 | -2.21 | 1/4 |
| DIAG pb vol rate <= 0.95 (k>=3) | M15 | 20.1 | -2.79 | +1.49 | -1.46 | -7.42 | 1/4 |
| DIAG pb vol rate mid (k>=3) | M15 | 20.1 | -0.51 | +1.69 | -2.05 | -1.53 | 1/4 |
| DIAG pb vol rate >= 1.04 (k>=3) | M15 | 20.1 | +1.14 | +0.86 | -3.95 | +1.80 | 3/4 |
| DIAG pb delta against % <= 0.03 (k>=3) | M15 | 20.1 | -3.58 | +2.18 | -4.27 | +1.01 | 2/4 |
| DIAG pb delta against % mid (k>=3) | M15 | 20.1 | +0.05 | +0.99 | -2.55 | -5.91 | 2/4 |
| DIAG pb delta against % >= 0.23 (k>=3) | M15 | 20.1 | +1.37 | +0.90 | -0.06 | -2.24 | 2/4 |

**3b pullback CANCEL rules** (32 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| CXL 1m-close pb vol rate > 1.0 | M5 | 171.7 | -1.74 | -1.59 | -0.31 | +0.50 | 1/4 |
| CXL 1m-close pb vol rate > 0.7 | M5 | 125.4 | -1.14 | -2.08 | -0.41 | +0.67 | 1/4 |
| CXL 1m-close pb vol rate > 0.5 | M5 | 123.8 | -1.08 | -2.20 | -0.12 | +0.65 | 1/4 |
| CXL 1m-close pb delta against > 0.3 | M5 | 208.8 | -1.04 | -1.11 | -0.12 | +1.43 | 1/4 |
| CXL 1m-close pb delta against > 0.5 | M5 | 235.8 | -1.06 | -1.11 | -0.27 | +0.91 | 1/4 |
| CXL 1m-close pb quiet vol rate < 0.3 | M5 | 251.8 | -1.08 | -0.98 | -0.54 | +0.77 | 1/4 |
| CXL 1m-close pb delta in favour > 0.3 | M5 | 196.8 | -1.51 | -1.50 | -0.92 | +1.53 | 1/4 |
| CXL 1m-close pb delta in favour > 0.5 | M5 | 226.3 | -1.25 | -1.34 | -0.75 | +1.11 | 1/4 |
| CXL chart-close pb vol rate > 1.0 | M5 | 213.3 | -1.65 | -1.41 | -0.91 | +1.53 | 1/4 |
| CXL chart-close pb vol rate > 0.7 | M5 | 177.6 | -1.42 | -1.53 | -0.78 | +1.53 | 1/4 |
| CXL chart-close pb vol rate > 0.5 | M5 | 176.3 | -1.38 | -1.56 | -0.72 | +1.59 | 1/4 |
| CXL chart-close pb delta against > 0.3 | M5 | 241.6 | -0.99 | -1.11 | -0.31 | +0.76 | 1/4 |
| CXL chart-close pb delta against > 0.5 | M5 | 245.9 | -1.07 | -1.07 | -0.32 | +0.80 | 1/4 |
| CXL chart-close pb quiet vol rate < 0.3 | M5 | 251.8 | -1.08 | -0.95 | -0.54 | +0.77 | 1/4 |
| CXL chart-close pb delta in favour > 0.3 | M5 | 233.9 | -1.08 | -1.32 | -0.88 | +1.27 | 1/4 |
| CXL chart-close pb delta in favour > 0.5 | M5 | 239.0 | -1.12 | -1.19 | -0.75 | +1.20 | 1/4 |
| CXL 1m-close pb vol rate > 1.0 | M15 | 42.0 | -1.12 | -2.79 | -1.33 | -2.02 | 0/4 |
| CXL 1m-close pb vol rate > 0.7 | M15 | 24.5 | -1.54 | -4.35 | -2.46 | -0.89 | 0/4 |
| CXL 1m-close pb vol rate > 0.5 | M15 | 23.9 | -1.17 | -4.61 | -2.06 | -1.07 | 0/4 |
| CXL 1m-close pb delta against > 0.3 | M15 | 59.3 | -1.79 | -0.60 | -2.75 | -0.66 | 0/4 |
| CXL 1m-close pb delta against > 0.5 | M15 | 76.2 | -0.51 | -0.47 | -3.40 | -2.57 | 0/4 |
| CXL 1m-close pb quiet vol rate < 0.3 | M15 | 90.5 | -0.87 | -0.08 | -2.71 | -1.87 | 0/4 |
| CXL 1m-close pb delta in favour > 0.3 | M15 | 60.3 | -0.60 | -1.11 | -2.82 | -2.98 | 0/4 |
| CXL 1m-close pb delta in favour > 0.5 | M15 | 76.7 | -1.13 | -0.94 | -2.45 | -2.68 | 0/4 |
| CXL chart-close pb vol rate > 1.0 | M15 | 77.3 | -0.67 | -0.10 | -1.55 | -1.88 | 0/4 |
| CXL chart-close pb vol rate > 0.7 | M15 | 62.5 | -0.94 | -0.39 | -2.19 | +0.01 | 1/4 |
| CXL chart-close pb vol rate > 0.5 | M15 | 62.1 | -0.98 | -0.64 | -2.05 | +0.18 | 1/4 |
| CXL chart-close pb delta against > 0.3 | M15 | 88.9 | -1.05 | -0.05 | -2.37 | -1.84 | 0/4 |
| CXL chart-close pb delta against > 0.5 | M15 | 90.5 | -0.87 | -0.05 | -2.56 | -1.87 | 0/4 |
| CXL chart-close pb quiet vol rate < 0.3 | M15 | 90.5 | -0.87 | -0.08 | -2.66 | -1.87 | 0/4 |
| CXL chart-close pb delta in favour > 0.3 | M15 | 86.6 | -0.65 | -0.01 | -2.36 | -1.94 | 0/4 |
| CXL chart-close pb delta in favour > 0.5 | M15 | 90.1 | -0.98 | -0.10 | -2.37 | -1.87 | 0/4 |

**4 LightGBM selections** (24 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| LGBM kit top 10% | M5 | 25.2 | +2.43 | +0.15 | +0.07 | -1.90 | 3/4 |
| LGBM kit top 20% | M5 | 50.4 | +1.46 | -0.40 | +0.27 | +0.41 | 3/4 |
| LGBM kit top 30% | M5 | 75.6 | +0.25 | -0.57 | -1.38 | +1.85 | 2/4 |
| LGBM kit bottom 30% | M5 | 75.6 | -2.52 | -2.84 | -0.98 | -1.61 | 0/4 |
| LGBM kit+OF top 10% | M5 | 25.2 | +4.22 | +0.48 | -0.89 | +4.25 | 3/4 |
| LGBM kit+OF top 20% | M5 | 50.4 | +3.48 | +0.82 | -0.73 | +1.81 | 3/4 |
| LGBM kit+OF top 30% | M5 | 75.6 | +2.21 | -0.22 | -0.04 | +3.20 | 2/4 |
| LGBM kit+OF bottom 30% | M5 | 75.6 | -2.61 | -1.93 | -1.36 | -2.07 | 0/4 |
| LGBM OF+dir top 10% | M5 | 25.2 | +2.27 | -0.17 | +1.72 | -0.68 | 2/4 |
| LGBM OF+dir top 20% | M5 | 50.4 | +2.10 | +0.67 | +1.73 | +1.11 | **PASS4** |
| LGBM OF+dir top 30% | M5 | 75.6 | +1.15 | -0.97 | +1.68 | +3.92 | 3/4 |
| LGBM OF+dir bottom 30% | M5 | 75.6 | -2.84 | -2.15 | +0.99 | -2.13 | 1/4 |
| LGBM kit top 10% | M15 | 9.1 | +1.85 | -3.50 | -2.14 | -2.57 | 1/4 |
| LGBM kit top 20% | M15 | 18.1 | -1.29 | +0.00 | -3.21 | +1.31 | 1/4 |
| LGBM kit top 30% | M15 | 27.2 | -0.83 | -1.52 | -5.44 | +0.16 | 1/4 |
| LGBM kit bottom 30% | M15 | 27.2 | -0.67 | +1.16 | -2.03 | -1.33 | 1/4 |
| LGBM kit+OF top 10% | M15 | 9.1 | +1.38 | +3.19 | -1.14 | -5.60 | 2/4 |
| LGBM kit+OF top 20% | M15 | 18.1 | -1.46 | -1.62 | -5.82 | -0.61 | 0/4 |
| LGBM kit+OF top 30% | M15 | 27.2 | -3.46 | -0.53 | -3.97 | -4.57 | 0/4 |
| LGBM kit+OF bottom 30% | M15 | 27.2 | -0.44 | +0.90 | +1.63 | -2.10 | 2/4 |
| LGBM OF+dir top 10% | M15 | 9.1 | -0.12 | +0.22 | -4.31 | -4.19 | 1/4 |
| LGBM OF+dir top 20% | M15 | 18.1 | -1.43 | -1.81 | -1.17 | -2.36 | 0/4 |
| LGBM OF+dir top 30% | M15 | 27.2 | -1.54 | -2.14 | -2.89 | -0.37 | 0/4 |
| LGBM OF+dir bottom 30% | M15 | 27.2 | -1.70 | +0.03 | -1.94 | -3.23 | 1/4 |

**5 composites and combinations** (52 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| FC4 score >= train q0.50 | M5 | 125.9 | -1.10 | +1.24 | +0.39 | +1.48 | 3/4 |
| FC3 (delta only) >= train q0.50 | M5 | 125.9 | -1.49 | +1.04 | -0.37 | +0.98 | 2/4 |
| FC4 score >= train q0.67 | M5 | 83.1 | -1.49 | +0.06 | +0.64 | +2.37 | 3/4 |
| FC3 (delta only) >= train q0.67 | M5 | 83.1 | -2.13 | -0.25 | +0.08 | +1.58 | 2/4 |
| FC4 score <= q0.33 (should be bad) | M5 | 83.1 | -1.86 | -3.56 | -0.22 | -0.74 | 0/4 |
| CVD confirms 20-bar extreme (cvd_new20>0) | M5 | 166.2 | -0.47 | -0.19 | -0.01 | +0.76 | 1/4 |
| no prior-HVN entry..stop..TP4 (max<1.5) | M5 | 123.0 | -0.86 | -0.95 | -0.10 | +0.03 | 1/4 |
| no prior-HVN entry..stop | M5 | 156.0 | -0.70 | -0.75 | -0.27 | +0.29 | 1/4 |
| entry not at prior HVN (rvp<1) | M5 | 161.7 | -1.35 | -1.26 | +0.43 | +0.45 | 2/4 |
| FC4>=med & no prior-HVN | M5 | 61.4 | -0.85 | +1.82 | +1.42 | +1.52 | 3/4 |
| cvd_new20>0 & no prior-HVN | M5 | 82.7 | -0.56 | -0.54 | +0.79 | +0.96 | 2/4 |
| FC4>=med & entry beyond prior VA | M5 | 60.4 | -2.61 | +1.80 | -0.26 | +3.65 | 2/4 |
| FC4>=med & narrow prior VA | M5 | 43.0 | +0.25 | +2.31 | +2.01 | +5.61 | **PASS4** |
| FC4 score >= train q0.50 | M15 | 45.3 | -0.21 | +0.77 | +1.05 | -3.18 | 2/4 |
| FC3 (delta only) >= train q0.50 | M15 | 45.3 | -0.59 | -0.16 | +0.14 | -2.24 | 1/4 |
| FC4 score >= train q0.67 | M15 | 29.9 | -0.91 | -0.12 | -0.46 | +0.22 | 1/4 |
| FC3 (delta only) >= train q0.67 | M15 | 29.9 | -1.46 | +0.49 | +0.52 | -1.49 | 2/4 |
| FC4 score <= q0.33 (should be bad) | M15 | 29.9 | -0.68 | -1.50 | -6.64 | -2.74 | 0/4 |
| CVD confirms 20-bar extreme (cvd_new20>0) | M15 | 58.0 | -0.80 | -0.08 | -1.50 | -1.81 | 0/4 |
| no prior-HVN entry..stop..TP4 (max<1.5) | M15 | 36.5 | +0.41 | +1.15 | +0.57 | +2.68 | **PASS4** |
| no prior-HVN entry..stop | M15 | 48.6 | +0.98 | -0.33 | +0.12 | +2.83 | 3/4 |
| entry not at prior HVN (rvp<1) | M15 | 60.9 | -0.75 | -0.32 | -1.46 | +0.14 | 1/4 |
| FC4>=med & no prior-HVN | M15 | 20.5 | +0.61 | +2.63 | +5.59 | +0.88 | **PASS4** |
| cvd_new20>0 & no prior-HVN | M15 | 26.3 | -0.76 | +1.30 | +1.72 | +1.23 | 3/4 |
| FC4>=med & entry beyond prior VA | M15 | 24.9 | +0.55 | +2.07 | +2.15 | -2.17 | 3/4 |
| FC4>=med & narrow prior VA | M15 | 15.6 | -2.94 | +3.26 | +4.25 | -5.33 | 2/4 |
| FC4 score >= train q0.50 | M1 | 591.3 | -2.38 | -3.11 | -1.17 | -3.06 | 0/4 |
| FC3 (delta only) >= train q0.50 | M1 | 591.3 | -2.50 | -2.97 | -1.51 | -2.97 | 0/4 |
| FC4 score >= train q0.67 | M1 | 390.2 | -2.57 | -3.28 | -1.18 | -1.97 | 0/4 |
| FC3 (delta only) >= train q0.67 | M1 | 390.3 | -2.50 | -3.22 | -1.16 | -2.18 | 0/4 |
| FC4 score <= q0.33 (should be bad) | M1 | 390.2 | -2.55 | -2.58 | -1.55 | -0.99 | 0/4 |
| CVD confirms 20-bar extreme (cvd_new20>0) | M1 | 676.6 | -2.44 | -3.11 | -1.86 | -2.52 | 0/4 |
| no prior-HVN entry..stop..TP4 (max<1.5) | M1 | 727.3 | -2.22 | -2.84 | -1.77 | -2.40 | 0/4 |
| no prior-HVN entry..stop | M1 | 844.4 | -2.20 | -2.82 | -1.95 | -2.37 | 0/4 |
| entry not at prior HVN (rvp<1) | M1 | 757.9 | -2.44 | -2.78 | -1.72 | -2.29 | 0/4 |
| FC4>=med & no prior-HVN | M1 | 364.7 | -2.08 | -2.71 | -1.00 | -2.99 | 0/4 |
| cvd_new20>0 & no prior-HVN | M1 | 418.3 | -2.25 | -2.75 | -1.81 | -2.79 | 0/4 |
| FC4>=med & entry beyond prior VA | M1 | 275.8 | -2.44 | -2.34 | -0.96 | -2.38 | 0/4 |
| FC4>=med & narrow prior VA | M1 | 197.0 | -0.32 | -0.56 | -1.00 | +0.20 | 1/4 |
| FC4 score >= train q0.50 | H1 | 12.2 | -6.12 | -2.07 | -1.96 | -4.61 | 0/4 |
| FC3 (delta only) >= train q0.50 | H1 | 12.2 | -6.21 | -0.81 | -1.51 | -7.72 | 0/4 |
| FC4 score >= train q0.67 | H1 | 8.0 | -1.88 | -0.65 | +0.36 | -9.94 | 1/4 |
| FC3 (delta only) >= train q0.67 | H1 | 8.1 | -5.80 | -3.07 | -1.31 | -5.18 | 0/4 |
| FC4 score <= q0.33 (should be bad) | H1 | 8.0 | -8.27 | +1.55 | +0.37 | +2.61 | 3/4 |
| CVD confirms 20-bar extreme (cvd_new20>0) | H1 | 14.3 | -5.88 | -1.00 | -1.04 | -2.79 | 0/4 |
| no prior-HVN entry..stop..TP4 (max<1.5) | H1 | 7.4 | -9.91 | -1.12 | +0.52 | -1.44 | 1/4 |
| no prior-HVN entry..stop | H1 | 9.0 | -8.91 | -1.17 | +1.40 | -0.81 | 1/4 |
| entry not at prior HVN (rvp<1) | H1 | 19.3 | -7.12 | -0.64 | -2.48 | +1.02 | 1/4 |
| FC4>=med & no prior-HVN | H1 | 4.9 | -10.04 | -5.28 | +0.57 | -5.26 | 1/4 |
| cvd_new20>0 & no prior-HVN | H1 | 5.8 | -10.34 | -6.29 | +5.53 | -3.55 | 1/4 |
| FC4>=med & entry beyond prior VA | H1 | 8.9 | -7.52 | -4.04 | -2.67 | -4.39 | 0/4 |
| FC4>=med & narrow prior VA | H1 | 4.4 | -4.86 | +3.38 | +3.33 | +1.05 | 3/4 |

**5 controls (momentum / ATR regime)** (68 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| CONTROL mom10_a >= train median | M5 | 125.9 | -0.89 | +0.04 | -0.10 | +2.45 | 2/4 |
| CONTROL mom30_a >= train median | M5 | 125.9 | -1.93 | -1.94 | +0.87 | +0.66 | 2/4 |
| CONTROL er10 >= train median | M5 | 125.9 | -0.75 | -0.01 | -0.46 | +1.70 | 1/4 |
| mom30 lo & FC4 >= med | M5 | 34.2 | -0.00 | +0.59 | -3.43 | +0.52 | 2/4 |
| mom30 lo & FC4 < med | M5 | 49.8 | +0.58 | +0.11 | -2.41 | -2.80 | 2/4 |
| mom30 mid & FC4 >= med | M5 | 42.8 | -1.98 | +2.89 | +2.73 | +1.24 | 3/4 |
| mom30 mid & FC4 < med | M5 | 41.1 | -1.79 | -6.48 | +0.13 | +2.64 | 2/4 |
| mom30 hi & FC4 >= med | M5 | 48.9 | -1.11 | +0.18 | +0.68 | +2.47 | 3/4 |
| mom30 hi & FC4 < med | M5 | 35.1 | -2.27 | -4.23 | -2.01 | +1.23 | 1/4 |
| CONTROL mom10_a >= train median | M15 | 45.3 | +0.16 | +2.30 | -0.32 | -4.92 | 2/4 |
| CONTROL mom30_a >= train median | M15 | 45.3 | -1.66 | -1.98 | -1.94 | -2.22 | 0/4 |
| CONTROL er10 >= train median | M15 | 45.3 | -0.45 | +0.63 | -1.03 | -3.37 | 1/4 |
| mom30 lo & FC4 >= med | M15 | 12.8 | -0.49 | +5.29 | -3.17 | -3.58 | 1/4 |
| mom30 lo & FC4 < med | M15 | 17.4 | -2.08 | +0.96 | -4.63 | +1.50 | 2/4 |
| mom30 mid & FC4 >= med | M15 | 14.7 | +5.54 | -4.12 | +1.66 | -8.91 | 2/4 |
| mom30 mid & FC4 < med | M15 | 15.5 | +0.51 | -4.25 | -8.80 | -0.09 | 1/4 |
| mom30 hi & FC4 >= med | M15 | 17.9 | -4.13 | +1.86 | +2.90 | +2.29 | 3/4 |
| mom30 hi & FC4 < med | M15 | 12.3 | -3.23 | +0.96 | -5.34 | -4.39 | 1/4 |
| CONTROL mom10_a >= train median | M1 | 591.3 | -2.97 | -3.70 | -1.06 | -1.74 | 0/4 |
| CONTROL mom30_a >= train median | M1 | 591.3 | -2.54 | -4.07 | -1.50 | -1.96 | 0/4 |
| CONTROL er10 >= train median | M1 | 591.3 | -3.03 | -3.51 | -1.15 | -1.53 | 0/4 |
| mom30 lo & FC4 >= med | M1 | 152.2 | -2.67 | -0.86 | -0.67 | -2.69 | 0/4 |
| mom30 lo & FC4 < med | M1 | 242.0 | -2.47 | -1.22 | -3.50 | -2.07 | 0/4 |
| mom30 mid & FC4 >= med | M1 | 195.4 | -2.23 | -2.57 | -1.40 | -3.35 | 0/4 |
| mom30 mid & FC4 < med | M1 | 198.7 | -3.02 | -3.24 | +0.02 | +0.66 | 2/4 |
| mom30 hi & FC4 >= med | M1 | 243.6 | -2.32 | -5.04 | -1.28 | -3.08 | 0/4 |
| mom30 hi & FC4 < med | M1 | 150.6 | -2.80 | -4.24 | -2.94 | -1.85 | 0/4 |
| CONTROL mom10_a >= train median | H1 | 12.2 | -5.55 | -3.36 | -0.13 | -3.11 | 0/4 |
| CONTROL mom30_a >= train median | H1 | 12.2 | -9.65 | -0.60 | -1.32 | +0.61 | 1/4 |
| CONTROL er10 >= train median | H1 | 12.2 | -5.58 | -2.15 | -1.83 | +1.33 | 1/4 |
| mom30 lo & FC4 >= med | H1 | 3.1 | +0.15 | -1.05 | -2.28 | -1.92 | 1/4 |
| mom30 lo & FC4 < med | H1 | 5.0 | -5.34 | -2.98 | -1.00 | +1.21 | 1/4 |
| mom30 mid & FC4 >= med | H1 | 4.2 | -4.17 | +0.51 | +0.84 | -18.05 | 2/4 |
| mom30 mid & FC4 < med | H1 | 3.9 | -7.74 | -4.45 | -7.04 | +4.92 | 1/4 |
| mom30 hi & FC4 >= med | H1 | 4.9 | -11.59 | -4.60 | -3.49 | +3.23 | 1/4 |
| mom30 hi & FC4 < med | H1 | 3.2 | -8.81 | +8.55 | -0.56 | -0.31 | 1/4 |
| CONTROL atr_d >= q2/3 (kit) | M5 | 82.7 | +1.20 | -0.39 | +1.52 | +2.49 | 3/4 |
| CONTROL atr_r100 >= q2/3 (kit) | M5 | 83.9 | +1.20 | -1.28 | +1.91 | +3.88 | 3/4 |
| atr_d lo & pva_w_a <= med(within) | M5 | 41.4 | -1.46 | +0.05 | -5.68 | -2.24 | 1/4 |
| atr_d lo & pva_w_a > med(within) | M5 | 41.3 | -2.83 | -0.79 | +2.27 | -6.54 | 1/4 |
| atr_d mid & pva_w_a <= med(within) | M5 | 41.3 | -1.97 | +1.67 | +0.42 | +4.02 | 3/4 |
| atr_d mid & pva_w_a > med(within) | M5 | 41.3 | -2.36 | -5.39 | -4.43 | +2.13 | 1/4 |
| atr_d hi & pva_w_a <= med(within) | M5 | 41.4 | +3.80 | -0.35 | +4.50 | +3.83 | 3/4 |
| atr_d hi & pva_w_a > med(within) | M5 | 41.3 | -1.35 | -0.43 | -1.03 | +1.11 | 1/4 |
| CONTROL atr_d >= q2/3 (kit) | M15 | 29.7 | +1.28 | -0.10 | -0.60 | -1.33 | 1/4 |
| CONTROL atr_r100 >= q2/3 (kit) | M15 | 30.2 | -0.25 | +0.10 | -0.97 | -3.44 | 1/4 |
| atr_d lo & pva_w_a <= med(within) | M15 | 14.9 | +0.48 | +6.96 | +2.19 | -3.72 | 3/4 |
| atr_d lo & pva_w_a > med(within) | M15 | 14.9 | -0.44 | -2.41 | -7.04 | -1.16 | 0/4 |
| atr_d mid & pva_w_a <= med(within) | M15 | 14.8 | -3.71 | +1.19 | -4.00 | -4.31 | 1/4 |
| atr_d mid & pva_w_a > med(within) | M15 | 14.8 | -3.85 | -5.74 | -5.19 | -0.14 | 0/4 |
| atr_d hi & pva_w_a <= med(within) | M15 | 14.9 | +2.08 | -2.14 | +1.51 | +3.55 | 3/4 |
| atr_d hi & pva_w_a > med(within) | M15 | 14.9 | +0.42 | +1.81 | -2.57 | -6.68 | 2/4 |
| CONTROL atr_d >= q2/3 (kit) | M1 | 387.6 | -1.09 | -1.77 | -1.68 | -1.42 | 0/4 |
| CONTROL atr_r100 >= q2/3 (kit) | M1 | 394.2 | -1.56 | -2.91 | -0.70 | -1.01 | 0/4 |
| atr_d lo & pva_w_a <= med(within) | M1 | 193.8 | -3.02 | -4.15 | -1.07 | -2.43 | 0/4 |
| atr_d lo & pva_w_a > med(within) | M1 | 193.8 | -4.02 | -4.13 | -1.14 | -4.27 | 0/4 |
| atr_d mid & pva_w_a <= med(within) | M1 | 193.8 | -2.35 | -2.17 | -1.76 | +0.70 | 1/4 |
| atr_d mid & pva_w_a > med(within) | M1 | 193.8 | -3.34 | -2.97 | -2.53 | -4.52 | 0/4 |
| atr_d hi & pva_w_a <= med(within) | M1 | 193.8 | -0.30 | -0.97 | -2.13 | -0.09 | 0/4 |
| atr_d hi & pva_w_a > med(within) | M1 | 193.8 | -1.88 | -2.58 | -1.30 | -2.75 | 0/4 |
| CONTROL atr_d >= q2/3 (kit) | H1 | 8.0 | -1.25 | -1.65 | -0.89 | -1.77 | 0/4 |
| CONTROL atr_r100 >= q2/3 (kit) | H1 | 8.1 | -5.93 | -3.02 | -0.84 | +2.96 | 1/4 |
| atr_d lo & pva_w_a <= med(within) | H1 | 4.0 | -4.73 | +0.65 | -1.83 | -4.39 | 1/4 |
| atr_d lo & pva_w_a > med(within) | H1 | 4.0 | -7.00 | -3.58 | -6.45 | -7.72 | 0/4 |
| atr_d mid & pva_w_a <= med(within) | H1 | 4.0 | -13.40 | -10.70 | +5.04 | +12.95 | 2/4 |
| atr_d mid & pva_w_a > med(within) | H1 | 4.0 | -8.28 | +6.38 | -8.66 | -2.72 | 1/4 |
| atr_d hi & pva_w_a <= med(within) | H1 | 4.0 | -4.88 | -5.28 | +0.91 | +0.80 | 2/4 |
| atr_d hi & pva_w_a > med(within) | H1 | 4.0 | +2.72 | +1.62 | -2.28 | -5.57 | 2/4 |

**5b prior value-area width** (12 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| pva_w_a <= q1/3 (narrow prior VA / ATR) | M5 | 83.9 | +1.63 | +0.83 | +1.28 | +4.17 | **PASS4** |
| pva_w_d <= q1/3 (VA width / daily ATR) | M5 | 82.7 | -0.64 | +0.40 | -0.47 | +2.76 | 2/4 |
| pva_w_d >= q2/3 | M5 | 82.7 | -3.78 | -2.57 | -1.20 | -0.77 | 0/4 |
| pva_w_a <= q1/3 (narrow prior VA / ATR) | M15 | 30.2 | -1.77 | -0.58 | +1.03 | -2.92 | 1/4 |
| pva_w_d <= q1/3 (VA width / daily ATR) | M15 | 29.7 | -1.33 | +2.58 | -1.66 | -2.43 | 1/4 |
| pva_w_d >= q2/3 | M15 | 29.7 | -0.67 | -2.59 | -4.05 | -2.76 | 0/4 |
| pva_w_a <= q1/3 (narrow prior VA / ATR) | M1 | 393.8 | -1.15 | -1.27 | -1.77 | +0.66 | 1/4 |
| pva_w_d <= q1/3 (VA width / daily ATR) | M1 | 388.4 | -2.56 | -2.19 | -1.45 | +0.54 | 1/4 |
| pva_w_d >= q2/3 | M1 | 387.7 | -3.36 | -3.72 | -1.55 | -3.82 | 0/4 |
| pva_w_a <= q1/3 (narrow prior VA / ATR) | H1 | 8.1 | -6.58 | -1.33 | -0.17 | +5.66 | 1/4 |
| pva_w_d <= q1/3 (VA width / daily ATR) | H1 | 8.0 | -8.60 | +0.70 | -1.24 | +7.76 | 2/4 |
| pva_w_d >= q2/3 | H1 | 8.0 | -5.05 | -1.41 | -3.57 | +3.04 | 1/4 |

**6b prior range vs value area** (48 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| low  prior VA width / ATR | M5 | 83.9 | +1.63 | +0.83 | +1.28 | +4.17 | **PASS4** |
| high prior VA width / ATR | M5 | 83.9 | -3.42 | -2.02 | -0.24 | -2.66 | 0/4 |
| low  prior RANGE / ATR (no volume) | M5 | 83.9 | +1.84 | +0.65 | +1.89 | +2.70 | **PASS4** |
| high prior RANGE / ATR (no volume) | M5 | 83.9 | -5.06 | -2.02 | -1.04 | -2.92 | 0/4 |
| low  VA width / prior range | M5 | 84.0 | +0.46 | +0.18 | -0.21 | +3.71 | 3/4 |
| high VA width / prior range | M5 | 84.1 | -2.47 | -2.83 | +0.68 | -0.27 | 1/4 |
| range/ATR lo & VA/ATR <= med | M5 | 41.9 | +4.08 | +0.89 | +0.64 | +3.36 | **PASS4** |
| range/ATR lo & VA/ATR > med | M5 | 41.9 | -0.29 | +0.39 | +2.98 | +2.00 | 3/4 |
| range/ATR mid & VA/ATR <= med | M5 | 41.9 | +0.44 | -1.87 | -0.15 | +4.49 | 2/4 |
| range/ATR mid & VA/ATR > med | M5 | 41.9 | -0.45 | -1.26 | -4.96 | -1.15 | 0/4 |
| range/ATR hi & VA/ATR <= med | M5 | 41.9 | -4.34 | +1.02 | -2.93 | -0.98 | 1/4 |
| range/ATR hi & VA/ATR > med | M5 | 41.9 | -5.73 | -5.26 | +0.77 | -4.99 | 1/4 |
| low  prior VA width / ATR | M15 | 30.2 | -1.77 | -0.58 | +1.03 | -2.92 | 1/4 |
| high prior VA width / ATR | M15 | 30.2 | -1.03 | -3.28 | -3.22 | +2.09 | 1/4 |
| low  prior RANGE / ATR (no volume) | M15 | 30.2 | +1.10 | +0.38 | -1.31 | -4.57 | 2/4 |
| high prior RANGE / ATR (no volume) | M15 | 30.2 | -2.32 | -0.73 | -3.72 | +0.73 | 1/4 |
| low  VA width / prior range | M15 | 30.2 | -1.59 | +3.67 | -1.98 | +1.60 | 2/4 |
| high VA width / prior range | M15 | 30.2 | +0.84 | -1.63 | -3.13 | -1.62 | 1/4 |
| range/ATR lo & VA/ATR <= med | M15 | 15.1 | -0.60 | +1.40 | +0.01 | -2.06 | 2/4 |
| range/ATR lo & VA/ATR > med | M15 | 15.1 | +2.76 | -0.68 | -2.37 | -7.01 | 1/4 |
| range/ATR mid & VA/ATR <= med | M15 | 15.1 | -2.37 | +0.91 | -2.20 | +2.09 | 2/4 |
| range/ATR mid & VA/ATR > med | M15 | 15.1 | -0.97 | -0.82 | -3.80 | -4.63 | 0/4 |
| range/ATR hi & VA/ATR <= med | M15 | 15.1 | -1.52 | +1.61 | -4.08 | +5.64 | 2/4 |
| range/ATR hi & VA/ATR > med | M15 | 15.1 | -3.16 | -2.97 | -3.41 | -6.26 | 0/4 |
| low  prior VA width / ATR | M1 | 393.8 | -1.15 | -1.27 | -1.77 | +0.66 | 1/4 |
| high prior VA width / ATR | M1 | 393.8 | -3.62 | -3.89 | -1.42 | -4.16 | 0/4 |
| low  prior RANGE / ATR (no volume) | M1 | 393.8 | -0.99 | -1.43 | -1.75 | -1.08 | 0/4 |
| high prior RANGE / ATR (no volume) | M1 | 393.8 | -4.08 | -4.26 | -1.22 | -4.48 | 0/4 |
| low  VA width / prior range | M1 | 395.4 | -2.38 | -2.82 | -1.17 | -0.22 | 0/4 |
| high VA width / prior range | M1 | 394.1 | -3.54 | -3.66 | -1.44 | -3.49 | 0/4 |
| range/ATR lo & VA/ATR <= med | M1 | 196.9 | -1.11 | -0.90 | -1.77 | +0.58 | 1/4 |
| range/ATR lo & VA/ATR > med | M1 | 196.9 | -0.88 | -1.97 | -1.74 | -2.79 | 0/4 |
| range/ATR mid & VA/ATR <= med | M1 | 196.9 | -2.35 | -3.12 | -1.95 | +0.57 | 1/4 |
| range/ATR mid & VA/ATR > med | M1 | 196.9 | -2.77 | -2.96 | -2.03 | -3.00 | 0/4 |
| range/ATR hi & VA/ATR <= med | M1 | 196.9 | -2.87 | -3.49 | -0.07 | -3.86 | 0/4 |
| range/ATR hi & VA/ATR > med | M1 | 196.9 | -5.30 | -5.02 | -2.55 | -5.20 | 0/4 |
| low  prior VA width / ATR | H1 | 8.1 | -6.58 | -1.33 | -0.17 | +5.66 | 1/4 |
| high prior VA width / ATR | H1 | 8.1 | -2.61 | -1.23 | -4.09 | +3.22 | 1/4 |
| low  prior RANGE / ATR (no volume) | H1 | 8.1 | -6.65 | -2.48 | +2.26 | +0.39 | 2/4 |
| high prior RANGE / ATR (no volume) | H1 | 8.1 | -1.07 | -2.09 | -1.38 | -2.66 | 0/4 |
| low  VA width / prior range | H1 | 8.1 | -7.36 | -3.46 | -2.01 | +6.05 | 1/4 |
| high VA width / prior range | H1 | 8.1 | -5.11 | -4.41 | -0.52 | +1.97 | 1/4 |
| range/ATR lo & VA/ATR <= med | H1 | 4.1 | -4.50 | +2.72 | -6.07 | -2.42 | 1/4 |
| range/ATR lo & VA/ATR > med | H1 | 4.1 | -8.29 | -9.68 | +7.26 | +2.55 | 2/4 |
| range/ATR mid & VA/ATR <= med | H1 | 4.1 | -10.99 | -8.46 | -4.20 | +10.73 | 1/4 |
| range/ATR mid & VA/ATR > med | H1 | 4.0 | -13.40 | +8.26 | -11.81 | -16.05 | 1/4 |
| range/ATR hi & VA/ATR <= med | H1 | 4.1 | +0.74 | +2.35 | +0.54 | -16.05 | 3/4 |
| range/ATR hi & VA/ATR > med | H1 | 4.1 | -2.97 | -6.28 | -3.81 | +8.14 | 1/4 |

**7 candidates (repeat of rows above, detailed)** (9 rows)

| variant | TF | n/mo | train L | train S | valid L | valid S | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| C1 narrow prior VA | M5 | 83.9 | +1.63 | +0.83 | +1.28 | +4.17 | **PASS4** |
| C1b narrow prior RANGE (no volume) | M5 | 83.9 | +1.84 | +0.65 | +1.89 | +2.70 | **PASS4** |
| C2 narrow prior VA & CVD confirms 20-bar extreme | M5 | 57.7 | +1.57 | +0.83 | +1.28 | +4.00 | **PASS4** |
| C1 narrow prior VA | M15 | 30.2 | -1.77 | -0.58 | +1.03 | -2.92 | 1/4 |
| C1b narrow prior RANGE (no volume) | M15 | 30.2 | +1.10 | +0.38 | -1.31 | -4.57 | 2/4 |
| C2 narrow prior VA & CVD confirms 20-bar extreme | M15 | 20.1 | -4.79 | +0.28 | +3.32 | -3.34 | 2/4 |
| C3 flow-confirm FC4>=med & no prior HVN | M15 | 20.5 | +0.61 | +2.63 | +5.59 | +0.88 | **PASS4** |
| C1 narrow prior VA | M1 | 393.8 | -1.15 | -1.27 | -1.77 | +0.66 | 1/4 |
| C1 narrow prior VA | H1 | 8.1 | -6.58 | -1.33 | -0.17 | +5.66 | 1/4 |
