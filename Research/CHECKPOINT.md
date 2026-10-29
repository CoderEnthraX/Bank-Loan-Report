# Research checkpoint: Auction Retest project

**Read this first when resuming.** It records what has been built, where every file is, how to rebuild the working
environment, and what was decided. Last updated 2026-10-29 (session `21ed2550`). No task is in progress: everything asked
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
| `TradingView/Auction_Retest_Model.pine` | Indicator, v3.3: clone of *Auction Retest Pro* (session VWAP + displacement + timed retest), with tables. |
| `TradingView/Auction_Retest_Strategy.pine` | The same engine as a strategy: risk sizing, partials, 19 loss-recovery rules (incl. Crooks A and B), streak pauses, news and force-close. |
| `MetaTrader5/AuctionRetestEA.mq5` | MT5 EA v3.5: port of the same engine plus the strategy's money management (19 recovery rules incl. Crooks A and B, Crooks TP1 rule), on-chart table and trade markings. |
| `TradingView/README.md` | User documentation of every rule and setting, v3 to v3.4 (Crooks A and B in the Loss recovery row). |
| `Research/deliverables/` | `Gold_2021_2026_Auction_Retest.xlsx` (gold study), `VWAP_vs_EMA_results.md`, `VWAP_settings_and_70pct_strategies.md`. |
| `Research/scratchpad/` | Every code and text file of the working scratchpad, each up to 2 MB. |
| `Research/inputs/` | The data files the user uploaded (screenshots not included), plus the Pine parser wheels. |
| `Research/results/gold/` | Compact gold results (xz pickles). `slim_*` files hold metrics only; `final_<TF>` holds the picks, trades, exits, recovery and robustness. |

Commits: v3 `ba3d37d`, v3.1 `9de5f6f` and `1ac5b0b`, v3.2 kill zones `d4624cf`, v3.3 minimum VWAP distance `952df97`,
the checkpoint `7075a27`, Rule C study `c75209e`, strategy catalogue `fac7170`, then Crooks A and B ("v3.4: Crooks A and Crooks B loss recovery"). Branch `claude/vwap-orderflow-signals-pxlzgq`. Open a PR only when the user asks.

## 3. How the code is built and checked (`Research/scratchpad/`)

- **Pine build.**
  - Sources: `build/shared_inputs.pine`, `build/shared_engine.pine`, `build/indicator_template.pine` and `build/strategy_template.pine`.
  - `build/assemble.py` writes both `.pine` files. The shared blocks (ENGINE INPUTS, ENGINE, STATS, DRAW) must be byte-identical; assemble.py checks this.
  - Pine rules followed:
    - no history references inside functions;
    - `time()` and history kept out of `and`/`or` chains;
    - ghost (invisible skip) filters: `zNo`, `chopNo`, `emaNo`, `nearNo`.
- **EA source.**
  - The canonical copy is `build/safe/AuctionRetestEA.mq5`. Copy it to `MetaTrader5/`; keep the source ASCII-only.
  - Before committing, grep for `_mq`, `#line` and `mql5rt`: a test harness once overwrote the EA with generated code.
- **EA checks.**
  - `mq5check/mq5check.py`: offline MQL5 checker using a clang++ shim.
  - `mq5check/run/`: executable parity harness (build.sh, parity.py with 28 configurations, driver.cpp). It runs the EA against the Python twin. `mq5rt.py` was fixed so it never writes `.mq5` files.
  - `mq5check/rec/`: money-management parity. `build.sh` compiles the EA's own `NextRisk()` / `BookClosed()` (copy of the EA, never written) with `rec_driver.cpp`;
    `parity_rec.py` compares the $ risk of every trade with `gold/recovery.py` on real gold sequences: every rule except % of equity, split 1-5, no cap / $500 Clamp /
    Start again / Stop. Result 2026-10-28: 1,488 runs, 1.9 million trades, 0 differences (the harness has no account, so runs the simulator ends as blown are compared up to that trade).
    `parity_tp1.py` (REC_T1 mode of the driver; build.sh makes a harness-only copy of the runtime header with settable tick value / bid / ask, and an OrderCalcMargin stub):
    the EA's TP1-rule decision and $ risk vs `gold/crooks_tp1.py` on the trades the simulator took. Result 2026-10-29: 224 runs, 381,509 trades (136,048 TP1-rule), 0 differences.
- **Python twin of the engine.** `build/ref.py` and `build/ref_ev.py`; `build/emsim_eth.py` simulates the strategy's execution.
- **Pine syntax check offline.** `pynescript` (wheels in `inputs/wheels`); see `fit/hunt/final_review`.
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
   - **Result:** 28,220 TP1-rule trades over every exit-at-TP1 setting: 25% reached TP1, 75% hit the tight stop (36% on the entry candle). Exit at TP1 is profitable
     only on 3 H1 settings; there, with $500 cap + Start again, random-order medians were negative with the rule and +$1.1k to +$1.3k without. Recommendation: off on gold.

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
| Crooks tests | `crooks.py` (default + every catalogue strategy x Off / Rule C split ref / Crooks A / Crooks B split 1-5 x cap none / $500 Clamp / Start again / Stop, each half, stress +0.05 / 0.10 R, caps $250 / $1,000), `crooks_mc.py` (500 random orders per profitable strategy), then `crooks_refresh.py` (recovery in final_TF + catalogue money) | `crooks.pkl`, `crooks_mc.pkl`, `crooks*.txt` | 15 s, 9 min, 1 min |
| Crooks TP1 rule | `crooks_tp1.py` (engine re-run at exit TP1: default / best / low-streak per TF + the 2 best H1 TP1-exit settings; bar replay, halves, 300 random orders) | `crooks_tp1.pkl`, `crooks_tp1.txt` | 1.5 min |
| Workbook | `build_final.py OUT.xlsx` (sheets from `strategy_sheets.py` and `crooks_sheet.py`), then `recalc.py` | xlsx | 1 min |
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

## 7. Possible next steps (not requested yet)

- MT5 `.set` presets and TradingView presets for the best settings per timeframe.
- Walk-forward check: choose on 2021–24, test on 2025–26.
- The same study on another broker's gold data.
- Real-tick spreads and slippage for M1 and M5.
- Add "trade only in active hours" as a recommended default for M1 and M5.
