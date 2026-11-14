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
- **Sync:** where the model acts inside a candle in a way TradingView cannot, a market order at the next open puts TradingView back in
  line ("sync" in the trade list). Those cases are:
  - an SL / TP moved by a BE, salvage or trailing trigger and hit in the same candle;
  - a dip under and back over the buy stop inside one candle;
  - a candle-close entry.

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
| 1-minute | 12, 10, 4, 9 | 96.6 % (3,469 of 3,591) | -0.7 % |

The trade counts are equal within 1 per strategy. Use a 1-minute chart for all 12 strategies (5-minute for 1-11). TradingView only
backtests the history it loads (on 1-minute charts a few weeks, more with Deep Backtesting).

**v3 tests:**
- **Engine:** the engine, the fast search evaluator and the indicator's Python twin with the v3 rules all agree. That is 0 differences on
  40 random settings (47,793 trades); 48 random option combinations (5,193 trades); and strategies 4, 9, 10 and 12 on a 1-minute chart
  (3,591 trades).
- **Strategy orders:** the broker model above.
- **Pine:** both files parse, have 0 inline-title warnings, and every name is defined. The indicator build has no `strategy.` reference.
  The strategy passed an independent review.
