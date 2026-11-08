# agentB: entry mechanics / gating of the Auction Retest signal on gold (XAUUSD, FxPro), results

Protocol: `kit.evaluate` (1-minute path, stop checked first, every signal simulated on its own). Train is 2021-01..2023-12 and valid is
2024-01..2025-06. **I never evaluated any rule on TEST.** One slip to report: the first run of my M1 random baseline computed and printed
the hit rates of *random* M1 entries in the test period. No rule was involved and I did not use those numbers. The code was then fixed
and the file regenerated without test. "Excess" means hit% minus random market entries of the same direction in the same split, averaged
over TP1-TP4 (0.6/1/1.5/2 R). L = longs, S = shorts. n/mo counts train trades per month. z = pooled (L+S) excess divided by the naive
s.e. 50/sqrt(n). Scripts, outputs and the variant log are in this folder: `lib.py`, `mech.py`, `gates.py`, `pb.py`, `combos.py`,
`fadehours.py`, `fade2.py`, `detail.py`, `detail_pb.py`, `gen_results.py`, `*.out` and `variants.csv`.

**Variants tried: 522 distinct evaluations** (about 200 distinct ideas across M1/M5/M15/H1; many are nested or correlated). With 522 × 4
sign cells, about 1/16 of noise rules come out "all four positive" by chance (about 33 expected; 84 observed). Across all variants the
pooled train z has an s.d. of 2.3. So only results above about 3 se in train **and** about 2-3 se in valid, which also replicate on a
second TF, count as evidence below.

## (1) Variant table

### 1a. The key rows (the full list of all 522 rows is in the appendix at the end)

| variant | TF | n/mo | train L / S | valid L / S | verdict |
|---|---|---|---|---|---|
| indicator as is (limit 5 bars, stop_h) | M5 | 251.9 | -1.07 / -0.95 | -0.54 / +0.77 | no edge (reference) |
| indicator as is | M15 | 90.6 | -0.90 / -0.10 | -2.61 / -1.87 | no edge (reference) |
| indicator as is | H1 | 24.3 | -6.60 / -1.38 | -2.28 / -1.03 | negative |
| market at signal close | M5 / M15 / H1 | 325 / 118 / 33 | -0.8/-2.5, -0.5/-2.2, -3.8/-2.3 | -0.4/+0.9, -0.5/+1.9, -1.2/-1.7 | no edge |
| fill window 1 / 2 / 3 bars | M5, M15, H1 | | -0.6..-1.7 (M5/M15), about -6 L (H1) | mixed | fail |
| limit depth 25/50/75/100% of the candle | M5, M15, H1 | | -1.9..+1.2 | -4.7..+0.9 | fail (noise) |
| retest CONFIRMATION (touch, then a bar closes back beyond the level; mkt), W3/W5/W8 | M5, M15, H1 | | -2.1..+1.3 | -2.2..+3.0 | fail |
| confirmation, stop structural / signal candle / 1.0 / 3.0 ATR | M5, M15, H1 | | tighter stops worse (spread, granularity) | | fail |
| confirmation, enter on a break of the confirmation bar | M5, M15, H1 | | -1.3..+0.6 | -4.3..+2.7 | fail |
| no fill after N=1-3 bars -> market if still beyond 0 / 0.3 ATR | M5 | 68-109 | +0.1..+1.2 / -0.9..-0.3 | +0.5..+1.4 / +0.9..+3.0 | fail (S train <0) |
| same | M15 | 25-39 | -2.8..+2.6 / -4.0..+0.3 | -1.6..+1.4 / +3.1..+6.9 | fail |
| 2nd displacement in the same direction within 6/12/24 bars | M5, M15, H1 | | -7..+1 | mixed | fail |
| 1st pullback bar's close (any) | M5 / M15 / H1 | 319 / 115 / 33 | +0.7/-0.4, +0.7/-0.3, +0.4/+0.3 | -0.0/+0.7, +0.3/+1.1, +3.2/+0.7 | weak / fail |
| **pb** = 1st pullback bar, close still beyond the retest level | M1 / M5 / M15 / H1 | 962 / 204 / 76 / 22 | -0.7/-1.5, +0.8/-0.5, +0.6/+1.1, +1.4/+0.0 | +0.5/+0.3, -0.4/+0.4, +1.0/+1.9, +4.9/+1.2 | positive only on M15/H1 (about 1 se); M1 significantly <0 in train |
| NY gate on the SIGNAL (L 14-17, S 07-10) | M5 | 29 | -7.1 / -3.3 (vs same-hours random -8.1 / -4.2) | +0.4 / +6.6 | fail: signals in those hours are WORSE than random |
| ATR regime atr/atr100 >1.2, atr_vs_h1 top third | M5, M15, H1 | | L +2.7..+4.9, S about -1 | L about 0 | fail (train only) |
| with week / month VWAP side, daily EMA20 side, 5-day trend | M5, M15, H1 | | ±1..2 | ±1..3 | fail |
| stronger thresholds: CMO≥40, body≥70%, close≤12%, range≥1.3 ATR, mom≥1.5 ATR, break≥0.3 ATR | M5, M15, H1 | | ±1..2 | ±1..3 | fail (raw); slightly positive with the pb entry on M15/H1 only |
| pb + 5-day trend (C3) | M15 / H1 | 45.5 / 14.7 | +1.8/+1.9, +2.2/+1.3 | +2.2/+1.6, +6.2/+5.2 | all >0 but weak; fails on M5 (+1.5/-0.5, -0.5/-0.5) and M1 (train <0) |
| FADE every signal (mkt, 1.8 ATR) | M1 / M5 / M15 / H1 | 1556 / 325 / 118 / 33 | +1.8/+1.5, +2.8/+1.0, +2.6/+0.9, +2.1/+3.4 | +0.7/+0.6, -0.5/+0.3, -2.4/+0.3, +1.4/+1.9 | M1 and H1 all >0; M5/M15 fail in valid |
| FADE by 3h NY block (8 blocks × 4 TF) | M5 | | blocks 12-15 and 15-18: all 8 cells >0, also vs same-block random | | rest mixed |
| **FADE NY 12:00-18:00 (C1)** | **M5** | **46.9** | **+4.98 / +4.02** | **+9.18 / +2.48** | **all >0, 3.7 se train, 3.1 se valid** |
| same | M1 | 298.8 | +1.25 / +2.97 | +2.68 / +1.02 | all >0 (4.3 / 2.6 se); E after spread very negative |
| same | M15 / H1 | 10.9 / 3.7 | +4.2 / -2.3, +4.5 / -2.0 | +3.2 / -1.7, +6.1 / +9.0 | S fails on M15; H1 too few trades |
| window variants 11-18 / 13-17 / 12-15 / 15-18 / 12-21 | M5 | 17-96 | L +4.0..+6.7, S +1.3..+4.8 | L +5.3..+14.8, S -0.5..+4.7 | robust to the window edges |
| FADE NY 12-18 + range≥1.2 ATR (C2) | M5 | 21.0 | +6.59 / +4.55 | +9.24 / +3.80 | all >0 (3.1 / 2.5 se) |
| FADE NY 12-18 + CMO≥40 | M5 | 32.5 | +5.01 / +2.51 | +9.35 / +4.57 | all >0 (2.6 / 3.3 se) |
| fade entry variants: stop-entry at the retest level, limit +0.3 ATR, after a counter bar, stop beyond the signal extreme | M5 | 26-36 | +1.4..+4.9 | -0.2..+10.2 | no better than a plain market fade |
| CONTROL: fade ANY bar closing beyond its 6-bar high/low (no indicator filters), NY 12-18 | M5 | 268 | +2.70 / +3.08 | +5.37 / -1.99 | about half of C1 -> the indicator's filters concentrate the effect |


## (2) Best candidates

### C1: fade the indicator's raw signal in the New York afternoon (M5), the main candidate

**Rule, decided at the close of M5 bar i:**
1. The indicator's raw signal fires on bar i (`signals.raw('M5')`, default P0). A bullish signal is a displacement candle (C>O, range
   ≥ 0.8 ATR14, body ≥ 55 %, close in the top 25 %, close > highest high of the previous 6 bars) with C > session VWAP, VWAP rising over
   3 bars, 10-bar momentum ≥ 0.85 ATR and efficiency (CMO) ≥ 20 %, not on Sunday. A bearish signal is the mirror image.
2. Bar i **opens between 12:00 and 17:59 New York local time** (DST aware), and **the next bar follows without a gap**. This drops the
   16:55 bar before the 17:00 NY daily break and the last bar before an early close; there you cannot trade at the close. In practice:
   bar open 12:00-16:50 NY.
3. Trade **against** the signal at market, at the close of bar i: **short after a bullish signal, long after a bearish signal.**
4. The stop is **1.8 × ATR14** beyond the entry. TP1-TP4 sit at 0.6 / 1 / 1.5 / 2 × that distance (unchanged).

**Trades:** 46.9 a month in train and 46.5 in valid (about 24 longs and 23 shorts). The README asks for at least 20 a month on M5.

| split | side | n | hit TP1..TP4 % | excess TP1..TP4 (pts) | avg excess | E after spread at TP1..TP4 (R) |
|---|---|---|---|---|---|---|
| train | long | 868 | 67.2 54.5 44.9 38.2 | +5.1 +4.7 +5.0 +5.2 | **+4.98** | -0.055 -0.039 -0.006 +0.018 |
| train | short | 819 | 66.7 54.3 43.7 37.2 | +4.1 +4.2 +3.7 +4.1 | **+4.02** | -0.055 -0.035 -0.029 -0.005 |
| train | both | 1687 | 66.9 54.4 44.3 37.8 | +4.6 +4.5 +4.3 +4.6 | +4.51 | -0.055 -0.037 -0.017 +0.007 |
| valid | long | 369 | 71.8 62.6 53.4 46.3 | +7.5 +9.7 +10.0 +9.4 | **+9.18** | +0.098 +0.201 +0.283 +0.339 |
| valid | short | 468 | 64.3 49.1 39.3 31.4 | +4.2 +2.1 +2.4 +1.2 | **+2.48** | -0.024 -0.070 -0.070 -0.111 |
| valid | both | 837 | 67.6 55.1 45.5 38.0 | +5.7 +5.5 +5.7 +4.8 | +5.44 | +0.030 +0.049 +0.086 +0.088 |

- **Every TP beats random in train and in valid, for longs and for shorts.** The weakest cell is the valid short TP4 at +1.2.
- **Excess against random entries in the same NY 12-18 window**, which removes the afternoon long-bias seasonality: train L +4.78 / S +4.70,
  valid L +4.91 / S +7.15.
- **Excess per year, longs / shorts:** 2021 +5.7 / +11.0; 2022 +1.3 / +3.2; 2023 +8.3 / **-2.8**; 2024 +11.1 / +3.5; 2025H1 +5.0 / +0.6.
  9 of 10 cells are positive.
- **Bootstrap s.e. by trading day:** train L 1.9, S 1.9; valid L 2.8, S 2.4. This is close to the naive 50/sqrt(n), so signal clustering does
  not inflate n. Train is about 2.6 / 2.1 se per side and 3.7 se pooled. Valid is 3.3 se for longs, **only about 1 se for shorts**, and
  3.1 se pooled.
- **Robustness:** windows 11-18, 13-17, 12-15, 15-18 and 12-21 give the same sign. Stops of 1.2 / 2.5 ATR give the same picture. Keeping
  the pre-break bar also gives the same picture (it is not executable). **M1 confirms the sign:** train +1.25 / +2.97, valid +2.68 / +1.02,
  9 of 10 year cells positive. **M15 does not:** longs +4.2 / +3.2 but shorts -2.3 / -1.7, at 11 trades a month. **H1 has too few trades**
  (3.7 a month).
- **Control:** fading *any* bar that closes beyond its 6-bar high/low in the same window, with none of the indicator's filters, gives only
  about half the edge (+2.7 / +3.1 train, +5.4 / **-2.0** valid). The displacement, VWAP and momentum filters pick the bars that revert.
- **Interpretation:** after the COMEX pit close (13:30 NY) and into the 17:00 break, gold liquidity is thin. A strong-looking displacement
  candle then is more often a liquidity spike that reverts than the start of a move. The same signal in the morning does not revert.

### C2: C1 restricted to strong candles, range ≥ 1.2 ATR (`signals.raw('M5', dispAtr=1.2)`)

The rule is the same as C1, except the signal candle's range must be at least 1.2 ATR (not 0.8). It gives 21.0 trades a month in train
and 21.6 in valid. That is just above the M5 minimum of 20.

| split | side | n | hit TP1..TP4 % | excess TP1..TP4 | avg | E after spread TP1..TP4 |
|---|---|---|---|---|---|---|
| train | long | 390 | 68.5 56.9 46.7 39.2 | +6.4 +7.2 +6.7 +6.1 | **+6.59** | -0.028 +0.015 +0.043 +0.054 |
| train | short | 367 | 67.0 55.0 45.2 36.8 | +4.5 +4.9 +5.2 +3.6 | **+4.55** | -0.048 -0.019 +0.011 -0.017 |
| valid | long | 189 | 73.5 64.6 51.9 44.4 | +9.3 +11.7 +8.5 +7.5 | **+9.24** | +0.128 +0.242 +0.247 +0.284 |
| valid | short | 199 | 66.3 51.3 40.2 31.7 | +6.3 +4.2 +3.2 +1.5 | **+3.80** | +0.006 -0.030 -0.050 -0.105 |

- **Per year, L / S:** 2021 +6.2 / +13.0; 2022 +3.8 / +6.9; 2023 +10.5 / **-8.7**; 2024 +11.3 / +3.4; 2025H1 +4.9 / +4.2.
- **Bootstrap s.e.:** about 2.5 in train and 3.4 in valid per side.
- **M1 (same rule):** +2.99 / +2.55 train, +2.41 / +1.85 valid.
- Its averages are higher than C1's but its n is half. It is one extra threshold chosen from five that I tried, so treat it as a
  refinement of C1 rather than an independent finding.

### C3: best continuation-type entry, "pb + 5-day trend" (M15 / H1), weak and NOT confirmed

**Rule:** a raw signal fires on bar i. The first counter-direction bar j within the next 5 bars (C<O for a long) still closes beyond the
indicator's retest level (for a long, C[j] > max(50 % body, 6-bar high)). The close of bar j is on the side of the close 5 completed
sessions earlier (for a long, C[j] > that close). Enter at market at C[j], stop 1.8 ATR.

| TF | n/mo | train L / S (per-TP excess) | valid L / S (per-TP excess) | E after spread at TP1..4 (train / valid, both sides) |
|---|---|---|---|---|
| M15 | 45.5 | +1.82 (+2.3 +1.8 +1.8 +1.4) / +1.86 (+1.6 +0.4 +1.8 +3.6) | +2.17 (+1.9 +2.9 +3.0 +0.8) / +1.64 (+2.3 +2.7 +2.3 -0.7) | -0.04..-0.01 / +0.03..+0.09 |
| H1 | 14.7 | +2.17 (+4.8 +2.1 +1.1 +0.7) / +1.28 (+1.5 +1.2 +0.2 +2.2) | +6.22 (+7.2 +5.5 +5.7 +6.4) / +5.18 (+4.8 +7.8 +4.3 +3.8) | -0.01..+0.02 / +0.11..+0.27 |

- **Per year on M15, L / S:** 2021 +3.7 / +4.1; 2022 +2.7 / +1.8; 2023 -0.8 / -0.0; 2024 -0.3 / -0.0; 2025H1 +6.5 / +6.1.
- **Per year on H1, L / S:** +4.8 / +5.4; +1.4 / +1.8; +0.5 / -2.4; +5.8 / +5.5; +6.9 / +4.7.
- **Why it is not confirmed:** train is only about 1.1 se per side on M15 and below 1 se on H1. 2023-2024 are flat on M15. The same rule
  is negative on M1 (train -0.8 / -0.6, n about 10k a side) and flat on M5 (+1.5 / -0.5, -0.5 / -0.5). It may be a small real trend-pullback
  effect on slower TFs, but this data does not show it with any confidence.

## (3) Conclusion

1. **Changing HOW the signal is entered does not create an edge.** Confirmation entries, limit depth, fill windows, market after no fill,
   second displacement, pullback entries and structural vs ATR stops all land within about ±2 pts of random on M5 and M15. None is positive
   for both sides in train and valid on two TFs. Structural or tight stops are consistently *worse*: the spread and the 1-minute granularity
   cost more than any accuracy they add. The indicator's continuation signal itself has no directional information (H1 is even negative).
2. **Gating WHICH signals are taken does not fix it either.** Gates tried: VWAP week/month side, daily trend, ATR regime, stronger
   thresholds and the README's NY windows. The NY-window gate applied *to the signal* is the opposite of helpful on M5. In those hours the
   signals do worse than random bars in the same hours.
3. **The one thing that stood out is the opposite trade in the NY afternoon (C1).** Fading the raw signal for bars opening 12:00-17:59 NY
   on M5 gives +4.5 pts average excess in train (3.7 se) and +5.4 in valid (3.1 se), on every TP and both sides. It holds against
   time-matched random entries, holds 9 of 10 years × sides, and replicates on M1. It is the top family out of 522 evaluations.
4. **Discount it honestly:**
   - About 522 tries make a 3.7 se train result worth roughly a 1-in-10 family-wise chance on its own.
   - I picked the window after seeing the 3h-block table on train **and** valid. Ranking on train alone would also have picked 06-09, which
     fails in valid, so valid is not a fully clean test of the window.
   - The valid short side is only about 1 se (+2.5).
   - M15 shorts contradict it, and H1 is too thin to judge.
   - Its economics are marginal: E after spread is about 0 in train (-0.055 R at TP1, +0.007 R at TP4) and +0.03..+0.09 R in valid, driven
     by valid longs (2024-25 afternoon longs).
   My estimate: there is probably a real but small mean-reversion effect in afternoon displacement candles (strongest on M5, still present
   on M1). It raises TP hit rates by about 3-5 pts but is barely enough to pay the M5 spread. **It should be checked once on TEST before
   anyone relies on it**, and judged on its short side there.
5. **C2** (C1 plus range ≥ 1.2 ATR) is a slightly stronger, thinner version of C1, about 21 trades a month. **C3** (pullback continuation
   plus 5-day trend on M15/H1) is not significant and does not replicate on M5/M1.
6. **Ruled out, so other agents need not retry:** retest confirmation, limit depth, fill window, market-after-no-fill, second displacement,
   structural stops, VWAP/trend/vol gates and stronger thresholds as stand-alone fixes for the continuation entry.

All work ran in this session on the session model; no sub-agents were launched (each step was small and fast).

## Appendix: every variant tried (522 rows, from variants.csv; verdict = automatic rule, see gen_results.py)

| # | family | variant | TF | n/mo (train) | train L | train S | valid L | valid S | z train | z valid | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | entry mechanics | base limit5 stop_h | M15 | 90.6 | -0.90 | -0.10 | -2.61 | -1.87 | -0.6 | -1.9 | fail (trL,trS,vaL,vaS <=0) |
| 2 | entry mechanics | base limit5 stop1.8 | M15 | 90.6 | -0.88 | -0.26 | -2.49 | -1.18 | -0.7 | -1.6 | fail (trL,trS,vaL,vaS <=0) |
| 3 | entry mechanics | market at signal close | M15 | 117.6 | -0.53 | -2.17 | -0.48 | +1.88 | -1.7 | 0.5 | fail (trL,trS,vaL <=0) |
| 4 | entry mechanics | limit window 1 | M15 | 62.0 | -0.79 | -0.78 | -1.95 | +0.57 | -0.7 | -0.6 | fail (trL,trS,vaL <=0) |
| 5 | entry mechanics | limit window 2 | M15 | 76.4 | -0.65 | -0.21 | -1.49 | -0.29 | -0.5 | -0.8 | fail (trL,trS,vaL,vaS <=0) |
| 6 | entry mechanics | limit window 3 | M15 | 82.8 | -1.03 | -0.02 | -2.30 | -1.22 | -0.6 | -1.5 | fail (trL,trS,vaL,vaS <=0) |
| 7 | entry mechanics | limit depth 25% of range | M15 | 97.0 | -0.72 | -0.90 | -1.87 | +0.16 | -0.9 | -0.9 | fail (trL,trS,vaL <=0) |
| 8 | entry mechanics | limit depth 50% of range | M15 | 76.8 | -0.91 | -0.00 | -1.35 | +0.18 | -0.5 | -0.6 | fail (trL,trS,vaL <=0) |
| 9 | entry mechanics | limit depth 75% of range | M15 | 57.0 | -0.40 | -1.53 | -3.09 | -1.14 | -0.9 | -1.5 | fail (trL,trS,vaL,vaS <=0) |
| 10 | entry mechanics | limit depth 100% of range | M15 | 41.9 | -1.69 | -0.26 | -4.67 | -0.49 | -0.8 | -1.7 | fail (trL,trS,vaL,vaS <=0) |
| 11 | entry mechanics | confirm W3 mkt stop1.8 | M15 | 45.0 | -0.91 | +1.33 | +2.96 | -1.72 | 0.1 | 0.6 | fail (trL,vaS <=0) |
| 12 | entry mechanics | confirm W5 mkt stop1.8 | M15 | 59.1 | -1.07 | +1.04 | +0.47 | -2.20 | -0.0 | -0.4 | fail (trL,vaS <=0) |
| 13 | entry mechanics | confirm W5 mkt stop struct | M15 | 59.1 | -0.57 | -0.52 | -1.25 | -2.59 | -0.5 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 14 | entry mechanics | confirm W5 mkt stop sigcandle | M15 | 59.1 | -0.08 | -0.40 | -1.84 | -4.34 | -0.2 | -1.9 | fail (trL,trS,vaL,vaS <=0) |
| 15 | entry mechanics | confirm W5 mkt stop1.0 | M15 | 59.1 | -0.35 | -0.64 | -2.03 | -3.08 | -0.5 | -1.6 | fail (trL,trS,vaL,vaS <=0) |
| 16 | entry mechanics | confirm W5 mkt stop3.0 | M15 | 59.1 | -1.23 | +0.85 | +1.88 | -2.91 | -0.2 | -0.0 | fail (trL,vaS <=0) |
| 17 | entry mechanics | confirm W5 break-of-bar stop1.8 | M15 | 46.8 | -1.14 | +0.59 | +1.04 | -4.27 | -0.3 | -0.6 | fail (trL,vaS <=0) |
| 18 | entry mechanics | confirm W8 mkt stop1.8 | M15 | 70.2 | -0.18 | -0.39 | +0.43 | -1.48 | -0.3 | -0.2 | fail (trL,trS,vaS <=0) |
| 19 | entry mechanics | confirm W5 close-beyond only | M15 | 67.3 | -1.98 | +1.80 | -0.77 | -0.56 | -0.2 | -0.5 | fail (trL,vaL,vaS <=0) |
| 20 | entry mechanics | nofill N1 mkt if beyond 0.0ATR | M15 | 39.4 | -0.44 | -2.36 | -1.57 | +3.60 | -1.0 | 0.3 | fail (trL,trS,vaL <=0) |
| 21 | entry mechanics | nofill N1 mkt if beyond 0.3ATR | M15 | 27.6 | -2.84 | -4.03 | -0.62 | +3.06 | -2.1 | 0.4 | fail (trL,trS,vaL <=0) |
| 22 | entry mechanics | nofill N2 mkt if beyond 0.0ATR | M15 | 33.4 | -0.88 | -1.40 | +0.53 | +6.19 | -0.8 | 1.4 | fail (trL,trS <=0) |
| 23 | entry mechanics | nofill N2 mkt if beyond 0.3ATR | M15 | 26.6 | -0.64 | -0.52 | +1.12 | +6.94 | -0.4 | 1.6 | fail (trL,trS <=0) |
| 24 | entry mechanics | nofill N3 mkt if beyond 0.0ATR | M15 | 29.2 | +2.60 | -1.14 | +1.43 | +4.30 | 0.6 | 1.2 | fail (trS <=0) |
| 25 | entry mechanics | nofill N3 mkt if beyond 0.3ATR | M15 | 24.5 | +1.82 | +0.27 | +1.44 | +4.67 | 0.7 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 26 | entry mechanics | 2nd disp K6 limit | M15 | 31.6 | +0.65 | -1.45 | -0.92 | -3.13 | -0.2 | -0.9 | fail (trS,vaL,vaS <=0) |
| 27 | entry mechanics | 2nd disp K6 market | M15 | 40.6 | +0.99 | -2.78 | +0.37 | +1.45 | -0.5 | 0.4 | fail (trS <=0) |
| 28 | entry mechanics | 2nd disp K12 limit | M15 | 40.6 | +0.32 | -2.67 | -1.34 | -3.61 | -0.8 | -1.2 | fail (trS,vaL,vaS <=0) |
| 29 | entry mechanics | 2nd disp K12 market | M15 | 52.4 | +0.75 | -2.63 | -0.54 | +1.79 | -0.7 | 0.2 | fail (trS,vaL <=0) |
| 30 | entry mechanics | 1st disp only K12 market | M15 | 65.2 | -1.64 | -1.84 | -0.43 | +1.94 | -1.7 | 0.4 | fail (trL,trS,vaL <=0) |
| 31 | entry mechanics | 2nd disp K24 limit | M15 | 54.1 | -0.59 | -1.70 | -1.30 | -3.54 | -1.0 | -1.4 | fail (trL,trS,vaL,vaS <=0) |
| 32 | entry mechanics | 2nd disp K24 market | M15 | 69.7 | -0.89 | -2.04 | -0.35 | +1.28 | -1.4 | 0.2 | fail (trL,trS,vaL <=0) |
| 33 | entry mechanics | 1st pullback close | M15 | 115.2 | +0.65 | -0.31 | +0.26 | +1.08 | 0.3 | 0.6 | fail (trS <=0) |
| 34 | entry mechanics | 1st pullback close above lvl | M15 | 75.8 | +0.62 | +1.10 | +1.01 | +1.93 | 0.9 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 35 | entry mechanics | FADE market | M15 | 117.6 | +2.63 | +0.89 | -2.35 | +0.31 | 2.2 | -0.7 | fail (vaL <=0) |
| 36 | entry mechanics | FADE stop-entry at retest lvl | M15 | 90.6 | +0.50 | +0.45 | +0.83 | +1.18 | 0.5 | 0.9 | all >0 but weak (<3 se train or <2 se valid) |
| 37 | entry mechanics | base limit5 stop_h | M5 | 251.9 | -1.07 | -0.95 | -0.54 | +0.77 | -1.9 | 0.0 | fail (trL,trS,vaL <=0) |
| 38 | entry mechanics | base limit5 stop1.8 | M5 | 251.9 | -1.07 | -1.10 | -0.45 | +0.86 | -2.1 | 0.2 | fail (trL,trS,vaL <=0) |
| 39 | entry mechanics | market at signal close | M5 | 324.9 | -0.82 | -2.48 | -0.38 | +0.86 | -3.5 | 0.2 | fail (trL,trS,vaL <=0) |
| 40 | entry mechanics | limit window 1 | M5 | 176.1 | -1.30 | -1.68 | -0.62 | +1.47 | -2.4 | 0.3 | fail (trL,trS,vaL <=0) |
| 41 | entry mechanics | limit window 2 | M5 | 213.5 | -1.19 | -1.67 | -0.33 | +0.97 | -2.5 | 0.3 | fail (trL,trS,vaL <=0) |
| 42 | entry mechanics | limit window 3 | M5 | 231.6 | -0.97 | -1.39 | -0.61 | +1.34 | -2.1 | 0.3 | fail (trL,trS,vaL <=0) |
| 43 | entry mechanics | limit depth 25% of range | M5 | 269.7 | -0.91 | -1.89 | -0.67 | +0.93 | -2.7 | 0.0 | fail (trL,trS,vaL <=0) |
| 44 | entry mechanics | limit depth 50% of range | M5 | 214.9 | -0.99 | -0.53 | -1.13 | +0.85 | -1.3 | -0.3 | fail (trL,trS,vaL <=0) |
| 45 | entry mechanics | limit depth 75% of range | M5 | 162.4 | +0.04 | -0.78 | -0.91 | +0.63 | -0.6 | -0.3 | fail (trS,vaL <=0) |
| 46 | entry mechanics | limit depth 100% of range | M5 | 120.4 | +1.21 | -0.05 | -0.98 | +0.84 | 0.8 | -0.2 | fail (trS,vaL <=0) |
| 47 | entry mechanics | confirm W3 mkt stop1.8 | M5 | 128.0 | -1.05 | -2.05 | -0.29 | +1.19 | -2.1 | 0.3 | fail (trL,trS,vaL <=0) |
| 48 | entry mechanics | confirm W5 mkt stop1.8 | M5 | 164.8 | -0.72 | -2.10 | -0.45 | +1.24 | -2.2 | 0.3 | fail (trL,trS,vaL <=0) |
| 49 | entry mechanics | confirm W5 mkt stop struct | M5 | 164.8 | -0.66 | -2.68 | -2.11 | +2.25 | -2.6 | -0.3 | fail (trL,trS,vaL <=0) |
| 50 | entry mechanics | confirm W5 mkt stop sigcandle | M5 | 164.8 | -1.03 | -1.81 | -0.86 | +1.08 | -2.2 | -0.0 | fail (trL,trS,vaL <=0) |
| 51 | entry mechanics | confirm W5 mkt stop1.0 | M5 | 164.8 | -1.96 | -2.41 | -2.61 | +2.31 | -3.4 | -0.6 | fail (trL,trS,vaL <=0) |
| 52 | entry mechanics | confirm W5 mkt stop3.0 | M5 | 164.8 | -1.20 | -1.69 | +0.85 | +0.19 | -2.2 | 0.6 | fail (trL,trS <=0) |
| 53 | entry mechanics | confirm W5 break-of-bar stop1.8 | M5 | 131.1 | -0.23 | -1.34 | +0.59 | +2.71 | -1.1 | 1.4 | fail (trL,trS <=0) |
| 54 | entry mechanics | confirm W8 mkt stop1.8 | M5 | 195.5 | -0.65 | -1.90 | -0.29 | +0.65 | -2.1 | 0.1 | fail (trL,trS,vaL <=0) |
| 55 | entry mechanics | confirm W5 close-beyond only | M5 | 184.8 | -0.48 | -1.55 | -0.76 | +1.08 | -1.6 | 0.0 | fail (trL,trS,vaL <=0) |
| 56 | entry mechanics | nofill N1 mkt if beyond 0.0ATR | M5 | 108.7 | +0.55 | -0.59 | +1.22 | +2.95 | 0.0 | 1.7 | fail (trS <=0) |
| 57 | entry mechanics | nofill N1 mkt if beyond 0.3ATR | M5 | 75.9 | +1.15 | -0.57 | +1.10 | +2.46 | 0.3 | 1.3 | fail (trS <=0) |
| 58 | entry mechanics | nofill N2 mkt if beyond 0.0ATR | M5 | 91.1 | +0.31 | -0.89 | +0.49 | +0.89 | -0.3 | 0.5 | fail (trS <=0) |
| 59 | entry mechanics | nofill N2 mkt if beyond 0.3ATR | M5 | 72.9 | +0.69 | -0.27 | +0.46 | +1.86 | 0.3 | 0.8 | fail (trS <=0) |
| 60 | entry mechanics | nofill N3 mkt if beyond 0.0ATR | M5 | 79.8 | +0.35 | -0.26 | +0.64 | +1.64 | 0.1 | 0.8 | fail (trS <=0) |
| 61 | entry mechanics | nofill N3 mkt if beyond 0.3ATR | M5 | 67.7 | +0.10 | -0.59 | +1.42 | +1.58 | -0.2 | 1.1 | fail (trS <=0) |
| 62 | entry mechanics | 2nd disp K6 limit | M5 | 92.6 | -0.47 | -0.98 | +1.74 | +1.27 | -0.8 | 1.3 | fail (trL,trS <=0) |
| 63 | entry mechanics | 2nd disp K6 market | M5 | 118.0 | -1.08 | -2.32 | +0.78 | +1.33 | -2.2 | 0.9 | fail (trL,trS <=0) |
| 64 | entry mechanics | 2nd disp K12 limit | M5 | 120.8 | -0.43 | -1.21 | +0.31 | +0.71 | -1.1 | 0.4 | fail (trL,trS <=0) |
| 65 | entry mechanics | 2nd disp K12 market | M5 | 154.0 | -1.14 | -2.82 | -0.40 | +0.54 | -2.9 | -0.0 | fail (trL,trS,vaL <=0) |
| 66 | entry mechanics | 1st disp only K12 market | M5 | 170.9 | -0.52 | -2.19 | -0.35 | +1.12 | -2.1 | 0.3 | fail (trL,trS,vaL <=0) |
| 67 | entry mechanics | 2nd disp K24 limit | M5 | 158.3 | -0.66 | -1.84 | -0.20 | +0.28 | -1.9 | -0.0 | fail (trL,trS,vaL <=0) |
| 68 | entry mechanics | 2nd disp K24 market | M5 | 202.0 | -0.97 | -2.92 | -0.22 | +0.47 | -3.3 | 0.1 | fail (trL,trS,vaL <=0) |
| 69 | entry mechanics | 1st pullback close | M5 | 319.1 | +0.68 | -0.39 | -0.03 | +0.65 | 0.3 | 0.4 | fail (trS,vaL <=0) |
| 70 | entry mechanics | 1st pullback close above lvl | M5 | 203.6 | +0.82 | -0.47 | -0.39 | +0.38 | 0.4 | -0.1 | fail (trS,vaL <=0) |
| 71 | entry mechanics | FADE market | M5 | 324.9 | +2.82 | +1.00 | -0.54 | +0.30 | 4.1 | -0.1 | fail (vaL <=0) |
| 72 | entry mechanics | FADE stop-entry at retest lvl | M5 | 251.9 | +1.25 | +0.63 | -0.87 | +0.26 | 1.8 | -0.3 | fail (vaL <=0) |
| 73 | gates (lim / mkt / pb entries) | lim / NY L14-17 S07-10 | M15 | 9.9 | +1.51 | +0.86 | +7.35 | +0.00 | 0.4 | 0.7 | fail (vaS <=0) |
| 74 | gates (lim / mkt / pb entries) | mkt / NY L14-17 S07-10 | M15 | 12.8 | +1.95 | +2.14 | +4.81 | +2.96 | 0.9 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 75 | gates (lim / mkt / pb entries) | pb / NY L14-17 S07-10 | M15 | 8.1 | +4.84 | +2.27 | -4.76 | -0.66 | 1.0 | -0.6 | fail (vaL,vaS <=0) |
| 76 | gates (lim / mkt / pb entries) | lim / NY L14-17 only | M15 | 2.1 | +1.51 |  | +7.35 |  | 0.3 | 1.2 | one direction only (both splits >0) |
| 77 | gates (lim / mkt / pb entries) | mkt / NY L14-17 only | M15 | 3.0 | +1.95 |  | +4.81 |  | 0.4 | 0.9 | one direction only (both splits >0) |
| 78 | gates (lim / mkt / pb entries) | pb / NY L14-17 only | M15 | 2.0 | +4.84 |  | -4.76 |  | 0.8 | -0.8 | one direction only (fails) |
| 79 | gates (lim / mkt / pb entries) | lim / NY S07-10 only | M15 | 7.8 |  | +0.86 |  | +0.00 | 0.3 | 0.0 | one direction only (fails) |
| 80 | gates (lim / mkt / pb entries) | mkt / NY S07-10 only | M15 | 9.8 |  | +2.14 |  | +2.96 | 0.8 | 0.8 | one direction only (both splits >0) |
| 81 | gates (lim / mkt / pb entries) | pb / NY S07-10 only | M15 | 6.2 |  | +2.27 |  | -0.66 | 0.7 | -0.1 | one direction only (fails) |
| 82 | gates (lim / mkt / pb entries) | lim / NY 07-17 both | M15 | 32.0 | -0.11 | -1.28 | +0.76 | -2.34 | -0.5 | -0.3 | fail (trL,trS,vaS <=0) |
| 83 | gates (lim / mkt / pb entries) | mkt / NY 07-17 both | M15 | 42.4 | +0.75 | -1.34 | +1.21 | +0.28 | -0.2 | 0.5 | fail (trS <=0) |
| 84 | gates (lim / mkt / pb entries) | pb / NY 07-17 both | M15 | 27.1 | +2.39 | +1.47 | +1.11 | -2.36 | 1.2 | -0.2 | fail (vaS <=0) |
| 85 | gates (lim / mkt / pb entries) | lim / atr/atr100<0.9 | M15 | 43.5 | -0.24 | +1.58 | -2.57 | -0.65 | 0.5 | -1.0 | fail (trL,vaL,vaS <=0) |
| 86 | gates (lim / mkt / pb entries) | mkt / atr/atr100<0.9 | M15 | 54.4 | -0.12 | -1.61 | +0.61 | +1.87 | -0.7 | 0.7 | fail (trL,trS <=0) |
| 87 | gates (lim / mkt / pb entries) | pb / atr/atr100<0.9 | M15 | 34.7 | -0.44 | +3.03 | +0.83 | +2.13 | 0.8 | 0.6 | fail (trL <=0) |
| 88 | gates (lim / mkt / pb entries) | lim / atr/atr100 0.9-1.2 | M15 | 29.8 | -4.29 | -1.83 | -3.57 | -0.29 | -2.0 | -1.1 | fail (trL,trS,vaL,vaS <=0) |
| 89 | gates (lim / mkt / pb entries) | mkt / atr/atr100 0.9-1.2 | M15 | 38.4 | -4.59 | -3.99 | -1.46 | +3.76 | -3.2 | 0.4 | fail (trL,trS,vaL <=0) |
| 90 | gates (lim / mkt / pb entries) | pb / atr/atr100 0.9-1.2 | M15 | 24.1 | -0.17 | -1.43 | +1.48 | +5.37 | -0.5 | 1.4 | fail (trL,trS <=0) |
| 91 | gates (lim / mkt / pb entries) | lim / atr/atr100>1.2 | M15 | 17.2 | +2.69 | -1.73 | +0.30 | -3.70 | 0.3 | -0.6 | fail (trS,vaS <=0) |
| 92 | gates (lim / mkt / pb entries) | mkt / atr/atr100>1.2 | M15 | 24.8 | +4.27 | -0.33 | -1.18 | -1.28 | 1.2 | -0.5 | fail (trS,vaL,vaS <=0) |
| 93 | gates (lim / mkt / pb entries) | pb / atr/atr100>1.2 | M15 | 16.9 | +3.48 | +1.14 | +0.28 | -3.74 | 1.2 | -0.6 | fail (vaS <=0) |
| 94 | gates (lim / mkt / pb entries) | lim / atr_vs_h1 low3 | M15 | 31.6 | +0.20 | +0.63 | -5.09 | +3.42 | 0.3 | -1.0 | fail (vaL <=0) |
| 95 | gates (lim / mkt / pb entries) | mkt / atr_vs_h1 low3 | M15 | 39.2 | +0.06 | -2.46 | -1.51 | +2.68 | -0.8 | -0.0 | fail (trS,vaL <=0) |
| 96 | gates (lim / mkt / pb entries) | pb / atr_vs_h1 low3 | M15 | 24.6 | -1.20 | +2.66 | -0.46 | +2.75 | 0.3 | 0.2 | fail (trL,vaL <=0) |
| 97 | gates (lim / mkt / pb entries) | lim / atr_vs_h1 high3 | M15 | 28.0 | +1.73 | -1.59 | +0.93 | -0.81 | 0.0 | 0.1 | fail (trS,vaS <=0) |
| 98 | gates (lim / mkt / pb entries) | mkt / atr_vs_h1 high3 | M15 | 39.2 | +2.84 | -1.14 | +0.27 | +0.33 | 0.7 | 0.2 | fail (trS <=0) |
| 99 | gates (lim / mkt / pb entries) | pb / atr_vs_h1 high3 | M15 | 26.4 | +4.04 | +1.11 | +0.99 | +1.68 | 1.6 | 0.6 | all >0 but weak (<3 se train or <2 se valid) |
| 100 | gates (lim / mkt / pb entries) | lim / with week VWAP side | M15 | 69.9 | -0.68 | +0.66 | -2.97 | -0.71 | -0.0 | -1.5 | fail (trL,vaL,vaS <=0) |
| 101 | gates (lim / mkt / pb entries) | mkt / with week VWAP side | M15 | 91.5 | +0.32 | -1.18 | -0.64 | +1.75 | -0.4 | 0.2 | fail (trS,vaL <=0) |
| 102 | gates (lim / mkt / pb entries) | pb / with week VWAP side | M15 | 59.5 | +1.51 | +2.18 | +1.10 | -0.03 | 1.7 | 0.5 | fail (vaS <=0) |
| 103 | gates (lim / mkt / pb entries) | lim / AGAINST week VWAP side | M15 | 20.7 | -1.60 | -3.33 | -0.18 | -2.60 | -1.3 | -0.5 | fail (trL,trS,vaL,vaS <=0) |
| 104 | gates (lim / mkt / pb entries) | mkt / AGAINST week VWAP side | M15 | 26.1 | -3.67 | -5.47 | +0.33 | +2.26 | -2.8 | 0.6 | fail (trL,trS <=0) |
| 105 | gates (lim / mkt / pb entries) | pb / AGAINST week VWAP side | M15 | 16.3 | -2.96 | -2.43 | +0.57 | +8.05 | -1.3 | 1.5 | fail (trL,trS <=0) |
| 106 | gates (lim / mkt / pb entries) | lim / with month VWAP side | M15 | 56.6 | -0.21 | +1.07 | -3.53 | -2.25 | 0.4 | -2.1 | fail (trL,vaL,vaS <=0) |
| 107 | gates (lim / mkt / pb entries) | mkt / with month VWAP side | M15 | 74.3 | +0.47 | -1.15 | -1.42 | +0.15 | -0.3 | -0.7 | fail (trS,vaL <=0) |
| 108 | gates (lim / mkt / pb entries) | pb / with month VWAP side | M15 | 48.2 | +2.46 | +2.56 | +1.30 | -1.92 | 2.1 | 0.2 | fail (vaS <=0) |
| 109 | gates (lim / mkt / pb entries) | lim / AGAINST month VWAP side | M15 | 34.0 | -2.06 | -2.37 | +1.40 | -0.03 | -1.5 | 0.2 | fail (trL,trS,vaS <=0) |
| 110 | gates (lim / mkt / pb entries) | mkt / AGAINST month VWAP side | M15 | 43.3 | -2.40 | -3.77 | +2.84 | +3.64 | -2.4 | 1.8 | fail (trL,trS <=0) |
| 111 | gates (lim / mkt / pb entries) | pb / AGAINST month VWAP side | M15 | 27.6 | -2.90 | -1.20 | +0.03 | +5.88 | -1.3 | 1.5 | fail (trL,trS <=0) |
| 112 | gates (lim / mkt / pb entries) | lim / with daily EMA20 side | M15 | 52.3 | -0.24 | +1.92 | -4.15 | -4.30 | 0.7 | -2.8 | fail (trL,vaL,vaS <=0) |
| 113 | gates (lim / mkt / pb entries) | mkt / with daily EMA20 side | M15 | 68.1 | +0.35 | -1.34 | -1.43 | -1.46 | -0.4 | -1.1 | fail (trS,vaL,vaS <=0) |
| 114 | gates (lim / mkt / pb entries) | pb / with daily EMA20 side | M15 | 44.2 | +0.40 | +2.25 | +1.08 | -1.73 | 1.0 | 0.2 | fail (vaS <=0) |
| 115 | gates (lim / mkt / pb entries) | lim / AGAINST daily EMA20 side | M15 | 36.8 | -1.49 | -3.34 | +4.94 | +0.94 | -1.7 | 1.1 | fail (trL,trS <=0) |
| 116 | gates (lim / mkt / pb entries) | mkt / AGAINST daily EMA20 side | M15 | 47.7 | -1.34 | -3.51 | +3.64 | +4.06 | -2.0 | 2.2 | fail (trL,trS <=0) |
| 117 | gates (lim / mkt / pb entries) | pb / AGAINST daily EMA20 side | M15 | 30.2 | +1.40 | -0.78 | +0.73 | +4.40 | 0.2 | 1.5 | fail (trS <=0) |
| 118 | gates (lim / mkt / pb entries) | lim / with 5-day trend | M15 | 52.9 | -0.11 | +1.97 | -3.48 | -1.75 | 0.7 | -1.9 | fail (trL,vaL,vaS <=0) |
| 119 | gates (lim / mkt / pb entries) | mkt / with 5-day trend | M15 | 69.3 | +0.66 | -0.54 | -1.09 | +1.16 | 0.1 | -0.3 | fail (trS,vaL <=0) |
| 120 | gates (lim / mkt / pb entries) | pb / with 5-day trend | M15 | 45.1 | +1.45 | +1.70 | +2.21 | +1.42 | 1.3 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 121 | gates (lim / mkt / pb entries) | lim / AGAINST 5-day trend | M15 | 36.2 | -1.81 | -3.17 | +0.06 | -0.64 | -1.8 | -0.2 | fail (trL,trS,vaS <=0) |
| 122 | gates (lim / mkt / pb entries) | mkt / AGAINST 5-day trend | M15 | 46.4 | -2.10 | -4.46 | +1.02 | +2.56 | -2.7 | 1.1 | fail (trL,trS <=0) |
| 123 | gates (lim / mkt / pb entries) | pb / AGAINST 5-day trend | M15 | 29.2 | -0.37 | +0.04 | -1.94 | +2.44 | -0.1 | 0.2 | fail (trL,vaL <=0) |
| 124 | gates (lim / mkt / pb entries) | lim / cmo>=40 | M15 | 64.8 | -0.74 | -0.80 | +0.11 | -3.01 | -0.7 | -0.8 | fail (trL,trS,vaS <=0) |
| 125 | gates (lim / mkt / pb entries) | mkt / cmo>=40 | M15 | 85.2 | -0.73 | -2.14 | +1.12 | +2.14 | -1.5 | 1.2 | fail (trL,trS <=0) |
| 126 | gates (lim / mkt / pb entries) | pb / cmo>=40 | M15 | 55.6 | +0.09 | +0.83 | +1.02 | +2.06 | 0.4 | 1.0 | all >0 but weak (<3 se train or <2 se valid) |
| 127 | gates (lim / mkt / pb entries) | lim / body>=70% | M15 | 65.7 | -1.32 | -0.35 | -2.50 | -0.73 | -0.8 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 128 | gates (lim / mkt / pb entries) | mkt / body>=70% | M15 | 88.2 | -1.09 | -1.74 | -0.51 | +2.78 | -1.6 | 0.7 | fail (trL,trS,vaL <=0) |
| 129 | gates (lim / mkt / pb entries) | pb / body>=70% | M15 | 59.3 | +0.75 | +1.35 | +0.86 | +3.27 | 1.0 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 130 | gates (lim / mkt / pb entries) | lim / close<=12% from ext | M15 | 55.4 | +0.29 | -0.23 | -3.17 | +0.27 | 0.0 | -1.1 | fail (trS,vaL <=0) |
| 131 | gates (lim / mkt / pb entries) | mkt / close<=12% from ext | M15 | 72.9 | -0.04 | -1.73 | -0.05 | +3.65 | -0.8 | 1.0 | fail (trL,trS,vaL <=0) |
| 132 | gates (lim / mkt / pb entries) | pb / close<=12% from ext | M15 | 47.6 | +1.32 | +0.89 | +2.21 | +4.52 | 0.9 | 1.8 | all >0 but weak (<3 se train or <2 se valid) |
| 133 | gates (lim / mkt / pb entries) | lim / range>=1.3ATR | M15 | 51.5 | -1.12 | +1.18 | -3.44 | -2.61 | 0.0 | -1.9 | fail (trL,vaL,vaS <=0) |
| 134 | gates (lim / mkt / pb entries) | mkt / range>=1.3ATR | M15 | 71.8 | -0.58 | -1.01 | -0.69 | +1.57 | -0.8 | 0.2 | fail (trL,trS,vaL <=0) |
| 135 | gates (lim / mkt / pb entries) | pb / range>=1.3ATR | M15 | 50.3 | +1.20 | +1.87 | +1.02 | +1.53 | 1.3 | 0.8 | all >0 but weak (<3 se train or <2 se valid) |
| 136 | gates (lim / mkt / pb entries) | lim / mom>=1.5ATR | M15 | 78.4 | -1.08 | -0.79 | -1.35 | -1.69 | -1.0 | -1.1 | fail (trL,trS,vaL,vaS <=0) |
| 137 | gates (lim / mkt / pb entries) | mkt / mom>=1.5ATR | M15 | 102.7 | -0.62 | -2.39 | +0.16 | +2.04 | -1.8 | 0.8 | fail (trL,trS <=0) |
| 138 | gates (lim / mkt / pb entries) | pb / mom>=1.5ATR | M15 | 66.2 | +0.01 | +0.82 | +0.99 | +2.19 | 0.4 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 139 | gates (lim / mkt / pb entries) | lim / break>=0.3ATR | M15 | 67.9 | -0.60 | +1.03 | -2.43 | -1.74 | 0.2 | -1.5 | fail (trL,vaL,vaS <=0) |
| 140 | gates (lim / mkt / pb entries) | mkt / break>=0.3ATR | M15 | 92.5 | -0.64 | -1.68 | +0.10 | +1.71 | -1.3 | 0.6 | fail (trL,trS <=0) |
| 141 | gates (lim / mkt / pb entries) | pb / break>=0.3ATR | M15 | 64.8 | +0.81 | +1.38 | +1.89 | +1.87 | 1.0 | 1.3 | all >0 but weak (<3 se train or <2 se valid) |
| 142 | gates (lim / mkt / pb entries) | lim / break<0.1ATR | M15 | 7.5 | +1.96 | -5.85 | -0.46 | +0.44 | -0.6 | -0.0 | fail (trS,vaL <=0), few trades |
| 143 | gates (lim / mkt / pb entries) | mkt / break<0.1ATR | M15 | 7.8 | +1.48 | -3.80 | -1.63 | +2.71 | -0.4 | 0.0 | fail (trS,vaL <=0), few trades |
| 144 | gates (lim / mkt / pb entries) | pb / break<0.1ATR | M15 | 2.9 | +0.84 | -16.28 | -1.46 | -3.12 | -1.6 | -0.3 | fail (trS,vaL,vaS <=0), few trades |
| 145 | gates (lim / mkt / pb entries) | lim / NY L14-17 S07-10 | M5 | 29.1 | -7.11 | -3.29 | +0.43 | +6.61 | -3.0 | 1.8 | fail (trL,trS <=0) |
| 146 | gates (lim / mkt / pb entries) | mkt / NY L14-17 S07-10 | M5 | 37.1 | -5.55 | -2.35 | -0.81 | +4.63 | -2.6 | 1.1 | fail (trL,trS,vaL <=0) |
| 147 | gates (lim / mkt / pb entries) | pb / NY L14-17 S07-10 | M5 | 21.9 | -3.69 | -1.10 | -2.82 | +3.52 | -1.2 | 0.3 | fail (trL,trS,vaL <=0) |
| 148 | gates (lim / mkt / pb entries) | lim / NY L14-17 only | M5 | 10.5 | -7.11 |  | +0.43 |  | -2.8 | 0.1 | one direction only (fails) |
| 149 | gates (lim / mkt / pb entries) | mkt / NY L14-17 only | M5 | 13.6 | -5.55 |  | -0.81 |  | -2.5 | -0.3 | one direction only (fails) |
| 150 | gates (lim / mkt / pb entries) | pb / NY L14-17 only | M5 | 8.2 | -3.69 |  | -2.82 |  | -1.3 | -0.8 | one direction only (fails) |
| 151 | gates (lim / mkt / pb entries) | lim / NY S07-10 only | M5 | 18.6 |  | -3.29 |  | +6.61 | -1.7 | 2.3 | one direction only (fails) |
| 152 | gates (lim / mkt / pb entries) | mkt / NY S07-10 only | M5 | 23.5 |  | -2.35 |  | +4.63 | -1.4 | 1.8 | one direction only (fails) |
| 153 | gates (lim / mkt / pb entries) | pb / NY S07-10 only | M5 | 13.7 |  | -1.10 |  | +3.52 | -0.5 | 1.1 | one direction only (fails) |
| 154 | gates (lim / mkt / pb entries) | lim / NY 07-17 both | M5 | 92.7 | -1.61 | -2.83 | -1.52 | -1.50 | -2.6 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 155 | gates (lim / mkt / pb entries) | mkt / NY 07-17 both | M5 | 120.6 | -1.21 | -3.16 | -1.94 | -2.73 | -2.9 | -2.1 | fail (trL,trS,vaL,vaS <=0) |
| 156 | gates (lim / mkt / pb entries) | pb / NY 07-17 both | M5 | 74.9 | +0.68 | -2.27 | -0.94 | -4.60 | -0.8 | -1.9 | fail (trS,vaL,vaS <=0) |
| 157 | gates (lim / mkt / pb entries) | lim / atr/atr100<0.9 | M5 | 110.8 | -1.41 | -1.01 | -2.60 | -2.35 | -1.5 | -2.1 | fail (trL,trS,vaL,vaS <=0) |
| 158 | gates (lim / mkt / pb entries) | mkt / atr/atr100<0.9 | M5 | 140.7 | -1.28 | -2.52 | -1.30 | -0.52 | -2.7 | -1.0 | fail (trL,trS,vaL,vaS <=0) |
| 159 | gates (lim / mkt / pb entries) | pb / atr/atr100<0.9 | M5 | 87.1 | +0.63 | -0.59 | -2.88 | -1.16 | 0.0 | -1.7 | fail (trS,vaL,vaS <=0) |
| 160 | gates (lim / mkt / pb entries) | lim / atr/atr100 0.9-1.2 | M5 | 85.9 | -2.97 | -1.27 | +0.87 | +2.52 | -2.4 | 1.3 | fail (trL,trS <=0) |
| 161 | gates (lim / mkt / pb entries) | mkt / atr/atr100 0.9-1.2 | M5 | 109.6 | -3.04 | -3.31 | +0.76 | +2.60 | -4.0 | 1.5 | fail (trL,trS <=0) |
| 162 | gates (lim / mkt / pb entries) | pb / atr/atr100 0.9-1.2 | M5 | 67.5 | -1.92 | -0.62 | +2.24 | +2.17 | -1.3 | 1.7 | fail (trL,trS <=0) |
| 163 | gates (lim / mkt / pb entries) | lim / atr/atr100>1.2 | M5 | 55.1 | +2.67 | -1.01 | +1.48 | +3.21 | 0.7 | 1.5 | fail (trS <=0) |
| 164 | gates (lim / mkt / pb entries) | mkt / atr/atr100>1.2 | M5 | 74.4 | +3.47 | -1.26 | -0.69 | +0.27 | 1.1 | -0.2 | fail (trS,vaL <=0) |
| 165 | gates (lim / mkt / pb entries) | pb / atr/atr100>1.2 | M5 | 48.9 | +4.93 | -0.02 | -0.55 | -0.08 | 2.2 | -0.2 | fail (trS,vaL,vaS <=0) |
| 166 | gates (lim / mkt / pb entries) | lim / atr_vs_h1 low3 | M5 | 85.7 | -2.57 | -1.24 | -2.49 | -4.34 | -2.1 | -2.4 | fail (trL,trS,vaL,vaS <=0) |
| 167 | gates (lim / mkt / pb entries) | mkt / atr_vs_h1 low3 | M5 | 108.2 | -1.35 | -3.09 | -1.83 | -2.48 | -2.7 | -1.7 | fail (trL,trS,vaL,vaS <=0) |
| 168 | gates (lim / mkt / pb entries) | pb / atr_vs_h1 low3 | M5 | 66.9 | +0.60 | -1.67 | -2.54 | -4.09 | -0.5 | -2.0 | fail (trS,vaL,vaS <=0) |
| 169 | gates (lim / mkt / pb entries) | lim / atr_vs_h1 high3 | M5 | 81.4 | +1.40 | -1.72 | +2.26 | +3.55 | -0.2 | 2.2 | fail (trS <=0) |
| 170 | gates (lim / mkt / pb entries) | mkt / atr_vs_h1 high3 | M5 | 108.2 | +1.84 | -2.03 | +0.23 | +1.20 | -0.1 | 0.6 | fail (trS <=0) |
| 171 | gates (lim / mkt / pb entries) | pb / atr_vs_h1 high3 | M5 | 70.0 | +2.45 | +0.25 | -0.37 | +0.99 | 1.4 | 0.2 | fail (vaL <=0) |
| 172 | gates (lim / mkt / pb entries) | lim / with week VWAP side | M5 | 188.0 | -1.30 | -1.26 | -0.20 | +1.07 | -2.1 | 0.4 | fail (trL,trS,vaL <=0) |
| 173 | gates (lim / mkt / pb entries) | mkt / with week VWAP side | M5 | 242.6 | -1.14 | -2.40 | -0.58 | +1.48 | -3.3 | 0.3 | fail (trL,trS,vaL <=0) |
| 174 | gates (lim / mkt / pb entries) | pb / with week VWAP side | M5 | 151.6 | +0.72 | -0.45 | -0.55 | -0.01 | 0.2 | -0.4 | fail (trS,vaL,vaS <=0) |
| 175 | gates (lim / mkt / pb entries) | lim / AGAINST week VWAP side | M5 | 63.9 | -0.35 | -0.65 | -1.64 | +0.33 | -0.5 | -0.3 | fail (trL,trS,vaL <=0) |
| 176 | gates (lim / mkt / pb entries) | mkt / AGAINST week VWAP side | M5 | 82.4 | +0.14 | -2.73 | +0.60 | -0.71 | -1.4 | -0.1 | fail (trS,vaS <=0) |
| 177 | gates (lim / mkt / pb entries) | pb / AGAINST week VWAP side | M5 | 52.0 | +1.12 | -0.50 | +0.37 | +1.40 | 0.3 | 0.5 | fail (trS <=0) |
| 178 | gates (lim / mkt / pb entries) | lim / with month VWAP side | M5 | 156.9 | -1.41 | -1.78 | -0.59 | +0.49 | -2.4 | -0.2 | fail (trL,trS,vaL <=0) |
| 179 | gates (lim / mkt / pb entries) | mkt / with month VWAP side | M5 | 201.7 | -1.12 | -2.86 | -0.45 | +0.09 | -3.3 | -0.3 | fail (trL,trS,vaL <=0) |
| 180 | gates (lim / mkt / pb entries) | pb / with month VWAP side | M5 | 125.9 | +1.24 | -0.76 | -0.52 | -0.16 | 0.4 | -0.4 | fail (trS,vaL,vaS <=0) |
| 181 | gates (lim / mkt / pb entries) | lim / AGAINST month VWAP side | M5 | 95.0 | -0.45 | -0.05 | +0.01 | +1.22 | -0.3 | 0.6 | fail (trL,trS <=0) |
| 182 | gates (lim / mkt / pb entries) | mkt / AGAINST month VWAP side | M5 | 123.2 | -0.30 | -1.91 | -0.13 | +1.63 | -1.5 | 0.9 | fail (trL,trS,vaL <=0) |
| 183 | gates (lim / mkt / pb entries) | pb / AGAINST month VWAP side | M5 | 77.8 | +0.08 | -0.04 | +0.03 | +0.91 | 0.0 | 0.4 | fail (trS <=0) |
| 184 | gates (lim / mkt / pb entries) | lim / with daily EMA20 side | M5 | 143.4 | -1.22 | -1.67 | -0.70 | -0.55 | -2.1 | -0.7 | fail (trL,trS,vaL,vaS <=0) |
| 185 | gates (lim / mkt / pb entries) | mkt / with daily EMA20 side | M5 | 184.2 | -1.35 | -2.74 | -0.40 | -1.19 | -3.3 | -0.7 | fail (trL,trS,vaL,vaS <=0) |
| 186 | gates (lim / mkt / pb entries) | pb / with daily EMA20 side | M5 | 114.8 | +0.85 | -0.70 | -0.51 | -1.19 | 0.1 | -0.7 | fail (trS,vaL,vaS <=0) |
| 187 | gates (lim / mkt / pb entries) | lim / AGAINST daily EMA20 side | M5 | 104.6 | -0.87 | -0.05 | +0.59 | +1.66 | -0.6 | 1.1 | fail (trL,trS <=0) |
| 188 | gates (lim / mkt / pb entries) | mkt / AGAINST daily EMA20 side | M5 | 135.8 | +0.01 | -2.11 | -0.29 | +2.05 | -1.4 | 1.3 | fail (trS,vaL <=0) |
| 189 | gates (lim / mkt / pb entries) | pb / AGAINST daily EMA20 side | M5 | 85.8 | +0.79 | -0.05 | +0.09 | +1.33 | 0.4 | 0.7 | fail (trS <=0) |
| 190 | gates (lim / mkt / pb entries) | lim / with 5-day trend | M5 | 146.4 | -0.81 | -1.29 | -0.05 | +1.08 | -1.5 | 0.4 | fail (trL,trS,vaL <=0) |
| 191 | gates (lim / mkt / pb entries) | mkt / with 5-day trend | M5 | 187.7 | -0.76 | -2.76 | -0.16 | +0.64 | -2.8 | 0.1 | fail (trL,trS,vaL <=0) |
| 192 | gates (lim / mkt / pb entries) | pb / with 5-day trend | M5 | 117.0 | +1.44 | -0.81 | -0.66 | -0.21 | 0.5 | -0.5 | fail (trS,vaL,vaS <=0) |
| 193 | gates (lim / mkt / pb entries) | lim / AGAINST 5-day trend | M5 | 101.7 | -1.50 | -0.62 | -1.45 | +0.66 | -1.2 | -0.2 | fail (trL,trS,vaL <=0) |
| 194 | gates (lim / mkt / pb entries) | mkt / AGAINST 5-day trend | M5 | 132.2 | -0.82 | -2.13 | -0.91 | +1.06 | -2.1 | 0.2 | fail (trL,trS,vaL <=0) |
| 195 | gates (lim / mkt / pb entries) | pb / AGAINST 5-day trend | M5 | 83.6 | -0.14 | +0.03 | +0.14 | +0.91 | -0.1 | 0.4 | fail (trL <=0) |
| 196 | gates (lim / mkt / pb entries) | lim / cmo>=40 | M5 | 176.7 | -0.22 | -1.43 | +0.03 | +1.08 | -1.3 | 0.6 | fail (trL,trS <=0) |
| 197 | gates (lim / mkt / pb entries) | mkt / cmo>=40 | M5 | 229.5 | -0.48 | -2.53 | +0.01 | +0.70 | -2.7 | 0.4 | fail (trL,trS <=0) |
| 198 | gates (lim / mkt / pb entries) | pb / cmo>=40 | M5 | 146.0 | +1.47 | -0.52 | +0.01 | +1.23 | 0.8 | 0.5 | fail (trS <=0) |
| 199 | gates (lim / mkt / pb entries) | lim / body>=70% | M5 | 189.8 | -1.49 | -1.08 | -1.14 | +1.39 | -2.1 | -0.0 | fail (trL,trS,vaL <=0) |
| 200 | gates (lim / mkt / pb entries) | mkt / body>=70% | M5 | 251.6 | -0.61 | -2.94 | -0.36 | +1.44 | -3.3 | 0.6 | fail (trL,trS,vaL <=0) |
| 201 | gates (lim / mkt / pb entries) | pb / body>=70% | M5 | 164.8 | +0.70 | -0.73 | -0.28 | +0.84 | 0.0 | 0.2 | fail (trS,vaL <=0) |
| 202 | gates (lim / mkt / pb entries) | lim / close<=12% from ext | M5 | 157.9 | -1.65 | -1.24 | -0.56 | +1.99 | -2.2 | 0.6 | fail (trL,trS,vaL <=0) |
| 203 | gates (lim / mkt / pb entries) | mkt / close<=12% from ext | M5 | 204.9 | -1.36 | -3.35 | -0.17 | +1.67 | -4.0 | 0.7 | fail (trL,trS,vaL <=0) |
| 204 | gates (lim / mkt / pb entries) | pb / close<=12% from ext | M5 | 129.5 | +0.24 | -0.56 | -0.12 | +1.12 | -0.2 | 0.4 | fail (trS,vaL <=0) |
| 205 | gates (lim / mkt / pb entries) | lim / range>=1.3ATR | M5 | 132.4 | -1.86 | -0.32 | -0.99 | +1.64 | -1.5 | 0.2 | fail (trL,trS,vaL <=0) |
| 206 | gates (lim / mkt / pb entries) | mkt / range>=1.3ATR | M5 | 182.5 | -1.37 | -2.25 | -1.27 | +1.05 | -2.9 | -0.2 | fail (trL,trS,vaL <=0) |
| 207 | gates (lim / mkt / pb entries) | pb / range>=1.3ATR | M5 | 124.9 | +1.41 | +0.38 | -0.60 | +0.87 | 1.2 | 0.1 | fail (vaL <=0) |
| 208 | gates (lim / mkt / pb entries) | lim / mom>=1.5ATR | M5 | 220.1 | -0.80 | -1.21 | -0.40 | +1.21 | -1.8 | 0.4 | fail (trL,trS,vaL <=0) |
| 209 | gates (lim / mkt / pb entries) | mkt / mom>=1.5ATR | M5 | 286.0 | -0.87 | -2.54 | -0.42 | +0.83 | -3.4 | 0.2 | fail (trL,trS,vaL <=0) |
| 210 | gates (lim / mkt / pb entries) | pb / mom>=1.5ATR | M5 | 180.8 | +1.02 | -0.13 | -0.58 | +1.12 | 0.8 | 0.2 | fail (trS,vaL <=0) |
| 211 | gates (lim / mkt / pb entries) | lim / break>=0.3ATR | M5 | 186.8 | -1.29 | -0.47 | -0.67 | +1.13 | -1.4 | 0.1 | fail (trL,trS,vaL <=0) |
| 212 | gates (lim / mkt / pb entries) | mkt / break>=0.3ATR | M5 | 254.0 | -1.12 | -2.14 | -0.84 | +0.93 | -3.1 | -0.1 | fail (trL,trS,vaL <=0) |
| 213 | gates (lim / mkt / pb entries) | pb / break>=0.3ATR | M5 | 174.0 | +0.63 | -0.33 | -0.84 | +0.38 | 0.3 | -0.4 | fail (trS,vaL <=0) |
| 214 | gates (lim / mkt / pb entries) | lim / break<0.1ATR | M5 | 20.6 | +0.42 | -2.32 | +0.02 | +0.31 | -0.5 | 0.1 | fail (trS <=0) |
| 215 | gates (lim / mkt / pb entries) | mkt / break<0.1ATR | M5 | 21.2 | +0.94 | -2.79 | +0.88 | +1.28 | -0.5 | 0.4 | fail (trS <=0) |
| 216 | gates (lim / mkt / pb entries) | pb / break<0.1ATR | M5 | 7.2 | +2.46 | -1.67 | +7.20 | -8.95 | 0.2 | 0.2 | fail (trS,vaS <=0), few trades |
| 217 | entry mechanics | base limit5 stop_h | H1 | 24.3 | -6.60 | -1.38 | -2.28 | -1.03 | -2.5 | -0.8 | fail (trL,trS,vaL,vaS <=0) |
| 218 | entry mechanics | base limit5 stop1.8 | H1 | 24.3 | -6.60 | -0.83 | -1.94 | -2.39 | -2.3 | -0.9 | fail (trL,trS,vaL,vaS <=0) |
| 219 | entry mechanics | market at signal close | H1 | 33.2 | -3.76 | -2.32 | -1.22 | -1.70 | -2.2 | -0.7 | fail (trL,trS,vaL,vaS <=0) |
| 220 | entry mechanics | limit window 1 | H1 | 17.2 | -6.75 | -1.00 | -3.60 | -3.03 | -2.0 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 221 | entry mechanics | limit window 2 | H1 | 20.6 | -6.01 | -1.79 | -4.20 | -2.70 | -2.2 | -1.4 | fail (trL,trS,vaL,vaS <=0) |
| 222 | entry mechanics | limit window 3 | H1 | 22.3 | -6.49 | -2.04 | -3.11 | -2.78 | -2.5 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 223 | entry mechanics | limit depth 25% of range | H1 | 26.2 | -5.52 | -1.41 | -1.18 | -3.05 | -2.2 | -0.9 | fail (trL,trS,vaL,vaS <=0) |
| 224 | entry mechanics | limit depth 50% of range | H1 | 20.2 | -3.88 | -0.82 | +0.35 | -2.28 | -1.3 | -0.3 | fail (trL,trS,vaS <=0) |
| 225 | entry mechanics | limit depth 75% of range | H1 | 14.7 | -2.36 | -0.33 | -1.86 | -2.93 | -0.7 | -0.8 | fail (trL,trS,vaL,vaS <=0) |
| 226 | entry mechanics | limit depth 100% of range | H1 | 11.2 | +0.90 | -2.03 | -2.99 | -1.63 | -0.2 | -0.7 | fail (trS,vaL,vaS <=0) |
| 227 | entry mechanics | confirm W3 mkt stop1.8 | H1 | 12.7 | -3.62 | -3.40 | +2.72 | +0.43 | -1.5 | 0.6 | fail (trL,trS <=0) |
| 228 | entry mechanics | confirm W5 mkt stop1.8 | H1 | 15.9 | -3.90 | -3.20 | +3.05 | -0.26 | -1.7 | 0.6 | fail (trL,trS,vaS <=0) |
| 229 | entry mechanics | confirm W5 mkt stop struct | H1 | 15.9 | +0.00 | -3.83 | -5.45 | -2.24 | -0.9 | -1.5 | fail (trL,trS,vaL,vaS <=0) |
| 230 | entry mechanics | confirm W5 mkt stop sigcandle | H1 | 15.9 | -2.37 | -4.01 | +0.13 | -1.58 | -1.5 | -0.2 | fail (trL,trS,vaS <=0) |
| 231 | entry mechanics | confirm W5 mkt stop1.0 | H1 | 15.9 | -1.52 | -2.93 | +0.26 | -4.43 | -1.1 | -0.5 | fail (trL,trS,vaS <=0) |
| 232 | entry mechanics | confirm W5 mkt stop3.0 | H1 | 15.9 | -3.56 | -3.20 | +6.09 | -2.89 | -1.6 | 1.0 | fail (trL,trS,vaS <=0) |
| 233 | entry mechanics | confirm W5 break-of-bar stop1.8 | H1 | 12.1 | -4.41 | -0.89 | +1.25 | -0.67 | -1.2 | 0.2 | fail (trL,trS,vaS <=0) |
| 234 | entry mechanics | confirm W8 mkt stop1.8 | H1 | 18.7 | -3.38 | -3.22 | +2.40 | -0.31 | -1.7 | 0.5 | fail (trL,trS,vaS <=0) |
| 235 | entry mechanics | confirm W5 close-beyond only | H1 | 17.9 | -4.29 | -1.37 | +1.85 | +0.61 | -1.5 | 0.5 | fail (trL,trS <=0) |
| 236 | entry mechanics | nofill N1 mkt if beyond 0.0ATR | H1 | 11.4 | +1.06 | -4.05 | +6.57 | -0.63 | -0.4 | 1.2 | fail (trS,vaS <=0) |
| 237 | entry mechanics | nofill N1 mkt if beyond 0.3ATR | H1 | 7.4 | +2.68 | -4.73 | +7.02 | -2.92 | -0.1 | 0.7 | fail (trS,vaS <=0) |
| 238 | entry mechanics | nofill N2 mkt if beyond 0.0ATR | H1 | 9.6 | -0.52 | -2.88 | +5.93 | +4.01 | -0.5 | 1.5 | fail (trL,trS <=0) |
| 239 | entry mechanics | nofill N2 mkt if beyond 0.3ATR | H1 | 7.1 | -0.23 | -1.95 | +6.72 | +4.40 | -0.3 | 1.5 | fail (trL,trS <=0) |
| 240 | entry mechanics | nofill N3 mkt if beyond 0.0ATR | H1 | 8.7 | +0.88 | +0.45 | +3.76 | +4.54 | 0.3 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 241 | entry mechanics | nofill N3 mkt if beyond 0.3ATR | H1 | 7.0 | -1.78 | -2.00 | +3.47 | +5.58 | -0.6 | 1.0 | fail (trL,trS <=0) |
| 242 | entry mechanics | 2nd disp K6 limit | H1 | 7.6 | -5.40 | -7.04 | +1.74 | +3.39 | -2.0 | 0.6 | fail (trL,trS <=0) |
| 243 | entry mechanics | 2nd disp K6 market | H1 | 10.5 | -2.18 | -6.34 | +0.51 | +5.02 | -1.5 | 0.6 | fail (trL,trS <=0) |
| 244 | entry mechanics | 2nd disp K12 limit | H1 | 9.9 | -6.08 | -4.14 | -0.01 | -0.92 | -2.0 | -0.1 | fail (trL,trS,vaL,vaS <=0) |
| 245 | entry mechanics | 2nd disp K12 market | H1 | 13.6 | -3.09 | -4.76 | +0.41 | +1.27 | -1.7 | 0.2 | fail (trL,trS <=0) |
| 246 | entry mechanics | 1st disp only K12 market | H1 | 19.6 | -4.26 | -0.79 | -3.08 | -3.63 | -1.4 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 247 | entry mechanics | 2nd disp K24 limit | H1 | 14.6 | -5.81 | -3.01 | -3.10 | -1.94 | -2.1 | -1.0 | fail (trL,trS,vaL,vaS <=0) |
| 248 | entry mechanics | 2nd disp K24 market | H1 | 19.7 | -4.35 | -4.76 | -2.72 | +1.59 | -2.4 | -0.5 | fail (trL,trS,vaL <=0) |
| 249 | entry mechanics | 1st pullback close | H1 | 32.6 | +0.40 | +0.32 | +3.22 | +0.68 | 0.3 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 250 | entry mechanics | 1st pullback close above lvl | H1 | 21.7 | +1.41 | +0.04 | +4.92 | +1.15 | 0.4 | 1.4 | all >0 but weak (<3 se train or <2 se valid) |
| 251 | entry mechanics | FADE market | H1 | 33.2 | +2.12 | +3.43 | +1.43 | +1.86 | 2.0 | 0.9 | all >0 but weak (<3 se train or <2 se valid) |
| 252 | entry mechanics | FADE stop-entry at retest lvl | H1 | 24.3 | +1.03 | +5.42 | +3.46 | -0.35 | 2.0 | 0.5 | fail (vaS <=0) |
| 253 | gates (lim / mkt / pb entries) | lim / NY L14-17 S07-10 | H1 | 3.2 | -10.22 | +0.13 | -10.09 | -1.52 | -0.4 | -0.6 | fail (trL,vaL,vaS <=0) |
| 254 | gates (lim / mkt / pb entries) | mkt / NY L14-17 S07-10 | H1 | 4.6 | -7.70 | -2.40 | -7.28 | +3.02 | -0.9 | -0.0 | fail (trL,trS,vaL <=0) |
| 255 | gates (lim / mkt / pb entries) | pb / NY L14-17 S07-10 | H1 | 3.1 | +8.24 | -0.97 | -13.95 | +7.70 | 0.2 | 0.3 | fail (trS,vaL <=0) |
| 256 | gates (lim / mkt / pb entries) | lim / NY L14-17 only | H1 | 0.6 | -10.22 |  | -10.09 |  | -0.9 | -0.8 | one direction only (fails) |
| 257 | gates (lim / mkt / pb entries) | mkt / NY L14-17 only | H1 | 0.9 | -7.70 |  | -7.28 |  | -0.9 | -0.7 | one direction only (fails) |
| 258 | gates (lim / mkt / pb entries) | pb / NY L14-17 only | H1 | 0.7 | +8.24 |  | -13.95 |  | 0.8 | -1.1 | one direction only (fails) |
| 259 | gates (lim / mkt / pb entries) | lim / NY S07-10 only | H1 | 2.6 |  | +0.13 |  | -1.52 | 0.0 | -0.2 | one direction only (fails) |
| 260 | gates (lim / mkt / pb entries) | mkt / NY S07-10 only | H1 | 3.7 |  | -2.40 |  | +3.02 | -0.6 | 0.5 | one direction only (fails) |
| 261 | gates (lim / mkt / pb entries) | pb / NY S07-10 only | H1 | 2.4 |  | -0.97 |  | +7.70 | -0.2 | 1.0 | one direction only (fails) |
| 262 | gates (lim / mkt / pb entries) | lim / NY 07-17 both | H1 | 10.4 | -5.66 | -4.41 | -0.44 | -1.93 | -2.0 | -0.3 | fail (trL,trS,vaL,vaS <=0) |
| 263 | gates (lim / mkt / pb entries) | mkt / NY 07-17 both | H1 | 15.9 | -1.06 | -3.94 | -2.28 | -3.04 | -1.1 | -0.9 | fail (trL,trS,vaL,vaS <=0) |
| 264 | gates (lim / mkt / pb entries) | pb / NY 07-17 both | H1 | 10.8 | +5.64 | -0.36 | +6.69 | -2.74 | 1.1 | 0.7 | fail (trS,vaS <=0) |
| 265 | gates (lim / mkt / pb entries) | lim / atr/atr100<0.9 | H1 | 6.9 | -2.18 | +4.33 | +0.13 | -8.36 | 0.4 | -0.6 | fail (trL,vaS <=0) |
| 266 | gates (lim / mkt / pb entries) | mkt / atr/atr100<0.9 | H1 | 8.4 | -2.66 | -0.15 | +0.24 | -2.51 | -0.5 | -0.2 | fail (trL,trS,vaS <=0) |
| 267 | gates (lim / mkt / pb entries) | pb / atr/atr100<0.9 | H1 | 5.0 | +4.35 | +0.33 | +4.76 | +14.50 | 0.6 | 1.5 | all >0 but weak (<3 se train or <2 se valid) |
| 268 | gates (lim / mkt / pb entries) | lim / atr/atr100 0.9-1.2 | H1 | 14.7 | -10.07 | -4.28 | -3.77 | +0.03 | -3.5 | -0.8 | fail (trL,trS,vaL <=0) |
| 269 | gates (lim / mkt / pb entries) | mkt / atr/atr100 0.9-1.2 | H1 | 19.9 | -6.37 | -5.12 | -3.07 | -0.27 | -3.1 | -0.8 | fail (trL,trS,vaL,vaS <=0) |
| 270 | gates (lim / mkt / pb entries) | pb / atr/atr100 0.9-1.2 | H1 | 12.9 | -1.59 | -0.34 | +4.58 | +3.56 | -0.5 | 1.4 | fail (trL,trS <=0) |
| 271 | gates (lim / mkt / pb entries) | lim / atr/atr100>1.2 | H1 | 2.6 | +4.07 | +0.07 | +4.72 | -3.98 | 0.4 | 0.0 | fail (vaS <=0), few trades |
| 272 | gates (lim / mkt / pb entries) | mkt / atr/atr100>1.2 | H1 | 4.9 | +6.44 | +4.61 | +6.26 | -5.64 | 1.5 | -0.0 | fail (vaS <=0) |
| 273 | gates (lim / mkt / pb entries) | pb / atr/atr100>1.2 | H1 | 3.7 | +8.78 | -0.03 | +7.20 | -13.61 | 1.0 | -0.8 | fail (trS,vaS <=0) |
| 274 | gates (lim / mkt / pb entries) | lim / with week VWAP side | H1 | 21.0 | -6.59 | -1.82 | -2.01 | -2.44 | -2.4 | -0.9 | fail (trL,trS,vaL,vaS <=0) |
| 275 | gates (lim / mkt / pb entries) | mkt / with week VWAP side | H1 | 29.1 | -3.46 | -1.87 | -1.81 | -1.46 | -1.8 | -0.8 | fail (trL,trS,vaL,vaS <=0) |
| 276 | gates (lim / mkt / pb entries) | pb / with week VWAP side | H1 | 19.1 | +1.78 | +0.26 | +5.81 | +1.07 | 0.6 | 1.6 | all >0 but weak (<3 se train or <2 se valid) |
| 277 | gates (lim / mkt / pb entries) | lim / AGAINST week VWAP side | H1 | 3.3 | -6.65 | +4.64 | -0.97 | -2.05 | -0.1 | -0.2 | fail (trL,vaL,vaS <=0) |
| 278 | gates (lim / mkt / pb entries) | mkt / AGAINST week VWAP side | H1 | 4.1 | -6.07 | -5.17 | +6.05 | -3.20 | -1.4 | 0.2 | fail (trL,trS,vaS <=0) |
| 279 | gates (lim / mkt / pb entries) | pb / AGAINST week VWAP side | H1 | 2.6 | -1.32 | -1.60 | -6.03 | +1.66 | -0.3 | -0.2 | fail (trL,trS,vaL <=0), few trades |
| 280 | gates (lim / mkt / pb entries) | lim / with month VWAP side | H1 | 16.8 | -5.13 | +0.99 | -2.49 | -5.96 | -1.1 | -1.3 | fail (trL,vaL,vaS <=0) |
| 281 | gates (lim / mkt / pb entries) | mkt / with month VWAP side | H1 | 23.6 | -2.48 | -0.53 | -1.74 | -5.03 | -0.9 | -1.2 | fail (trL,trS,vaL,vaS <=0) |
| 282 | gates (lim / mkt / pb entries) | pb / with month VWAP side | H1 | 15.6 | +2.23 | +2.01 | +6.72 | -0.36 | 1.0 | 1.6 | fail (vaS <=0) |
| 283 | gates (lim / mkt / pb entries) | lim / AGAINST month VWAP side | H1 | 7.5 | -10.06 | -4.66 | +0.50 | +2.87 | -2.4 | 0.4 | fail (trL,trS <=0) |
| 284 | gates (lim / mkt / pb entries) | mkt / AGAINST month VWAP side | H1 | 9.6 | -6.91 | -6.72 | +1.01 | +3.18 | -2.5 | 0.6 | fail (trL,trS <=0) |
| 285 | gates (lim / mkt / pb entries) | pb / AGAINST month VWAP side | H1 | 6.1 | -0.57 | -5.46 | -2.28 | +3.03 | -0.8 | 0.2 | fail (trL,trS,vaL <=0) |
| 286 | gates (lim / mkt / pb entries) | lim / with daily EMA20 side | H1 | 15.4 | -5.24 | -1.68 | -3.09 | -5.42 | -1.7 | -1.4 | fail (trL,trS,vaL,vaS <=0) |
| 287 | gates (lim / mkt / pb entries) | mkt / with daily EMA20 side | H1 | 21.3 | -3.17 | -2.38 | -1.54 | -2.16 | -1.6 | -0.7 | fail (trL,trS,vaL,vaS <=0) |
| 288 | gates (lim / mkt / pb entries) | pb / with daily EMA20 side | H1 | 13.9 | -0.75 | +0.79 | +7.05 | +3.10 | -0.0 | 2.1 | fail (trL <=0) |
| 289 | gates (lim / mkt / pb entries) | lim / AGAINST daily EMA20 side | H1 | 8.6 | -7.59 | -0.40 | +4.10 | +0.35 | -1.5 | 0.4 | fail (trL,trS <=0) |
| 290 | gates (lim / mkt / pb entries) | mkt / AGAINST daily EMA20 side | H1 | 11.4 | -3.34 | -2.33 | +0.50 | -1.24 | -1.2 | -0.2 | fail (trL,trS,vaS <=0) |
| 291 | gates (lim / mkt / pb entries) | pb / AGAINST daily EMA20 side | H1 | 7.5 | +6.10 | -3.15 | -4.94 | -0.46 | 0.6 | -0.5 | fail (trS,vaL,vaS <=0) |
| 292 | gates (lim / mkt / pb entries) | lim / with 5-day trend | H1 | 16.1 | -7.64 | -1.04 | -3.26 | -2.83 | -2.2 | -1.1 | fail (trL,trS,vaL,vaS <=0) |
| 293 | gates (lim / mkt / pb entries) | mkt / with 5-day trend | H1 | 22.3 | -4.19 | -1.40 | -2.20 | -0.30 | -1.7 | -0.7 | fail (trL,trS,vaL,vaS <=0) |
| 294 | gates (lim / mkt / pb entries) | pb / with 5-day trend | H1 | 14.4 | +2.13 | +1.15 | +6.59 | +5.10 | 0.8 | 2.1 | all >0 but weak (<3 se train or <2 se valid) |
| 295 | gates (lim / mkt / pb entries) | lim / AGAINST 5-day trend | H1 | 7.9 | -2.50 | -1.57 | +2.80 | -1.81 | -0.7 | 0.1 | fail (trL,trS,vaS <=0) |
| 296 | gates (lim / mkt / pb entries) | mkt / AGAINST 5-day trend | H1 | 10.5 | -1.06 | -4.23 | +2.07 | -3.55 | -1.0 | -0.3 | fail (trL,trS,vaS <=0) |
| 297 | gates (lim / mkt / pb entries) | pb / AGAINST 5-day trend | H1 | 6.9 | +1.08 | -4.06 | -0.33 | -3.39 | -0.4 | -0.5 | fail (trS,vaL,vaS <=0) |
| 298 | gates (lim / mkt / pb entries) | lim / cmo>=40 | H1 | 16.9 | -7.64 | -1.25 | -0.11 | -2.51 | -2.3 | -0.4 | fail (trL,trS,vaL,vaS <=0) |
| 299 | gates (lim / mkt / pb entries) | mkt / cmo>=40 | H1 | 23.7 | -3.35 | -1.35 | -1.78 | +2.08 | -1.4 | -0.2 | fail (trL,trS,vaL <=0) |
| 300 | gates (lim / mkt / pb entries) | pb / cmo>=40 | H1 | 15.4 | +0.57 | +2.85 | +6.38 | +4.78 | 0.8 | 2.1 | all >0 but weak (<3 se train or <2 se valid) |
| 301 | gates (lim / mkt / pb entries) | lim / body>=70% | H1 | 16.4 | -5.61 | -0.52 | -1.55 | -1.05 | -1.6 | -0.5 | fail (trL,trS,vaL,vaS <=0) |
| 302 | gates (lim / mkt / pb entries) | mkt / body>=70% | H1 | 23.6 | -3.56 | +0.72 | -0.40 | -1.34 | -1.0 | -0.3 | fail (trL,vaL,vaS <=0) |
| 303 | gates (lim / mkt / pb entries) | pb / body>=70% | H1 | 16.3 | +1.58 | +2.11 | +7.17 | +1.48 | 0.9 | 1.8 | all >0 but weak (<3 se train or <2 se valid) |
| 304 | gates (lim / mkt / pb entries) | lim / close<=12% from ext | H1 | 13.4 | -7.05 | -1.35 | -1.14 | -4.21 | -1.9 | -0.7 | fail (trL,trS,vaL,vaS <=0) |
| 305 | gates (lim / mkt / pb entries) | mkt / close<=12% from ext | H1 | 18.7 | -4.40 | -1.72 | -0.18 | +0.41 | -1.7 | 0.0 | fail (trL,trS,vaL <=0) |
| 306 | gates (lim / mkt / pb entries) | pb / close<=12% from ext | H1 | 12.5 | -0.12 | +1.09 | +7.52 | +1.39 | 0.2 | 1.6 | fail (trL <=0) |
| 307 | gates (lim / mkt / pb entries) | lim / range>=1.3ATR | H1 | 13.8 | -6.40 | +1.58 | +2.19 | -1.50 | -1.1 | 0.2 | fail (trL,vaS <=0) |
| 308 | gates (lim / mkt / pb entries) | mkt / range>=1.3ATR | H1 | 20.7 | -2.58 | -0.71 | +0.90 | -1.39 | -0.9 | -0.0 | fail (trL,trS,vaS <=0) |
| 309 | gates (lim / mkt / pb entries) | pb / range>=1.3ATR | H1 | 14.6 | +0.64 | +2.95 | +9.22 | -0.74 | 0.8 | 1.6 | fail (vaS <=0) |
| 310 | gates (lim / mkt / pb entries) | lim / mom>=1.5ATR | H1 | 20.0 | -7.00 | -2.30 | -0.86 | -2.05 | -2.6 | -0.5 | fail (trL,trS,vaL,vaS <=0) |
| 311 | gates (lim / mkt / pb entries) | mkt / mom>=1.5ATR | H1 | 27.9 | -3.73 | -2.04 | -1.94 | +0.65 | -1.9 | -0.5 | fail (trL,trS,vaL <=0) |
| 312 | gates (lim / mkt / pb entries) | pb / mom>=1.5ATR | H1 | 18.3 | +0.58 | +0.42 | +6.34 | +3.19 | 0.3 | 2.0 | all >0 but weak (<3 se train or <2 se valid) |
| 313 | gates (lim / mkt / pb entries) | lim / break>=0.3ATR | H1 | 18.2 | -5.26 | -1.55 | -1.27 | -1.92 | -1.8 | -0.6 | fail (trL,trS,vaL,vaS <=0) |
| 314 | gates (lim / mkt / pb entries) | mkt / break>=0.3ATR | H1 | 26.3 | -2.84 | -3.23 | -0.59 | -1.35 | -1.9 | -0.4 | fail (trL,trS,vaL,vaS <=0) |
| 315 | gates (lim / mkt / pb entries) | pb / break>=0.3ATR | H1 | 18.5 | +1.41 | +0.63 | +5.91 | -1.02 | 0.5 | 1.2 | fail (vaS <=0) |
| 316 | gates (lim / mkt / pb entries) | lim / break<0.1ATR | H1 | 1.6 | -18.25 | +1.44 | -6.28 | -13.27 | -1.2 | -0.9 | fail (trL,vaL,vaS <=0), few trades |
| 317 | gates (lim / mkt / pb entries) | mkt / break<0.1ATR | H1 | 1.8 | -16.76 | +4.57 | -5.06 | -1.05 | -0.9 | -0.5 | fail (trL,vaL,vaS <=0), few trades |
| 318 | gates (lim / mkt / pb entries) | pb / break<0.1ATR | H1 | 0.6 | -15.38 | +10.19 | -14.78 | +33.95 | 0.0 | 0.1 | fail (trL,vaL <=0), few trades |
| 319 | pullback entry variants | pb W5 lvl close stop1.8 | M5 | 203.6 | +0.82 | -0.47 | -0.39 | +0.38 | 0.4 | -0.1 | fail (trS,vaL <=0) |
| 320 | pullback entry variants | pb W3 lvl close stop1.8 | M5 | 177.6 | +0.65 | -0.48 | -0.59 | +0.62 | 0.2 | -0.1 | fail (trS,vaL <=0) |
| 321 | pullback entry variants | pb W8 lvl close stop1.8 | M5 | 209.0 | +0.90 | -0.58 | -0.30 | +0.31 | 0.3 | -0.0 | fail (trS,vaL <=0) |
| 322 | pullback entry variants | pb W5 mid close stop1.8 | M5 | 225.0 | +1.00 | -0.40 | -0.45 | +0.57 | 0.6 | -0.0 | fail (trS,vaL <=0) |
| 323 | pullback entry variants | pb W5 none close stop1.8 | M5 | 319.1 | +0.68 | -0.39 | -0.03 | +0.65 | 0.3 | 0.4 | fail (trS,vaL <=0) |
| 324 | pullback entry variants | pb W5 lvl break stop1.8 | M5 | 108.0 | -0.76 | -0.62 | +0.79 | +3.58 | -0.9 | 1.7 | fail (trL,trS <=0) |
| 325 | pullback entry variants | pb W5 lvl close stopstruct | M5 | 203.6 | +0.25 | -0.92 | -3.33 | -0.82 | -0.5 | -2.8 | fail (trS,vaL,vaS <=0) |
| 326 | pullback entry variants | pb W5 lvl close stop2.5 | M5 | 203.6 | +0.18 | +0.36 | +0.32 | -0.04 | 0.5 | 0.2 | fail (vaS <=0) |
| 327 | pullback entry variants | pb W5 lvl break stopstruct | M5 | 108.0 | -0.78 | -0.93 | -0.66 | +3.30 | -1.1 | 0.8 | fail (trL,trS,vaL <=0) |
| 328 | pullback entry variants | pb W5 lvl close stop1.8 | M15 | 75.8 | +0.62 | +1.10 | +1.01 | +1.93 | 0.9 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 329 | pullback entry variants | pb W3 lvl close stop1.8 | M15 | 67.4 | +0.63 | +1.38 | +0.80 | +1.91 | 1.0 | 0.9 | all >0 but weak (<3 se train or <2 se valid) |
| 330 | pullback entry variants | pb W8 lvl close stop1.8 | M15 | 77.9 | +0.60 | +0.95 | +1.41 | +2.79 | 0.8 | 1.5 | all >0 but weak (<3 se train or <2 se valid) |
| 331 | pullback entry variants | pb W5 mid close stop1.8 | M15 | 82.7 | +0.73 | +0.58 | +1.06 | +1.05 | 0.7 | 0.8 | all >0 but weak (<3 se train or <2 se valid) |
| 332 | pullback entry variants | pb W5 none close stop1.8 | M15 | 115.2 | +0.65 | -0.31 | +0.26 | +1.08 | 0.3 | 0.6 | fail (trS <=0) |
| 333 | pullback entry variants | pb W5 lvl break stop1.8 | M15 | 40.4 | +0.84 | -1.80 | +2.55 | +2.07 | -0.3 | 1.3 | fail (trS <=0) |
| 334 | pullback entry variants | pb W5 lvl close stopstruct | M15 | 75.8 | +2.68 | +0.88 | -1.68 | +3.51 | 1.9 | 0.3 | fail (vaL <=0) |
| 335 | pullback entry variants | pb W5 lvl close stop2.5 | M15 | 75.8 | +1.03 | +0.39 | +2.60 | -0.15 | 0.8 | 1.1 | fail (vaS <=0) |
| 336 | pullback entry variants | pb W5 lvl break stopstruct | M15 | 40.4 | -1.72 | -1.95 | -0.36 | +4.62 | -1.4 | 0.9 | fail (trL,trS,vaL <=0) |
| 337 | pullback entry variants | pb W5 lvl close stop1.8 | H1 | 21.7 | +1.41 | +0.04 | +4.92 | +1.15 | 0.4 | 1.4 | all >0 but weak (<3 se train or <2 se valid) |
| 338 | pullback entry variants | pb W3 lvl close stop1.8 | H1 | 19.5 | +1.56 | +0.66 | +4.34 | +1.21 | 0.6 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 339 | pullback entry variants | pb W8 lvl close stop1.8 | H1 | 22.2 | +1.49 | +0.04 | +4.17 | +1.38 | 0.5 | 1.3 | all >0 but weak (<3 se train or <2 se valid) |
| 340 | pullback entry variants | pb W5 mid close stop1.8 | H1 | 23.7 | +0.66 | +0.29 | +4.54 | +0.57 | 0.3 | 1.3 | all >0 but weak (<3 se train or <2 se valid) |
| 341 | pullback entry variants | pb W5 none close stop1.8 | H1 | 32.6 | +0.40 | +0.32 | +3.22 | +0.68 | 0.3 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 342 | pullback entry variants | pb W5 lvl break stop1.8 | H1 | 10.5 | -4.38 | +0.01 | +7.75 | +12.19 | -1.0 | 2.8 | fail (trL <=0) |
| 343 | pullback entry variants | pb W5 lvl close stopstruct | H1 | 21.7 | +3.83 | -0.17 | -4.65 | +10.71 | 1.1 | 0.6 | fail (trS,vaL <=0) |
| 344 | pullback entry variants | pb W5 lvl close stop2.5 | H1 | 21.7 | +1.05 | +0.25 | +7.66 | +3.51 | 0.4 | 2.5 | all >0 but weak (<3 se train or <2 se valid) |
| 345 | pullback entry variants | pb W5 lvl break stopstruct | H1 | 10.5 | +2.94 | -4.48 | +0.19 | +10.57 | -0.0 | 1.1 | fail (trS <=0) |
| 346 | pullback entry variants | pb W5 lvl close stop1.8 | M1 | 962.4 | -0.72 | -1.52 | +0.49 | +0.34 | -4.2 | 1.2 | fail (trL,trS <=0) |
| 347 | pullback entry variants | pb W3 lvl close stop1.8 | M1 | 835.5 | -0.82 | -1.57 | +0.39 | +0.31 | -4.1 | 0.9 | fail (trL,trS <=0) |
| 348 | pullback entry variants | pb W8 lvl close stop1.8 | M1 | 1002.4 | -0.61 | -1.62 | +0.66 | +0.43 | -4.2 | 1.5 | fail (trL,trS <=0) |
| 349 | pullback entry variants | pb W5 mid close stop1.8 | M1 | 1054.2 | -0.68 | -1.43 | +0.45 | +0.37 | -4.1 | 1.2 | fail (trL,trS <=0) |
| 350 | pullback entry variants | pb W5 none close stop1.8 | M1 | 1510.6 | -0.57 | -0.93 | +0.54 | +0.01 | -3.5 | 1.0 | fail (trL,trS <=0) |
| 351 | pullback entry variants | pb W5 lvl break stop1.8 | M1 | 508.8 | +0.56 | -0.27 | +1.31 | +1.99 | 0.4 | 3.2 | fail (trS <=0) |
| 352 | pullback entry variants | pb W5 lvl close stopstruct | M1 | 962.4 | -7.77 | -7.88 | -7.66 | -8.27 | -29.1 | -21.4 | fail (trL,trS,vaL,vaS <=0) |
| 353 | pullback entry variants | pb W5 lvl close stop2.5 | M1 | 962.4 | -0.71 | -1.28 | +0.72 | +0.18 | -3.7 | 1.3 | fail (trL,trS <=0) |
| 354 | pullback entry variants | pb W5 lvl break stopstruct | M1 | 508.8 | -6.27 | -5.66 | -5.37 | -5.40 | -16.2 | -10.6 | fail (trL,trS,vaL,vaS <=0) |
| 355 | combinations + fades | pb (ref) | M15 | 75.8 | +0.62 | +1.10 | +1.01 | +1.93 | 0.9 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 356 | combinations + fades | pb + 5d trend | M15 | 45.5 | +1.82 | +1.86 | +2.17 | +1.64 | 1.5 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 357 | combinations + fades | pb + 5d trend + week VWAP | M15 | 41.9 | +2.04 | +3.06 | +3.20 | +0.85 | 1.9 | 1.5 | all >0 but weak (<3 se train or <2 se valid) |
| 358 | combinations + fades | pb + month VWAP + 5d trend | M15 | 39.8 | +2.00 | +2.68 | +2.18 | -1.89 | 1.7 | 0.6 | fail (vaS <=0) |
| 359 | combinations + fades | pb + daily EMA20 + 5d trend | M15 | 36.6 | +1.27 | +2.06 | +2.37 | -1.54 | 1.2 | 0.8 | fail (vaS <=0) |
| 360 | combinations + fades | pb + atr/atr100>1.1 | M15 | 25.5 | +3.15 | +1.46 | -1.73 | -1.32 | 1.4 | -0.7 | fail (vaL,vaS <=0) |
| 361 | combinations + fades | pb + atr_vs_h1 high3 | M15 | 27.2 | +2.93 | +0.10 | +0.10 | +1.87 | 1.0 | 0.4 | all >0 but weak (<3 se train or <2 se valid) |
| 362 | combinations + fades | pb + atr_vs_h1 high3 + 5d trend | M15 | 17.9 | +2.83 | -1.64 | +2.18 | +0.48 | 0.4 | 0.6 | fail (trS <=0) |
| 363 | combinations + fades | cmo40 pb + 5d trend | M15 | 33.6 | +0.75 | +1.53 | +2.37 | +1.20 | 0.7 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 364 | combinations + fades | cmo40 pb + 5d trend + week VWAP | M15 | 31.3 | +1.22 | +3.25 | +2.97 | +0.59 | 1.4 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 365 | combinations + fades | cmo40 pb + month VWAP + 5d trend | M15 | 29.6 | +1.34 | +2.83 | +2.36 | -1.30 | 1.3 | 0.7 | fail (vaS <=0) |
| 366 | combinations + fades | cmo40 pb + daily EMA20 + 5d trend | M15 | 27.5 | -0.08 | +2.22 | +2.30 | -0.47 | 0.5 | 0.8 | fail (trL,vaS <=0) |
| 367 | combinations + fades | cmo40 pb + atr/atr100>1.1 | M15 | 20.2 | +2.23 | +1.13 | -4.05 | -2.05 | 0.9 | -1.2 | fail (vaL,vaS <=0) |
| 368 | combinations + fades | cmo40 pb + atr_vs_h1 high3 | M15 | 20.1 | +3.33 | -0.39 | -1.17 | +1.44 | 0.9 | 0.0 | fail (trS,vaL <=0) |
| 369 | combinations + fades | cmo40 pb + atr_vs_h1 high3 + 5d trend | M15 | 12.9 | +3.59 | -0.84 | +1.46 | +0.85 | 0.7 | 0.4 | fail (trS <=0) |
| 370 | combinations + fades | FADE all | M15 | 117.6 | +2.63 | +0.89 | -2.35 | +0.31 | 2.2 | -0.7 | fail (vaL <=0) |
| 371 | combinations + fades | FADE NY 07-10 | M15 | 21.7 | -1.24 | +1.93 | -1.07 | -0.85 | 0.3 | -0.4 | fail (trL,vaL,vaS <=0) |
| 372 | combinations + fades | FADE NY 14-17 | M15 | 6.1 | +1.06 | -1.65 | +2.60 | -5.60 | -0.1 | -0.6 | fail (trS,vaS <=0), few trades |
| 373 | combinations + fades | FADE outside NY 07-17 | M15 | 75.1 | +2.96 | +1.23 | -3.79 | +1.21 | 2.1 | -0.6 | fail (vaL <=0) |
| 374 | combinations + fades | FADE longs-sig NY07-10 + shorts-sig NY14-17 | M15 | 14.9 | +1.06 | +1.93 | +2.60 | -0.85 | 0.8 | -0.1 | fail (vaS <=0) |
| 375 | combinations + fades | pb (ref) | H1 | 21.7 | +1.41 | +0.04 | +4.92 | +1.15 | 0.4 | 1.4 | all >0 but weak (<3 se train or <2 se valid) |
| 376 | combinations + fades | pb + 5d trend | H1 | 14.7 | +2.17 | +1.28 | +6.22 | +5.18 | 0.8 | 2.0 | all >0 but weak (<3 se train or <2 se valid) |
| 377 | combinations + fades | pb + 5d trend + week VWAP | H1 | 14.1 | +2.37 | +1.95 | +6.09 | +4.45 | 1.0 | 1.9 | all >0 but weak (<3 se train or <2 se valid) |
| 378 | combinations + fades | pb + month VWAP + 5d trend | H1 | 13.2 | +1.83 | +3.16 | +6.01 | +0.72 | 1.1 | 1.5 | all >0 but weak (<3 se train or <2 se valid) |
| 379 | combinations + fades | pb + daily EMA20 + 5d trend | H1 | 12.0 | +0.29 | +1.76 | +7.35 | +2.70 | 0.4 | 2.0 | all >0 but weak (<3 se train or <2 se valid) |
| 380 | combinations + fades | pb + atr/atr100>1.1 | H1 | 7.8 | +10.58 | -0.96 | +9.46 | -3.04 | 1.6 | 0.7 | fail (trS,vaS <=0) |
| 381 | combinations + fades | cmo40 pb + 5d trend | H1 | 10.7 | +0.29 | +4.29 | +6.84 | +9.71 | 0.9 | 2.3 | all >0 but weak (<3 se train or <2 se valid) |
| 382 | combinations + fades | cmo40 pb + 5d trend + week VWAP | H1 | 10.5 | +0.48 | +4.46 | +6.95 | +8.95 | 0.9 | 2.2 | all >0 but weak (<3 se train or <2 se valid) |
| 383 | combinations + fades | cmo40 pb + month VWAP + 5d trend | H1 | 9.7 | +0.26 | +6.21 | +6.05 | +7.53 | 1.2 | 1.8 | all >0 but weak (<3 se train or <2 se valid) |
| 384 | combinations + fades | cmo40 pb + daily EMA20 + 5d trend | H1 | 8.8 | -2.07 | +5.60 | +7.82 | +8.95 | 0.5 | 2.3 | fail (trL <=0) |
| 385 | combinations + fades | cmo40 pb + atr/atr100>1.1 | H1 | 5.8 | +11.69 | +1.38 | +5.07 | -2.55 | 1.9 | 0.3 | fail (vaS <=0) |
| 386 | combinations + fades | FADE all | H1 | 33.2 | +2.12 | +3.43 | +1.43 | +1.86 | 2.0 | 0.9 | all >0 but weak (<3 se train or <2 se valid) |
| 387 | combinations + fades | FADE NY 07-10 | H1 | 8.2 | +0.31 | +1.20 | -0.16 | +6.01 | 0.3 | 0.8 | fail (vaL <=0) |
| 388 | combinations + fades | FADE NY 14-17 | H1 | 1.7 | +15.61 | +5.99 | -0.72 | +13.95 | 1.6 | 1.1 | fail (vaL <=0), few trades |
| 389 | combinations + fades | FADE outside NY 07-17 | H1 | 17.3 | +1.88 | +6.08 | -3.39 | +0.76 | 2.1 | -0.3 | fail (vaL <=0) |
| 390 | combinations + fades | FADE longs-sig NY07-10 + shorts-sig NY14-17 | H1 | 5.2 | +15.61 | +1.20 | -0.72 | +6.01 | 0.9 | 1.0 | fail (vaL <=0) |
| 391 | combinations + fades | pb (ref) | M5 | 203.6 | +0.82 | -0.47 | -0.39 | +0.38 | 0.4 | -0.1 | fail (trS,vaL <=0) |
| 392 | combinations + fades | pb + 5d trend | M5 | 117.9 | +1.54 | -0.51 | -0.53 | -0.46 | 0.8 | -0.5 | fail (trS,vaL,vaS <=0) |
| 393 | combinations + fades | pb + 5d trend + week VWAP | M5 | 106.6 | +1.52 | -0.64 | -0.55 | +0.29 | 0.7 | -0.2 | fail (trS,vaL <=0) |
| 394 | combinations + fades | pb + month VWAP + 5d trend | M5 | 102.4 | +1.42 | -0.38 | -0.89 | -0.75 | 0.7 | -0.8 | fail (trS,vaL,vaS <=0) |
| 395 | combinations + fades | pb + daily EMA20 + 5d trend | M5 | 93.6 | +1.36 | -0.32 | -0.44 | -1.51 | 0.7 | -0.6 | fail (trS,vaL,vaS <=0) |
| 396 | combinations + fades | pb + atr/atr100>1.1 | M5 | 72.3 | +3.21 | -0.30 | +0.61 | +1.05 | 1.5 | 0.6 | fail (trS <=0) |
| 397 | combinations + fades | pb + atr_vs_h1 high3 | M5 | 73.5 | +2.88 | +0.09 | +0.16 | +1.62 | 1.6 | 0.6 | all >0 but weak (<3 se train or <2 se valid) |
| 398 | combinations + fades | pb + atr_vs_h1 high3 + 5d trend | M5 | 46.7 | +2.36 | +0.60 | -0.46 | -0.04 | 1.3 | -0.2 | fail (vaL,vaS <=0) |
| 399 | combinations + fades | cmo40 pb + 5d trend | M5 | 85.2 | +2.32 | -0.12 | -0.48 | -0.22 | 1.3 | -0.3 | fail (trS,vaL,vaS <=0) |
| 400 | combinations + fades | cmo40 pb + 5d trend + week VWAP | M5 | 77.7 | +2.31 | -0.13 | -0.27 | +0.84 | 1.3 | 0.1 | fail (trS,vaL <=0) |
| 401 | combinations + fades | cmo40 pb + month VWAP + 5d trend | M5 | 74.3 | +2.47 | +0.08 | -0.54 | -0.32 | 1.4 | -0.4 | fail (vaL,vaS <=0) |
| 402 | combinations + fades | cmo40 pb + daily EMA20 + 5d trend | M5 | 67.7 | +2.42 | +0.43 | -0.31 | -1.87 | 1.5 | -0.6 | fail (vaL,vaS <=0) |
| 403 | combinations + fades | cmo40 pb + atr/atr100>1.1 | M5 | 54.2 | +4.04 | -0.42 | +1.50 | +2.73 | 1.7 | 1.4 | fail (trS <=0) |
| 404 | combinations + fades | cmo40 pb + atr_vs_h1 high3 | M5 | 53.1 | +4.34 | +0.36 | +0.73 | +2.46 | 2.1 | 1.0 | all >0 but weak (<3 se train or <2 se valid) |
| 405 | combinations + fades | cmo40 pb + atr_vs_h1 high3 + 5d trend | M5 | 34.4 | +4.33 | +0.96 | +0.03 | -0.08 | 2.0 | -0.0 | fail (vaS <=0) |
| 406 | combinations + fades | FADE all | M5 | 324.9 | +2.82 | +1.00 | -0.54 | +0.30 | 4.1 | -0.1 | fail (vaL <=0) |
| 407 | combinations + fades | FADE NY 07-10 | M5 | 49.0 | +3.71 | +1.59 | -4.79 | +3.14 | 2.2 | -0.1 | fail (vaL <=0) |
| 408 | combinations + fades | FADE NY 14-17 | M5 | 28.6 | +7.98 | +5.77 | +9.88 | -0.42 | 4.5 | 1.8 | fail (vaS <=0) |
| 409 | combinations + fades | FADE outside NY 07-17 | M5 | 204.3 | +2.04 | +0.66 | -2.05 | -0.79 | 2.3 | -1.6 | fail (vaL,vaS <=0) |
| 410 | combinations + fades | FADE longs-sig NY07-10 + shorts-sig NY14-17 | M5 | 40.5 | +7.98 | +1.59 | +9.88 | +3.14 | 3.0 | 2.8 | **all >0, train >=3 se, valid >=2 se** |
| 411 | combinations + fades | pb (ref) | M1 | 962.4 | -0.72 | -1.52 | +0.49 | +0.34 | -4.2 | 1.2 | fail (trL,trS <=0) |
| 412 | combinations + fades | pb + 5d trend | M1 | 549.2 | -0.79 | -0.64 | +0.84 | -0.09 | -2.0 | 1.1 | fail (trL,trS,vaS <=0) |
| 413 | combinations + fades | pb + 5d trend + week VWAP | M1 | 494.4 | -0.97 | -0.46 | +0.74 | +0.03 | -1.9 | 1.0 | fail (trL,trS <=0) |
| 414 | combinations + fades | pb + month VWAP + 5d trend | M1 | 477.2 | -0.72 | -0.54 | +0.99 | -0.07 | -1.7 | 1.3 | fail (trL,trS,vaS <=0) |
| 415 | combinations + fades | pb + daily EMA20 + 5d trend | M1 | 434.2 | -0.46 | -0.59 | +1.02 | +0.42 | -1.3 | 1.6 | fail (trL,trS <=0) |
| 416 | combinations + fades | pb + atr/atr100>1.1 | M1 | 358.4 | +0.03 | -2.21 | +1.20 | +1.48 | -2.4 | 2.2 | fail (trS <=0) |
| 417 | combinations + fades | pb + atr_vs_h1 high3 | M1 | 343.0 | +0.60 | -1.35 | +0.10 | +1.13 | -0.9 | 1.0 | fail (trS <=0) |
| 418 | combinations + fades | pb + atr_vs_h1 high3 + 5d trend | M1 | 206.1 | +0.65 | -0.85 | +0.41 | +0.96 | -0.1 | 0.8 | fail (trS <=0) |
| 419 | combinations + fades | cmo40 pb + 5d trend | M1 | 388.2 | -0.87 | -0.58 | +0.88 | -0.61 | -1.7 | 0.6 | fail (trL,trS,vaS <=0) |
| 420 | combinations + fades | cmo40 pb + 5d trend + week VWAP | M1 | 349.5 | -1.01 | -0.41 | +0.77 | -0.17 | -1.6 | 0.8 | fail (trL,trS,vaS <=0) |
| 421 | combinations + fades | cmo40 pb + month VWAP + 5d trend | M1 | 337.8 | -0.84 | -0.57 | +0.84 | -0.37 | -1.6 | 0.7 | fail (trL,trS,vaS <=0) |
| 422 | combinations + fades | cmo40 pb + daily EMA20 + 5d trend | M1 | 307.2 | -0.54 | -0.33 | +0.97 | +0.15 | -0.9 | 1.2 | fail (trL,trS <=0) |
| 423 | combinations + fades | cmo40 pb + atr/atr100>1.1 | M1 | 261.4 | -0.61 | -2.40 | +1.88 | +0.63 | -2.9 | 1.8 | fail (trL,trS <=0) |
| 424 | combinations + fades | cmo40 pb + atr_vs_h1 high3 | M1 | 243.6 | +0.52 | -1.34 | +0.38 | +0.32 | -0.8 | 0.5 | fail (trS <=0) |
| 425 | combinations + fades | cmo40 pb + atr_vs_h1 high3 + 5d trend | M1 | 148.0 | +0.74 | -0.43 | +0.35 | -0.19 | 0.2 | 0.2 | fail (trS,vaS <=0) |
| 426 | combinations + fades | FADE all | M1 | 1556.1 | +1.78 | +1.48 | +0.70 | +0.62 | 7.7 | 2.3 | **all >0, train >=3 se, valid >=2 se** |
| 427 | combinations + fades | FADE NY 07-10 | M1 | 203.4 | +1.89 | +1.36 | -1.50 | +2.41 | 2.8 | 0.8 | fail (vaL <=0) |
| 428 | combinations + fades | FADE NY 14-17 | M1 | 175.7 | +1.45 | +3.08 | +1.79 | +0.42 | 3.5 | 1.2 | all >0 but weak (<3 se train or <2 se valid) |
| 429 | combinations + fades | FADE outside NY 07-17 | M1 | 931.6 | +1.98 | +1.14 | +0.52 | -0.25 | 5.7 | 0.2 | fail (vaS <=0) |
| 430 | combinations + fades | FADE longs-sig NY07-10 + shorts-sig NY14-17 | M1 | 195.2 | +1.45 | +1.36 | +1.79 | +2.41 | 2.3 | 2.6 | all >0 but weak (<3 se train or <2 se valid) |
| 431 | fade by 3h NY block | FADE NY 00-03 | M5 | 49.1 | +2.89 | -0.02 | -4.49 | -0.30 | 1.2 | -1.2 | fail (trS,vaL,vaS <=0) |
| 432 | fade by 3h NY block | FADE NY 03-06 | M5 | 42.2 | +2.89 | +2.98 | -3.57 | -1.78 | 2.3 | -1.4 | fail (vaL,vaS <=0) |
| 433 | fade by 3h NY block | FADE NY 06-09 | M5 | 47.2 | +3.49 | +4.66 | -5.88 | +2.07 | 3.4 | -0.7 | fail (vaL <=0) |
| 434 | fade by 3h NY block | FADE NY 09-12 | M5 | 39.3 | +1.72 | -4.72 | -0.93 | +0.98 | -1.1 | 0.1 | fail (trS,vaL <=0) |
| 435 | fade by 3h NY block | FADE NY 12-15 | M5 | 29.7 | +4.00 | +3.58 | +5.32 | +4.68 | 2.5 | 2.2 | all >0 but weak (<3 se train or <2 se valid) |
| 436 | fade by 3h NY block | FADE NY 15-18 | M5 | 18.4 | +8.83 | +5.51 | +15.32 | +0.75 | 3.7 | 2.6 | all >0 but too few trades |
| 437 | fade by 3h NY block | FADE NY 18-21 | M5 | 48.7 | +3.36 | -1.03 | +3.47 | +0.71 | 0.8 | 1.1 | fail (trS <=0) |
| 438 | fade by 3h NY block | FADE NY 21-24 | M5 | 50.4 | -0.70 | +0.26 | -2.63 | -2.53 | -0.2 | -1.5 | fail (trL,vaL,vaS <=0) |
| 439 | fade by 3h NY block | FADE NY 00-03 | M15 | 19.1 | +3.15 | +0.83 | -1.62 | -1.01 | 1.0 | -0.5 | fail (vaL,vaS <=0) |
| 440 | fade by 3h NY block | FADE NY 03-06 | M15 | 17.0 | +1.62 | +3.13 | -5.64 | +4.08 | 1.2 | 0.0 | fail (vaL <=0) |
| 441 | fade by 3h NY block | FADE NY 06-09 | M15 | 19.9 | -1.17 | +5.17 | -6.85 | +0.16 | 1.2 | -1.0 | fail (trL,vaL <=0) |
| 442 | fade by 3h NY block | FADE NY 09-12 | M15 | 16.7 | +3.44 | -3.62 | +1.32 | -1.29 | -0.1 | -0.0 | fail (trS,vaS <=0) |
| 443 | fade by 3h NY block | FADE NY 12-15 | M15 | 8.0 | +6.12 | -2.40 | +2.84 | +3.05 | 0.7 | 0.7 | fail (trS <=0) |
| 444 | fade by 3h NY block | FADE NY 15-18 | M15 | 3.4 | -3.16 | -1.52 | +3.85 | -7.91 | -0.5 | -0.8 | fail (trL,trS,vaS <=0), few trades |
| 445 | fade by 3h NY block | FADE NY 18-21 | M15 | 13.3 | +4.63 | -0.42 | +2.48 | +4.94 | 0.8 | 1.3 | fail (trS <=0) |
| 446 | fade by 3h NY block | FADE NY 21-24 | M15 | 20.1 | +4.22 | +1.05 | -5.91 | -2.71 | 1.4 | -1.6 | fail (vaL,vaS <=0) |
| 447 | fade by 3h NY block | FADE NY 00-03 | H1 | 4.9 | +3.42 | +1.78 | -5.75 | -3.15 | 0.7 | -0.8 | fail (vaL,vaS <=0) |
| 448 | fade by 3h NY block | FADE NY 03-06 | H1 | 4.9 | -1.76 | +8.28 | +2.51 | +4.85 | 0.8 | 0.8 | fail (trL <=0) |
| 449 | fade by 3h NY block | FADE NY 06-09 | H1 | 6.4 | -3.74 | +6.83 | -4.32 | +7.89 | 0.5 | 0.6 | fail (trL,vaL <=0) |
| 450 | fade by 3h NY block | FADE NY 09-12 | H1 | 7.3 | +4.52 | -2.45 | +14.08 | -4.80 | 0.2 | 0.7 | fail (trS,vaS <=0) |
| 451 | fade by 3h NY block | FADE NY 12-15 | H1 | 2.9 | -0.28 | -3.41 | +9.56 | +10.61 | -0.4 | 1.4 | fail (trL,trS <=0), few trades |
| 452 | fade by 3h NY block | FADE NY 15-18 | H1 | 0.9 | +18.13 | +14.82 | +3.27 | +5.38 | 1.9 | 0.4 | all >0 but too few trades |
| 453 | fade by 3h NY block | FADE NY 18-21 | H1 | 1.8 | -14.98 | +14.10 | -16.17 | +3.11 | 0.7 | -0.2 | fail (trL,vaL <=0), few trades |
| 454 | fade by 3h NY block | FADE NY 21-24 | H1 | 4.2 | +15.05 | +3.05 | -5.41 | -0.31 | 2.0 | -0.4 | fail (vaL,vaS <=0) |
| 455 | fade by 3h NY block | FADE NY 00-03 | M1 | 218.9 | +1.66 | +0.52 | -1.04 | -1.69 | 1.9 | -1.8 | fail (vaL,vaS <=0) |
| 456 | fade by 3h NY block | FADE NY 03-06 | M1 | 197.4 | +1.53 | +1.91 | -0.90 | +0.81 | 2.9 | 0.1 | fail (vaL <=0) |
| 457 | fade by 3h NY block | FADE NY 06-09 | M1 | 206.1 | +1.60 | +2.84 | -0.12 | +0.67 | 3.8 | 0.4 | fail (vaL <=0) |
| 458 | fade by 3h NY block | FADE NY 09-12 | M1 | 186.4 | +1.25 | +0.23 | -0.24 | +3.18 | 1.2 | 1.9 | fail (vaL <=0) |
| 459 | fade by 3h NY block | FADE NY 12-15 | M1 | 183.7 | +0.76 | +3.04 | +2.96 | +2.85 | 3.0 | 3.4 | all >0 but weak (<3 se train or <2 se valid) |
| 460 | fade by 3h NY block | FADE NY 15-18 | M1 | 116.5 | +2.44 | +2.94 | +2.43 | -1.23 | 3.5 | 0.4 | fail (vaS <=0) |
| 461 | fade by 3h NY block | FADE NY 18-21 | M1 | 228.3 | +5.54 | +1.16 | +4.84 | -0.04 | 5.8 | 2.8 | fail (vaS <=0) |
| 462 | fade by 3h NY block | FADE NY 21-24 | M1 | 218.9 | -0.45 | +0.31 | -1.71 | +0.30 | -0.1 | -0.8 | fail (trL,vaL <=0) |
| 463 | NY-afternoon fade variants | FADE NY 12-18 (incl. pre-break bar) mkt 1.8 | M5 | 48.1 | +5.87 | +4.30 | +9.47 | +2.95 | 4.3 | 3.4 | **all >0, train >=3 se, valid >=2 se** |
| 464 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.8 | M5 | 46.9 | +4.98 | +4.02 | +9.18 | +2.48 | 3.7 | 3.1 | **all >0, train >=3 se, valid >=2 se** |
| 465 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.2 | M5 | 46.9 | +4.29 | +3.99 | +8.16 | +4.14 | 3.4 | 3.4 | **all >0, train >=3 se, valid >=2 se** |
| 466 | NY-afternoon fade variants | FADE NY 12-18 mkt 2.5 | M5 | 46.9 | +4.66 | +3.44 | +13.11 | +0.99 | 3.3 | 3.7 | **all >0, train >=3 se, valid >=2 se** |
| 467 | NY-afternoon fade variants | FADE NY 12-18 mkt stop sig-ext+0.3 | M5 | 46.9 | +2.93 | +2.52 | +3.42 | +7.51 | 2.2 | 3.3 | all >0 but weak (<3 se train or <2 se valid) |
| 468 | NY-afternoon fade variants | FADE NY 12-18 stop-entry @retest lvl | M5 | 35.8 | +4.92 | +3.08 | +10.17 | -0.15 | 2.9 | 2.3 | fail (vaS <=0) |
| 469 | NY-afternoon fade variants | FADE NY 12-18 limit +0.3ATR W3 | M5 | 32.1 | +2.83 | +2.13 | +8.37 | +0.48 | 1.7 | 1.9 | all >0 but weak (<3 se train or <2 se valid) |
| 470 | NY-afternoon fade variants | FADE NY 12-18 after counter bar | M5 | 25.6 | +4.39 | +1.41 | +9.79 | -0.13 | 1.8 | 2.0 | fail (vaS <=0) |
| 471 | NY-afternoon fade variants | FADE NY 12-18 cmo40 | M5 | 32.5 | +5.01 | +2.51 | +9.35 | +4.57 | 2.6 | 3.3 | all >0 but weak (<3 se train or <2 se valid) |
| 472 | NY-afternoon fade variants | FADE NY 12-18 range>=1.2ATR | M5 | 21.0 | +6.59 | +4.55 | +9.24 | +3.80 | 3.1 | 2.5 | **all >0, train >=3 se, valid >=2 se** |
| 473 | NY-afternoon fade variants | FADE NY 12-15 mkt 1.8 | M5 | 29.7 | +4.00 | +3.58 | +5.32 | +4.68 | 2.5 | 2.2 | all >0 but weak (<3 se train or <2 se valid) |
| 474 | NY-afternoon fade variants | FADE NY 15-18 mkt 1.8 | M5 | 17.2 | +6.65 | +4.79 | +14.81 | -0.51 | 2.9 | 2.3 | fail (vaS <=0), few trades |
| 475 | NY-afternoon fade variants | FADE NY 13-17 mkt 1.8 | M5 | 38.5 | +5.95 | +4.23 | +8.41 | +0.41 | 3.8 | 2.0 | **all >0, train >=3 se, valid >=2 se** |
| 476 | NY-afternoon fade variants | FADE NY 11-18 mkt 1.8 | M5 | 57.3 | +4.00 | +2.16 | +7.92 | +2.06 | 2.8 | 3.0 | all >0 but weak (<3 se train or <2 se valid) |
| 477 | NY-afternoon fade variants | FADE NY 12-21 mkt 1.8 | M5 | 95.5 | +4.21 | +1.29 | +6.35 | +1.56 | 3.2 | 3.0 | **all >0, train >=3 se, valid >=2 se** |
| 478 | NY-afternoon fade variants | FADE NY 12-18 (incl. pre-break bar) mkt 1.8 | M1 | 300.2 | +1.40 | +3.00 | +2.75 | +1.23 | 4.5 | 2.9 | **all >0, train >=3 se, valid >=2 se** |
| 479 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.8 | M1 | 298.8 | +1.25 | +2.97 | +2.68 | +1.02 | 4.3 | 2.6 | **all >0, train >=3 se, valid >=2 se** |
| 480 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.2 | M1 | 298.8 | +1.49 | +2.50 | +1.49 | +1.08 | 4.1 | 1.9 | all >0 but weak (<3 se train or <2 se valid) |
| 481 | NY-afternoon fade variants | FADE NY 12-18 mkt 2.5 | M1 | 298.8 | +1.28 | +3.49 | +3.66 | +0.24 | 4.8 | 2.7 | **all >0, train >=3 se, valid >=2 se** |
| 482 | NY-afternoon fade variants | FADE NY 12-18 mkt stop sig-ext+0.3 | M1 | 298.8 | -4.64 | -4.11 | -6.14 | -5.59 | -9.1 | -8.7 | fail (trL,trS,vaL,vaS <=0) |
| 483 | NY-afternoon fade variants | FADE NY 12-18 stop-entry @retest lvl | M1 | 229.4 | +0.27 | +1.84 | +4.21 | +1.51 | 1.8 | 3.5 | all >0 but weak (<3 se train or <2 se valid) |
| 484 | NY-afternoon fade variants | FADE NY 12-18 limit +0.3ATR W3 | M1 | 214.6 | -1.00 | +0.95 | +0.59 | -1.55 | -0.1 | -0.7 | fail (trL,vaS <=0) |
| 485 | NY-afternoon fade variants | FADE NY 12-18 after counter bar | M1 | 154.8 | -0.53 | +0.48 | +1.77 | +2.02 | -0.1 | 2.0 | fail (trL <=0) |
| 486 | NY-afternoon fade variants | FADE NY 12-18 cmo40 | M1 | 199.8 | +0.75 | +3.21 | +1.83 | +0.41 | 3.2 | 1.3 | all >0 but weak (<3 se train or <2 se valid) |
| 487 | NY-afternoon fade variants | FADE NY 12-18 range>=1.2ATR | M1 | 181.9 | +2.99 | +2.55 | +2.41 | +1.85 | 4.5 | 2.5 | **all >0, train >=3 se, valid >=2 se** |
| 488 | NY-afternoon fade variants | FADE NY 12-15 mkt 1.8 | M1 | 183.7 | +0.76 | +3.04 | +2.96 | +2.85 | 3.0 | 3.4 | all >0 but weak (<3 se train or <2 se valid) |
| 489 | NY-afternoon fade variants | FADE NY 15-18 mkt 1.8 | M1 | 115.1 | +2.05 | +2.85 | +2.22 | -1.81 | 3.1 | -0.0 | fail (vaS <=0) |
| 490 | NY-afternoon fade variants | FADE NY 13-17 mkt 1.8 | M1 | 237.7 | +1.45 | +3.36 | +2.72 | +1.36 | 4.4 | 2.6 | **all >0, train >=3 se, valid >=2 se** |
| 491 | NY-afternoon fade variants | FADE NY 11-18 mkt 1.8 | M1 | 360.5 | +1.20 | +2.69 | +2.21 | +1.79 | 4.4 | 3.3 | **all >0, train >=3 se, valid >=2 se** |
| 492 | NY-afternoon fade variants | FADE NY 12-21 mkt 1.8 | M1 | 527.1 | +2.98 | +2.13 | +3.60 | +0.55 | 7.1 | 3.8 | **all >0, train >=3 se, valid >=2 se** |
| 493 | NY-afternoon fade variants | FADE NY 12-18 (incl. pre-break bar) mkt 1.8 | M15 | 11.4 | +3.66 | -2.11 | +3.14 | -1.43 | 0.3 | 0.1 | fail (trS,vaS <=0) |
| 494 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.8 | M15 | 10.9 | +4.16 | -2.27 | +3.22 | -1.74 | 0.4 | 0.1 | fail (trS,vaS <=0) |
| 495 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.2 | M15 | 10.9 | +3.79 | -2.02 | +7.96 | +2.80 | 0.4 | 1.5 | fail (trS <=0) |
| 496 | NY-afternoon fade variants | FADE NY 12-18 mkt 2.5 | M15 | 10.9 | +4.67 | -6.12 | +8.22 | -3.49 | -0.3 | 0.4 | fail (trS,vaS <=0) |
| 497 | NY-afternoon fade variants | FADE NY 12-18 mkt stop sig-ext+0.3 | M15 | 10.9 | +8.08 | +2.21 | +0.33 | +9.10 | 2.0 | 1.7 | all >0 but weak (<3 se train or <2 se valid) |
| 498 | NY-afternoon fade variants | FADE NY 12-18 stop-entry @retest lvl | M15 | 8.1 | +1.15 | -3.21 | +7.87 | -2.59 | -0.3 | 0.4 | fail (trS,vaS <=0) |
| 499 | NY-afternoon fade variants | FADE NY 12-18 limit +0.3ATR W3 | M15 | 7.1 | +4.78 | -6.14 | +2.76 | +0.23 | -0.2 | 0.3 | fail (trS <=0), few trades |
| 500 | NY-afternoon fade variants | FADE NY 12-18 after counter bar | M15 | 6.0 | -1.21 | -3.59 | +6.35 | -7.02 | -0.7 | -0.4 | fail (trL,trS,vaS <=0), few trades |
| 501 | NY-afternoon fade variants | FADE NY 12-18 cmo40 | M15 | 8.8 | +6.51 | +0.62 | +1.62 | -3.29 | 1.3 | -0.3 | fail (vaS <=0) |
| 502 | NY-afternoon fade variants | FADE NY 12-18 range>=1.2ATR | M15 | 4.4 | +6.08 | -4.01 | +1.54 | +1.14 | 0.4 | 0.3 | fail (trS <=0), few trades |
| 503 | NY-afternoon fade variants | FADE NY 12-15 mkt 1.8 | M15 | 8.0 | +6.12 | -2.40 | +2.84 | +3.05 | 0.7 | 0.7 | fail (trS <=0) |
| 504 | NY-afternoon fade variants | FADE NY 15-18 mkt 1.8 | M15 | 2.9 | -1.94 | -1.98 | +4.17 | -10.13 | -0.4 | -0.9 | fail (trL,trS,vaS <=0), few trades |
| 505 | NY-afternoon fade variants | FADE NY 13-17 mkt 1.8 | M15 | 8.2 | +5.32 | -3.13 | +1.35 | -5.84 | 0.4 | -0.7 | fail (trS,vaS <=0) |
| 506 | NY-afternoon fade variants | FADE NY 11-18 mkt 1.8 | M15 | 14.7 | +5.59 | -2.01 | +5.64 | -1.25 | 0.8 | 0.6 | fail (trS,vaS <=0) |
| 507 | NY-afternoon fade variants | FADE NY 12-21 mkt 1.8 | M15 | 24.2 | +4.40 | -1.19 | +2.87 | +1.87 | 0.8 | 1.0 | fail (trS <=0) |
| 508 | NY-afternoon fade variants | FADE NY 12-18 (incl. pre-break bar) mkt 1.8 | H1 | 3.8 | +4.47 | +0.72 | +7.54 | +8.95 | 0.6 | 1.4 | all >0 but weak (<3 se train or <2 se valid) |
| 509 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.8 | H1 | 3.7 | +4.47 | -1.95 | +6.05 | +8.95 | 0.2 | 1.3 | fail (trS <=0) |
| 510 | NY-afternoon fade variants | FADE NY 12-18 mkt 1.2 | H1 | 3.7 | +9.31 | +0.55 | +5.13 | +7.70 | 1.1 | 1.1 | all >0 but weak (<3 se train or <2 se valid) |
| 511 | NY-afternoon fade variants | FADE NY 12-18 mkt 2.5 | H1 | 3.7 | +3.26 | -3.02 | +5.13 | +9.57 | -0.0 | 1.3 | fail (trS <=0) |
| 512 | NY-afternoon fade variants | FADE NY 12-18 mkt stop sig-ext+0.3 | H1 | 3.7 | +3.67 | +4.48 | -2.28 | +2.70 | 0.9 | 0.1 | fail (vaL <=0) |
| 513 | NY-afternoon fade variants | FADE NY 12-18 stop-entry @retest lvl | H1 | 2.2 | +11.57 | +7.93 | +1.67 | +12.65 | 1.8 | 1.1 | all >0 but too few trades |
| 514 | NY-afternoon fade variants | FADE NY 12-18 limit +0.3ATR W3 | H1 | 2.4 | +1.50 | -1.54 | +13.97 | +5.38 | -0.0 | 1.2 | fail (trS <=0), few trades |
| 515 | NY-afternoon fade variants | FADE NY 12-18 after counter bar | H1 | 1.9 | +0.28 | -6.41 | +10.22 | +11.45 | -0.5 | 1.3 | fail (trS <=0), few trades |
| 516 | NY-afternoon fade variants | FADE NY 12-18 cmo40 | H1 | 2.8 | +2.93 | -4.68 | -0.89 | +7.28 | -0.3 | 0.6 | fail (trS,vaL <=0), few trades |
| 517 | NY-afternoon fade variants | FADE NY 12-18 range>=1.2ATR | H1 | 1.9 | -1.23 | -7.08 | +6.05 | -9.39 | -0.7 | -0.2 | fail (trL,trS,vaS <=0), few trades |
| 518 | NY-afternoon fade variants | FADE NY 12-15 mkt 1.8 | H1 | 2.9 | -0.28 | -3.41 | +9.56 | +10.61 | -0.4 | 1.4 | fail (trL,trS <=0), few trades |
| 519 | NY-afternoon fade variants | FADE NY 15-18 mkt 1.8 | H1 | 0.8 | +18.13 | +5.13 | -2.28 | +3.95 | 1.3 | 0.1 | fail (vaL <=0), few trades |
| 520 | NY-afternoon fade variants | FADE NY 13-17 mkt 1.8 | H1 | 2.5 | +7.04 | -2.16 | +5.22 | +14.50 | 0.4 | 1.4 | fail (trS <=0), few trades |
| 521 | NY-afternoon fade variants | FADE NY 11-18 mkt 1.8 | H1 | 5.1 | +7.01 | -0.99 | +11.53 | +0.76 | 0.7 | 1.0 | fail (trS <=0) |
| 522 | NY-afternoon fade variants | FADE NY 12-21 mkt 1.8 | H1 | 5.4 | -0.45 | +4.16 | +0.50 | +6.45 | 0.6 | 0.9 | fail (trL <=0) |
