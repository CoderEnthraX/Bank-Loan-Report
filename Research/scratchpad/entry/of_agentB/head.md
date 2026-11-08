# of_agentB: order-flow entries on gold (XAUUSD, FxPro, tick volume), results

Scope: train 2021-01..2023-12 and valid 2024-01..2025-06 only. TEST (2025-07..) was never evaluated (kit default; `allow_test` never set).
All outcomes come from `kit.evaluate` / `outcomes.simulate` (1-minute path, stop first, every signal on its own). "Excess" = hit% minus random
market entries of the same direction in the same split (kit baseline), averaged over TP1-TP4 (0.6 / 1 / 1.5 / 2 R). "Placebo-adj" = hit% minus
agentA's placebo: the same order geometry (entry offset and stop in ATR, mode, window), same direction, same split, same **New York hour**, 3 random
bars per trade (5 in the detail runs). It removes time-of-day and order-mechanics effects.
Order flow = `of.py` (tick-volume only: estimated delta per 1-min candle by tick rule `dtk` or CLV `dcl`, session CVD, developing / prior session
profile POC / VAH / VAL in $0.50 bins, RVP). Composite profile for LVN / HVN = sum of the 5 previous sessions (`oflib.comp_rvp`).
Common settings unless stated: Mon-Fri, bar >= 180 min into the session for "developing" rules, one trade per direction per hour (M5 12 bars, M15 4,
H1 2, M1 60), "mkt" = market at the signal close, "stp" = stop entry at the signal bar's extreme +-0.05 ATR (3 bars), "atr" = 1.8 ATR stop,
"struct" = structural stop (signal bar / probe extreme -+0.1 ATR, clipped to 0.5-3 ATR). Thresholds that are percentiles come from TRAIN bars only.
Scripts (all in `entry/of_agentB/`): `oflib.py` (context, orders, composite profile), `fam12.py` (absorption, failed auction, 80 % rule), `fam3.py`
(loose absorption, LVN / HVN), `fam45.py` (POC, delta / CVD), `fam6.py`, `fam6b.py` (with the indicator's raw signals), `cand.py`, `cand_m1.py`,
`c3.py`, `c3delta.py` (sensitivity), `detail.py`, `detail3.py` (finalists), `boot.py` (month-block bootstrap), `score.py`, `make_table.py`.
Raw rows: `rows.jsonl`; finalists: `detail.json`, `detail3.json`; logs `*.out`.

**Bottom line.** The order-flow ideas themselves (absorption, failed auction, 80 % rule, LVN / HVN, CVD divergence, delta flip, climax + opposite
delta, IB breakout with CVD, delta / CVD / value-area filters on the indicator) do **not** beat random entries: in the first 350-variant screen 15 had
all four cells positive versus about 22 expected by chance, and none held across timeframes. Estimated delta (tick volume) adds nothing anywhere
it was tested, including on top of the one survivor. One setup does stand out: **C3, fade an impulse bar (the indicator's raw signal) that extends
AWAY from the developing POC when price is already far from it (>= 5.8 ATR on M5)**. On M5 it is positive at every TP, in train and valid, longs and
shorts, every year 2021-2025H1 and across its parameter neighbourhood (train +4.9, valid +3.7 points, month-block z 4.1 / 2.6). It holds partly on
M1 and H1 and is weak on M15. The "order-flow" part of it is only "distance from the session's value (POC ~ VWAP)"; the edge after spread is
0 to +0.06 R a trade in train. It is the one candidate worth sending to TEST, and it was found after many tries (see the multiple-testing notes).

## Multiple-testing context
- 495 rows in `rows.jsonl`. The first 350 are the family screen (F1-F6); the other 145 are the sensitivity sweeps of C1, C2 and C3, so they are strongly
  correlated with their base rules. Screen: 15 of 350 all-4 > 0 (about 22 expected under no edge), pooled z mean -0.25, sd 1.08.
  All 495: 61 all-4 > 0, 19 with pooled z > 3. 17 of those 19 are C3 and its neighbours (same trades, slightly changed); the other two are C1 (z 3.0) and
  "OPP sig NOT devPOC ahead" (z 3.3, but valid L -0.9: FAIL).
- C3 came from step 8 (combine the best family idea, POC distance, with the indicator signal, as the brief asked), and I picked that step after seeing
  C1's train AND valid numbers. So valid is not a clean hold-out for C3. Train alone gives z 4.1 (month-block bootstrap), which is above a Bonferroni
  bar for ~500 tries (about 3.5) but not by much, given how the rule was found.
- Stop entries on structure (agentA saw a systematic plus for shorts) are not the source here: C3 uses market entries with an ATR stop.
