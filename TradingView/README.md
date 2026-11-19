# TradingView indicators

| File | What it is |
|---|---|
| [`Auction_Retest_Model.pine`](Auction_Retest_Model.pine) | **Auction Retest Model**: session VWAP + displacement + time-limited retest. It reproduces the trade logic seen on the *Auction Retest Pro* reference screenshots. |
| [`Auction_Retest_Strategy.pine`](Auction_Retest_Strategy.pine) | The same engine as a **strategy** for backtesting (identical signals and trades), with money-management settings (from v4.0 the defaults are the gold / FxPro settings, see v4.0 below). |
| [`../MetaTrader5/AuctionRetestEA.mq5`](../MetaTrader5/AuctionRetestEA.mq5) | MetaTrader 5 Expert Advisor: a port of the same engine plus the strategy's money management. |
| [`VWAP_Orderflow_Sniper.pine`](VWAP_Orderflow_Sniper.pine) | The earlier VWAP + absorption/aggression orderflow indicator. |
| [`Fractal_Breakout_Grid.pine`](Fractal_Breakout_Grid.pine) | **Fractal Breakout Grid** (v3.1): 12 long breakout strategies on swing highs (your 9 + an M5, an M15 and an M1 one), each on its own timeframe, all at once or one by one, with a results table, money management (position size in $ risk, lots or % of equity; 28 loss recovery rules, profit ladder, hard cap, next trade's lots) and optional filters / exits. See below. |
| [`Fractal_Breakout_Grid_Strategy.pine`](Fractal_Breakout_Grid_Strategy.pine) | The same as a **strategy** for TradingView's Strategy Tester: the same rules and money, executed with TradingView orders (see v3 below). |
| [`../MetaTrader5/FractalBreakoutGridEA.mq5`](../MetaTrader5/FractalBreakoutGridEA.mq5) | The Fractal Breakout Grid as a **MetaTrader 5 EA**: the same 12 strategies, rules and money, with the stops moved on every tick (see below). |

## Install

1. In TradingView, open **Pine Editor** and choose **Open → New blank indicator**.
2. Paste the whole `.pine` file, then click **Save** and **Add to chart**.
3. Use a 5-minute chart. Futures and FX with volume give a true VWAP. Symbols without volume (e.g. `NSE:NIFTY`) automatically use a time-weighted average instead.

**The EA on Windows or Mac.** `AuctionRetestEA.mq5` is one file for both. MetaTrader 5 for Mac is the same terminal with the same MQL5
compiler, and the EA uses nothing Windows-specific: no DLLs, no files or folder paths, and only the Arial font. Its table measures its
text, so it fits whatever font the Mac uses.
1. In MetaTrader 5 choose **File → Open Data Folder**, then open `MQL5/Experts` and copy the file there. On the standard Mac app the folder
   is `~/Library/Application Support/net.metaquotes.wine.metatrader5/drive_c/Program Files/MetaTrader 5/MQL5/Experts` (in Finder: Go → Go
   to Folder).
   If the Mac will not copy it there, paste the code in MetaEditor instead. MetaTrader for Mac runs in a Windows layer: its folder is in
   the hidden Library, macOS blocks changes inside the app, and its folder window may not accept files dragged from Finder.
   1. Open the `.mq5` in TextEdit, then **Select All** and **Copy**.
   2. In MetaEditor, open the old `AuctionRetestEA`, or create it with **File → New → Expert Advisor (template)**.
   3. Use **Edit → Select All**, then **Edit → Paste**, then **Save**.
2. Open it in MetaEditor and compile it: F7, or **Fn + F7** on a MacBook keyboard, or the **Compile** button.
3. Keep the computer awake while it trades: a sleeping Mac stops MetaTrader. Open trades keep their stop loss and take profit at the
   broker, and the EA continues correctly when it wakes up.
4. Run the EA on one computer only. Two computers on the same account with the same magic number cannot see each other, so the copy
   check cannot stop that. The **Broker server clock = Auto** setting uses the computer's clock, so keep the date, time and time zone set
   automatically.

## Fractal Breakout Grid (indicator)

File: [`Fractal_Breakout_Grid.pine`](Fractal_Breakout_Grid.pine). The same code as text is in `Research/scratchpad/Fractal_Breakout_Grid.txt`.
Add it like any indicator (see Install). A 5-minute or 1-minute chart runs all 11 strategies; a 15-minute chart runs all but strategy 10.

**What it does.** 11 long-only breakout strategies, each on the swing highs (fractals) of its own timeframe.
1. A swing high is a candle whose high is strictly above the *Left* candles before it and the *Right* candles after it. It is confirmed
   when the last Right candle closes. Only completed candles are used, so nothing repaints.
2. A buy stop goes at swing high x (1 + offset / 100). A newer swing high replaces it.
   - A trade opens when the price rises through the buy stop.
   - One trade at a time per strategy: a breakout while a trade is open is skipped.
   - Either way that buy stop is used up.
3. Exits are measured from the fill:
   - **SL % and TP %.**
   - **BE trigger:** once the price is up this %, the SL moves to the entry.
   - **Salvage trigger:** once the price is down this %, the TP moves to the entry, so the trade closes at break-even if the price comes
     back.
   - Only the first of BE and salvage happens in a trade, and 0 turns either one off.
4. The trades are worked out on the chart's candles, along open -> the nearer of high / low -> the other -> close. Gaps fill at the open.

**Settings.**
- **Run:** all strategies, only the ticked ones, or a single one.
- **Per strategy:** On and colour, Fractal TF / Buy entry offset %, Right / Left candles, SL % / TP %, and BE / Salvage trigger %.
- **Costs per trade:** default 0.23, which is gold's 0.16 spread plus $7 per lot.
- **The date the table counts from.**
- **Display switches:** waiting buy stops, trade lines and labels.
- **Alerts:** create one alert with "Any alert() function call". It sends new buy stops (price, SL, TP), entries and exits at the candle
  close.

**Table.** One row per strategy:
- trades and win %;
- net % and net R after costs;
- profit factor and max drawdown in R;
- stop-losses in a row;
- exits by reason (TP · SL · BE · SALV);
- what the strategy is doing now: an open trade, a waiting buy stop, or waiting for a swing high.

Hover over a header to see what it means.

**How your table was read.** Every point below is also a setting.
- **Right / Left:** the first number is the right candles, as the column header says (strategy 3: 2 right, 7 left). Read this way, the 9
  strategies make +282R together; read the other way round, +173R.
- **Buy entry offset:** the buy stop sits that % below the swing high.
- **BE trigger:** the SL moves to the entry. Without it, the drawdowns are 2 to 3 times bigger.
- **Salvage trigger:** the TP moves to the entry once the trade is that % down. It rarely changes strategies 1 to 9.

**Gold results, 2021-01 to 2026-10.**
- **Data:** FxPro M1 data, costs 0.23 per trade, one trade at a time per strategy.
- **R:** 1 R = the trade's SL distance.
- **Win %:** BE and salvage exits close at the entry, so the costs make them small losses.
- **Last column:** the result if every 1-minute candle went to its high first. That is the order least favourable to a long: the BE stop
  is hit right after the BE trigger.

| # | TF | Right / Left | offset % | SL / TP % | BE / salvage % | trades | win % | TP · SL · BE · SALV | net R | PF | max DD R | SL in a row | worst year R | R, high first |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | D1 | 3 / 25 | -0.14 | 3.00 / 0.75 | 0.45 / 0.80 | 43 | 70 | 29 · 1 · 6 · 7 | +6.2 | 6.95 | 1.0 | 1 | -0.0 | +5.9 |
| 2 | D1 | 3 / 15 | -0.085 | 0.50 / 2.00 | 0.25 / 0.80 | 49 | 22 | 11 · 7 · 31 · 0 | +36.0 | 5.63 | 2.1 | 2 | -1.2 | +36.0 |
| 3 | D1 | 2 / 7 | -0.065 | 0.30 / 1.65 | 0.20 / 0.50 | 79 | 15 | 12 · 19 · 48 · 0 | +44.4 | 3.09 | 7.3 | 6 | -3.5 | +25.9 |
| 4 | H4 | 8 / 12 | -0.025 | 0.44 / 3.10 | 0.33 / 0.90 | 144 | 15 | 21 · 41 · 82 · 0 | +103.7 | 3.37 | 4.4 | 4 | +4.3 | +102.7 |
| 5 | H1 | 19 / 30 | -0.045 | 2.00 / 0.35 | 0.10 / 0.70 | 274 | 41 | 112 · 7 · 139 · 16 | +11.2 | 2.44 | 2.0 | 2 | -0.2 | +5.5 |
| 6 | H1 | 25 / 25 | -0.06 | 4.20 / 0.33 | 0.15 / 0.80 | 225 | 51 | 113 · 3 · 84 · 25 | +5.4 | 2.65 | 1.9 | 1 | -0.5 | +3.8 |
| 7 | H1 | 23 / 25 | -0.055 | 0.87 / 0.56 | 0.13 / 1.10 | 255 | 30 | 76 · 25 · 154 · 0 | +21.0 | 1.78 | 3.4 | 3 | +0.8 | +12.0 |
| 8 | H1 | 20 / 25 | -0.06 | 0.68 / 0.43 | 0.10 / 0.70 | 294 | 35 | 102 · 23 · 169 · 0 | +37.1 | 2.44 | 2.4 | 2 | +2.8 | +18.8 |
| 9 | H1 | 5 / 5 | -0.08 | 2.00 / 0.70 | 0.10 / 1.00 | 996 | 17 | 165 · 36 · 754 · 41 | +16.6 | 1.41 | 5.2 | 3 | -0.9 | +4.0 |
| 10 | M5 | 30 / 65 | -0.05 | 1.00 / 1.00 | 0.20 / 0.00 | 1192 | 22 | 264 · 161 · 767 · 0 | +91.4 | 1.54 | 7.7 | 6 | +6.8 | +75.3 |
| 11 | M15 | 20 / 40 | -0.01 | 1.00 / 3.00 | 0.20 / 0.10 | 740 | 5 | 38 · 39 · 270 · 393 | +67.6 | 2.47 | 4.8 | 4 | +2.7 | +55.6 |

All 11 strategies are profitable over the whole period, and they stay profitable when every candle goes to its high first.

**Strategies 10 (M5) and 11 (M15): how they were picked.**
- **Search:** about 2.2 million settings per timeframe (Right, Left, offset, SL, TP, BE, salvage) on M1 data, each tested under two
  candle-path assumptions.
- **Train / test split:** the settings were chosen on 2021 to 2023 only, when gold was harder for long trades, and then checked on
  2024 to 2026.
- **Required:**
  - profitable in every year 2021 to 2026, also when every candle goes to its high first;
  - SL at least 0.15 %;
  - BE off, or at least 0.10 %;
  - Right at most 30 candles.
- **Why Right is capped:** without the cap, the M5 and the M15 searches both ended on the same 5 to 15 hour swing highs, which repeat the
  1-hour strategies 5 to 8.
- **Checks on the two picks:**
  - every neighbouring setting (one step on each setting) is profitable too;
  - with costs of 0.40 instead of 0.23 they still make +83R and +62R;
  - buying at random times with the same exits makes only +11R and +12R.
- **Left out on purpose:** the tightest BE triggers (0.03 to 0.05 %) looked best on paper, but fell to about zero when the candles go to
  their high first. There the BE happens inside one 1-minute candle, and the data cannot show what really happened.

**What to know.**
- **History:** TradingView loads a limited history (an M5 chart reaches a few months back), so the table covers that period, not
  2021 to 2026.
- **Chart timeframe:** the closer the chart's timeframe is to 1 minute, the closer the table is to the results above.
- **Scope:** long only. The results are from one symbol and one period, and they do not promise the future.
- **Tuning:** if strategies 1 to 9 were tuned on this same history, their past results flatter them. Strategies 10 and 11 were checked on
  years they were not chosen on.

**Tests.** The research code is in `Research/scratchpad/fractal`.
- **Independent re-implementation:** a separate agent wrote one from the written rules only. It matched the reference engine (exact,
  1-minute paths) on 2,359 trades, with 0 differences.
- **Search evaluator vs the engine:** 0 differences on about 750,000 trades from random settings, under all three candle-path
  assumptions.
- **Indicator code vs the engine:** the indicator's code, translated line by line to Python, matched the engine on M5 and M15 chart
  candles for all 11 strategies (4,284 and 3,086 trades).
- **Pine checks:** it parses, has 0 inline-title warnings, and passed an adversarial review (no compile, runtime or repainting problem
  found; its suggestions were taken).

### v2: money management, loss recovery and more settings (November 2026)

**Money (on by default).** Every strategy is its own account; the trades themselves never change.
- **Account:** start balance $10,000 and base risk $50 per trade. units = risk / (stop distance + costs per unit).
- **Gold contract:** 100 oz per lot, lot step 0.01, leverage limit 1:100.
- **Hard cap:** $500 per trade (clamp, stop trading, or start again from the base risk).
- **Loss recovery:** the same 28 rules as the Auction Retest strategy and EA, under the same names, with their options:
  - over N wins;
  - after N losing recovery trades: forget / % / wait;
  - the Crooks E / I lot, and the F, G, H and J limits;
  - the profit ladder for Crooks F to J.
- **Default:** Crooks F + profit ladder Medium.
- **Where you see it:**
  - the table adds Net $ and the largest drawdown ($ and %);
  - the Now column shows the next trade's lots and $ risk at the waiting buy stop;
  - the labels and alerts carry the lots and $ amounts.

Gold 2021-01 to 2026-10, the 11 strategies, $50 base, $10,000 each, 200 shuffled orders per strategy:

| Rule ($500 cap, clamp, unless noted) | net, 11 strategies | average / worst max drawdown | 95 % of shuffled orders: drawdown below | shuffled orders that blew the account |
|---|---|---|---|---|
| Off (fixed $50) | +21,725 $ | 1.8 % / 3.4 % | 2.9 % | 0.0 % |
| % of equity (1 %) | +59,754 $ | 3.7 % / 7.4 % | 6.4 % | 0.0 % |
| Crooks C | +23,177 $ | 2.1 % / 5.4 % | 5.4 % | 0.0 % |
| Crooks F | +22,781 $ | 1.9 % / 3.7 % | 3.7 % | 0.0 % |
| Crooks F + ladder Low | +31,876 $ | 2.2 % / 5.0 % | 4.3 % | 0.0 % |
| **Crooks F + ladder Medium (default)** | +41,885 $ | 2.7 % / 6.2 % | 5.5 % | 0.0 % |
| Crooks J + ladder Medium | +43,324 $ | 3.1 % / 6.3 % | 6.3 % | 0.0 % |
| Crooks F + ladder Max | +104,611 $ | 6.1 % / 15.0 % | 12.1 % | 0.0 % |
| Rule C split | +108,303 $ | 5.2 % / 14.5 % | 11.8 % | 0.0 % |
| D'Alembert | +209,622 $ | 12.3 % / 27.0 % | 20.6 % | 0.0 % |
| Labouchere | +209,724 $ | 13.1 % / 29.0 % | 20.9 % | 0.0 % |
| Martingale | +152,381 $ | 11.1 % / 27.4 % | 20.5 % | 0.0 % |
| Martingale, no cap | blew the account | - | - | 27.8 % (3 of the 11 real orders too) |

- **Default choice:** Crooks F + ladder Medium about doubles the profit of fixed risk, and its worst drawdown is 6.2 %.
- **Higher-profit rules:** D'Alembert, Labouchere and Martingale make 7 to 10 times more, with drawdowns near 30 %. Only use them with
  the hard cap.

**Entry and exit options, all off by default (as tested):**
- **Entry:** buy stop (as tested) or candle close at / above the buy stop.
- **Buy-stop expiry:** after N fractal candles.
- **Entries per day:** the most per strategy.
- **Trailing stop:** start % and distance %.
- **Time exit:** after N hours.
- **Weekend close:** from a set Friday hour, New York time.
- **Trend filter:** only buy when the last closed candle of a set timeframe closed above its EMA.
- **Days and hours:** time zone, ticked days, trading hours; the same layout as the Auction Retest scripts.
- **Effect:** a breakout that a filter does not allow is skipped, and its buy stop is used up.

On gold 2021 to 2026, none of these options raised the total. Each was tested alone on all 11 strategies; total net R by option:

| Option | total net R (plain: +440.7) |
|---|---|
| hours 02-17 New York | +296.4 |
| skip Monday / skip Friday | +403.6 / +394.6 |
| trend: 4 hour EMA 50 (helps 5 of 11) | +381.0 |
| buy stop expiry 48 candles | +396.9 |
| trailing from +2 % by 1 % | +429.3 |
| time exit after a week | +432.3 |
| weekend close Friday 16:00 New York | +389.1 |
| entry on candle close | +354.9 |
| max 1 trade a day | +416.5 |

They are there for your own choices (for example, not holding over the weekend). The table shows their effect on your chart at once.

**v2 tests:**
- **v2 defaults vs v1:** with every option off, v2 gives exactly the v1 trades. M5 chart: all 11 strategies, 4,284 trades. M1 chart:
  strategies 4, 10 and 11.
- **Indicator code vs the engine with the new options:** the indicator's code, translated line by line to Python, matched the
  extended engine on 125 random option combinations (M15 and M5 charts, 4 time zones). That is 20,394 trades, all identical; the
  engine computes its filters independently.
- **Money code vs `gold/recovery.py`:** the Pine money code matched the strategy / EA reference on 2,600 random money settings (all 28
  rules, caps, ladder and options), about 880,000 trades, with 0 differences.
  - Oscar's Grind: one rounding knife-edge (zero costs) made a unit count of exactly 1 round up to 2, so the count now ignores a 1e-9
    residue.
- **End to end with Money on:** identical on 34 random settings (7,908 trades), including the cap's Stop trading.
- **Name check:** every name and every strategy field the code reads is defined.
- **Pine checks:** it parses, has 0 inline-title warnings, and passed an independent review.

### v3: strategy 12 (1 minute) and the strategy version (November 2026)

**Strategy 12 (1-minute swing highs).**
- **Settings:** Right 45 / Left 200, offset -0.05 %, SL 0.75 %, TP 3.00 %, BE 0.20 %, salvage off.
- **How it was picked:** chosen like 10 and 11, from about 900,000 settings searched on M1 data under both candle-path assumptions.
  - Chosen on 2021-2023, checked on 2024-2026.
  - Profitable in every year, also when every candle goes to its high first.
  - SL at least 0.15 %; BE off or at least 0.10 %.
  - Then ranked by its edge over random entries with the same exits.
- **Why the edge ranking:** for 1-minute swing highs, the settings with the most profit mostly ride gold's rise, and random entries do
  almost as well. The pick beats random entries by +66R (+34R in 2021-2023).
- **Robustness:**
  - +130.7R with a 13.9R drawdown and profit factor 1.50;
  - +113.4R when every candle goes to its high first; +119.3R with costs of 0.40;
  - every one-step neighbouring setting is profitable;
  - 32 % of its entries are within an hour of an entry of strategies 1 to 11.
- **Money:** with the default money rule (Crooks F + ladder Medium) it makes +$14,983 on a 1-minute chart.

**Two small rule changes (the same in the indicator, the strategy and all tests):**
- **Gap fill on the activation candle:** a buy stop also fills on a gap at the open of the candle where it becomes active, as a buy stop
  placed at the confirming candle's close would. On gold this changed only strategy 9 (+3 trades, +0.4R) and strategy 11 (+1 trade).
- **Trading hours:** read straight from "HHMM-HHMM": start included, end not, over midnight when the end is earlier, all day when they
  are equal.

All 12 strategies, gold 2021-01 to 2026-10, M1, costs 0.23 per trade:

| # | TF | Right / Left | offset % | SL / TP % | BE / salvage % | trades | win % | TP · SL · BE · SALV | net R | PF | max DD R | SL in a row | worst year R | R, high first |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | D1 | 3 / 25 | -0.14 | 3.00 / 0.75 | 0.45 / 0.80 | 43 | 70 | 29 · 1 · 6 · 7 | +6.2 | 6.95 | 1.0 | 1 | -0.0 | +5.9 |
| 2 | D1 | 3 / 15 | -0.085 | 0.50 / 2.00 | 0.25 / 0.80 | 49 | 22 | 11 · 7 · 31 · 0 | +36.0 | 5.63 | 2.1 | 2 | -1.2 | +36.0 |
| 3 | D1 | 2 / 7 | -0.065 | 0.30 / 1.65 | 0.20 / 0.50 | 79 | 15 | 12 · 19 · 48 · 0 | +44.4 | 3.09 | 7.3 | 6 | -3.5 | +25.9 |
| 4 | H4 | 8 / 12 | -0.025 | 0.44 / 3.10 | 0.33 / 0.90 | 144 | 15 | 21 · 41 · 82 · 0 | +103.7 | 3.37 | 4.4 | 4 | +4.3 | +102.7 |
| 5 | H1 | 19 / 30 | -0.045 | 2.00 / 0.35 | 0.10 / 0.70 | 274 | 41 | 112 · 7 · 139 · 16 | +11.2 | 2.44 | 2.0 | 2 | -0.2 | +5.5 |
| 6 | H1 | 25 / 25 | -0.06 | 4.20 / 0.33 | 0.15 / 0.80 | 225 | 51 | 113 · 3 · 84 · 25 | +5.4 | 2.65 | 1.9 | 1 | -0.5 | +3.8 |
| 7 | H1 | 23 / 25 | -0.055 | 0.87 / 0.56 | 0.13 / 1.10 | 255 | 30 | 76 · 25 · 154 · 0 | +21.0 | 1.78 | 3.4 | 3 | +0.8 | +12.0 |
| 8 | H1 | 20 / 25 | -0.06 | 0.68 / 0.43 | 0.10 / 0.70 | 294 | 35 | 102 · 23 · 169 · 0 | +37.1 | 2.44 | 2.4 | 2 | +2.8 | +18.8 |
| 9 | H1 | 5 / 5 | -0.08 | 2.00 / 0.70 | 0.10 / 1.00 | 999 | 17 | 166 · 36 · 756 · 41 | +17.0 | 1.42 | 5.2 | 3 | -0.8 | +4.0 |
| 10 | M5 | 30 / 65 | -0.05 | 1.00 / 1.00 | 0.20 / 0.00 | 1192 | 22 | 264 · 161 · 767 · 0 | +91.4 | 1.54 | 7.7 | 6 | +6.8 | +75.3 |
| 11 | M15 | 20 / 40 | -0.01 | 1.00 / 3.00 | 0.20 / 0.10 | 741 | 5 | 38 · 39 · 271 · 393 | +67.6 | 2.47 | 4.8 | 4 | +2.7 | +55.5 |
| 12 | M1 | 45 / 200 | -0.05 | 0.75 / 3.00 | 0.20 / 0.00 | 1256 | 8 | 98 · 245 · 913 · 0 | +130.7 | 1.50 | 13.9 | 9 | +4.9 | +113.4 |

**The strategy version: `Fractal_Breakout_Grid_Strategy.pine`.** The same code as text is in
`Research/scratchpad/Fractal_Breakout_Grid_Strategy.txt`. It has the same inputs, rules and money as the indicator, and its own table.

TradingView fills an order only from the candle after it is placed, so every order is placed at a candle's close for the next candle:
- **Buy stop:** the waiting buy stop, including a new one that this close confirms. It is only placed while the price is below it.
- **Exits:** the model's current SL / TP for an open trade.
- **Timed closes:** a time or weekend close due at the next open.
- **Next open:** where the model acts inside a candle in a way TradingView cannot, a market order at the next open follows the model.
  Those cases are:
  - an SL / TP moved by a BE, salvage or trailing trigger and hit in the same candle;
  - a dip under and back over the buy stop inside one candle;
  - a candle-close entry.

**What the trade list shows (the Signal column):**

| Signal | Meaning |
|---|---|
| S1 ... S12 | An entry by that strategy's buy stop. |
| TP / SL | The take profit / the stop loss. |
| BE | The stop was moved to the entry by the BE trigger and then hit: out at the entry price, so only the commission is lost. |
| SALV | The target was moved to the entry by the salvage trigger and then hit: out at the entry price, so only the commission is lost. |
| TRAIL / TIME / WKND | The trailing stop / the time exit / the weekend close. |
| BE next open, SALV next open, ... | The model's exit (named by its reason) happened inside a candle where TradingView cannot move an order, so the strategy closes at the next candle's open. The result is what the price did by that open: a little better or worse than the model's exit. |
| S11 next open (any S1 ... S12) | The model's entry happened inside a candle where TradingView could not fill it (or at a candle close), so the strategy buys at the next open. |
| rules flat next open | TradingView holds a trade the model does not have (not seen in the tests); it is closed at the next open. |
| off | The strategy was switched off while its trade was open. |

**Why so many trades are about $0.** TradingView counts a BE or SALV exit (the commission lost) as a losing trade, so the win % of a
strategy with BE / salvage triggers looks low. Strategy 11 (BE 0.20 %, salvage 0.10 %, SL 1 %, TP 3 %) on gold 2021-2026, 1-minute
candles: 741 trades, 393 SALV (53 %), 271 BE (37 %), 38 TP (5 %), 39 SL (5 %). About 90 % end at break-even; the few +3 % targets carry the
result (PF 2.47).

Properties (already set):
- **Commission:** 0.115 per contract per order, which is the 0.23 round-trip costs. If you change the Costs input, set it to half of
  that.
- **Initial capital:** 120,000, which is 12 accounts of 10,000.
- **Pyramiding 12, close rule "ANY":** each strategy (entry id S1 ... S12) holds its own trade.
- **Margin 0.**

The table adds a Tester $ column per strategy and a Strategy Tester summary row.

**How close the Strategy Tester comes to the indicator.** A Python model of TradingView's broker executed the strategy's orders on the
gold data:

| Chart | Strategies | Same trades (entry and exit candle and price) | Net $ vs the indicator |
|---|---|---|---|
| 5-minute | 1-11 | 93.5 % (4,010 of 4,287) | -2.6 % |
| 1-minute | all 12 | 96.4 % (5,353 of 5,551) | -1.5 % |

The trade counts are equal within 1 per strategy. With options on (16 random option sets, 15-minute chart) the counts stay equal within
3 per run. Two options leave TradingView further from the indicator:
- **Entry on candle close:** the model fills at the triggering candle's close, TradingView at the next open.
- **Trailing stop:** the model moves the stop inside the candle, TradingView at its close.

Strategy 11 on its own, by chart timeframe (the same broker model; "next open" = exits and entries made at the next open):

| Chart | Same trades as the indicator | Next-open exits | Next-open entries | Net $ vs the indicator |
|---|---|---|---|---|
| 15-minute | 89.0 % (646 of 726) | 59 (8.1 %) | 20 | +0.3 % |
| 5-minute | 92.5 % (676 of 731) | 37 (5.1 %) | 17 | -0.2 % |
| 1-minute | 96.8 % (717 of 741) | 12 (1.6 %) | 11 | -1.8 % |

The next-open exits do not bias the result. On the 15-minute chart they net +$65 over the 5 years, against -$44 for the model's own
exits of the same trades. The smaller the chart timeframe, the fewer of them, because TradingView can move the orders at every candle
close. The settings of strategies 10-12 were also picked on 1-minute candles.

Use a 1-minute chart for all 12 strategies (5-minute for 1-11). TradingView only
backtests the history it loads (on 1-minute charts a few weeks, more with Deep Backtesting).

**v3 tests:**
- **Engine:** the engine, the fast search evaluator and the indicator's Python twin with the v3 rules all agree. That is 0 differences on
  40 random settings (47,793 trades); 48 random option combinations (5,193 trades); and strategies 4, 9, 10 and 12 on a 1-minute chart
  (3,591 trades).
- **Strategy orders:** the broker model above.
- **Pine:** both files parse and have 0 inline-title warnings, every name is defined, and no name shadows another (Pine warns about
  that). The indicator build has no `strategy.` reference. The strategy uses no `barstate.islast` / `isnew` / `isrealtime` /
  `isconfirmed`: TradingView warns about those in a strategy that calculates on confirmed candles only. The table is drawn by candle
  index instead.
- **After the first TradingView run (2026-11-15):** the one warning (`barstate.islast` at 1124:4) is gone. The exit orders carry the
  model's names (BE, SALV, TRAIL), and "sync" became "... next open". Trades and orders are unchanged, and the indicator is
  byte-identical.
- **Strategy review:** an independent review found no compile error and no lookahead leak. Its fixes were taken:
  - no sync entry when a time / weekend exit is due at that open;
  - stale orders are cancelled;
  - a table variable named like a global was renamed;
  - the recalculation settings are written out.

### v3.1: position size, gap fills, the "no trades" note, and every strategy checked (November 2026)

**Position Size** (MONEY group, in the indicator and the strategy):

| Position Size | The base trade | Its input (default) |
|---|---|---|
| Fixed $ risk (default, as before) | loses the Base Risk at its stop, costs included | Base Risk Per Trade ($): 50 |
| Fixed lots | is the Base Lots, whatever its stop | Base Lots (Fixed lots): 0.01 |
| % of equity at risk | loses this % of the strategy's account at its stop, costs included | Risk % Of Equity: 1 |

- **How the loss recovery rule uses it:** the rule sizes every trade from the base trade, so with a recovery rule on, some trades are
  bigger than the base. For exactly the base on every trade (for example 0.01 lot on every trade), set Loss Recovery to Off.
- **Fixed lots in $:** a fixed lot risks lots x contract size x (stop distance + costs). That $ amount is the base the recovery rule
  works from. For example, Martingale with 0.01 lot goes 0.01, 0.02, 0.04 lot.
- **One % input:** Risk % Of Equity moved to the MONEY group. The "% of equity" loss recovery rule uses the same input.

**Strategies 10 and 12 take no trades on a 15-minute chart.** This is by design:
- Strategy 10 uses 5-minute swing highs and strategy 12 uses 1-minute ones. A strategy only runs on a chart of its own timeframe or lower.
- The table already said "needs a chart of M5 or lower". Now a red note at the top of the chart names every ticked strategy that
  cannot run there, even with the table off.
- To backtest them for a year, use a 5-minute chart (strategy 10) or a 1-minute chart (both), with Deep Backtesting.

**Strategy 1 has few trades.** That is the rule:
- It needs a daily high above the 25 daily highs before it and the 3 after it, then a breakout.
- On gold it traded 6 / 6 / 9 / 9 / 11 times in 2021-2025, and only 2 times in January-October 2026 (4 in the 365 days to 2 October 2026).

**Why so many trades are about $0, in every strategy.** Each of strategies 1-12 has a BE trigger and most have a salvage trigger. A trade
that reaches its BE trigger and comes back closes at the entry (BE). A trade that falls to its salvage trigger and comes back also closes
at the entry (SALV). Both lose only the commission, and TradingView counts them as losing trades.

Gold 2021-2026, every strategy:
- **Exits:** the rules' exits on 1-minute candles.
- **Next-open exits:** when the BE / salvage move and the return to the entry happen inside one candle, TradingView closes at the next open.
- **$ difference:** TradingView's result against the rules', from the broker model.

| # | Trades 2021-26 (1 min) | TP / SL / BE / SALV | At break-even | Next-open exits: 15 min / 5 min / 1 min | TradingView $ vs the rules: 15 min / 1 min |
|---|---|---|---|---|---|
| 1 | 43 | 29 / 1 / 6 / 7 | 30.2 % | 0.0 % / 0.0 % / 0.0 % | +0.0 % / +0.0 % |
| 2 | 49 | 11 / 7 / 31 / 0 | 63.3 % | 4.1 % / 4.1 % / 4.1 % | +0.3 % / -1.0 % |
| 3 | 79 | 12 / 19 / 48 / 0 | 60.8 % | 7.6 % / 1.3 % / 2.5 % | -6.9 % / -1.2 % |
| 4 | 144 | 21 / 41 / 82 / 0 | 56.9 % | 2.1 % / 0.7 % / 0.7 % | -0.2 % / -0.0 % |
| 5 | 274 | 112 / 7 / 139 / 16 | 56.6 % | 11.3 % / 7.7 % / 4.0 % | -11.9 % / -4.8 % |
| 6 | 225 | 113 / 3 / 84 / 25 | 48.4 % | 6.7 % / 4.4 % / 2.7 % | -6.9 % / -6.8 % |
| 7 | 255 | 76 / 25 / 154 / 0 | 60.4 % | 10.6 % / 6.7 % / 3.5 % | -14.7 % / -7.1 % |
| 8 | 294 | 102 / 23 / 169 / 0 | 57.5 % | 11.6 % / 8.5 % / 5.1 % | -19.5 % / -7.7 % |
| 9 | 999 | 166 / 36 / 756 / 41 | 79.8 % | 11.9 % / 7.0 % / 2.4 % | -28.5 % / -4.8 % |
| 10 | 1192 | 264 / 161 / 767 / 0 | 64.3 % | - / 2.2 % / 0.5 % | - / -1.6 % |
| 11 | 741 | 38 / 39 / 271 / 393 | 89.6 % | 8.1 % / 5.1 % / 1.6 % | +0.3 % / -1.8 % |
| 12 | 1256 | 98 / 245 / 913 / 0 | 72.7 % | - / - / 0.2 % | - / -0.5 % |

Strategies with a tight BE trigger lose some result on a 15-minute chart (strategy 9: -28.5 %). After a BE inside a candle the next open is
usually below the entry. On a 1-minute chart the difference is 0 to -8 %. Use the 1-minute chart for backtests.

**A bug fixed: a gap open above the buy stop.**
- **What happened:** the strategy sent the SL / TP with the buy stop as prices worked out from the buy stop. A gap open above the buy stop
  (for example Sunday's open) filled the trade at the open. When the gap was bigger than the TP distance, the TP was already below the
  fill and closed the trade at once at the entry price. That was a "$0 TP" trade the rules do not have.
- **The fix:** the SL / TP now go with the buy stop as distances from the fill. On the next candle they become the rules' exact prices.
- **The result:** in the broker model the instant exits are gone. What is left on gap fills is a TP within 0.03-0.3 of the rules' TP.

**v3.1 tests:**
- **Money:** the Python copy of the Pine money code against `gold/recovery.py`.
  - The new base modes, with random settings over every recovery rule: 800 runs, 286,157 trades, 0 differences.
  - Fixed $ risk is unchanged: 300 runs, 95,235 trades, 0 differences.
  - Fixed lots 0.01 with Loss Recovery Off gives exactly 0.01 lot on every trade. 1 % of equity risks exactly 1.000000 % on every trade.
- **TradingView orders:** the broker model runs all 12 strategies on 15-minute, 5-minute and 1-minute charts. It tags and explains every
  trade that differs from the rules (the table above).
- **Pine:** both files parse and have 0 inline-title warnings. They have no `barstate.islast` (the strategy's only TradingView warning), no
  shadowed names and no undefined names.
- **Review:** an independent review found no compile error or warning.

### v3.2 (EA v1.1): presets and the monthly restart (indicator, strategy and EA)

**PRESET** is now the first setting. **Custom** (the default) uses your settings below, exactly as before. Each of the other 6 choices is a combination from the $1,000-a-month gold study (2021–2026, the 1-minute model the EA uses).

**What a preset sets**
- It turns on its own strategies and switches the others off.
- It uses their tested settings: timeframe, candles, offset, SL, TP, BE and salvage.
- The entry and exit options are as tested.
- The money is as tested:
  - a fixed $ base risk;
  - exact recovery, or no recovery;
  - the hard cap;
  - no profit ladder;
  - the monthly restart on.
- Your own values stay saved, and Custom brings them back.

**Always your own settings, with any preset:** the weekend close, costs, start balance, leverage, display and alerts.

**Two switches under the preset**
- **Add My Days And Hours** (off): with it on, your day and hour filters apply too.
- **Use My Money Settings** (off): with it on, your base risk, loss recovery, cap, ladder and monthly restart apply instead of the preset's.

**Which chart:** use a 1-minute chart, as tested. A 5-minute chart runs every strategy except S12, which only G5 and G6 use.

**Results in the $1,000-a-month study** (calendar months in Indian time, trades counted in their entry month):

| Preset | Strategies | Money | 2021-23: losing / profitable months | total | worst month | deepest drop | 2024-26: losing / profitable months | total | worst month | deepest drop |
|---|---|---|---|---|---|---|---|---|---|---|
| Best monthly (G1) | S7, S8, S10 | $10 fixed, exact recovery, cap $100 Clamp | 4 / 32 | +1320 | -13 | 171 | 3 / 31 | +1603 | -16 | 157 |
| Safest (G2) | S1, S2, S6, S7, S8, S10 | $5 fixed, exact recovery, cap $50 Clamp | 3 / 33 | +734 | -14 | 85 | 3 / 31 | +975 | -8 | 78 |
| Steady, more profit (G3) | S1, S2, S6, S7, S8, S10 | $10 fixed, exact recovery, cap $100 Start again | 3 / 33 | +1307 | -153 | 169 | 4 / 30 | +1797 | -130 | 157 |
| Small (G4) | S7, S8, S10 | $5 fixed, exact recovery, cap $50 Clamp | 4 / 32 | +660 | -6 | 85 | 3 / 31 | +801 | -8 | 78 |
| No recovery (G5) | all 12 | $10 fixed, no recovery | 13 / 23 | +1896 | -118 | 171 | 10 / 24 | +3744 | -74 | 139 |
| No recovery (G6) | S1, S2, S3, S5, S6, S7, S8, S9, S10, S11, S12 | $10 fixed, no recovery | 11 / 25 | +1563 | -115 | 161 | 9 / 25 | +3061 | -74 | 134 |

How these results were tested:
- Each strategy was its own account of $1,000 / k (k = the number of strategies), restarted every month.
- The deepest drop is the largest fall inside one month.
- On a real account, the start balance stays yours and is larger. Then only G5 and G6 can differ: in the study, a small $83 account could be wiped out in a bad month.
- With large accounts, the twin gave exactly the study's monthly results for every preset. Small differences (G3: at most $3.18 in one month) come only from the leverage limit on the small study accounts.

**Monthly restart** (MONEY, "Restart Every Strategy's Money On The 1st Of Each Month"; off by default, on in every preset)
- At each strategy's first trade of a new month (time zone of DAYS AND HOURS; EA: your time zone), its loss recovery starts again from the base risk.
- The profit ladder, Crooks J and Rule C split count the closed profit from there.
- A hard-cap "Stop trading" ends when the month changes.
- The balance carries on.

**Checks**
- **Custom is unchanged:**
  - all inputs keep their titles, defaults and order;
  - the EA on the defaults matched the Python twin of the Pine code trade for trade: 5,551 trades, the same $ risk.
- **Monthly restart:** the twin was checked against the study's fresh-every-month results, and the EA against the twin. The tests covered the defaults and random money and option sets.
- **In total:** 15 EA configurations against the twin, 44,945 trades and their $ risk, all identical.
- **Presets:**
  - each of the 6 presets ran in the EA with random values in every other input, and the EA ignored them as it should;
  - the EA matched the twin with "Add My Days And Hours" and with "Use My Money Settings";
  - all 1,488 preset values in the indicator and the strategy were read back from the files and checked.
- **Compile and parse:** EA 0 errors / 0 warnings; both Pine files parse, with 0 warnings and every name defined.

### Fractal Breakout Grid EA (MetaTrader 5)

File: [`../MetaTrader5/FractalBreakoutGridEA.mq5`](../MetaTrader5/FractalBreakoutGridEA.mq5). It is the same 12 strategies, rules and money as the
TradingView strategy, but it acts on every tick.

**Why an EA.** A TradingView strategy cannot move a stop inside a candle in a backtest. It sees each candle's open, high, low and close
and acts at the close (hence its "BE next open" / "SALV next open" exits). The EA sees every tick:
- **BE and salvage:** the moment the price touches the BE trigger, the SL moves to the entry (the salvage trigger moves the TP the same way).
- **No next-open exits:** there are none.
- **All 12 strategies on any chart:** each strategy reads its own timeframe's candles from MT5.

**Install.**
1. Copy the file to `MQL5/Experts` and compile it (F7).
2. Attach it to an XAUUSD chart. Any timeframe works, because the rules run on 1-minute bars of the ticks, as in the research.
3. Allow algo trading.

It needs a **hedging** account: every strategy holds its own position, with magic number base + strategy number (26111 ... 26122 by
default).

**How it trades.**
- **Swing highs:** they come from the broker's completed candles on each strategy's timeframe. The D1 and H4 candles of brokers on
  New York close time (GMT+2 / +3) are the same as TradingView's.
- **The buy stop:** it waits on the bid. When the bid goes through it, a market buy opens with the rules' SL and TP at the broker.
- **On every tick:** BE, salvage and trailing move the SL / TP. The broker always holds them. One too close to the price (stops level)
  stays with the EA until it can be placed.
- **Rule exits:** an exit the rules call (time, weekend, or a level the broker does not hold yet) closes at market. A position the broker
  closes itself (SL, TP, stop-out, by hand) is booked with its real result and its reason.
- **Money:** each strategy is its own account (Start balance), with Position size (Fixed $ risk / Fixed lots / % of equity at risk), the
  28 loss recovery rules, the profit ladder, the hard cap and the leverage limit, as in the TradingView files.
- **Real results are booked:** each trade's real result (profit + commission + swap) goes into its strategy's account. Lots are rounded
  to the broker's step: at least the minimum lot, reduced if the free margin is short.

**Restart memory.** The state is kept in MT5 global variables (`FBG|symbol|magic|...`): the buy stops, the open trades, the money and
the stats.
- **After a restart:** the minutes missed are caught up from the 1-minute history. The buy stops follow the rules and no new trade opens
  for those minutes. An open trade is managed as the rules say: an exit that was missed closes it at once.
- **A fresh start:** each strategy reads its latest swing high and the 1-minute history since it started (60 days by default), so a
  buy stop the price already went through is not taken again.

**Inputs.**
- **Grid:** run all, the ticked ones or one strategy; magic number base; the spread and commission used for sizing (0.16 + 7 per lot
  on gold = the 0.23 costs of the TradingView files).
- **Strategies 1-12:** on / timeframe / right / left / offset / SL / TP / BE / salvage, with the same defaults as TradingView.
- **Entry and exit options, days and hours, money, loss recovery:** the same choices and defaults as the TradingView strategy.
  - Your time zone is a fixed GMT offset (India 5.5).
  - The broker's clock is read from MT5 (Auto).
  - "Candle close" entry uses 1-minute candles.
- **Display:** a table (per strategy: trades, win %, net $, TP / SL / BE / SALV, and what it does now) and lines for the waiting buy
  stops and the open trades' SL / TP.

**Tests.** The EA's own code was compiled into a test harness. Its rules ran on gold 2021-2026, 1-minute bars along the research's
path (open, nearer extreme, other extreme, close).
- **Against the Python copy of the Pine code:** trade for trade, every entry and exit time, price and reason, and the $ risk of every
  trade.
  - Defaults: 5,551 trades (S1 ... S12: 43 / 49 / 79 / 144 / 274 / 225 / 255 / 294 / 999 / 1,192 / 741 / 1,256), all identical; $ risk
    within 1e-12.
  - Random option and money sets (candle-close entry, expiry, max per day, trailing, time / weekend exits, the EMA filter, days /
    hours, all 28 recovery rules, the ladder, caps, the three position sizes): 24 sets on the final EA, all identical (76,760 trades), with the $ risk within 5e-11.
  - **A bug the comparison found, now fixed:** "Close a trade after N hours" counted hours on the broker's clock, which jumps an hour at
    the US summer-time switches. Trades open over a switch closed an hour early or late. It now counts real hours (UTC). Time exits of
    4 / 24 / 72 h on all 12 strategies are identical (8,758 / 6,660 / 6,003 trades).
- **Restart memory:** a save, a fresh program and a reload every 26-29 days of data gives the same trades and accounts as a run without
  restarts. That holds for the defaults (55 restarts) and for five option sets (70 restarts each).
- **Compile:** 0 errors and 0 warnings in the offline MQL5 check (MetaEditor itself is not available here).
- **Review:** an independent review of the live parts (orders, catch-up, memory), checked by me. Its findings were fixed, and the
  restart tests were run again:
  - **A refused close:** a close the broker refuses (MT5's trade library still returns true for it) could have been booked as closed
    while the position stayed open. Now a trade is only booked when its position is gone. Refused closes are tried again every
    5 seconds.
  - **A restart in the same minute:** the minute the EA was in when it stopped is finished from its last price, so a gap through a buy
    stop at the next open is not missed.
  - **History still loading:** the EA waits (up to 60 s) until MT5 has loaded the history it needs. Candles not read yet are read on the
    next tick, not skipped.
  - **A position without memory:** after a crash between a buy and the save, the position (its magic number) is adopted and managed.
  - **Older ticks:** a tick with an older time no longer starts a new minute.
  - **Rounding up to the minimum lot never goes past the hard cap,** and the free margin limits the lots directly.

The broker part (orders, deals) cannot run outside MetaTrader. Test it first in the Strategy Tester ("Every tick based on real ticks",
a hedging account) and on a demo account.

## Auction Retest Model: how a trade is built

The rules below were fitted to **80 trades of the original indicator** read candle by candle from 53 screenshots, and then checked against
**80 more trades a student logged with the real indicator** (SENSEX, MCX crude, NSE NIFTY futures, MCX natural gas, 5-16 Oct).

| Step | Rule | Default |
|---|---|---|
| VWAP | Session VWAP, reset at each new trading day | Session |
| Side filter | Longs only when the signal candle closes above VWAP and VWAP is higher than 3 bars ago; shorts the opposite. On a session's first bars the slope looks back into the previous session | On / 3 bars |
| Displacement | A confirmed candle closing beyond the highest high (long) / lowest low (short) of the previous **6** bars. Body >= 55 % of its range, close within 25 % of its extreme, range >= 0.8 ATR, close >= 0.85 ATR beyond the close 10 bars earlier, and a clean move: **CMO(10) >= 20** (net move / total distance travelled) | 6 / 55 % / 25 % / 0.8 / 0.85 / 20 |
| Session start | The session's first bar may signal; bars opening on Sunday (UTC), the thin weekly reopen, are skipped | 0 bars / On |
| Re-anchored break | Within 10 bars of a closed trade's fill, a new signal in that trade's direction must break the high (long) / low (short) made since that fill | On |
| Armed | Limit = the shallower of the 50 % body level and the 6-bar high (long) / low (short) before the candle, for 5 bars. A newer candle in the same direction does not move an armed limit; an opposite one replaces it | 5 bars |
| Filled | Price trades back into the limit: ▲ / ▼ marker, trade boxes start on this bar, the stop is also checked on it | — |
| Stop | Entry ∓ 1.8 × ATR(14) | 1.8 |
| Half stop | The first impulse of a session in a direction gets entry ∓ 0.9 ATR (or just beyond the signal candle if that is further) when the previous session had >= 3 more impulses the other way, **or** the session opened outside the previous session's range against the trade. An impulse = a candle with range >= 0.8 ATR, body >= 50 %, close within 25 % of its extreme, wick beyond the 10-bar extreme and VWAP sloping its way | 0.9 / 3 |
| Targets | TP1-TP4 = 0.6 / 1 / 1.5 / 2 R; the trade ends at the final target (**TP4, +2R**, in the reference; v4.0 default **TP1**) or the stop (stop first when a bar touches both). Levels unrounded | 0.6/1/1.5/2 |
| Controls | One trade at a time (carried over sessions), no new setup on the exit bar, at most 5 fills per day in the reference (v4.0 default 10), **no daily R stop** (the original keeps trading after three losses) | 1 / 10 / off |

**Accuracy against the original** (all numbers re-run on the final engine):

| Ground truth | Published v2 | **v3** |
|---|---|---|
| 80 screenshot trades | 79 exact, 1 missed, 3 extra | **80 exact, 0 missed, 1 extra; all 80 stops right** |
| Student log SENSEX + MCX crude (42) | 32 matched | **41 matched, 38 stops right** |
| Student log NSE NIFTY futures (20) | 15 matched | **20 matched, 18 stops right** |
| Student log MCX natural gas (18) | 12 matched | **16 matched, 12 stops right** |
| 6 MODEL DAY table readings | 6/6 | 6/6 |

Remaining differences: one CRUDE long on 10-06 21:00 (CMO 21.7, just above the filter), one CRUDE trade whose entry needs a second signal
type (optional setting below), a few logged stops that the logged exit times show are student typos, and two natural gas stops.

### Settings added in v3 (identical in the indicator, the strategy and the EA)

| Group | Setting | Default |
|---|---|---|
| Signal model | Deep pullback signal (a second signal type, 1 supporting trade); Strict bias check for the half stop (3 supporting trades) | Off |
| Entry price | Model · Custom % of the signal candle · Market (next bar open) | Model |
| Targets, exit and stop moves | Final exit at TP1-TP4; move the stop when TP1 / TP2 / TP3 hits (breakeven at +1R = TP2 → 0) | TP1 (v4.0; TP4 before) / off |
| Accuracy filters (research) | **Don't chase**: skip a signal more than 2.4 σ from the session VWAP; the skipped setup still runs invisibly so the next, more stretched candle is not taken instead. **After a loss, no same-direction trade until a win** (rest of the session) | Off |
| Days and hours | **Trade only on the ticked days** (Mon ... Sun) and trade only between two times, in your time zone (default Asia/Kolkata). They stop new setups only; open trades finish | On from v4.0: Tue / Wed / Thu, 06:00-23:00 |

### Settings added in v3.1 (all off by default; identical in the indicator, the strategy and the EA)

| Group | Setting | What it does | Research result |
|---|---|---|---|
| Signal model | **Half stop never wider than the normal stop** | A half stop that would sit further from the entry than the 1.8 ATR stop (after a very tall signal candle) is pulled in to the normal stop | One more logged stop matched (NIFTY futures #27), 3 of 1,190 trades changed, all 80 screenshot stops unchanged |
| Accuracy filters | **Skip choppy sessions: max VWAP crosses per 100 bars** (default limit 12) | Counts how often the close has crossed the VWAP so far in the session (from more than 0.2 ATR on one side to more than 0.2 ATR on the other). Above the limit a new setup is skipped and runs invisibly, like Don't Chase | Average +0.17R → +0.21R per trade, October +0.20R → +0.27R, total +197R → +207R, 82 % of trades kept, 9 of 10 instruments better, natural gas +0.28R → +0.34R. Not proven; it skips mostly the same trades as Don't Chase, so use one or the other |
| Accuracy filters | **Skip when the 1h EMA20 moved more than X ATR in 3 hours** (default 1.65) | Builds 1-hour candles (UTC hours) from the chart and skips a setup when the EMA20 of the last completed hour has moved more than the limit from 3 hours earlier (an over-extended trend); runs invisibly | Average +0.17R → +0.23R, total +197R → +199R, 72 % kept, 8 of 10 instruments better, **natural gas worse** (+0.28R → +0.08R). Not proven |
| Accuracy filters | **Skip signals too close to VWAP: min distance** (default 1.0 ATR) | Skips a long whose signal candle closes less than this many ATR above the VWAP (short: below); runs invisibly like Don't Chase. Together with Don't Chase it makes a band (e.g. 1 ATR to 2σ) | 1:1 win rate 54.0% → 54.7%, 1:2 38.9% → 39.8%, +0.17R → +0.20R per trade, total +197R → +218R, 94 % kept, 8 of 10 instruments better. With Don't Chase at 2.0σ: 1:1 57.5 %, 1:2 43.9 %, +0.32R per trade, about half the trades. Not proven |
| Style | **Show trade markings** (default on) | One switch for the limit line, boxes, entry and TP lines and fill triangles | — |
| Days and hours | **Trade only in kill zones** (Indian time), each zone ticked separately: Asia 05:30-09:30, London 11:30-14:30, New York 16:30-19:30, London close 19:30-21:30; **Shift all kill zones** −2 … +2 hours (e.g. +1: Asia 06:30-10:30); these are the summer times, and since v3.8 London / London close and New York move 1 hour later in their winter time by themselves (see v3.8) | New setups are armed only inside the ticked zones (bar open time, end not included); open trades and armed limits finish. The table says OUTSIDE KILL ZONES | — |

The tables also gained **TP HIT** (share and number of closed trades that reached TP1, TP2, TP3 and TP4 before the stop), **BREAKEVEN** (shown when a
Move Stop setting is on: trades closed at breakeven or at a locked profit) and **SKIPPED BY FILTERS** (shown when a filter is on: how many
setups the filters skipped and what those trades would have done, so you can judge a filter on your own charts).

**Accuracy research** (separate from the clone; October data held out of every fit): the don't-chase filter raised the October 2R hit rate
from 39 % to 42 % and the average from +0.18R to +0.26R per trade with 75 % of trades kept; the after-loss rule helped in October only;
breakeven at +1R cut full losses from 62 % to 47 % and the longest losing streak from 20 to 8 without changing the average. Volume /
delta / absorption / exhaustion proxies, deeper entries and trend filters did not help beyond chance. Looking back over whole days,
sessions that keep crossing the VWAP lose (−0.13R per trade) and trend days carry the profit (+0.55R), but at the signal only about a third
of that is visible, which is why the VWAP-cross filter above helps only a little. Flat or squeezed EMAs mark the *best* trades, not the worst,
and EMA trend-agreement or pullback-to-EMA rules removed more winners than losers. Forward-test before relying on any filter.

### Settings added in v3.6 (identical in the indicator, the strategy and the EA)

| Group | Setting | What it does | Gold 2021–2026 result |
|---|---|---|---|
| Accuracy filters | **Skip signals too far from VWAP: max distance** (off; default 5.0, unit **x ATR** or **Price**) | Skips a signal whose candle closes farther than this from the VWAP (with the anchor you set: Session, Week or Month), above or below (distance = \|close − VWAP\| on the signal candle, in ATR(14) or in price). The skipped setup runs invisibly like Don't Chase, so the other signals stay the same, and SKIPPED BY FILTERS shows what the skipped trades would have done. EA: `InpMaxVwOn`, `InpMaxVwDist`, `InpMaxVwUnit` | Far trades were not the losers on gold. With the Session anchor every cut-off from 2 to 4.5 ATR lowered the profit per trade (the far trades were the better ones); 5 ATR did the least harm, so it is the default value. Over all 30 profitable settings the best cut-off (5 ATR) gave a better R per trade in both 2021–23 and 2024–26 on only 9 (worse on 3) and cut total profit from +2,386R to +1,488R because it skips 47% of the trades. A fixed price distance did worst (gold's ranges doubled from 2021 to 2026). **Keep it off on gold**; test it on your own market with the SKIPPED BY FILTERS row. Workbook sheet *VWAP distance* |

Settings that share one line in the settings window now carry one title for the whole line (e.g. *Targets TP1 · TP2 · TP3 · TP4 (R)*), which removes
TradingView's 34 "title of an inline input" warnings in the strategy and 24 in the indicator. Values and defaults are unchanged.

### Settings added in v3.7 (strategy and EA only; the signals are unchanged)

| Group | Setting | What it does | Gold 2021–2026 result |
|---|---|---|---|
| Loss recovery | **Crooks TP1 Rule: Stop Before TP1** (EA `InpCrkT1Stop`; default Normal stop from v4.0, Tight before) | For the "Crooks At Exit TP1" trades only. The size stays the same (half at TP1 banks the whole recovery amount, the rest runs to TP2 with its stop at the entry); only the stop before TP1 changes: **Tight** (TP1 ÷ 2, a stop-out loses 1× the amount), **0.45R** (about 1.6×), **0.6R** (about 2.1×), **Normal stop** (the 1.8 ATR or half stop, about 3.5×), **Normal stop on the entry candle, then tight**, **Normal stop, tight after a candle closes in profit**, **Normal stop, breakeven after a candle closes in profit**. Stop moves happen at a candle close and act from the next candle. The hard cap limits the real stop-out loss, so a wider stop means a smaller amount per trade (with $500 and the normal stop, about $145). In the EA a TP1-rule trade too small to split (e.g. 0.01 lot with a 0.01 minimum) closes completely at TP1, with no TP2 half | Average per recovery trade over 14 exit-TP1 settings: Normal stop −0.06×, plain (checkbox off) −0.07×, all others −0.14× to −0.17×. On the 3 settings profitable at exit TP1 (H1), Crooks C + $500 Start again: Normal stop +$1,760 / +$2,283 / +$2,053 against plain +$589 / +$896 / +$921 and Tight +$44 / −$1,365 / −$1,204 |
| Loss recovery | **Crooks C: Win The Loss Back Over N Wins** (off, N = 1; EA `InpCrkCnOn`, `InpCrkCn`) | 1 = the trade after a win wins back the whole loss (Crooks C as before). 2 = it wins back half; if it wins, the next trade wins back the rest. 3 = a third, then the next third, then the rest. A loss at any point: base trades until the next win, then the parts start again from the new loss. The table shows "recovery trade, part 1 of 2" | 25 profitable strategies, $500 cap + Start again: total +$125.6k (N 1), +$128.0k (N 2), +$123.6k (N 3), +$128.4k (N 4); without a cap the account blew in 16% / 9% / 4% / 2% of random trade orders on average (worst strategy 43% / 31% / 17% / 10%) |
| Risk | **Lot Rounding**: Down / To the nearest lot step (default Down in both from v4.0; the EA's default was nearest before) and **size below the minimum lot**: trade the minimum / skip (EA `InpSmallLot`, default the minimum; the strategy's "If Size Is Below 1 Lot Step") | Nearest: 0.125 lot → 0.13, 0.124 → 0.12, 0.009 → 0.01; below the minimum (e.g. 0.004) → 0.01. It never rounds up past the hard cap or the leverage limit, and the minimum lot is skipped when its stop-out loss would break the hard cap or the leverage limit. Rounding comes first, so with nearest rounding "skip" only applies to sizes that round to 0 (below half a step) | — |

### Settings added in v3.8

| Group | Setting | What it does | Gold 2021–2026 result |
|---|---|---|---|
| Accuracy filters | **Skip When The Stop Is Beyond The VWAP: Buffer (x ATR)** (off, buffer 0; EA `InpStopVwOn`, `InpStopVwBuf`) | Skips a long whose stop is below the VWAP (short: above): the signal is still sitting on the VWAP and the VWAP is inside the trade's risk. Buffer 0 = the stop must be on the trade's side of the VWAP; −1 = up to 1 ATR past it is allowed; +0.5 = at least 0.5 ATR clear of it. VWAP and ATR of the signal candle. Like Don't Chase, the skipped setup runs on invisibly (the other signals stay the same) and SKIPPED BY FILTERS shows what it would have done | 13 Session-VWAP settings profitable in both 2021–23 and 2024–26, all trades pooled: buffer 0 raised the profit per trade from +0.088R to +0.138R and was better in both halves on 9 of 13 (worse on none), but it keeps only 19% of the trades, so the total fell from +1,225R to +357R. Buffer −1: +0.120R, 36% kept (+610R), better in both halves on 10 of 13. With the Month VWAP it made things worse (worse in both halves on 9 of 17) |
| Accuracy filters | **Skip When The VWAP Was Touched In The Last N Candles** (off, N 3; EA `InpTouchVwOn`, `InpTouchVwN`) | Skips a long when the low of the signal candle or of one of the N − 1 candles before it reached the VWAP (short: the high): price has only just left the VWAP. N 1 = the signal candle only. Each candle is compared with its own VWAP | N 3: +0.088R → +0.108R per trade, better in both halves on 7 of 13 (worse on none), 57% of the trades kept (+862R). N 2 did not help |
| Accuracy filters | **Skip When The Entry Is Too Close To The VWAP: Min Distance (x ATR)** (off, 0.75; EA `InpEntVwOn`, `InpEntVwAtr`) | Skips a long whose entry (the retest level) is less than this many ATR above the VWAP (short: below), or on the other side of it | 0.75 ATR: +0.088R → +0.094R, better in both halves on 6 of 13 (worse on none), 86% kept (+1,129R) |
| Days and hours | **Kill Zones Follow London / New York Summer Time** (on; EA `InpKzAuto`) | The kill-zone times are the summer times in IST. London and London Close move 1 hour later while London is on winter time (last Sunday of October to last Sunday of March: 12:30–15:30 and 20:30–22:30 IST), New York while New York is on winter time (first Sunday of November to second Sunday of March: 17:30–20:30 IST). Asia never moves (Tokyo has no summer time). The switch happens at the exact hour the clocks change; **Shift All Kill Zones** adds on top. Off = the old fixed times | — |
| News (strategy, EA) | **Daily News Window Follows New York Time** (on; EA `InpDNewsAuto`) | Set the daily window as it is in New York summer time (US data at 8:30 New York = 18:00–19:00 IST); while New York is on winter time it moves 1 hour later (19:00–20:00 IST), so it stays on the same New York time. The strategy works the move out for any time zone in DAYS AND HOURS (London: only in the 2–3 weeks a year when the two switch on different dates); the EA's own clock is a fixed GMT offset, so it moves 1 hour in New York winter. Off = the same time in your zone all year | — |
| Loss recovery | **Crooks TP1 Rule: % Closed At TP1** (50; EA `InpCrkT1Pct`, 10–90) | For the Crooks TP1-rule trades: this share of the position closes at TP1 and alone banks the whole recovery amount; the rest's stop moves to the entry and it closes at TP2. The position risks 1 ÷ (% × TP1) times the amount without costs: 50% with TP1 = 0.6R → 3.33× (the "owed ÷ 0.3" size), 30% → 5.6×, 70% → 2.4×. The tight stop sits at % × TP1 − (1 + %) × costs, so a stop-out there still loses exactly the amount. The EA rounds the TP1 part up to the lot step | see below |
| Loss recovery | **Crooks TP1 Rule: Works With Any Final Exit** (off; EA `InpCrkT1Any`) | Off: the TP1 rule acts only with Final Exit At TP1. On: also with Final Exit TP2, TP3 or TP4; the TP1 part closes at TP1 and the rest at TP2 (also with TP3 / TP4). The other trades keep the normal exits. The stop moves (When TP1 / TP2 / TP3 Hits, Move Stop) and the partial profits do not apply to the TP1-rule trades | see below |

**Half at TP1 and the rest at TP2 with the normal stop, whatever the Final Exit:** Loss Recovery = Crooks A / B / C / D, tick *Crooks At Exit TP1*,
*Stop Before TP1* = **Normal stop**, *% Closed At TP1* = **50**, tick *Works With Any Final Exit* (EA: `InpCrkT1` = true, `InpCrkT1Stop` = Normal stop,
`InpCrkT1Pct` = 50, `InpCrkT1Any` = true). Only the recovery trades change; with half and TP1 = 0.6R a stop-out at the normal stop loses about 3.3×
the amount, so keep the hard cap on (with $500 the amount per trade is at most about $150).

Gold 2021–2026, the 14 exit-TP1 settings of the TP1-rule study, each also run with Final Exit TP2 (`gold/crooks_t1p.py`), Crooks C with the $500 cap
and Start again:

| Final exit | Box off (plain Crooks C) | Tight stop 30% / 50% / 70% | Normal stop 30% / 50% / 70% |
|---|---|---|---|
| TP1: settings in profit (of 14) | 3 | 1 / 2 / 3 | 8 / 7 / 5 |
| TP1: average net | −$4,448 | −$7,594 / −$5,848 / −$5,008 | −$2,392 / −$3,444 / −$3,717 |
| TP2 + any final exit: settings in profit | 6 | 1 / 2 / 5 | 7 / 6 / 6 |
| TP2 + any final exit: average net | −$1,681 | −$6,905 / −$6,390 / −$4,573 | −$2,533 / −$2,729 / −$3,382 |
| Per recovery trade (multiples of the amount), TP1 / TP2 | −0.07 / −0.02 | −0.25 to −0.12 | −0.06 to −0.05 |

The normal stop was better than the tight stop at every %. At Final Exit TP1 the TP1 rule with the normal stop beat the plain Crooks C; at
Final Exit TP2 the plain Crooks C (box off) did better on average. The settings that were the defaults in v3.8 lose with every variant. A smaller % makes the
position bigger, so the $500 cap starts a new cycle sooner (30%: whenever the amount is above about $90), which explains part of its result.

### Settings added in v3.9 (strategy and EA only; the signals are unchanged)

| Group | Setting | What it does |
|---|---|---|
| Loss recovery | **Crooks C: After N Losing Recovery Trades In A Row** (Off; EA `InpCrkPr`) and **N** (2; `InpCrkPrN`) | Crooks C only. When N recovery trades in a row have lost (recovery trades that lost with no winning recovery trade between them; base trades between them do not break the count): **Forget the loss**: a new cycle starts at the base risk (the money lost stays lost, it is just no longer chased). **Go for a % of the loss, forget it after N** (% box, 50; `InpCrkPrPct`): every recovery trade goes for that % of the loss, the rest is forgotten when it wins. **Wait for M wins in a row, then a loss and a win** (M box, 2; `InpCrkPrM`): every trade risks the base until M trades win in a row; then, after the next loss and the win after it, the trade after that win is the recovery trade (the loss is kept). **Skip D trading days** (D box, 3; `InpCrkPrD`): no new trades for the rest of that day and D more trading days in the DAYS AND HOURS time zone (the ticked days when Trade Only On The Ticked Days is on, Monday to Friday when it is off), then Crooks C goes on; **Forget The Loss After The Skipped Days** (off = keep it; `InpCrkPrForget`); **Count Every Day, Not Only The Trading Days** (`InpCrkPrAll`). Example: Tue / Wed / Thu ticked, D = 3, the trade closes on a Tuesday: the rest of Tuesday, Wednesday, Thursday and next Tuesday are skipped; trading starts again next Wednesday. The table shows the state (lost recoveries in a row, waiting for wins, paused with the days left; STATE: CROOKS C PAUSE) and counts the paused signals as skipped ("Crooks C pause"). The hard cap still works on top |

Gold 2021–2026, the 19 strategies profitable at fixed $50 (no partial close), Crooks C with **no hard cap**, $50 base (`gold/crooks_user.py`;
200 random orders of the same trades over the real trade times). A worst fall above 100% means an account was blown in the real order:

| Rule | Total profit | Average fall | Worst fall | Biggest single loss (average) | Blown in random orders |
|---|---|---|---|---|---|
| Crooks C as now | +$225k | 40.2% | 92% | $1,916 | 20% |
| Forget the loss after 2 / 3 | +$100k / +$108k | 13.9% / 14.7% | 26% / 27% | $344 / $434 | 0% / 0% |
| 50% of the loss, forget after 2 / 3 | +$93k / +$96k | 11.3% / 11.1% | 20% / 20% | $156 / $171 | 0% / 0% |
| Wait for 2 wins after 2 (then a loss and a win) | +$182k | 27.4% | 95% | $1,110 | 14% |
| Wait for 3 wins after 2 | +$114k | 26.5% | 107% | $1,168 | 10% |
| Skip 3 days after 2, keep the loss | +$176k | 32.0% | 111% | $1,463 | 18% |
| Skip 3 days after 2, forget the loss | +$89k | 15.0% | 32% | $343 | 0% |
| Skip 2 days after 3, forget the loss | +$107k | 14.1% | 27% | $434 | 0% |

Rules that keep the whole loss (wait, skip and keep) still blow the account in 10–18% of the random orders; the rules that forget the loss
(or go for part of it) never did. On gold a win does not make the next trade more likely to win (after a win 41.6%, after a loss 39.4%), which is
why timing rules help less than limiting what is chased.

### v4.0: your settings are the defaults (indicator, strategy and EA)

The defaults of all three files are now the settings traded on gold with FxPro (the TradingView strategy settings of 7 November 2026), so a fresh
copy of the strategy and of the EA take the same trades without changing anything. Nothing in the signal logic changed.

| Group | v4.0 default (TradingView = EA) |
|---|---|
| Signal model | As before, plus **Half Stop Never Wider Than The Normal Stop** on (`InpHalfCap`) and **Max Fills Per Day** 10 (`InpMaxFills`) |
| Entry, targets | Model entry (Custom % 25), targets 0.6 / 1 / 1.5 / 2 R, **Final Exit At TP1** (`InpExitAt`), no stop moves |
| Days and hours | **Tuesday, Wednesday, Thursday**, **06:00-23:00** India time, kill zones **Asia, London, New York** (London Close off), following London / New York summer time |
| Risk | $50 base risk, hard cap off ($250, Start again), leverage 1:100, lot rounding **Down**, below one lot step: trade the minimum |
| Costs | Spread **0.16**, commission **$7 per lot** round trip (FxPro gold: $3.50 a side), earn-back on; TradingView **Properties -> Commission 0.115** per contract (the value the strategy's table asks for with these costs) |
| Force-close, news | Force-close 23:55, close when Saturday starts, no new trades 60 minutes before news, daily news window **17:45-18:15** India time, following New York time |
| Loss recovery | **Crooks C** (Crooks TP1 rule off, Crooks C rule Off) |
| EA only | **Broker server clock: auto with EU summer time** (FxPro); **Match bid-chart levels** on; new **Spread** input (`InpSpread`, 0.16): the lot size, the earn-back and the Crooks TP1-rule distance use this spread, like TradingView, instead of the live spread, so lots and target levels are the same as TradingView's (0 = the live spread, as before) |

The values of switched-off settings were copied too (e.g. Don't Chase 2, Choppy 13.5, stop for the day after 23 losses, Crooks C rule D = 4), so both
files read the same.

**Loading v4.0.** TradingView keeps the input values of a strategy already on the chart: remove the old one and add the new one (or Settings ->
Defaults -> Reset settings), then check Properties -> Commission. MetaTrader 5 remembers the last inputs in the Strategy Tester: after compiling the
new EA, reset its inputs to the defaults. With another broker check **Broker server clock**; with another symbol change the spread and the commission.

**Why the 6 Oct - 6 Nov 2026 tests differed** (`Research/deliverables/TradingView_vs_EA_6Oct_6Nov_2026.xlsx`): 35 of TradingView's 52 trades were
the same in the EA. Nine settings were different (news window 17:55 for 75 minutes, US server clock, London Close on, kill zones not following summer
time, 5 fills a day, bid-chart matching off, lot rounding to the nearest step, commission 0.16, half-stop cap off); they caused 12 of the differences
directly and probably 4 more, and most of the rest followed from those (one different trade changes the next signals and the Crooks C recovery
trades). What no setting changes: OANDA and FxPro are different price feeds (the candles differ by a few cents, and the volume that weights the VWAP
is different), so expect a few different trades a month. The trading day is not one of the differences: gold is closed 17:00-18:00 New York time and
FxPro's first candle of every server day is the 18:00 New York reopen, the same candle TradingView starts its session on, all year (its report had
23 hours of candles on every test day, the late-October week included).

Checks: every default of the strategy, the indicator (160 settings) and the EA (162) compared with the screenshots, 0 differences, confirmed by an
independent reviewer; EA lot size = TradingView's formula in 8 hand cases; engine parity 51 configurations (3 new with the v4.0 defaults), also with
the data moved across the October / November and March clock changes, 0 differences; money management `parity_rec.py` 1,680 runs / 2.15 M trades,
`parity_tp1.py` 5,824 runs / 7.98 M trades, `parity_crkpr.py` 5,184 runs / 7.43 M signals, 0 differences (the older test configurations pass the
v3.9 defaults explicitly).

### EA v4.1: Crooks C hedge rule (EA only)

New choice in **Crooks C: After N Losing Recovery Trades In A Row** (`InpCrkPr`): **Hedge: a buy and a sell on the next signal**. After N recovery
trades in a row have lost (the N box, default 2), the next signal the EA takes opens a **buy and a sell at the same entry price**, both sized like
the recovery trade, each with its own stop loss and take profit at the broker:

| Input | Default | What it does |
|---|---|---|
| `InpCrkHgSl` hedge stop loss | 1 | Stop loss of both trades (in R: 1 = the signal's own stop distance) |
| `InpCrkHgTp` hedge take profit | 0.6 | Take profit of both trades (in R: 0.6 = TP1) |
| `InpCrkHgUnit` | R | R (x the signal's stop distance) or Price (e.g. 5.0 = $5 on gold) |
| `InpCrkHgForget` | on | On: when both trades have closed, forget the loss and start again from the base risk. Off: keep what is left of the loss; if the trade that closed last won, the next trade is a recovery trade, if it lost, base trades until a win |

The two trades run to their own stop loss and take profit: the engine's exit, stop moves, earn-back, partials and the TP1 rule do not touch them;
force-close, weekend and news close them like any trade. New signals are skipped while they are open, and the table shows "hedge pair on the next
signal" / "hedge pair open". It needs an MT5 **hedging** account: on a netting account a buy and a sell cancel out, so there the rule forgets the
loss instead (a message in the Journal). With the default 0.6R target and 1R stop, a price that keeps going one way gives one target and one stop
(-0.4R for the pair); the pair wins 1.2R only when the price reaches both targets. With a take profit beyond the stop loss both trades can
lose; with the hard cap on, each trade then risks at most half the cap. The stop loss and take profit are kept at least the broker's minimum
distance plus the spread from the entry; the free margin must carry both trades; if only one of the two can be opened it is closed again (never one
trade alone); a trade still waiting when the other has opened is cancelled at force-close, weekend and news. Not tested on gold (built on request
without a test). The TradingView strategy does not have this rule: a TradingView strategy cannot hold a buy and a sell at the same time.

Checks: compile 0 errors / 0 warnings; the EA's own code run through scripted sequences (forget, keep with the last trade lost / won, netting
account): trigger, recovery sizing and booking as described; engine parity 51 configurations (3 shifts) and money-management parity (1,680 /
5,824 / 5,184 runs) unchanged, 0 differences; independent review (5 edge cases fixed: the distances above, a gap past a level, a lone trade, margin
for both trades, a waiting trade after force-close / news).

### v4.2: monthly profit lock (strategy and EA; all off by default)

New group **MONTHLY PROFIT LOCK** (TradingView: "MONTHLY PROFIT LOCK (strategy only)"; the indicator does not have it). The month is the calendar
month in your time zone (TradingView: the Time Zone of DAYS AND HOURS; EA: `InpUserGMT`), and only closed trades count, with their costs.

| TradingView setting | EA input | Default | What it does |
|---|---|---|---|
| Stop For The Month Once It Is Up ($) + amount box | `InpMLockOn`, `InpMLockAmt` | off, 150 | Once this month's closed profit reaches the amount, no new trades until the 1st of next month |
| Lock Profit Once The Month Is Up ($) · Lock % (two boxes) | `InpPLockOn`, `InpPLockAt`, `InpPLockPct` | off, 500, 20 | Once this month's closed profit reaches the amount, the lock % of the month's highest closed profit is locked; if the month's profit falls back to that level, no new trades until the 1st |
| Restart The Loss Recovery On The 1st Of Each Month | `InpMRestart` | off | On the 1st the loss recovery starts again from the base risk |

- **Profit lock example:** amount $500, lock 20%. The month reaches +$500, so $100 is locked. It climbs to +$650, so $130 is locked (the locked level
  only rises). It falls back to +$129, so it stops until the 1st. It is checked when a trade closes, so one big losing trade can end below the
  locked level. A lock % of 100 stops at the first trade that closes below the month's high.
- **Stop for the month** = the gold study's "Monthly lock +$X" column (`Research/deliverables/Gold_No_Losing_Month.xlsx`). The study also restarted
  the loss recovery every month: switch both on to trade a setting from that workbook. The profit lock was not part of the study.
- **Restart** forgets the loss to win back, the losing runs, the Labouchere list, Rule C's carried losses and the Crooks C rule state, including a
  skip pause, like the hard cap's "Start again". If a trade or entry order of the old month is still open, the restart happens right after it closes.
- **Already open:** a trade or entry order that is already open runs to its exit; the locks only stop new trades. Skipped signals show
  "monthly lock". The status reads "MONTHLY LOCK (until the 1st)". With a lock on, the DAY P&L row also shows the month (and the locked level).
- **How a trade counts:** TradingView uses its closed profit (commission included). The EA counts a trade when it has fully closed: its deals,
  commission, swap and fees. The EA counts only its own trades (this symbol and magic number). After the EA or MT5 restarts in the middle of a month,
  the EA rebuilds this month's profit, its high and the locks from the deal history.

Checks:
- **TradingView:** assembled with the shared blocks unchanged. Inline lint 0, both files parse. Six new inputs; every other input is unchanged.
- **EA:** compiles with 0 errors and 0 warnings. The EA's own code passed scripted sequences:
  - stop at +$150;
  - the profit-lock example above;
  - the restart with Crooks C (owed $20 forgotten on the 1st, or kept with the restart off);
  - a trade closed by the EA counting in its month.
- **Unchanged with the locks off (0 differences):** engine parity, 51 configurations across 3 data shifts; money-management parity, 1,680 / 3,360 /
  5,184 runs; the v4.1 hedge sequences.
- **Independent review:** no findings in the strategy. In the EA it found 5 points, all fixed:
  - a trade closed by the engine's exit was missed;
  - a summer-time hour was missing in the history rebuild;
  - the month at start-up;
  - an open trade's entry commission was counted early;
  - a lock % below 1 was accepted.

**Loading v4.2:** remove the strategy from the chart and add it again, or use Settings -> Defaults -> Reset settings. Then switch the locks on in
MONTHLY PROFIT LOCK. In MT5, compile the new EA and reset its inputs. Nothing changes until a lock is switched on.

### EA v4.3: restart memory (EA only, automatic)

When MT5 or the EA restarts, the EA now continues where it left off. A restart means closing MT5, a reboot, a power cut, a crash, or removing
and re-adding the EA. Closing the laptop lid (sleep) was never a problem: MT5 keeps running in memory and the EA catches up when it reconnects.
Changing inputs or the timeframe also kept the EA's memory before (MT5 keeps it then). The TradingView strategy needs nothing: it recalculates
every trade from the chart history each time it loads.

**Setting:** **Continue after a restart** (`InpRemember`, group RESTART MEMORY), **on** by default.

**What is kept:**
- **Loss recovery:** the amount to win back, the losing / winning trades in a row, the Labouchere list, Rule C's carried losses, and the state
  of every other rule. Total profit is kept too (the Step-up rule's size comes from it).
- **Crooks C:** the loss to win back, the cycle, the wait for a win, and the Crooks C rule state (losing recoveries in a row, the wait or skip
  pause and its days left, the hedge pair on the next signal).
- **Streaks and pauses:** the day's P&L, the streak stop, the pause days left, the hard-cap stop.
- **Monthly profit lock:** the month's profit, its high, the lock, and a monthly restart that is still waiting.
- **The open trade or entry order:**
  - whether it is a recovery trade, its risk, and what it has booked so far (partial closes);
  - the Crooks TP1-rule levels, and the hedge pair;
  - which broker deals were already counted.

**How it is saved:** in MT5 global variables (Tools -> Global Variables, F3), names starting `ARS|<symbol>|<magic number>|`. They are written
only when a value changes and flushed to disk at once, so a crash or power cut loses nothing.

**What happens on a restart:**
1. The EA replays the chart as before and loads the saved state.
2. It counts the days that passed: the streak pause, the Crooks C skip days, and a new month (the locks start again; the monthly restart
   waits for a trade still open).
3. It waits until MT5 is connected to the trade server (positions and deals are not visible before), so a trade that is still open is never
   booked as closed.
4. It books every deal the broker made while it was off, through the same code as after an internet disconnect. That covers a stop loss or
   take profit that closed the trade, and an entry order that filled.
5. It adopts a trade that is still open, and re-places a setup that is still waiting. A trade that runs on after the engine's exit (the
   Crooks TP1 rule's rest, earn-back) or an order that filled just before the engine's fill bar is kept.
6. If a force-close time, a weekend start or a news start passed while it was off, a trade still open is closed now (as after a disconnect).

The Journal prints `Restart memory: continued from <time> | loss to win back ...`, and the table shows `RESTART MEMORY | on | continued from
<time>`.

**Notes:**
- **Starting fresh:** switch the setting off (the saved state is deleted), then on again.
- **One saved state per symbol and magic number on this MT5.** A state saved by another account is not loaded. Use a different magic number
  for each EA on the same symbol.
- **MT5 deletes global variables that are not used for 4 weeks.** The EA rewrites every value once a day while it runs, so the memory is
  lost only after MT5 has been off for 4 weeks.
- **The Strategy Tester ignores it.** Every test starts fresh.
- **A hard-cap Stop stays in force after a restart.** Change any input to trade again (as before); it also ends when the cap is switched
  off or no longer set to Stop.
- **Changing inputs** now also keeps the open trade's bookkeeping (e.g. a Crooks TP1-rule trade). It was wiped before.
- **Also fixed:** after a disconnect or restart that spans several days, each missed day now counts for the streak pause (before: only one).
  The Labouchere list is now kept when inputs change, like the other rules (it was reset).
- **Limits** (the same as after a disconnect):
  - a trade that closed while the EA was off counts from the moment the EA books it at the restart (e.g. a pause it starts begins then);
  - EA-only partial closes whose level the price reached while the EA was off are not done afterwards.
- **Starting fresh** (v4.4): use **Start fresh once** (below). Switching the setting off and on does not clear the values MT5 keeps in
  memory while the EA stays on the chart.

### EA v4.4: no early closes; trades closed outside the EA are booked right; VWAP line on the chart (EA only)

**The report (11 Nov 2026, new broker, `GOLD.i#`):** three trades closed at +$4.86, +$4.97 and +$6.48 a few minutes after entry, instead of
reaching TP1 (0.6R). Two of them had no take profit at the broker.

**What v4.3 did, and why trades could close early:**
- **No take profit until the next candle close.** v4.3 sent only the stop loss with the order. The take profit followed when the engine
  confirmed the fill at the next 5-minute candle close. Until then the trade had no target at the broker, and if the EA was off it had none
  at all.
- **"Engine wins".** At every candle close v4.3 closed any trade the engine was not in, at whatever the price was. The engine is
  recalculated when the chart's timeframe is switched (for example to M1 to look closer), when an input is changed, or when the EA is
  re-attached. It may then no longer hold the trade, which was closed at the next candle.
  In a broker simulation on 3 months of gold ticks:
  - frequent timeframe switches closed 48 trades this way, at +$8.69 on average;
  - input changes closed 9 trades, at +$6.76 on average.
  Running alone with no switches, v4.3 closed no trade early.
- **Closes outside the EA were booked as $0 losses.** A trade closed by hand, from the phone app, or by another EA (for example a trade
  manager) has a closing deal with another magic number. v4.3 did not count that deal, so it booked a winning trade as a $0 loss. The loss
  recovery then went wrong: in the simulation 25 of 99 bookings were wrong, and Crooks C skipped the recovery trade after a win.
- **The screenshot fits these causes:**
  - trade 2 closed in the middle of a 5-minute candle (09:17:11), and v4.3 can close mid-candle on M5 only through the Crooks TP1 rule or
    a restart;
  - all three closed after only a small move in their favour.
  Without the Experts / Journal log of that day the exact cause cannot be proven. v4.4 writes it down for every trade.

**What v4.4 changes:**
- **The take profit goes to the broker with the order.** Every trade has its stop loss and take profit from the moment it opens, including
  while the EA or MT5 is off. The TradingView strategy still sets its target one candle after the fill, like the indicator's statistics. So
  when the target is reached inside the entry candle, the EA takes TP1 there, while TradingView goes on to the next candles. Either side can
  come out ahead: in two test periods of gold ticks (Aug - Oct 2026 and Sep 2025 - Jan 2026) the difference was +$106 and -$182.
- **A trade of this EA is never closed early.** A trade the engine stops following runs to its own stop loss and take profit. This covers:
  - a fill a moment before the engine's, when the spread narrowed;
  - a setup that ended;
  - new inputs, another timeframe, or a re-attach;
  - an order that filled while it was being cancelled.
  The EA closes a trade itself only:
  - at the engine's stop on the bid chart, as before;
  - at the engine's final target when earn-back is off;
  - at the force-close time, the weekend start or a news start (your settings);
  - for the Crooks TP1 rule's part;
  - for a hedge pair with only one trade open.
- **Closes outside the EA are booked with their real profit**, and the loss recovery goes on from them. The same applies to a trade closed
  while the EA was off.
- **Who closed each trade.** The Experts tab prints one line per close, and the table shows the last close (red if it was outside the EA):
  `Trade #990361292 closed: 0.06 lots at 4048.70 | trade P&L +4.86 (costs included) | closed by ...`.
  The end of the line is one of: its take profit, its stop loss, this EA (with the reason), HAND (MetaTrader on the computer / the phone app
  / the web terminal), ANOTHER EA OR SCRIPT (magic N), an EA with this magic number (a second copy?), or a margin stop-out. Every close the
  EA makes is also printed first: `Closing #... : <reason>`.
- **The EA trades the timeframe it was attached to.** If you switch the chart to another timeframe to look at the candles, it opens no new
  trades until the chart is back (an alert says so, and the table shows `CHART ON M1: NO NEW TRADES`). The open trade keeps its stop loss and
  take profit: the other timeframe's engine never takes it over, and it is linked to its setup again when the chart is back. To trade
  another timeframe, remove the EA and attach it again on that timeframe. To look at other timeframes, open a second chart.
- **One copy per symbol and magic number.** A second copy with the same symbol and magic number does not start (alert). Two copies cancel
  and close each other's trades and share one restart memory. Another EA on the account is listed in the Experts tab at start.
- **Broker server clock: Auto (new default).** The EA reads the broker's GMT offset from MT5 (server time minus GMT) and picks the EU or US
  summer-time rule, or that fixed offset. A new broker no longer needs the clock set by hand. With any other choice, an alert appears when
  the broker's clock differs from it, because your days, hours, kill zones, news and force-close times would be off. The table row `BROKER
  CLOCK` shows the offset in use. In the Strategy Tester Auto means the EU rule, as before.
- **VWAP line on the chart** (new, on by default). The EA draws the VWAP it trades on: the same anchor (session / week / month), source and
  tick volume as its signals. It looks like the TradingView indicator's VWAP (#4DD0E1, width 2, over the candles, a jump at each new
  session). The DISPLAY inputs are **Show the VWAP line** (on), its colour, its width, and how many candles of VWAP are drawn (1,500; older
  parts are removed as new candles come, also after a disconnect). The line shows as soon as the EA is attached, also with the market
  closed. It is drawn on the chart and in the Strategy Tester's visual mode, and removed with the EA. Switch it off with **Show the VWAP
  line = false**.
- **Start fresh once** (`InpMemFresh`, restart memory group): forgets the loss recovery, streaks and pauses once. Set it to true and click
  OK; set it back to false later. Use it if trades closed outside v4.3 were booked as losses.
- **Restart memory:** the open trade's setup (its signal candle and entry level) is saved. After a restart, new inputs or a timeframe
  switch, the trade is re-linked to the engine only when it is the same setup; otherwise it keeps its own levels. Before, the engine's other
  setup's stop and target could be applied to it. A state saved by v4.3 loads unchanged.
- **Also fixed:**
  - After a restart, new inputs or a timeframe switch, v4.3 could place a signal it had already traded a second time, when the engine still
    showed that setup armed. v4.4 saves the last signal it placed and never places it again. An order that was still waiting when the EA
    stopped is placed again, as before.
  - A buy or sell limit's take profit is checked against the order's own price, as MT5 does. A market entry is skipped when the price is
    already past its target.
  - After a restart, the engine's fill, stop moves and exit that happened while the EA was off now reach the open trade, as after a
    disconnect. A trade whose engine stop (for example moved to break-even) was hit while the EA was off is closed at the restart. Before, it
    kept its original stop. This also works when MT5 starts before it is connected.
  - A close that MT5 refuses (off quotes, trading disabled, market closed) is tried again at every candle close. This covers the engine's
    exit, the force-close, the weekend and news closes, and closes at a restart.
  - The EA's own partial closes are logged as its own (`partly closed ... partial close at TP1`). Every position the EA closes gets its own
    `Closing #...` line, both trades of a hedge pair included.
  - After a restart, a new trade placed on the first tick could be closed at the next candle by an engine exit that belonged to the old,
    already closed trade. The events from the time the EA was off now apply only to the trade they belong to (also the Crooks TP1-rule
    catch-up).
  - Every setup the EA decided on (taken, or skipped by news, a pause, a streak stop or being in a trade) is remembered, so a restart never
    takes a setup the live run did not. Setups seen while the chart shows another timeframe are not counted, so the real one is placed
    when the chart is back.
  - A trade whose position is gone is booked with its closing deal. If that deal is not in the history yet, the booking waits one candle
    instead of booking the trade without its profit.
  - A close by the EA just before a restart is still reported as the EA's after the restart.
  - With **Continue after a restart** off: a trade that closed in the seconds before new inputs or a timeframe switch was not counted in
    the loss recovery (MT5 keeps the recovery in memory, but the new start skipped that deal). It is now booked first. A restart of MT5 or
    of the EA still starts fresh, as that setting says.
- **Netting accounts** (one position per symbol): a close by hand, from the phone or by another EA is booked while the EA holds a trade.
  Do not run another EA on the same symbol of a netting account: the position is shared, so the trades cannot be told apart.

**How it was tested** (`Research/scratchpad/sim/`, results in `sim/results.txt`):
- **Broker simulator.** v4.3 and v4.4 run on an MT5-like broker: hedging account, limit and stop orders, stops level, stop loss and take
  profit at the tick, deals with reason, magic number and position id, and commission. Ticks come from FxPro gold M1 bars, 3 Aug - 2 Oct
  2026 and 15 Sep 2025 - 20 Jan 2026 (across the clock change), with varying spreads.
  - **17 scenarios:**
    - restarts with the EA off;
    - new inputs and timeframe switches;
    - hand and other-EA closes;
    - stops level and commission;
    - market entries and stop moves with restarts;
    - MT5 starting before it connects;
    - all of them combined.
  - **16 more runs** cover the Crooks TP1 rule, the hedge rule, partial closes and market entries, alone and with restarts or switches.
  - **4 runs with Continue after a restart off** cover timeframe switches, new inputs, restarts and all of them combined.
- **Over the 17 scenarios:**

  |                                         | v4.3  | v4.4  |
  |-----------------------------------------|-------|-------|
  | Trades                                  | 1,659 | 1,571 |
  | Opened without a take profit            | 1,659 | 0     |
  | Closed early by "engine wins"           | 67    | 0     |
  | Booked wrong                            | 81    | 0     |
  | Same signal traded twice                | 3     | 0     |
  | Opened while the chart showed M1        | 87    | 0     |
- **v4.4 on all 37 runs (3,767 trades):**
  - 0 early closes, 0 signals traded twice, 0 rejected orders, 0 failed starts;
  - a take profit on every order;
  - every trade booked once, with the broker's profit (a hedge pair as one booking). The only exceptions are 2 trades that closed while
    the EA was off with Continue after a restart off: that setting forgets them on purpose;
  - an open trade is never taken over by the engine of another timeframe;
  - the only closes by the EA were its rules: the engine's stop, a stop the price had already passed after a move, and a news start;
  - restarts and same-input re-initialisations give the same trades as no restart (a sell's take profit can move by the live spread when it
    is re-sent);
  - the copy lock and the clock detection work (GMT+3 / +2 / 0 / +5.5 / -4);
  - the VWAP line: 1,500 candles with no gaps after restarts, disconnects, timeframe switches and new inputs, its last point equal to the
    VWAP the EA trades on.
- **Two independent code reviews** (Opus, high effort; the second on the fixes of the first). Every finding was checked against the code
  first, the serious ones were reproduced in the simulator, and all were fixed.
- **Compile check:** 0 errors, 0 warnings.
- **Parity suites on the final file** (`Research/scratchpad/v40/final_v44.txt`): the money management matches its reference with 0
  mismatches, both normally and with a restart after every step. That covers 2.15 million loss-recovery trades, 3.87 million TP1-rule
  trades and 7.4 million Crooks C signals. The scripted hedge and month tests are identical to v4.3, and the engine is identical in all four
  runs (three date shifts).

**Upgrading from v4.3:**
1. Replace the file and compile it in MetaEditor (F7).
2. Inputs: MT5 keeps your chart's input values, so new defaults do not apply by themselves.
   - Set **Broker server clock** to **Auto**.
   - On a broker without commission, set **Commission per lot** to 0. It is used for the lot size and the earn-back target.
3. The saved loss recovery and streaks continue. If trades closed outside v4.3 were counted as losses, use **Start fresh once**.
4. Run one copy per symbol and magic number. Remove an old copy from other charts.

**What to look at on the chart:** the Experts tab shows who closed each trade. If it says HAND or ANOTHER EA OR SCRIPT, look for another EA
or trade manager on the account, a second MT5 or VPS logged in to the same account, or the phone app. If it says this EA, the reason is
printed with it.

### v4.5: Crooks E - J: loss recovery that loses less in a long losing run (strategy and EA)

Six new choices in **Loss Recovery**. Each is Crooks C with one change, and every Crooks C setting also works with them: win the loss back
over N wins, the rule after N losing recovery trades (and the hedge rule in the EA), the Crooks TP1 rule, and the hard cap.

- **Crooks E (your rule).** As in Crooks C, after a loss the EA waits for a win, and the trade right after the win is the recovery trade.
  While it waits, every trade is **0.01 lot** whatever the stop, or the normal size if that is smaller. If the recovery trade loses, the
  trades go back to 0.01 lot until the next win. For example, on the broker simulator with a $50 base:
  1. a 0.06-lot trade lost $42.54;
  2. the next trade was 0.01 lot and lost $13.87;
  3. the next was 0.01 lot and won $3.39;
  4. the recovery trade (0.13 lot) won $57.20, so everything was back;
  5. the trades after that were the normal size again.
- **Five more rules**, each with a limit on the recovery trade so that it cannot keep growing:

  | Rule | What it does | Setting (default) |
  |---|---|---|
  | **Crooks F** | A recovery trade risks at most K x base. If the loss is bigger, the rest is won back after the next wins. | K = 3 ($150 at a $50 base) |
  | **Crooks G** | The loss to win back is never more than X x base; anything above is accepted as lost. | X = 10 ($500) |
  | **Crooks H** | A recovery trade risks at most this % of the equity. | 1% |
  | **Crooks I** | Crooks E (0.01 lot while waiting) plus the Crooks F limit. | 0.01 lot, K = 3 |
  | **Crooks J** | The deeper the drawdown of the closed profit, the smaller the recovery trade: x (1 - drawdown / (X x base)), never below the base. | X = 20 (half size at a $500 drawdown, base at $1,000) |

  The limits of F, H and I count the real stop-out loss, so they also hold with the Crooks TP1 rule's wider stop.
- **Settings:**
  - EA: `InpCrkELot` (E / I), `InpCrkFK` (F / I), `InpCrkGX`, `InpCrkHPct` and `InpCrkJX`.
  - Strategy: the same five settings in the LOSS RECOVERY group.
  - Existing input titles did not change, so TradingView and MT5 keep your saved settings.

**Gold 2021-2026** (`Research/scratchpad/gold/crooks_e1.py`, `crooks_e2.py`):
- 19 profitable strategies, $50 base, $10,000 start, no hard cap.
- "Shuffled" means the same trades in 200 random orders per strategy (3,800 runs per rule). "Blown" means the account went to zero.

| Rule | Profit, 19 strategies | Average / worst drawdown | Worst losing run (average) | Blown, shuffled | Drawdown in the worst 5% of shuffles |
|---|---|---|---|---|---|
| Crooks C | +$225k | 40% / 92% | $2,086 | 20.0% | 115% |
| **Crooks E** | +$145k | 28% / 59% | $1,152 | 15.8% | 110% |
| **Crooks F** | +$130k | 21% / 40% | $709 | 0% | 32% |
| **Crooks G** | +$115k | 15% / 29% | $687 | 0% | 29% |
| **Crooks H** | +$123k | 16% / 29% | $702 | 0% | 26% |
| **Crooks I** | +$89k | 20% / 36% | $381 | 0% | 37% |
| **Crooks J** | +$95k | 13% / 21% | $696 | 0% | 20% |
| Off ($50 every trade) | +$91k | 11% / 18% | $679 | 0% | 18% |

What the table shows:
- **Crooks E alone** cuts the losses while waiting (its losing runs are about half of Crooks C's). But the recovery trade can still keep
  growing, and in shuffled orders it still blew the account 16% of the time. If you want the 0.01-lot idea with protection, use **Crooks I**.
- **F, G, H, I and J never blew an account** in any shuffled order. They keep 40-58% of Crooks C's profit with half its drawdown or less:
  - **J** has the smallest drawdown;
  - **I** has the smallest losing runs;
  - **F** keeps the most profit.
- Rejected after testing:
  - halving the next recovery after a lost one;
  - waiting for 2 wins in a row before the recovery;
  - shrinking every trade (not only the recovery) in a drawdown;
  - recovering only from profit already made.

  They lost more, or blew accounts.

**How it was tested:**
- **EA money management against the Python reference** (`gold/recovery.py`, `gold/crooks_tp1.py`), trade by trade:
  - every rule: 2,928 runs, 4.07 million trades;
  - with the Crooks C rule after N losing recoveries: 10,944 runs, 16.5 million signals;
  - with the Crooks TP1 rule: 12,684 runs, 18.7 million trades.

  All showed 0 differences, also with a restart after every step (`Research/scratchpad/v40/final_v45.txt`). The 22 older rules give exactly
  the same results as before.
- **Broker simulator** (3 months of gold ticks), each new rule run plainly and with restarts, new inputs and timeframe switches:
  - every trade was booked with its broker profit, with no rejected order;
  - in E and I, every waiting trade was exactly 0.01 lot, and the recovery trade came right after each win;
  - the 37-run suite of v4.4 gives identical results.
- **Compile check:** 0 errors, 0 warnings.
- **Strategy:** 0 inline-title warnings, the Pine parse passes, and the shared engine blocks are byte-identical with the indicator.

### v4.6: Profit ladder: more risk after a first profit, paid only from that profit (strategy and EA, Crooks F - J)

New settings in LOSS RECOVERY:
- **Profit Ladder (Crooks F-J): Risk Appetite** (Off, Low, Medium, High, Extra high, Max). EA: `InpLadder`.
- **Profit target before the risk goes up** ($1,000). EA: `InpLadT`.

The ladder works with Crooks F, G, H, I and J; with any other rule it stays off. How it works:
1. **Until your closed profit first reaches the target**, the rule trades exactly as without the ladder.
2. **Then part of your best profit is locked.** Low keeps 80% of it, Max keeps 40%. The profit above the lock is the **cushion**.
3. **The trades grow with the cushion.** The base risk becomes the base plus a share of the cushion, up to 2x the base at Low and 12x at
   Max. The rule's recovery trade and limits then work with that bigger base.
4. **The extra risk is paid only from the cushion.** A trade never risks less than the plain rule, and never more than the plain rule plus
   a share of the cushion. If losses use up the cushion, the trades are back to the plain rule.
5. **If the profit falls back to the start**, every trade is the 0.01 lot (`InpCrkELot`) until it is in profit again.

| Level | Keeps of the best profit | Base grows up to | Share of the cushion added to the base | Most extra loss per trade |
|---|---|---|---|---|
| Low | 80% | 2x | 10% | 25% of the cushion |
| Medium | 70% | 3x | 15% | 30% |
| High | 60% | 5x | 20% | 35% |
| Extra high | 50% | 8x | 25% | 40% |
| Max | 40% | 12x | 30% | 50% |

The table on the chart shows the ladder: the best profit so far against the target, then the lock, the cushion and the base in use, or "back
at the start".

**Gold 2021-2026** (`Research/scratchpad/gold/crooks_ladder3.py`): 19 profitable strategies, $50 base, $10,000 start, the 1:100 leverage
limit, the 0.01-lot minimum and a $1,000 target. Each cell is the profit of the 19 strategies, then the average / worst drawdown:

| Rule | No ladder | Low | Medium | High | Extra high | Max |
|---|---|---|---|---|---|---|
| Crooks F | +$134k, 21% / 40% | +$144k, 19% / 40% | +$181k, 20% / 40% | +$242k, 24% / 40% | +$256k, 26% / 46% | +$291k, 29% / 48% |
| Crooks G | +$119k, 15% / 29% | +$107k, 16% / 29% | +$144k, 17% / 29% | +$185k, 20% / 29% | +$231k, 23% / 36% | +$271k, 25% / 43% |
| Crooks H | +$127k, 16% / 29% | +$127k, 15% / 29% | +$158k, 17% / 29% | +$173k, 19% / 33% | +$213k, 22% / 36% | +$247k, 26% / 48% |
| Crooks I | +$92k, 20% / 36% | +$100k, 19% / 36% | +$129k, 21% / 36% | +$155k, 22% / 37% | +$198k, 24% / 38% | +$269k, 27% / 48% |
| Crooks J | +$99k, 13% / 21% | +$94k, 14% / 21% | +$115k, 15% / 21% | +$141k, 17% / 24% | +$194k, 20% / 32% | +$268k, 23% / 43% |

What the results show:
- **Never blown.** No account blew in any of the 3,800 shuffled orders (200 per strategy) for any rule and level, nor in the real order.
- **After the first $1,000, the dips below the start are much smaller.** In the worst 5% of shuffles, the lowest profit was:
  - without the ladder: -$417 (J) to -$2,008 (I);
  - with the ladder: -$191 (J, Low) to -$603 (I, Max).
- **What cannot be promised is "never below the start".** Even without any ladder, after first reaching +$1,000 the rules fell back below
  the start in 18-33% of the shuffles: a normal losing run at a $50 base is bigger than $1,000.
- **A strict lock** was tested first: the trades shrink to keep the locked profit. It cut the profit in half and still went below the start
  through the 0.01-lot trades. The ladder keeps such dips small instead.
- **Why a $1,000 target:** with $500 the results were lower and did not rise steadily from Low to Max. A $500 profit is gone in a normal
  losing run, so the 0.01-lot guard acted too often.
- The no-ladder numbers here use the 0.01-lot minimum and the leverage limit, so they differ a little from the v4.5 table.

**How it was tested:**
- **Reference:** `gold/recovery.py` and `gold/crooks_tp1.py` give the same results as the study with the ladder. With the ladder off they
  are identical to v4.5.
- **EA money management against the reference** (every level, targets $500 and $1,000), with 0 differences:
  - every rule: 7,728 runs, 11.4 million trades;
  - with the Crooks C rules: 20,544 runs, 31.3 million signals;
  - with the Crooks TP1 rule: 22,484 runs, 34 million trades.

  The same three suites again with a restart (the state saved and reloaded) before every trade: 0 differences. The engine parity is
  identical too. Results: `Research/scratchpad/v40/final_v46.txt`.
- **Broker simulator:**
  - 14 runs with the ladder (Medium and Max, targets $100 / $300 / $1,000, restarts, new inputs, the TP1 rule): every trade was booked
    with its broker profit, with no rejected order;
  - with Medium and $1,000, the trades were about 3x bigger after the target (0.053 -> 0.157 lot on average);
  - back at the start, every trade was exactly 0.01 lot;
  - with the ladder off, the 37-run suite is identical to v4.5.
- **Checks:**
  - compile check: 0 errors, 0 warnings;
  - strategy: 0 inline-title warnings, the parse passes, only the two new inputs were added and no existing title changed (saved settings
    are kept).

### v4.7: Position size: fixed $ risk, fixed lots or % of equity (strategy and EA)

RISK AND POSITION SIZE has a new **Position Size**:
- **Fixed $ risk (default):** the same as before.
- **Fixed lots:** for example 0.01 lot.
- **% of equity at risk:** the base trade loses this % of the equity at its stop.

| Position Size | The base trade | Its input (default) |
|---|---|---|
| Fixed $ risk | loses the Base Risk at its stop (commission and spread included) | Base Risk Per Trade ($): 50 |
| Fixed lots | is the Base Lots, whatever its stop | Base Lots (Fixed lots): 0.01 |
| % of equity at risk | loses this % of the equity at its stop | Risk % Of Equity: 1 (moved here from Loss Recovery; the "% of equity" rule uses it too) |

- **How the loss recovery rule uses it:** the rule sizes every trade from the base trade. The default Crooks C sizes the recovery trades
  bigger. For exactly 0.01 lot on every trade, set Loss Recovery to Off.
- **Fixed lots in $:** a fixed lot risks lots x units per lot x (stop distance x point value + costs per unit). That $ amount is the base
  for the recovery rule, the hard cap's "start again" and the profit ladder.
- **Still applied:** lot step, rounding, leverage and the hard cap.
- **Unchanged in the default mode:** with Fixed $ risk every number is the same as in v4.6.
- **The EA (v4.7):** RISK AND POSITION SIZE has the same three choices: `InpSizeMode` (Position size), `InpBaseRisk`, `InpBaseLots`, and
  `InpEqPct` (moved up from the loss recovery group, same name, so saved settings keep it).
  - **Fixed lots in $:** lots x ((stop distance + spread) / tick size x tick value + commission per lot), the same formula as the EA's lot size.
  - **% of equity:** the account equity at the setup.
  - **The base is remembered:** the base a trade was sized with is kept for its booking (Oscar's Grind, Crooks G) and in the restart
    memory.
  - **Bad inputs stop the start:** a base of 0 or less is refused when the EA starts.
  - **No overflow:** Oscar's Grind's unit count can no longer overflow on an almost empty account.
- **Small fixes:**
  - A size that cannot be worked out (for example % of equity on an empty account) is skipped as "size 0".
  - A function parameter that had the same name as a variable was renamed.
- **Checks:**
  - **Strategy:** the shared blocks are byte-identical with the indicator. 0 inline-title warnings, 0 shadowed names, no
    `barstate.islast`, and the file parses.
  - **EA compile:** 0 errors and 0 warnings (offline MQL5 check). The source is ASCII.
  - **EA money, new modes:** its own compiled sizing and booking against `gold/recovery.py` (with the same base modes). Fixed lots
    0.01 / 0.05 and 0.5 / 1 / 2 % of equity, every recovery rule, caps, Crooks C over 1 / 2 wins, the ladder: 10,800 runs, 10,188,179
    trades, 0 differences.
  - **EA restart memory:** the same check with a full save, fresh start and reload every 3rd step: 10,800 runs, 1,924,348 trades,
    0 differences.
  - **EA regression:** Fixed $ risk against the reference, 7,728 runs, 11,449,048 trades, 0 differences.
    - The Crooks TP1 rule: 34,075,795 trades, 0 differences.
    - The Crooks C rule after N losses: 31,277,261 signals, 0 differences.
    - The full EA engine against the Python reference on every test symbol: all trades identical.

### v4.8: strategy presets, "Add My Filters" and a wider monthly restart (indicator, strategy and EA)

**STRATEGY PRESET** is now the first setting. **Custom** (the default) uses your settings below, exactly as before. Each of the other 25 choices is one tested catalogue strategy (gold, FxPro, 4 Jan 2021 – 2 Oct 2026).

**What a preset sets**
- Every signal setting, exactly as tested: stop, targets and final exit (TP4), entry price, all filters, VWAP anchor, max fills and cooldown.
- Its own hours or kill zone.
- In the strategy and the EA: the 70% partial close at TP1 of M15-S2, S4 and S5 and H1-S2, S4 and S5.
- Your own values stay saved, and Custom brings them back.

**Only on its own chart.** A preset trades only on its own chart timeframe (the M1, M5, M15 or H1 in its name). On another chart:
- there are no signals and no trades;
- the table says WRONG CHART;
- the EA also prints a message and raises an alert.

**Always your own settings, with any preset:**
- force-close and the Saturday close;
- spread, commission and earn-back;
- risk, loss recovery and the monthly settings;
- display and alerts.

**Add My Filters** (right under the preset, off by default)
- **Off:** the preset trades exactly as tested. It uses only its own hours or kill zone:
  - M5: 18:30–22:30 IST;
  - M1: the London Close kill zone, 19:30–21:30 IST;
  - M15-S9: the Asia kill zone, 05:30–09:30 IST;
  - all others: all day.

  Your days, hours, kill zones and news windows are not used.
- **On:** your own filters apply, each as you have it switched on or off.
  - Your days and news windows are added on top of the preset.
  - Your hours or kill zones replace the preset's own hours once either is switched on. With both off, the preset keeps its own hours.
  - Examples with M5-S3:
    - Tue/Wed/Thu only: tick the days, and switch your hours and kill zones off. M5-S3 then trades 18:30–22:30 on those days.
    - Your kill zones: M5-S3 trades in Asia, London and New York instead.
    - A window of your own (e.g. 19:00–21:00): switch on your hours with that window.
  - A preset with your filters is no longer the tested strategy.

**Times**
- A preset's own hours are Indian times, whatever your time zone setting.
- Its kill zones use the fixed IST times, as tested (they do not move with summer time).
- The daily news window keeps New York time. It is 17:45–18:15 IST in US summer time and 18:45–19:15 IST in US winter time.
- So for the M5 presets (from 18:30) the news window matters only in US winter time.

**VWAP Month presets need the whole month on the chart.** These are every M1 and M5 preset, and H1-S2 and S4 to S8.
- **TradingView:** it computes the VWAP from the first loaded candle.
  - A 1-minute chart usually loads only 2–3 weeks (at most 20,000 candles), so in the first loaded month the VWAP, and with it the signals, differ from the tested ones. From the next month on they are right.
  - A 5-minute chart needs about 6,500 candles for a month.
- **The EA:** since v4.8 its warm-up reads back to the 1st of the month (the Monday for the Week VWAP), up to 100,000 bars. If the broker's history is shorter, it says so in the log.

**Tested results of the 25 presets** (fixed risk; R after the spread in the data, before commission; final exit TP4):

| Preset | Goal | Chart | Main settings (on top of the v3 defaults) | Own hours | Trades | Win % | R per trade | Total R | Longest losing streak |
|---|---|---|---|---|---|---|---|---|---|
| M1-S1 | Most profit | M1 | stop 4 ATR, cooldown 8, VWAP month | London Close kill zone | 1,958 | 36.6 | +0.057 | +112 | 14 |
| M1-S2 | Shortest losing streak | M1 | stop 4 ATR, cooldown 30, VWAP month | London Close kill zone | 1,802 | 36.5 | +0.052 | +93 | 12 |
| M1-S3 | Most trades a day | M1 | stop 4 ATR, displacement 0.4 ATR, VWAP month | London Close kill zone | 2,111 | 36.1 | +0.044 | +93 | 14 |
| M1-S4 | Simplest | M1 | stop 4 ATR, VWAP month | London Close kill zone | 2,006 | 36.1 | +0.041 | +83 | 14 |
| M5-S1 | Most profit | M5 | stop 2.4 ATR, TP4 2.5R, market entry, VWAP month, choppy max 8 | 18:30-22:30 IST | 1,472 | 32.1 | +0.087 | +128 | 21 |
| M5-S2 | Shortest losing streak | M5 | stop 2.4 ATR, market entry, VWAP month, choppy max 8, TP2 → stop +0.6R | 18:30-22:30 IST | 1,692 | 17.3 | +0.045 | +76 | 9 |
| M5-S3 | Most trades a day | M5 | stop 2.4 ATR, momentum 5 bars, market entry, VWAP month, choppy max 8 | 18:30-22:30 IST | 1,805 | 36.9 | +0.072 | +130 | 13 |
| M5-S4 | Simplest | M5 | market entry, VWAP month, choppy max 8, 1h EMA 1.4 | 18:30-22:30 IST | 1,488 | 36.8 | +0.058 | +86 | 20 |
| M15-S1 | Most profit | M15 | stop 4 ATR, half stop 1.2, TP3 → stop +1R | all day | 1,388 | 25.1 | +0.134 | +186 | 17 |
| M15-S2 | Shortest losing streak | M15 | stop 4 ATR, half stop 1.2, CMO 30, 1h EMA 1.2, TP3 → stop +1R, 70% closed at TP1 | all day | 1,137 | 26.5 | +0.066 | +76 | 5 |
| M15-S3 | Shortest losing streak, no partial close | M15 | stop 4 ATR, half stop 1.2, VWAP slope 0, 1h EMA 1.2, TP3 → stop +1R | all day | 1,129 | 25.1 | +0.132 | +149 | 8 |
| M15-S4 | Longest winning streak | M15 | stop 4 ATR, half stop 1.2, choppy max 16, TP3 → stop +1R, 70% closed at TP1 | all day | 1,207 | 25.4 | +0.070 | +85 | 6 |
| M15-S5 | Highest win rate | M15 | stop 4 ATR, half stop 1.2, TP1 0.5R, TP3 → stop +1R, 70% closed at TP1 | all day | 1,388 | 25.1 | +0.055 | +77 | 5 |
| M15-S6 | Most trades a day | M15 | stop 4 ATR, half stop 1.2, TP2 → stop +0.6R, TP3 → stop +1R | all day | 1,776 | 13.6 | +0.062 | +110 | 11 |
| M15-S7 | Every year positive | M15 | stop 4 ATR, half stop 1.2, break 8 bars, TP3 → stop +1R | all day | 1,377 | 25.9 | +0.146 | +201 | 17 |
| M15-S8 | Simplest | M15 | stop 4 ATR | all day | 1,179 | 37.1 | +0.084 | +99 | 18 |
| M15-S9 | Asia session only | M15 | stop 4 ATR, half stop 1.2, entry level 8 bars, 1h EMA 1.2, TP3 → stop +1R | Asia kill zone | 712 | 23.5 | +0.051 | +36 | 21 |
| H1-S1 | Most profit | H1 | stop 2.4 ATR, cooldown 12, displacement 0.65 ATR, momentum 5 bars, don't chase 2σ | all day | 186 | 45.2 | +0.337 | +63 | 8 |
| H1-S2 | Shortest losing streak | H1 | stop 2.2 ATR, structure 20, max 1 fill a day, VWAP month, don't chase 1.25σ, 70% closed at TP1 | all day | 195 | 44.1 | +0.176 | +34 | 3 |
| H1-S3 | Shortest losing streak, no partial close | H1 | stop 2.2 ATR, body 60%, don't chase 2σ | all day | 228 | 41.7 | +0.232 | +53 | 6 |
| H1-S4 | Longest winning streak | H1 | stop 2.2 ATR, displacement 0.5 ATR, momentum 5 bars, structure 20, VWAP month, don't chase 1.25σ, 70% closed at TP1 | all day | 261 | 42.1 | +0.108 | +28 | 6 |
| H1-S5 | Highest win rate | H1 | stop 2.2 ATR, max 1 fill a day, VWAP month, don't chase 1.25σ, 70% closed at TP1 | all day | 200 | 43.0 | +0.174 | +35 | 4 |
| H1-S6 | Most trades a day | H1 | stop 2.2 ATR, TP4 3R, displacement 0.5 ATR, body 45%, structure 20, VWAP month | all day | 542 | 28.4 | +0.119 | +64 | 16 |
| H1-S7 | Smoothest | H1 | stop 2.2 ATR, structure 20, VWAP month, don't chase 1.25σ, Sunday open on | all day | 208 | 44.2 | +0.309 | +64 | 7 |
| H1-S8 | Simplest | H1 | VWAP month, don't chase 2.2σ | all day | 498 | 37.6 | +0.105 | +52 | 12 |

The S3 presets of M15 and H1 are the low-streak versions without a partial close, so the indicator shows the same trades as the strategy.

**Monthly restart** (strategy and EA, "Restart The Loss Recovery On The 1st Of Each Month")
- It now also restarts:
  - the profit ladder (the best profit and the closed profit count from the restart);
  - the Crooks J drawdown;
  - the Rule C split steps;
  - a hard-cap "Stop trading".
- So every month starts like a fresh account, as in the $1,000-a-month study.
- It still waits until no trade of the old month is open.
- The account balance itself is not reset.

**Checks**
- **Custom is unchanged:**
  - every existing input keeps its title, default and order (only two tooltips changed);
  - the EA engine parity suite (51 configurations, 10 symbols) is identical to v4.7;
  - the money suites show 0 differences: 7,728 runs / 11.4 M trades, and 20,544 runs / 31 M signals.
- **Presets in the EA:**
  - the EA with each preset matched the research engine trade for trade on 10 symbols: 25 presets × 4 variants, 35,307 trades;
  - the four variants: as tested, your time zone GMT+0, Add My Filters with your hours and kill zones, and Add My Filters with days only;
  - on the wrong chart there were no trades.
- **Presets in TradingView:** all 4,025 preset values in the indicator and the strategy were read back from the files and matched the catalogue.
- **Monthly restart:** the EA's restart against the simulator run fresh every month gave 0 differences: 1,344 runs and 1.6 M trades, also with restarts of the EA in between.
- **Compile and parse:** EA 0 errors / 0 warnings; both Pine files parse, with 0 inline-title warnings.

### v4.9: BE trigger and salvage trigger (indicator, strategy and EA)

Two new settings in **TARGETS, EXIT AND STOP MOVES**, right after "When TP3 Hits". In the EA they come right after "When TP3 hits, move stop".

| Setting | What it does | Default |
|---|---|---|
| **BE Trigger: Stop To Entry Once Up (R)** | Once a candle after the fill reaches this many R in profit, the stop moves to the entry from the next candle. The trade then ends at the target or at break-even (costs paid). | off, value **1.5** |
| **Salvage Trigger: Target To Entry Once Down (R)** | Once a candle reaches this many R against the trade, the final target moves to the entry from the next candle. If the price comes back, the trade ends at break-even (0R) instead of waiting for the full target. Must be below 1, because the stop is at 1R. | off, value **0.9** |

**The rules**
- Both are decided at the candle close, like every rule of the engine, so the indicator, the strategy and the EA show the same trades.
- Only the first of the two acts in a trade. If both levels are reached in one candle, the one nearer the candle's open came first.
- Neither acts on the fill candle.
- The salvage exit is exactly at the entry: earn-back does not push it, so the strategy and the EA leave at the same level as the engine.
- The table's BREAKEVEN row also counts the salvage exits.
- Both work on top of any preset: a preset doesn't set them, and off is as tested.
- R is the stop distance. On gold it is about 0.27% of the price on M5 and 0.52% on M15.

**Gold test, 2021–2026** (every preset without a partial close; after costs of 0.23 per oz; values chosen on 2021–23 and checked on 2024–26). Each cell is the change against both triggers off, added over the timeframe's presets:

| | BE 0.3R | BE 1.0R | BE 1.5R | Salvage 0.5R | Salvage 0.9R |
|---|---|---|---|---|---|
| M5 (4 presets), 2021–23 / 2024–26 | −241R / −64R | −54R / +80R | −21R / +25R | −170R / −79R | −33R / −25R |
| M15 (6 presets), 2021–23 / 2024–26 | −468R / −240R | −52R / −53R | **+32R / +47R** | −359R / −244R | −113R / −14R |

**What the test shows**
- **Best values for M5 and M15:** BE 1.5R, and salvage off (0.9R does the least harm). These are the default values when you switch the triggers on.
- **Where BE 1.5R helps:** strategies without a stop move of their own.
  - M15-S8: +51R → +83R in 2021–23, +44R → +91R in 2024–26.
  - M5-S1: +67R → +68R and +45R → +57R.
  - It does nothing on presets that already move their stop by then, such as M5-S2 and M15-S1.
- **Early triggers lose:** with BE at 0.3R, 63% of M5-S1's trades end at break-even, because winners usually come back to the entry before they run.
- **M1 and H1:** both are best left off.

**Checks**
- **Your settings and the presets are unchanged with both triggers off:** the EA engine parity (51 configurations), the preset parity (25 presets × 5 variants) and the money suites give 0 differences, and all existing inputs are unchanged.
- **The EA with the triggers on matches the research engine trade for trade:** Custom, Custom with a TP stop move, and M5 / M15 / H1 presets, each with BE 0.3R, salvage 0.5R, both, and BE 1.5R + salvage 0.9R, on 10 symbols.
- **The research engine** was checked against an independent implementation of these rules: 20 cases, 0 mismatches.
- **Compile and parse:** EA 0 errors / 0 warnings; both Pine files parse, with 0 inline-title warnings.

### v5.0: amounts as the profit at the final TP, Crooks K and Crooks L (strategy and EA)

Three additions to the money management. With the new setting on its default (Risk) and neither Crooks K nor L chosen, the strategy and
the EA trade exactly as v4.9.

**1. Base And Recovery Amounts Are** (strategy: RISK AND POSITION SIZE, right after Position Size; EA: "Base and recovery amounts are",
right after "Position size")

| Choice | What the Base Risk $ (or the % of equity) means |
|---|---|
| **Risk: the loss at the stop** (default) | What the base trade loses at its stop, as before. |
| **Profit: the win at the final TP** | What the base trade **wins** at the final TP (the Final Exit). The stop-out loss follows from it: risk = amount ÷ what $1 of risk wins at the final TP. Example: $50 with the final TP at 0.1R and a $2.50 gold stop → the trade risks $546 and wins $50 (v5.1 counts the spread and commission; see v5.1 below). |

With Profit, every loss-recovery rule goes for its amounts as **wins at the final TP**, whatever the stop-out loss becomes:

| Rule | With Profit |
|---|---|
| Recover all losses on the next trade | The next trade wins all the losses plus the base win. |
| Recover losses over N trades | Each trade wins 1/N of the losses plus the base win (N = 3: a third each time). |
| Recover a % of losses per trade | That % of the losses plus the base win. |
| Step-up | The base win plus the step $ per loss in a row. |
| Delayed recovery | After N losses: the base win plus the losses ÷ N. |
| Rule C / Rule C split | The carried losses ÷ split as a win (C split's growing base too). |
| % of equity (rule and Position Size) | That % of the equity as the win. |
| Oscar's Grind | A cycle ends at +1 base win. |
| Exact at final TP, Crooks A–L | Already sized to win the loss at the final TP: the same formula, on the new base. |
| Martingale, Fibonacci, D'Alembert, Labouchere, Grand Martingale, Paroli, Reverse D'Alembert | Multiples of the base trade, as before. |

- **Stay on the loss at the stop:** the hard cap, the limits of Crooks F, G, H, J and K, the profit ladder, and Crooks L's part steps.
- **Fixed lots:** the base trade stays the lots; the recovery amounts still follow the setting.
- **Partial profits:** a full win brings a little less, because the parts closed at the earlier TPs make less than the final TP.
- **Size:** a small final TP makes every trade big (0.1R → about 11× the amount on gold). The leverage limit and the broker's maximum lot can cut a
  recovery trade, and then it wins back only part of the loss. In the gold test with your M5 settings, a 0.1R final TP won 78% of the
  trades but lost money with every recovery rule.

**2. Crooks K** (Loss Recovery, after Crooks J): Crooks J while the closed profit is at or above the start, careful below it.

- **At or above the start:** exactly Crooks J, with the profit ladder if it is on.
- **Below the start:** the trade after a win uses the **careful size**; the trades after a loss use the Crooks E / I lot (0.01) until the
  next win. The ladder's 0.01-lot start guard is not used, and the Crooks TP1 rule is off below the start.
- **The start:** the closed profit since the EA started (the restart memory keeps it) or the backtest start; with the monthly restart on,
  the 1st of each month.

| Setting | Default |
|---|---|
| Careful size below the start: Lots / Fixed $ / % of base | **Lots** |
| Careful lots · $ · % of base | **0.02** lot · $25 · 50% |

The $ is the risk, or with Profit the win at the final TP. Lots are rounded up to the lot step.

**3. Crooks L** (Loss Recovery, after Crooks K): 0.01 lot until a win, then the loss is split by the drawdown.

- **After a loss:** the Crooks E / I lot (0.01) until a trade wins; then the recovery trades win the loss back **in parts**.
- **The parts are set when a loss is booked**, from where the closed profit is after it:
  - below the start: 1 part per **2 × base** of drawdown from the start, at most **6** (e.g. $250 down with a $50 base → 3 parts);
  - above the start but below the best: 1 part per **5 × base** below the best, at most **3**;
  - each winning recovery trade wins one part back; a loss sets the parts again.
- **At a new best** (and at the start), the base grows by **10% of the profit**, at most **4 × base**.
- "Win the loss back over N wins" is not used by Crooks L; every other Crooks C setting works.

| Setting | Default |
|---|---|
| Below the start: 1 part per (× base) · most parts | **2** · **6** |
| Above the start: 1 part per (× base) below the best · most parts | **5** · **3** |
| At a new best: base + % of the profit · at most (× base) | **10%** · **4** |

**Gold tests behind K and L** (2021–Oct 2026, 1:100 leverage, costs included):
- Crooks K on M15-S1 ($10,000, $50 base, monthly restart): Crooks J made $9,693 (biggest drawdown $1,127, worst month −$906); K with 0.02 lot made $6,968
  (drawdown $739, worst month −$341). Over the five tested strategies (M5-S1, M5-S3, M15-S1, S7, S8), K with 0.02 lot cut
  the worst month by 44–71% and the biggest drawdown by 34–57%, for 28–70% less profit. Of the careful sizes, lots worked best.
- Crooks L with your M5 settings ($1,000, $10 base, TP 0.1R / 0.6R / 2R): at 0.1R and 0.6R every rule, L included, emptied the
  account; at 2R L was the only rule that survived. No money rule makes a losing entry profitable.

**Checks**
- **Your settings are unchanged with Risk and the old rules:** the EA's money code gives the same $ risk as v4.9 on every trade (money
  suites: 8,784 + 22,484 + 20,544 runs, 78 M trades and signals, 0 differences). On the broker simulator (gold M1, Aug–Oct 2026 and
  Sep 2025–Jan 2026) every order and booking of v5.0 is identical to v4.9.
- **The new settings in the EA match the Python reference trade for trade:** Profit on every rule (also with your M5 settings at 0.1R and
  0.3R), Crooks K (lots / $ / %, ladder off and on) and L (three settings), the Crooks C rule after N losing recovery trades, Fixed lots
  and % of equity, the monthly restart and the TP1 rule: 33,984 runs, 45 M trades, 0 differences.
- **The Python reference** matches an independent implementation written only from the rules: 13,740 runs, 7.9 M trades, 0 differences.
- **The strategy** follows the same rules line by line (independent review: no defects); it parses, with 0 inline-title and 0 shadowing
  warnings, and every existing input keeps its title.
- **The EA** compiles with 0 errors and 0 warnings; on the broker simulator 12 runs with the new settings (Profit at 0.6R / 0.3R / 0.1R,
  Crooks K and L, restarts, the monthly restart) booked every trade with 0 rejected orders; wrong K / L / Profit inputs are refused at
  start with a message.

### v5.1: Profit amounts include the spread and commission (strategy and EA)

With **Base And Recovery Amounts Are = Profit**, v5.0 sized a trade as the amount ÷ the final TP's R. But the spread and the commission
are part of the loss at the stop, so a final-TP win came short by their share: about 8–9% with your M5 gold settings (a $50 base won about
$46). v5.1 sizes every trade from what a final-TP win brings per $1 lost at the stop **on that trade, costs included**, so the win is the
amount itself.

Example: gold, $50, final TP 0.1R, a $2.50 stop, spread 0.16, commission $7 a lot. One lot loses $273 at the stop and wins $25 at the TP.

| | Risk at the stop | Lots | Win at the final TP |
|---|---|---|---|
| v5.0 | $500 | 1.83 | $45.79 |
| v5.1 | $546 | 2.00 | **$50.00** |

- **Every amount** is converted the same way: the base, what each recovery rule adds, Exact at final TP and the Crooks recovery, Oscar's
  goal (one base win), Crooks K's careful $ and Crooks L's growth. The limits (hard cap, Crooks F–K, the profit ladder, L's part steps) stay
  on the loss at the stop, as in v5.0.
- **Keep "Extend Targets To Earn Back Commission + Spread" on** (the default). The target is then pushed by the costs and a win nets the
  full R. With it off the costs come out of the win, so the trade has to be far bigger: at 0.1R on a $2.50 stop a lot nets only $2 after
  the $23 of costs, so a $50 win needs $6,825 at risk. If a target cannot even pay the costs, the size falls back to amount ÷ R (v5.0's rule).
- **Lots are rounded down** to the lot step, so a win is the amount or a little less, never more. On a live account the fill price and the
  spread at that moment move each win a little.
- **Risk mode is unchanged.** The costs come from the strategy's "Spread (price)" and "Commission ($ per lot, round trip)", and from the
  EA's "Spread for sizing" (0 = the live spread) and "Commission per lot".

**Checks**
- **The EA matches the Python reference trade for trade** with Profit and the costs (spread 0.16, commission $7, earn-back on and off) on
  every rule, Crooks K and L in Risk and Profit, the Crooks C rule after N losing recovery trades, Fixed lots and % of equity, the monthly
  restart and the TP1 rule: 56,896 runs, 70 M trades. Every difference was traced: with earn-back off the test's own P&L makes a
  recovery win land exactly on the amount owed, so a few runs (5 of 56,896) split on a floating-point tie (a Crooks L / Oscar test landing
  exactly on its limit), or on the rounding of the test harness's impossible running totals (10¹² dollars); run a month at a time, those
  match to 5 × 10⁻¹². With a save and reload of the EA's memory after every step: 22,512 more runs, 27 M trades; one difference of
  6 × 10⁻⁹ on the trade where a test account blows (% of equity), the same without the restart. V51_RESTART_B
- **Risk mode and the old rules are unchanged:** the v4.9 money suites on v5.1 give 0 differences (rec 8,784 runs, TP1 22,484, Crooks C
  rule 20,544, monthly 1,536, position size 12,240: 90 M trades and signals).
- **Broker simulator** (gold M1, Aug–Oct 2026, $50, no recovery, the commission charged): the win each trade was sized for at its TP:

| Final TP | v5.0 average | v5.1 average | v5.1 largest |
|---|---|---|---|
| 0.6R | $46.22 | $47.21 | $49.99 |
| 0.2R | $47.78 | $49.07 | $49.99 |
| 0.1R | $48.17 | $49.56 | $49.99 |

  What v5.1 still misses is the lot rounding (largest at 0.6R, where a trade is about 0.09 lot). Every trade was booked; 0 rejected orders.
- **The EA** compiles with 0 errors and 0 warnings. **The strategy** parses with 0 inline-title and 0 shadowing warnings, and every input
  keeps its title.


### v5.2: Crooks X: win back the gap to the start, then to each step above it (strategy and EA)

A new Loss Recovery rule, after Crooks L. It works like **Crooks E** (after a loss, 0.01 lot until a win; then N recovery trades), but
**the loss to win back is read from your balance**, not added up from the trades:

| Where the balance is | Loss to win back (N = "Win The Loss Back Over N Wins") |
|---|---|
| Below the start | the whole gap to the start (start $1,000, balance $700 → $300; N = 3 → $100 a trade, N = 5 → $60) |
| Above the start, below the best | the gap up to the next step above the start, never above the best (step $1,000: balance $1,100, best $5,000 → $900 up to $2,000; then $1,000 up to $3,000, $4,000, $5,000) |
| At the best | nothing: the base trade |

- Each step is won back in N recovery trades; reaching a step starts N trades again for the next one. A loss sends it back to 0.01 lot;
  after the next win the gap is measured again.
- **The start and the best:** since the EA started (the backtest start in TradingView); with the monthly restart on, since the 1st of the
  month. The best is the highest closed balance.
- **Amounts:** with Risk each part is the loss at the stop, with Profit the win at the final TP (as every rule).

| Setting | Where | Default |
|---|---|---|
| Loss Recovery | Strategy: Loss Recovery → "Crooks X (Crooks E, the loss = the gap to the start / the next step)"; EA: "Loss recovery" → Crooks X | Crooks C |
| N (trades per gap) | "Crooks C: Win The Loss Back Over N Wins" (tick it and type N); EA: "...win the loss back over N wins" = true and "...N" | off (= 1) |
| Step above the start | Strategy: "Crooks X: Step Above The Start ($)"; EA: "Crooks X: above the start, win back up to the next level every this much" | **$1,000** |
| Limit of a recovery trade | Strategy: "Crooks X: Limit Of A Recovery Trade" (dropdown, the $ on the same line); EA: "Crooks X: limit of a recovery trade" + "...per-trade limit" | **Hard cap only** · $500 |
| 0.01 lot while waiting | "Crooks E / I: Lot While Waiting For A Win"; EA: "Crooks E / I / K / L: lot of the trades while a loss waits for a win" | 0.01 |

- **Hard cap only:** the Hard Cap (if you turn it on) limits a recovery trade, as for every rule. **Per-trade limit ($):** also, a
  recovery trade never risks more than this (the loss at its stop; never less than the base); what it does not win back is won by the next trades.
- A rule after N losing recovery trades (forget / % / wait / skip) or the Hard Cap's Start again clears the loss for the moment; with
  Crooks X the gap is measured again at the next close, so it comes back while the balance is still below the level.

**Checks**
- The EA matches the Python reference trade for trade on Crooks X: Risk and Profit, N = 1 / 3 / 5, steps $1,000 / $200 / $50, hard cap
  only / $300 limit, every hard-cap choice, the Crooks C rule after N losing recovery trades: 3,136 runs, 3.9 M trades, 0 differences;
  again with a save and reload after every step: 2,016 runs, 2.6 M trades, 0 differences (with the Crooks C rule: still running). The monthly restart suite with Crooks X: identical (month by month).
- Broker simulator (gold M1, Aug–Oct 2026, 0.2R): Crooks X with Risk and Profit, N = 3 and 5, a $300 limit: every trade booked, 0
  rejected orders; with 248 restarts of the EA the same bookings; the limit held (largest risk $299.95). Default settings: every order
  and booking identical to v5.1.
- The EA compiles with 0 errors and 0 warnings; the strategy parses with 0 inline-title and 0 shadowing warnings, every existing input
  keeps its title (3 new inputs).

### Entry accuracy research (November 2026, no code change)

Full results: `Research/deliverables/Gold_Entry_Accuracy_Research.xlsx`. The data was FxPro gold, 1-minute bars from 2021 to October 2026.

- **No edge today.** The signals hit TP1-TP4 about 62 / 50 / 40 / 33 % of the time. Random entries with the same stop and targets do the same
  (1 / (1 + target in R) = 62.5 / 50 / 40 / 33.3 %). Your v4.0 settings are the same.
- **What was tested.** About 1,100 entry rules and 3,700 mined conditions:
  - filters on the signals and machine learning on about 60 features;
  - other retest and confirmation entries, stops and VWAP rules;
  - opening ranges, liquidity sweeps, fades and time-of-day rules.
- **Result.** The best rules looked 3-7 points better than random on 2021-2025. None beat random on July 2025 - October 2026, the months kept
  aside and tested once.
- **Decision.** The engine is unchanged.
- **The one real pattern is New York time of day:** gold is weaker 07:00-10:00 and stronger 13:00-17:00. It was strong in 2023-2025 but weak
  in the test months.
- **Why the retest entry can't add accuracy:** the limit fills mostly on moves that are already weakening, and the strongest moves never come
  back to it.
- **Order flow (about 940 more variants), estimated from tick volume:** gold CFDs have no real buy / sell volume. Volume profile (POC, value area,
  LVN / HVN), delta and cumulative delta, absorption, exhaustion and low-volume pullbacks were tested, both as filters on the signals and as
  entries. None separated the winning signals from the losing ones in the test months (workbook sheet "7 Order flow").

## Same signals in the indicator, the strategy and the EA

The indicator and the strategy contain a **byte-identical ENGINE block** (between `// >>> ENGINE BEGIN` and `// <<< ENGINE END`, plus the shared
inputs, statistics and drawing blocks). It decides every setup, fill, stop move and exit from the chart's bars. The strategy's execution part only copies
those decisions into orders and never feeds back into them: the entry limit and the stop are placed on the tick grid so they trigger on exactly
the bars where the engine's levels are touched, the targets are added only after the fill bar, and if TradingView's fill simulator ever
disagrees the engine wins (the order is cancelled or the position closed). The old strategy drove its signals from the simulator's fills and
exits, which is why its trades drifted from the indicator's.

The EA's `ProcessBar()` is a line-by-line port of the same engine; it runs on closed bars only and then mirrors the decisions into broker
orders (buy limits and short stops/targets are shifted by the live spread so they trigger at the same bid-chart levels). Its signals follow
the same rules on the broker's own data feed and server-midnight session, so expect small differences where the broker's candles differ from
TradingView's.

EA setup: set **Broker server clock** (default from v4.0: **auto with EU summer time**, for brokers on Eastern European time such as FxPro, whose clock changes on the last Sundays of March and October; most other FX brokers use auto GMT+2 / GMT+3 with **US** daylight saving; or a fixed offset; with the wrong choice the days, hours, kill zones, news and force-close times are one hour off for 1-3 weeks a year) and
**Your time zone** (India = 5.5) so the day filter, trading hours, force-close and news times match your clock. The EA warms the engine up on
the last 3,000 bars when it starts, re-places a setup that is still armed, adopts its own open trade if the engine is in it, catches up bars
missed during a disconnect, and closes any broker position the engine is not in. The loss-recovery state (the loss to win back, the
Crooks cycle) is kept in memory only: after MetaTrader or the EA is restarted it starts again from the base risk.

EA display (group DISPLAY): **Show trade markings** draws every engine trade like the indicator, history included: the armed limit (dashed),
the target and stop boxes, the entry line, TP lines, a buy/sell arrow, price labels (entry, SL, final TP) and the result at the exit
(TP4 +2.00R, STOP -1.00R, BE). **Show the table** puts the strategy's table on the chart (state, levels, risk and lots, recovery, streaks,
day P&L, signals / taken / skipped, signal accuracy, TP HIT, BREAKEVEN, SKIPPED BY FILTERS, DATA RANGE). Each has one switch. In the
Strategy Tester tick **Visualization** to watch both; the markings stay on the visual chart when the test ends (they are skipped in
non-visual tests and optimisation, where nothing is drawn).

## Auction Retest Strategy (backtesting)

Signals and trades are the indicator's. Strategy-only settings never change them; they only decide whether a signal is taken and how big:

| Group | Settings |
|---|---|
| Partial profits | Close % at TP1 / TP2 / TP3 (share of the original position); the trade still ends at the final exit or the stop. |
| Risk | Base $ risk per trade (default $50); quantity = risk ÷ (stop distance × point value + costs per unit), converted to the account currency and rounded down to the lot step. Units per lot: auto by ticker or a fixed broker size. Hard cap with clamp / stop / restart. Leverage cap (default 1:100). Lot rounding down or to the nearest step; sizes below one lot step: fractional, minimum or skip. |
| Costs | Spread (price units) and commission per lot are counted in the sizing; the table shows the Properties commission per contract to enter (it includes the spread). Earn-back pushes the strategy's targets out by the costs (then the strategy can exit later than the indicator). |
| Streaks | Stop for the day after N losses / N wins in a row; pause 1-3 days after N losses in a row. |
| Force-close, weekend, news | Daily force-close time; close trades when Saturday starts; a daily news window and 5 one-off news events (no new trades from N minutes before, close at the start). |
| Loss recovery | 27 modes (all, over N, %, martingale, exact at final TP, step-up, Fibonacci, D'Alembert, Rule C, Rule C split, Labouchère, Grand Martingale, Paroli, Reverse D'Alembert, delayed, % of equity, Oscar's Grind, Crooks A, Crooks B, Crooks C, Crooks D, and from v4.5 Crooks E - J, see v4.5 above). **Crooks A**: trades 1 and 2 of a cycle risk the base; from trade 3 every other trade (3, 5, 7 ...) is a recovery trade risking max(base, loss to win back ÷ final target R), e.g. $250 with TP4 (2R) as the final target → $125; the trades between risk the base; losses add to the loss to win back, wins reduce it, and a winning recovery trade starts a new cycle. **Crooks B**: the same alternation, recovery risk = max(base, loss ÷ split ÷ final target R) with the Rule C split setting, and a new cycle only when the whole loss is won back. **Crooks C**: every trade risks the base until a trade wins; the trade after a win is a recovery trade (same size as Crooks A), and if it loses the rule waits for the next win again. E.g. four $50 losses = $200 to win back, trade 5 wins $50 → $150, trade 6 is the recovery trade for $150. Crooks C starts a new cycle only when the whole loss is won back: if a recovery trade wins but leaves part of the loss (leverage limit, hard cap Clamp, costs), the next trade is a recovery trade again for the rest. **Crooks D**: two base trades between recovery trades: base, base, recovery (trades 3, 6, 9 ...), same size as Crooks A; a winning recovery trade, or a loss fully won back, starts a new cycle. Keep the hard cap on with them (e.g. $500, Start again). **Crooks C: After N Losing Recovery Trades In A Row** (v3.9) can forget the loss, go for a part of it, wait for M wins in a row or skip D trading days after N losing recovery trades. The table row CROOKS: LOSS TO WIN BACK shows the amount, the trade number in the cycle and whether it is a base or recovery trade (Crooks C: base, waiting for a win). **Crooks At Exit TP1** (off by default from v4.0; EA `InpCrkT1`): with Final Exit At TP1 (any final exit with *Works With Any Final Exit*), a recovery trade is made bigger: the part set in *% Closed At TP1* (default half) closes at TP1 and banks the whole recovery amount, the stop of the rest moves to the entry and it closes at TP2; the default stop sits where a stop-out loses exactly the recovery amount (% × TP1 − (1 + %) × costs: 0.3R with half, TP1 = 0.6R and no costs; *Stop Before TP1* can widen it, e.g. to the normal stop). While that half runs on, new signals are skipped. On gold 2021–2026 the tight stop was hit on 75% of these trades, so it lost money: see the workbook before using it. **Gold 2021–2026, 25 profitable settings, $500 cap with Start again**: Crooks C made more than fixed $50 on 18 and Crooks D on 21 (Crooks A on 20), but the profit per $ of drawdown was better on only 5 (C) and 6 (D) (A: 10); without a cap Crooks D blew the account on 5 settings (M1, M5, M15). |

The table shows SIGNALS · TAKEN · SKIPPED, so any signal that an execution setting blocked is visible. With every execution setting off every signal is taken; the v4.0 defaults skip the signals in the news window, and earn-back can keep a trade open past the indicator's exit.
Below it the same accuracy rows as the indicator: SIGNAL TRADES · WIN % · R, TP HIT, BREAKEVEN (when a stop move is on), SKIPPED BY FILTERS
(when a filter is on) and DATA RANGE (first and last bar, bar count; time zone in DISPLAY).
**Leverage**: TradingView's own margin check is off (margin 0 in Properties); the leverage input limits the position value instead.
The only remaining way the strategy's trade list can differ from the indicator is a single bar that touches both the stop and the target after
the fill bar (the indicator counts the stop; TradingView's simulator decides from the bar's shape). It does not affect any later signal.

## Indicator table and alerts

**Model monitor table** (compact rows; hover a row for its tooltip): STATE (scanning / armed / active / day cap / day switched off /
outside hours / skipped and by which filter) · REGIME / BIAS · ENTRY / STOP (½ = half stop) · TP1 · TP2 · TP3 · TP4 · LIVE · BARS · HIT ·
MODEL DAY (date, W/L, win %, R, fills / cap) · LOADED BARS (closed trades, win % with W/L, total R, last result) · **TP HIT** (TP1 … TP4: share
and number of closed trades that reached each target before the stop) · **BREAKEVEN** (when a Move Stop setting is on) · **SKIPPED BY
FILTERS** (when a filter is on) · WIN 1R · 1.5R · 2R (share of closed trades that reached each level before the stop) · DATA RANGE.

**Alerts**: fixed alerts for Buy / Sell Retest Armed, Entry Filled, Target Hit, Stop Hit and Retest Cancelled, plus one "Any alert() function
call" alert that sends every event with its prices.

For educational use only. This is not financial advice.
