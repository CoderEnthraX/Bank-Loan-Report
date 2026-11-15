# Independent check 2: monthly money results, "your settings" workbooks

Recompute sample results from the raw trade lists using ONLY this spec, and compare them with the two workbooks.
Do NOT read any .py file outside this `verify/` folder (in particular not `mcej*/*.py`, `gold/recovery.py`).

## Inputs (this folder)
- `trades_user.json`: `{"TF|setup|TPn": {exitR, cap, trades: [{entry, exit, R, c, rp, lim}]}}`, 8 runs: TF M5 / M15, setup `off` / `on`, TP1 / TP2.
  Trades are in time order and never overlap. Times are IST, ISO strings. `R` = result in R, `c` = cost in R, `rp` = stop distance (price),
  `lim` = limit price.
- Workbooks (recalculated; openpyxl `data_only=True`): `../out/Gold_Monthly_YourSettings_1_AllFiltersOff.xlsx` (setup `off`) and
  `../out/Gold_Monthly_YourSettings_2_YourFilters.xlsx` (setup `on`); sheets `M5 TP1`, `M5 TP2`, `M15 TP1`, `M15 TP2`.
- Column order E..AJ (32 settings): E = No recovery (fixed $50); F = Crooks E (no ladder); G..L = Crooks F with level Off, Low, Medium,
  High, Extra high, Max; M..R = Crooks G; S..X = Crooks H; Y..AD = Crooks I; AE..AJ = Crooks J.
- Block 1 = rows 8..77 = months Jan 2021 .. Oct 2026 (column A holds the month as a date): ONE ACCOUNT from the first trade, each trade
  counted in the IST calendar month of its EXIT time.
- Block 5 = 70 rows starting 4 rows below the row whose column A text starts with `5. Each month ON ITS OWN`: for every month only the
  trades whose ENTRY time is in that month, a fresh account and fresh state.

## Money rules (one account)
Start balance 10,000; base b = 50; cap = 0 (none); ladder target T = 1,000; Crooks F/I multiple 3; G multiple 10; H 1 %; J multiple 20.
Per trade: `levk = 100 * (rp + 0.23) / lim` (leverage limit per $ of balance) and `rmin = rp + 0.23` (the $ risk of 0.01 lot = 1 oz).
Ladder levels (lam, phi, bmax, gam): Low (0.8, 0.10, 2, 0.25); Medium (0.7, 0.15, 3, 0.30); High (0.6, 0.20, 5, 0.35);
Extra high (0.5, 0.25, 8, 0.40); Max (0.4, 0.30, 12, 0.50). Off = no ladder. No recovery and Crooks E never use the ladder.
State: eq = 10,000; net = 0; peakNet = 0; crL = 0; crW = False; ruined = False. For each trade in order:
1. If ruined: stop.
2. No recovery: r = b. Otherwise: recovery = crW and crL > 0; plain(B): if recovery: x = max(B, crL / exitR); F or I: x = min(x, 3B);
   H: x = min(x, max(B, 0.01 * eq)); J: x = max(B, x * max(0, 1 - (peakNet - net) / (20B))). Else if crL > 0 and the rule is E or I:
   x = min(B, rmin). Else x = B. r = plain(b).
3. Ladder (rules F-J, level not Off) and peakNet >= T: C = max(0, net - lam * peakNet); B = b + min((bmax - 1) b, phi * C);
   r = min(plain(B), r + gam * C); then if net <= 0: r = min(b, rmin).
4. If eq > 0: r = min(r, eq * levk).
5. pnl = r * (R - c) / (1 + c); eq += pnl; net += pnl; peakNet = max(peakNet, net); if eq <= 0: ruined = True.
6. crL = max(0, crL - pnl). Rule G: B2 = (ladder applies and peakNet >= T) ? b + min((bmax - 1) b, phi * max(0, net - lam * peakNet)) : b
   (UPDATED net / peakNet); crL = min(crL, 10 * B2). If crL < 0.01: crL = 0.   7. crW = pnl > 0.

## What to check (tolerance $0.01 per cell)
1. `off` workbook, sheet `M15 TP2`: block 1, all 32 settings x 70 months.
2. `on` workbook, sheets `M5 TP1` and `M15 TP1`: block 1, all 32 settings x 70 months.
3. `on` workbook, sheet `M5 TP2`: block 5, all 32 settings x 70 months.
Write your code and a progress file `indep2/progress.md` (update after each step) in `verify/indep2/`. Report per check: cells compared, cells
above $0.01, largest difference, and up to 5 mismatches (sheet, cell, workbook value, yours).
