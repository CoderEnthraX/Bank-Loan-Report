# Independent check 3: monthly results of the recommended settings ($1,000 fresh every month)

Recompute the monthly results of 5 settings from the raw trades using ONLY this spec, then compare with `expected.json`.
Do NOT read any .py file outside this `verify/` folder.

## Inputs
- `trades.json`: `{"ars": {"M15-S3 fcOff": {exitR, trades}}, "grid": {"S1"|"S2"|"S6"|"S7"|"S8"|"S10": {exitR, trades}}}`; each trade
  `{entry, exit, R, c, levk, rmin}` (IST ISO times, in time order, never overlapping within one strategy). `R` = result in R, `c` = cost in R,
  `levk` = the leverage limit per $ of balance, `rmin` = $ risk of 0.01 lot (not needed here).
- `expected.json`: `{name: [70 monthly nets]}` for months Jan 2021 .. Oct 2026 (open it only to compare, after computing).

## Months
70 IST calendar months Jan 2021 .. Oct 2026. A trade belongs to the month of its ENTRY time. Every month starts again: a fresh balance, a fresh
money state; the month's net = the sum of the P&L of the trades it took.

## One account, one month (trades in order)
State: eq = start; recPool = 0; oscU = 1; oscP = 0; net = 0. For each trade:
1. If the month has a lock L and net >= L: stop taking trades for this month.   2. If eq <= 0: stop (blown).
3. Risk r by rule (b = base):
   - No recovery: r = b.
   - Exact recovery at final TP: r = b + recPool / exitR.
   - Oscar's Grind: need = max(1, ceil((b - oscP) / (b * exitR))); r = b * min(oscU, need).
4. Hard cap: if cap > 0 and r > cap: r = cap (Clamp).   5. If eq > 0: r = min(r, eq * levk).
6. pnl = r * (R - c) / (1 + c); eq += pnl; net += pnl; win = pnl > 0.
7. Exact recovery bookkeeping: if win: recPool = max(0, recPool - pnl); else recPool += -pnl.
   Oscar's Grind bookkeeping: oscP += pnl; if oscP >= b: oscU = 1, oscP = 0; else if win: oscU += 1.

## The 5 settings
- `ars_safe`: ARS "M15-S3 fcOff", one account start 1000, Oscar's Grind, b = 10, no cap, lock 20.
- `ars_norec`: ARS "M15-S3 fcOff", start 1000, No recovery, b = 20, no cap, lock 20.
- `grid_bal`: grid S7 + S8 + S10, EACH strategy its own account with start 1000 / 3 and its own money state; Exact recovery, b = 10,
  cap 100 Clamp, no lock; the month's net = the sum of the three accounts' nets.
- `grid_safe`: grid S1 + S2 + S6 + S7 + S8 + S10, each its own account with start 1000 / 6; Exact recovery, b = 5, cap 50 Clamp, no lock; summed.
- `combo safe + balanced`: ARS "M15-S3 fcOff" with start 500, Oscar's Grind, b = 5, no cap, lock 10, PLUS grid S7 + S8 + S10 each with start
  500 / 3, Exact recovery, b = 5, cap 50 Clamp, no lock; the month's net = ARS net + the three grid nets.

## Report
For each setting: months compared, months differing by more than $0.01, the largest difference, the number of months with profit / loss in
your results, and up to 5 mismatches. Keep a progress file `indep3/progress.md` and your code in `verify/indep3/`.
