# TradingView indicators

| File | What it is |
|---|---|
| [`Auction_Retest_Model.pine`](Auction_Retest_Model.pine) | **Auction Retest Model**: session VWAP + displacement + time-limited retest. It reproduces the trade logic seen on the *Auction Retest Pro* reference screenshots. |
| [`Auction_Retest_Strategy.pine`](Auction_Retest_Strategy.pine) | The same model as a **strategy** for backtesting, with money-management settings (all off by default). |
| [`VWAP_Orderflow_Sniper.pine`](VWAP_Orderflow_Sniper.pine) | The earlier VWAP + absorption/aggression orderflow indicator. |

## Install

1. In TradingView, open **Pine Editor** and choose **Open → New blank indicator**.
2. Paste the whole `.pine` file, then click **Save** and **Add to chart**.
3. Use a 5-minute chart. Futures and FX with volume give a true VWAP. Symbols without volume (e.g. `NSE:NIFTY`) automatically use a time-weighted average instead.

## Auction Retest Model: how a trade is built

The rules below were fitted to **80 trades of the original indicator**. They were read candle by candle from 53 screenshots (original vs. this model) and matched to exported 5-minute data. The symbols are GC1!, EURUSD, US Tech 100, US30, MCX crude, Nifty, Sensex and ETHUSD, for 5–12 Oct.

| Step | Rule | Default |
|---|---|---|
| VWAP | Session VWAP, reset at each new trading day (03:30 IST for CME/ICE, 09:00 for MCX, 09:15 for NSE, 05:30 for crypto) | Session |
| Side filter | Longs only when the displacement closes above VWAP and VWAP is higher than 3 bars ago. Shorts only when it closes below and VWAP is lower | On / 3 bars |
| Displacement | A confirmed candle closing beyond the highest high (long) or lowest low (short) of the previous **10** bars. Its body is ≥ 55 % of its range, it closes within 25 % of its extreme, its range is ≥ 0.8 × ATR, and its close is ≥ 0.85 × ATR beyond the close 10 bars earlier | 10 / 55 % / 25 % / 0.8 / 0.85 |
| Skipped | The first bar after a VWAP reset, and bars opening on Sunday (UTC), the thin weekly reopen | 1 bar / On |
| Re-anchored break | Within 10 bars of a closed trade's fill, a new signal in that trade's direction must break the high (long) / low (short) made since that fill instead of the 10-bar extreme | On |
| Armed | Limit = the shallower of the 50 % body level and the 6-bar high (long) or low (short) before the candle. A dashed line marks it for the retest window. A newer candle in the same direction does not move an armed limit; an opposite one replaces it | 5 bars |
| Filled | Price trades back into the limit: ▲ under the bar for a long, ▼ above the bar for a short. The trade boxes start on this bar, and the stop is also checked on it | — |
| Stop | Entry ∓ 1.8 × ATR(14) of the displacement candle (an optional *Swing + Buffer* mode is available) | 1.8 |
| Half stop | The first impulse of a session in a direction, when the previous session had at least 3 more impulses the other way (bull minus bear), uses entry ∓ 0.9 × ATR, or just beyond the displacement candle if that is further. An *impulse* is the displacement candle whose wick breaks the 10-bar high/low, counted with no other gates | 0.9 / 3 |
| Targets | TP1–TP4 = 0.6R / 1R / 1.5R / 2R. The trade ends at **TP4 (+2R)** or the **stop (−1R)**. Levels are kept unrounded, like the original | 0.6/1/1.5/2 |
| Controls | One trade at a time (trades carry over to the next session); a 2-bar cooldown after an exit; at most 5 fills per day; no new setups after −3R on the day (a trade stopped out on its own fill bar does not count toward this daily stop) | 2 / 5 / 3R |

**Model monitor table** (10 compact rows; hover a row for its tooltip):

1. **STATE**: SCANNING / BUY or SELL RETEST ARMED / LONG or SHORT ACTIVE / DAY CAP REACHED / DAILY STOP HIT.
2. **REGIME / BIAS**: regime with the ADX, then the DI bias.
3. **ENTRY / STOP** (LIMIT / STOP while armed). A **½** marks a half stop.
4. **TP1 · TP2 · TP3 · TP4**.
5. **LIVE · BARS · HIT**: the current R, the bars since the fill and TP1–TP3 reached.
6. **MODEL DAY**: the trading date, W/L, win %, R and fills / daily cap. A trade counts on the day it exits.
7. **LOADED BARS**: the last result, the win % and the total R over the loaded history.
8. **DATA RANGE**: the first and last loaded bar and the bar count.
9. **WIN 1R · 1.5R · 2R**: the share of closed trades that reached each profit level before the stop, plus the trade count. The levels can be changed in the settings.

**Alerts**:

- Fixed alerts: Buy/Sell Retest Armed, Entry Filled, Target Hit, Stop Hit and Retest Cancelled (the armed limit expired or was replaced, so cancel a working order).
- Full details: one alert with **Any alert() function call** sends every event with its prices.

### Accuracy notes

The model was replayed bar by bar on the same 5-minute data as the 80 original trades:

- **79 of 80** original trades are reproduced on the exact candle, with the same direction, entry and stop. The first version matched 50.
- **3** trades are extra (the first version had 38) and **1** original trade is missed. The remaining differences are borderline cases: an ETH long whose breakout clears the 10-bar high by only 0.15, so the model arms one bar before the original (one extra plus the one miss); a CRUDE long where the VWAP slope is barely positive; and a NIFTY short whose setup matches a SENSEX trade the original did take.
- **Entries:** every original entry is the body mid or the 6-bar level of a breakout candle, including the US30 7 Oct shorts, which need the re-anchored break after the 05:30 trade.
- **Stops:** all 80 original stops are reproduced: 72 at 1.8 × ATR(14) and the 8 half stops at 0.9 × ATR (or just beyond the displacement candle), which the half-stop rule picks out exactly. It also explains why NIFTY and SENSEX took the same 9 Oct long with different stops: SENSEX had an earlier impulse that session, NIFTY did not.
- **Win rate:** across the exported history the model wins 33–39 % per symbol at +2R / −1R. This is the same range as the original's LOADED BARS readings (34–38 %).
- REGIME and BIAS are informational only. The reference trades in every regime.

## Auction Retest Strategy (backtesting)

Signals are the indicator's. Extra settings, all **off by default**:

| Group | Settings |
|---|---|
| Entry price | Model limit (default) · Custom % of the signal candle measured from its close (0 = close, 50 = midpoint, 100 = low/high) · Market at the next open. The stop is measured from the chosen entry. |
| Targets | TP1–TP4 in R; optional partial close % at TP1, TP2, TP3; optional stop moves when TP1/TP2/TP3 hit (in R: 0 = breakeven, 0.6 = TP1 level, …). |
| Risk | Base $ risk per trade (default $50). Quantity = risk ÷ (stop distance × point value), converted to the account currency and rounded down to the lot step. Units per lot (forex, default 100,000) and max-risk cap. |
| Costs | Spread in ticks (chart = bid; buys pay the spread). Commission $ per lot round trip, plus an option to push every target out by commission + spread. TradingView only charges commission set in **Settings → Properties**; the table shows the value to enter there. |
| Streaks | Stop for the day after N losses in a row; stop for the day after N wins in a row; pause for 1–3 trading days after N losses in a row. |
| Loss recovery | Off · recover all unrecovered losses on the next trade (base + total loss) · over N trades · a % of the losses · martingale multiplier · exact recovery at TP4 (base + losses ÷ TP4 R) · step-up (+$ per loss in a row) · Fibonacci · D'Alembert. Sizing returns to base once profits repay the pool. |

Note: TradingView's broker emulator decides the order of stop vs target inside a bar from the bar's open/high/low, so a few trades can exit differently from the indicator, which always assumes the stop first.

For educational use only. This is not financial advice.
