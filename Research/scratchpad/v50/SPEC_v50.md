# v5.0 money rules: exact specification (strategy, EA and gold/recovery.py)

Asked 2026-11-19: (1) a setting so the base amount and every loss-recovery amount mean the PROFIT at the final TP (the stop-out loss
follows from it), for every recovery rule; (2) Crooks K; (3) Crooks L. Everything else is unchanged: with the new setting on its
default (Risk) and neither K nor L chosen, every number must be bit-identical to v4.9.

Notation (one setup being sized):
- `exitR` = the R of the final exit (TP1..TP4 of the Final Exit setting; Pine `exitR`, EA `NextRisk(exitR)` / `ExitR()`). Always > 0.
- `pm` = Size By is Profit. `D` = `pm ? exitR : 1.0`.
- `nR` = closed profit since the zero line = Pine `strategy.netprofit - rNet0`, EA `totalNet - gNet0`, reference `net`
  (the zero line = the last monthly restart, else the start).
- `pR` = the best closed profit since the zero line = `crkPk` (updated at every booking: `crkPk = max(crkPk, nR)`; 0 at a restart),
  reference `peakNet`.
- `minRisk` / `eRisk` = the stop-out $ loss of the Crooks E / I lot (InpCrkELot / crkELot, rounded up to the lot step, at least one
  step) on this setup, costs included (unchanged v4.5 definition). Reference: trade element [5].
- `kRisk` = the same for the Crooks K careful lots (InpCrkKLots / ckLots). Reference: trade element [7].

## 1. Size By: Risk (default) / Profit

New input after Position Size. Pine `sizeBy` ("Base And Recovery Amounts Are": "Risk: the loss at the stop" / "Profit: the win at the
final TP"); EA `InpSizeBy` (SZB_RISK = 0, SZB_PROFIT = 1).

With Profit (`pm`), all with the same `exitR` the trade is sized with:
1. Base: Fixed $: `B0 = BaseRisk$ / exitR`; % of equity: `B0 = max(0, equity) x pct / 100 / exitR`; Fixed lots: unchanged (the lots'
   stop-out loss).
2. Amounts the rule adds are divided by `D`:
   - All: `B0 + pool / D`; Over N: `B0 + pool / N / D`; % of losses: `B0 + pool x pct / 100 / D`; Step-up: `B0 + step x losses / D`;
     Delayed: `B0 + pool / N / D` (after N losses); Rule C / C split: `max(baseC, carried / split / D)`, C split's step base:
     `stepBase / D` (then the hard-cap min and the max with B0 as before); % of equity (rule): `equity x pct / 100 / D`.
   - Exact at final TP (`B0 + pool / exitR`) and every Crooks rule (`loss / exitR`) already divide: unchanged formulas.
   - Martingale, Fibonacci, D'Alembert, Labouchere, Grand Martingale, Paroli, Reverse D'Alembert: multiples of B0, unchanged formulas.
   - Oscar's Grind: the cycle goal is one base WIN: `G = pm ? B0 x exitR : B0`; `oscNeed = max(1, ceil((G - oscP) / (B0 x exitR)))`;
     booking: the cycle ends when `oscP >= (pm ? exBase x exitR : exBase)` (EA: `BookBase() x ExitR()` with pm).
3. Limits stay on the risk (the stop-out loss): the hard cap, Crooks F / I (K x base), G (X x base), H (% of equity), J (X x base),
   the profit ladder (all in base RISK = B0), and Crooks L's part steps (x base).
4. In risk mode every expression is the v4.9 one (division by D = 1.0 is exact; nothing else changes).
5. EA `BookBase()`: Fixed $ with Risk = InpBaseRisk (as before); otherwise `exBase > 0 ? exBase : InpBaseRisk / D` (D with ExitR()).
6. Validation: Pine: exitR >= 0.1 by the input minimum; EA OnInit: Profit needs ExitR() > 0.

## 2. Crooks K (ENUM 28, after Crooks J)

Crooks C family (every Crooks C setting applies: over N wins, the rule after N losing recovery trades, the TP1 rule) and the profit
ladder family; its recovery trades shrink like Crooks J (`max(B, q x max(0, 1 - max(0, pR - nR) / (jX x B)))`).
- K zone = `nR < 0` (below the zero line). In the K zone, after the Crooks + ladder size is computed, it is REPLACED:
  - `crkW` (the last closed trade won): the careful size: Lots: `kRisk` (EA: `kRisk > 0 ? kRisk : B0`); Fixed $: `ckUsd / D`;
    % of base: `B0 x ckPct / 100`;
  - else: the Crooks E / I lot: `min(B0, eRisk)` (EA: `minRisk > 0 ? min(B0, minRisk) : B0`).
- The ladder's start guard (0.01 lot at nR <= 0) does not apply to K (LadGuard() false for K; Pine f_lad guard false for K).
- The TP1 rule is off in the K zone (CrkT1Dist() = 0 / t1Ok false), so the careful and 0.01-lot trades use the normal exits.
- Inputs: careful mode Lots (default) / Fixed $ / % of base; lots 0.02; $ 25; % 50.
- EA: TakeSetup passes minRisk = MinLotRisk() for E, I, K, L or when the ladder is on; kRisk = LotRisk(InpCrkKLots) for K with Lots.

## 3. Crooks L (ENUM 29, after Crooks K)

Crooks C family (not the ladder family). While a loss is owed, a trade that is not the recovery trade is the Crooks E / I lot
(`min(B, eRisk)`, as Crooks E). The recovery trade goes for `loss / parts` (`max(B, x / exitR)`, the TP1 rule as Crooks C).
- Parts are decided when a LOSS is booked (after crkPk is updated), from the closed profit after that loss:
  - `nR < 0`: `dd = -nR`, `step = z1 x b`, `most = z1N`;
  - `0 <= nR < pR`: `dd = pR - nR`, `step = z2 x b`, `most = z2N`;
  - else 1 part.
  - `parts = max(1, min(most, ceil(dd / step - 1e-9)))`; `b` = the booked trade's base risk (EA `BookBase()`, Pine `exBase`,
    reference the trade's `b`).
  - A winning recovery trade: one part fewer (at least 1); any other win: unchanged; a new cycle / restart / cap reset: 1 part.
  - "Over N wins" (crkCn) is not used by L (its N is 1 for L).
- Base growth at a new best: when `nR >= pR` (the closed profit is at its best since the zero line, also at the start),
  `B = B0 + min((gMax - 1) x B0, max(0, g / 100 x nR / D))`; otherwise `B = B0`. B is the base of all of L's sizing for that trade
  (base trade, recovery minimum, waiting lot min(B, eRisk)). The hard cap's Start-again size stays min(baseC, cap) with baseC = B0.
- Inputs: below the start: 1 part per 2 x base, at most 6 parts; above the start: 1 part per 5 x base below the best, at most 3 parts;
  at a new best: base + 10% of the profit, at most 4 x base.
- EA CrkParts() for L: `max(1, min(crkP, max(z1N, z2N)))` (a state from another rule can hold any crkP).

## 4. Order of operations (sizing; Crooks case)

1. `B0` (section 1). L: `B = LBase(B0)`; others `B = B0`.
2. `r = CrkRule(B)` (E / I / L waiting lot; F / I / H / J / K limits).
3. Ladder (F - J, K) when on: `r = guard ? min(B0, eRisk) : min(CrkRule(ladderBase(B0)), r + gam x C / m)`; guard never for K.
4. K zone: replace r (section 2).
5. Hard cap (unchanged).
