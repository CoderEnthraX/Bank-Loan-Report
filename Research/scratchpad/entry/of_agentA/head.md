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
