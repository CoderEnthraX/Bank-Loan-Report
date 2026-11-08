
## (3) Honest conclusion
- **Classical order-flow entries computed from tick volume do not give an edge on gold.** Absorption, failed auctions, the 80 % rule, LVN / HVN, POC
  migration, CVD divergence, delta flips, climax with opposite delta and IB breakouts with CVD agreement all sit within the noise band of random entries,
  or they work on one timeframe and fail on the others. Estimated delta and CVD never add information. Gold CFD tick volume carries no aggressor side.
  CLV or tick-rule "delta" is just a transform of the candle shape, and the indicator's signals already agree with it 96-98 % of the time.
- **Answer to the question:** no order-flow-only rule beats random at all four TPs, both directions, train and valid, on more than one timeframe. The one rule that
  does on M5 is **C3**: when the indicator fires an impulse signal AWAY from the developing POC while price is already >= 5.8 M5-ATR from it, take the
  **opposite** trade. Hit rates go up 2-6 points at every TP (train +4.9, valid +3.7 average; every year positive). The volume-profile part of it
  is only "how far price is from the session's value"; VWAP distance works about as well, which helps for coding in Pine or MQL5. It is an
  exhaustion fade, and the indicator's own direction is the wrong side in that state. So a practical change to the indicator is to **suppress
  signals that point away from the POC / VWAP when |C - POC| >= ~6 M5-ATR** (they are worse than random), or to trade them the other way.
- **Caveats.** (a) It was found after ~500 tries, and after looking at valid for the step that led to it, so valid is not a clean confirmation.
  Train alone is z ~4, above a Bonferroni bar for ~500 tests but not by much. (b) Timeframe support is partial: M5 strong, M1 and H1 positive but
  small (z < 2), M15 weak. (c) The money edge is thin: E after spread at 1.8 ATR is -0.06..+0.06 R a trade in train and -0.07..+0.24 R in valid (longs
  helped by the 2024-25 uptrend). Slippage on market orders right after an impulse bar is not modelled. (d) 2025H1 is the weakest year (L +1.8, S +0.3).
- **Recommendation:** pre-register **C3 on M5** (exact rule above, k = 5.8 ATR, 1.8 ATR stop, market, 1-hour decluster) as the single TEST candidate, with
  success = average excess > 0 for longs AND shorts on 2025-07..2026-10, judged once. Use C3gen (no indicator) and C3 on H1 as secondary looks only.
  Expect +2..+4 points of hit rate at best and an E near zero after costs. The edge is useful as a **filter / veto on the indicator**, not as a stand-alone money-maker.

Cheaper models: none. Every step ran in this single agent (Opus); no sub-agents were launched, and every number above comes from scripts in this folder.
