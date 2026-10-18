# TradingView indicators

| File | What it is |
|---|---|
| [`Auction_Retest_Model.pine`](Auction_Retest_Model.pine) | **Auction Retest Model**: session VWAP + displacement + time-limited retest. It reproduces the trade logic seen on the *Auction Retest Pro* reference screenshots. |
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
| Armed | Limit = the shallower of the 50 % body level and the 6-bar high (long) or low (short) before the candle. A dashed line marks it for the retest window. A newer candle in the same direction does not move an armed limit; an opposite one replaces it | 5 bars |
| Filled | Price trades back into the limit: ▲ under the bar for a long, ▼ above the bar for a short. The trade boxes start on this bar, and the stop is also checked on it | — |
| Stop | Entry ∓ 1.8 × ATR(14) of the displacement candle (an optional *Swing + Buffer* mode is available) | 1.8 |
| Targets | TP1–TP4 = 0.6R / 1R / 1.5R / 2R. The trade ends at **TP4 (+2R)** or the **stop (−1R)**. Levels are kept unrounded, like the original | 0.6/1/1.5/2 |
| Controls | One trade at a time (trades carry over to the next session); a 2-bar cooldown after an exit; at most 5 fills per day; no new setups after −3R on the day | 2 / 5 / 3R |

**Model monitor table**, one row each:

1. **STATE**: SCANNING / BUY or SELL RETEST ARMED / LONG or SHORT ACTIVE / DAY CAP REACHED / DAILY STOP HIT.
2. **REGIME**: from the ADX and the DI spread.
3. **BIAS**: from the DI spread.
4. **ENTRY**: shown as LIMIT while the setup is armed.
5. **STOP**.
6. **TP1–TP4**.
7. **LIVE / BARS**: the current R and the bars since the fill.
8. **TARGETS HIT**: n/3.
9. **TRADING DAY**: the date the MODEL DAY row covers.
10. **MODEL DAY**: W/L, win % and R. A trade counts on the day it exits.
11. **FILLS / CAP**.
12. **DATA RANGE**: the first and last loaded bar and the bar count.
13. **LOADED BARS**: the last result, the win % and the total R over the loaded history.
14. **WIN RATE 1R / 1.5R / 2R**: the share of closed trades that reached that profit before the stop. The levels can be changed in the settings.

**Alerts**:

- Fixed alerts: Buy/Sell Retest Armed, Entry Filled, Target Hit and Stop Hit.
- Full details: one alert with **Any alert() function call** sends every event with its prices.

### Accuracy notes

The model was replayed bar by bar on the same 5-minute data as the 80 original trades:

- **71 of 80** original trades are reproduced on the exact candle, with the same direction, entry and stop. The previous version matched 50.
- **9** trades are extra (the previous version had 38), and **9** original trades are missed.
- **Entries:** every original entry is the body mid or the 6-bar level of a 10-bar breakout candle. The exception is two US30 shorts on 7 Oct, where one spike wick blocks the breakout in this data.
- **Stops:** 72 of the 80 original stops are exactly 1.8 × ATR(14). The other 8 are about half that (0.9 × ATR, or just beyond the displacement candle). No rule in the data separates them, so the model always uses 1.8 × ATR. On those trades the original exits earlier, and this causes most of the remaining misses.
- **Win rate:** across the exported history the model wins 33–39 % per symbol at +2R / −1R. This is the same range as the original's LOADED BARS readings (34–38 %).
- REGIME and BIAS are informational only. The reference trades in every regime.

For educational use only. This is not financial advice.
