# Holdout plan (written BEFORE the TEST months 2025-07-01 .. 2026-10-02 are opened; they are opened once)

Candidates (rules frozen as below; numbers in brackets = train / valid average excess over TP1-TP4, long / short):

1. PRIMARY  C1 - M5: when the indicator's raw signal fires on a bar opening 12:00-17:59 New York time (next bar without a gap),
   take the OPPOSITE trade at market at the signal close; stop 1.8 ATR; TP 0.6 / 1 / 1.5 / 2 R.  [+4.98/+4.02, +9.18/+2.48]
2. C1L - the same, long side only (fade bearish signals only).  [+4.98, +9.18]
3. ORB - M15 (agent A): range 09:30-10:00 NY (weekdays); at 10:00 a buy stop at its high + 0.05 ATR and a sell stop at its low - 0.05
   ATR, both valid until 13:00 NY; stop 1.8 ATR from the entry.  [+1.8/+4.5, +3.9/+3.1]
4. SWEEP - M15 (agent A): first bar of the NY trading day with High > previous day's high and Close < it (short; mirror long);
   stop entry 0.05 ATR beyond the sweep bar's other end, valid 3 bars; stop 0.1 ATR beyond the sweep extreme, at least 0.5 ATR.
   [+3.3/+4.3, +6.0/+8.2]
5. Reference: time-of-day bias, every bar (long NY 13:00-16:59, short NY 07:00-09:59), M15 and M5.
6. Reference: the indicator as it is (raw signals, retest limit), M5 and M15.

Pass rule (decided now): a candidate passes when its TEST average excess is > 0 for longs AND for shorts (C1L: longs), the pooled TEST
excess is at least 1 standard error, and at least 3 of the 4 targets are above random. Expected size if real: +2 to +5 points.
Only a passing PRIMARY (or C1L) goes into the indicator as a new option; ORB / SWEEP only if they pass clearly (they were not
significant after multiple testing).
