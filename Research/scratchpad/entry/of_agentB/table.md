| # | family | variant | TF | n/mo (train) | train L | train S | valid L | valid S | placebo-adj train L/S | placebo-adj valid L/S | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | F1 absorption | F1 absorb pVA mkt atr | M15 | 2.4 | +2.7 | -4.3 | -11.5 | +7.2 | +0.7 / -4.4 | -5.0 / +10.8 | FAIL ; few trades |
| 2 | F1 absorption | F1 absorb pVA mkt struct | M15 | 2.4 | -9.2 | -3.0 | -9.5 | +1.3 | -11.1 / -3.7 | -12.0 / -5.9 | FAIL ; few trades |
| 3 | F1 absorption | F1 absorb pVA stp atr | M15 | 1.8 | -0.3 | +0.8 | -7.4 | +7.2 | -4.3 / -5.3 | -5.4 / +13.8 | FAIL ; few trades |
| 4 | F1 absorption | F1 absorb pVA stp struct | M15 | 1.8 | -5.7 | -2.9 | -1.9 | +1.8 | -6.1 / -7.6 | -7.2 / -2.2 | FAIL ; few trades |
| 5 | F1 absorption | F1 absorb pVA +opp.delta mkt atr | M15 | 0.5 | +13.8 | +0.8 | +12.0 | -17.8 | +4.2 / +7.4 | +1.0 / -11.1 | FAIL ; few trades |
| 6 | F1 absorption | F1 absorb pVA +opp.delta mkt struct | M15 | 0.5 | -1.2 | -1.9 | +18.3 | -9.5 | -3.3 / -2.8 | +13.5 / +2.8 | FAIL ; few trades |
| 7 | F1 absorption | F1 absorb pVA +opp.delta stp atr | M15 | 0.4 | +25.2 | +0.1 | +8.9 | -17.8 | +0.4 / +1.7 | +1.9 / +18.8 | FAIL ; few trades |
| 8 | F1 absorption | F1 absorb pVA +opp.delta stp struct | M15 | 0.4 | +21.6 | -7.1 | +12.0 | +7.2 | +10.0 / -1.5 | +7.5 / +28.1 | FAIL ; few trades |
| 9 | F1 absorption | F1 absorb dVA mkt atr | M15 | 2.7 | -11.1 | -11.9 | -12.3 | -0.2 | -14.6 / -8.6 | -8.6 / -0.0 | FAIL ; few trades |
| 10 | F1 absorption | F1 absorb dVA mkt struct | M15 | 2.7 | +0.8 | -3.8 | -7.0 | +10.1 | -1.8 / -1.8 | -2.6 / +12.5 | FAIL ; few trades |
| 11 | F1 absorption | F1 absorb dVA stp atr | M15 | 2.1 | -8.7 | -8.4 | -7.5 | +1.3 | -12.2 / -3.1 | -4.2 / -6.8 | FAIL ; few trades |
| 12 | F1 absorption | F1 absorb dVA stp struct | M15 | 2.1 | -0.9 | -5.9 | -10.6 | +8.0 | -2.9 / -5.4 | -6.8 / +1.5 | FAIL ; few trades |
| 13 | F1 absorption | F1 absorb dVA +opp.delta mkt atr | M15 | 0.6 | -16.8 | -0.5 | -22.7 | -3.2 | -20.6 / -11.1 | -24.1 / -9.7 | FAIL ; few trades |
| 14 | F1 absorption | F1 absorb dVA +opp.delta mkt struct | M15 | 0.6 | +0.8 | -17.2 | -8.8 | -9.5 | -10.3 / -16.7 | +6.5 / -6.2 | FAIL ; few trades |
| 15 | F1 absorption | F1 absorb dVA +opp.delta stp atr | M15 | 0.5 | -13.5 | +16.1 | -0.5 | -4.2 | -14.3 / -6.2 | -13.2 / -7.9 | FAIL ; few trades |
| 16 | F1 absorption | F1 absorb dVA +opp.delta stp struct | M15 | 0.5 | +7.6 | -2.6 | +9.5 | -20.1 | -9.0 / -4.2 | -1.8 / -17.8 | FAIL ; few trades |
| 17 | F2 failed auction | F2 failVA mkt atr | M15 | 62.5 | -1.9 | -2.0 | -2.0 | +2.2 | -2.4 / -2.8 | -2.8 / +1.2 | FAIL |
| 18 | F2 failed auction | F2 failVA mkt struct | M15 | 62.5 | -2.5 | -1.6 | -1.2 | +3.5 | -3.6 / -2.2 | -2.8 / +2.6 | FAIL |
| 19 | F2 failed auction | F2 failVA stp atr | M15 | 44.5 | -1.2 | -0.4 | -0.1 | +2.9 | -2.2 / -1.2 | -0.8 / +2.7 | FAIL |
| 20 | F2 failed auction | F2 failVA stp struct | M15 | 44.5 | -0.7 | -1.9 | -0.1 | +5.2 | -1.5 / -2.3 | -1.1 / +4.2 | FAIL |
| 21 | F2 failed auction | F2 failVA accepted mkt atr | M15 | 43.7 | -1.8 | -2.2 | -1.3 | +3.9 | -2.1 / -3.4 | +2.3 / +2.5 | FAIL |
| 22 | F2 failed auction | F2 failVA accepted mkt struct | M15 | 43.7 | -2.3 | -2.6 | -1.3 | +4.5 | -2.7 / -4.1 | +2.8 / +3.5 | FAIL |
| 23 | F2 failed auction | F2 failVA accepted stp atr | M15 | 33.3 | -1.9 | +0.5 | -2.4 | +4.1 | -3.7 / +0.1 | -0.3 / +1.7 | FAIL |
| 24 | F2 failed auction | F2 failVA accepted stp struct | M15 | 33.3 | -2.0 | -1.1 | -3.6 | +4.8 | -2.8 / -1.5 | -1.2 / +3.6 | FAIL |
| 25 | F2 80% rule | F2 80pct sess mkt atr | M15 | 6.8 | -3.4 | +0.2 | +0.0 | +2.2 | +0.7 / +1.7 | +5.7 / -3.3 | FAIL ; few trades |
| 26 | F2 80% rule | F2 80pct sess mkt struct | M15 | 6.8 | -3.0 | +2.6 | -3.9 | +3.0 | -1.7 / +2.8 | +1.8 / -0.5 | FAIL ; few trades |
| 27 | F2 80% rule | F2 80pct sess stp atr | M15 | 4.5 | -8.7 | +2.1 | +2.0 | -4.8 | -5.8 / +6.0 | +6.5 / -9.1 | FAIL ; few trades |
| 28 | F2 80% rule | F2 80pct sess stp struct | M15 | 4.5 | -3.0 | +1.2 | -2.9 | -2.6 | -2.6 / +2.0 | +1.6 / -4.6 | FAIL ; few trades |
| 29 | F2 80% rule | F2 80pct ny0930 mkt atr | M15 | 4.4 | -1.9 | +0.8 | -2.3 | +9.2 | -1.3 / +0.3 | -6.5 / +2.6 | FAIL ; few trades |
| 30 | F2 80% rule | F2 80pct ny0930 mkt struct | M15 | 4.4 | -2.9 | +1.6 | +1.4 | -2.7 | -1.8 / -0.6 | -3.7 / -1.1 | FAIL ; few trades |
| 31 | F2 80% rule | F2 80pct ny0930 stp atr | M15 | 2.9 | -0.7 | +0.7 | +5.4 | +0.7 | +1.0 / -0.3 | +7.2 / -2.6 | FAIL ; few trades |
| 32 | F2 80% rule | F2 80pct ny0930 stp struct | M15 | 2.9 | -4.0 | +1.9 | -3.4 | -11.3 | -1.7 / -2.0 | -7.0 / -13.7 | FAIL ; few trades |
| 33 | F1 absorption | F1 absorb pVA mkt atr | M5 | 3.7 | -4.0 | -5.3 | -7.5 | +5.5 | -3.0 / -9.5 | -17.6 / +2.1 | FAIL ; few trades |
| 34 | F1 absorption | F1 absorb pVA mkt struct | M5 | 3.7 | +0.5 | -2.1 | -5.4 | +5.5 | +0.3 / -2.4 | -7.4 / +2.7 | FAIL ; few trades |
| 35 | F1 absorption | F1 absorb pVA stp atr | M5 | 3.0 | -1.3 | +0.5 | -2.4 | +11.9 | -0.9 / -4.0 | -3.0 / +8.4 | FAIL ; few trades |
| 36 | F1 absorption | F1 absorb pVA stp struct | M5 | 3.0 | +5.3 | -4.2 | +1.6 | +8.6 | +4.0 / -9.5 | +3.4 / +4.4 | FAIL ; few trades |
| 37 | F1 absorption | F1 absorb pVA +opp.delta mkt atr | M5 | 0.9 | +8.5 | -18.5 | -8.7 | -6.1 | -2.1 / -18.6 | -6.2 / -6.9 | FAIL ; few trades |
| 38 | F1 absorption | F1 absorb pVA +opp.delta mkt struct | M5 | 0.9 | +10.0 | -11.2 | -0.9 | -26.9 | -1.6 / -10.3 | +7.3 / -30.6 | FAIL ; few trades |
| 39 | F1 absorption | F1 absorb pVA +opp.delta stp atr | M5 | 0.8 | +5.5 | -7.2 | -3.9 | -10.2 | +3.5 / -3.2 | +0.6 / -20.5 | FAIL ; few trades |
| 40 | F1 absorption | F1 absorb pVA +opp.delta stp struct | M5 | 0.8 | +12.7 | -19.7 | +7.5 | -10.2 | +7.8 / -15.7 | +12.6 / -20.5 | FAIL ; few trades |
| 41 | F1 absorption | F1 absorb dVA mkt atr | M5 | 6.0 | -2.2 | -1.2 | -9.7 | +1.1 | -0.4 / -1.8 | -7.8 / -1.5 | FAIL ; few trades |
| 42 | F1 absorption | F1 absorb dVA mkt struct | M5 | 6.0 | -0.6 | -6.0 | -7.0 | -7.4 | -0.2 / -5.0 | -7.4 / -14.4 | FAIL ; few trades |
| 43 | F1 absorption | F1 absorb dVA stp atr | M5 | 4.7 | -1.6 | +2.4 | -10.1 | +5.5 | +0.7 / +1.3 | -9.9 / +1.4 | FAIL ; few trades |
| 44 | F1 absorption | F1 absorb dVA stp struct | M5 | 4.7 | +3.0 | +4.3 | -5.7 | -1.7 | +5.5 / +2.3 | -7.5 / -6.3 | FAIL ; few trades |
| 45 | F1 absorption | F1 absorb dVA +opp.delta mkt atr | M5 | 1.7 | -7.2 | -7.2 | -17.4 | +24.3 | -2.0 / -4.4 | -14.3 / +28.0 | FAIL ; few trades |
| 46 | F1 absorption | F1 absorb dVA +opp.delta mkt struct | M5 | 1.7 | -1.1 | -10.8 | -17.4 | +2.9 | -1.8 / -14.7 | -4.2 / -1.8 | FAIL ; few trades |
| 47 | F1 absorption | F1 absorb dVA +opp.delta stp atr | M5 | 1.4 | -11.2 | -5.4 | -4.4 | +29.5 | -6.0 / +1.3 | -6.4 / +22.2 | FAIL ; few trades |
| 48 | F1 absorption | F1 absorb dVA +opp.delta stp struct | M5 | 1.4 | -0.5 | -7.2 | -6.0 | +8.4 | -0.0 / -9.2 | -4.6 / -6.4 | FAIL ; few trades |
| 49 | F2 failed auction | F2 failVA mkt atr | M5 | 78.2 | -0.5 | -2.0 | +0.9 | +2.9 | +0.8 / -1.6 | +0.5 / +0.9 | FAIL |
| 50 | F2 failed auction | F2 failVA mkt struct | M5 | 78.2 | -0.5 | -1.6 | -0.2 | +3.3 | +0.4 / -1.7 | +0.3 / +0.4 | FAIL |
| 51 | F2 failed auction | F2 failVA stp atr | M5 | 56.7 | +1.2 | -0.6 | -0.9 | +4.2 | +1.2 / -0.8 | -0.4 / +1.8 | FAIL |
| 52 | F2 failed auction | F2 failVA stp struct | M5 | 56.7 | +0.9 | -0.2 | -0.4 | +5.1 | +0.9 / -0.7 | +0.7 / +2.9 | FAIL |
| 53 | F2 failed auction | F2 failVA accepted mkt atr | M5 | 64.0 | -1.7 | -1.5 | +3.0 | +3.8 | -1.9 / -1.3 | +3.8 / +4.8 | FAIL |
| 54 | F2 failed auction | F2 failVA accepted mkt struct | M5 | 64.0 | -1.0 | -0.9 | +2.4 | +4.7 | -1.3 / -1.0 | +3.7 / +5.8 | FAIL |
| 55 | F2 failed auction | F2 failVA accepted stp atr | M5 | 49.2 | +1.0 | +0.2 | +0.6 | +5.1 | +1.0 / -0.4 | -0.1 / +5.8 | all 4 > 0, pooled z 1.4 |
| 56 | F2 failed auction | F2 failVA accepted stp struct | M5 | 49.2 | +1.1 | +1.0 | +1.4 | +5.7 | +0.7 / -0.2 | +0.5 / +6.4 | all 4 > 0, pooled z 1.9 |
| 57 | F2 80% rule | F2 80pct sess mkt atr | M5 | 6.6 | +0.8 | +1.1 | +2.6 | +4.0 | +4.5 / +0.2 | +2.8 / -1.6 | all 4 > 0, pooled z 0.6 ; few trades |
| 58 | F2 80% rule | F2 80pct sess mkt struct | M5 | 6.6 | -4.4 | +3.3 | +4.6 | -0.8 | -0.0 / +4.7 | +5.0 / -6.6 | FAIL ; few trades |
| 59 | F2 80% rule | F2 80pct sess stp atr | M5 | 4.3 | -2.5 | +1.0 | +0.6 | -6.7 | -4.9 / -4.7 | +3.8 / -10.5 | FAIL ; few trades |
| 60 | F2 80% rule | F2 80pct sess stp struct | M5 | 4.3 | -0.8 | +0.7 | +6.1 | -4.3 | +0.3 / -0.3 | +9.3 / -12.1 | FAIL ; few trades |
| 61 | F2 80% rule | F2 80pct ny0930 mkt atr | M5 | 4.1 | -4.4 | +2.9 | -0.4 | +4.2 | -7.3 / +1.0 | +4.7 / +4.7 | FAIL ; few trades |
| 62 | F2 80% rule | F2 80pct ny0930 mkt struct | M5 | 4.1 | -2.2 | +0.8 | +3.6 | -0.2 | -6.0 / -2.2 | +9.0 / +0.5 | FAIL ; few trades |
| 63 | F2 80% rule | F2 80pct ny0930 stp atr | M5 | 2.4 | -12.3 | +3.0 | +1.9 | +6.4 | -16.1 / +4.8 | +0.7 / +3.6 | FAIL ; few trades |
| 64 | F2 80% rule | F2 80pct ny0930 stp struct | M5 | 2.4 | -4.0 | +1.4 | +4.4 | +1.4 | -8.8 / +2.6 | +3.8 / -2.2 | FAIL ; few trades |
| 65 | F1 absorption | F1b absorbL pVA mkt atr | M15 | 12.4 | +5.1 | -1.0 | -3.9 | +5.6 | +5.7 / +2.0 | -1.1 / +3.2 | FAIL |
| 66 | F1 absorption | F1b absorbL pVA mkt struct | M15 | 12.4 | +1.8 | -4.0 | -0.5 | +3.8 | +1.8 / -1.5 | +2.8 / +2.2 | FAIL |
| 67 | F1 absorption | F1b absorbL pVA stp atr | M15 | 9.7 | +7.1 | +0.6 | -1.2 | +3.5 | +9.0 / +1.8 | +3.7 / +0.5 | FAIL |
| 68 | F1 absorption | F1b absorbL pVA stp struct | M15 | 9.7 | +2.6 | -3.2 | -0.5 | +6.6 | +5.0 / -3.1 | +4.0 / +5.9 | FAIL |
| 69 | F1 absorption | F1b absorbL dVA mkt atr | M15 | 17.9 | -2.4 | -2.8 | -4.7 | +3.1 | -2.5 / -4.4 | -3.9 / +3.6 | FAIL |
| 70 | F1 absorption | F1b absorbL dVA mkt struct | M15 | 17.9 | -0.4 | -1.4 | -3.9 | +3.4 | +0.2 / -1.4 | -3.6 / +2.7 | FAIL |
| 71 | F1 absorption | F1b absorbL dVA stp atr | M15 | 13.9 | -3.0 | -1.2 | -2.8 | +2.1 | -3.1 / -1.5 | -1.3 / +0.7 | FAIL |
| 72 | F1 absorption | F1b absorbL dVA stp struct | M15 | 13.9 | -2.8 | +0.2 | -2.8 | +3.5 | -1.9 / -1.2 | -2.8 / +2.4 | FAIL |
| 73 | F3 LVN/HVN | F3 brk12 LVN ahead mkt atr | M15 | 66.4 | -1.5 | +0.3 | +0.4 | +5.6 | -0.6 / -0.8 | +1.4 / +3.9 | FAIL |
| 74 | F3 LVN/HVN | F3 brk12 LVN ahead mkt struct | M15 | 66.4 | -2.4 | -0.5 | -2.2 | +1.7 | -1.3 / -1.5 | +0.4 / -1.2 | FAIL |
| 75 | F3 LVN/HVN | F3 brk12 LVN ahead stp atr | M15 | 50.8 | -2.2 | -1.5 | -1.3 | +4.2 | -1.3 / -3.1 | -1.5 / +1.5 | FAIL |
| 76 | F3 LVN/HVN | F3 brk12 LVN ahead stp struct | M15 | 50.8 | -0.6 | -1.0 | +0.7 | +2.6 | +0.4 / -3.2 | +1.1 / +0.5 | FAIL |
| 77 | F3 LVN/HVN | F3 brk12 HVN ahead mkt atr | M15 | 55.4 | +1.8 | -2.2 | -1.4 | +1.2 | +2.4 / -1.6 | -0.0 / +1.5 | FAIL |
| 78 | F3 LVN/HVN | F3 brk12 HVN ahead mkt struct | M15 | 55.4 | +0.3 | -3.0 | -2.6 | +2.5 | +0.2 / -2.1 | -2.3 / +2.9 | FAIL |
| 79 | F3 LVN/HVN | F3 brk12 HVN ahead stp atr | M15 | 42.8 | +1.7 | -3.2 | +1.1 | +1.8 | +2.4 / -3.2 | +3.9 / +1.3 | FAIL |
| 80 | F3 LVN/HVN | F3 brk12 HVN ahead stp struct | M15 | 42.8 | -0.5 | -3.5 | -1.7 | +1.8 | +0.8 / -2.9 | -0.6 / +1.8 | FAIL |
| 81 | F3 LVN/HVN | F3 brk12 all mkt atr | M15 | 168.2 | -0.3 | -1.3 | -0.6 | +1.5 | +0.2 / -1.8 | -0.4 / +1.2 | FAIL |
| 82 | F3 LVN/HVN | F3 brk12 all mkt struct | M15 | 168.2 | -1.4 | -2.1 | -3.6 | +1.4 | -1.0 / -2.9 | -2.0 / -0.4 | FAIL |
| 83 | F3 LVN/HVN | F3 brk12 all stp atr | M15 | 129.7 | -0.5 | -2.5 | +0.1 | +0.5 | +0.1 / -3.4 | -0.3 / -0.3 | FAIL |
| 84 | F3 LVN/HVN | F3 brk12 all stp struct | M15 | 129.7 | -0.8 | -2.4 | -0.9 | +0.3 | -0.4 / -4.0 | -0.7 / -1.4 | FAIL |
| 85 | F3 LVN/HVN | F3 LVN reject mkt atr | M15 | 4.6 | -0.7 | -1.2 | +4.0 | -1.5 | +0.7 / +0.0 | +7.3 / +7.7 | FAIL ; few trades |
| 86 | F3 LVN/HVN | F3 LVN reject mkt struct | M15 | 4.6 | -6.6 | +1.2 | +1.7 | +7.2 | -5.3 / -0.3 | +6.4 / +16.0 | FAIL ; few trades |
| 87 | F3 LVN/HVN | F3 LVN reject stp atr | M15 | 3.6 | +6.2 | -3.5 | +0.5 | +6.0 | +7.7 / -4.8 | +4.7 / +15.9 | FAIL ; few trades |
| 88 | F3 LVN/HVN | F3 LVN reject stp struct | M15 | 3.6 | +1.3 | -0.7 | -0.5 | +7.2 | +3.5 / -4.2 | +5.5 / +17.9 | FAIL ; few trades |
| 89 | F3 LVN/HVN | F3 HVN hold mkt atr | M15 | 36.5 | +2.4 | -1.2 | -6.6 | -0.3 | +2.2 / -2.8 | -5.9 / -0.4 | FAIL |
| 90 | F3 LVN/HVN | F3 HVN hold mkt struct | M15 | 36.5 | +0.0 | -1.1 | -7.3 | +0.9 | -0.2 / -1.8 | -5.3 / +1.5 | FAIL |
| 91 | F3 LVN/HVN | F3 HVN hold stp atr | M15 | 29.3 | +3.8 | +0.3 | -6.5 | +1.6 | +3.1 / -1.2 | -5.4 / +1.7 | FAIL |
| 92 | F3 LVN/HVN | F3 HVN hold stp struct | M15 | 29.3 | +1.0 | +1.3 | -5.4 | -0.2 | -0.6 / -0.9 | -4.3 / +0.2 | FAIL |
| 93 | F3 LVN/HVN | F3 nonHVN hold (ctrl) mkt atr | M15 | 108.4 | -1.5 | -1.3 | -0.2 | -1.2 | -1.2 / -1.7 | +0.7 / -1.8 | FAIL |
| 94 | F3 LVN/HVN | F3 nonHVN hold (ctrl) mkt struct | M15 | 108.4 | -2.0 | -1.0 | -2.0 | +0.3 | -1.8 / -1.2 | +0.3 / -0.8 | FAIL |
| 95 | F3 LVN/HVN | F3 nonHVN hold (ctrl) stp atr | M15 | 87.8 | -1.7 | -0.1 | -0.2 | -0.7 | -0.9 / -0.3 | +1.1 / -1.2 | FAIL |
| 96 | F3 LVN/HVN | F3 nonHVN hold (ctrl) stp struct | M15 | 87.8 | -0.7 | +0.6 | -1.4 | -0.1 | -1.3 / +0.7 | +0.7 / -0.6 | FAIL |
| 97 | F1 absorption | F1b absorbL pVA mkt atr | M5 | 20.1 | -0.2 | -3.2 | +2.4 | +6.0 | -2.0 / -4.8 | +1.3 / +7.3 | FAIL |
| 98 | F1 absorption | F1b absorbL pVA mkt struct | M5 | 20.1 | +0.2 | -0.7 | +0.5 | +6.4 | -0.5 / -2.5 | +1.1 / +5.6 | FAIL |
| 99 | F1 absorption | F1b absorbL pVA stp atr | M5 | 14.9 | +0.0 | -1.1 | +3.7 | +7.1 | -1.9 / -4.6 | +2.0 / +8.3 | FAIL ; few trades |
| 100 | F1 absorption | F1b absorbL pVA stp struct | M5 | 14.9 | -0.7 | -1.2 | +2.6 | +6.1 | -1.6 / -4.6 | +1.9 / +5.3 | FAIL ; few trades |
| 101 | F1 absorption | F1b absorbL dVA mkt atr | M5 | 34.0 | -1.5 | -0.5 | -2.0 | +2.3 | -1.5 / -0.9 | -2.0 / +2.6 | FAIL |
| 102 | F1 absorption | F1b absorbL dVA mkt struct | M5 | 34.0 | +0.6 | -1.7 | -2.1 | +3.1 | +0.9 / -0.9 | -1.7 / +1.8 | FAIL |
| 103 | F1 absorption | F1b absorbL dVA stp atr | M5 | 25.9 | +0.3 | -1.4 | -0.2 | +4.9 | -0.6 / -2.8 | +0.1 / +3.3 | FAIL |
| 104 | F1 absorption | F1b absorbL dVA stp struct | M5 | 25.9 | +3.1 | -0.0 | +2.1 | +5.8 | +2.3 / -0.8 | +1.3 / +4.1 | FAIL |
| 105 | F3 LVN/HVN | F3 brk12 LVN ahead mkt atr | M5 | 130.3 | -1.0 | -2.3 | -0.1 | +0.4 | -0.4 / -2.2 | +0.2 / -0.3 | FAIL |
| 106 | F3 LVN/HVN | F3 brk12 LVN ahead mkt struct | M5 | 130.3 | -1.6 | -1.9 | -1.6 | +1.2 | -0.7 / -2.0 | +0.2 / -1.1 | FAIL |
| 107 | F3 LVN/HVN | F3 brk12 LVN ahead stp atr | M5 | 99.8 | +0.5 | -1.4 | -0.6 | +1.3 | +0.3 / -1.9 | -0.9 / +0.3 | FAIL |
| 108 | F3 LVN/HVN | F3 brk12 LVN ahead stp struct | M5 | 99.8 | +0.0 | -0.5 | -0.9 | +1.6 | +0.6 / -1.6 | -0.8 / -1.0 | FAIL |
| 109 | F3 LVN/HVN | F3 brk12 HVN ahead mkt atr | M5 | 126.9 | -0.9 | -2.0 | +0.3 | +3.5 | -1.6 / -1.6 | +0.2 / +2.5 | FAIL |
| 110 | F3 LVN/HVN | F3 brk12 HVN ahead mkt struct | M5 | 126.9 | -1.1 | -2.7 | -1.9 | +4.4 | -0.9 / -2.1 | -1.2 / +2.2 | FAIL |
| 111 | F3 LVN/HVN | F3 brk12 HVN ahead stp atr | M5 | 97.1 | +1.0 | -1.6 | +0.2 | +5.2 | +0.0 / -1.5 | -0.9 / +2.9 | FAIL |
| 112 | F3 LVN/HVN | F3 brk12 HVN ahead stp struct | M5 | 97.1 | +1.7 | -0.5 | +0.2 | +6.1 | +0.5 / -0.8 | -0.7 / +3.6 | FAIL |
| 113 | F3 LVN/HVN | F3 brk12 all mkt atr | M5 | 357.6 | -0.6 | -2.2 | -0.5 | +1.1 | -0.2 / -2.5 | -0.2 / +1.2 | FAIL |
| 114 | F3 LVN/HVN | F3 brk12 all mkt struct | M5 | 357.6 | -0.9 | -2.2 | -1.8 | +1.9 | -0.5 / -2.4 | +0.0 / +0.9 | FAIL |
| 115 | F3 LVN/HVN | F3 brk12 all stp atr | M5 | 274.7 | +1.2 | -1.4 | -0.4 | +2.2 | +0.9 / -2.4 | -1.1 / +1.6 | FAIL |
| 116 | F3 LVN/HVN | F3 brk12 all stp struct | M5 | 274.7 | +1.2 | -0.7 | -0.6 | +2.5 | +1.3 / -1.8 | -0.8 / +0.8 | FAIL |
| 117 | F3 LVN/HVN | F3 LVN reject mkt atr | M5 | 3.5 | -4.2 | -3.3 | -0.9 | +2.9 | -2.3 / -8.2 | +5.6 / +4.8 | FAIL ; few trades |
| 118 | F3 LVN/HVN | F3 LVN reject mkt struct | M5 | 3.5 | -7.7 | -7.4 | -0.1 | -4.3 | -8.0 / -11.1 | +4.8 / -6.3 | FAIL ; few trades |
| 119 | F3 LVN/HVN | F3 LVN reject stp atr | M5 | 2.8 | -9.4 | -3.0 | -11.4 | -5.3 | -8.9 / -6.7 | -2.9 / -10.2 | FAIL ; few trades |
| 120 | F3 LVN/HVN | F3 LVN reject stp struct | M5 | 2.8 | -12.0 | -4.2 | -8.0 | -5.3 | -12.1 / -8.5 | +0.3 / -10.2 | FAIL ; few trades |
| 121 | F3 LVN/HVN | F3 HVN hold mkt atr | M5 | 97.6 | -0.4 | +0.5 | -2.3 | +1.5 | -0.0 / -0.2 | -2.7 / -0.3 | FAIL |
| 122 | F3 LVN/HVN | F3 HVN hold mkt struct | M5 | 97.6 | -1.0 | -0.2 | -5.3 | +2.6 | -0.6 / -0.3 | -2.6 / +0.8 | FAIL |
| 123 | F3 LVN/HVN | F3 HVN hold stp atr | M5 | 80.3 | +0.7 | +1.9 | -1.7 | +1.1 | +0.8 / +1.0 | -2.9 / -0.5 | FAIL |
| 124 | F3 LVN/HVN | F3 HVN hold stp struct | M5 | 80.3 | +0.2 | +2.3 | -3.9 | +1.8 | +0.1 / +1.9 | -3.6 / -1.1 | FAIL |
| 125 | F3 LVN/HVN | F3 nonHVN hold (ctrl) mkt atr | M5 | 256.5 | +0.4 | +0.9 | -0.4 | -0.4 | +1.0 / +1.2 | -0.4 / -0.2 | FAIL |
| 126 | F3 LVN/HVN | F3 nonHVN hold (ctrl) mkt struct | M5 | 256.5 | -0.0 | +0.3 | -2.2 | +1.7 | +0.4 / +1.4 | -0.2 / +0.8 | FAIL |
| 127 | F3 LVN/HVN | F3 nonHVN hold (ctrl) stp atr | M5 | 210.3 | +0.9 | +1.9 | +0.8 | +0.7 | +0.8 / +1.4 | -0.0 / -0.2 | all 4 > 0, pooled z 2.5 |
| 128 | F3 LVN/HVN | F3 nonHVN hold (ctrl) stp struct | M5 | 210.3 | +0.5 | +2.6 | -1.0 | +3.0 | -0.0 / +2.0 | -0.6 / +1.1 | FAIL |
| 129 | F4 POC | F4 POCrev dPOC k4.9 mkt atr | M15 | 50.9 | +2.0 | -0.9 | +1.0 | -3.0 | +2.1 / -1.1 | -3.2 / -0.2 | FAIL |
| 130 | F4 POC | F4 POCrev dPOC k4.9 mkt struct | M15 | 50.9 | +1.7 | +0.1 | +0.3 | +1.6 | +2.5 / +0.2 | +1.0 / +1.9 | all 4 > 0, pooled z 1.0 |
| 131 | F4 POC | F4 POCrev dPOC k4.9 stp atr | M15 | 26.6 | +0.6 | -0.2 | +0.4 | -4.3 | -0.5 / -0.3 | -4.0 / +0.3 | FAIL |
| 132 | F4 POC | F4 POCrev dPOC k4.9 stp struct | M15 | 26.6 | +2.9 | -0.0 | +3.3 | -0.4 | +2.9 / +1.6 | -1.4 / +3.0 | FAIL |
| 133 | F4 POC | F4 POCrev dPOC k4.9 +revbar mkt atr | M15 | 24.4 | +3.4 | -1.2 | +0.5 | -10.3 | +3.3 / -1.3 | -0.1 / -5.8 | FAIL |
| 134 | F4 POC | F4 POCrev dPOC k4.9 +revbar mkt struct | M15 | 24.4 | +4.0 | -0.5 | -2.1 | -5.4 | +4.1 / -1.6 | -2.4 / -4.8 | FAIL |
| 135 | F4 POC | F4 POCrev dPOC k4.9 +revbar stp atr | M15 | 19.7 | +2.5 | -2.0 | +3.1 | -11.5 | +2.4 / -2.2 | +1.7 / -7.2 | FAIL |
| 136 | F4 POC | F4 POCrev dPOC k4.9 +revbar stp struct | M15 | 19.7 | +6.4 | -1.2 | +0.9 | -8.0 | +5.9 / -2.9 | -0.7 / -5.2 | FAIL |
| 137 | F4 POC | F4 POCrev pPOC k11.4 mkt atr | M15 | 47.1 | -1.1 | +1.1 | +2.8 | +1.1 | -2.1 / +3.0 | +2.0 / +3.8 | FAIL |
| 138 | F4 POC | F4 POCrev pPOC k11.4 mkt struct | M15 | 47.1 | -4.2 | +2.2 | +0.1 | +5.2 | -3.7 / +4.0 | +0.6 / +6.6 | FAIL |
| 139 | F4 POC | F4 POCrev pPOC k11.4 stp atr | M15 | 27.6 | -1.9 | -1.4 | +6.2 | +0.4 | -2.5 / -0.0 | +4.5 / +3.2 | FAIL |
| 140 | F4 POC | F4 POCrev pPOC k11.4 stp struct | M15 | 27.6 | -3.0 | -1.6 | +2.8 | +4.6 | -1.9 / +0.4 | +2.6 / +6.3 | FAIL |
| 141 | F4 POC | F4 POCrev pPOC k11.4 +revbar mkt atr | M15 | 27.2 | -1.4 | -1.2 | +2.8 | +0.3 | -0.3 / -0.2 | +3.8 / +1.0 | FAIL |
| 142 | F4 POC | F4 POCrev pPOC k11.4 +revbar mkt struct | M15 | 27.2 | -2.0 | -0.9 | +1.8 | +3.4 | -1.7 / -1.5 | +5.8 / +0.6 | FAIL |
| 143 | F4 POC | F4 POCrev pPOC k11.4 +revbar stp atr | M15 | 22.2 | -2.4 | -2.3 | +4.9 | -0.7 | -1.8 / -1.6 | +7.0 / +0.2 | FAIL |
| 144 | F4 POC | F4 POCrev pPOC k11.4 +revbar stp struct | M15 | 22.2 | -0.0 | -2.0 | +2.5 | +0.9 | -0.4 / -2.9 | +5.7 / -0.7 | FAIL |
| 145 | F4 POC | F4 POCmig pullback mkt atr | M15 | 34.7 | -4.8 | -0.8 | -1.6 | -0.9 | -5.5 / +0.2 | -1.5 / -3.7 | FAIL |
| 146 | F4 POC | F4 POCmig pullback mkt struct | M15 | 34.7 | -1.6 | +3.6 | -4.6 | -2.9 | -1.7 / +4.4 | -3.0 / -6.2 | FAIL |
| 147 | F4 POC | F4 POCmig pullback stp atr | M15 | 27.8 | -4.2 | -0.5 | -3.9 | +3.9 | -4.4 / -1.2 | -4.9 / +0.5 | FAIL |
| 148 | F4 POC | F4 POCmig pullback stp struct | M15 | 27.8 | +0.3 | +2.2 | -1.7 | +1.1 | +0.4 / +2.5 | -0.8 / -3.9 | FAIL |
| 149 | F4 POC | F4 POCmig trend mkt atr | M15 | 35.0 | -1.6 | +1.7 | -0.5 | -1.8 | -2.7 / +2.3 | -0.1 / -1.9 | FAIL |
| 150 | F4 POC | F4 POCmig trend stp atr | M15 | 22.3 | -3.3 | +3.1 | -1.4 | +3.0 | -3.7 / +2.8 | -2.6 / -0.1 | FAIL |
| 151 | F5 delta/CVD | F5 CVDdiv tk mkt atr | M15 | 26.8 | -3.2 | +5.2 | -0.6 | +1.7 | -4.1 / +3.6 | +0.8 / -0.9 | FAIL |
| 152 | F5 delta/CVD | F5 CVDdiv tk mkt struct | M15 | 26.8 | -1.2 | +0.2 | -2.6 | +6.1 | -1.2 / -1.7 | -0.1 / +3.5 | FAIL |
| 153 | F5 delta/CVD | F5 CVDdiv tk stp atr | M15 | 12.4 | -2.1 | +3.6 | -2.2 | -5.0 | +0.1 / +3.6 | -2.3 / -7.2 | FAIL |
| 154 | F5 delta/CVD | F5 CVDdiv tk stp struct | M15 | 12.4 | -1.7 | +3.1 | -5.7 | -5.2 | -1.2 / +3.4 | -3.1 / -7.6 | FAIL |
| 155 | F5 delta/CVD | F5 CVDdiv tk +rej mkt atr | M15 | 9.1 | -4.2 | +2.8 | -0.5 | +1.2 | +0.9 / +0.9 | +1.3 / -0.3 | FAIL |
| 156 | F5 delta/CVD | F5 CVDdiv tk +rej mkt struct | M15 | 9.1 | -6.6 | -2.0 | +2.2 | +4.2 | -2.0 / -3.7 | +7.5 / +4.2 | FAIL |
| 157 | F5 delta/CVD | F5 CVDdiv tk +rej stp atr | M15 | 6.3 | -3.5 | +5.9 | -3.4 | -4.2 | -0.6 / +3.3 | -4.2 / -3.6 | FAIL ; few trades |
| 158 | F5 delta/CVD | F5 CVDdiv tk +rej stp struct | M15 | 6.3 | -6.9 | +1.8 | -5.5 | -1.9 | -6.5 / -0.3 | -2.7 / -1.9 | FAIL ; few trades |
| 159 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) mkt atr | M15 | 47.2 | +1.5 | -1.5 | -2.5 | -2.2 | +1.6 / -3.1 | -2.4 / -2.4 | FAIL |
| 160 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) mkt struct | M15 | 47.2 | +1.6 | -0.7 | -6.4 | +1.7 | +2.4 / -1.6 | -2.6 / -0.9 | FAIL |
| 161 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) stp atr | M15 | 18.8 | +2.0 | +1.9 | -2.1 | -0.1 | +1.2 / +1.8 | -3.8 / -1.9 | FAIL |
| 162 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) stp struct | M15 | 18.8 | +1.4 | +2.6 | +2.0 | -0.2 | +1.6 / +2.5 | +0.6 / -3.2 | FAIL |
| 163 | F5 delta/CVD | F5 CVDconfirm follow mkt atr | M15 | 47.2 | +1.0 | -2.5 | +1.9 | +3.2 | +2.6 / -3.3 | +2.5 / +3.2 | FAIL |
| 164 | F5 delta/CVD | F5 CVDconfirm follow mkt struct | M15 | 47.2 | +2.0 | +0.0 | +0.3 | +5.4 | +3.6 / -0.3 | +2.1 / +3.7 | all 4 > 0, pooled z 1.5 |
| 165 | F5 delta/CVD | F5 CVDconfirm follow stp atr | M15 | 32.1 | +0.4 | -2.0 | +2.0 | +4.3 | +2.4 / -2.0 | +1.6 / +4.7 | FAIL |
| 166 | F5 delta/CVD | F5 CVDconfirm follow stp struct | M15 | 32.1 | +2.6 | -0.8 | +2.4 | +3.5 | +4.3 / -0.5 | +2.5 / +2.3 | FAIL |
| 167 | F5 delta/CVD | F5 CVDdiv cl mkt atr | M15 | 33.1 | -1.5 | +3.4 | -1.4 | +3.2 | +1.5 / +3.8 | -0.8 / +2.2 | FAIL |
| 168 | F5 delta/CVD | F5 CVDdiv cl mkt struct | M15 | 33.1 | +2.1 | +0.4 | -3.8 | +2.3 | +4.2 / +0.7 | -1.0 / -0.2 | FAIL |
| 169 | F5 delta/CVD | F5 CVDdiv cl stp atr | M15 | 15.3 | -3.2 | +3.3 | -1.5 | -4.6 | -0.2 / +4.3 | -0.9 / -7.6 | FAIL |
| 170 | F5 delta/CVD | F5 CVDdiv cl stp struct | M15 | 15.3 | -4.1 | +2.9 | +0.6 | -3.3 | -2.6 / +3.0 | +2.9 / -6.2 | FAIL |
| 171 | F5 delta/CVD | F5 CVDdiv cl +rej mkt atr | M15 | 10.6 | +2.1 | +2.6 | +2.4 | +3.2 | +2.4 / +4.2 | +1.5 / -2.1 | all 4 > 0, pooled z 1.2 |
| 172 | F5 delta/CVD | F5 CVDdiv cl +rej mkt struct | M15 | 10.6 | -0.6 | +1.6 | +2.2 | +5.0 | -1.5 / +3.2 | +4.1 / -0.4 | FAIL |
| 173 | F5 delta/CVD | F5 CVDdiv cl +rej stp atr | M15 | 7.7 | +0.3 | +7.5 | +1.4 | +0.7 | +2.2 / +9.9 | +2.1 / -2.8 | all 4 > 0, pooled z 1.2 ; few trades |
| 174 | F5 delta/CVD | F5 CVDdiv cl +rej stp struct | M15 | 7.7 | -1.6 | +2.6 | +4.8 | +1.2 | -2.2 / +4.6 | +7.5 / -7.1 | FAIL ; few trades |
| 175 | F5 delta/CVD | F5 deltaflip after sweep mkt atr | M15 | 12.9 | -2.3 | -1.0 | -6.1 | -5.2 | -1.5 / -0.8 | -3.2 / -4.0 | FAIL |
| 176 | F5 delta/CVD | F5 deltaflip after sweep mkt struct | M15 | 12.9 | -1.9 | -2.3 | -7.3 | -6.0 | -1.3 / -2.8 | -5.3 / -4.8 | FAIL |
| 177 | F5 delta/CVD | F5 deltaflip after sweep stp atr | M15 | 10.1 | -1.4 | -0.3 | -3.7 | -4.5 | -0.5 / -1.0 | -0.4 / -4.1 | FAIL |
| 178 | F5 delta/CVD | F5 deltaflip after sweep stp struct | M15 | 10.1 | -3.2 | -3.0 | -5.3 | -6.1 | -3.3 / -3.0 | -1.2 / -5.0 | FAIL |
| 179 | F5 delta/CVD | F5 climax opp delta mkt atr | M15 | 1.2 | -14.3 | +3.6 | -8.8 | -7.4 | -8.8 / +1.9 | -4.6 / +0.7 | FAIL ; few trades |
| 180 | F5 delta/CVD | F5 climax opp delta mkt struct | M15 | 1.2 | -7.3 | +1.8 | -17.1 | +13.4 | -6.0 / -5.9 | -8.3 / +30.6 | FAIL ; few trades |
| 181 | F5 delta/CVD | F5 climax opp delta stp atr | M15 | 0.9 | -11.6 | +7.8 | +7.9 | -9.5 | -16.2 / +13.7 | +11.9 / -4.2 | FAIL ; few trades |
| 182 | F5 delta/CVD | F5 climax opp delta stp struct | M15 | 0.9 | -15.4 | +3.6 | +7.9 | -12.3 | -14.9 / +3.2 | +8.3 / -14.1 | FAIL ; few trades |
| 183 | F5 delta/CVD | F5 climax aligned delta (ctrl) mkt atr | M15 | 2.4 | -0.1 | +0.7 | +2.4 | -7.4 | -3.1 / -0.6 | -10.6 / -12.8 | FAIL ; few trades |
| 184 | F5 delta/CVD | F5 climax aligned delta (ctrl) mkt struct | M15 | 2.4 | -5.1 | -14.2 | -7.2 | +5.1 | -3.5 / -12.1 | -7.0 / +5.9 | FAIL ; few trades |
| 185 | F5 delta/CVD | F5 climax aligned delta (ctrl) stp atr | M15 | 0.9 | -5.0 | +0.5 | +10.7 | -15.6 | -8.0 / +7.3 | +10.2 / -24.6 | FAIL ; few trades |
| 186 | F5 delta/CVD | F5 climax aligned delta (ctrl) stp struct | M15 | 0.9 | -10.9 | +5.2 | +5.1 | -11.0 | -10.0 / +9.2 | +3.0 / -17.3 | FAIL ; few trades |
| 187 | F5 delta/CVD | F5 IBbrk CVD agree mkt atr | M15 | 15.2 | -1.6 | +1.0 | +2.7 | -4.0 | +1.7 / -0.2 | +4.5 / +0.3 | FAIL |
| 188 | F5 delta/CVD | F5 IBbrk CVD agree mkt struct | M15 | 15.2 | +0.7 | -1.8 | -2.0 | -5.3 | +3.9 / -2.1 | +0.1 / -0.6 | FAIL |
| 189 | F5 delta/CVD | F5 IBbrk CVD agree stp atr | M15 | 11.5 | +2.0 | -0.5 | -0.5 | -5.9 | +5.6 / -1.9 | +1.3 / -2.1 | FAIL |
| 190 | F5 delta/CVD | F5 IBbrk CVD agree stp struct | M15 | 11.5 | +1.2 | -1.9 | -2.7 | -9.0 | +4.5 / -1.7 | -2.0 / -4.0 | FAIL |
| 191 | F5 delta/CVD | F5 IBbrk CVD disagree mkt atr | M15 | 3.3 | -2.7 | -0.1 | +6.9 | +5.6 | -5.9 / +1.2 | +10.5 / +10.4 | FAIL ; few trades |
| 192 | F5 delta/CVD | F5 IBbrk CVD disagree mkt struct | M15 | 3.3 | -6.1 | -4.3 | +4.2 | +11.1 | -9.6 / +1.0 | +5.9 / +16.7 | FAIL ; few trades |
| 193 | F5 delta/CVD | F5 IBbrk CVD disagree stp atr | M15 | 2.6 | -5.3 | +2.0 | -1.7 | +8.2 | -11.7 / +5.9 | +5.3 / +10.8 | FAIL ; few trades |
| 194 | F5 delta/CVD | F5 IBbrk CVD disagree stp struct | M15 | 2.6 | -6.3 | -1.9 | +0.8 | +3.2 | -11.8 / +3.2 | +7.0 / +6.9 | FAIL ; few trades |
| 195 | F4 POC | F4 POCrev dPOC k8.7 mkt atr | M5 | 54.2 | +5.0 | +1.1 | +5.1 | +0.3 | +3.7 / +0.3 | +1.0 / +2.6 | all 4 > 0, pooled z 3.0 |
| 196 | F4 POC | F4 POCrev dPOC k8.7 mkt struct | M5 | 54.2 | +1.1 | +1.8 | +2.4 | +3.1 | +1.4 / +3.1 | +4.3 / +3.0 | all 4 > 0, pooled z 2.1 |
| 197 | F4 POC | F4 POCrev dPOC k8.7 stp atr | M5 | 31.1 | +4.0 | -1.8 | +2.5 | -5.1 | +5.2 / -2.4 | -2.2 / -3.5 | FAIL |
| 198 | F4 POC | F4 POCrev dPOC k8.7 stp struct | M5 | 31.1 | -0.3 | +1.9 | +1.3 | -2.2 | +1.3 / +0.6 | -1.0 / -3.0 | FAIL |
| 199 | F4 POC | F4 POCrev dPOC k8.7 +revbar mkt atr | M5 | 40.2 | +2.5 | -0.1 | +5.9 | -3.4 | +1.9 / +1.0 | +2.6 / -1.0 | FAIL |
| 200 | F4 POC | F4 POCrev dPOC k8.7 +revbar mkt struct | M5 | 40.2 | -0.2 | -2.7 | +1.1 | -0.7 | -0.7 / -2.4 | +3.5 / -1.8 | FAIL |
| 201 | F4 POC | F4 POCrev dPOC k8.7 +revbar stp atr | M5 | 32.3 | +2.5 | +1.1 | +6.3 | -3.0 | +1.2 / +1.8 | +2.8 / -2.5 | FAIL |
| 202 | F4 POC | F4 POCrev dPOC k8.7 +revbar stp struct | M5 | 32.3 | +0.9 | +0.9 | +3.2 | -1.2 | +0.5 / +0.6 | +4.5 / -3.3 | FAIL |
| 203 | F4 POC | F4 POCrev pPOC k21.6 mkt atr | M5 | 51.6 | +3.2 | -2.0 | +1.7 | +0.0 | +2.9 / -1.0 | -1.2 / +0.9 | FAIL |
| 204 | F4 POC | F4 POCrev pPOC k21.6 mkt struct | M5 | 51.6 | +0.2 | -1.6 | -2.2 | +1.0 | +1.5 / +0.8 | -2.9 / -1.5 | FAIL |
| 205 | F4 POC | F4 POCrev pPOC k21.6 stp atr | M5 | 32.0 | +3.2 | -2.8 | +1.7 | +2.7 | +2.3 / -1.3 | -2.7 / +3.4 | FAIL |
| 206 | F4 POC | F4 POCrev pPOC k21.6 stp struct | M5 | 32.0 | -1.5 | -2.6 | -2.7 | +5.1 | -0.3 / -0.6 | -4.3 / +3.4 | FAIL |
| 207 | F4 POC | F4 POCrev pPOC k21.6 +revbar mkt atr | M5 | 41.2 | +3.9 | -0.9 | +3.4 | -1.0 | +4.1 / +0.3 | +1.7 / +0.9 | FAIL |
| 208 | F4 POC | F4 POCrev pPOC k21.6 +revbar mkt struct | M5 | 41.2 | -1.3 | -1.7 | -2.5 | +2.2 | -0.9 / -1.8 | -0.1 / +0.2 | FAIL |
| 209 | F4 POC | F4 POCrev pPOC k21.6 +revbar stp atr | M5 | 33.9 | +5.4 | -1.0 | +2.5 | -0.5 | +5.6 / +0.8 | +0.6 / +0.2 | FAIL |
| 210 | F4 POC | F4 POCrev pPOC k21.6 +revbar stp struct | M5 | 33.9 | +1.4 | -0.6 | +0.4 | +0.2 | +1.9 / -0.8 | +0.7 / -2.4 | FAIL |
| 211 | F4 POC | F4 POCmig pullback mkt atr | M5 | 62.3 | -0.5 | +1.4 | -2.6 | -0.2 | +0.2 / +0.3 | -0.9 / -2.1 | FAIL |
| 212 | F4 POC | F4 POCmig pullback mkt struct | M5 | 62.3 | +1.0 | +1.5 | -4.7 | +2.0 | +1.4 / +1.6 | -2.9 / +0.5 | FAIL |
| 213 | F4 POC | F4 POCmig pullback stp atr | M5 | 49.8 | +1.6 | +1.3 | -1.7 | +1.0 | +0.9 / -0.2 | -1.3 / -0.8 | FAIL |
| 214 | F4 POC | F4 POCmig pullback stp struct | M5 | 49.8 | +3.4 | +4.2 | -1.9 | +3.6 | +2.8 / +3.5 | -0.9 / +1.9 | FAIL |
| 215 | F4 POC | F4 POCmig trend mkt atr | M5 | 59.7 | -0.1 | +2.0 | -0.8 | +2.9 | +0.0 / +0.6 | -0.5 / +1.8 | FAIL |
| 216 | F4 POC | F4 POCmig trend stp atr | M5 | 37.7 | -0.3 | +1.6 | -2.0 | +4.2 | +0.6 / -2.0 | -1.0 / +3.1 | FAIL |
| 217 | F5 delta/CVD | F5 CVDdiv tk mkt atr | M5 | 44.1 | +1.4 | +3.0 | -4.3 | -1.0 | +5.1 / +2.4 | -2.6 / -3.5 | FAIL |
| 218 | F5 delta/CVD | F5 CVDdiv tk mkt struct | M5 | 44.1 | +0.4 | -0.5 | -5.1 | -1.8 | +4.0 / -0.4 | -1.1 / -2.9 | FAIL |
| 219 | F5 delta/CVD | F5 CVDdiv tk stp atr | M5 | 20.0 | -0.2 | -0.4 | +1.1 | +1.6 | +1.8 / +1.7 | +0.0 / -3.7 | FAIL |
| 220 | F5 delta/CVD | F5 CVDdiv tk stp struct | M5 | 20.0 | +0.9 | +0.7 | +1.4 | +1.8 | +2.8 / +1.9 | +0.6 / -3.9 | all 4 > 0, pooled z 0.7 |
| 221 | F5 delta/CVD | F5 CVDdiv tk +rej mkt atr | M5 | 15.6 | -0.8 | +0.8 | -2.2 | +0.3 | +1.4 / +0.3 | -0.4 / -2.5 | FAIL ; few trades |
| 222 | F5 delta/CVD | F5 CVDdiv tk +rej mkt struct | M5 | 15.6 | +0.0 | +0.4 | -1.4 | +0.9 | +2.1 / +0.6 | +1.2 / -3.7 | FAIL ; few trades |
| 223 | F5 delta/CVD | F5 CVDdiv tk +rej stp atr | M5 | 11.3 | -0.4 | -0.4 | -0.6 | +1.2 | +1.2 / -1.5 | -1.2 / -5.8 | FAIL ; few trades |
| 224 | F5 delta/CVD | F5 CVDdiv tk +rej stp struct | M5 | 11.3 | +1.6 | +1.6 | -0.8 | +2.7 | +3.3 / +0.2 | +0.9 / -5.0 | FAIL ; few trades |
| 225 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) mkt atr | M5 | 74.9 | +0.1 | -1.0 | -0.3 | -0.4 | +0.0 / +0.1 | +1.9 / -2.5 | FAIL |
| 226 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) mkt struct | M5 | 74.9 | -0.3 | -1.5 | -4.2 | +1.8 | +0.3 / -0.8 | -0.6 / -0.7 | FAIL |
| 227 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) stp atr | M5 | 28.9 | -1.5 | +2.4 | -1.8 | +3.9 | -2.6 / +3.4 | -3.0 / +1.1 | FAIL |
| 228 | F5 delta/CVD | F5 CVDconfirm fade (ctrl) stp struct | M5 | 28.9 | -1.6 | +3.3 | -3.7 | +5.3 | -3.6 / +4.1 | -5.0 / +2.6 | FAIL |
| 229 | F5 delta/CVD | F5 CVDconfirm follow mkt atr | M5 | 74.9 | +0.8 | -0.2 | -0.6 | -0.3 | -0.4 / -0.5 | +0.4 / -1.7 | FAIL |
| 230 | F5 delta/CVD | F5 CVDconfirm follow mkt struct | M5 | 74.9 | +2.1 | -0.5 | -0.2 | -1.1 | +2.5 / -1.0 | +3.3 / -2.8 | FAIL |
| 231 | F5 delta/CVD | F5 CVDconfirm follow stp atr | M5 | 51.9 | +1.7 | -1.7 | -0.5 | +1.4 | +0.3 / -2.9 | +0.6 / -2.7 | FAIL |
| 232 | F5 delta/CVD | F5 CVDconfirm follow stp struct | M5 | 51.9 | +2.4 | -0.9 | -0.1 | +0.1 | +1.5 / -1.9 | +1.8 / -2.3 | FAIL |
| 233 | F5 delta/CVD | F5 CVDdiv cl mkt atr | M5 | 54.4 | +1.4 | +1.0 | -2.7 | +0.2 | +3.1 / -0.3 | -0.5 / +0.2 | FAIL |
| 234 | F5 delta/CVD | F5 CVDdiv cl mkt struct | M5 | 54.4 | +1.3 | -1.1 | -5.9 | -0.1 | +3.4 / +0.0 | -3.5 / +1.2 | FAIL |
| 235 | F5 delta/CVD | F5 CVDdiv cl stp atr | M5 | 24.4 | +0.8 | +1.0 | +2.0 | +4.8 | +3.5 / +1.1 | +2.2 / +7.1 | all 4 > 0, pooled z 1.1 |
| 236 | F5 delta/CVD | F5 CVDdiv cl stp struct | M5 | 24.4 | +2.4 | +2.2 | +1.6 | +5.4 | +5.6 / +2.1 | +1.3 / +5.1 | all 4 > 0, pooled z 1.9 |
| 237 | F5 delta/CVD | F5 CVDdiv cl +rej mkt atr | M5 | 18.2 | +0.4 | -1.4 | +0.8 | +0.1 | +0.9 / -2.1 | +4.5 / +0.5 | FAIL ; few trades |
| 238 | F5 delta/CVD | F5 CVDdiv cl +rej mkt struct | M5 | 18.2 | -0.9 | -1.4 | -1.3 | -1.3 | +2.3 / -3.0 | -0.0 / -1.0 | FAIL ; few trades |
| 239 | F5 delta/CVD | F5 CVDdiv cl +rej stp atr | M5 | 13.3 | +0.1 | -0.6 | +1.7 | +4.4 | +0.1 / -3.8 | +5.6 / +2.9 | FAIL ; few trades |
| 240 | F5 delta/CVD | F5 CVDdiv cl +rej stp struct | M5 | 13.3 | +1.7 | +1.1 | +0.2 | +2.9 | +3.6 / -2.2 | +0.5 / +2.9 | all 4 > 0, pooled z 0.7 ; few trades |
| 241 | F5 delta/CVD | F5 deltaflip after sweep mkt atr | M5 | 22.5 | -1.2 | -1.8 | -1.4 | +2.5 | +2.1 / -2.8 | -4.1 / +1.5 | FAIL |
| 242 | F5 delta/CVD | F5 deltaflip after sweep mkt struct | M5 | 22.5 | -1.3 | -0.9 | -3.3 | +4.6 | +1.8 / -1.4 | -7.0 / +3.7 | FAIL |
| 243 | F5 delta/CVD | F5 deltaflip after sweep stp atr | M5 | 17.6 | +2.2 | -0.7 | -3.0 | +0.1 | +3.7 / -1.1 | -7.3 / -1.7 | FAIL ; few trades |
| 244 | F5 delta/CVD | F5 deltaflip after sweep stp struct | M5 | 17.6 | -0.1 | -0.1 | -4.0 | +1.0 | +1.9 / -1.0 | -8.7 / -1.0 | FAIL ; few trades |
| 245 | F5 delta/CVD | F5 climax opp delta mkt atr | M5 | 1.9 | -4.3 | -0.3 | +10.3 | -1.3 | -11.9 / +2.4 | +23.4 / +2.9 | FAIL ; few trades |
| 246 | F5 delta/CVD | F5 climax opp delta mkt struct | M5 | 1.9 | -7.8 | +5.5 | +1.6 | +6.4 | -13.1 / +9.6 | +11.9 / +4.2 | FAIL ; few trades |
| 247 | F5 delta/CVD | F5 climax opp delta stp atr | M5 | 1.4 | -10.5 | -0.5 | +9.0 | -3.1 | -7.5 / +1.6 | +22.8 / -3.0 | FAIL ; few trades |
| 248 | F5 delta/CVD | F5 climax opp delta stp struct | M5 | 1.4 | -12.9 | +4.3 | +3.0 | +1.7 | -8.0 / +7.1 | +14.1 / +8.7 | FAIL ; few trades |
| 249 | F5 delta/CVD | F5 climax aligned delta (ctrl) mkt atr | M5 | 3.5 | +3.8 | -6.7 | -5.9 | +5.4 | +1.2 / -5.3 | -4.4 / +7.3 | FAIL ; few trades |
| 250 | F5 delta/CVD | F5 climax aligned delta (ctrl) mkt struct | M5 | 3.5 | +2.2 | -14.1 | -14.2 | +4.3 | +3.1 / -9.6 | -8.7 / +5.6 | FAIL ; few trades |
| 251 | F5 delta/CVD | F5 climax aligned delta (ctrl) stp atr | M5 | 1.1 | -6.0 | -15.9 | -17.0 | -9.8 | -9.3 / -21.4 | -10.6 / -14.9 | FAIL ; few trades |
| 252 | F5 delta/CVD | F5 climax aligned delta (ctrl) stp struct | M5 | 1.1 | +2.7 | -17.3 | -14.1 | -6.1 | +5.6 / -20.8 | +1.1 / -10.5 | FAIL ; few trades |
| 253 | F5 delta/CVD | F5 IBbrk CVD agree mkt atr | M5 | 16.9 | +1.4 | -1.7 | -1.6 | -5.1 | +1.4 / -5.0 | -2.5 / -3.4 | FAIL ; few trades |
| 254 | F5 delta/CVD | F5 IBbrk CVD agree mkt struct | M5 | 16.9 | +0.6 | -1.7 | +1.1 | -2.0 | +0.8 / -4.2 | -2.0 / +0.7 | FAIL ; few trades |
| 255 | F5 delta/CVD | F5 IBbrk CVD agree stp atr | M5 | 12.8 | +0.1 | -0.3 | -3.3 | -7.3 | +0.8 / -3.5 | -4.2 / -7.3 | FAIL ; few trades |
| 256 | F5 delta/CVD | F5 IBbrk CVD agree stp struct | M5 | 12.8 | -0.2 | -0.7 | +0.1 | -4.1 | +0.6 / -2.5 | -1.9 / -1.2 | FAIL ; few trades |
| 257 | F5 delta/CVD | F5 IBbrk CVD disagree mkt atr | M5 | 3.3 | +4.7 | -6.8 | +8.1 | +9.1 | +2.8 / -5.0 | +2.5 / +14.9 | FAIL ; few trades |
| 258 | F5 delta/CVD | F5 IBbrk CVD disagree mkt struct | M5 | 3.3 | -1.6 | -9.6 | +13.1 | +6.4 | -4.9 / -7.1 | +8.1 / +14.2 | FAIL ; few trades |
| 259 | F5 delta/CVD | F5 IBbrk CVD disagree stp atr | M5 | 2.6 | +1.8 | -13.3 | +6.2 | +9.2 | -2.3 / -12.8 | +3.9 / +18.1 | FAIL ; few trades |
| 260 | F5 delta/CVD | F5 IBbrk CVD disagree stp struct | M5 | 2.6 | -4.1 | -11.0 | +12.7 | +5.5 | -10.5 / -9.1 | +10.7 / +10.2 | FAIL ; few trades |
| 261 | F6 combo | F6 sig ALL lim own | M15 | 90.6 | -0.9 | -0.1 | -2.6 | -1.9 | +0.8 / -0.9 | +0.4 / -2.2 | FAIL |
| 262 | F6 combo | F6 sig ALL mkt atr | M15 | 117.5 | -0.6 | -2.2 | -0.5 | +1.9 | +0.9 / -2.7 | +1.4 / +0.2 | FAIL |
| 263 | F6 combo | F6 sig ALL stp atr | M15 | 97.1 | +0.3 | -1.9 | +0.0 | +1.4 | +1.1 / -2.3 | +1.2 / -1.4 | FAIL |
| 264 | F6 combo | F6 sig +bar delta agrees lim own | M15 | 86.9 | -0.7 | -0.1 | -2.6 | -2.0 | +0.2 / -0.8 | -1.9 / -1.2 | FAIL |
| 265 | F6 combo | F6 sig +bar delta agrees mkt atr | M15 | 113.2 | -0.4 | -2.2 | -0.6 | +1.9 | +0.6 / -3.5 | +0.2 / +1.9 | FAIL |
| 266 | F6 combo | F6 sig +bar delta agrees stp atr | M15 | 93.7 | +0.4 | -1.8 | -0.2 | +1.3 | +1.6 / -3.8 | +0.6 / +1.0 | FAIL |
| 267 | F6 combo | F6 sig NOT bar delta agrees lim own | M15 | 3.7 | -6.2 | +0.2 | -3.8 | +0.6 | -8.6 / +1.4 | +8.3 / +6.7 | FAIL ; few trades |
| 268 | F6 combo | F6 sig NOT bar delta agrees mkt atr | M15 | 4.3 | -4.6 | -1.8 | +2.2 | +2.5 | -4.0 / -1.3 | +13.1 / +5.0 | FAIL ; few trades |
| 269 | F6 combo | F6 sig NOT bar delta agrees stp atr | M15 | 3.4 | -2.0 | -4.1 | +7.9 | +2.9 | -2.3 / -2.9 | +17.7 / +5.0 | FAIL ; few trades |
| 270 | F6 combo | F6 OPP sig NOT bar delta agrees mkt | M15 | 4.3 | +7.6 | -0.3 | -2.2 | -1.6 | +6.5 / +0.4 | -5.8 / -12.4 | FAIL ; few trades |
| 271 | F6 combo | F6 sig +sess CVD agrees lim own | M15 | 76.0 | -1.1 | +0.6 | -2.3 | -1.3 | -0.4 / -0.4 | +0.5 / -1.8 | FAIL |
| 272 | F6 combo | F6 sig +sess CVD agrees mkt atr | M15 | 99.3 | -0.8 | -1.7 | -0.3 | +2.6 | +0.0 / -3.2 | +0.6 / +1.1 | FAIL |
| 273 | F6 combo | F6 sig +sess CVD agrees stp atr | M15 | 82.2 | +0.3 | -1.8 | +0.2 | +2.1 | +0.9 / -3.3 | +0.7 / +0.0 | FAIL |
| 274 | F6 combo | F6 sig NOT sess CVD agrees lim own | M15 | 14.6 | +0.1 | -3.4 | -5.3 | -3.7 | +2.5 / -6.0 | -2.1 / -3.9 | FAIL |
| 275 | F6 combo | F6 sig NOT sess CVD agrees mkt atr | M15 | 18.2 | +0.8 | -4.7 | -1.6 | -0.7 | +3.9 / -7.3 | +1.2 / -1.3 | FAIL |
| 276 | F6 combo | F6 sig NOT sess CVD agrees stp atr | M15 | 14.9 | +0.6 | -1.9 | -2.0 | -1.2 | +3.5 / -4.8 | +0.6 / -1.2 | FAIL |
| 277 | F6 combo | F6 OPP sig NOT sess CVD agrees mkt | M15 | 18.2 | +4.3 | -0.7 | -0.3 | +1.7 | +7.0 / -5.0 | +1.4 / +0.5 | FAIL |
| 278 | F6 combo | F6 sig +close beyond devVA lim own | M15 | 82.4 | -0.8 | -0.4 | -2.6 | -2.9 | -0.1 / -0.9 | -1.4 / -3.2 | FAIL |
| 279 | F6 combo | F6 sig +close beyond devVA mkt atr | M15 | 108.3 | -0.3 | -1.9 | -0.4 | +1.5 | +0.3 / -3.0 | +0.5 / +1.0 | FAIL |
| 280 | F6 combo | F6 sig +close beyond devVA stp atr | M15 | 89.9 | +0.4 | -1.6 | -0.0 | +1.1 | +1.0 / -2.5 | +1.1 / +0.1 | FAIL |
| 281 | F6 combo | F6 sig NOT close beyond devVA lim own | M15 | 8.1 | -2.7 | +2.5 | -2.6 | +8.8 | -3.6 / +3.5 | +1.1 / +10.2 | FAIL |
| 282 | F6 combo | F6 sig NOT close beyond devVA mkt atr | M15 | 9.2 | -3.1 | -5.3 | -1.7 | +6.2 | -5.2 / -4.1 | +0.6 / +7.0 | FAIL |
| 283 | F6 combo | F6 sig NOT close beyond devVA stp atr | M15 | 7.2 | -0.6 | -5.1 | +0.1 | +5.1 | -0.8 / -5.5 | +1.4 / +9.7 | FAIL ; few trades |
| 284 | F6 combo | F6 OPP sig NOT close beyond devVA mkt | M15 | 9.2 | +4.1 | +4.2 | -8.1 | +2.8 | +2.4 / +6.5 | -9.2 / +1.6 | FAIL |
| 285 | F6 combo | F6 sig +devPOC ahead lim own | M15 | 0.5 | +14.9 | +31.8 | -10.5 | +37.2 | +19.9 / +34.9 | -28.4 / +38.3 | FAIL ; few trades |
| 286 | F6 combo | F6 sig +devPOC ahead mkt atr | M15 | 0.6 | +23.0 | +16.1 | -0.5 | +7.2 | +27.6 / +20.8 | -15.2 / +16.7 | FAIL ; few trades |
| 287 | F6 combo | F6 sig +devPOC ahead stp atr | M15 | 0.5 | +26.0 | +13.0 | -0.5 | +23.8 | +32.7 / +23.3 | -13.9 / +37.5 | FAIL ; few trades |
| 288 | F6 combo | F6 sig NOT devPOC ahead lim own | M15 | 90.1 | -1.0 | -0.3 | -2.6 | -2.1 | -0.1 / -0.2 | -2.5 / -2.9 | FAIL |
| 289 | F6 combo | F6 sig NOT devPOC ahead mkt atr | M15 | 116.9 | -0.7 | -2.3 | -0.5 | +1.9 | -0.5 / -3.5 | -0.5 / +0.4 | FAIL |
| 290 | F6 combo | F6 sig NOT devPOC ahead stp atr | M15 | 96.7 | +0.2 | -1.9 | +0.0 | +1.3 | +0.6 / -3.1 | -0.4 / -0.8 | FAIL |
| 291 | F6 combo | F6 OPP sig NOT devPOC ahead mkt | M15 | 116.9 | +2.7 | +1.0 | -2.2 | +0.3 | +3.7 / +0.7 | -0.9 / +0.2 | FAIL |
| 292 | F6 combo | F6 sig +LVN path ahead lim own | M15 | 38.9 | -0.1 | +4.2 | -2.2 | -0.4 | +0.9 / +3.2 | -0.5 / +0.4 | FAIL |
| 293 | F6 combo | F6 sig +LVN path ahead mkt atr | M15 | 51.7 | +0.6 | +1.2 | -1.5 | +4.5 | +1.1 / +0.4 | -0.4 / +2.9 | FAIL |
| 294 | F6 combo | F6 sig +LVN path ahead stp atr | M15 | 43.1 | +1.6 | +1.2 | -2.2 | +4.2 | +2.1 / +0.5 | -1.4 / +2.4 | FAIL |
| 295 | F6 combo | F6 sig NOT LVN path ahead lim own | M15 | 51.7 | -1.5 | -3.6 | -3.1 | -2.6 | -0.1 / -3.8 | -0.6 / -3.8 | FAIL |
| 296 | F6 combo | F6 sig NOT LVN path ahead mkt atr | M15 | 65.8 | -1.4 | -5.0 | +0.7 | +0.5 | -1.6 / -5.6 | +1.4 / -0.2 | FAIL |
| 297 | F6 combo | F6 sig NOT LVN path ahead stp atr | M15 | 54.1 | -0.7 | -4.4 | +2.3 | -0.2 | -0.5 / -5.7 | +1.9 / -1.6 | FAIL |
| 298 | F6 combo | F6 OPP sig NOT LVN path ahead mkt | M15 | 65.8 | +5.1 | +1.5 | -0.9 | -1.1 | +6.1 / +0.8 | +0.5 / -2.4 | FAIL |
| 299 | F6 combo | F6 sig +beyond priorVA lim own | M15 | 49.6 | +0.9 | +1.9 | -2.1 | -1.4 | +1.5 / +1.5 | +1.3 / -1.3 | FAIL |
| 300 | F6 combo | F6 sig +beyond priorVA mkt atr | M15 | 66.1 | +1.4 | -0.1 | +0.1 | +2.0 | +2.7 / -1.3 | +1.8 / +0.5 | FAIL |
| 301 | F6 combo | F6 sig +beyond priorVA stp atr | M15 | 54.7 | +1.9 | +0.1 | +0.9 | +1.2 | +2.8 / -1.3 | +1.2 / +0.5 | all 4 > 0, pooled z 1.1 |
| 302 | F6 combo | F6 sig NOT beyond priorVA lim own | M15 | 41.0 | -3.3 | -2.5 | -3.5 | -2.4 | -3.0 / -4.0 | +1.1 / -4.1 | FAIL |
| 303 | F6 combo | F6 sig NOT beyond priorVA mkt atr | M15 | 51.4 | -3.1 | -4.8 | -1.6 | +1.7 | -2.3 / -5.8 | +1.2 / +0.2 | FAIL |
| 304 | F6 combo | F6 sig NOT beyond priorVA stp atr | M15 | 42.4 | -1.7 | -4.4 | -1.5 | +1.6 | -1.2 / -5.2 | -0.0 / +0.2 | FAIL |
| 305 | F6 combo | F6 OPP sig NOT beyond priorVA mkt | M15 | 51.4 | +4.5 | +3.8 | -2.5 | +0.7 | +5.8 / +2.9 | -0.9 / -2.2 | FAIL |
| 306 | F6 combo | F6 sig ALL lim own | M5 | 251.6 | -1.1 | -0.9 | -0.5 | +0.8 | +0.3 / -0.1 | -0.1 / +1.5 | FAIL |
| 307 | F6 combo | F6 sig ALL mkt atr | M5 | 324.5 | -0.8 | -2.5 | -0.4 | +0.9 | -0.1 / -2.2 | -0.4 / +0.5 | FAIL |
| 308 | F6 combo | F6 sig ALL stp atr | M5 | 269.9 | +0.5 | -1.9 | -0.1 | +2.3 | +0.4 / -2.4 | -0.6 / +1.4 | FAIL |
| 309 | F6 combo | F6 sig +bar delta agrees lim own | M5 | 245.2 | -1.1 | -1.0 | -0.5 | +0.8 | -0.6 / -1.3 | +0.8 / -0.4 | FAIL |
| 310 | F6 combo | F6 sig +bar delta agrees mkt atr | M5 | 316.8 | -0.8 | -2.5 | -0.3 | +0.8 | -0.4 / -3.0 | +0.4 / -0.1 | FAIL |
| 311 | F6 combo | F6 sig +bar delta agrees stp atr | M5 | 263.6 | +0.5 | -2.0 | -0.1 | +2.2 | +0.3 / -2.7 | +0.2 / +1.1 | FAIL |
| 312 | F6 combo | F6 sig NOT bar delta agrees lim own | M5 | 6.4 | -0.9 | +0.8 | -4.1 | +2.1 | -0.6 / -2.5 | +1.9 / +4.3 | FAIL ; few trades |
| 313 | F6 combo | F6 sig NOT bar delta agrees mkt atr | M5 | 7.8 | -0.8 | -2.2 | -2.0 | +7.1 | +0.1 / -3.4 | +1.5 / +10.9 | FAIL ; few trades |
| 314 | F6 combo | F6 sig NOT bar delta agrees stp atr | M5 | 6.4 | -0.7 | -0.6 | -0.7 | +14.8 | +0.4 / -2.8 | +2.9 / +23.4 | FAIL ; few trades |
| 315 | F6 combo | F6 OPP sig NOT bar delta agrees mkt | M5 | 7.8 | -2.0 | -0.8 | -13.5 | +1.4 | -0.4 / -0.8 | -17.9 / -2.8 | FAIL ; few trades |
| 316 | F6 combo | F6 sig +sess CVD agrees lim own | M5 | 202.4 | -1.4 | -0.5 | -0.2 | +0.7 | -1.1 / -1.0 | +0.4 / -0.5 | FAIL |
| 317 | F6 combo | F6 sig +sess CVD agrees mkt atr | M5 | 260.6 | -1.1 | -2.1 | -0.2 | +0.7 | -0.8 / -2.6 | +0.6 / -0.8 | FAIL |
| 318 | F6 combo | F6 sig +sess CVD agrees stp atr | M5 | 216.4 | +0.7 | -1.3 | +0.2 | +2.3 | +0.2 / -2.7 | +0.3 / +0.2 | FAIL |
| 319 | F6 combo | F6 sig NOT sess CVD agrees lim own | M5 | 49.3 | +0.5 | -2.7 | -2.5 | +1.0 | +0.9 / -3.3 | -3.3 / +1.6 | FAIL |
| 320 | F6 combo | F6 sig NOT sess CVD agrees mkt atr | M5 | 64.0 | +0.2 | -4.0 | -1.3 | +1.3 | +0.5 / -3.9 | -1.5 / +2.4 | FAIL |
| 321 | F6 combo | F6 sig NOT sess CVD agrees stp atr | M5 | 53.5 | -0.3 | -4.2 | -2.2 | +2.6 | -0.6 / -4.6 | -2.2 / +3.9 | FAIL |
| 322 | F6 combo | F6 OPP sig NOT sess CVD agrees mkt | M5 | 64.0 | +4.9 | -0.3 | -1.8 | +1.5 | +5.1 / -0.1 | -2.3 / +2.1 | FAIL |
| 323 | F6 combo | F6 sig +close beyond devVA lim own | M5 | 202.4 | -0.7 | -0.8 | -0.0 | +0.9 | +0.3 / -0.1 | +0.7 / +1.1 | FAIL |
| 324 | F6 combo | F6 sig +close beyond devVA mkt atr | M5 | 262.3 | -0.9 | -2.6 | -0.3 | +0.9 | -0.7 / -2.6 | -0.1 / +0.4 | FAIL |
| 325 | F6 combo | F6 sig +close beyond devVA stp atr | M5 | 218.1 | +0.1 | -2.1 | -0.1 | +2.6 | -0.2 / -2.4 | -0.3 / +1.6 | FAIL |
| 326 | F6 combo | F6 sig NOT close beyond devVA lim own | M5 | 49.2 | -2.5 | -1.6 | -2.9 | +0.4 | -2.9 / -0.9 | -2.8 / +3.4 | FAIL |
| 327 | F6 combo | F6 sig NOT close beyond devVA mkt atr | M5 | 62.2 | -0.3 | -2.1 | -0.7 | +0.7 | -1.2 / -2.1 | -1.2 / +1.5 | FAIL |
| 328 | F6 combo | F6 sig NOT close beyond devVA stp atr | M5 | 51.9 | +2.1 | -1.4 | -0.3 | +1.3 | +0.5 / -1.7 | -1.3 / +0.8 | FAIL |
| 329 | F6 combo | F6 OPP sig NOT close beyond devVA mkt | M5 | 62.2 | +2.3 | -0.6 | -0.3 | +1.6 | +2.6 / -0.3 | -1.8 / +2.1 | FAIL |
| 330 | F6 combo | F6 sig +devPOC ahead lim own | M5 | 3.8 | +6.0 | -4.4 | +3.5 | -9.2 | +5.2 / -1.7 | +11.4 / -15.6 | FAIL ; few trades |
| 331 | F6 combo | F6 sig +devPOC ahead mkt atr | M5 | 5.2 | +7.8 | -6.0 | +6.5 | -16.2 | +11.7 / -3.5 | +12.6 / -16.8 | FAIL ; few trades |
| 332 | F6 combo | F6 sig +devPOC ahead stp atr | M5 | 4.4 | +9.4 | -8.6 | +7.4 | -14.2 | +14.0 / -6.4 | +12.7 / -14.4 | FAIL ; few trades |
| 333 | F6 combo | F6 sig NOT devPOC ahead lim own | M5 | 247.9 | -1.2 | -0.9 | -0.6 | +1.0 | -0.4 / -0.8 | +0.6 / +0.4 | FAIL |
| 334 | F6 combo | F6 sig NOT devPOC ahead mkt atr | M5 | 319.4 | -1.0 | -2.4 | -0.5 | +1.2 | -0.4 / -2.6 | +0.2 / +0.6 | FAIL |
| 335 | F6 combo | F6 sig NOT devPOC ahead stp atr | M5 | 265.6 | +0.4 | -1.8 | -0.3 | +2.7 | +0.5 / -2.5 | -0.3 / +1.6 | FAIL |
| 336 | F6 combo | F6 OPP sig NOT devPOC ahead mkt | M5 | 319.4 | +2.7 | +1.2 | -0.9 | +0.4 | +2.9 / +0.7 | -0.5 / -0.2 | FAIL |
| 337 | F6 combo | F6 sig +LVN path ahead lim own | M5 | 99.1 | -2.5 | -0.5 | +0.1 | +2.1 | -1.3 / -0.2 | +1.6 / +3.4 | FAIL |
| 338 | F6 combo | F6 sig +LVN path ahead mkt atr | M5 | 128.5 | -1.8 | -1.9 | -0.9 | +1.9 | -1.2 / -2.3 | +0.2 / +2.3 | FAIL |
| 339 | F6 combo | F6 sig +LVN path ahead stp atr | M5 | 106.2 | -0.4 | -1.3 | -0.8 | +3.3 | -0.7 / -2.8 | -0.5 / +3.1 | FAIL |
| 340 | F6 combo | F6 sig NOT LVN path ahead lim own | M5 | 152.5 | -0.2 | -1.3 | -1.1 | +0.1 | +0.6 / -0.6 | +1.5 / -0.3 | FAIL |
| 341 | F6 combo | F6 sig NOT LVN path ahead mkt atr | M5 | 196.0 | -0.2 | -2.9 | +0.1 | +0.3 | +0.2 / -3.1 | +1.6 / -0.8 | FAIL |
| 342 | F6 combo | F6 sig NOT LVN path ahead stp atr | M5 | 163.8 | +1.1 | -2.3 | +0.5 | +1.9 | +1.2 / -3.2 | +0.9 / +0.1 | FAIL |
| 343 | F6 combo | F6 OPP sig NOT LVN path ahead mkt | M5 | 196.0 | +3.0 | +0.4 | -0.2 | +0.3 | +3.6 / -0.1 | +0.9 / -0.9 | FAIL |
| 344 | F6 combo | F6 sig +beyond priorVA lim own | M5 | 125.2 | -2.0 | -0.8 | -0.3 | +1.3 | -1.9 / +0.3 | +1.3 / +2.5 | FAIL |
| 345 | F6 combo | F6 sig +beyond priorVA mkt atr | M5 | 163.3 | -1.3 | -1.4 | -1.5 | +2.3 | -1.6 / -1.6 | -1.2 / +1.8 | FAIL |
| 346 | F6 combo | F6 sig +beyond priorVA stp atr | M5 | 135.0 | -0.0 | -0.6 | -1.1 | +4.2 | -0.9 / -1.9 | -1.6 / +3.2 | FAIL |
| 347 | F6 combo | F6 sig NOT beyond priorVA lim own | M5 | 126.4 | -0.1 | -1.1 | -0.9 | +0.3 | +0.0 / -0.9 | -0.3 / +0.9 | FAIL |
| 348 | F6 combo | F6 sig NOT beyond priorVA mkt atr | M5 | 161.2 | -0.3 | -3.6 | +1.3 | -0.4 | -0.9 / -4.3 | +1.2 / -0.6 | FAIL |
| 349 | F6 combo | F6 sig NOT beyond priorVA stp atr | M5 | 134.9 | +1.1 | -3.2 | +1.3 | +0.7 | -0.0 / -5.1 | +1.0 / -0.4 | FAIL |
| 350 | F6 combo | F6 OPP sig NOT beyond priorVA mkt | M5 | 161.2 | +3.5 | +0.3 | +0.1 | -0.8 | +4.1 / +0.7 | -0.4 / -0.7 | FAIL |
| 351 | cand | C1 dPOC p80(k5.8) mkt atr | M5 | 115.2 | +1.8 | +0.7 | +3.0 | +0.1 | +1.9 / +0.6 | +1.8 / +1.8 | all 4 > 0, pooled z 2.1 |
| 352 | cand | C1 dPOC p85(k6.9) mkt atr | M5 | 85.7 | +3.1 | +1.7 | +3.1 | +0.6 | +2.7 / +2.4 | +2.5 / +0.3 | all 4 > 0, pooled z 2.9 |
| 353 | cand | C1 dPOC p90(k8.6) mkt atr | M5 | 55.9 | +5.0 | +1.1 | +4.1 | -0.3 | +4.5 / +1.7 | +1.4 / +1.4 | FAIL |
| 354 | cand | C1 dPOC p95(k12.0) mkt atr | M5 | 27.5 | +6.9 | +0.1 | +7.2 | -1.8 | +5.8 / +0.3 | +3.2 / +1.9 | FAIL |
| 355 | cand | C1 dPOC p90 mkt atr1.2 | M5 | 55.9 | +4.4 | +1.2 | +2.2 | +1.6 | +4.7 / +1.0 | +1.3 / +2.1 | all 4 > 0, pooled z 2.7 |
| 356 | cand | C1 dPOC p90 mkt atr2.5 | M5 | 55.9 | +4.9 | -0.2 | +4.6 | -2.4 | +4.4 / +0.7 | +1.1 / +0.2 | FAIL |
| 357 | cand | C1 dPOC p90 stp atr | M5 | 31.9 | +5.2 | -0.4 | +0.4 | -5.0 | +3.5 / -0.8 | -3.6 / -3.0 | FAIL |
| 358 | cand | C1 dPOC p90 minsess0 mkt atr | M5 | 64.9 | +3.7 | +0.5 | +1.7 | -0.2 | +3.0 / +1.3 | -0.8 / +2.8 | FAIL |
| 359 | cand | C1 dPOC p90 minsess360 mkt atr | M5 | 46.9 | +3.4 | -0.7 | +5.2 | -3.5 | +2.3 / -0.6 | +1.2 / +0.4 | FAIL |
| 360 | cand | C1 dPOC p90 gap6 mkt atr | M5 | 99.2 | +3.6 | +0.2 | +4.2 | -1.0 | +2.4 / +0.4 | +1.7 / +1.6 | FAIL |
| 361 | cand | C1 dPOC p90 gap24 mkt atr | M5 | 33.8 | +5.8 | +1.9 | +5.3 | +0.8 | +6.9 / +3.0 | +1.6 / +3.8 | all 4 > 0, pooled z 3.0 |
| 362 | cand | C1 dPOC p90 /SD(k2.7) mkt atr | M5 | 86.0 | +2.2 | -0.7 | -3.8 | -0.4 | +2.2 / -0.6 | -5.2 / -0.6 | FAIL |
| 363 | cand | C1ctrl VWAP p90 mkt atr | M5 | 60.1 | +3.4 | +0.5 | -0.1 | -1.8 | +1.6 / +0.4 | -2.5 / +1.1 | FAIL |
| 364 | cand | C1 pPOC p90 mkt atr | M5 | 52.6 | +4.2 | -0.6 | +2.4 | -0.0 | +3.9 / +0.1 | +2.6 / +1.3 | FAIL |
| 365 | cand | C1 dPOC p80(k3.4) mkt atr | M15 | 105.3 | +1.6 | +0.0 | +3.2 | -1.9 | +1.2 / +0.3 | +2.0 / -1.1 | FAIL |
| 366 | cand | C1 dPOC p85(k4.0) mkt atr | M15 | 79.2 | +2.6 | -0.4 | +2.1 | -2.6 | +3.1 / -0.6 | -0.1 / -0.8 | FAIL |
| 367 | cand | C1 dPOC p90(k4.8) mkt atr | M15 | 52.9 | +2.1 | -0.9 | +1.2 | -3.0 | +1.6 / -0.8 | -2.0 / -1.5 | FAIL |
| 368 | cand | C1 dPOC p95(k6.3) mkt atr | M15 | 26.4 | +2.7 | -0.2 | -2.4 | -7.6 | +3.0 / -0.8 | -4.2 / -4.0 | FAIL |
| 369 | cand | C1 dPOC p90 mkt atr1.2 | M15 | 52.9 | +3.2 | -1.1 | +1.4 | -1.4 | +3.0 / -0.0 | -0.7 / +0.7 | FAIL |
| 370 | cand | C1 dPOC p90 mkt atr2.5 | M15 | 52.9 | +1.5 | +0.6 | -0.9 | -3.5 | +0.7 / +0.8 | -4.3 / -1.9 | FAIL |
| 371 | cand | C1 dPOC p90 stp atr | M15 | 27.4 | +1.3 | -1.1 | +0.9 | -4.0 | +0.2 / +0.6 | -4.6 / -3.1 | FAIL |
| 372 | cand | C1 dPOC p90 minsess0 mkt atr | M15 | 61.2 | +2.7 | -1.2 | -0.6 | -1.8 | +2.8 / -1.8 | -3.2 / +0.3 | FAIL |
| 373 | cand | C1 dPOC p90 minsess360 mkt atr | M15 | 44.9 | +2.3 | -0.8 | +0.3 | -4.7 | +3.0 / +0.3 | -2.8 / -0.9 | FAIL |
| 374 | cand | C1 dPOC p90 gap2 mkt atr | M15 | 93.2 | +1.7 | -1.0 | +0.6 | -3.7 | +1.5 / -0.2 | -3.2 / -3.0 | FAIL |
| 375 | cand | C1 dPOC p90 gap8 mkt atr | M15 | 32.4 | +1.9 | +0.8 | +2.2 | -1.9 | +2.6 / +0.3 | -0.8 / +1.0 | FAIL |
| 376 | cand | C1 dPOC p90 /SD(k2.7) mkt atr | M15 | 70.4 | -0.5 | +0.1 | -1.8 | -2.7 | -0.6 / -0.5 | -1.7 / -2.8 | FAIL |
| 377 | cand | C1ctrl VWAP p90 mkt atr | M15 | 55.8 | +2.9 | -0.6 | -0.0 | -2.9 | +2.3 / -0.8 | -2.0 / -1.3 | FAIL |
| 378 | cand | C1 pPOC p90 mkt atr | M15 | 48.1 | -1.5 | +1.3 | +2.7 | +1.3 | -3.1 / +1.6 | +0.1 / +4.4 | FAIL |
| 379 | cand | C1 dPOC p80(k1.8) mkt atr | H1 | 50.4 | +1.7 | +0.6 | +0.4 | +0.8 | +2.1 / +0.7 | +1.6 / +4.1 | all 4 > 0, pooled z 1.0 |
| 380 | cand | C1 dPOC p85(k2.2) mkt atr | H1 | 38.2 | +1.7 | +0.6 | -1.1 | +1.7 | +0.6 / +0.8 | -4.2 / +2.6 | FAIL |
| 381 | cand | C1 dPOC p90(k2.7) mkt atr | H1 | 25.2 | +2.3 | -1.0 | -4.1 | +1.4 | +0.4 / -0.1 | -6.3 / +1.3 | FAIL |
| 382 | cand | C1 dPOC p95(k3.6) mkt atr | H1 | 12.8 | +1.4 | -2.5 | -7.0 | +1.2 | +0.4 / +0.1 | -7.5 / +1.2 | FAIL |
| 383 | cand | C1 dPOC p90 mkt atr1.2 | H1 | 25.2 | +0.9 | -3.2 | -4.6 | -1.1 | -0.6 / -2.2 | -5.9 / -2.5 | FAIL |
| 384 | cand | C1 dPOC p90 mkt atr2.5 | H1 | 25.2 | +2.1 | +0.1 | -1.8 | -1.1 | +0.5 / +1.8 | -5.3 / -0.8 | FAIL |
| 385 | cand | C1 dPOC p90 stp atr | H1 | 10.9 | +0.5 | -3.0 | -3.0 | +2.6 | -0.8 / -3.7 | -6.0 / +1.1 | FAIL |
| 386 | cand | C1 dPOC p90 minsess0 mkt atr | H1 | 29.2 | +1.6 | -0.2 | -2.4 | +0.8 | +1.7 / +0.6 | -3.7 / +1.4 | FAIL |
| 387 | cand | C1 dPOC p90 minsess360 mkt atr | H1 | 21.6 | +0.9 | -1.1 | -3.5 | +3.6 | -0.5 / +0.8 | -4.8 / +5.1 | FAIL |
| 388 | cand | C1 dPOC p90 gap1 mkt atr | H1 | 42.6 | +1.2 | -1.0 | -4.0 | +1.3 | -0.3 / +1.1 | -5.5 / +4.8 | FAIL |
| 389 | cand | C1 dPOC p90 gap4 mkt atr | H1 | 16.0 | +2.3 | -0.4 | -5.5 | +1.4 | +2.7 / +0.8 | -4.2 / +1.7 | FAIL |
| 390 | cand | C1 dPOC p90 /SD(k2.8) mkt atr | H1 | 32.6 | -0.6 | +0.7 | -2.1 | -1.7 | -3.1 / +0.6 | -0.8 / -1.5 | FAIL |
| 391 | cand | C1ctrl VWAP p90 mkt atr | H1 | 26.2 | +2.0 | -0.1 | -1.8 | -0.1 | +0.6 / +1.6 | -5.3 / -1.2 | FAIL |
| 392 | cand | C1 pPOC p90 mkt atr | H1 | 23.5 | -0.2 | -2.4 | +2.5 | -3.1 | +0.1 / -2.2 | +4.5 / -0.2 | FAIL |
| 393 | cand | C2 div cl m3 stp struct | M5 | 31.1 | +3.0 | +3.0 | +2.1 | +2.5 | +4.5 / +1.5 | +3.6 / -0.7 | all 4 > 0, pooled z 2.2 |
| 394 | cand | C2 div cl m3 stp atr | M5 | 31.1 | +1.2 | +2.5 | +3.0 | +2.5 | +3.2 / +1.0 | +5.3 / -0.0 | all 4 > 0, pooled z 1.8 |
| 395 | cand | C2 div cl m6 stp struct | M5 | 24.4 | +2.4 | +2.2 | +1.6 | +5.4 | +5.6 / +2.1 | +1.3 / +5.1 | all 4 > 0, pooled z 1.9 |
| 396 | cand | C2 div cl m6 stp atr | M5 | 24.4 | +0.8 | +1.0 | +2.0 | +4.8 | +3.5 / +1.1 | +2.2 / +7.1 | all 4 > 0, pooled z 1.1 |
| 397 | cand | C2 div cl m12 stp struct | M5 | 17.7 | +3.3 | +1.0 | +3.3 | +5.2 | +5.1 / +1.2 | +6.4 / +0.5 | all 4 > 0, pooled z 1.6 ; few trades |
| 398 | cand | C2 div cl m12 stp atr | M5 | 17.7 | +1.0 | +0.3 | +2.6 | +4.4 | +2.1 / +0.8 | +5.8 / -1.8 | all 4 > 0, pooled z 0.9 ; few trades |
| 399 | cand | C2 div tk m3 stp struct | M5 | 26.2 | +1.4 | +0.7 | -0.7 | -0.1 | +0.4 / +0.1 | -0.7 / -3.7 | FAIL |
| 400 | cand | C2 div tk m3 stp atr | M5 | 26.2 | +2.0 | +0.6 | -0.2 | +0.4 | +1.7 / +0.3 | +0.6 / -2.9 | FAIL |
| 401 | cand | C2 div tk m6 stp struct | M5 | 20.0 | +0.9 | +0.7 | +1.4 | +1.8 | +2.8 / +1.9 | +0.6 / -3.9 | all 4 > 0, pooled z 0.7 |
| 402 | cand | C2 div tk m6 stp atr | M5 | 20.0 | -0.2 | -0.4 | +1.1 | +1.6 | +1.8 / +1.7 | +0.0 / -3.7 | FAIL |
| 403 | cand | C2 div tk m12 stp struct | M5 | 14.9 | +0.1 | -1.1 | +1.1 | +1.5 | +3.3 / -0.2 | -0.3 / -1.0 | FAIL ; few trades |
| 404 | cand | C2 div tk m12 stp atr | M5 | 14.9 | -0.7 | -0.7 | +0.8 | +1.5 | +2.7 / +0.4 | +0.7 / +0.9 | FAIL ; few trades |
| 405 | cand | C2 div cl m6 minsess0 stp struct | M5 | 29.9 | +2.1 | +1.8 | +3.4 | +3.4 | +2.5 / +0.5 | +3.1 / +1.9 | all 4 > 0, pooled z 1.9 |
| 406 | cand | C2 div cl m3 stp struct | M15 | 23.2 | -1.5 | +1.8 | +1.2 | -0.8 | -0.9 / +1.1 | +2.2 / -3.1 | FAIL |
| 407 | cand | C2 div cl m3 stp atr | M15 | 23.2 | +0.0 | +1.9 | -1.2 | -4.2 | +0.1 / +1.6 | -0.3 / -8.0 | FAIL |
| 408 | cand | C2 div cl m6 stp struct | M15 | 15.3 | -4.1 | +2.9 | +0.6 | -3.3 | -2.6 / +3.0 | +2.9 / -6.2 | FAIL |
| 409 | cand | C2 div cl m6 stp atr | M15 | 15.3 | -3.2 | +3.3 | -1.5 | -4.6 | -0.2 / +4.3 | -0.9 / -7.6 | FAIL |
| 410 | cand | C2 div cl m12 stp struct | M15 | 9.2 | +0.4 | +5.8 | -5.8 | -4.1 | -0.3 / +4.4 | -3.0 / -4.7 | FAIL |
| 411 | cand | C2 div cl m12 stp atr | M15 | 9.2 | -0.4 | +5.2 | -4.9 | -4.1 | +0.4 / +4.9 | -1.2 / -7.9 | FAIL |
| 412 | cand | C2 div tk m3 stp struct | M15 | 18.4 | +0.9 | +2.7 | -3.5 | -1.0 | +2.6 / +1.2 | -4.2 / -6.5 | FAIL |
| 413 | cand | C2 div tk m3 stp atr | M15 | 18.4 | +2.2 | +3.5 | -2.0 | -2.9 | +2.8 / +2.1 | -2.7 / -6.2 | FAIL |
| 414 | cand | C2 div tk m6 stp struct | M15 | 12.4 | -1.7 | +3.1 | -5.7 | -5.2 | -1.2 / +3.4 | -3.1 / -7.6 | FAIL |
| 415 | cand | C2 div tk m6 stp atr | M15 | 12.4 | -2.1 | +3.6 | -2.2 | -5.0 | +0.1 / +3.6 | -2.3 / -7.2 | FAIL |
| 416 | cand | C2 div tk m12 stp struct | M15 | 7.9 | +1.6 | +1.4 | -12.4 | -3.6 | +3.5 / +2.3 | -6.1 / -13.6 | FAIL ; few trades |
| 417 | cand | C2 div tk m12 stp atr | M15 | 7.9 | -0.2 | -1.0 | -5.6 | -7.4 | +2.2 / -0.4 | -1.7 / -13.8 | FAIL ; few trades |
| 418 | cand | C2 div cl m6 minsess0 stp struct | M15 | 17.3 | -3.5 | +2.1 | -0.1 | -3.1 | -1.1 / +0.5 | -0.4 / -9.5 | FAIL |
| 419 | cand | C2 div cl m3 stp struct | H1 | 11.1 | -6.7 | +5.7 | -5.4 | -14.6 | -5.5 / +4.1 | -4.6 / -15.4 | FAIL |
| 420 | cand | C2 div cl m3 stp atr | H1 | 11.1 | -4.3 | +3.2 | -4.1 | -11.1 | -4.6 / -0.0 | -4.4 / -11.5 | FAIL |
| 421 | cand | C2 div cl m6 stp struct | H1 | 5.0 | -6.7 | +7.8 | -4.3 | -12.3 | -2.9 / +8.2 | -1.2 / -3.9 | FAIL |
| 422 | cand | C2 div cl m6 stp atr | H1 | 5.0 | -6.1 | +6.0 | -2.3 | -8.7 | +1.6 / +6.0 | +1.4 / -2.4 | FAIL |
| 423 | cand | C2 div cl m12 stp struct | H1 | 1.4 | -3.2 | -1.8 | -11.5 | +4.0 | -4.8 / -1.3 | -5.4 / +8.8 | FAIL ; few trades |
| 424 | cand | C2 div cl m12 stp atr | H1 | 1.4 | +5.1 | -1.8 | -3.6 | -1.1 | +2.9 / -2.1 | +6.8 / +3.8 | FAIL ; few trades |
| 425 | cand | C2 div tk m3 stp struct | H1 | 8.8 | -5.5 | +2.0 | +1.7 | -6.0 | -5.1 / -0.8 | +8.9 / -12.2 | FAIL |
| 426 | cand | C2 div tk m3 stp atr | H1 | 8.8 | -4.3 | +0.2 | +0.0 | -7.4 | -2.6 / -2.8 | +6.2 / -11.5 | FAIL |
| 427 | cand | C2 div tk m6 stp struct | H1 | 4.2 | -0.1 | +4.9 | -2.3 | -6.0 | +2.8 / +0.8 | +6.5 / -14.7 | FAIL |
| 428 | cand | C2 div tk m6 stp atr | H1 | 4.2 | +1.3 | +2.7 | -2.3 | -5.2 | +3.7 / -3.0 | +5.4 / -5.5 | FAIL |
| 429 | cand | C2 div tk m12 stp struct | H1 | 1.0 | -1.6 | -7.0 | -15.6 | -21.1 | -7.3 / +3.1 | +1.8 / -23.4 | FAIL ; few trades |
| 430 | cand | C2 div tk m12 stp atr | H1 | 1.0 | +4.1 | -5.3 | -10.6 | -16.1 | -7.3 / +3.6 | -0.0 / -21.1 | FAIL ; few trades |
| 431 | cand | C2 div cl m6 minsess0 stp struct | H1 | 5.0 | -6.7 | +7.8 | -4.3 | -12.3 | -2.9 / +8.2 | -1.2 / -3.9 | FAIL |
| 432 | cand | C2 div cl m15 stp struct | M1 | 28.5 | -4.2 | -1.8 | -4.1 | -4.3 | -2.1 / -2.5 | -3.1 / -1.7 | FAIL ; few trades |
| 433 | cand | C2 div cl m15 stp atr | M1 | 28.5 | -3.6 | -0.7 | -2.7 | -3.5 | -2.6 / -2.8 | -3.5 / -2.5 | FAIL ; few trades |
| 434 | cand | C2 div cl m30 stp struct | M1 | 23.6 | -4.1 | -2.5 | -6.4 | -6.5 | -6.6 / -1.8 | -4.0 / -4.2 | FAIL ; few trades |
| 435 | cand | C2 div cl m30 stp atr | M1 | 23.6 | -2.5 | -2.1 | -5.0 | -4.1 | -5.4 / -3.1 | -3.6 / -5.2 | FAIL ; few trades |
| 436 | cand | C2 div cl m60 stp struct | M1 | 17.3 | -2.9 | -2.4 | -7.0 | -5.5 | -1.5 / +0.9 | -7.3 / -2.5 | FAIL ; few trades |
| 437 | cand | C2 div cl m60 stp atr | M1 | 17.3 | -2.6 | -2.8 | -5.1 | -4.2 | +0.3 / -0.6 | -4.1 / -6.0 | FAIL ; few trades |
| 438 | cand | C1 dPOC p90(k23.1) mkt atr | M1 | 60.3 | +1.7 | +0.4 | +0.4 | +0.3 | +2.8 / +0.3 | -2.7 / +2.0 | all 4 > 0, pooled z 0.9 |
| 439 | cand | C1 dPOC p95(k35.4) mkt atr | M1 | 31.0 | +1.5 | +0.7 | +4.2 | +1.7 | +1.4 / +3.1 | +3.4 / +5.6 | all 4 > 0, pooled z 1.3 ; few trades |
| 440 | F6 combo | C1xSIG away -> OPP mkt atr | M5 | 69.7 | +5.2 | +4.5 | +3.3 | +3.4 | +5.3 / +3.8 | +2.2 / +4.2 | all 4 > 0, pooled z 5.4 |
| 441 | F6 combo | C1xSIG away -> OPP stp atr | M5 | 19.9 | +3.6 | +0.5 | +3.3 | -2.3 | +5.1 / +1.3 | +3.9 / -1.8 | FAIL ; few trades |
| 442 | F6 combo | C1xSIG away -> OPP mkt atr | M15 | 35.7 | -0.5 | +1.2 | +1.9 | +1.1 | +1.4 / -0.1 | +5.2 / -0.3 | FAIL |
| 443 | F6 combo | C1xSIG away -> OPP stp atr | M15 | 9.1 | -2.1 | +1.0 | +8.4 | +0.1 | -1.8 / +0.3 | +6.4 / -6.1 | FAIL |
| 444 | C3 | C3 p80 declust12 mkt | M5 | 43.2 | +5.1 | +4.6 | +5.2 | +2.6 | +6.2 / +4.0 | +3.5 / +4.2 | **all 4 > 0, pooled z 4.4 (candidate)** |
| 445 | C3 | C3 p70(k4.2) declust mkt | M5 | 69.0 | +4.7 | +3.8 | +2.7 | +1.6 | +5.2 / +3.9 | +1.6 / +1.9 | all 4 > 0, pooled z 4.3 |
| 446 | C3 | C3 p90(k8.6) declust mkt | M5 | 17.8 | +6.0 | +3.7 | +7.3 | +2.8 | +5.6 / +5.1 | +3.8 / +3.9 | all 4 > 0, pooled z 3.0 ; few trades |
| 447 | C3 | C3 p95(k12.0) declust mkt | M5 | 7.8 | +11.6 | +6.0 | +6.8 | +4.2 | +13.0 / +6.9 | +6.5 / +7.6 | all 4 > 0, pooled z 3.1 ; few trades |
| 448 | C3 | C3 p80 declust mkt atr1.2 | M5 | 43.2 | +4.3 | +3.4 | +6.0 | +4.3 | +5.6 / +3.6 | +6.0 / +5.7 | all 4 > 0, pooled z 4.2 |
| 449 | C3 | C3 p80 declust mkt atr2.5 | M5 | 43.2 | +4.2 | +4.7 | +6.4 | +1.9 | +5.7 / +4.5 | +4.3 / +3.9 | all 4 > 0, pooled z 4.1 |
| 450 | C3 | C3 p80 declust minsess0 mkt | M5 | 52.6 | +4.4 | +2.8 | +4.7 | +1.4 | +5.0 / +1.8 | +4.7 / -0.5 | all 4 > 0, pooled z 3.6 |
| 451 | C3 | C3ctrl NEAR POC (<p80) OPP mkt | M5 | 128.9 | +1.5 | -0.3 | -2.9 | -0.3 | +2.0 / -0.9 | -1.8 / -1.4 | FAIL |
| 452 | C3 | C3 VWAP-dist p80 declust mkt | M5 | 51.3 | +3.8 | +4.6 | +2.8 | +2.7 | +3.5 / +3.5 | +0.1 / +1.9 | all 4 > 0, pooled z 4.0 |
| 453 | C3 | C3 priorPOC-dist p80 declust mkt | M5 | 26.6 | +3.1 | +3.3 | +4.5 | +3.1 | +0.6 / +5.3 | +7.1 / +4.5 | all 4 > 0, pooled z 2.6 |
| 454 | C3 | C3gen impulse bar 0.8ATR away p80 OPP mkt | M5 | 56.5 | +2.2 | +3.5 | +4.5 | +1.1 | +2.8 / +2.1 | +3.6 / +1.8 | **all 4 > 0, pooled z 3.1 (candidate)** |
| 455 | C3 | C3gen impulse bar 1.2ATR away p80 OPP mkt | M5 | 27.8 | +2.4 | +5.7 | +3.2 | +1.4 | +3.8 / +6.3 | +1.8 / -1.4 | all 4 > 0, pooled z 2.7 |
| 456 | C3 | C3 p80 declust4 mkt | M15 | 28.1 | -0.8 | +1.7 | +1.2 | +0.3 | +1.1 / +0.7 | +1.9 / -2.5 | FAIL |
| 457 | C3 | C3 p70(k2.5) declust mkt | M15 | 43.2 | +1.1 | +1.8 | -1.0 | -0.7 | +2.3 / +0.6 | -1.0 / +1.0 | FAIL |
| 458 | C3 | C3 p90(k4.8) declust mkt | M15 | 12.8 | -1.6 | +2.8 | +0.7 | +0.1 | -1.0 / -0.2 | +7.0 / -3.0 | FAIL |
| 459 | C3 | C3 p95(k6.3) declust mkt | M15 | 5.8 | -1.2 | +5.8 | -5.2 | +1.1 | -1.2 / +5.5 | -4.6 / +0.3 | FAIL ; few trades |
| 460 | C3 | C3 p80 declust mkt atr1.2 | M15 | 28.1 | +0.4 | +2.3 | -0.8 | +2.6 | +2.7 / +0.7 | +0.9 / -1.0 | FAIL |
| 461 | C3 | C3 p80 declust mkt atr2.5 | M15 | 28.1 | -0.4 | +0.6 | +1.9 | -1.0 | +1.7 / -0.7 | +1.4 / -3.9 | FAIL |
| 462 | C3 | C3 p80 declust minsess0 mkt | M15 | 33.0 | -0.8 | +2.4 | +0.3 | +0.1 | -0.3 / +2.7 | -0.0 / +0.0 | FAIL |
| 463 | C3 | C3ctrl NEAR POC (<p80) OPP mkt | M15 | 58.2 | +3.7 | +0.8 | -4.9 | -0.4 | +5.0 / +0.1 | -2.6 / -1.5 | FAIL |
| 464 | C3 | C3 VWAP-dist p80 declust mkt | M15 | 35.6 | -0.2 | +2.3 | -2.2 | +2.3 | +1.0 / +3.0 | -1.2 / +1.8 | FAIL |
| 465 | C3 | C3 priorPOC-dist p80 declust mkt | M15 | 15.2 | -0.8 | +2.2 | -2.9 | +2.2 | +3.2 / +3.9 | -2.4 / +2.6 | FAIL |
| 466 | C3 | C3gen impulse bar 0.8ATR away p80 OPP mkt | M15 | 33.4 | +1.9 | +2.0 | +1.6 | +1.9 | +2.5 / +0.6 | +3.6 / +0.9 | **all 4 > 0, pooled z 1.6 (candidate)** |
| 467 | C3 | C3gen impulse bar 1.2ATR away p80 OPP mkt | M15 | 19.3 | -1.9 | +1.2 | +2.5 | +3.8 | -0.6 / -2.0 | +4.1 / +2.2 | FAIL |
| 468 | C3 | C3 p80 declust60 mkt | M1 | 82.6 | +3.8 | +0.8 | +1.4 | +3.1 | +4.8 / -0.2 | -1.1 / +5.0 | all 4 > 0, pooled z 3.2 |
| 469 | C3 | C3 p70(k10.2) declust mkt | M1 | 128.0 | +2.6 | +2.1 | +1.1 | +4.9 | +2.9 / +1.9 | -0.0 / +4.5 | all 4 > 0, pooled z 4.5 |
| 470 | C3 | C3 p90(k23.1) declust mkt | M1 | 39.9 | +4.6 | +1.2 | +0.6 | +5.2 | +5.4 / +0.9 | +0.1 / +6.1 | all 4 > 0, pooled z 2.9 ; few trades |
| 471 | C3 | C3 p95(k35.4) declust mkt | M1 | 19.8 | +4.6 | +5.2 | +4.0 | +1.7 | +4.3 / +5.3 | +5.8 / +2.2 | all 4 > 0, pooled z 2.7 ; few trades |
| 472 | C3 | C3 p80 declust mkt atr1.2 | M1 | 82.6 | +3.0 | -0.1 | +0.9 | +1.4 | +4.8 / -0.7 | -1.1 / +3.2 | FAIL |
| 473 | C3 | C3 p80 declust mkt atr2.5 | M1 | 82.6 | +3.4 | +1.5 | +4.1 | +0.8 | +3.8 / +0.6 | +0.3 / +2.9 | all 4 > 0, pooled z 3.2 |
| 474 | C3 | C3 p80 declust minsess0 mkt | M1 | 96.0 | +3.8 | +0.6 | +4.0 | +1.1 | +4.1 / +0.8 | +3.6 / +0.8 | all 4 > 0, pooled z 3.3 |
| 475 | C3 | C3ctrl NEAR POC (<p80) OPP mkt | M1 | 283.0 | -0.5 | +1.1 | +0.5 | +0.7 | -0.2 / +0.7 | +1.2 / +1.4 | FAIL |
| 476 | C3 | C3 VWAP-dist p80 declust mkt | M1 | 91.0 | +3.4 | +2.1 | +1.8 | +2.8 | +2.1 / +1.6 | +0.7 / +3.1 | all 4 > 0, pooled z 3.7 |
| 477 | C3 | C3 priorPOC-dist p80 declust mkt | M1 | 61.1 | +1.5 | +3.4 | +2.5 | +2.3 | +1.4 / +3.6 | +2.9 / +1.1 | all 4 > 0, pooled z 2.9 |
| 478 | C3 | C3gen impulse bar 0.8ATR away p80 OPP mkt | M1 | 99.4 | +1.1 | +0.9 | +1.8 | +1.4 | +0.5 / +1.0 | +0.4 / +1.5 | all 4 > 0, pooled z 1.8 |
| 479 | C3 | C3gen impulse bar 1.2ATR away p80 OPP mkt | M1 | 75.7 | +2.8 | +2.0 | +1.6 | -0.7 | +1.5 / +1.1 | +0.5 / -1.5 | FAIL |
| 480 | C3 | C3 p80 declust2 mkt | H1 | 15.3 | +1.8 | +3.0 | +2.7 | +6.7 | +3.0 / +4.2 | +4.1 / +3.8 | all 4 > 0, pooled z 2.0 |
| 481 | C3 | C3 p70(k1.3) declust mkt | H1 | 19.9 | -0.3 | +2.4 | +4.5 | +2.8 | -0.5 / +3.8 | +6.6 / +3.8 | FAIL |
| 482 | C3 | C3 p90(k2.7) declust mkt | H1 | 8.2 | +1.1 | +0.4 | +0.2 | +4.5 | +2.5 / +0.1 | -3.3 / +1.3 | all 4 > 0, pooled z 0.6 |
| 483 | C3 | C3 p95(k3.6) declust mkt | H1 | 3.8 | +0.6 | +4.3 | -10.6 | +4.8 | +0.7 / +3.7 | -8.6 / -4.6 | FAIL |
| 484 | C3 | C3 p80 declust mkt atr1.2 | H1 | 15.3 | +1.9 | +2.1 | -2.5 | +7.3 | +4.4 / +3.2 | +0.3 / +5.8 | FAIL |
| 485 | C3 | C3 p80 declust mkt atr2.5 | H1 | 15.3 | +4.0 | +3.0 | +0.8 | +3.2 | +4.4 / +3.2 | -1.4 / +2.9 | all 4 > 0, pooled z 1.8 |
| 486 | C3 | C3 p80 declust minsess0 mkt | H1 | 17.2 | +0.9 | +3.5 | +2.9 | +4.7 | +2.0 / +2.9 | +3.3 / +4.9 | all 4 > 0, pooled z 1.8 |
| 487 | C3 | C3ctrl NEAR POC (<p80) OPP mkt | H1 | 13.9 | +1.9 | +3.5 | +2.4 | -1.9 | +1.1 / +2.7 | +8.8 / -2.5 | FAIL |
| 488 | C3 | C3 VWAP-dist p80 declust mkt | H1 | 17.5 | -0.7 | +2.5 | +3.6 | +4.7 | -0.3 / +2.4 | +2.5 / +4.0 | FAIL |
| 489 | C3 | C3 priorPOC-dist p80 declust mkt | H1 | 8.3 | -0.8 | +4.8 | -0.0 | +4.7 | +2.4 / +4.3 | +3.4 / +6.3 | FAIL |
| 490 | C3 | C3gen impulse bar 0.8ATR away p80 OPP mkt | H1 | 16.5 | +0.7 | +1.6 | +2.4 | +4.9 | -0.4 / +2.4 | +2.5 / +1.7 | all 4 > 0, pooled z 1.3 |
| 491 | C3 | C3gen impulse bar 1.2ATR away p80 OPP mkt | H1 | 11.6 | -2.0 | -0.1 | +1.3 | +9.2 | +2.5 / -2.4 | +4.1 / +8.0 | FAIL |
| 492 | C3 | C3 x strong bar delta | M5 | 21.6 | +5.5 | +3.4 | +7.5 | +2.4 | +5.7 / +2.6 | +7.1 / +5.5 | all 4 > 0, pooled z 3.2 |
| 493 | C3 | C3 x weak bar delta | M5 | 21.6 | +4.6 | +5.8 | +2.2 | +2.9 | +5.2 / +4.6 | +1.6 / +4.4 | all 4 > 0, pooled z 3.0 |
| 494 | C3 | C3 x CVD with move | M5 | 31.2 | +5.0 | +5.8 | +6.7 | +2.2 | +6.9 / +5.2 | +6.1 / +2.4 | all 4 > 0, pooled z 4.1 |
| 495 | C3 | C3 x CVD against move (diverg) | M5 | 12.0 | +5.1 | +2.2 | +1.2 | +8.5 | +4.8 / -0.1 | -1.2 / +7.4 | all 4 > 0, pooled z 1.6 ; few trades |
