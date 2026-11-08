
Rows with `*few trades*` fall below the README minimum (M5 20/mo, M15 8/mo, H1 3/mo, M1 taken as 40/mo; train, long + short).

### What failed (short)
- **Absorption at VA edges** (F1, F1b): strict version 0.4-6 trades a month, noisy. Loose version: M15 prior-VA longs +5..+7 in train, -0.5..-3.9 in valid.
  Adding "delta pushes into the level" makes it worse or too rare.
- **Failed auction at the prior VAH / VAL** (F2): M15 train negative in every variant; M5 "accepted outside, back inside, stop entry" +1.0 / +1.1 / +1.4 / +5.7 (z 1.9): noise.
  **80 % rule** (open outside the prior VA, back inside 30 min, session or NY 09:30 anchor): 2-7 a month, signs mixed.
- **LVN / HVN** (F3): breakouts with an LVN ahead (composite-profile path RVP < 0.5) are no faster or better than with an HVN ahead or all breakouts (all within
  -2.5..+1.7 train). LVN rejection: 3-5 a month, mostly negative. "HVN hold" reversal is no better than the same reversal outside an HVN.
- **POC** (F4): reversion to the prior POC and the /sigma version fail. POC migration (trend or pullback to dev POC) fails valid longs. Reversion to the developing POC
  at >= 8.6 M5-ATR (C1) works for **longs only** (M5 train +5.0, valid +4.1, every year +3.2..+5.9; shorts +1.1 / -0.3). M15 / H1 longs are weaker or negative in valid.
- **Delta / CVD** (F5): CVD divergence at a new session high / low (C2) is all-4 > 0 on M5 with CLV delta (+2.4 / +2.2 / +1.6 / +5.4, 24/mo) but **negative on M1, M15
  and H1 in valid** in every variant, so it is a one-timeframe fluke. Delta flip after a session-extreme sweep: negative. Climax volume with opposite delta: 1-2 a month,
  no better than climax with aligned delta. IB (NY 09:30-10:30) breakout with CVD agreement: no better than with disagreement (both ~0).
- **Order flow on the indicator's signals** (F6): 96-98 % of signals already have bar delta in their direction and 80-85 % have the session CVD with them, so these filters
  select almost nothing. CVD / value-area / LVN-ahead filters and opposite trades on the NOT subsets are all within +-2, with signs flipping between train and valid.
  Only the distance-from-POC condition (C3) matters.
- **Delta on top of C3**: splitting C3 by the signal bar's delta strength or by session CVD with / against the move changes nothing consistent (both halves +2..+7).
