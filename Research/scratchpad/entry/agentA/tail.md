
## (2) Best candidates in full detail

### A. New York 09:30 opening-range breakout with stop entries (M15 primary, M5 the same orders with M5 ATR)
**Rule (decided at the close of the 09:45 NY M15 bar = 10:00 New York local time, Mon-Fri):**
- ORH / ORL = high / low of the bars from 09:30 to 10:00 NY (M15: the 09:30 and 09:45 bars; M5: six bars).
- At 10:00, place a buy stop at ORH + 0.05·ATR14 and a sell stop at ORL − 0.05·ATR14 (ATR14 = RMA ATR of the chart timeframe at the 09:45 bar).
  Both orders stay valid until 13:00 NY (12 M15 bars) and are then cancelled.
- Stop = entry ∓ 1.8·ATR14. TP1-TP4 = 0.6 / 1 / 1.5 / 2 R.
- Kit version: both orders run independently, so on a whipsaw day both can fill. OCO version: the first fill cancels the other order (numbers below).
- Fill rate is about 60% per order. Median fill is 1 bar after 10:00.

| M15, both orders independent | n | /mo | hit TP1 | TP2 | TP3 | TP4 | excess TP1..TP4 | avg excess | E@TP1..TP4 after spread (R) |
|---|---|---|---|---|---|---|---|---|---|
| train long  | 455 | 12.6 | 64.4 | 51.6 | 41.1 | 34.7 | +1.8 +1.9 +1.5 +1.7 | **+1.75** | −0.015 −0.013 −0.018 −0.004 |
| train short | 453 | 12.6 | 68.2 | 55.4 | 44.2 | 35.8 | +5.7 +5.3 +4.4 +2.6 | **+4.51** | +0.045 +0.062 +0.058 +0.027 |
| valid long  | 256 | 14.2 | 68.0 | 57.8 | 48.4 | 43.4 | +2.2 +3.9 +4.2 +5.4 | **+3.93** | +0.073 +0.141 +0.196 +0.286 |
| valid short | 238 | 13.2 | 64.7 | 50.4 | 37.4 | 31.1 | +5.9 +4.4 +1.1 +0.8 | **+3.08** | +0.020 −0.007 −0.080 −0.082 |
| train both / valid both | 908 / 494 | 25.2 / 27.4 | | | | | | +3.13 / +3.52 | +0.015..+0.024 / +0.047..+0.109 |

- Placebo-adjusted (same geometry, same NY hour): train L +2.2, S +3.0; valid L +4.9, S +1.7, so the setup is not just the time-of-day effect.
- Per-year average excess, M15 (S / L): 2021 −0.2 / +2.8 · 2022 +9.6 / +1.0 · 2023 +3.9 / +1.5 · 2024 +6.1 / +5.1 · 2025H1 −3.4 / +1.6 (8 of 10 cells > 0).
- OCO (one trade per day), M15, 20/mo: train +3.40 (L +1.08, S +5.75), valid +2.81 (L +5.37, S +0.15). Shorts are weak in valid at TP3/TP4 (−2.8 / −2.1).
- M5 (same orders, 1.8·ATR(M5) stop), 25/mo: train L +2.02, S +3.25; valid L +1.03, S +3.19. E@TP1 is about −0.02..0.00 R: the smaller stop pays more spread.
- Day-block bootstrap of the 4-TP average: M15 train +3.13 ± 1.39 (z 2.25, P(≤0) 0.011), valid +3.52 ± 1.89 (z 1.86, P 0.029); M5 z 1.85 / 1.08.
- Sensitivity (rows_cand A*, 18 variants with the 09:30 start on M15 + M5): train cells > 0 in 35 of 36, valid cells > 0 in 29 of 36. The valid misses are the 1.0 ATR stop,
  the 3.0 ATR stop (M15 shorts), the 45 min range and the 16:00 end (M5 longs), and buffer 0.3 ATR on M5. It fails when the range starts at 08:30, 09:00 or 10:00
  (valid longs ≤ 0), so it is specific to the 09:30 equity open.
- Related evidence (not independent: same information): first-30-min momentum (market at 10:00 in the sign of the 09:30-10:00 return, 1.8 ATR) is positive in all
  8 cells on M5 and M15, but small (+0.1..+3.7).

### B. Previous-day high/low sweep, then a confirmation stop entry (M15 only)
**Rule (decided at an M15 bar close, Mon-Fri):**
- PDH / PDL = high / low of the previous NY trading day (18:00 → 17:00 New York).
- Short setup: the first M15 bar of the day with High > PDH and Close < PDH. Long setup: the first bar with Low < PDL and Close > PDL. At most one per direction per day.
- Entry: sell stop at the setup bar's Low − 0.05·ATR (long: buy stop at High + 0.05·ATR), valid for the next 3 bars, otherwise cancelled.
- Stop: setup bar High + 0.1·ATR (long: Low − 0.1·ATR), at least 0.5·ATR from the entry. The median risk is 1.7 ATR(M15).

| M15 | n | /mo | hit TP1 | TP2 | TP3 | TP4 | excess TP1..TP4 | avg excess | E@TP1..TP4 after spread (R) |
|---|---|---|---|---|---|---|---|---|---|
| train long  | 217 | 6.0 | 65.4 | 51.6 | 41.5 | 39.6 | +2.9 +1.9 +1.9 +6.6 | **+3.32** | −0.044 −0.059 −0.054 +0.098 |
| train short | 213 | 5.9 | 67.6 | 53.1 | 43.2 | 39.0 | +5.1 +3.0 +3.4 +5.8 | **+4.33** | −0.011 −0.032 −0.013 +0.076 |
| valid long  | 85 | 4.7 | 76.5 | 57.6 | 50.6 | 41.2 | +10.7 +3.7 +6.3 +3.2 | **+6.01** | +0.198 +0.128 +0.239 +0.210 |
| valid short | 118 | 6.6 | 66.9 | 53.4 | 47.5 | 36.4 | +8.2 +7.4 +11.1 +6.2 | **+8.23** | +0.034 +0.031 +0.149 +0.056 |
| train both / valid both | 430 / 203 | 11.9 / 11.3 | | | | | | +3.82 / +7.30 | −0.045..+0.087 / +0.071..+0.187 |

- Placebo-adjusted: train L +5.2, S +4.6; valid L +6.0, S +7.5.
- Per-year (S / L): 2021 +3.0 / +3.5 · 2022 +0.9 / +8.0 · 2023 +10.0 / −1.1 · 2024 +11.8 / +4.9 · 2025H1 +1.8 / +8.9 (9 of 10 > 0, but each cell has n ≈ 25-80).
- Day-block bootstrap: train z 1.75 (P 0.037), valid z 2.39 (P 0.009).
- Sensitivity on M15 (rows_cand B*): every variant is positive in all 4 cells: window 1/3/6 bars, entry buffer 0.25, stop buffer 0.4, 1.8 ATR stop, all sweeps
  declustered 1 h (35/mo: train +2.8/+1.1, valid +3.2/+5.7), depth ≥ 0.3 ATR, and the 03-12 NY / 18-03 NY windows. The only exception is the 12-17 NY window (few trades, negative).
- **Red flag: it does not carry over to other timeframes.** M5, same rule: train +4.5 / +3.5, but valid shorts −1.0 (z 0.6 overall in valid). H1: valid longs −5.2,
  valid overall −1.0. Market entry on the sweep bar (no confirmation) is about 0. All of the edge sits in the confirmation stop entry.
- Low frequency: about 12 trades a month, near the M15 minimum of 8.

### Runners-up (not recommended)
- C, a round $50 level break (close beyond the next $50 level, market, 1.8 ATR, 1 h declustering): M5 train +3.2 / +0.9, valid +2.0 / +3.9 (z 2.5). M15 train is about
  0 (+0.3 / +0.8) and H1 train longs are −2.8. $25 fails train shorts. Not consistent across timeframes.
- D, a fade when |Close − session VWAP| first exceeds 6·ATR(M5): M5 train +2.0 / +2.8, valid +5.0 / +1.5; 5-8 ATR are all positive on M5. On M15 the 4-5 ATR versions
  fail valid, and H1 fails. Not consistent.

## (3) Honest conclusion
- **No new setup beats random entries out of sample with confidence.** 292 of 357 variants fail at least one of the four cells. Most opening-range, Asian-range,
  VWAP (reclaim, reject, pullback, 1σ, 2-2.5σ fades), data-bar, momentum, consecutive-bar, NR7/inside-bar, gap and round-number rules sit within ±2 points of
  random, with no consistent sign. A recurring trap: tight structural stops look good in train (+5..+9) and turn negative in valid longs.
- The two best, A (NY 09:30 opening-range stop entries) and B (PDH/PDL sweep, confirmation stop entry, M15), have positive excess in train and valid, for longs and shorts
  separately, at every TP, mostly every year, and across their parameter neighbourhoods. But their size (+3 to +7 points, z ≈ 2-2.5 per split) is about what the
  best of ~360 correlated tries reaches by chance (pooled-z cloud mean 0.5, sd 1.05, max 2.8). A also lacks independent cross-TF evidence (M5 is the same orders),
  and B fails on M5 and H1. E after spread is near zero: A M15 +0.01..+0.11 R a trade, B M15 −0.05..+0.19 R. Stop-order slippage is not modelled and would eat
  most of it.
- If anything goes to TEST, use **A on M15 (or OCO A)** as the single pre-registered candidate, with B as the second. Treat them as hypotheses: success
  means average excess > 0 for both directions on 2025-07..2026-10, judged once. Expect a hit-rate improvement of 2-4 points at best. That does not change the
  verdict that a large, stable entry edge for TP1-TP4 is not available from these session/VWAP/structure rules alone.
- I did not try: M1 (no kit baseline file), combining A or B with the NY time-of-day filter (the A sensitivity with end 16:00, which covers the 14-17 long window,
  was no better), and ML on top of these setups (n too small).

Cheaper models: none. The whole study ran in this one agent (Opus); no sub-agents were launched.
