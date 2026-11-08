# agentB progress (entry mechanics / gating family)
- step 0: setup, folder created. Scripts: lib.py (helpers + variants.csv log)
- step 1 DONE (mech.py -> mech.out, logged in variants.csv family=mech): 36 mechanics x M15/M5. All within +-2 pts avg excess (noise level,
  se 1.2-2). Nothing with L and S both >0 on both TFs in train and valid. Faintly positive on M15 only: '1st pullback close above lvl'
  (+0.6/+1.1 tr, +1.0/+1.9 va; M5 mixed), 'nofill N3 mkt if beyond 0.3ATR' (M15 +1.8/+0.3, +1.4/+4.7; M5 +0.1/-0.6, +1.4/+1.6).
  Structural / tight stops worse (spread + granularity). Fades: no stable sign.
- step 2 next: gates.py (NY time, ATR regime, W/M VWAP side, daily trend, stronger thresholds) on base limit / market / pullback-above.
- step 2 DONE (gates.py -> gates.out, family=gate, ~150 rows): no gate gives L and S >0 in train and valid on both TFs.
  NY windows on the SIGNALS: M15 small n (~10/mo) positive but below gate-matched random; M5 strongly NEGATIVE in train (L14-17 -7.1,
  -8 vs gate). high ATR regime (atr/atr100>1.2, atr_vs_h1 high): longs +2.7..+4.9 train on both TFs but valid ~0 -> not confirmed.
  'pb' (1st pullback bar close still beyond the retest lvl, mkt, 1.8 ATR) is mildly positive in nearly every M15 subset
  (+1..+2 per side, ~1 se) but NOT on M5 (shorts train <0). Candidate to check on H1 / per year.
- step 3 next: h1.py (H1 confirmation of mech + pb), fade in NY windows, pb robustness per year.
- step 3a DONE (mech_H1.out, gates_H1.out): H1 base signals negative (mkt -3.8/-2.3 tr). H1 FADE market all 4 positive
  (+2.1/+3.4 tr, +1.4/+1.9 va, 33/mo) but M15/M5 fade not stable. H1 pb (1st pullback close above lvl) +1.4/+0.0 tr, +4.9/+1.2 va;
  pb subsets on H1 valid longs +5..+9. -> pb is the only candidate seen on 3 TFs-ish (M5 shorts fail). Next: pb.py variants + M1.
- note: m1_baseline first run also computed+printed RANDOM-entry TEST hit rates (no rule involved); code fixed to train/valid only, file regenerated.
- step 3b DONE (pb.py -> pb.out, family=pb): pb W5 lvl close 1.8ATR: M1 tr -0.7/-1.5 (n 17k/side, significantly <0), va +0.5/+0.3;
  M5 +0.8/-0.5, -0.4/+0.4; M15 +0.6/+1.1, +1.0/+1.9 (per year 2023 both <0, 2024 L <0); H1 +1.4/+0.0, +4.9/+1.2 (2023 S -4.6, 25H1 S -4.0).
  Variants W3/W8/mid/none/break/struct/2.5ATR: same picture; struct stops hurt everywhere (spread). Edge grows with TF, absent on M1/M5.
- step 4 next: combos.py (pb + trend / cmo40 / vol regime / W-M VWAP), fade by NY window, H1 fade per year.
- step 4 DONE (combos.py -> combos.out, family=combo): pb+5d trend: M15 +1.8/+1.9 tr, +2.2/+1.6 va (2023-24 ~0), H1 +2.2/+1.3, +6.2/+5.2
  (n 15/mo, small), but M5 (+1.5/-0.5, -0.5/-0.5) and M1 (all tr <0) fail. Vol-regime combos: train only.
  NEW: FADE all on M1 +1.8/+1.5 tr (5 se), +0.7/+0.6 va; per year 2024/25H1 long-fades <0. FADE aligned with NY seasonality
  (short after bull signal NY07-10, long after bear signal NY14-17): M5 +8.0/+1.6 tr, +9.9/+3.1 va (40/mo); M1 +1.5/+1.4, +1.8/+2.4;
  M15 +1.1/+1.9, +2.6/-0.9; caveat README seasonality was measured on 2021-25H1 (incl. valid) -> need vs-gate numbers.
- step 5 next: fadehours.py: fade by 3h NY block vs gate-matched random, M1/M5/M15/H1.
- step 5 DONE (fadehours.py -> fadehours.out, 32 cells): fading the raw signal in NY 12-15 and 15-18 on M5: ALL of tr/va x L/S >0 and
  >0 vs same-block random (12-15 vs gate +5.0/+3.0 tr, +3.4/+7.1 va; 15-18 +6.8/+8.2, +7.5/+8.9). M1 12-15 all 4 >0, 15-18 3/4.
  M15/H1: small n, mixed. Train-only block ranking would have picked 15-18, 12-15, 06-09 (06-09 fails valid).
  Caveat to check: last bar before the 17:00 NY break -> market fill at C[i] not executable; check contiguity.
- step 6 next: fade2.py candidate 'FADE NY 12-18' details (contiguity, per-year, per-TP, entry variants, TF).
- step 6 DONE (fade2.py -> fade2.out): CANDIDATE C1 = M5 fade raw signal, NY 12:00-17:59 bar open, next bar contiguous, mkt at close,
  stop 1.8 ATR: 46.9/mo, tr L +4.98 (868) S +4.02 (819), va L +9.18 (369) S +2.48 (468); vs same-window random +4.8/+4.7, +4.9/+7.2.
  per year L >0 all 5, S >0 4/5 (2023 -2.8). Windows 11-18/13-17/12-15/15-18/12-21 all similar on M5. M1 confirms (+1.3/+3.0, +2.7/+1.0,
  9/10 year-cells >0) but spread kills M1 (E1 -0.39). M15 longs only (S <0), H1 n too small. Variants: range>=1.2ATR (21/mo) +6.6/+4.6, +9.2/+3.8;
  cmo40 +5.0/+2.5, +9.4/+4.6. Entry variants (stop-entry @lvl, limit, after counter bar, other stops) no better.
- step 7 next: detail.py: per-TP / E per TP / day-block bootstrap / control (fade any plain 6-bar breakout) for C1, C2.
- step 7 DONE (detail.py -> detail.out): C1 M5 per TP all >0 tr+va both dirs; boot(day) s.e. ~ naive (1.9 tr, 2.4-2.8 va per side);
  E after spread M5 train -0.055..+0.007, valid +0.03..+0.09. CONTROL (fade any plain 6-bar breakout in window) only ~half the edge
  on M5 (+2.7/+3.1, +5.4/-2.0) -> indicator filters add to it. C2 (range>=1.2ATR) 21/mo: +6.6/+4.6, +9.2/+3.8.
- step 8 next: gen_results.py (table from variants.csv) + results.md.
- step 8: writing results.md (head.md + candidates + conclusion + appendix table.md)
- step 8 DONE: results.md written (curated table + C1/C2/C3 + conclusion + full 522-row appendix). TASK COMPLETE.
