# Research checkpoint: Auction Retest project

**Read this first when resuming.** It records what has been built, where every file is, how to rebuild the working
environment, and what was decided. Last updated 2026-11-22 (session `21ed2550`, Auction Retest v5.4 + v6.0 order block / grid files, Fractal Grid v3.2 / EA v1.1). No task is in progress: everything asked
so far has been delivered.

## 1. Resume in one step

```bash
bash Research/restore.sh      # about 3 minutes
```

The script recreates the research scratchpad at its original absolute path
`/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad`. Every research script uses
that path, so it works in a fresh container. The script:

- copies `Research/scratchpad/` back (all code and text files, same layout);
- unzips the gold data and rebuilds the M1, M5, M15 and H1 bars with `gold/convert.py`;
- unpacks the compact gold results (`Research/results/gold/*.xz`).

Rebuild the gold workbook from the saved results, without running the engine again:

```bash
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad
cd $S/gold && python3 -I build_final.py $S/Gold_2021_2026_Auction_Retest.xlsx
python3 <xlsx skill>/scripts/recalc.py $S/Gold_2021_2026_Auction_Retest.xlsx 300    # the xlsx skill's recalc.py; must report 0 errors
```

The restore was tested on 2026-10-24 with the live scratchpad moved away. After `restore.sh`:

- the rebuilt workbook matched the delivered one in all 49,591 cells;
- `pickcfg.choose()` returned the same picks;
- re-running the engine gave identical trades for the default, best and low-streak settings on H1 and M15;
- `build/assemble.py` reproduced both `.pine` files byte for byte;
- `build/safe/AuctionRetestEA.mq5` was identical to the repo's EA.

To refresh this checkpoint after new work, run `python3 -I $S/tools/make_checkpoint.py`, then commit `Research/`.

## 2. What is in the repository

| Path | What it is |
|---|---|
| `TradingView/Auction_Retest_Model.pine` | Indicator, v3.8: clone of *Auction Retest Pro* (session VWAP + displacement + timed retest), with tables and optional filters (v3.6: max distance from the VWAP; v3.8: stop beyond / VWAP touched / entry too close to the VWAP; kill zones follow London / New York summer time). |
| `TradingView/Auction_Retest_Strategy.pine` | The same engine as a strategy: risk sizing, partials, 21 loss-recovery rules (incl. Crooks A, B, C, D and the Crooks TP1 rule), streak pauses, news and force-close. |
| `MetaTrader5/AuctionRetestEA.mq5` | MT5 EA v3.9: port of the same engine plus the strategy's money management (21 recovery rules incl. Crooks A-D, Crooks TP1 rule), on-chart table and trade markings. |
| `TradingView/README.md` | User documentation of every rule and setting, v3 to v3.9 (Crooks A-D in the Loss recovery row; sections per version; v3.8: the three VWAP skip rules, kill zones and daily news follow summer time, TP1 rule % and any final exit, with the gold results). |
| `Research/deliverables/` | `Gold_2021_2026_Auction_Retest.xlsx` (gold study), `VWAP_vs_EMA_results.md`, `VWAP_settings_and_70pct_strategies.md`. |
| `Research/scratchpad/` | Every code and text file of the working scratchpad, each up to 2 MB. |
| `Research/inputs/` | The data files the user uploaded (screenshots not included), plus the Pine parser wheels. |
| `Research/results/gold/` | Compact gold results (xz pickles). `slim_*` files hold metrics only; `final_<TF>` holds the picks, trades, exits, recovery and robustness. |

Commits: v3 `ba3d37d`, v3.1 `9de5f6f` and `1ac5b0b`, v3.2 kill zones `d4624cf`, v3.3 minimum VWAP distance `952df97`,
the checkpoint `7075a27`, Rule C study `c75209e`, strategy catalogue `fac7170`, then Crooks A and B ("v3.4: Crooks A and Crooks B loss recovery"), the Crooks TP1 rule `c6a0a5c`, `f251880`, `233d2e3`,
then v3.6 ("v3.6: Crooks C and D, max VWAP distance filter, no inline-title warnings"), Crooks C leftover `7c0a5cd`, v3.7 `b7853ba` and `374f458`, EA v3.7.1 `3593218` (server clock option for EU summer time), then v3.8 ("v3.8: VWAP skip rules, kill zones and daily news follow summer time, TP1 rule % and any final exit"). Branch `claude/vwap-orderflow-signals-pxlzgq`. Open a PR only when the user asks.

## 3. How the code is built and checked (`Research/scratchpad/`)

- **Pine build.**
  - Sources: `build/shared_inputs.pine`, `build/shared_engine.pine`, `build/indicator_template.pine` and `build/strategy_template.pine`.
  - `build/assemble.py` writes both `.pine` files. The shared blocks (ENGINE INPUTS, ENGINE, STATS, DRAW) must be byte-identical; assemble.py checks this.
  - Pine rules followed:
    - no history references inside functions;
    - `time()` and history kept out of `and`/`or` chains;
    - ghost (invisible skip) filters: `zNo`, `chopNo`, `emaNo`, `nearNo`, `farNo`, and since v3.8 `stopNo`, `tchNo`, `entNo` (touch counters `tchL` / `tchS` update on every bar, warm or not);
    - inputs that share an `inline` id carry a title only on the first one (TradingView warns otherwise). `pinecheck/inline_lint.py FILE.pine` reproduces the warning and must print 0;
      `pinecheck/inputs_cmp.py OLD NEW` lists every input change other than titles.
- **EA source.**
  - The canonical copy is `build/safe/AuctionRetestEA.mq5`. Copy it to `MetaTrader5/`; keep the source ASCII-only.
  - Before committing, grep for `_mq`, `#line` and `mql5rt`: a test harness once overwrote the EA with generated code.
- **EA checks.**
  - `mq5check/mq5check.py`: offline MQL5 checker using a clang++ shim.
  - `mq5check/run/`: executable parity harness (build.sh, parity.py with 48 configurations, driver.cpp). It runs the EA against the Python twin. `mq5rt.py` was fixed so it never writes `.mq5` files.
    `PARITY_SHIFT_DAYS=49` / `-189` moves every bar by whole weeks so the data cross the October / November and the March summer-time switches (kill zones in auto mode).
  - `mq5check/dst/`: the EA's `UkSummer()` / `NySummer()` compiled with a wrapper and compared with Python's zoneinfo every 15 minutes 2019-2035 (68 switches, 0 differences).
  - `mq5check/rec/`: money-management parity. `build.sh` compiles the EA's own `NextRisk()` / `BookClosed()` (copy of the EA, never written) with `rec_driver.cpp`;
    `parity_rec.py` compares the $ risk of every trade with `gold/recovery.py` on real gold sequences: every rule except % of equity, split 1-5, no cap / $500 Clamp /
    Start again / Stop, Crooks A-D. Result 2026-10-30: 1,584 runs, 2,029,437 trades, 0 differences (the harness has no account, so runs the simulator ends as blown are compared up to that trade).
    `parity_tp1.py` (REC_T1 mode of the driver; build.sh makes a harness-only copy of the runtime header with settable tick value / bid / ask, and an OrderCalcMargin stub):
    the EA's TP1-rule decision and $ risk vs `gold/crooks_tp1.py` on the trades the simulator took, Crooks A-D. Result 2026-10-30: 336 runs, 590,427 trades (184,324 TP1-rule), 0 differences.
- **Python twin of the engine.** `build/ref.py` and `build/ref_ev.py`; `build/emsim_eth.py` simulates the strategy's execution.
- **Pine syntax check offline.** `pynescript` (wheels in `inputs/wheels`): `python3 -I pinecheck/parse_both.py FILE.pine ...` (both files take a few minutes).
- **Earlier fitting work.**
  - `fit/`, `hunt2/` … `hunt8/`, `halfstop3/`, `gt/` and `z_*` folders hold the rule hunts against the 80 screenshot trades and the student logs, plus the tests per asset.
  - Each sub-study has its own `progress.md`.

## 4. Research studies and conclusions

1. **Consolidation (VWAP crosses) and 1h-EMA filters** (`research/chop`, `research/ema`): added in v3.1 as optional filters, off by default. Their measured effect is in `TradingView/README.md`.
2. **VWAP vs EMA50/100/200** → `deliverables/VWAP_vs_EMA_results.md`. No moat for any EMA variant; VWAP is best.
3. **VWAP settings and "70% win" strategies** → `deliverables/VWAP_settings_and_70pct_strategies.md`. No tested strategy reaches 70% at 1:1 or better. VWAP band from 1 ATR to 2σ: 57.5% at 1:1, 43.9% at 1:2.
4. **Gold, FxPro MT5, 4 Jan 2021 – 2 Oct 2026** (`gold/`, workbook in `deliverables/`). All results after the spread recorded in the data; settings chosen on 2021–23 and checked on 2024–26.

| Timeframe | Default R per trade | Best settings (most profit) | R per trade | Longest win / loss |
|---|---|---|---|---|
| M1 | −0.46 | Stop 4 ATR, cooldown 8, VWAP anchor Month, kill zone London Close only | +0.057 | 8 / 14 |
| M5 | −0.11 | Stop 2.4, TP4 2.5R, VWAP Month, market entry, choppy-session max 8, trade only 18:30–22:30 IST | +0.087 | 7 / 21 |
| M15 | −0.055 | Stop 4 ATR, half stop 1.2, move stop to +1R at TP3 | +0.134 | 8 / 17 |
| H1 | −0.045 | Displacement 0.65, momentum lookback 5, stop 2.4, cooldown 12, don't chase 2.0σ | +0.337 | 8 / 8 |

Low-streak versions ("Close 70% at TP1" exists only in the strategy and the EA):

| Timeframe | Settings | Longest win / loss | R per trade |
|---|---|---|---|
| H1 | Structure 20, stop 2.2, max 1 fill a day, VWAP Month, don't chase 1.25σ, close 70% at TP1 | 12 / 3 | +0.176 |
| M15 | Min CMO 30, stop 4, half stop 1.2, +1R at TP3, 1h EMA20 cap 1.2, close 70% at TP1 | 18 / 5 | +0.066 |
| M5 | Stop 2.4, VWAP Month, market entry, stop to +0.6R at TP2, choppy 8, 18:30–22:30 IST | 11 / 9 | +0.045 |
| M1 | Stop 4, cooldown 30, VWAP Month, London Close kill zone | 7 / 12 | +0.052 |

Other gold findings:

- **Losses do not cluster.** The longest losing streak follows from the win rate; pause rules don't help.
- **Recovery rules:** fixed risk (Off) gives the best profit for the drawdown on average. % of equity and Paroli stayed within the limits (survived, at most $500 a trade, at most 40% drawdown) in all 8 cases; since 2026-10-28 so does Crooks B (split 3, $500 cap), with 0.95 x Off's profit per drawdown and 1.38 x its profit, the best rule after Off. Martingale-type rules are worst.
- **M1 default is broken by the 5-fills-a-day cap.** All 5 fills happen every day between 03:00 and 09:00 IST, where the spread costs 0.25–0.6 R per trade.
- **Robustness:** 76–94% of single changes around the picks stay profitable in both halves (M1: 62%). A tighter stop breaks every pick.
- **Picks are fitted to both halves.** Choosing on 2021–23 alone kept only part of the gain in 2024–26, so expect weaker live results.

5. **Rule C and Rule C split, split 1–5** (asked 2026-10-24; workbook sheet *Rule C split test*). The first recovery study used only the default split of 3.
   - **Default settings:** every Rule C variant blew the $10k account.
   - **Best settings, $500 hard cap (Clamp), split 3:**
     - M15: +$83.7k, max drawdown 33%. Fixed risk: +$9.1k, 9%.
     - H1: +$17.9k, 20%. Fixed risk: +$3.1k, 3%.
     - M1: +$59k, 59%.
     - M5: blew the account. With cap action "Start again": +$51.5k, 36%.
   - **Per $ staked** it lost about the same as fixed risk. The extra profit comes from bigger stakes: the base grows with profit.
   - **Without the cap,** split 1–3 blew M1, M5 and M15.
   - **Split 3 beats split 2** in most cases: similar profit, smaller drawdown.
   - **Best profit for the drawdown:** M15, split 3, $500 cap, "Start again": ratio 9.45 against 8.18 for fixed risk.
   - **Stress test** (extra 0.05 / 0.10 R cost per trade): H1 stays safe, M15 holds to about 0.05 R, M1 and M5 blow up.
   - **Workbook reorganised by strategy (2026-10-24):**
     - Sheets, in order:
       - *Strategy guide*: pick by goal × timeframe, with links;
       - *M1/M5/M15/H1 strategies*: every indicator input with its exact name, changed ones in yellow, then expected results, streaks and money;
       - *All profitable settings*: a filterable list;
       - then the money-management and research sheets.
     - Goals: most profit; shortest losing streak (with partial close, and indicator-only); longest winning streak; highest win rate; most trades a day; every year positive; smoothest (total R / deepest fall); simplest; and one session only.
     - Built by `gold/strategy_sheets.py`, called from `build_final.py`.
   - **Recovery simulator changes:**
     - partial closes now update Rule C's carried losses per part, as the strategy does (only the H1 and M15 low-streak Rule C rows moved, slightly);
     - the average stake per trade (`avgRisk`) is recorded.

6. **Crooks A and Crooks B** (asked 2026-10-28; added to the strategy and the EA v3.4; workbook sheet *Crooks A and B test*).
   - **Rule** (user's spec + answers): trades 1 and 2 of a cycle risk the base; from trade 3 every other trade (k = closed trades in the cycle, k >= 2 and even) is a recovery trade.
     A: risk max(base, L / exitR); B: max(base, L / split / exitR) (split = Rule C split input). L = max(0, L - pnl) after every trade. Reset (L = 0, k = 0): L < $0.01, and in A
     also a winning recovery trade. exitR = R of the final TP (partials not counted). Hard cap only when on; Start again also resets L and k. Trade type stored when the order is placed.
   - **Code:** `recovery.py` (MODES 18-19), `strategy_template.pine` (L_CRA / L_CRB, crkL / crkN / crkRec, f_crkRecNext), EA (REC_CRA / REC_CRB, CrkRecNext). Table row CROOKS: LOSS TO WIN BACK.
   - **Checks:** hand example $50, $50, $100, $50, $250 (TP2); EA = simulator on 1.9 M trades; Pine parsed, shared blocks identical; an independent review agent found no rule or compile problem
     (its one robustness point, a float leftover blocking the reset, led to the < $0.01 rule in all three).
   - **Results:** gold trades do not win more often after losses, so Crooks only adds profit by risking more. Without the cap Crooks A blew the account in up to 48% of random
     orders (M1); with $500 + Start again at most 0.8% (M1), none on M5, M15 and H1. Best settings, $500 Start again, Crooks A: M15 +$12.3k (fall 16%) vs Off +$9.1k (9%); H1 +$4.3k (5%) vs +$3.1k (3%).
     M1 +$15.8k is luck of the order (beats 99% of random orders; median +$7.4k). Per $ of drawdown Off is still as good or better on most strategies.
   - **Also fixed:** `final.py` now gives every recovery rule the strategy's exitR (`exitR_strategy`); before, Exact recovery and Oscar's Grind used the partial-weighted win R on the 2
     low-streak settings with a partial close. `final_<TF>.pkl` 'recovery' now has 20 rules x 2 caps; catalogue money has `crA_reset`, `crB3_reset` and `mc` (random-order medians).

7. **Crooks TP1 rule** (asked 2026-10-29; strategy input "Crooks At Exit TP1: Bank The Loss At TP1, Rest To TP2", EA `InpCrkT1`, on by default; EA v3.5; workbook part 6).
   - **Rule** (user's answers: the whole amount banked at TP1, the rest's stop to the entry): Final Exit At TP1, Crooks recovery trades only. T = max(base, X) after the cap.
     Stop distance = TP1 / 2 - 1.5 x costs (rounded toward the entry); size = T / (stop distance x value + costs); half closes at TP1 (banks T), rest at TP2, its stop moves
     to the entry once TP1 is booked (Pine from the next bar, EA at once). Impossible geometry (costs >= TP1 / 3) -> plain Crooks. The strategy ignores the engine's TP1 exit
     for this trade (still follows an engine loss exit); new signals are skipped while the rest runs.
   - **Simulator:** `gold/crooks_tp1.py` replays these trades on bars with TradingView's fill rules (emsim) and skips signals while busy; hand tests in the session log.
   - **Review fixes (independent reviewer, then verified):** the trade keeps its own TP1 / TP2 (exT1Tp1 / exT1Tp2; the engine's t1 / t2 change with its next setup while
     the rest runs on); EA: TP1 half rounded UP to the lot step, booked at the bar close if no tick did it (engine TP1 win), breakeven move retried until accepted (exT1Be),
     SetExits skips no-op modifies, a restart never widens an adopted position's stop.
   - **Result:** 28,220 TP1-rule trades over every exit-at-TP1 setting: 25% reached TP1, 75% hit the tight stop (36% on the entry candle). Exit at TP1 is profitable
     only on 3 H1 settings; there, with $500 cap + Start again, random-order medians were negative with the rule and +$1.1k to +$1.3k without. Recommendation: off on gold.

8. **Crooks C and Crooks D** (asked 2026-10-30; strategy and EA v3.6; workbook sheet *Crooks A-D test*, renamed from *Crooks A and B test*).
   - **Rule** (user's spec): C: base until a trade wins; the trade after a win is a recovery trade while L > 0 (risk max(base, L / exitR)); a losing recovery trade -> base until
     the next win. D: base, base, recovery (k >= 2 and (k - 2) % 3 == 0: trades 3, 6, 9 ...). D resets like A (a winning recovery trade, or L < $0.01); C only when L < $0.01 since item 11; Start again also clears
     the last-win flag. The Crooks TP1 rule applies to their recovery trades too.
   - **Code:** `recovery.py` MODES 20-21 (state `crW`), `crooks_tp1.py`, `strategy_template.pine` (L_CRC / L_CRD, `crkW`, `f_crkRecNext`), EA (REC_CRC = 20 / REC_CRD = 21,
     `crkW`, `CrkRecNext()`). Table: C shows "base, waiting for a win".
   - **Checks:** hand examples; EA = simulator (rec and TP1 parity above, 0 differences); Pine parsed. Independent review (Sonnet, high effort, verified here): no rule bug.
     Fixed from it: the hard cap now acts only on a signal that can be taken (Pine `preSkip`, EA `NextRisk(exitR, canTake)`); before, a signal skipped while a
     TP1-rule half was still open could restart the cycle or stop trading on the unbooked state, which the simulators never do. Also: the EA rejects a max VWAP
     distance <= 0, the TP1-rule tooltip names C and D. Left as is (documented in the README): the EA keeps the recovery state in memory only.
   - **Results, 25 profitable strategies, $500 cap + Start again:** more net than Off: C 17, D 21 (A 20); better profit per $ of drawdown than Off: C 7, D 6 (A 10).
     Uncapped, D blew the account on 5 strategies (M1, M5, M15); in random orders without a cap C blew it in up to 39%, D in up to 44%.
     Best settings: H1 C +$3.6k (fall 3%), D +$3.8k (4%) vs Off +$3.1k (3%); M15 C +$11.7k (16%), D +$12.2k (13%) vs Off +$9.1k (9%).
9. **Distance from the VWAP** (asked 2026-10-30: "the losing trades were far from the VWAP"; filter "Skip Signals Too Far From VWAP: Max Distance" in v3.6, indicator,
   strategy and EA, off, default 5 ATR, unit x ATR or Price; workbook sheet *VWAP distance*).
   - **Study** (`gold/vwfilter.py collect | collect_tp2 | scan`): distance |close - VWAP| at the signal in ATR, price and sigma for 41 settings (default + catalogue per TF,
     plus TP2 exits of default / S1 / S2); every cut-off scored on 2021-23 and 2024-26; a cut-off picked on 2021-23 read on 2024-26.
   - **Result:** far trades are not worse. Session anchor: every cut-off from 2 to 4.5 ATR lowered the R per trade (+0.088 -> +0.066 to +0.085), worse in both halves on up
     to 10 of 13 settings; 5 ATR did the least harm, hence the default value. All 30 profitable settings: best cut-off 5 ATR, better in both halves on 9, worse on 3, total
     +2,386R -> +1,488R (47% fewer trades). Price cut-offs worst. Don't Chase 2.5 sigma: never worse in both halves, removed 18% for the same R per trade. Month anchor:
     most M1 / M5 signals are more than 5 ATR away. Verdict: keep it off on gold.
   - **Engine:** ghost filter `farNo` in the Pine engine, the EA and the Python twins (ref.py, ref_gs.py, ref_g.py), skip reason BEYOND MAX VWAP DISTANCE. Engine with the
     filter on = the same trades dropped afterwards (checked); EA = ref.py on 6 filter configurations (parity.py).
10. **TradingView warnings** (2026-10-30): the user's screenshots showed 34 inline-title warnings in the strategy (24 in the indicator). Every settings line now has one
    title (e.g. "Targets TP1 · TP2 · TP3 · TP4 (R)"); the day boxes, kill zones and Allow Long / Short got their own lines. Defaults, options and limits are unchanged
    (`pinecheck/inputs_cmp.py`). The workbook labels (`strategy_sheets.py`, `labels.py`) use the new titles.
11. **Crooks C keeps the leftover** (asked 2026-10-30, after the user's OANDA M5 trade lists: trade #82 owed $27,400 but the 1:100 leverage limit cut the
    recovery trade to about $6,200, it won, and the old rule then forgot the other $21,481). Now a Crooks C cycle ends only when the loss is all back
    (L < $0.01): a winning recovery trade that leaves part of the loss is followed by another recovery trade. A and D unchanged. Code: the reset in
    `recovery.py`, `crooks_tp1.py`, the strategy and the EA no longer lists C. Checks: hand cases; rec parity 1,584 runs, 2,027,096 trades, 0 differences;
    TP1 parity 336 runs, 576,082 trades, 0 differences. Gold, 25 profitable strategies, $500 cap + Start again: more net than Off on 18 (was 17), better
    profit per drawdown on 5 (was 7); best M15 +$13.1k, fall 16% (was +$11.7k). Replay of the user's TP2 list (`tools/csvcheck/whatif.py`, reproduces the
    file within $1 on 736 of 773 trades): their settings (no cap, 1:100, $100k) -52.4k with the old rule, about -$100k (account gone) with the new one;
    with $500 + Start again -$7.3k vs -$7.4k; fixed $50 -$3.8k. The list's stop-outs fill $0.10 past the stop (Properties slippage) and pay $0.07/oz,
    neither in the strategy's cost inputs.

12. **TP1-rule stop variants** (asked 2026-11-04; `gold/crooks_t1var.py`, research only, nothing changed in the strategy or EA yet). Every variant keeps the
    TP1-rule size (the half at TP1 banks the owed amount T, the rest runs to TP2 with its stop at the entry); only the stop before TP1 differs: tight 0.3R
    (current), 0.45R, 0.6R, the normal stop (wide), normal stop on the fill bar then tight, normal stop until a bar closes in profit then tight (the user's
    idea) or then breakeven, and plain (checkbox off). The hard cap limits the real stop-out loss (T x loss multiple). 14 exit-TP1 gold settings.
    Per recovery trade: wide -0.061 T (better than plain on 9 of 14), plain -0.068, user's idea -0.138, tight -0.158. On the 3 settings profitable at
    exit TP1 (all H1), Crooks C $500 + Start again: wide +$1,760 / +$2,283 / +$2,053 (falls 7-9%, both halves positive, random medians +$1.0k to +$1.4k)
    vs plain +$589 / +$896 / +$921; user's idea -$109 / +$399 / +$1,551; tight +$44 / -$1,365 / -$1,204. No variant rescues the 11 losing settings.
    The wide variant's stop-out loses about 3.5 T, so with a $500 cap T is at most about $145.

13. **v3.7 settings** (asked 2026-11-04; strategy and EA v3.7). (a) *Crooks TP1 Rule: Stop Before TP1* (`crkT1Stop`, EA `InpCrkT1Stop`): the 7 stop choices of
    item 12; size unchanged (tight-based), the hard cap limits the real stop-out loss (`t1Mul`, `CrkT1Mult()`), moves at a bar close, toward the entry only, never
    after the TP1 half. (b) *Crooks C: Win The Loss Back Over N Wins* (`crkCnOn`/`crkCn`, state `crkP`; EA `InpCrkCnOn`/`InpCrkCn`, `CrkParts()`): recovery
    amount = owed / parts left; a winning recovery trade -1 part, any loss -> N parts. (c) Lot rounding: strategy `lotRound` (default Down), EA `InpLotRound`
    (default nearest) + `InpSmallLot` (minimum lot or skip); never past the cap or leverage. Python: `recovery.py` and `crooks_tp1.py` take `cN`; `crooks_tp1`
    caps T x `m`. Checks: `mq5check/rec/parity_rec.py` 1,680 runs / 2.15 M trades and `parity_tp1.py` 2,464 runs / 4.1 M trades (all stop choices x caps,
    N 1-3), 0 differences; `lots_harness` (built by rec/build.sh, settable lot step / minimum / equity) 11 hand cases. Gold, `gold/crooks_cn.py`: over the 25
    profitable strategies with $500 + Start again N 1-4 make +$124k to +$128k (fixed $50 +$108k); uncapped blow-ups in random orders 16% -> 9% -> 4% -> 2%.

14. **v3.8** (asked 2026-11-06; indicator, strategy and EA v3.8). (a) Three ghost skip rules on the signal candle (`stopVwOn`/`stopVwBuf` 0,
    `touchVwOn`/`touchVwN` 3, `entVwOn`/`entVwAtr` 0.75; EA `InpStopVwOn` ... , `trSkip` 6 / 7 / 8): stop beyond the VWAP (d x (stop - VWAP) < buffer x ATR), VWAP
    touched in the last N candles (`tchL` / `tchS`: candles since low <= VWAP / high >= VWAP, 0 = this candle), entry too close (d x (entry - VWAP) < X x ATR).
    Gold, `gold/vwfilter2.py` (collect: per trade `vs` / `vt` / `ve` from `ref_gs`; check: the engine with each rule on keeps exactly the trades the scan keeps,
    9 of 9; scan): Session VWAP, the 13 settings profitable in both halves, pooled: stop >= 0 +0.088R -> +0.138R per trade but 19% kept (total +1,225R -> +357R),
    better in both halves on 9 of 13; >= -1 +0.120R, 36% kept; touch N 3 +0.108R, 57%; entry 0.75 ATR +0.094R, 86%; none worse in both halves on any of the 13.
    Month VWAP: the stop rule was worse in both halves on 9 of 17. (b) Kill zones follow London / New York summer time (`kzAuto`, default on; EA `InpKzAuto`):
    Pine `ukOff` / `nyOff` from `hour(time, tz)`, EA `UkSummer()` / `NySummer()` (exact switch instants), `ref.py` `uk_summer` / `ny_summer`; London and London
    Close +60 in UK winter, New York +60 in US winter, the shift on top. `ref_gs.py` / `ref_g.py` keep `kzAuto=False`, so the earlier research is unchanged.
    (c) Daily news window follows New York time (strategy `dnAuto`, EA `InpDNewsAuto`, default on): Pine shift = the change of the (DAYS AND HOURS zone - New
    York) gap against 1 July (minute math when shifted, the `time(session)` call when not); emulated in Python for 8 zones 2025-2027: exact on every trading
    day, differences only on switch weekends. The EA user clock is a fixed offset, so +60 in New York winter. (d) Crooks TP1 rule: `crkT1Pct` (10-90, default
    50; EA `InpCrkT1Pct`, `CrkT1P()`): tight distance p x TP1 - (1 + p) x costs, X1 qty p, EA `T1Half` rounds p x lots up to the lot step; `crkT1Any` (EA
    `InpCrkT1Any`): the rule also with Final Exit TP2-TP4, the rest always to TP2; EA bar-close backup `t1Bar` books the TP1 part at market when a closed bar
    after the fill bar reached TP1 (+ earn-back costs) and no tick did. Gold, `gold/crooks_t1p.py` (p 30 / 50 / 70 x tight / normal stop x Final Exit TP1 /
    TP2 + any, on the 14 exit-TP1 settings; the p = 0.5 replays are asserted equal to `crooks_t1var` / `crooks_tp1`, 66,869 trades). Crooks C + $500 Start
    again, average net, exit TP1: plain -$4,448 (3 of 14 profitable), tight 50% -$5,848 (2), normal 30 / 50 / 70% -$2,392 / -$3,444 / -$3,717 (8 / 7 / 5);
    exit TP2: plain -$1,681 (6), normal -$2,533 / -$2,729 / -$3,382 (7 / 6 / 6). The normal stop beats the tight one at every p; at exit TP2 the plain rule
    is better. Checks: engine parity 48 configurations (14 new) 0 differences, also with `PARITY_SHIFT_DAYS` 49 and -189; `mq5check/dst` 0 differences;
    `parity_rec.py` 1,680 runs 0; `parity_tp1.py` 2,464 runs (p 50, exit TP1) + 3,360 runs / 3.87 M trades (p 30 / 50 / 70, exit TP1 and TP2 + any, tight and
    normal stop, Crooks A-D, caps) 0 (it reads `gold/crooks_t1p.pkl`: run `gold/crooks_t1p.py` first, about 2 minutes; the 30 MB file is not kept in
    `results/`); lot cases; `mq5check.py` 0 errors / 0 warnings; Pine parse OK, inline lint 0. Independent review (Sonnet, high effort): no high or
    medium findings; fixed after it: the EA books a due TP1 part before the bar's stop / target update, and a TP1 touch on bars caught up after a disconnect
    or a failed partial close is booked at the next bar close (`gT1Seen`); texts for % other than 50 (tight = % x TP1; the 0.45R / 0.6R multiples hold for
    half with TP1 0.6R) and the rest's costs at the entry (a small unpaid part: Crooks B / C carry it, A / D drop it). All checks re-run: 0 differences.

15. **Crooks C with single wins** (asked 2026-11-06, research only: the user loses big when wins come one at a time, L L W L W L W ...; suggestions
    asked before any new setting). `gold/crooks_alt.py` and `crooks_alt2.py`, the 19 gold strategies profitable at fixed $50 without a partial close,
    $50 base. Wins are not clustered: P(win) 40.3%, after a win 41.6%, after a loss 39.4%, after 2 wins 41.0%, so recovery trades lose about 57% of
    the time whatever the timing rule. Totals with $500 + Start again (avg fall / worst / biggest single loss): Crooks C +$108k (18.7% / 45% / $406);
    hard cap $250 +$112k (13.4% / 27% / $220, both halves positive 19 of 19); $150 +$99k (12.1% / 24%); over 2 wins +$109k (20.4% / 39%); forget the
    loss after 2 losing recovery trades +$100k (13.5% / 26% / $313); recovery for 50% of the loss, the rest forgotten, +$99k (11.9% / 22% / $269);
    both +$93k (11.3% / 20% / $156); wait for 2 wins in a row +$90k (16.7% / 33%); same day only +$98k (14.5% / 25%); same direction +$110k (18.4% / 33%);
    Paroli +$137k (20.9% / 41%, max risk $200); fixed $50 +$91k (10.8% / 18%).
    Crooks C only with NO cap (`crooks_alt3.py`, 200 random orders each, no leverage limit in the simulation): as now +$225k but avg fall 40%, worst 92%,
    biggest single loss avg $1,916, blown in 20.5% of random orders; forget the loss after 1 / 2 / 3 lost recovery trades +$88k / +$100k / +$108k (worst
    fall 27% / 26% / 27%, never blown); 50% of the loss +$104k (worst 25%, blown 0.6%); 50% + forget after 2 +$93k (worst 20%, biggest loss avg $156);
    75% +$130k (worst 49%, blown 5.7%); over 2 / 3 wins +$96k / +$114k (3 / 1 accounts blown in the real order); wait for 2 wins +$25k (6 blown).

16. **v3.9: Crooks C rule after N losing recovery trades in a row** (asked 2026-11-06; strategy and EA v3.9, the indicator unchanged). The user's two ideas
    (wait for M wins in a row; skip D trading days) plus forget the loss and a % of the loss, in one dropdown (`crkPr`, EA `InpCrkPr`; N `crkPrN`, % `crkPrPct`,
    M `crkPrM`, D `crkPrD`, `crkPrForget`, `crkPrAll`). Decided with the user: after the M wins the recovery waits for a loss, then a win; the skip rule keeps
    the loss unless the checkbox is on; it skips the rest of that day plus D counted days (the ticked days with the day filter, else Monday-Friday, or every
    day); the hard caps stay in the Hard Cap box. State: `crkF` (losing recovery trades in a row; base trades do not reset it), `crkWait` / `crkWW` /
    `crkNeedL`, `crkSkip` / `crkSkipLeft`; days counted per new day in the DAYS AND HOURS zone before the bar's booking (Pine `udKey`, EA `CrkDayTick()`
    after `ProcessBar()` for the closed and the caught-up bars). Python twin: `recovery.simulate(crkPr=..., trades with day events)`, equal to
    `crooks_user.py` / `crooks_alt3.py` on 342 runs. EA parity `mq5check/rec/parity_crkpr.py` (REC_DAYS mode of rec_driver: day events + SKIP): 5,184 runs,
    7.43 M signals (1.05 M skipped by the pause), 0 differences; parity_rec / parity_tp1 / engine parity unchanged, 0 differences. Gold numbers: item 15
    and `gold/crooks_user.txt` (README v3.9 table). Independent review (Sonnet, high effort): no high or medium findings; fixed in the EA: the day
    tracker `crkUDay` is kept on a re-init (MT5 keeps the pause), a setup armed on a caught-up bar while paused is not placed on reconnect (`gPauseArm`),
    a new dropdown choice starts the rule's state again (`gCrkPrPrev`), state text "d left" like the strategy. Known limit: a trade that closes during a
    disconnect starts the pause when the EA books it (on reconnect). All checks re-run: 0 differences.

17. **Month-by-month workbooks** (asked 2026-11-07). `gold/monthly.py collect | money | check` -> `monthly_trades.pkl`, `monthly.pkl`; Excel by
    `gold/build_monthly_xlsx.py` (texts in `monthly_readme.json`) -> `Gold_Monthly_1_MonFri_NoFilters.xlsx`, `Gold_Monthly_2_TueWedThu_KillZones_News.xlsx`
    (Read me, Summary, one sheet per strategy, one "By month" sheet per rule). The 19 strategies of item 15 x 17 rules (fixed $50, Crooks C, caps $500 /
    $250 / $150 Start again, over 2 wins, forget 2 / 3, 50% + forget 2 / 3, wait 2W N2 / 3W N2 / 2W N3, skip 3d N2 / 2d N3 keep / forget) x 70 months,
    each month alone (fresh $10,000 and recovery state, $50 base, gold spread, 1:100 leverage via `recovery.simulate` element 5, no lot rounding). file1:
    no day / hour / kill-zone / news filter (the strategies' own filters removed: 4 M1 London Close only, 4 M5 18:30-22:30, M15-S9 Asia only); file2:
    Tue / Wed / Thu IST, kill zones Asia + London + New York with kzAuto, daily news 17:45-18:15 IST following New York time, 60 min no new trades before
    it, at its start close at the next bar's open / cancel a waiting entry (Pine semantics: newsBlock on the arm bar = not taken; newsBlock on a bar
    between arm and fill = cancelled; newsStart on a bar from the fill to the bar before the engine exit = closed at O[b+1]). Checks: file1 equals the
    stored trades for the 10 strategies without own filters; fixed $50 = 50 x net R per month; an independent re-implementation (`verify_monthly/verify.py`,
    Sonnet high) matched trade lists, counts and 4 rules x 70 months on M15-S8 / M1-S4 / M5-S4 / H1-S8 (file2) and M15-S8 (file1), 0 differences.
    Findings: summed over the 19 strategies every rule is negative in both files because the M1 / M5 strategies lose without their own windows; M15 and
    H1 stay positive in file1; in file2 the news close hits M15 (about 40% of its trades); the leverage limit cut 727 (file1) / 192 (file2) trade sizes of
    Crooks C and kept every month from blowing the account.

18. **Settings with no losing month** (asked 2026-11-07; research only). `gold/bestmonth.py collect | screen | money | report | exact`,
    `bestmonth_final.py` (exact engine re-runs), workbook `build_bestmonth_xlsx.py` -> `Gold_No_Losing_Month.xlsx`. Each window (calendar month or
    15th-14th) on its own as in item 17. Criteria: fewest losing windows, then the best worst window, then profit; >= 3 signals a window, no blown window;
    choice on 2021-23, then 2024-26. Lesson: filters applied to the trades afterwards were badly optimistic (exact re-runs: 5 -> 13 and 5 -> 11 losing
    months), so the final search uses exact trade sets only (as designed, no time filter, file2). Today's settings: no setting without losing months even in
    2021-23; best 7-8 of 69. With a new monthly lock ("stop for the month once it is up $X", plus the recovery restarted each month): 317 settings had 0 in
    2021-23, 55% of them also 0 in 2024-26. Best: M15-S9 signals without its kill zone, Labouchere, cap $500 Clamp, lock +$250: 69/69 positive, +$27,110,
    worst month +$259, deepest fall $1,950 (fragile: +0.02R costs -> 1 losing month, 15th-14th -> 8). M15-S7 as designed, Martingale x2, Clamp, +$150:
    69/69, +$18,105 (+0.05R -> 1, 15th-14th -> 3). Most robust: M1-S3 as designed, Exact recovery, Clamp, +$50: 0 in all 6 stress cases but +$6,187 and falls
    to $4,719. Independent re-implementation (Sonnet high, `verify_bestmonth/sim.py`) confirmed both winners and the +$500 / Start-again variants.

19. **TradingView vs EA, 6 Oct - 6 Nov 2026** (asked 2026-11-07; analysis only, no code change). Inputs: OANDA trade list
    (`ARS_OANDA_XAUUSD_2026-11-07_cb7e3.csv`, 52 trades), FxPro MT5 report (`ReportTester-592122324_6_OCT_TO_6_NOV.xlsx`, 50 trades, EA inputs at the top),
    11 screenshots of the strategy inputs. Tools: `tools/csvcheck/cmp_ea_tv.py TV.csv REPORT.xlsx 5.5 3 2 2026-10-25` (match),
    `nov7/classify.py` (kill zone / news / fill count of every order and trade under each platform's settings), `nov7/spread.py` (FxPro spread from the
    earn-back targets: median 0.16), `tools/csvcheck/replay.py TV.csv 0.6` (confirmed TradingView is on Crooks C), `nov7/build_cmp_xlsx.py` ->
    `TradingView_vs_EA_6Oct_6Nov_2026.xlsx`. Result: 35 of 52 same trades, 17 TradingView only, 15 EA only; +$458.54 vs +$626.68. Settings that differ:
    EA news window 17:55 + 75 min (TV 17:45-18:15), `InpServerTz` US rule (FxPro is EET: set 2), London Close on, kill zones not following summer time,
    max fills 5 (TV 10), `InpBidChart` off (EA buy orders on the ask: 2 missed long fills, 1 win turned loss), lot rounding nearest (TV down),
    `InpCommLot` 0.16 (FxPro charges $7 per lot round trip; TV commission input 0, Properties $0.07 per oz), half-stop cap off (TV on). 12 differences
    directly from settings, 4 likely; the rest knock-on and OANDA vs FxPro prices / volume. CORRECTED the same day: the first answer said FxPro's day (and
    the EA's VWAP) starts an hour later from 25 Oct to 1 Nov. Wrong: gold is closed 17:00-18:00 New York and the report has 6,348 bars = 23 days x 276
    (23 h every day, that week too), so the first FxPro candle of each server day is the 18:00 New York reopen, the same candle TradingView's session
    starts on. No VWAP-anchor option is needed; that week's differences were the server-clock setting and price data (workbook rebuilt).

20. **v4.0: the user's settings as the defaults** (asked 2026-11-07; strategy, indicator and EA). Pine: `build/patch_pine_v40.py` (34 defaults: half-stop
    cap on, 10 fills, entry % 25, exit TP1, TP3 move 0, Don't Chase 2, Choppy 13.5, Tue-Thu, 06:00-23:00, kill zones on with London Close off, border 1;
    cap $250 Start again, trade the minimum, spread 0.16, commission 7, earn-back, stop after 23 losses (off), force-close 23:55, weekend close, news
    17:45-18:15, Crooks C, split 2, TP1 rule off with Normal stop, Crooks C rule D 4; strategy() commission_value 0.115). EA: `build/patch_ea_v40.py`
    (same defaults; server clock SRV_EET; news 17:45 + 30; news 1-5 23:30 user time = TradingView's 18:00 UTC; new `InpSpread` 0.16 via `CostSpr()` in
    LotsFor / CrkT1Dist / CrkT1Mult / exCostPx / exRiskAmt, live spread when 0; `Spr()` for the bid-chart order shift stays live; version 4.00).
    Checks: `v40/user_settings.py` (the screenshot settings) vs the strategy 160/160 and `v40/ea_vs_pine.py` vs the EA 162/162 (v3.9 EA: 41 differ);
    independent review (Sonnet high) agreed, its 4 stale texts fixed (indicator header, README); assemble identical, lint 0, parse ok, mq5check 0/0,
    markers 0, ASCII; engine parity 51 configs (old configs pass the v3.9 defaults via `V39_EA`; 3 new v4.0 configs) 0 differences, also with
    PARITY_SHIFT_DAYS 49 / -189; parity_rec 1,680 runs, parity_tp1 5,824 runs (now pass `InpSpread=0`), parity_crkpr 5,184 runs, 0 differences;
    `lots_harness` 8 cases = TradingView's sizing formula. Logs `*_v40.log`.

21. **TradingView vs EA v4.0, 6 Oct - 6 Nov** (asked 2026-11-07, analysis only). The TradingView list sent again was byte-identical to the old run
    (sha256 cb44af75..., `in_nov7b_tv`); the EA report (`in_nov7b_ea`) is v4.0 with all defaults: 53 trades, -$452.72 (TV +$458.54). Match 42 of 52
    (41 same result; was 35), base-trade lots equal. Through 4 Nov TV +$459.69, EA +$463.12; the whole gap is 5 Nov (TV -$1.15, EA -$915.84): after
    06:45 both owed the same ($153.46 / $153.36); TV's recovery trade 07:40 long (#49; no FxPro signal) won +$143.96; the EA's recovery moved to 08:40
    (TV still in #49): -$249.10, then 20:20 short 0.45 lot (planned $622 = owed / 0.6R; TV took it as a 3 oz base trade): -$611.56. Recovery trades TV 14
    (+$358.93) vs EA 15 (-$569.68); base trades 38 each (+$99.61 vs +$116.96). 20 Oct: TV #22 limit 4140.415 filled (low about 4140.30); the EA's level
    4140.26 (+ spread shift) was not reached. EA sizing checked = Crooks C rule, no bug. Tool: `nov7/ledger.py TV.csv REPORT.xlsx`.

22. **EA v4.1: Crooks C hedge rule** (asked 2026-11-07; EA only, not tested on gold at the user's request). `build/patch_ea_v41.py` + review fixes
    `build/patch_ea_v41b.py`: `CPR_HEDGE = 5` in `InpCrkPr`; inputs `InpCrkHgSl` 1, `InpCrkHgTp` 0.6, `InpCrkHgUnit` (R / price), `InpCrkHgForget` true.
    After N losing recovery trades in a row `crkHg`; the next taken signal: `CrkHedgeNow()` makes it a recovery trade (NextRisk), `PlaceHedge` = BuyLimit
    + SellStop (buy signal) or SellLimit + BuyStop at `lim` (buy side + Spr()), comment HEDGE, own SL / TP (`HgLevels`, `HgDist` >= stops level +
    spread + tick); market / virtual fallbacks (`HgMarket` clamps stops to the live price and closes a lone trade); margin for 2 x lots; hard cap: with
    TP > SL each trade at most cap / 2. Guards `!exHg` on SetExits, engine exit, engine-wins close, caught-up SetExits, ManagePartials; a waiting leg
    cancelled at force-close / weekend / news. `BookClosed`: exPnl of both, forget (CrkCycle) or keep (crkW = last closing deal `gLastOutProfit` > 0).
    Netting account (`gHedgeOk` false): the rule forgets the loss. Restart: `HgOpen()` leaves the pair to its SL / TP. Checks: mq5check 0/0; regression
    parity unchanged (logs `*_v41.log`, `*_v41b.log`); `mq5check/rec/hg_driver.cpp` (entry points `rec_hgok` / `rec_hgclose` / `rec_hgnow` / `rec_owed`
    in rec/build.sh) scripted cases forget / keep-lost / keep-won / netting all as designed; review (Sonnet high) 5 edge cases fixed, rest nits.

23. **v4.2: monthly profit lock in the strategy and the EA, and workbook v2** (asked 2026-11-07). All new settings are off by default.
    - **Pine:** `build/patch_strat_v42.py` (applied to `build/strategy_template.pine`, then `assemble.py`).
      - Group `GRP_ML` "MONTHLY PROFIT LOCK (strategy only)" with inputs `mLockOn` / `mLockAmt` 150, `pLockOn` / `pLockAt` 500 / `pLockPct` 20 (1-100),
        and `mRestart`.
      - State: `mNet0`, `mPeak`, `mStop`, `pLocked`, `mRestPend`.
      - Month key `year(time, tzUse) * 100 + month(time, tzUse)`. On a new month: `mNet0 = strategy.netprofit[1]`; the locks reset; `mRestPend` is set
        if `mRestart`.
      - Before "3. follow the engine":
        - the restart, when `exState == 0` and flat;
        - then `mPnl = strategy.netprofit - mNet0` and the checks (lock at the amount; the profit lock arms at `pLockAt`, the locked level is
          `pLockPct` % x `mPeak` (trailing), and it stops when `mPnl` is at or below that level).
      - `preSkip` also checks `mStop`; skip reason "monthly lock"; status "MONTHLY LOCK (until the 1st)"; the DAY P&L row shows the month.
    - **EA:** `build/patch_ea_v42.py`, then review fixes in `build/patch_ea_v42b.py`.
      - Inputs `InpMLockOn` / `InpMLockAmt`, `InpPLockOn` / `InpPLockAt` / `InpPLockPct`, `InpMRestart`.
      - Globals `gMonKey`, `monPnl`, `monPeak`, `monStop`, `monLocked`, `monRestPend`.
      - `RecoveryRestart()` resets the same state as the hard cap's Start again, plus `CrkCycle`, `crkW` and the skip pause.
      - `MonthTick(UserTime(bt))` runs on every bar.
      - `BookClosed()` adds the whole trade's `exPnl`, so the engine-wins path is covered too.
      - Just before "5. take the engine's new setup": the restart (when `exState == 0` and there is no position), then `MonthCheck()`.
      - `MonthFromHistory()` runs in OnInit:
        - the month of the last closed bar;
        - deals of this symbol and magic number whose own user-time month matches;
        - positions still open are skipped;
        - `MonthCheck` runs after each OUT deal.
      - Version 4.20.
    - **Checks:**
      - mq5check 0 / 0; Pine lint 0, both files parse, the shared blocks are identical, 6 new inputs.
      - `mq5check/rec/month_driver.cpp` (entry points `rec_mtick` / `rec_mpnl` / `rec_mcheck` / `rec_mrestart` / `rec_mpeak`): lock $150, the
        profit-lock example (stops at +$129 with the high at $650 and 20%), the restart (owed $20 forgotten, or kept when off), and a BookClosed
        trade counting.
      - `hg_driver` cases unchanged. Log: `v40/hg_month_v42_final.log`.
      - Parity with the locks off, `v40/run_parity_v42b.sh`: engine ALL IDENTICAL x 3 shifts; rec 1,680 runs, tp1 3,360, crkpr 5,184; 0 mismatches.
      - Review (Sonnet high): no Pine findings; 5 EA findings fixed in v42b.
    - **Workbook:** `gold/build_bestmonth_xlsx_v2.py` builds `Gold_No_Losing_Month.xlsx` from the saved `gold/bestmonth_book.pkl` + `gold/monthly.pkl`.
      Every sheet now opens with WHAT THIS SHEET IS / HOW TO READ IT. New sheets:
      - "Strategies explained": the goal words, the base settings, and each strategy's changes with their TradingView group / title and EA input.
        The titles are read from the repo .pine files.
      - "Settings explained": time filters, 22 recovery rules, hard caps, the monthly lock and the v4.2 settings.
      - The Read me's stale "neither exists yet" line was replaced.
      - Recalc: 0 errors.

24. **Entry accuracy research** (asked 2026-11-08: "rethink the entry / VWAP rules so that the accuracy of every TP goes up"; research only, the
    indicator, strategy and EA were NOT changed because nothing passed the final test). Workbook `deliverables/Gold_Entry_Accuracy_Research.xlsx`.
    - **Kit, `$S/entry/`** (guide: `README_KIT.md`; run `python3 -I`, numba / scikit-learn / LightGBM / scipy installed with pip):
      - `data.py`: bars as cached `.npz` + the engine's session / week / month VWAP, sigma, ATR.
      - `signals.py raw(tf)`: every raw signal without the position rules. Checked against `ref_g`: H1 exact; M15 4 and M5 19 trades differ (the
        re-anchored break).
      - `outcomes.py`: numba fill and outcome on the 1-minute path and on the chart convention.
      - `features.py`: about 60 causal features. `dataset.py` writes `ds_TF.pkl`; `barscan.py` writes `bars_TF.pkl` (every bar, long and short at
        market, stop 1.8 ATR); `baseline_m1.py` writes the M1 version (every third bar).
      - `kit.py evaluate()`: excess = hit% minus random entries of the same direction and split. `placebo.py` shifts the clock; `exact.py` builds
        the `ref_g` trade table.
    - **Splits:** train 2021-23, valid 2024-01..2025-06, TEST 2025-07..2026-10. The finalists were pre-registered in `holdout_plan.md` and TEST was
      opened once (`holdout_result.txt`).
    - **The signals' accuracy equals random.** Random TP1-4 hit is about 62.5 / 50 / 40 / 33.3 %. Raw-signal excess (train / valid / test): M5
      -1.0 / 0.0 / +0.3, M15 -0.5 / -2.3 / +2.2, H1 -4.1 / -1.8 / 0.0.
    - **Models and screens:** LightGBM on the signals reaches AUC 0.50-0.51 (valid); on every M15 bar 0.53 (the trend regime). The univariate
      screen (`screen1.py`, `barscreen.py`) finds only noise.
    - **Rule mining (`rulemine.py`):** use per-trade means with day-clustered errors. The first version averaged per-day means, which inflated
      mean reversion (+12.7 vs +1.2 per trade).
    - **The retest limit is adverse selection (`adverse.py`).** Taken at market instead of at the limit: TP1 about 51 % when the limit would have
      filled, about 96 % when it never fills.
    - **Time of day (`season.py`, `seas_entry.py`):** shorts NY 07-10, longs NY 13-17. It beats every clock-shifted copy; M15 +2.0 train / +5.5 valid,
      by year +0..2 in 2021-22 and +3.5..10 in 2023-25, only +0.7 on TEST.
    - **Explorers (Opus, high effort):**
      - agent A (`entry/agentA/`, 357 variants): new setups.
      - agent B (`entry/agentB/`, 522 variants): the indicator's own entry.
    - **Finalists on TEST:**
      - C1, the fade of the raw M5 signal NY 12:00-17:59 at market with a 1.8 ATR stop: -0.43 (L +2.32 / S -3.20). It was +4.51 / +5.44 before.
      - C1 longs only: +2.32, se 2.6.
      - ORB, M15 NY 09:30-10:00 stop entries: -1.29.
      - SWEEP, M15 previous-day high / low plus a confirmation stop entry: -0.39.
      - None passed. The verifier (Sonnet, high effort; `entry/verify/`, its own code) reproduced every number. Day-bootstrap 95 % CI for C1 on
        TEST [-4.1, +3.5]: a +4.8 edge has p about 0.3 %.
    - **Offered to the user, not built:** an off-by-default "long after a bearish signal NY 12-18" for a demo forward test; a "random" row in the
      TP tables.

25. **Order-flow research (done 2026-11-08; no change to the engine)** (asked 2026-11-08: "do order-flow concepts (LVN, POC, delta, cumulative delta, absorption,
    exhaustion ...) combined with the entry signals find the false losing signals and the winners?"; also "save everything, checkpoints").
    - **Data limit:** gold CFD has tick volume only, no bid/ask volume. `entry/of.py` (README_KIT "Order flow") builds estimated delta / CVD from
      1-minute candles and the session volume profile (POC, VAH / VAL, RVP for LVN / HVN), developing and prior; caches `entry/of_TF.npz`
      (`python3 -I of.py build`, 4 s).
    - **Agents** (Opus, high effort, run in parallel, each writes `progress.md` after every step):
      - OF-A, `entry/of_agentA/`: order flow as a filter or confirmation of the indicator's signals (signal-bar delta, absorption, CVD
        divergence, profile location of the entry / stop / TP, LVN / HVN on the path to the targets, pullback volume and delta with cancel
        rules, and LightGBM with the order-flow features added);
      - OF-B, `entry/of_agentB/`: order-flow entries (absorption / exhaustion at value-area edges, failed auctions, LVN breakouts, POC
        reversion, CVD divergence reversals, delta flips) alone and with the indicator's signal.
    - **Protocol** as item 24: train / valid only, excess vs random entries of the same direction and period. Then the finalists are
      pre-registered in `entry/of_holdout_plan.md`, TEST is opened once, an independent verifier checks it, and the workbook is updated.
    - **Resume after a stop:** `bash Research/restore.sh` (also installs the packages and rebuilds the caches), read this item and
      `entry/of_agent*/progress.md`, then relaunch an agent with "resume from progress.md". Auto-checkpoint: the session commits
      `Research/` every 20 minutes while the agents run.
    - **Results:**
      - OF-A (446 variants): no order-flow filter separates winners from losers. LightGBM valid AUC 0.501 -> 0.506 with 40 order-flow
        features (M5), M15 0.485-0.500.
      - OF-B (495 variants): order-flow entries fail.
      - Finalists, re-derived by the main session (`entry/of_finalists.py`, plan `of_holdout_plan.md`, result `of_holdout_result.txt`); TEST
        excess pooled, long / short:
        - OFA-C1 (M5 signals after a narrow previous value area, <= 7.5 ATR): +0.82 (se 1.3), +1.22 / +0.42;
        - OFA-C1b (narrow previous high-low <= 16.8 ATR, no volume): +0.87, +0.81 / +0.93;
        - OFB-C3 (fade a signal pointing away from the developing POC, >= 5.8 ATR): -1.77;
        - OFB-C1L (long >= 8.6 ATR below the POC): -2.12.
      - None passed (< 1 se or negative). The only effect that kept its sign is compression before breakouts, which is not order flow.
      - Workbook sheet "7 Order flow". The test evaluation is the same `kit.evaluate` that the item-24 verifier reproduced exactly.
26. **EA v4.3: restart memory** (asked 2026-11-09: "continue from the same streak / loss amount when the laptop or MT5 restarts, automatically";
    EA only, because the TradingView strategy recalculates from the chart history).
    - **Patches** `build/patch_ea_v43.py`, then the review fixes `v43b` (month values saved), `v43c` (named by symbol + magic, account saved as a
      value), `v43d` (no save before a processed bar), `v43e` (independent review F1-F5, L1-L4, L6, L8). Backup: `bak/v42_final/`.
    - **Input:** `InpRemember` (group RESTART MEMORY, default on). Off in the Strategy Tester. Version 4.30.
    - **Storage:** terminal global variables `ARS|<symbol>|<magic>|<field>`.
      - `StateIO(save)` is the single list of saved values (recovery: every rule's state, totalNet, capStop; Crooks: crkL ... crkHg, gCrkPrPrev;
        day: dayPnl, lossRow, winRow, dayBlock, pauseLeft, paused; month: gMonKey, monRestPend, monPnl, monPeak, monStop, monLocked; trade:
        exState, exL, exLots, exRiskAmt, exCostPx, exPnl, exKeepSl, crkRec, exSynced, pDone, exT1*, exHg*; the deal cursor lastDeal; the
        Labouchere list L0..; meta: ver, lb = the last processed bar, sv, acc).
      - `StateSave` writes only the values that changed (a full rewrite at OnInit, OnDeinit and once a day), then `GlobalVariablesFlush`.
    - **Start (OnInit), also on new inputs:**
      - `StateLoad`. A state of another account is refused. A hard-cap Stop ends on new inputs, or when the cap no longer stops.
      - The warm-up reaches back to `lb` (at most 100,000 bars). For the bars after `lb` it counts `gDayPendN`, `CrkDayTick` and `gPauseArm`,
        and `FlatBetween` (force-close, weekend start, news start) sets `gRestFlat`.
      - `BrokerStart()` runs at once if MT5 is connected, else at the first tick once it is; nothing is saved meanwhile. It runs `MonthTick`,
        then `RestoreTrade`, then adoption (a restored runner or an early fill is kept, `exArm` relinked), `CancelPending` (a restored hedge
        pair keeps its waiting leg), `DayStart`, the TP1 catch-up, `BookBrokerDeals` (a copy of OnNewBar steps 1-2), `gRestFlat` close, the
        monthly restart, `MonthCheck`, and `gRearm`.
      - `gDayPend` became the counter `gDayPendN`: `DayStart(n)` ends one pause day per new day, including after a disconnect.
    - **Harness:**
      - `mq5check/mql5shim.h` and `run/rt_impl.h`: GlobalVariable* functions (an in-memory hash store) and `StringGetCharacter`.
      - `rec/gen_fresh.py` generates `rec_fresh()`, which puts every EA global back to its declared initial value, i.e. a fresh program load.
      - `rec_restart()` is save, then fresh, then what OnInit does. `rec_driver` with `REC_RESTART=k` restarts at every k-th step.
      - Negative control: `v43neg/run_neg.sh`.
    - **Results** (`v40/final_v43.txt`, final EA):
      - Compile: mq5check 0 errors / 0 warnings, ASCII only.
      - Money-management parity, normal / with a restart after every step (`REC_RESTART=1`), 0 / 0 mismatches each:
        - rec: 1,680 runs, 2.15 M trades;
        - tp1: 3,360 runs, 3.87 M trades;
        - crkpr: 5,184 runs, 7.43 M signals.
      - Negative control: without `crkL`, `totalNet` or `crkSkipLeft` the restart parity gives 460 / 213 / 3,294 mismatches, so omissions
        are caught.
      - Hedge and month scripted cases: unchanged.
      - Engine parity: ALL IDENTICAL x 3 shifts.
      - Independent review: Sonnet, high effort; its findings were verified, then fixed in v43e.
27. **EA v4.4: live trades closed early (IN PROGRESS)** (asked 2026-11-11 with a phone screenshot: new broker, symbol `GOLD.i#`, commission
    0; three trades closed at +4.86 / +4.97 / +6.48 instead of TP1 = 0.6R).
    - **Trades** (server time): buy 0.06 05:05:03 -> 05:15:00 (4047.89 -> 4048.70, SL 4040.07, TP 4052.46); buy 0.07 09:11:14 -> 09:17:11
      (4062.34 -> 4063.05, SL 4055.74, no TP); sell 0.09 14:40:05 -> 14:45:03 (4042.14 -> 4041.42, SL 4047.41, no TP). All have the comment ARM.
    - **What v4.3 can close** (every CloseAll): the engine's exit (stop / target), "engine wins" (a position the engine is not in, at the next
      bar), force-close / weekend / news start, SetExits' price-already-past check, the Crooks TP1-rule part (intrabar), a lone hedge leg,
      `gRestFlat` at a restart. On M5 only the TP1 rule and a restart close mid-bar.
    - **Reading the screenshot:** trade 2 closed mid-bar (09:17:11), so not by an M5 bar rule; trade 1 had its TP (the engine was in sync),
      and with earn-back on v4.3 keeps such a trade; all three closed after only +0.71 to +0.81 in price. Most likely causes:
      something outside the EA (another EA, a second copy of this EA with the same magic, a hand close), or "engine wins" after a
      re-initialisation (timeframe switch, new inputs), which makes the engine lose track of the trade. Without the Experts/Journal log this
      cannot be proven.
    - **Bugs found in v4.3:** (1) a trade closed outside the EA (by hand, phone, another EA) has an exit deal with another magic, so
      `NewDealsPnl` skips it and BookClosed books a winning trade as a $0 loss (recovery, streaks and pauses go wrong); `ExitDealAfter` has
      the same blind spot after a restart. (2) No TP at the broker until the engine confirms the fill at the next bar close. (3) "Engine
      wins" closes the EA's own filled order at a random price (early fill when the spread narrows on buys, setup expiry, timeframe switch,
      new inputs, two copies). (4) Two copies with the same symbol + magic cancel and close each other's trades and share one restart state.
      (5) The server clock defaults to FxPro's EET rule; a new broker may differ. (6) No log of why a trade closed.
    - **Plan:** `build/patch_ea_v44.py`: TP from placement; keep own trades (no "engine wins" close; exits only by broker SL/TP, the engine's
      stop/target for a synced trade, force-close / weekend / news); our-trade events via the arm bar (`EngStep` wrapper, ProcessBar
      untouched); save the arm bar time `exArmT` so a restart / timeframe switch re-links or keeps the trade; book deals by position ID;
      report who closed every trade (DEAL_REASON); one-copy lock (temporary global variable); server clock Auto (detect); close reasons
      in the log. Then a broker simulator harness (`$S/sim/`), the old parity suites, a review, README, ship.
    - **Done so far (2026-11-11 21:40):** patches `v44` (44 edits), `v44b` (timeframe hold: the EA trades the timeframe it was attached to;
      a chart switched to another timeframe opens no new trades until it is back; `ARX|..|tf`, forgotten on REASON_REMOVE / CHARTCLOSE),
      `v44c` (the close report shows the trade's whole P&L). Rebuild: copy `bak/v43_final/AuctionRetestEA_v43.mq5` to `build/safe/`, run
      the three patches in order. mq5check 0/0. Harness additions: `GlobalVariableSetOnCondition`, `GlobalVariableName` (shim + rt_impl),
      empty deal-history / chart stubs in `rt_impl.h`.
    - **Broker simulator `$S/sim/`** (`build.sh EA NAME [v43]`, `sim_driver`, `sim_impl.h`, `analyze.py`, `run_all.sh` -> `results.txt`):
      MT5 hedging broker (limit/stop orders, stops level, SL/TP at the tick, deals with reason / magic / position id, commission), ticks
      from FxPro M1 bars (`export_m1.py`, 4 per minute, spread x (1 +- JIT)), M5 and M1 bars, restarts (fresh globals), new inputs, timeframe
      switches, hand / other-EA closes, lock and clock tests. 0.9 s for 3 months.
    - **Results (3 Aug - 2 Oct 2026, 13 scenarios):** v4.3 opens every trade without a TP; plain running gives no early closes, but timeframe
      switches give 48 "engine wins" closes (avg +8.69) and input changes 9 (avg +6.76), the user's symptom; hand / other-EA closes are booked
      as $0 (25 of 99 bookings wrong, Crooks C then skips the recovery trade). v4.4: 0 early closes, every trade has a TP from the open, all
      bookings equal the broker P&L, restarts and same-input re-inits give identical trades, lock refuses a second copy and takes a stale lock,
      clock read as GMT+3 / +2 / 0 / +5.5 / -4. (A commission-scenario mismatch was the analyzer missing the entry deal; fixed.)
    - **v44d (simulator finds, 22:00):** (1) a setup already traded was placed again after a restart / timeframe switch when the engine still
      showed it armed (v4.3 too: gRearm) -> `gTakenT` ("xt") = arm bar time of the last placed setup, never re-placed; an order still waiting at
      the stop is re-placed as before (RestoreTrade clears gTakenT when sx == 1). (2) OrderExits checked a pending order's stops against the
      current price, which pushed a limit's TP to the price when it had run past the target -> reference = order price (pending) / closing
      price (market); a market entry past the target is skipped. Rebuild order: v44, v44b, v44c, v44d. All 13 scenarios + TP1 rule / hedge /
      partials / market entry (with restarts, switches, hand closes): 0 early closes, 0 duplicates, 0 rejects, every booking = broker P&L.
      A sell's TP moves by the live spread when re-sent after a restart (bid-chart shift by design).
    - **Review 1 (Opus, high) -> v44e** (all verified, then fixed): F1 BarTimeOf by iBarShift(gLastDone) (a start before MT5 connects ran
      BrokerStart before the missed bars: restored trades were not re-linked; reproduced with the driver's DISC=1); F2 restart: the saved setup
      is re-linked in the warm-up (arm bar time, direction, entry), bars after gSvLast run through EngStep -> gMiss*, BrokerStart closes a trade
      whose engine stop / target was hit while off (reproduced with stop moves + RESTART=397 OFF=150); F3 daily rewrite of ARX rsd / tf
      (ExtraRefresh); F4 CloseRule + gExitRetry ("xq") retries refused closes; F5 partial closes carry their reason, "partly closed"; F6 quiet
      NewDealsPnl only moves the cursor; F7 exTpL on adoption; F8 tf deleted on INITFAILED / PROGRAM / TEMPLATE too; N netting: magic only.
      Harness: rt_impl.h stubs PositionSelectByTicket / PositionGetInteger (sim build drops them). Rebuild order: v44, v44b, v44c, v44d, v44e.
    - **Simulator on v44e:** 13 scenarios + 14 extra runs (TP1 rule, hedge, partials, market, Sep 2025 - Jan 2026 period, stop moves with
      offline restarts): 0 trades without TP, 0 duplicates, 0 rejects, 0 failed starts, every booking = broker P&L.
    - **Review 2 (Opus, high; resumed after a usage-limit stop) -> v44g**, verified first:
      - R1 (high, reproduced in the simulator: a new trade closed at the first bar after a restart by the old trade's engine stop):
        the warm-up's gMiss* are handled in BrokerStart and cleared there; TakeSetup(ok) and BookClosed clear gMiss* and gT1Seen;
      - R2: netting books outside exits while exState != 0;
      - R3: gRearm when gTakenT == 0;
      - R4: gTakenT for every decided setup;
      - R5: gCloseId saved ("xw"), "this EA (before a restart)";
      - R6: gExitSeen / gGoneWait: a gone position is booked with its closing deal, else one bar later; BookBrokerDeals needs a closing
        deal.
    - **v44f** (own read-through): NoteClose / ClosedByUs ring of 8 ids (hedge pairs closed together), gHedgeOk re-read in BrokerStart.
    - **v44h:** CloseAll prints one line per position.
    - **v44i:** a setup seen while the chart shows another timeframe (TfHold) is not recorded in gTakenT. M5 bar times are also M1 bar times,
      so a skipped M1 setup at 09:05 blocked the M5 setup armed at 09:05 back on M5. With heavy switching, 3 trades were restored (86 vs 83).
    - **v44j (asked 2026-11-12: "I don't see any VWAP line; enable it by default with an option to turn it off"):** VwDraw, called first in
      DrawBar (which ProcessBar calls at the end of every bar), draws the engine's VWAP (vwHist[0]) as one OBJ_TREND segment per bar
      (ARM_VW<time>) for the last InpVwapBars bars (1500; 50-20000). Live, the segment that leaves the window is deleted. Inputs (DISPLAY):
      InpVwapShow (true), InpVwapColor (#4DD0E1, like the TradingView indicator), InpVwapWidth (2), InpVwapBars. Simulator object store:
      `VWLINE` report, e.g. 1500 segments, 0 gaps, 0 backwards, last point = the engine's VWAP; off: 0 segments.
    - **v44k (the v44j suite found it):** with an offline start (DISC, several caught-up bars in one tick) the live cleanup deleted one
      segment per bar by index (iTime(gVwN + 1)), so the window grew to 1507 segments and a later delete opened a gap inside it. Now every
      bar from index gVwN + 1 back to the last cutoff gVwCut is deleted, then gVwCut = iTime(gVwN). Also: the line is drawn over the candles
      (OBJPROP_BACK false, like the TradingView plot; the markings stay behind), and OnInit ends with ChartRedraw when gCanDraw, so the line
      shows at once with the market closed. Checked: base, DISC, DISC with 50 bars, 300 bars + restarts + TF switch: 0 gaps, exact window.
    - **v44l (found with InpRemember = false in the simulator; the default checked too):**
      - TfHold: the open trade is never linked to another timeframe's engine (warm-up re-link and BrokerStart `same` need !TfHold()); it
        keeps its own SL / TP and is linked again on the trading timeframe. Memory off + TF stress: 12 adoptions + 2 early-fill links on M1
        -> 0. Memory on: 0 on M1 before and after (sc_08 trades and bookings identical, 86 / 86).
      - Memory off + new inputs / TF switch: OnInit skips every earlier deal (NewDealsPnl quiet), so a trade closed seconds before the
        re-init was never booked (TF stress 45 of 68 booked, REINIT=23 stress 25 of 57). OnDeinit (REASON_PARAMETERS / CHARTCHANGE,
        !gPersist, exState != 0) calls BookBrokerDeals first: 68 / 68 and 57 / 57. A restart with memory off still forgets a trade that
        closed while the EA was off (by design: 1 per run).
      - New checker `sim/unbooked.py` (bookings vs broker trades with gaps, hedge pairs as one booking, "closed while off");
        `sim/summarize.sh` builds `final_summary.txt` from it.
    - **Patch chain:** v4.3 -> v44, b, c, d, e, f, g, h, i, j, k, l reproduces the final file exactly (`build/chain/`).
    - **Final file:** `MetaTrader5/AuctionRetestEA.mq5`, md5 415a06f66db5, 2433 lines. mq5check 0/0, ASCII, no CR, no harness markers,
      no adjacent string literals (tokenizer scan).
    - **Simulator, final file (`sim/run_final.sh`):** `sim/run_all.sh` has 17 scenarios (14-17 added: market + restarts off, stop moves +
      restarts off, offline start, TP1 rule + offline + hand) plus 16 extra v4.4 runs and 4 with the memory off (z_);
      `sim/final_summary.txt` covers 37 runs and 3,767 trades (memory on: 33 runs, 3,446 trades).
      - v4.4: 0 without TP, 0 duplicates, 0 stale closes (new analyzer check), 0 rejects, 0 failed starts, 0 M1 links; every trade booked
        once with the broker P&L, except 2 that closed while the EA was off with the memory off (by design).
      - VWAP line in all 37 runs: 1500 segments, 0 gaps, 0 backwards, last point = the engine's VWAP (sc_15 ends while the EA is off: 0).
      - 17 scenarios, v4.3 vs v4.4: trades 1659 / 1571; without TP 1659 / 0; engine-wins closes 67 / 0; wrong bookings 81 / 0; same
        signal twice 3 / 0; opened while the chart showed M1 87 / 0. Restart and same-input re-init runs = the run without them (99 / 99).
    - **Regression `v40/run_v44.sh v44l` on the final file (08:51 - 09:40, `v40/final_v44.txt`):** scripted hedge + month identical to
      v4.3; rec / tp1 / crkpr 0 mismatches, normal and REC_RESTART (2,150,319 / 3,870,319 / 7,429,684 compared); engine parity ALL
      IDENTICAL (plain, +49, -189 days, data restored). Earlier runs: v44e died in the pause; v44h - v44k stopped for the next fix.
    - **Delivered** to the user (SendUserFile) with the final summary; task closed.

28. **v4.5: Crooks E - J (asked 2026-11-13)** (strategy + EA; tasks #48-#51).
    - **The ask:** Crooks E: like Crooks C, but while a loss waits for a win every trade is 0.01 lot (confirmed: the 0.01-lot trades count;
      a losing recovery trade goes back to 0.01 lot; the lot is a setting, the normal size if smaller; all Crooks C extras apply). Plus 5
      more rules that lose less in a long losing run and keep the drawdown small.
    - **Study** (`gold/crooks_e.py` round 1 = `crooks_e_round1_rawmin.txt` with the raw 0.01-lot risk; `crooks_e1.py` = round 1 with min(base,
      0.01 lot); `crooks_e2.py` round 2): 19 profitable gold strategies, $50 base, $10k, no cap, 200 shuffled orders each.
      - The 0.01-lot risk needs each trade's stop distance: x[5] of the trade record (x[4] = cost) -> 1 oz x (stop + cost). On wide H1 stops
        0.01 lot is more than the $50 base, hence min(base, 0.01-lot risk).
      - Results: C +$225k, fall 40% / 92%, 20% blown when shuffled. E +$145k, 28% / 59%, 15.8% blown (the recovery still grows).
        F (cap 3x) +$130k 21% / 40%; G (owed 10x) +$115k 15% / 29%; H (1% equity) +$123k 16% / 29%; I (E + cap 3x) +$89k 20% / 36%,
        losing runs $381 (C $2,086); J (recovery x (1 - DD / 20 base)) +$95k 13% / 21%. F - J: 0 blown in shuffles.
      - Rejected: halve after a lost recovery (blown 5-6), 2 wins first (blown 6), brake on every trade (worse than Off), house money, decay,
        base = % of equity.
    - **Code:** `build/patch_ea_v45.py` (26 edits) and `build/patch_strat_v45.py` (14 edits).
      - ENUM_REC 22-27 / L_CRE..L_CRJ; CrkCFam() / crkCFam replaces every `== REC_CRC` that means Crooks C behaviour.
      - EA: CrkRecLimit (F / I: K x base / CrkT1Mult; H: max(base, equity x %) / mult; J: max(base, r x (1 - max(0, crkPk - totalNet) /
        (X x base)))). NextRisk(exitR, canTake, minRisk): E / I waiting = min(base, minRisk). MinLotRisk(sd) = lots x LotsFor's per-lot loss
        (LotsFor gives back exactly that lot). BookClosed: G cap after the subtraction; crkPk = max(crkPk, totalNet) for every rule.
        StateIO "pk"; StateLoad: crkPk = max(crkPk, totalNet) (a v4.4 state has no peak). MemoryFresh: crkPk = 0. Inputs InpCrkELot, InpCrkFK,
        InpCrkGX, InpCrkHPct, InpCrkJX + OnInit checks. Table shows the rule's limit / the 0.01 lot.
      - Pine: the same, with strategy.equity (H), strategy.netprofit and its peak at booking (J), and E's lot x unitsPer x (rp x pointvalue
        x fx + costUnit). Input titles unchanged (only tooltips and options); `pinecheck/inputs_cmp.py`: 5 added, 0 titles changed.
    - **Reference:** `gold/recovery.py` MODES 22-27 + CFAM; the 6th trade element is the E / I lot's $ risk.
      - J uses peakNet - net: the parity's 1e12 start lost precision with peak - eq (276 tiny mismatches, now 0).
      - The old reference vs the new on the 22 old rules: 3,168 runs identical. Study sim() vs recovery.py: 161 runs identical.
      - `gold/crooks_tp1.py`: E - J (limits x m).
    - **Harness:** `rec_driver.cpp`: REC_MIN (each line carries the 0.01-lot risk after the cost) and REC_START (equity = start + P&L so far).
      `build.sh`: rec_next_m / rec_next_t1 (T1 mode uses the EA's own MinLotRisk); rec_restart mirrors OnInit with CrkCFam().
    - **Parity:**
      - `parity_rec.py` (+ E - J with variants and over 2 wins): 2,928 runs, 4.07 M trades, 0;
      - `parity_crkpr.py` (+ E - J with forget / % / wait / skip, N 1-2): 10,944 runs, 16.5 M signals, 0;
      - `parity_tp1.py` (+ E - J): 12,684 runs, 18.7 M trades, 0.
    - **Simulator:** `sim/n_rec22..27*.log`. All trades booked, 0 rejects. E / I: 62 / 62 waiting trades exactly 0.01 lot, the recovery
      trade after each win. The 37-run suite on v4.5 is identical to v4.4 (`final_summary.txt`, `results.txt`).
    - **v45b (Pine only):** the Loss Recovery tooltip's new lines were shortened (3,623 -> 3,138 characters; v4.4 had 2,764).
    - **v45c (the restart parity of run v45a found it: 48 runs, Crooks J only):** StateLoad set crkPk = max(crkPk, totalNet) on every load.
      A v4.5 state saved in mid-trade after a partial close already counted that profit, so the peak moved before the trade was booked.
      Now only a state without "pk" (saved before v4.5) does this. Restart parity rec after the fix: 2,928 runs, 0. Simulator: J and I with
      partial closes + restarts (+ outside closes) book every trade.
    - **Checks:** mq5check 0/0; ASCII, no CR, no markers, no adjacent strings; patch chain v4.3 -> v44 ... v44l -> v45 -> v45c identical; Pine
      inline lint 0, parse ok (618), shared blocks identical, indicator unchanged.
    - **Final file:** `MetaTrader5/AuctionRetestEA.mq5`, md5 c8af9a1b7b27, 2,493 lines.
    - **Regression `v40/run_v45.sh v45c` (17:33 - 19:25, `v40/final_v45.txt`; run v45a was stopped after the restart finding):**
      - scripted hedge + month identical to v4.3;
      - rec 2,928 runs / 4.07 M trades, tp1 4,620 + 8,064 runs / 18.7 M trades, crkpr 10,944 runs / 16.5 M signals: 0 mismatches, both
        normal and REC_RESTART;
      - engine parity ALL IDENTICAL (plain, +49, -189 days, data restored).
    - **Delivered** to the user (SendUserFile: the EA and the strategy) with the final summary; tasks #48-#51 closed.

29. **v4.6: profit ladder (asked 2026-11-14)** (strategy + EA; tasks #52-#54).
    - **The ask:** first make a profit ($500 or $1,000), then raise the risk, like an effort slider (Low / Medium / High / Extra high / Max),
      without going back into loss and never blowing the account; built on Crooks F - J.
    - **Study** (19 profitable gold strategies, $50 base, $10k, 1:100 leverage from the H1 price, the 0.01-lot minimum, 200 shuffles):
      - `gold/crooks_ladder.py` (round 1, `crooks_ladder_v1_strictfloor.txt`): a strict floor with trades clamped to a share of the cushion.
        It cut profit about in half and still went below the start in 20-50% of the shuffles (0.01-lot trades leak).
      - `crooks_ladder2.py`: v2 "house money" (extra risk only from the cushion above a lock) and v3 (0.01 lot below the lock). v2 adds a lot
        of profit; v3 freezes the account.
      - `crooks_ladder3.py`: v2 + start guard g0 (0.01 lot at closed profit <= 0) or g1 (half). Also measured without a ladder: after the
        first +$500 the rules go back below the start in 39-50% of the shuffles, after +$1,000 in 18-33%.
      - Picked v2 + g0, target $1,000 ($500 was lower and not monotone by level). Results (profit, fall avg / worst):
        - F: none 134k 21 / 40; Low 144k; Medium 181k; High 242k; Extra high 256k; Max 291k (29 / 48);
        - J: none 99k 13 / 21; Low 94k; Medium 115k; High 141k; Extra high 194k; Max 268k (23 / 43).
        - 0 blown anywhere. The 5% lowest profit after the target: none -$417 to -$2,008, ladder -$191 to -$603.
    - **Rule:** once crkPk >= InpLadT, lock = lam x crkPk, C = max(0, totalNet - lock), B = base + min((bmax - 1) base, phi C).
      r = min(rule(B), rule(base) + gam C / CrkT1Mult()). Guard (totalNet <= 0): r = min(base, 0.01-lot risk), TP1 rule off (CrkT1Dist 0).
      Crooks G's limit is gX x B after the trade (crkPk is updated before it).
      Levels (lam, phi, bmax, gam): Low 0.8 / 0.10 / 2 / 0.25; Medium 0.7 / 0.15 / 3 / 0.30; High 0.6 / 0.20 / 5 / 0.35;
      Extra high 0.5 / 0.25 / 8 / 0.40; Max 0.4 / 0.30 / 12 / 0.50.
    - **Code:**
      - EA `build/patch_ea_v46.py` (14 edits): ENUM_LADDER, InpLadder, InpLadT, LadFam / LadOn / LadGuard / LadPar / LadBase / LadTxt,
        CrkRule(base) (the old Crooks case body). NextRisk uses the ladder; minRisk is also passed when LadOn. BookClosed: crkPk before
        G's cap. Table row PROFIT LADDER; OnInit checks.
      - Pine `build/patch_strat_v46.py` (10 edits): ladMode / ladT, f_lad(), f_crkRule(); t1Ok needs not ladGuard; a table row.
      - No new saved state (totalNet, crkPk).
    - **Reference:**
      - `gold/recovery.py`: LADDER, LADFAM, lad_state(); simulate(lad=, ladT=). With the ladder off it is identical to v4.5 (2,016 runs).
        With it on it equals the study's sim (1,150 runs).
      - `gold/crooks_tp1.py`: the same with m; the guard turns sp off. Off: identical to v4.5 (198 runs).
    - **Harness:** `rec/build.sh` rec_next_t1 passes MinLotRisk when LadOn. The parity scripts take a lad and pass
      InpLadder / InpLadT: rec (F - J x 5 levels x $500 / $1,000 x over 1 / 2 wins), crkpr (Medium / Max x the rules), tp1 (Medium / Max).
      - Normal: rec 7,728 runs / 11.4 M trades, crkpr 20,544 / 31.3 M, tp1 7,700 + 14,784 / 34 M: 0 mismatches.
    - **Simulator:** `sim/l_*.log`, 14 runs, every trade booked, 0 rejects. Medium $1,000: 0.053 -> 0.157 lot after the target. Guard
      trades all 0.01 lot. The 37-run suite with the ladder off is identical to v4.5.
    - **v46b** (`build/patch_ea_v46b.py`, 5 edits): every local variable of the ladder code starts with a value (split declarations), so
      MetaEditor cannot report "possible use of uninitialized variable". No change in behaviour: the 14 ladder simulator runs are trade for
      trade identical to v46, and the 37-run suite (ladder off) is identical to v4.5.
    - **Checks:** mq5check 0/0; ASCII, no CR, no markers, no adjacent strings; patch chain v4.3 -> ... -> v45c -> v46 -> v46b identical. Pine:
      inline lint 0, parse ok (633), shared blocks identical, indicator unchanged; inputs_cmp: 7 added since v4.4, 0 titles changed.
    - **Final file:** `MetaTrader5/AuctionRetestEA.mq5`, md5 be1cd268ece8, 2,555 lines. Strategy .txt: `Research/scratchpad/Auction_Retest_Strategy.txt`.
    - **Regression `v40/run_v46.sh v46b`** (the suites side by side; the v46 run was stopped for v46b; `v40/final_v46.txt`), all passed:
      scripted hedge + month vs v4.3 IDENTICAL; normal and restart (state saved and reloaded before every trade) rec 7,728 runs / 11.4 M trades,
      tp1 7,700 + 14,784 runs / 34 M trades, crkpr 20,544 runs / 31.3 M signals: 0 mismatches each; engine parity (as is, +49, -189, data
      files restored) ALL IDENTICAL. Done 12:30. Task #54 complete.

30. **Fractal Breakout Grid indicator (asked 2026-11-14)** (TradingView indicator only; tasks #55-#60). Work dir `$S/fractal`, mirrored in
    `Research/scratchpad/fractal` (no .npz: rebuild with `bars.py`, `search.py`).
    - **The ask:** an indicator with the user's 9 fractal-breakout strategies (image: fractal TF, Right / Left, buy entry offset, SL, TP,
      BE trigger, salvage trigger), each selectable or all at once, plus strategies 10 (M5) and 11 (M15) found on gold; .pine + .txt.
    - **Reading (SPEC.md):** Right / Left as the header (first = right candles); swing high strictly above both sides; active from the TF
      candle after the confirming one; buy stop at high x (1 + offset%), the newest swing high replaces the older; used up by its first
      breakout (skipped while a trade is open); SL / TP % from the fill; BE: SL to the entry once up BE%; salvage: TP to the entry once down
      salvage%; candle path open -> nearer of high / low (tie: low) -> other -> close; gaps fill at the open; costs 0.23 per trade.
      Checks of the reading: Right / Left as read +282R vs swapped +173R; BE as read cuts the drawdowns 2-3x; salvage barely matters.
    - **Code:** `bars.py` (NY+7 clock: D1 at 17:00 NY, H4 from 17:00 NY), `engine.py` (exact numba engine; pm = path mode), `fast.py`
      (first-passage evaluator; equal to engine.sim trade for trade: `fast_check.py`, 0 mismatches incl. path modes), `search.py`
      (STAGE 1 coarse / 2 refined, PM 0 / 2), `ana1-4.py`, `cand.py` (robustness: path modes, costs 0.40, M5 / M15 chart, random entries).
      Independent re-implementation from SPEC.md only (`indep/`, Sonnet sub-agent): 2,359 / 2,360 trades, 0 mismatches (checked by me).
    - **The 9 strategies, gold M1 2021-01 .. 2026-10:** all profitable (+5R .. +104R, DD 1-7R); still profitable when every candle goes
      high first (the path most against a long).
    - **M5 / M15 search:** stage 1 (1.36 M combos per TF) and stage 2 (0.89 M) on M1, each with PM 0 and PM 2. Tight BE triggers
      (0.03-0.05%) look best but collapse to about 0 when candles go high first (the BE happens inside one M1 candle).
      `pick.py`: every year 2021-26 positive under PM 0 and PM 2, >= 150 / 100 trades train / test, SL >= 0.15, BE off or >= 0.10,
      right <= 30 (without it M5 and M15 both converge on 5-15 h swing highs, i.e. the H1 strategies); ranked by PM 2 train R / DD.
      - **10 = M5 R30 L65 off -0.05 SL 1.00 TP 1.00 BE 0.20 salvage 0:** 1,192 trades, PF 1.54, +91.4R, DD 7.7, high-first +75.3R,
        costs 0.40 +82.9R, random entries +10.8R, every year positive.
      - **11 = M15 R20 L40 off -0.01 SL 1.00 TP 3.00 BE 0.20 salvage 0.10:** 740 trades, PF 2.47, +67.6R, DD 4.8, high-first +55.6R,
        costs 0.40 +62.2R, random +11.9R, every year positive.
      - `neigh.py`: every one-step neighbour profitable (salvage on for 10 hurts: +27R). Results: `cand_final.txt`, `final11_M1.md`.
    - **Indicator:** `pine/build_fbg.py` -> `TradingView/Fractal_Breakout_Grid.pine` (550 lines; .txt copy
      `Research/scratchpad/Fractal_Breakout_Grid.txt`). Per strategy: request.security(tf if not below the chart else the chart's,
      f_piv(L, R), lookahead_on) with f_piv using only completed candles ([1] offsets); UDT Strat with methods openAt / closeAt / doBE /
      doSV / useLvl / up / dn / seg / onBar (all end with `true`); table with header tooltips; alert() at candle close.
    - **Checks:** `pine_twin.py` (the Pine code line by line in Python) = engine on M5 (11 strategies, 4,284 trades) and M15 (3,086):
      ALL IDENTICAL. pynescript parse ok, 0 inline-title warnings. Adversarial review (Sonnet sub-agent): no compile / runtime / repaint
      issue; taken: no ';' format sub-patterns (sign added like the Auction Retest indicator), explicit `true` returns, no lower-TF
      request. Not taken: "first chart bar does not arm a stale swing high" (arming it matches the engine).

31. **Fractal Breakout Grid v2 (asked 2026-11-15: "all the settings ... different recovery rules")** (tasks #61-#63).
    - **Research:** `rec11.py` (all 28 recovery rules + caps + ladder on the 11 strategies' gold trades, 200 shuffles; `rec11.txt`):
      fixed $50 +$21.7k (worst DD 3.4 %); Crooks F + ladder Medium +$41.9k (6.2 %) = the default; % equity +$59.8k (7.4 %); Rule C split
      $500 clamp +$108k (14.5 %); D'Alembert / Labouchere $500 clamp ~+$210k (27-29 %); without a cap Martingale-type rules blow 8-28 %
      of the shuffles. `study2.py` (`study2.txt`): hours, days, EMA trend, expiry, trailing, time exit, weekend close, candle-close entry,
      max per day, each alone on the 11: none raised the total (plain +440.7R) -> all off by default.
    - **Spec:** `SPEC2.md`. Engine: `engine2.sim2` (= engine.sim with everything off: `check2.py`, 0 differences).
    - **Pine:** `pine2/build_fbg2.py` -> v2 (money per strategy, 28 rules ported from recovery.simulate, ladder, cap, leverage, next
      trade's lots; entry / exit options; days and hours). Oscar's Grind needs ceil(x - 1e-9) (float knife-edge with zero costs;
      `recovery_tol.py` = recovery.py with the same tolerance, used by the tests only).
    - **Checks:** `pine_twin2.py` (the Pine v2 code in Python) vs engine2 with independently computed masks (`parity2_trades.py`):
      75 settings M15 + 12 M5, 13,519 trades ALL IDENTICAL (a London-mask bug in the test itself was fixed: pandas datetime64[s]);
      money (`parity2_money.py`): 2,600 random settings, ~880k trades, 0 mismatches; end to end with Money on (`parity2_e2e.py`): 34
      settings, 7,908 trades ALL IDENTICAL. More trade batches: 125 settings in all (M15 + M5), 20,394 trades identical.
      v2 defaults = v1 trades (`v2_defaults_check.py`: M5, all 11, 4,284 trades; `v2_m1_check.py`: M1, strategies 4 / 10 / 11).
      `namecheck.py`: every identifier and every s.field defined.
    - **Review (Sonnet sub-agent, checked by me):** no compile / runtime error, no deviation from SPEC / SPEC2 / recovery.simulate.
      Taken: no line getter (slX / tpX kept, moveSL / moveTP), session / New York calls out of and / or, the rule's risk as a switch,
      a header note on the live candle. Not taken: renaming unused tuple names to `_` (Pine does not warn on unused names).
    - **Final file:** `TradingView/Fractal_Breakout_Grid.pine` (v2, 1,066 lines; .txt copy `Research/scratchpad/Fractal_Breakout_Grid.txt`).
      Defaults: options off; Money on, Crooks F + ladder Medium, $50 base, $10,000 each, $500 cap clamp (gold M5 chart: +$42,653 over
      the 11 strategies, worst drawdown 6.2 %).

32. **Fractal Breakout Grid v3: strategy 12 (M1) and the STRATEGY version (asked 2026-11-15)** (tasks #64-#66).
    - **Rule change (v3, everywhere):** the gap rule also applies on the activation candle (a buy stop placed at the confirming close fills on
      a gap at the next open); needed for the strategy's pre-placed buy stops. Gold: only S9 (+3 trades, +0.4R) and S11 (+1) changed.
      Hours: parsed "HHMM-HHMM" (f_inSess), the same test for this candle and (strategy) the next. v2 copies: `fractal/v2_frozen/`.
    - **Strategy 12:** `search_m1.py` (STAGE M1, PM 0 / 2; files searchM1_M1.npz / searchM1h_M1.npz, 907k combos), `pick_m1.py`,
      `m1_edge.py` (edge over random entries; the R / DD winners mostly ride gold's drift), `m1_final.py`:
      M1 R45 L200 off -0.05 SL 0.75 TP 3.00 BE 0.20 salvage 0: 1,256 trades, PF 1.50, +130.7R, DD 13.9, high-first +113.4R, costs 0.40
      +119.3R, random +64.7R (edge +66R, train +34R), every year positive; neighbours all profitable; 32 % near S1-11 entries.
    - **Generator:** `pine3/build_fbg3.py OUT pick_10_12.json indicator|strategy` (shared model code; strategy-only table code between
      //@@S / //@@E markers, removed from the indicator). f_piv returns also the swing high confirmed BY the current fractal candle
      (pq / pu) and its time_close (tc): the strategy places that buy stop at the candle's last chart candle (time_close >= tc).
    - **Strategy order layer:** at every close for the next candle: open trade -> strategy.exit at the model's SL / TP (or strategy.close
      for a time / weekend exit due at the next open); model in / TradingView out -> market "sync" entry; model out / TradingView in ->
      market "sync" close; both flat -> buy stop (only if close < E, filters predicted for the next candle) with the exit attached, else
      cancel. Properties: commission 0.115 per contract per order, capital 120,000, pyramiding 12, close_entries_rule ANY, margin 0.
    - **Checks:** v3 engine = fast (`fast_check.py`) = twin (`parity3_trades.py`: 48 option combos, 5,193 trades; `twin3_s12.py`: M1, S12 /
      4 / 9 / 10, 3,591 trades): all identical. `emsim3.py` (TradingView broker model executing the strategy's orders): M5 S1-11 93.5 %
      identical trades, $ -2.6 %; M1 S12 / 10 / 4 / 9 96.6 %, $ -0.7 %; trade counts equal within 1. Both Pine files parse, 0 inline
      warnings, `namecheck.py` clean (the first strategy draft had strategy-only table code in the indicator: fixed with the markers).
      M1 all 12 (`emsim3_M1b.txt` + `emsim3_M1.txt`): 96.4 % identical trades (5,353 / 5,551), $ -1.5 %. Options (`emsim3_opts.py`, 32 random
      sets): counts equal within 4; candle-close entry and trailing stop diverge most (TradingView acts at the next open / candle close).
    - **Strategy review (Sonnet sub-agent, checked by me):** no compile error, no lookahead leak. Taken: no sync entry when a time / weekend
      exit is due at that open (`dueX`), cancel stale orders when no size, `tN` in the table renamed `tTot` (Pine warns on shadowing;
      `shadowcheck.py` now 0 for both builds), calc_on_every_tick / calc_on_order_fills written out, table title v3.
    - **Final files:** `TradingView/Fractal_Breakout_Grid.pine` (indicator v3, 1,096 lines) and `TradingView/Fractal_Breakout_Grid_Strategy.pine`
      (1,201 lines); .txt copies in `Research/scratchpad/`.
    - **Fix after the user's first TradingView run (2026-11-15).**
      1. **The warning.** TradingView's only warning was `barstate.islast` in a strategy without calc_on_every_tick. The strategy's table
         is now drawn when `bar_index >= last_bar_index - 1`, so it never reads barstate. `pinecheck/strategy_lint.py` flags any
         confirmed-candle barstate in a strategy and reports 0 now. calc_on_every_tick was deliberately left off: it would change live
         order handling.
      2. **The "$0" trades.** The user saw many ~$0 trades named TP / SL, plus "sync" exits.
         - What they are: strategy 11's BE / SALV exits at the entry price. Strategy 11 uses BE 0.2 % and salvage 0.1 %, so about 90 % of
           its trades end at break-even.
         - New exit names: the exit orders carry the model's names. `f_slName` gives TRAIL / BE / SL and `f_tpName` gives SALV / TP.
         - New catch-up names: catch-up orders are "<model's reason> next open" (exits) or "S# next open" (entries). They read the Strat
           fields xWhy / xBar, which exist in the strategy build only (//@@S). A trade TradingView holds and the model does not is
           named "rules flat next open".
      3. **How often catch-ups happen.** `sync_why.py` (emsim3 with tags) and `labels/sync_usd.py`, strategy 11 alone:

         | Chart | Next-open exits | Same trades | $ vs the model |
         |---|---|---|---|
         | M15 | 59 (8.1 %) | 89.0 % | +0.3 % |
         | M5 | 37 (5.1 %) | 92.5 % | -0.2 % |
         | M1 | 12 (1.6 %) | 96.8 % | -1.8 % |

         On M15 the next-open exits net +$65, against -$44 for the model's own exits of the same trades.
      4. **What did not change.** Trades and orders are the same, and the indicator is byte-identical. The strategy is now 1,216 lines.
         The generator before this fix is kept as `pine3/build_fbg3_prelabels.py`.

33. **Position size (lots / $ / % of equity), gap-fill exits, "no trades" note, audit of all 12 grid strategies (asked 2026-11-15)** (tasks #71-#74).
    - **User reports:**
      - S10 / S12 had no trades on a 1-year test. The cause: the user's chart is M15, so they are switched off by design.
      - S1 showed 2 trades in a year. That is by design: 6-11 trades a year in 2021-25, and 2 in Jan-Oct 2026.
      - "sync" / $0 trades in all strategies: these are BE / SALV exits at the entry plus next-open catch-ups.
      - Check: `fractal/labels/counts.py`.
    - **No-trades note:** a red `table` at `position.top_center` on the last 2 bars in both builds (`NOTICE` in `pine3/build_fbg3.py`).
      It names every ticked strategy whose timeframe is below the chart's.
    - **Audit:** `fractal/labels/audit_all.py` runs `sync_why.py` (emsim3 with tags) for every strategy and chart. Output:
      `labels/audit_all_v3.txt` and `labels/readme_table_v31.md`.
      - Break-even share 30-90 %.
      - Next-open exits: M15 up to 11.9 % (S9), M1 0-5.1 %.
      - $ (`labels/emsim3_final.txt`): M15 S9 -28.5 %, S8 -19.5 %, S7 -14.7 %, S5 -11.9 %; M1 0 to -7.7 %. The BE-in-candle next-open
        exits are biased down, and SALV ones up.
    - **Bug found and fixed (grid strategy):** on a gap fill above the buy stop, the pre-placed exits were absolute prices based on E. A
      weekend gap bigger than the TP made an instant "TP" exit at the entry ($0).
      - Fix: `strategy.exit(..., profit = nE * tp / 100 / mintick, loss = nE * sl / 100 / mintick)` (ticks from the fill). The next
        candle re-sends the absolute model prices.
      - emsim3 and sync_why use distances, and compare prices at 6 decimals, because E + d and E (1 + p) differ by about 1e-12.
      - Remaining: gap-fill TP within 0.03-0.3. The "same entry, other exit: SL" cases are BE inside a candle followed by the original
        SL in the same candle (inherent).
    - **Position size, grid:** `szMode` (Fixed $ risk / Fixed lots / % of equity at risk), `baseLot`, and `eqPct` moved to MONEY.
      - `f_base(s, sd)`: lots = baseLot x lotSz x (sd + costIn); % = max(0, s.eq) x eqPct / 100.
      - `f_raw` uses it, `mmOpen` stores `s.bR`, `mmBook` uses `s.bR` (Oscar reset, Crooks G via `f_lad(s, s.bR)`), and `f_lad(s, B)`.
      - Twin: `pine_twin2.py` (f_base, P.szMode / baseLot). Reference: `recovery_tol.simulate(..., baseMode, basePct)`, with the lot
        base as the 7th tuple element.
      - Parity (`labels/parity_size.py`): 800 runs, 286,157 trades, 0 differences. The old `parity2_money.py` regression: 300 runs,
        0 differences.
      - Backups: `pine3/build_fbg3_presize.py`, `pine_twin2_presize.py`, `recovery_tol_presize.py`, `emsim3_pregap.py`.
    - **Position size, VWAP strategy (v4.7):** in `build/strategy_template.pine`.
      - `sizeMode`, `baseRiskIn` (input), `baseLot`; `eqPct` moved to GRP_R.
      - `var float baseRisk` is set in `if evArm`. `exBase` is stored at the entry and used in booking (Oscar, Crooks G via
        `f_lad(exBase)`), and `f_lad(float B)`.
      - Default mode: identical numbers.
      - Guard: `na(q) or q <= 0` means "size 0" (Oscar's 0/0 on an empty account in % mode).
      - The `f_crkRule` parameter `t1` was renamed `useT1` (shadowcheck).
      - The EA is unchanged (no lots / % base there). Backup: `build/bak/strategy_template_presize.pine`.
    - **Review:** a Sonnet high-effort sub-agent, whose findings I checked. It found no compile issue. It confirmed the default mode is
      identical and that no stale base is used. The na guard was taken. The display of the base before the first signal (non-default
      modes) was left as is.
    - **Lint:** `pinecheck/strategy_lint.py` now flags only `barstate.islast` (the known TradingView warning). Other live-bar barstates
      are only counted: the VWAP strategy has 4, never reported as warnings.
    - **Final files:**
      - Grid indicator v3.1, 1,124 lines.
      - Grid strategy v3.1, 1,247 lines.
      - VWAP strategy v4.7, 1,441 lines.
      - .txt copies in `Research/scratchpad/`.

34. **EA v4.7: Position Size (Fixed $ risk / Fixed lots / % of equity at risk), the same as the strategy (asked 2026-11-15)** (task #75).
    - **Patch:** `build/patch_ea_v47.py` (applied to `build/safe/AuctionRetestEA.mq5`; the v4.6 copy is in
      `build/bak/AuctionRetestEA_v46_presize.mq5`).
      - **Inputs:** `ENUM_SIZE_MODE` (PSZ_USD / PSZ_LOT / PSZ_PCT), `InpSizeMode`, `InpBaseLots`; `InpEqPct` moved to RISK AND POSITION SIZE
        (same name).
      - `BaseRisk(stopDist)`: lots x ((sd + CostSpr) / ts x tv + InpCommLot), as in LotsFor; % = max(0, equity) x pct.
      - `NextRisk` uses `BaseRisk(trRisk)`, sets `gBase`, and returns 0 when base <= 0 (never a zero divide).
      - `exBase = gBase` in TakeSetup. `BookBase()` (PSZ_USD: InpBaseRisk as in v4.6, else exBase) feeds the Oscar reset and Crooks G.
      - `LadBase(base, cush)`. The restart memory has `IoD("xb", exBase)` (SvVer unchanged; old memory loads).
      - OnInit refuses a base <= 0.
    - **Bug found by the new parity and fixed:** Oscar's Grind `oscNeed` int overflow with a tiny base (% of equity on an almost empty
      account). It is now clamped `MathMin(1e9, ...)`. Pine ints are 64-bit, so the Pine files are unaffected.
    - **Reference:** `gold/recovery.py` simulate has `baseMode` / `basePct`, with the lot base as the 7th tuple element (as
      `fractal/recovery_tol.py`). The pre-change copy is `gold/recovery_presize.py`.
    - **Harness changes:**
      - `mq5check/rec/build.sh`: rec_next* set exBase = gBase in the same step, as TakeSetup does (a restart cannot fall between them in
        the EA).
      - `rec_driver.cpp`: REC_SD=1 (the stop distance per trade, which sets trRisk and tick value 1).
      - Pre-change copies: `build_pre47.sh`, `rec_driver_pre47.cpp`.
    - **Checks (results in `mq5check/rec/*v47*.log`, `parity_size_1500.log`, `run/parity_v47.log`):**
      - mq5check: 0 errors, 0 warnings.
      - `parity_size_ea.py` (new modes): 10,800 runs, 10,188,179 trades, 0 differences. With REC_RESTART=3: 10,800 runs, 1,924,348 trades,
        0 differences.
      - `parity_rec.py` ($ mode regression): 7,728 runs, 11,449,048 trades, 0 differences.
      - `run/parity.py`: all identical.
      - `parity_tp1.py`: 22,484 runs, 34,075,795 trades, 0 differences.
      - `parity_crkpr.py`: 20,544 runs, 31,277,261 signals, 0 differences.
      - Rebuilt from the exact final file (PSZ_ names): compile 0 / 0; new modes 2,670,000 trades and, with restarts, 1,478,875 trades,
        0 differences; run/parity all identical.

35. **Fractal Breakout Grid EA (MetaTrader 5) (asked 2026-11-15)** (tasks #76-#78). The user asked to "make the strategy move the stop inside the
    candle like the EA". That is impossible on TradingView historical bars: they show OHLC only and act at the close or after a fill, so it
    was answered with the 1-minute chart advice. The user then asked for an EA of the grid.
    - **Files:**
      - `$S/fbgea/build_ea.py`, the generator: HEAD + 12 strategy input blocks + OPTS + CORE, then `ea_rest.mq5` (broker, replay, memory, table),
        then TAIL (Setup, lock, OnInit / OnDeinit / OnTick / OnTimer).
      - Output: `FractalBreakoutGridEA.mq5`, also at `MetaTrader5/`.
      - Progress notes: `fbgea/progress.md`.
    - **Core:** the pine_twin2.Strat model, method by method (PushTf, BarOpen, Up, Dn, BarClose, Trail, OpenAt, CloseAt, money FBase / FLad /
      FCrk / FRaw / FNext / MmOpen / MmBook).
      - It runs on 1-minute bars built from ticks: the first tick of a minute is the open (the gap rules), later ticks are path moves.
      - TF candles come from the broker (PushLive: iTime(tf, 0) changed -> CopyRates [tfLast, t0)). The trend EMA works the same way
        (TrendLive).
      - `gSim` = harness mode: no broker, the model P&L is booked, closed trades go to `gSimLog`.
    - **Live part:**
      - Entries: a virtual buy stop on the bid becomes a market Buy with the rules' SL / TP (too close: 0, kept by the EA). Magic = base +
        id; a hedging account is required.
      - `Sync` modifies SL / TP (throttled 10 s on a refusal).
      - `CloseAt` -> `BrokerClose` (PositionClose; deals via HistorySelectByPosition; a refusal -> `exitDue` retry in Reconcile).
      - `Reconcile` books broker-closed positions (DEAL_REASON SL / TP -> BE / TRAIL / SALV as the state says, else OUT).
    - **Memory and replay:**
      - Memory: `StateIO` per strategy (names s<id><key>, fingerprint tf / r / l / off resets the level), `lt` = the last bar.
      - `Restore`: silent candle rebuild up to lt (kAct from actT), then `ReplayStrat(from lt + 60, pushedTo lt, closePrev true)`.
      - `WarmStrat` (fresh start): the latest swing high from 3000 TF candles, silent pushes up to its activation (or now - InpWarmDays),
        then the replay. If the start is before the M1 history, the TF candles' highs decide whether it was used up.
      - ReplayStrat starts from the real previous M1 close.
    - **Harness (`fbgea/harness`):**
      - `export.py` writes bars.npz -> data/*.bin.
      - `build.py` translates the EA with mq5rt (its own wrapper + stubs for broker / history functions) -> `fbg_harness`, and
        `fbg_harness_rs` for the restart test.
      - `driver.cpp` pushes TF candles completed by each M1 bar, then the open and the path moves.
      - `parity.py` compares against `pine_twin2.twin2(B, 'M1', ...)` trade for trade, with the $ risk.
    - **Results:**
      - Defaults: 5,551 trades identical, $ risk within 9e-13.
      - Random option / money sets: 24 sets on the final EA, all identical (76,760 trades), with the $ risk within 5e-11.
      - The first run found 3 differing trades: time exits over a summer-time switch, because the EA used server-clock hours. Fixed: the
        time exit now compares UtcOf times. Time exits of 4 / 24 / 72 h on all 12 strategies are identical (`harness/dst_exit.py`).
      - Restart test (`FBG_RESTART`): defaults with 55 restarts, and 5 option sets with 70 restarts each, all identical.
      - mq5check: 0 / 0. The shim got the missing `CopyRates(symbol, tf, datetime start, datetime stop, rates)` overload (VWAP EA still
        0 / 0, run_tests 17 / 17).
    - **Review (Sonnet high, checked by me):** 13 findings, all verified, and the restart tests were run again (all identical).
      - Fixed:
        - 1, blocker: BrokerClose trusted a true return from PositionClose. It now books only when the position is gone and retries
          every 5 s (gExAt).
        - 2: tfLast after the replay, done with TfMark.
        - 3 / 4: Restore is seeded from the saved last price (StateIO "cl"). The rest of bar lt is processed only as last -> close,
          because its high / low may come before the entry.
        - 5: PushLive / TrendLive only move on after a read. TryStart waits for SERIES_SYNCHRONIZED for up to 60 s; the shim got
          SeriesInfoInteger.
        - 6: m > gC.T.
        - 7: Adopt.
        - 9: quiet warm-up.
        - 11: long time arithmetic.
        - 12: the lots are limited by the cap and the margin directly.
      - Not fixed: 10 (a breakout seconds before the start is taken at the first tick, a next-open style late entry) and 13 (the warm-up
        approximation when the buy stop is older than the history read).

36. **Monthly analysis: Crooks E - J x the 6 profit-ladder levels, gold M5 then M15 (asked 2026-11-15)** (tasks #79-#82). The user asked for
    every calendar month of 2021-2026 with Crooks E - J and "effort level" columns Off / Low / Medium / High / Extra high / Max, first on M5,
    then on M15. The strategy was not named, so both were done: the Fractal Breakout Grid (all strategies on an M5 chart, then an M15 chart)
    and the Auction Retest M5 / M15 catalogue strategies. Work dir `$S/mcej` (mirrored in `Research/scratchpad/mcej`, no .pkl / .json).
    - **Two readings of "each month":** ONE ACCOUNT from Jan 2021, P&L booked in the IST month of the exit (blocks 1-4), and EACH MONTH ON
      ITS OWN, a fresh $10,000 and fresh state on the 1st, trades by entry month (block 5). With a fresh month the $1,000 ladder target is
      reached in 4 of 3,500 ARS strategy-rule-months and 0 of 3,850 / 3,500 grid ones, so only the one-account view shows the levels.
    - **Trades:** `collect_ars.py` (engine re-run of M5 S1-S4, M15 S1 / S3 / S6-S9 as designed: 10 / 10 identical to the stored trades;
      fill / exit time, entry price). `collect_grid.py` (engine.run on the chart TF = pine_twin2.twin2, 21 strategy / chart runs identical;
      M5 chart S1-S11, M15 chart S1-S9 + S11; IST times).
    - **Money:** `money.py ars | grid` = gold/recovery.py (ARS) and fractal/recovery_tol.py (grid) per account, defaults: $50, $10,000,
      1:100, E / I 0.01 lot, F x3, G x10, H 1 %, J x20, target $1,000; ARS no cap, grid $500 Clamp; no lot rounding. Per trade the ladder
      flag and the start-guard flag. Grid check: the twin's own money (Crooks F + Medium) trade for trade, worst relative 1.5e-7.
      `targets.py`: ARS with ladder targets $1,000 / $2,000 / $3,000 / $5,000.
    - **Workbooks:** `build_xlsx.py OUTDIR both` -> `Gold_Monthly_Crooks_EJ_Fractal_Grid.xlsx` (Read me, Summary, M5 chart, M5 by strategy,
      M15 chart, M15 by strategy; 6,622 formulas) and `Gold_Monthly_Crooks_EJ_Auction_Retest.xlsx` (Read me, Summary M5, M5-S1..S4, Summary
      M15, M15-S1..S9, Ladder target test; 32,621 formulas). Monthly sheet: 1 month P&L (values, green = ladder on, orange = guard trades),
      2 years (SUMIFS), 3 balance (formulas), 4 deepest drop in the month, 5 each month alone; stats rows by formula; summaries link the
      sheets (INDEX / MATCH best setting per row). recalc 0 errors.
    - **Checks:** `check_xlsx.py` (7,618 cells vs the pickles, 0 differences); independent re-implementation from `verify/SPEC.md` only
      (Sonnet high, `verify/indep/sim.py` + `check.py`, re-run by me): 9,172 cells, 0 above $0.01.
    - **Findings:**
      - Grid: every level adds profit, the guard never fires. M5 chart Crooks F Off +$23,261 / Medium +$42,653 (= v2 number) / Max
        +$104,522; worst month -$590 / -$770 / -$2,122; M15 chart +$18,529 / +$33,309 / +$84,797. S1, S5, S6 never reach $1,000.
      - ARS: the start guard traps accounts. M5-S2 / S3 / S4 and M15-S9 reach $1,000 early, fall back to $0, then trade 0.01 lot for years
        (60+ guard months): M5-S2 Crooks F Off +$5,487, Low -$555, Medium -$555, Max -$558. M15-S1 / S7 the opposite: F Off +$13.3k /
        +$13.7k -> Max +$112.6k / +$138.2k (fall 16 % -> 45 % / 42 %).
      - Higher target: runs with guard trades 138 of 250 ($1,000) -> 35 ($2,000), 13 ($3,000), 2 ($5,000). M5-S2 F Medium -$555 / +$4,310 /
        +$5,415 / +$5,017. Suggested to the user: target $2,000-3,000 for the ARS ladder, or a guard that releases (not built).
    - **Delivered:** both xlsx in `Research/deliverables/` and sent to the user.

37. **Monthly analysis with the user's own settings, filters off vs on, TP1 and TP2 (asked 2026-11-15, follow-up to item 36)** (tasks #83-#85).
    The user clarified: the Auction Retest strategy with their settings (TP1 0.6, TP2 1.0; days / hours / news / kill zones), once with all
    filters off and once with their filters (Tue-Thu, 06:00-23:00, news 17:45-18:15 with 60 min before + close at its start, kill zones Asia +
    London + New York), final exit TP1 and TP2 separately, M5 then M15. Work dir `$S/mcej2` (mirrored in `Research/scratchpad/mcej2`).
    - **Settings:** the strategy's defaults = the user's screenshots (`v40/user_settings.py` 160/160, only baseRisk renamed). Engine opts = run/parity.py
      V40_REF (+ kzAuto True). Force-close 23:55 and the Saturday close kept on in both setups (trade management, not entry filters). Costs 0.23 per oz
      (commission_value 0.115 per side = spread 0.16 + $7 per lot), earn-back targets.
    - **Trades:** `ref_gse.py` = gold/ref_gs.py + per-bar events like shared_engine.pine (arm / cancel EXPIRED or REPLACED / fill / exit + win / move /
      armBar after the bar); identical trades to ref_gs in all 8 runs. `stratemu.py` = TradingView's broker emulator + strategy_template.pine sections
      1-5 at the defaults (limit from the next bar, stop at once, earn-back target after the engine fill, close at the next open on the engine's loss
      exit / force-close / Saturday / news start, entries cancelled in the news block, one trade at a time). `collect_user.py [check]`.
    - **Checks:** earn-back + time closes off -> 100 % the engine's (dir, fill bar, exit bar) in all 8 runs; win / loss differs in 0.1-0.3 % (both
      levels in one candle, TradingView's path). News flags = monthly.py news_flags (both TFs). EA broker simulator (`sim/sim46`, the EA's own code,
      M5, user defaults, 2021-01-11 .. 2026-10-03, `cmp_ea.py`): 3,014 EA vs 3,143 emulator trades, 2,920 matched (96.9 % / 92.9 %), 98.3 % same exit
      candle, 99.2 % same win / loss (TP2: 96.3 / 92.6 %, 99.1 %, 99.5 %). Money (`cmp_ea_levels.py`): the simulator books +216R (TP1) / +198R (TP2)
      only because it charges no commission and its 4 ticks a minute fill entries / targets past the order prices; at the EA's own order levels
      (bid-chart shift = the real spread) + $7 per lot: -264R / -209R; the TradingView model -185R / -138R on the same matched trades.
      Filters off, TP1 (`sim46 ... InpDayOn=0 InpHoursOn=0 InpKzOn=0 InpDNewsOn=0`): 11,182 EA vs 11,407 trades, 94.8 % / 92.9 % matched, 98.3 % same
      exit candle, 99.0 % same win / loss, 311 EA force-closes vs 293; order levels + commission -1,259R vs the model -1,027R.
    - **Review of stratemu / ref_gse vs the Pine (Sonnet high, checked by me):** no discrepancy that changes trades at the defaults. Minor: the
      'off' setup has no news window (intended: all filters off); size-0 skip not modelled (needs equity < ~$40); the summer news window uses the
      bar-open minute (= time(tf, session) per the Pine docs, unverified on TradingView); stop moves would need ex['stp'] refreshed (off by default).
    - **Independent money check (Sonnet high, `verify/indep2`, re-run by me):** 8,960 cells (off M15 TP2 block 1; on M5 TP1 and M15 TP1 block 1;
      on M5 TP2 block 5), 0 above $0.01, largest 2e-11.
    - **Money:** `money2.py` (gold/recovery.py; No recovery + Crooks E + F-J x 6 levels; $50, $10,000, 1:100 at the limit price, no cap, E / I 1 oz,
      ladder target $1,000, exitR 0.6 / 1.0). `costs.py`: fixed-risk net R at costs 0 / 0.16 / 0.23.
    - **Findings:** fixed risk, after costs: filters off M5 TP1 -1,109R, TP2 -929R, M15 -243R / -234R; your filters M5 TP1 -194.5R (59.8 % wins),
      TP2 -150.7R, M15 TP1 -81.3R, TP2 -60.1R. Without costs your filters: M5 +94R / +114R, M15 -16R / -0R (the 0.23 cost is 0.10R per trade on M5).
      M5 your filters by year: -59, -18, -79, -59, +15, +6. One account: 95 (your filters) / 118 (off) of 128 rule-level-sheet runs end wiped out
      (balance < $100; the 1:100 limit shrinks trades so it never reaches $0); survivors e.g. M5 TP2 Crooks E +$13,985. The ladder switched on in 0 /
      10 of 100 runs; where it did (off, M15 TP2, G / J), the start guard kept the account at about -$1.3k to -$1.7k. Each month alone: Crooks E wins
      most months (up to 61 of 70) with very large losing months (worst -$9,981).
    - **Workbooks:** `build_user_xlsx.py OUTDIR` (layout from mcej/build_xlsx.py + a No recovery column, grey = wiped out, a fixed-risk / cost table on
      the Summary) -> `Gold_Monthly_YourSettings_1_AllFiltersOff.xlsx`, `Gold_Monthly_YourSettings_2_YourFilters.xlsx` (13,472 formulas each, recalc 0
      errors; 4,912 cells checked vs the pickles, 0 differences).
    - **Delivered:** both xlsx in `Research/deliverables/` and sent to the user.

38. **Best monthly settings with a fresh $1,000 every month, Auction Retest and Fractal Grid (asked 2026-11-16)** (tasks #1-#3 of that session).
    The container had restarted: the scratchpad was rebuilt with `bash Research/restore.sh` (2 min) and `fractal/bars.py` (bars.npz, 5 s;
    strategy 12 needs `B['M1_' + k] = B[k]`). Work dir `$S/mcej3` (mirrored without .pkl / .npz / .json).
    - **Trades (`collect.py`):** ARS = the 19 catalogue strategies without a partial close (force-close on and off) + the user's settings (M5 / M15 /
      H1 x filters off / on x TP1-TP4) through the TradingView strategy model (mcej2 ref_gse + stratemu; built-in check: with earn-back and the time
      closes off the model = the engine in all 62 sets). Grid = the 12 strategies on the M1 model (= the grid EA). The grid part runs in a spawn
      process (another `engine.py` on sys.path shadows fractal/engine.py).
    - **Model fixes found here (mcej2, before -> `*_premove.py`):** (1) stop moves: ref_gse records the moved stop (`E_['stp']`), stratemu re-sends it
      (Pine re-sends exits with the live stp); (2) market entries (`entryMode 'market'`, all M5 catalogue strategies) fill at the next open.
      The user's-settings workbooks (item 37) are unaffected (no stop moves, model entries).
    - **Money (`search.py`):** every IST month alone, $1,000, fresh state, trades by entry month; base $5 / $10 / $20 x 38 rules (incl. Crooks E-J and
      the ladder with $50 / $100 targets) x 5 caps; ARS also the monthly lock (none, 20, 30, 50, 100, 150); grid: each strategy $1,000 / k,
      subsets summed in `choose.py` (all 4,095). 2.5 min.
    - **Choice (`choose.py`, `robust.py`, `robust2.py 300|150`):** 2021-23 only; versions calendar / mid-month (15th) / +0.07 cost; no blown window,
      deepest drop inside a window <= $300 or $150; fewest losing windows (worst version), then profit. Test 2024-26 only reported.
      Lesson: without a drop limit, recovery + monthly lock gives ~0 losing months in 2021-23 but -$880 to -$970 months in the test period.
    - **Results (70 months, $1,000 each):** both 50/50 (ARS M15-S3 fcOff Oscar's Grind $5 lock +$10 + grid S7+S8+S10 exact $5 cap $50 Clamp)
      66 profit / 4 loss, +$2,249, worst -$20; grid S7+S8+S10 exact $10 cap $100 Clamp 63 / 7, +$2,923, worst -$16; grid S1+S2+S6+S7+S8+S10 exact
      $5 cap $50 64 / 6, +$1,709, worst -$14; ARS M15-S3 fcOff Oscar's Grind $10 lock +$20 61 / 9, +$1,575, worst -$55; ARS M15-S3 fcOff no
      recovery $20 lock +$20 61 / 9, +$1,972, worst -$102. Higher risk: grid S8+S10 $20 66 / 4 (+$5,215, but a -$503 mid-month window); ARS
      M15-S6 recover-all 67 / 3 (worst -$972); user's own settings best +$238 (break-even).
    - **Checks:** independent re-implementation from `verify/SPEC3.md` (Sonnet high, re-run by me): the 5 recommended options, 70 months each, 0
      differences. Workbook `build_best_xlsx.py` -> `Gold_Best_Monthly_Settings_1000.xlsx` (Read me, Recommendations, How to set, Monthly, Top
      lists; 210 formulas, recalc 0 errors; formula values = Python).

39. **Strategy presets and the monthly restart in all six files (asked 2026-11-16)** (tasks #4-#8 of that session).
    The user asked for the monthly restart in every Auction Retest (ARS) and Fractal Grid file, and for the catalogue strategies as one-click presets
    at the top of the settings. Their answers: force-close and the Saturday close stay theirs; M1 and H1 presets too; grid presets yes, several combinations.
    - **One source of the values:** `$S/presets/preset_data.py`.
      - ARS: `crooks.sources` + `greedy.defaults()`, i.e. every engine value of the 25 catalogue strategies (M1 S1-S4, M5 S1-S4, M15 S1-S9, H1 S1-S8),
        the own session (`session()`) and the partial at TP1 (`p1`).
      - Grid: `GRID_PRESETS` G1-G6, from mcej3 `final.txt` / `final_150.txt` / `combo.txt`.
    - **ARS Pine v4.8:** `build/patch_pine_v48.py` (on `build/bak/*_v47.pine`), then `assemble.py`.
      - The engine inputs are renamed `<name>In`. The effective values follow the inputs (`PI` index, `PC` = Custom), so the engine block reads the same names.
      - Time filters:
        - `myF` = Custom or Add My Filters: days and news windows;
        - `ownS` = a preset whose own session is not replaced by the user's hours / kill zones;
        - the preset's hours use `tzHr` = Asia/Kolkata;
        - its kill zones use kzAuto off, as tested.
      - The timeframe guard `presetTfOk` is in `canArm`.
      - Strategy only: the partial `p1Pct`; the news `n*On` / `dNewsOn` through `myF`.
      - Monthly restart: `rNet0` (closed profit at the restart; the ladder, Crooks J and Rule C split count from it), `crkPk = 0`, `capStop = false`.
      - Tables: a PRESET row and the state "WRONG CHART".
    - **ARS EA v4.8:** `build/patch_ea_v48.py` (on `build/bak/AuctionRetestEA_v47.mq5`).
      - `ENUM_PRESET`, `InpPreset` and `InpAddMine` come first.
      - 92 inputs are read through `gp*`, set by `PresetApply()` first in OnInit.
      - `gpHrIst`: a preset's hours are IST (UTC + 5:30).
      - `gpTfOk` is in `canArm`. A preset sets `gTfTrade` to its own timeframe, so switching the chart to it starts trading.
      - `MonthRestart()` = RecoveryRestart + `gNet0` + `crkPk = 0` + `capStop = false`; memory key `rn`.
    - **Grid Pine v3.2:** `fractal/pine3/patch_fbg_v32.py` (on `build_fbg3_pre32.py`) -> `build_fbg3.py`.
      - New inputs: preset, Add My Days And Hours, Use My Money Settings, and `mRestartIn` in MONEY.
      - `effective(strats)` writes the values after the strategy blocks.
      - Strat fields `n0 / mKey / curM / capStp`. `mReset` runs in `mmOpen` at a strategy's first trade of a new month; a cap stop ends at the month change.
    - **Grid EA v1.1:** `fbgea/presetize.py`, called by `build_ea.py` (backup `build_ea_pre11.py`), with the same rules.
      - The twin `fractal/pine_twin2.py` got `mRestart` (backup `pine_twin2_pre48.py`).
    - **Checks (all on the final files):**
      - ARS EA:
        - `mq5check` 0/0;
        - parity 51 configurations: Custom = v4.7;
        - `mq5check/run/parity_presets.py`: the 25 presets x (as tested, user GMT 0, Add + my hours/kz, Add + days only, wrong chart) vs the research
          engine `ref_gs` with the anchors, 10 symbols, 35,307 trades identical;
        - money: `parity_rec` 7,728 runs / 11.4 M trades and `parity_crkpr` 20,544 runs, 0 differences;
        - `rec/parity_month.py` (new `mrs_driver`): the EA restart vs `recovery.simulate` fresh every month, 1,344 runs / 1.63 M trades, 0 differences,
          also with REC_RESTART=3;
        - `parity_tp1` (the cache `gold/crooks_t1p.pkl` rebuilt with `crooks_t1p.py`, 10 min): 7,700 + 14,784 runs, 34 M trades, 0 mismatches.
      - ARS Pine: parse OK, 0 inline-title warnings; all 188 / 115 old inputs unchanged in order and defaults (2 tooltips changed);
        `presets/pine_preset_check.py` reads the generated files and evaluates every preset expression: 4,025 values, 0 wrong.
      - Grid Pine: parse OK, 0 inline warnings, `namecheck` / `shadowcheck` clean, old inputs unchanged; `pine_preset_check.py` 1,488 values, 0 wrong.
      - Grid twin vs the study (`presets/grid_twin_months.py`): G1 / G2 / G4 the same in every month. G3 is within $3.18 in one month, because the
        leverage limit binds on the small study accounts. G5 / G6 are the same with large accounts (`grid_twin_g56.py`); the study's $83 accounts can be blown.
      - Grid EA: `mq5check` 0/0. `fbgea/harness/parity_v11.py`: 15 configurations vs the twin, 44,945 trades and $ risks identical:
        - the defaults = v1.0;
        - the restart with the defaults and with 4 random sets;
        - G1-G6 with random other inputs;
        - G2 + my days and hours;
        - G1 + my money, with the restart on and off.
      - Independent review (Sonnet, high effort; every finding re-checked by me):
        - no high-severity finding;
        - fixed:
          - (1) medium: the EA's warm-up (3,000 bars) did not reach the 1st of the month for a Month / Week VWAP (the M1 / M5 presets). It now
            reads back to the period start (at most 100,000 bars) and logs when the history is shorter. Custom with a Month / Week anchor gets it too;
          - (3) the grid's "next trade" text before the first trade of a month: the money now also restarts at the first candle of a new month while
            the strategy is flat, in Pine, the EA and the twin. Sizing is unchanged; parity was re-run;
          - (4) grid EA preset names were not unique (G5 / G6);
          - (5) back to Custom after a preset on another timeframe: the EA now trades the chart's timeframe (global variable `tfp`);
        - left as tested: (2) the M1 presets' London Close uses fixed IST, because the catalogue research used `kzAuto` off.
    - Harness changes:
      - `mq5check/run/mq5rt.py`: `HAS_PRESET`, so `rt_reset` calls PresetApply and `rt_look` uses `gp*`; `rt_period`;
      - `mq5check/run/rt_impl.h`: `StringToTime` (backup `rt_impl_pre48.h`);
      - do not build two harnesses at once: each build rewrites `run/mql5rt.h`;
      - `driver.cpp`: `PERIOD=`;
      - `mq5check/rec/build.sh`: `rec_init` calls PresetApply, `rec_mrestart` calls MonthRestart, plus `mrs_harness`;
      - `fbgea/harness/data` must be rebuilt with `export.py` after a restore.
    - Docs: `TradingView/README.md` sections "v4.8: strategy presets ..." and "v3.2 (EA v1.1): presets and the monthly restart", with the result
      tables (`presets/ars_table.md`, `presets/grid_table.md`).

40. **BE trigger and salvage trigger for the Auction Retest strategy (asked 2026-11-16)** (task #9). The user asked to add the grid's BE / salvage
    triggers to the ARS and find the best values on M5 and the other timeframes. Work dir `$S/bese` (mirrored).
    - **Engine:** `bese/ref_gbe.py` is made by `make_refgbe.py` from `gold/ref_gs.py`.
      - BE trigger `beR`: a candle reaches entry + beR x risk, and the stop moves to the entry.
      - Salvage trigger `svR`: a candle reaches entry - svR x risk, and the final target becomes the entry (0R).
      - Both are decided at the candle close and act from the next candle, as every engine rule (indicator / strategy / EA). Only the first acts;
        when both are reached on one candle, the extreme nearer the open counts first. Never on the fill candle.
      - With both off it is identical to ref_gs (checked on M5 Month, H1 Month and M15 session).
    - **LESSON: `gold/ref_g.py` (used by `geng.run`) resets the VWAP-period counters every day even with a Week / Month anchor.** These are
      vwBars, the session count, the sigma sums of Don't Chase and the chop counts. `ref_gs.py`, Pine, the EA and the catalogue statistics follow the
      anchor. Results for Month-VWAP strategies:
      - M5 / M1: small differences (M5-S1 1,464 vs 1,472 trades);
      - H1 Month with Don't Chase: large (H1-S8 125 vs 498 trades).
      - The first sweep was built on ref_g (kept as `ref_gbe_from_ref_g.py`, `sweep_ref_g.jsonl`). Its Month-VWAP part was re-run on ref_gs; the session
        part is identical in both. **Use ref_gs (or geng with ref_gs) for anything with a Week / Month anchor.**
    - **Sweep:** `sweep.py`, 1,776 runs, resumable `sweep.jsonl`.
      - Every catalogue strategy without a partial close (M1 4, M5 4, M15 6, H1 5) and the user's M5 settings (filters off / on x TP1-TP4).
      - BE off / 0.2-1.5R x salvage off / 0.3-0.9R (M1: a reduced grid).
      - Costs 0.23 / oz. Choose on 2021-23, test on 2024-26. `analyze.py` -> `analysis.txt`.
    - **Check:** an independent exit simulator written from `SPEC_BE.md` (Sonnet high, re-run by me on the ref_gs-based engine): `verify/check_exits.py`,
      20 cases, 0 mismatches.
    - **Result:** off is best.
      - Totals over the catalogue presets, 2021-23 / 2024-26: BE 0.3R M5 -241 / -64R, M15 -468 / -240R; salvage 0.5R M5 -170 / -79R,
        M15 -359 / -244R; salvage 0.9R (the least harm) M5 -33 / -25R.
      - M5-S1 with BE 0.3R: 63% of trades end at 0R, 2021-23 +67R -> +6R.
      - BE 1.5R (= the TP3 level) helps the presets without a stop move of their own: M15-S8 +51 / +44R -> +83 / +91R; M5-S1 +67 / +45 -> +68 / +57R;
        H1-S6 +40 / +22 -> +41 / +43R. Mixed elsewhere.
      - The user's M5 settings: BE 0.2R cuts the loss (+364R / +152R over the 8 variants) but they stay far below 0 after costs.
      - Median stop distance (% of price): M1 0.23, M5 0.27, M15 0.52, H1 0.56, the user's M5 settings 0.12.
41. **v4.9: BE trigger and salvage trigger in the ARS indicator, strategy and EA (asked 2026-11-16)** (task #10). The user wanted them for backtesting,
    with the best M5 / M15 values.
    - **Inputs:** `beOn` / `beR` (off, 1.5) and `svOn` / `svR` (off, 0.9; must be below 1) in GRP_T, inline ids `trbe` / `trsv` (`sv` was taken). EA:
      `InpBeOn` / `InpBeR` / `InpSvOn` / `InpSvR` after InpMv3R. They are not set by a preset, so they work on top of any preset.
    - **Engine:** Pine `build/patch_pine_v49.py` (on `bak/*_v48.pine`) + `assemble.py`; EA `build/patch_ea_v49.py` (on `bak/AuctionRetestEA_v48.mq5`,
      the output of patch_ea_v48.py). The rule is the same as ref_gbe.
      - `trTrig` (Pine "" / "be" / "sv"; EA 0 / 1 / 2) is reset at the fill.
      - A trigger sets `evMove`, so the strategy and the EA re-send their stop / target.
      - The salvage exit has res 0 and is not a win: `evSalv`, `svN` in BREAKEVEN.
      - The salvage target is priced without the earn-back push (`f_tgtPx0` / `TgtPx0`), so the strategy and the EA leave at the engine's level.
      - Indicator alerts: "BE TRIGGER ..." / "SALVAGE TRIGGER ..." / "SALVAGE EXIT AT ENTRY".
    - **Checks:** `mq5check` 0/0; Pine lint 0, parse OK; 4 inputs added, every other input unchanged.
      - EA parity: the 51 old configurations and the 25 presets x 5 variants are identical.
      - `mq5check/run/parity_trig.py`: the EA vs ref_gbe with the triggers on (Custom, Custom + TP2 stop to 0, M5-S1 / M5-S2 / M15-S1 / M15-S8 / H1-S1
        presets x 4 trigger settings, 10 symbols): 18 cases, 15,986 trades identical.
      - The first parity_trig run against the ref_g-based reference flagged one CRUDE trade on the M5 presets: that was the ref_g lesson above,
        not the EA.
      - Money suites on v4.9: month 1,344 runs / 1.63 M trades, rec 7,728 runs / 11.4 M, crkpr 20,544 runs / 31.3 M signals, tp1 22,484 runs / 34 M trades: 0 mismatches.

42. **Confirmation entry after a loss (asked 2026-11-17).** The user's idea: instead of the limit fill, wait for a candle that closes beyond the
   entry in the trade direction with "aggressive delta", enter at its close, stop at the entry, target extended (k x the new stop). Study
   `conf/confirm.py` (overlay on the engine's filled setups, bese/ref_gbe engine, gold FxPro 2021-2026, costs 0.23/oz): wait K 1/3/6 candles,
   delta off / close in the outer 40% / + tick volume above its 20-candle mean, stop at the entry / the candle's low, target TP1 / 1 / 1.5 / 2 x,
   minimum stop 0 / 0.15 / 0.3 x the original risk; mode A = every setup this way, mode B = normal trades, after a loss confirmation trades until
   one wins. Result (`conf/ana.txt`): the literal rule (stop at the entry) loses on all 11 bases; the win rate FALLS (30-50%) because the stop is
   tight (median $1-3 on M5) and the 0.23 cost is a large share of it. Every good catalogue strategy makes far more as it is (M15-S7 normal
   +97/+98R vs the best confirmation +15/+15R); mode B is also worse than normal on every profitable base. The user's own M5 settings are
   negative as they are (-246/-101R) and stay negative in every variant. Conclusion: no, it does not give "a win or a very small loss".
   Two trades hand-checked bar by bar.

43. **Crooks K money rule (asked 2026-11-18). BUILT in v5.0 (item 46) when the user asked on 2026-11-19.** Crooks J (+ ladder) while the month is at or above its starting balance; below it:
   0.01 lot after a loss, a CAREFUL size after a win (fixed $15/25/35, 25/50/75% of base, or 0.02/0.03/0.05 lot), repeated while it wins; the
   ladder's 0.01-lot guard is replaced. `conf/krule.py` (own simulator, parity with gold/recovery.py on 36 runs with the restart off; the monthly
   restart = the EA's MonthRestart: zero line, ladder peak, J drawdown AND the loss owed cleared), $10,000, $50 base, 1:100, 2021-2026, six trade
   sets. Result `conf/kana.txt`: K about halves the max drawdown and the worst month (M15-S1 worst month -$877 J / -$218 K) but cuts the net by
   25-60% and doubles the number of (small) losing months; profit / drawdown about equal to J, best with the lot sizing (0.02-0.03 lot: M15-S1
   9.4 vs J 8.6). $ and % sizing are the same thing ($25 = 50%: identical rows, a check). The user's M5 settings lose with every rule (K slows it:
   -$3.5k vs ruin). The user's ladder target $50 hurts on M5-S3 / M15-S8 (net -40% to -57%, twice the losing months).

44. **Variable recovery split (asked 2026-11-18, discussion only).** Crooks C over N wins with N = few parts above the month's starting balance and
   more parts below it. `conf/split.py` (parity with recovery.py Crooks C cN = N, 24 runs), `conf/split.txt`. Result: more parts below the start
   lower the biggest recovery trade (M15-S1 $401 -> $149) and the worst month a little, but the net falls towards fixed $50; profit / drawdown
   ends between Off and Crooks J, never clearly better than J. The user's M5 settings are ruined with every split. Smaller final targets (0.3 /
   0.1R) raise the win rate but lose more (M5 settings -347R -> -509R -> -750R; needed win rate 68% -> 84% -> 99%) and make recovery trades huge.

45. **Crooks L test with the user's EA settings (asked 2026-11-18; BUILT in v5.0, item 46).** Crooks L: 0.01 lot after a loss until a
   win; the recovery split by zone: below the starting balance 1 part per 2 x base of drawdown from the START (max 6), between the start and the
   best balance 1 part per 5 x base of drawdown from the PEAK (max 3), at a new best balance the base grows (+10% of the profit, max 4x).
   `conf/crl.py`: EA-like execution over the engine's setups (news block 17:45 IST 30 min + 30 min before, New York time; close at news start /
   23:55 / Saturday; earn-back target; whole 0.01 lots, minimum 0.01, 1:100), $1,000, $10 base, M5 user settings, Tue-Thu, 06-23 IST, KZ Asia /
   London / NY. Result `conf/crl.txt`: TP 0.1R: 78% wins but -519R; EVERY rule wipes the account (C / E / L by May 2021, Off Feb 2022). TP 0.6R:
   -254R, all wiped 2022-23. TP 2R: -153R; only Crooks L survives (ends $958, it mostly trades the 0.01 lot below the start). Trade sizes
   hand-traced; a first run counted stop-outs 7% too small (fixed before reporting).

46. **v5.0: Size By (Risk / Profit at the final TP), Crooks K and Crooks L in the strategy and the EA (asked 2026-11-19)** (tasks #11-#15).
    - **The ask:** a setting so the base and every loss-recovery amount are the PROFIT at the final TP (the stop-out loss follows), for every
      recovery rule; plus Crooks K (item 43) and Crooks L (item 45), "perfect, no error / bug / warning", strategy + EA.
    - **Spec:** `v50/SPEC_v50.md`. Profit: base / exitR (Fixed $ and % of equity; Fixed lots stays the lots); the amounts a rule adds / D
      (All, Over N, % of losses, Step-up, Delayed, Rule C / C split carried + step base, % of equity rule); Exact and Crooks unchanged; Oscar's
      goal = one base win; limits stay on the risk (hard cap, F / G / H / J / K, ladder, L's steps). K = J (+ ladder, no start guard) at or
      above the zero line; below it careful size after a win (lots 0.02 / $25 / 50% of base), else the E / I lot; TP1 rule off there.
      L = C family, E-like waiting lot, parts set at a booked loss from the drawdown after it (below the start 1 part / 2x base, max 6;
      below the best 1 part / 5x base, max 3), base growth +10% of the profit (max 4x) at a new best (nR >= crkPk); crkCn not used.
    - **Reference:** `v50/patch_ref_v50.py` -> `gold/recovery.py`, `gold/crooks_tp1.py` (v4.9 copies `*_v49.py`). Risk mode = v4.9:
      `v50/ref_regress.py` 27,648 + 2,128 runs identical. Independent implementation from the spec (Sonnet agent, `v50/indep/`):
      2,340 + 11,400 runs, 7.9 M trades, 0 differences (re-run by me: 2,340 runs, 0).
    - **EA:** `build/patch_ea_v50.py` (from `build/bak/AuctionRetestEA_v49.mq5`): ENUM_SIZE_BY / InpSizeBy, REC_CRK 28 / REC_CRL 29,
      ENUM_CRK_K + InpCrkK*, InpCrkL*; SizeProfit, BookBase / ShowBase / BaseTxt, KZone, KCare, LBase, LParts, LotRisk (MinLotRisk = LotRisk
      of InpCrkELot), CrkNp / CrkParts for L, NextRisk(exitR, canTake, minRisk, kRisk), TakeSetup kR, BookClosed (Oscar goal, L parts),
      table, OnInit checks. No new saved state. 3,019 lines, md5 2cf85d3481fa, mq5check 0 errors / 0 warnings, ASCII.
    - **Strategy:** `build/patch_pine_v50.py` (strategy template only; indicator unchanged): sizeBy, ck* / cl* inputs, f_lParts, f_lBase,
      kZone; inline lint 0, parse ok (797), titles unchanged (inputs_cmp: 11 added), new `pinecheck/shadow_lint.py` 0 (it caught a local
      `st` shadowing the engine's `st`, renamed lStep), independent review (Sonnet agent) no defects.
    - **Harness:** `mq5check/rec/build.sh` rec_next_k + rec_next_t1 with K / L; rec_driver / mrs_driver REC_KMIN (K careful-lot risk column);
      **rec_restart now calls PresetApply() (OnInit order)**: since v4.8 a harness restart left the gp* values at 0 (only the month suite
      had been run with restarts for v4.8 / v4.9). New suites `parity_v50.py` (rec / pr / size), `parity_month_v50.py` (restarts the harness
      after a month in which the simulator's 1e12 account blew: the harness has no account and its totals lose precision at 1e16),
      `parity_tp1_v50.py`.
    - **Results (all 0 differences):** normal mode: v4.9 suites on v5.0 rec 8,784 runs / 13.1 M trades, tp1 7,700 + 14,784
      runs / 34.1 M, crkpr 20,544 runs / 31.3 M signals; v5.0 suites rec 5,208 / 6.5 M, pr 8,960 / 10.8 M, size 8,736 / 5.2 M, month 1,840 /
      3.1 M (228 blown months compared up to the blow-up), tp1 9,240 / 19.4 M (2.1 M TP1-rule trades). Restart mode (after the harness fix)
      and the engine parity: running at this commit (`v50/run_restart_suites.sh` -> `v50/restart_progress.txt`, `mq5check/run/parity_v50.log`)
    - **Broker simulator (`sim/`, sim49 / sim50, M1 data re-exported from 2026-06-01 / 2025-07-15 for the warm-up):** defaults v4.9 vs v5.0
      SIM / BOOK lines identical (694 and 1,181 lines); 12 v5.0 runs (Profit at 0.6R / 0.3R / 0.1R, K lots / $ + ladder, L, restarts,
      monthly restart): every position booked, 0 rejects, 0 init failures; invalid K / L / Profit inputs refused at start with the message.
47. **Recover losses over N trades with the user's EA settings, every month 2021-2026 (asked 2026-11-19).** `nt3/nt3_test.py` +
    `nt3/build_xlsx.py` -> `Research/deliverables/Gold_OverN3_TP0.2_Monthly_2021_2026.xlsx` (642 formulas, recalc 0 errors). N = 3,
    final TP = TP1 0.2R, $20 base, news window, Asia / London / New York kill zones (New York time), 06:00-23:00 IST, force close and
    weekend close, no trade after 2 AM; every month from a fresh start. 3,507 trades, 77.2% won. Over N = 3 (Risk) -$13,924 (15 of 69 months
    profitable); Over N = 3 with Profit (costs included) -$24,721 (12 of 69); fixed $20 risk -$5,752; fixed $20 win -$23,372; 2025 -$267
    (6 months profitable), 2026 Jan-Sep +$51 (5 of 9). Why: at 0.2R a win nets about 0.18R against -1R for a loss (break-even win rate
    about 85%), and recovery makes the losses bigger. Building it showed v5.0's Profit wins came short by the costs -> v5.1 (item 48).
48. **v5.1: Size By Profit includes the spread and commission (2026-11-19)** (task #16). v5.0 sized Profit as risk = amount / exitR, so a
    final-TP win was amount x stop / (stop + costs) (gold M5 user settings: 8-9% short).
    - **Spec:** `v50/SPEC_v50.md` section 5. D = W / Lu per setup: Lu = the stop-out loss per unit with the costs, W = exitR x stop with
      earn-back (the target is pushed by the costs), exitR x stop - costs without; no stop / tick value or W <= 0: D = exitR (v5.0). With
      Profit every conversion uses D: the base, the rule add-ons, Exact (pool / D), the Crooks recovery and the ladder (x / D), L's growth,
      K's careful $, Oscar (need (B0 D - oscP) / (B0 D), goal one base win B0 x D kept with the trade). Risk unchanged; TP1 rule unchanged.
    - **Reference:** `v50/patch_ref_v51.py` -> `gold/recovery.py` (trade element [8] = D) and `gold/crooks_tp1.py` (`x['pd']`); v5.0 copies
      `*_v50.py`. `v50/ref_regress51.py`: no D given = v5.0, 7,920 + 160 runs identical.
    - **EA:** `build/patch_ea_v51.py` (from `build/bak/AuctionRetestEA_v50.mq5`): PDiv(exitR), NextRisk dv / xr, gBaseWin -> exBaseWin
      (saved as "xw"; a v5.0 memory without it falls back to BookBase() x ExitR()), KCare / LBase take dv, ShowBase / BaseTxt / table.
      3,035 lines, md5 f6fa6b8e4c35, mq5check 0 errors / 0 warnings, ASCII.
    - **Strategy:** `build/patch_pine_v51.py` (from `build/bak/strategy_template_v50.pine`): f_pD, pXR, f_crkRule(..., xr), exBaseWin;
      inline lint 0, shadow lint 0, parse ok (799), input titles unchanged (only the Size By tooltip's example changed).
    - **Harness:** `build.sh` rec_next* also set exBaseWin; rec_driver's REC_DAYS loop and mrs_driver read the stop distance with REC_SD.
      New suites `parity_v51.py` (rec / pr / size: Profit with REC_SD, spread 0.16, commission 7, earn-back on and off; D computed like
      PDiv and given to the reference), `parity_month_v51.py`, `parity_tp1_v51.py`; runners `v51/run_normal.sh`, `v51/run_restart_a.sh`,
      `v51/run_restart_b.sh`, results in `v51/progress.txt`.
    - **Results:** old suites (Risk) on v5.1: rec 8,784 / tp1 22,484 / crkpr 20,544 / month 1,536 / size 12,240 runs, 0 differences.
      v5.1 suites (normal): rec 9,072, pr 13,440, size 17,472, month 3,360, tp1 13,552 runs (70 M trades). They are tie-aware (a run that
      differs is compared again with every D x (1 +- 1e-12)) and the earn-back-off runs use a $5 commission: with $7 (M5 sources, costs
      0.23) or $6 (M1, 0.22) D equals the harness's own P&L ratio and every recovery / Oscar test lands exactly on its limit. Left: 2 size
      runs (Crooks L, earn-back off: the closed profit back exactly at the best after a full recovery, `nR >= crkPk` a tie) and 3 month
      runs (Crooks L, M5 0.1R no cap: the chained harness's totals reach 1e12, so nR = totalNet - gNet0 loses digits; month by month in a
      fresh harness 4.8e-12). Restart: rec 9,072 (1: % of equity at 5.7e-9 on the trade where the account blows, the same without the
      restart: start + a huge negative sum), pr 13,440 identical. Restart month 3,440 / tp1 13,552 / size 18,368 runs: the same
      differences as normal mode only (month 5: Crooks L / X chained-harness totals; size 2: Crooks L ties), tp1 identical.
    - **Broker simulator** (`sim/sim51`): defaults v5.0 vs v5.1 SIM / BOOK lines identical (694 and 1,181); Profit, recovery off, COMM 3.5 a
      side: planned TP win (lots x R x stop, stop from the EA's risk) v5.0 $46.22 / $47.78 / $48.17, v5.1 $47.21 / $49.07 / $49.56 at
      0.6R / 0.2R / 0.1R, max $49.99 (lots rounded down) (`sim/profit_win_check_v51.txt`); Oscar, Crooks C, K, L with Profit at 0.2R and a
      restart every 997 ticks: the bookings and the filled positions identical to the runs without restarts; every position booked, 0 rejects.

49. **Over N = 3 on M5 and M15, Risk and Profit, months from $1,000 / $2,000 / $10,000 (asked 2026-11-19).** `nt4/nt4_test.py TF` (the nt3
    test with the timeframe and three starts) + `nt4/build_xlsx.py START OUT` -> `Research/deliverables/Gold_OverN3_TP0.2_M5_M15_Start{1000,
    2000,10000}.xlsx` (936 formulas each, recalc 0 errors; Summary checked against the pickles). M5 $1,000 reproduces item 47 exactly.
    Totals (69 months): M5 Risk -13,924 / -17,228 / -19,561; M5 Profit -24,721 / -44,432 / -166,668; M15 Risk -2,152 (all three: the
    leverage never binds); M15 Profit -9,905 / -15,018 / -20,775. A bigger start loses more: the 1:100 limit cuts the big recovery trades
    on small accounts.
50. **v5.2: Crooks X (asked 2026-11-19)** = Crooks E with the loss to win back SET from the levels after every close: below the start the
    gap to it (whole, in N trades); above it the gap to the next step (InpCrkXStep / cxStep, $1,000) up to the best; a win into another
    step: N parts again; optional per-trade limit (dropdown Hard cap only / Per-trade limit $, default $500). Spec `v50/SPEC_v50.md`
    section 6. Reference `gold/recovery.py` (MODES[30], xStep / xLim; v5.1 copy `recovery_v51.py`), EA `build/patch_ea_v52.py` (from
    `bak/AuctionRetestEA_v51.mq5`: REC_CRX, XIdx / XTarget, BookClosed, CrkRecLimit, table, OnInit; no new saved state; 3,062 lines,
    mq5check 0 / 0), strategy `build/patch_pine_v52.py` (from `bak/strategy_template_v51.pine`: L_CRX, cxStep / cxLim / cxLimUsd, f_xIdx /
    f_xTarget). Checks: `mq5check/rec/parity_x.py` rec 2,016 + pr 1,120 runs, 0 differences; restart rec 2,016 + pr 1,120 identical; independent review (Sonnet agent) no defects; month suite with X: the
    same chained-harness precision case only (fresh per month 4.8e-12); simulator `sim/sim52` x52_*.log: booked, 0 rejects, restarts
    identical, limit held; defaults identical to v5.1.

51. **v5.3: recovery part size (asked 2026-11-19).** Spec `v50/SPEC_v50.md` section 7: Recalculate after each win (default) / Fixed when
    recovery starts for the Crooks C family (fixed part set at the first win = crL / parts, min(fx, crL) per trade; after the last part a
    leftover < the base amount (Risk base risk, Profit base win) -> new cycle, else one more trade for it; a loss or a new X step clears it).
    Reference `gold/recovery.py` partFix (v5.2 copy `recovery_v52.py`); EA `build/patch_ea_v53.py` (InpCrkPart, crkFx saved as "kq": "kx"
    was already gCrkPrPrev, caught before shipping; 75 saved keys unique; 3,083 lines, mq5check 0 / 0); strategy `build/patch_pine_v53.py`
    (crkPart, crkFx; parse ok 811). Checks `mq5check/rec/parity_fix.py` rec 5,488 + pr 1,680 runs identical (3,377 of 16,442 Crooks E N = 5
    trades differ from Recalculate, so the path is exercised); regression (old rec / tp1 / crkpr, v51 rec / pr / size / tp1, X rec / pr) same results as v5.2; restart fixed rec + pr identical; simulator sim53: defaults identical to
    v5.2, fixed E / X booked, restarts identical. Delivered as the EA + strategy .txt only (the user asked for two files).

52. **Money rules for low R (asked 2026-11-19; the user said "remember these 5 rules", NOT built yet).** `mm/mm_test.py` -> `mm/mm_results.txt`
    (independent trades, $1,000, $20 base, 1,000 trades; break-even win rate = 1 / (1 + R): 0.1R 90.9%, 0.2R 83.3%, 0.3R 76.9%, 0.5R 66.7%).
    No rule makes a negative-expectancy entry profitable. NEW single rules to remember: (1) Kelly / 1/2 or 1/4 Kelly (f = (pR - q) / R of
    equity; 0 = don't trade when the edge is negative), (2) 1-3-2-6 positive progression (reset after a loss or 4 wins), (3) equity-curve
    filter (full size when equity >= its 20-trade average, else 1/4), (4) drawdown cut (1/2 at 10% off the best, 1/4 at 20%), (5) cooling-off
    (after 2 losses in a row skip 3 trades). Already in the strategy and good with an edge: Paroli, % of equity.
53. **5 combination rules (asked 2026-11-19; NOT built yet).** `mm/combo_test.py` -> `mm/combo_results.txt`. Every one: no trade above 3% of the
    equity, the reduced sizes shrink with the account (a fixed $ floor blew the long M5 run before that change). C1 Paroli above the start /
    brake below (1/2 under 10% off the best, 1/4 under 20%); C2 1-3-2-6 above the start / the small lot (base / 8) below; C3 1.5% of equity +
    equity-curve filter (1/4 under the 20-trade average); C4 1/4 Kelly learned from the last 100 trades (no edge -> the small lot) + 1/2 at
    10% off the best; C5 profit-paid recovery (above the start Over N = 3 with the extra at most 30% of the profit above the start) / brake
    below. None blew in any test. Real 0.2R trades (one run 2021-2026 from $1,000): M5 (mean -0.087R) Fixed -968 blown, C4 -604, C3 -776,
    C2 -778, C1 / C5 -808; M15 (mean -0.056R) Fixed -960 blown, C2 -227, C4 -320, C1 / C5 -416, C3 -430. Months fresh: M15 C3 total -800,
    worst month -44 (Fixed -1,664 / -124). With an edge (80% at 0.5R): C4 and C3 grow the most, C1 / C2 / C5 with drawdowns of 9-10%.

54. **v5.4: the 10 money rules of items 52 / 53 built (asked 2026-11-20).** Spec `v50/SPEC_v50.md` section 8; Loss Recovery 31 - 40
    (EA REC_KELLY .. REC_C5, Pine L_KELLY .. L_C5), group MONEY RULES (12 inputs). Reference `gold/recovery.py` MM (v5.3 copy
    `recovery_v53.py`); EA `build/patch_ea_v54.py` (MmPushR / MmPushEq / MmMA / MmKelly, gRisk -> exRisk0, cooling skip in TakeSetup, saved
    keys z*: "mr" was already used; mq5check 0 / 0); strategy `build/patch_pine_v54.py` (arrays mmRa / mmEqA, f_mmMA / f_mmKelly, coolSkip).
    Harness: rec_cool + exRisk0 in the wrappers. `mq5check/rec/parity_mm.py`: 4,480 runs identical (the 2nd setting set uses a 4% cap: a
    cap equal to the first drawdown step makes a capped loss at the best a floating-point tie); restart 4,480 identical; old rec 8,832 / v51 rec 9,296 / fixed 5,488 / X 2,016 runs as v5.3 (the older suites skip the money rules: their compare does not read Cooling-off SKIP lines). Simulator sim54:
    every rule booked, 0 rejects, Cooling-off 99 of 102 trades, restarts identical, defaults identical to v5.3 (the simulator's $10 M
    account makes the equity rules' risks large).

55. **2024 edge search, M5 / M15 (asked 2026-11-20).** `nt5/`: `edge.py` (nt4's EA-rule trade builder for any TF / TP / filters; replica of the
    user's settings checked: M15 0.2R 1,497 trades, 2024 -0.097R), `stage1.py` (700 random settings per TF: TP 0.1-2R, stop ATR, entry, chop,
    hours, kill zones, days, VWAP, momentum, stop moves), `stage2.py` (2 hill-climb rounds incl. long / short only; 1,102 M15 + 1,173 M5),
    `stage3.py` (every money rule, Risk / Profit, on candidates), `allyears*.py`, `edge_data.py` + `build_xlsx.py` ->
    `Research/deliverables/Gold_2024_Edge_Search_M5_M15.xlsx` (recalc 0 errors; Summary / months checked against the data). Findings: no edge
    at 0.1-0.3R in 2024 on either TF; the edge is LONG ONLY with 1-2R targets (gold rose). M5 D (long, 2R, stop 2.4 ATR, market entry, chop 8,
    12:00-23:00, kill zones A/L/NY, Tue-Thu, session VWAP, momentum 1.1): 2024 +21.5R, fixed $20 +$430 (8% DD, 11/12 months); with Fibonacci /
    % of losses / Labouchere 12/12 months in 2024 but 100% drawdown in 2026 (and 2021 for some). M15 B (long, 2R, stop 4 ATR, 06-23, London +
    NY, momentum 0.6, TP2 stop move): fixed +$250 2024, 2022-2025 positive. Every candidate lost in 2021. Picked on 2024 (in-sample).

56. **Best settings per timeframe + the grid, 2021 - 2 Oct 2026 (asked 2026-11-20).** `nt6/`: `make_bars.py` (H4 / D1 from H1 -> gold/data),
    `search.py TF NRAND ROUNDS` (score = total R - 0.5 x max drawdown R; month / year R kept; random + hill-climb incl. direction; nt5 seeds),
    `picks.py` (best + picked-on-2021-2023, money rules, hindsight best per month), `build_file1.py` / `build_file2.py` (+ `common_xl.py`) ->
    `Research/deliverables/Gold_Best_Settings_Per_Timeframe_2021_2026.xlsx` and `Gold_Grid_All_Timeframes_2021_2026.xlsx` (recalc 0 errors;
    totals = months = years checked). D1: 0 trades with the EA rules (23:55 force-close + cancel-before-fill). Best (fixed $20): M1 short 2R
    +$1,714 (85.7R, 517 trades), M5 long 2R +$766, M15 long 2R +$1,399, H1 short 0.6R +$245, H4 short 0.6R +$160. Grid of all five: +$4,284,
    every year positive (648 / 837 / 1,421 / 329 / 369 / 680), max drawdown $468, 49 of 70 months positive. Picked on the same years (in-sample).
    Honest check (picked on 2021-2023 only, run on 2024-2026): M1 +9.3R, M5 -18.8R, M15 -3.5R, H1 -1.4R, H4 +1.5R - the in-sample totals overstate the edge.

57. **Grid in one file - ON HOLD (asked 2026-11-20).** Possible next work, not started: (1) a single MT5 grid EA (v6.0): one chart, five
    engine copies (M1 / M5 / M15 / H1 / H4) with the item 56 settings, own magic per engine, hedging account, verified against five separate
    EA copies on the broker simulator; (2) a TradingView grid backtester on an M1 chart (results table only: a Pine strategy holds one net
    position, so opposite-direction trades cannot be real orders). Today the grid runs as five copies of the current EA with different InpMagic.

58. **Order block + absorption + aggression test, 2026 (asked 2026-11-20).** `ob/ob_test.py` (all bars from M1; OB = last opposite candle with an
    FVG within 3 candles and a close beyond it, usable from that close; absorption = volume > 20-bar mean, body < 40%, wick into the zone >= 50%;
    aggression = later candle, body >= 55%, market entry; stops candle / last confirmed swing; outcome on M1, stop-first), `ob_summary.py`,
    `ob_xlsx.py` -> `Research/deliverables/Gold_2026_OrderBlock_Absorption_Test.xlsx` (0 errors). Pairs M1/M3, M1/M5, M5/M15, M5/M30, M5/H1,
    M15/H1, M15/H4, with and without the user's filters. Negative net R at every target for M1 and M5 entries; M15/H4 positive (+0.09R at 1R,
    75 trades; +0.20R with filters, 36 trades) - too few trades to trust.

59. **v6.0: order block strategy / EA and VWAP + order block grid (asked 2026-11-21; TradingView grid: same direction only).** New files only,
    v5.4 unchanged: `TradingView/OrderBlock_Strategy.pine`, `TradingView/Auction_Retest_OB_Strategy.pine` (+ `.txt` copies in
    `Research/scratchpad/`), `MetaTrader5/OrderBlockEA.mq5`, `MetaTrader5/AuctionRetestGridEA.mq5`. Build: `python3 -I build/build_ob_ea.py`
    (from `build/safe/AuctionRetestEA.mq5` v5.40 + `build/ob_ea_parts.py`; the grid EA = `build/classwrap.py`: the whole EA as class CLeg,
    globals -> members (inits in the constructor), functions -> methods, two legs: magic / magic + 1, objects ARM_ / ARN_, table on the other
    side) and `python3 -I build/build_ob_pine.py` (from `TradingView/Auction_Retest_Strategy.pine` v5.4; `build/grid_pine.py`: the per-slot
    engine + stats + markings + execution in `for slot = 0 to (gridOn ? 1 : 0)`, slot 1's state in the UDT `sb` exchanged around its pass,
    entries L2 / S2, exits Y1 - Y4, closed trades / positions split by entry id, `f_net()` = the slot's closed profit, `oppSkip` = same
    direction only; pyramiding 2, close_entries_rule ANY). Order block engine = `ob/ob_stream.py` (bar by bar; identical to `ob_test.py` on
    all 7 pairs, 14,962 trades). Checks (`obt/`): `prep.py` (M5 volumes + Python signals), `mk.py` (OBSIG log), `build_v.sh` / `build_g.sh` /
    `build_gr.sh` (simulator with real tick volumes; class EA; class EA with restarts), `runall.sh`, `cmp.py`: EA = Python 428/428 signals;
    grid EA VWAP only = v5.40 (364 deals), OB only = OrderBlockEA (178), grid legs = the two EAs, one at a time max 1 position, 30 restarts
    identical, 0 rejects, all booked. The data's server clock = Europe/Athens (EU summer time), so the Pine default for the H4 candles is
    that clock. Pine: `pinecheck/loop_audit.py` (no loop-local name used after the loop, no history refs in the loop).

60. **v6.1: Auction Retest + VWAP Orderflow Sniper strategy / EA (asked 2026-11-22: "drop the OB, add the Sniper").** New files:
    `TradingView/Auction_Retest_Sniper_Strategy.pine` (+ `.txt`), `MetaTrader5/AuctionRetestSniperEA.mq5`; the v6.0 OB files are kept.
    Build: `build/build_sn_pine.py` (`sn_pine_parts.py` + `grid_pine.py`), `build/build_sn_ea.py` (`sn_ea_parts.py` + `classwrap.py`).
    The Sniper = the signal logic of `Research/scratchpad/VWAP_Orderflow_Sniper.txt` on the strategy's VWAP, with its entry / stop and the
    strategy's targets and money management. Checks (`obt/`): `build_s.sh` (simulator with PERIOD_M1 series = its M1 bars + M1 / M5 volumes,
    `vol_m1.txt` / `vol_m5.txt`), `sn_mirror.py` (Python copy of the Pine engine on the EA's VWAP: 149 / 149 signals), runs `q_*.log`:
    VWAP only = v5.40 (364 deals), grid legs = single modes, 30 restarts identical, 0 rejects, all booked.

## 5. Gold pipeline: scripts in order (`$S/gold`)

| Step | Command | Output | Time, 4 free cores |
|---|---|---|---|
| Bars | `convert.py RAW.csv data` | `data/{M1,M5,M15,H1}.pkl` | 2 min |
| Engine | `ref_g.py` / `ref_gs.py` (made by `make_refg.py` from `build/ref.py`), harness `geng.py` | — | per run: M1 45 s, M5 12 s, M15 2.5 s, H1 0.8 s |
| 1 setting at a time | `sweep.py H1,M15,M5,M1` → `anaA.py TF` | `sweep_TF.pkl`, `anaA_TF.txt` | M1 about 30 min |
| Combinations | `stageB.py TF` → `repB.py TF` | `stageB_TF.pkl` | M5 about 10 min |
| Exits | `pick_cands.py TF` → `stageC.py TF` → `repC.py TF` | `stageC_TF.pkl`, `repC_TF.txt` | minutes |
| Step-by-step search | `greedy.py TF full\|lite[th] maxRounds obj:start …` | `greedy_TF.pkl` (paths), `greedy_pool_TF.pkl` (every scored version) | per round: H1 40 s, M15 2 min, M5 5 min, M1 15 min |
| Picks | `pickcfg.py TF` (`choose()`) | printed | seconds |
| Final runs | `final.py TF` | `final_TF.pkl` (cfg, passed, trades, exits, recovery, neigh) | M1 25 min |
| Rule C tests | `rulec.py` (split 1–5 × cap, each half), `rulec_caps.py` (cap $250 / $500 / $1,000 × Clamp / Start again), `rulec_stress.py` (+0.05 / 0.10 R) | `rulec*.pkl`, `rulec*.txt` | seconds |
| Strategy catalogue | `catalog.py [TF …]`: one profitable strategy per goal per timeframe, re-run for full statistics | `catalog_TF.pkl` | M1 about 6 min |
| Crooks tests | `crooks.py` (default + every catalogue strategy x Off / Rule C split ref / Crooks A / Crooks B split 1-5 / Crooks C / Crooks D x cap none / $500 Clamp / Start again / Stop, each half, stress +0.05 / 0.10 R, caps $250 / $1,000), `crooks_mc.py` (500 random orders per profitable strategy), then `crooks_refresh.py` (recovery in final_TF + catalogue money) | `crooks.pkl`, `crooks_mc.pkl`, `crooks*.txt` | 15 s, 9 min, 1 min |
| Crooks TP1 rule | `crooks_tp1.py` (engine re-run at exit TP1: default / best / low-streak per TF + the 2 best H1 TP1-exit settings; bar replay, halves, 300 random orders) | `crooks_tp1.pkl`, `crooks_tp1.txt` | 1.5 min |
| VWAP distance | `vwfilter.py collect`, `vwfilter.py collect_tp2`, `vwfilter.py scan` | `vwfilter_trades.pkl`, `vwfilter_trades_tp2.pkl`, `vwfilter_scan.pkl`, `vwfilter.txt` | 1.5 min, 1 min, seconds |
| VWAP skip rules (v3.8) | `vwfilter2.py collect`, `vwfilter2.py check`, `vwfilter2.py scan` | `vwfilter2_trades.pkl`, `vwfilter2_scan.pkl`, `vwfilter2.txt` | about 2 min, 1 min, seconds |
| TP1 rule % and any final exit (v3.8) | `crooks_t1p.py` | `crooks_t1p.pkl` (30 MB, not kept), `crooks_t1p_money.pkl`, `crooks_t1p.txt` | about 2 min |
| Crooks C single wins | `crooks_alt.py`, `crooks_alt2.py`, `crooks_alt3.py` (no cap) | `crooks_alt*.pkl`, `crooks_alt*.txt` | 1 min each |
| The user's Crooks C rules (v3.9) | `crooks_user.py` (wait for wins, skip days, forget, %; random orders over the real trade times) | `crooks_user.pkl`, `crooks_user.txt` | 1 min |
| Month-by-month workbooks | `monthly.py collect`, `monthly.py money`, `monthly.py check`, then `build_monthly_xlsx.py` | `monthly_trades.pkl`, `monthly.pkl`, 2 xlsx | 1.5 min, 1 min, seconds, 1 min + recalc |
| Monthly Crooks E-J x ladder (item 36, `$S/mcej`) | `collect_ars.py`, `collect_grid.py`, `money.py ars`, `money.py grid`, `targets.py`, `build_xlsx.py OUTDIR both`, recalc, `check_xlsx.py OUTDIR` | `*_trades.pkl`, `*_money.pkl`, `ars_targets.pkl`, 2 xlsx | 10 s, 20 s, 5 s, 3 s, 30 s, 5 s + recalc 1 min |
| Monthly, the user's settings (item 37, `$S/mcej2`) | `collect_user.py [check]`, `money2.py`, `costs.py`, `build_user_xlsx.py OUTDIR`, recalc; EA check: `sim/export_m1.py` -> `sim46 m1_all.csv 2021-01-11 2026-10-03 InpExitAt=1|2 [filters 0]`, `cmp_ea.py`, `cmp_ea_levels.py` | `user_trades.pkl`, `user_money.pkl`, `user_costs.pkl`, 2 xlsx | 1 min, 20 s, 1 min, 5 s + recalc; sim 45 s (filters on) / 7 min (off) |
| Best monthly settings, $1,000 (item 38, `$S/mcej3`) | `collect.py`, `search.py`, `choose.py`, `robust2.py 300`, `robust2.py 150`, `combo.py`, `build_best_xlsx.py OUT` | `sets.pkl`, `money_*.npz`, `final*.pkl`, `picks.pkl`, `combo.pkl`, xlsx | 2 min, 2.5 min, 10 s, 20 s each, 10 s, 5 s + recalc |
| Presets + monthly restart (item 39, `$S/presets`) | `preset_data.py`; build `build/patch_pine_v48.py` + `assemble.py`, `build/patch_ea_v48.py`, `fractal/pine3/patch_fbg_v32.py` + `build_fbg3.py OUT pick_10_12.json indicator|strategy`, `fbgea/build_ea.py OUT`; checks `pine_preset_check.py`, `mq5check/run/parity_presets.py`, `mq5check/rec/parity_month.py`, `fbgea/harness/parity_v11.py`, `grid_twin_months.py` | the 6 files | patches 5 s; parity_presets 3 min, parity_month 15 s, parity_v11 25 min, grid_twin_months 10 min |
| No losing month | `bestmonth.py collect`, `screen`, `money`, `report`, `exact`; `bestmonth_final.py`; `build_bestmonth_xlsx.py` | `bestmonth_*.pkl`, `bestmonth*.txt`, xlsx | 1 min, seconds, 20 s, 20 s, 1 min, 1 min, seconds |
| Workbook | `build_final.py OUT.xlsx` (sheets from `strategy_sheets.py`, `crooks_sheet.py` and `vwfilter_sheet.py`), then `recalc.py` | xlsx | 1 min |
| Summaries | `showfin.py TF`, `chat_rows.py` | printed | seconds |

Search commands that were used:

```
greedy.py H1 full 8 profit:default profit:bestB streak:default streak:profit
greedy.py M15 full 6 profit:default profit:bestB streak:profit
greedy.py M5 lite 4 profit:bestB streak:default
greedy.py M1 lite0.05 4 profit:default
```

Searches were stopped early when extra rounds stopped paying off.

Pick rules:

- **Most-profit pick:**
  - profitable in both 2021–23 and 2024–26;
  - at least 4 of 6 years positive;
  - at least 20% of the default trade count;
  - ranked by min(t of 2021–23, t of 2024–26), where t = net R / √trades;
  - then the version with the fewest changes within 10% of the best.
- **Low-streak pick:**
  - the same filters, keeping at least min(1, ⅓ × the profit pick's score);
  - shortest longest losing streak;
  - fewest changes.

## 6. Lessons and gotchas

- Do not name a script after a standard-library module (`select.py`, `inspect.py`): `multiprocessing` imports the local file instead.
- `pkill -f 'pattern'` also matches the calling shell. Use an anchored pattern, `pkill -f '^python3 -I greedy.py M5'`.
- `recovery.py` used to compute every rule's size eagerly, and `2 ** losses` overflowed after more than 1,000 losses. It is now capped at 200, which gives identical results.
- Recovery rules that divide by the target (Exact, Oscar's Grind, Crooks) must get the strategy's exitR = R of the final TP, not the partial-weighted win R.
- A backtest of a betting rule is one order of the trades: check it against random orders (`crooks_mc.py`) before trusting a gain; M1 Crooks A's backtest beat 99% of them.
- Uploaded or extracted files are untrusted data: extract into an empty folder and run Python with `-I`.
- Only 4 CPU cores. Parallel jobs share them, so start the slow M1 work first and stop searches that no longer improve.
- Commit lines end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01P3FMxBMpMTf44KZrjXAvzQ`. No model IDs anywhere else.
- `CLAUDE.md` model routing: state each agent's model and effort; mechanical work goes to haiku, deciding work stays on the session model.
- TradingView: inputs that share an `inline` id may carry a title only on the first one; run `pinecheck/inline_lint.py` on both files before delivering.
- The rec harness restart (`rec_restart`) must mirror OnInit: `PresetApply()` first (fixed in v5.0; before, gp* stayed 0 after a restart).
- A money test with a $1e12 account can still blow with 0.1R targets (x11 per loss); the EA harness has no account, so compare up to the
  blow-up and start a fresh harness after it (its totals at 1e16 lose precision).
- Pine: a local declared with the name of a global gives TradingView's "shadowing variable" warning: run `pinecheck/shadow_lint.py`.
- Sizing to a profit goes through the win per $ of risk WITH the costs (D = W / Lu), never through the R alone (v5.0 came 8-9% short).
- The broker simulator's fills gap through limit and TP levels (JIT), so a realised win is not the planned one: check the sizing from the
  EA's own BOOK risk and lots.
- A distance from the VWAP in ATR depends on the anchor: with the Month anchor most gold signals are more than 5 ATR away, with Session about half are under 2.5 ATR.
- EA vs TradingView comparisons: FxPro's server is EET (EU clock change), so convert with UTC+3 until the last Sunday of October and UTC+2 after;
  the EA's Orders table (armed setups, including cancelled ones) shows which TradingView-only trades were the same setup left unfilled.

## 7. Possible next steps (not requested yet)

- MT5 `.set` presets and TradingView presets for the best settings per timeframe.
- Walk-forward check: choose on 2021–24, test on 2025–26.
- The same study on another broker's gold data.
- Real-tick spreads and slippage for M1 and M5.
- Add "trade only in active hours" as a recommended default for M1 and M5.
