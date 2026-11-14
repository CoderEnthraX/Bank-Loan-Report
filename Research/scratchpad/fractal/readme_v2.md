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
- **Indicator code vs the engine with the new options:** the indicator's code, translated line by line to Python, matched the
  extended engine on 87 random option combinations (M15 and M5 charts, 5 time zones). That is 13,519 trades, all identical; the engine
  computes its filters independently.
- **Money code vs `gold/recovery.py`:** the Pine money code matched the strategy / EA reference on 2,600 random money settings (all 28
  rules, caps, ladder and options), about 880,000 trades, with 0 differences.
  - Oscar's Grind: one rounding knife-edge (zero costs) made a unit count of exactly 1 round up to 2, so the count now ignores a 1e-9
    residue.
- **End to end with Money on:** identical on 10 random settings, including the cap's Stop trading.
- **Pine checks:** it parses, has 0 inline-title warnings, and passed an independent review.
