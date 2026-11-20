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

## 5. v5.1 (2026-11-19): Profit = the win at the final TP INCLUDING the costs

v5.0 used `D = exitR`, so a final-TP win was `amount x stop / (stop + costs)` (gold M5: about 8-9% short). v5.1 sizes with the win per $ of
stop-out loss of THIS setup:
- `D = W / Lu`: `Lu` = the stop-out loss per unit (costs included; the sizing's per-lot loss), `W` = the win per unit at the final TP:
  with earn-back `exitR x stop` (the target is pushed by the costs), without it `exitR x stop - costs`.
  EA: `PDiv(exitR)`: `Lu = (trRisk + spr) / ts x tv + comm`, `W = exitR x trRisk / ts x tv` (- `spr / ts x tv + comm` without
  earn-back); no tick value / stop, or `W <= 0` or `Lu <= 0`: `D = exitR` (the v5.0 rule). Pine: `pvf = pointvalue x fx`,
  `Lu = rp x pvf + costUnit`, `W = exitR x rp x pvf` (- costUnit). Reference: trade element [8] = D (given by the parity script exactly as
  the harness computes it), absent: `exitR`.
- With Profit EVERY amount-to-risk conversion uses this D: the base (Fixed $ and % of equity), the rule add-ons (D instead of 1), Exact
  (`pool / D`), the Crooks recovery (`x / D` instead of `x / exitR`, also on the ladder base), Crooks L's growth (`/ D`), Crooks K's
  careful $ (`/ D`), Oscar's need `(B0 D - oscP) / (B0 D)` with the goal = one base win `B0 x D` (kept with the trade: EA `exBaseWin`,
  saved as "xw"; Pine `exBaseWin`; booking `oscP >= base win of the booked trade`).
- Risk mode: unchanged (v5.0 = v4.9: Exact and Crooks divide by exitR).
- The Crooks TP1 rule is unchanged (its size already banks the amount at TP1 after the costs).

## 6. v5.2 (2026-11-19): Crooks X (ENUM 30, after Crooks L)

Asked by the user: Crooks E (0.01 lot while a loss waits for a win, then N recovery trades) where the loss to win back is measured from the
levels, not summed from the trades.
- Zero line = the start (EA start / backtest start; with the monthly restart the 1st of the month). `nR` = closed profit since it,
  `pR` = the best closed profit since it (crkPk / peakNet, updated before this). `step` = InpCrkXStep / xStep (default $1,000).
- After every booked trade (after crkPk / peakNet is updated) the loss to win back is SET (not reduced by the P&L):
  - `nR < -0.005` (below the start): `T = -nR` (the whole gap to the start, however big);
  - `nR >= pR - 0.005` (at the best): `T = 0` (a new cycle, base trades);
  - else (above the start, below the best): the level = `min(pR, (floor((nR + 0.005) / step) + 1) x step)`, `T = max(0, level - nR)`.
  The 0.005 makes a balance a fraction of a cent under a level count as at it (then the next level is the target).
- Parts: N = "win the loss back over N wins" (CrkNp: N when on, else 1). As Crooks C / E: a loss sets the parts to N; a winning recovery
  trade one fewer (at least 1); in addition a WIN that moves the closed profit into another step (index `-1` below the start, else
  `floor((nR + 0.005) / step)`; before = nR - pnl, after = nR) sets the parts to N (a new step is won back in N trades).
- T < 0.01: a new cycle (as Crooks C). Waiting lot: as Crooks E (min(B, the 0.01-lot risk) while T > 0 and not a recovery trade).
- Recovery trade: as Crooks C: `max(B, T / parts / XR)` (XR = exitR with Risk, D with Profit; TP1 rule as Crooks C).
- Limit (new): InpCrkXLim / xLim: "Hard cap only" (default; the hard cap as for every rule) or "Per-trade limit ($)": a recovery trade's
  stop-out risk is at most max(B, InpCrkXLimUsd) (EA: / CrkT1Mult(), as Crooks F). Default limit $500.
- The rules after N losing recovery trades (forget / % / wait / skip / hedge) and the hard cap's Start again clear the loss; with Crooks X
  it is measured again at the next close (the gap to the level is still there).
- No new saved state (T and the step come from the closed profit, crkPk and crkL, all already saved).

## 7. v5.3 (2026-11-19): recovery part size: recalculate (default) / fixed when recovery starts

For the Crooks C family (C, E - L, X; N from "win the loss back over N wins", Crooks L its own parts). New input "Recovery part size":
Recalculate after each win (default: every v5.2 number unchanged) / Fixed when recovery starts. Fixed (`fx` = the fixed part, $ to win
back, 0 = not set; EA `crkFx`, saved as "kq"; Pine `crkFx`; reference `crFx`), at every booking in the not-new-cycle branch, after the parts
update and Crooks X's new step:
- a loss: `fx = 0`;
- a win: Crooks X new step: `fx = 0` first; then if this was a recovery trade for the last part (`crRec and parts were 1`, not a new X step):
  the leftover `crL < base amount` (Risk: the booked trade's base risk; Profit: its base win `b x D` / exBaseWin) -> a new cycle (forgotten,
  base trades); else `fx = crL`, parts = 1 (one more trade for exactly what is left; repeated the same way); otherwise if `fx <= 0`:
  `fx = crL / parts` (set at the first win).
- every new cycle (all won back, cap Start again, monthly restart, forget rules): `fx = 0`; EA hedge pair kept going: `fx = 0`.
- Sizing: the part a recovery trade goes for = `fx > 0 ? min(fx, crL) : crL / parts`, then x the % rule's %, then as before (/ XR, limits).

## 8. v5.4 (2026-11-20): 10 money rules (Loss Recovery 31 - 40)

Notation at sizing: B = the base (as every rule; Profit: / D), E = the equity (EA AccountInfoDouble(ACCOUNT_EQUITY), Pine
strategy.initial_capital + strategy.netprofit, reference eq), nR = closed profit since the zero line, pk = crkPk / peakNet, start0 = E - nR,
dd = pk > nR and start0 + pk > 0 ? (pk - nR) / (start0 + pk) : 0, mlot = the 0.01-lot risk (minRisk / rmin; 0 or unknown: B).
State (booked after every closed trade, all modes): the R of the trade = pnl / its planned risk (EA exRisk0 = NextRisk's r, saved), kept
for the last KWin trades; the closed profit after each trade (nR, starting with 0 at the zero line), kept for the last EqN values (cleared at
the monthly restart); s1326 (a win: (s + 1) mod 4, a loss: 0); lossRow / coolLeft. RecoveryRestart (cap Start again, monthly restart):
s1326 = 0, lossRow = 0, coolLeft = 0.
- Kelly(learned): with fewer than KMin R values: B. Else over the last KWin: p = share of R > 0, Rw = mean of R > 0, Lw = -mean of R <= 0
  (none: 1), f = Rw > 0 ? max(0, (p Rw - (1 - p) Lw) / (Rw Lw)) x KFrac : 0; f > 0: r = f x E x Lw, else r = mlot.
- 31 Kelly: Kelly(learned). 32 1-3-2-6: B x (1, 3, 2, 6)[s1326]. 33 Equity-curve filter: MA = mean of the kept nR values (incl. the last);
  r = B x (nR >= MA - 1e-9 ? 1 : EqLow). 34 Drawdown cut: B x (dd < Dd1 ? 1 : dd < Dd2 ? 0.5 : 0.25). 35 Cooling-off: B; after CoolL losses
  in a row the next CoolN signals that could be taken are skipped (each one counts down), then lossRow starts again.
- 36 C1: nR >= 0 and dd < Dd1 ? B x 2^parWins (Paroli, Wins Before Reset) : B x min(1, E / start0) x (dd < Dd2 ? 0.5 : 0.25).
  37 C2: nR >= 0 ? B x (1, 3, 2, 6)[s1326] : min(B, mlot). 38 C3: E x C3Pct / 100 / D x (nR >= MA - 1e-9 ? 1 : EqLow).
  39 C4: Kelly(learned), x 0.5 when dd >= Dd1. 40 C5: nR >= 0 ? B + min(recPool / RecN / D, C5Share / 100 x nR) : as C1's brake.
  C1 - C5: r = min(r, Cap / 100 x E). Then the hard cap as every rule.
- Defaults: KFrac 0.25, KWin 100, KMin 30, EqN 20, EqLow 0.25, Dd1 10%, Dd2 20%, CoolL 2, CoolN 3, Cap 3%, C3Pct 1.5, C5Share 30%.
