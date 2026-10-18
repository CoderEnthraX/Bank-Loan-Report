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

Every rule below was measured from the reference screenshots: 12 fully measured trades on GC1! and EURUSD, plus checks on US Tech 100, MCX crude and Nifty.

| Step | Rule | Default |
|---|---|---|
| VWAP | Session VWAP, reset at each new trading day (03:30 IST for CME/ICE, 09:00 for MCX, 09:15 for NSE) | Session |
| Side filter | Longs only when the displacement closes above VWAP; shorts only when it closes below | On |
| Displacement | A confirmed candle closing beyond the highest high (long) or lowest low (short) of the previous 6 bars. Its body is ≥ 60 % of its range, it closes within 30 % of its extreme, and its range is ≥ 0.8 × ATR | 6 / 60 % / 30 % / 0.8 |
| Armed | Limit = the shallower of the 50 % body level and the broken 6-bar level. A dashed line marks it for the retest window | 5 bars |
| Filled | Price trades back into the limit: ▲ under the bar for a long, ▼ above the bar for a short. The trade boxes start on this bar | — |
| Stop | Entry ∓ 1.8 × ATR(14) (an optional *Swing + Buffer* mode is available) | 1.8 |
| Targets | TP1–TP4 = 0.6R / 1R / 1.5R / 2R. The trade ends at **TP4 (+2R)** or the **stop (−1R)** | 0.6/1/1.5/2 |
| Controls | One trade at a time; a 2-bar cooldown after an exit; at most 5 fills per day | 2 / 5 |

**Model monitor table**, one row each:

1. **STATE**: SCANNING / BUY or SELL RETEST ARMED / LONG or SHORT ACTIVE.
2. **REGIME**: from the ADX and the DI spread.
3. **BIAS**: from the DI spread.
4. **ENTRY**: shown as LIMIT while the setup is armed.
5. **STOP**.
6. **TP1–TP4**.
7. **LIVE / BARS**: the current R and the bars since the fill.
8. **TARGETS HIT**: n/3.
9. **MODEL DAY**: W/L, win % and R. A trade counts on the day it exits.
10. **FILLS / CAP**.
11. **LOADED BARS**: the last result, the win % and the total R over the loaded history.

**Alerts**:

- Fixed alerts: Buy/Sell Retest Armed, Entry Filled, Target Hit and Stop Hit.
- Full details: one alert with **Any alert() function call** sends every event with its prices.

### Accuracy notes

- The entry rule matched all 12 measured trades to within one or two ticks.
- The 1.8 × ATR stop matched 10 of 12. Two shorts in the screenshots had tighter stops, just beyond the displacement candle, and no rule fitted them consistently.
- The reference uses a closed-source script, so a few internals could not be measured from photos: the exact ATR length, and how the vendor treats a bar that touches both the stop and TP4. Expect most trades to match, but a few may differ by a bar or a tick. All of these settings are inputs.
- REGIME and BIAS are informational only. The reference trades in every regime.

For educational use only. This is not financial advice.
