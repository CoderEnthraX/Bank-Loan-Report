# Independent check: monthly money results of Crooks E - J x profit-ladder levels

Recompute sample results from the raw trade lists using ONLY this spec, and compare them with the two workbooks.
Do NOT read any .py file outside this `verify/` folder (in particular not `mcej/*.py`, `gold/recovery.py`, `fractal/recovery_tol.py`).

## Inputs (this folder)
- `trades_ars.json`: `{account: {exitR, cap, trades: [{entry, exit, R, c, sd, price}]}}`, 10 accounts (M5-S1 ... M15-S9).
- `trades_grid.json`: `{chart: {account: {...same...}}}`, charts `M5` (S1-S11) and `M15` (S1-S9, S11).
- Trades are in time order; within one account they never overlap. Times are IST, ISO strings.
- `R` = result in R (multiples of the stop distance), `c` = cost in R, `sd` = stop distance (price), `price` = entry price.

## Workbooks (recalculated; read with openpyxl `data_only=True`)
- `../out/Gold_Monthly_Crooks_EJ_Auction_Retest.xlsx`: one sheet per account, named like the account (`M5-S2`, ...).
- `../out/Gold_Monthly_Crooks_EJ_Fractal_Grid.xlsx`: sheets `M5 chart`, `M15 chart` = all strategies of that chart added up.
- Column order E..AI (31 settings): E = Crooks E (no ladder); F..K = Crooks F with level Off, Low, Medium, High, Extra high, Max;
  L..Q = Crooks G (same 6 levels); R..W = Crooks H; X..AC = Crooks I; AD..AI = Crooks J.
- Block 1 = rows 8..77 = months Jan 2021 .. Oct 2026 (70 months; column A holds the month as a date): profit/loss of the month,
  ONE ACCOUNT running from the first trade, each trade counted in the IST calendar month of its EXIT time.
- Block 5 = 70 month rows starting 4 rows below the row whose column A text starts with `5. Each month ON ITS OWN`:
  EACH MONTH ALONE: for every month, only the trades whose ENTRY time is in that month, a fresh account and fresh state.
- Grid sheets: each value = the sum over that chart's strategies, each strategy simulated as its own account.
- Sheet `Ladder target test` (Auction Retest workbook): total profit of one account over all trades with other ladder targets.

## Money rules (one account)
Constants: start balance 10,000; base b = 50; leverage limit 100; Crooks F/I multiple 3; G multiple 10; H 1 %; J multiple 20;
ladder target T = 1,000 (unless the target-test sheet says otherwise); hard cap = the account's `cap` (0 = none; grid 500, clamp).
Per trade: `levk = 100 * sd * (1 + c) / price` and `rmin = sd * (1 + c)` (the $ risk of 0.01 lot = 1 oz).
Ladder levels (lam, phi, bmax, gam): Low (0.8, 0.10, 2, 0.25); Medium (0.7, 0.15, 3, 0.30); High (0.6, 0.20, 5, 0.35);
Extra high (0.5, 0.25, 8, 0.40); Max (0.4, 0.30, 12, 0.50). Off = no ladder. Crooks E never uses the ladder.

State: eq = 10,000; net = 0; peakNet = 0; crL = 0 (the $ loss to win back); crW = False (the previous trade won); ruined = False.
For each trade in order:
1. If ruined: stop (no more trades for this account).
2. recovery = crW and crL > 0.
3. plain(B): if recovery: x = max(B, crL / exitR); then F or I: x = min(x, 3B); H: x = min(x, max(B, 0.01 * eq));
   J: x = max(B, x * max(0, 1 - (peakNet - net) / (20B))). Else if crL > 0 and the rule is E or I: x = min(B, rmin). Else x = B.
4. r = plain(b).
5. Ladder (rule F, G, H, I or J, level not Off) and peakNet >= T: C = max(0, net - lam * peakNet); B = b + min((bmax - 1) b, phi * C);
   r = min(plain(B), r + gam * C); then if net <= 0: r = min(b, rmin)   (the "start guard").
6. If cap > 0 and r > cap: r = cap.   7. If eq > 0: r = min(r, eq * levk).
8. pnl = r * (R - c) / (1 + c); eq += pnl; net += pnl; peakNet = max(peakNet, net); if eq <= 0: ruined = True.
9. crL = max(0, crL - pnl). If the rule is G: B2 = (ladder applies and peakNet >= T) ? b + min((bmax - 1) b, phi * max(0, net - lam * peakNet)) : b
   (using the UPDATED net and peakNet); crL = min(crL, 10 * B2). If crL < 0.01: crL = 0.
10. crW = pnl > 0.

## What to check (tolerance $0.01 per cell)
1. Auction Retest `M5-S2` and `M15-S7`: block 1, all 31 settings x 70 months.
2. Auction Retest `M5-S1`: block 5, all 31 settings x 70 months.
3. Grid `M5 chart`: block 1, all 31 settings x 70 months (sum of S1..S11).
4. Grid `M15 chart`: block 5 for settings F..K (Crooks F, all levels) x 70 months.
5. `Ladder target test`: the rows of M5-S2 and M15-S1 for Crooks F (all 4 targets x 5 levels + the Off column D).

Write your code and a progress file `indep/progress.md` (update it after each step) in `verify/indep/`. Report: per check, the number of
cells compared, the number above $0.01, the largest difference, and the first few mismatches (sheet, cell, workbook value, yours).
