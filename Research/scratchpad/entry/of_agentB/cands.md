
## (2) Best candidates in detail

### C3 (main): fade the indicator's signal when it extends away from the developing POC (M5)
**Rule, decided at the close of M5 bar i:**
1. Session = server day (the indicator's VWAP session; it starts at 17:00 New York). Developing POC = price bin ($0.50) with the most tick volume
   in the session so far, built from the session's 1-minute candles up to bar i's close (each minute's tick volume spread evenly over its high-low).
2. `dist = (C[i] - devPOC[i]) / ATR14[i]` (ATR = RMA 14 of M5 true range). Need `|dist| >= 5.8` (80th percentile of |dist| on train bars).
3. Bar i carries a raw Auction Retest signal (`signals.raw('M5')`, default parameters, not both directions at once) whose direction is AWAY from
   the POC: a LONG signal with dist >= +5.8 or a SHORT signal with dist <= -5.8.
4. Bar i is >= 180 min after the session start, Monday-Friday (NY trading day).
5. Trade the OPPOSITE way: long signal -> SELL, short signal -> BUY, **market** at bar i's close (filled on the next bar).
6. Stop = entry -+ 1.8 x ATR14[i]; TP1-TP4 = 0.6 / 1 / 1.5 / 2 R. Skip it if a trade in the same direction was taken in the previous 12 bars (1 hour).

**Trades:** 43 a month in train (21 long, 22 short), 49 a month in valid.

| split | dir | n | n/mo | hit TP1-TP4 | excess TP1-TP4 | avg | placebo-adj TP1-TP4 | E after spread TP1-TP4 (R) |
|---|---|---|---|---|---|---|---|---|
| train | long | 771 | 21.4 | 66.1 / 54.7 / 45.3 / 39.0 | +4.0 / +5.0 / +5.3 / +5.9 | +5.1 | +4.3 / +5.2 / +4.9 / +5.0 | -0.06 / -0.02 / +0.02 / +0.06 |
| train | short | 784 | 21.8 | 66.5 / 55.2 / 43.8 / 39.0 | +3.9 / +5.1 / +3.7 / +5.8 | +4.6 | +3.1 / +4.5 / +2.4 / +4.5 | -0.05 / -0.01 / -0.02 / +0.06 |
| valid | long | 366 | 20.3 | 68.3 / 58.5 / 48.9 / 42.6 | +4.0 / +5.6 / +5.5 / +5.7 | +5.2 | +1.9 / +3.3 / +2.2 / +3.3 | +0.06 / +0.13 / +0.18 / +0.24 |
| valid | short | 518 | 28.8 | 63.1 / 49.4 / 39.2 / 33.0 | +3.1 / +2.4 / +2.2 / +2.8 | +2.6 | +2.5 / +2.7 / +2.0 / +2.6 | -0.04 / -0.06 / -0.07 / -0.06 |

Per-year average excess (n): 2021 L +5.1 (240) / S +9.0 (255); 2022 L +4.2 (250) / S +3.6 (280); 2023 L +5.8 (281) / S +1.3 (249);
2024 L +6.7 (255) / S +3.7 (350); 2025H1 L +1.8 (111) / S +0.3 (168). **All 10 cells are positive**, but 2025H1 is the weakest.
Month-block bootstrap (2000 resamples, `boot.out`): train +4.85 (se 1.19, z 4.1; L z 3.5, S z 2.7), valid +3.70 (se 1.45, z 2.6; L z 2.4, S z 1.3).

Sensitivity (M5, `c3.out`, every one all-4 > 0; train L / S, valid L / S): pct 70 +4.7 / +3.8 / +2.7 / +1.6; pct 90 +6.0 / +3.7 / +7.3 / +2.8;
pct 95 +11.6 / +6.0 / +6.8 / +4.2 (8/mo); stop 1.2 ATR +4.3 / +3.4 / +6.0 / +4.3; stop 2.5 ATR +4.2 / +4.7 / +6.4 / +1.9; no session-time filter
+4.4 / +2.8 / +4.7 / +1.4; not declustered (70/mo) +5.2 / +4.5 / +3.3 / +3.4; distance from VWAP instead of POC +3.8 / +4.6 / +2.8 / +2.7;
from the prior session POC +3.1 / +3.3 / +4.5 / +3.1. Control: the same opposite trade on signals NEAR the POC (< p80): +1.5 / -0.3 / -2.9 / -0.3. So distance is the key.
A stop entry (instead of market) is weaker (shorts -2.3 in valid).

Other timeframes (same rule, p80 of that timeframe, `detail3.out`):

| TF | k (ATR) | n/mo train | train L | train S | valid L | valid S | E TP1 / TP4 train | note |
|---|---|---|---|---|---|---|---|---|
| M1 | 14.3 | 83 | +3.8 | +0.8 | +1.4 | +3.1 | -0.33 / -0.29 | positive but spread (0.17 R+) eats it; train shorts placebo-adj ~0 |
| M5 | 5.8 | 43 | +5.1 | +4.6 | +5.2 | +2.6 | -0.05 / +0.06 | candidate |
| M15 | 3.4 | 28 | -0.8 | +1.7 | +1.2 | +0.3 | -0.05 / -0.06 | weak, train longs negative: FAIL |
| H1 | 1.8 | 15 | +1.8 | +3.0 | +2.7 | +6.7 | +0.01 / +0.00 | all 4 > 0 but z 1.4 / 1.8; valid long placebo-adj -1.1 |

### C3gen: the same idea without the indicator (M5, also M15)
Replace step 3 with a generic impulse bar: body `|C-O| >= 0.8 ATR` in the direction away from the developing POC and a close in the outer 25 % of
the range (CLV >= +0.5 for an up bar, <= -0.5 for a down bar); everything else as C3 (fade at market, 1.8 ATR stop, p80 distance 5.8 ATR, 1-hour decluster).

| split | dir | n | n/mo | hit TP1-TP4 | excess TP1-TP4 | avg | placebo-adj TP1-TP4 | E after spread TP1-TP4 (R) |
|---|---|---|---|---|---|---|---|---|
| train | long | 1023 | 28.4 | 64.2 / 52.0 / 42.1 / 35.5 | +2.1 / +2.2 / +2.2 / +2.4 | +2.2 | +1.5 / +1.9 / +1.9 / +2.2 | -0.09 / -0.07 / -0.06 / -0.05 |
| train | short | 1010 | 28.1 | 65.0 / 53.4 / 43.7 / 37.8 | +2.5 / +3.2 / +3.6 / +4.6 | +3.5 | +1.9 / +2.1 / +2.3 / +3.6 | -0.08 / -0.05 / -0.03 / +0.02 |
| valid | long | 494 | 27.4 | 67.6 / 56.7 / 48.8 / 42.3 | +3.3 / +3.8 / +5.4 / +5.4 | +4.5 | +3.6 / +3.1 / +5.0 / +4.6 | +0.04 / +0.09 / +0.18 / +0.23 |
| valid | short | 661 | 36.7 | 61.9 / 48.1 / 37.1 / 31.5 | +1.8 / +1.1 / +0.1 / +1.3 | +1.1 | +1.5 / +1.3 / -0.3 / +0.8 | -0.06 / -0.08 / -0.12 / -0.10 |

Per year: 2021 L +2.4 / S +4.8; 2022 L +0.4 / S +3.5; 2023 L +3.9 / S +2.4; 2024 L +5.3 / S +2.7; 2025H1 L +2.7 / S **-2.3**.
Bootstrap: train z 2.3, valid z 1.6. On **M15** (k 3.4 ATR, 33/mo) it is all-4 > 0 too: +1.9 / +2.0 / +1.6 / +1.9 (placebo-adj +5.4 / +2.2 / +2.4 / +2.7 on TP1),
year cells 8 of 10 positive. Smaller than C3, but it shows the effect is a general "exhaustion bar far from value" pattern and not something special to the indicator.

### C1 (long-only, weaker): buy far below the developing POC (M5)
Rule: `dist <= -8.6` (p90 of |dist| on train, M5 ATR), session >= 180 min, Mon-Fri, BUY at market, 1.8 ATR stop, 1-hour decluster; 28 longs a month.
Longs: train +5.6 / +5.7 / +3.8 / +5.0 (avg +5.0, placebo +3.5), valid +3.4 / +4.0 / +3.8 / +5.1 (avg +4.1, placebo +2.2); every year +3.2..+5.9;
E after spread train -0.04 / -0.01 / -0.03 / +0.02, valid +0.04 / +0.09 / +0.14 / +0.21 R. Shorts (the mirror) do not work (+1.1 train, -0.3 valid), and M15 / H1
longs are weak or negative in valid. Only a one-direction rule, with no reason it should be one-sided other than gold's long-run drift. C3 contains most of its long trades.
