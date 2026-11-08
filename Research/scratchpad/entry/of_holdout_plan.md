# Order-flow holdout plan (written BEFORE the TEST months 2025-07-01 .. 2026-10-02 are opened for these rules)

Note: the TEST months were already opened once (2026-11-08) for the entry finalists of item 24 (none passed). These order-flow rules
were found without looking at TEST (agents never loaded it); TEST is opened once more, only for the rules below.

From agent OF-A (order flow as a filter of the indicator's signals; re-derived independently by the main session, same numbers):
1. OFA-C1 - M5: take the indicator's raw signal (retest limit, stop_h, 5 bars) only if the PREVIOUS session's tick-volume value area
   (VAH - VAL, 70 %, $0.50 bins) <= 7.5 x ATR(14) at the signal bar.  [train +1.65 / +0.83, valid +1.26 / +4.13, long / short]
2. OFA-C1b - M5, the no-volume control: previous session's high - low <= 16.8 x ATR(14).  [+1.88 / +0.66, +1.83 / +2.67]

From agent OF-B (order-flow entries; re-derived independently, same numbers within ~0.5):
3. OFB-C3 - M5, fade the extension from the POC: the indicator's raw signal points AWAY from the developing session POC with
   d x (C - dPOC) / ATR14 >= 5.8, the bar is >= 180 minutes into the session (Mon-Fri); take the OPPOSITE trade at market, stop 1.8 ATR;
   skip if a trade of the same direction was taken in the last 12 bars.  [train +5.16 / +4.53, valid +5.35 / +3.12]
4. OFB-C1L - M5, long only: price >= 8.6 ATR below the developing POC, >= 180 minutes into the session; long at market, stop 1.8 ATR,
   one per 12 bars.  [train +5.13, valid +4.49]

Pass rule (same as item 24): TEST average excess > 0 for longs AND shorts, pooled >= 1 standard error, >= 3 of 4 targets above random.
