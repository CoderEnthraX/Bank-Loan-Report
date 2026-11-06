# Research checkpoint: Auction Retest project

**Read this first when resuming.** It records what has been built, where every file is, how to rebuild the working
environment, and what was decided. Last updated 2026-11-06 (session `21ed2550`, v3.8). No task is in progress: everything asked
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
| `MetaTrader5/AuctionRetestEA.mq5` | MT5 EA v3.8: port of the same engine plus the strategy's money management (21 recovery rules incl. Crooks A-D, Crooks TP1 rule), on-chart table and trade markings. |
| `TradingView/README.md` | User documentation of every rule and setting, v3 to v3.8 (Crooks A-D in the Loss recovery row; sections per version; v3.8: the three VWAP skip rules, kill zones and daily news follow summer time, TP1 rule % and any final exit, with the gold results). |
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
- A distance from the VWAP in ATR depends on the anchor: with the Month anchor most gold signals are more than 5 ATR away, with Session about half are under 2.5 ATR.

## 7. Possible next steps (not requested yet)

- MT5 `.set` presets and TradingView presets for the best settings per timeframe.
- Walk-forward check: choose on 2021–24, test on 2025–26.
- The same study on another broker's gold data.
- Real-tick spreads and slippage for M1 and M5.
- Add "trade only in active hours" as a recommended default for M1 and M5.
