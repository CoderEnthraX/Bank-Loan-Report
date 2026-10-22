# TradingView indicators

| File | What it is |
|---|---|
| [`Auction_Retest_Model.pine`](Auction_Retest_Model.pine) | **Auction Retest Model**: session VWAP + displacement + time-limited retest. It reproduces the trade logic seen on the *Auction Retest Pro* reference screenshots. |
| [`Auction_Retest_Strategy.pine`](Auction_Retest_Strategy.pine) | The same engine as a **strategy** for backtesting (identical signals and trades), with money-management settings (all off by default). |
| [`../MetaTrader5/AuctionRetestEA.mq5`](../MetaTrader5/AuctionRetestEA.mq5) | MetaTrader 5 Expert Advisor: a port of the same engine plus the strategy's money management. |
| [`VWAP_Orderflow_Sniper.pine`](VWAP_Orderflow_Sniper.pine) | The earlier VWAP + absorption/aggression orderflow indicator. |

## Install

1. In TradingView, open **Pine Editor** and choose **Open → New blank indicator**.
2. Paste the whole `.pine` file, then click **Save** and **Add to chart**.
3. Use a 5-minute chart. Futures and FX with volume give a true VWAP. Symbols without volume (e.g. `NSE:NIFTY`) automatically use a time-weighted average instead.

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
| Targets | TP1-TP4 = 0.6 / 1 / 1.5 / 2 R; the trade ends at **TP4 (+2R)** or the stop (stop first when a bar touches both). Levels unrounded | 0.6/1/1.5/2 |
| Controls | One trade at a time (carried over sessions), no new setup on the exit bar, at most 5 fills per day, **no daily R stop** (the original keeps trading after three losses) | 1 / 5 / off |

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
| Targets, exit and stop moves | Final exit at TP1-TP4; move the stop when TP1 / TP2 / TP3 hits (breakeven at +1R = TP2 → 0) | TP4 / off |
| Accuracy filters (research) | **Don't chase**: skip a signal more than 2.4 σ from the session VWAP; the skipped setup still runs invisibly so the next, more stretched candle is not taken instead. **After a loss, no same-direction trade until a win** (rest of the session) | Off |
| Days and hours | **Trade only on the ticked days** (Mon ... Sun) and trade only between two times, in your time zone (default Asia/Kolkata). They stop new setups only; open trades finish | Off |

**Accuracy research** (separate from the clone; October data held out of every fit): the don't-chase filter raised the October 2R hit rate
from 39 % to 42 % and the average from +0.18R to +0.26R per trade with 75 % of trades kept; the after-loss rule helped in October only;
breakeven at +1R cut full losses from 62 % to 47 % and the longest losing streak from 20 to 8 without changing the average. Volume /
delta / absorption / exhaustion proxies, deeper entries and trend filters did not help beyond chance. Forward-test before relying on them.

## Same signals in the indicator, the strategy and the EA

The indicator and the strategy contain a **byte-identical ENGINE block** (between `// >>> ENGINE BEGIN` and `// <<< ENGINE END`, plus the shared
inputs and drawing blocks). It decides every setup, fill, stop move and exit from the chart's bars. The strategy's execution part only copies
those decisions into orders and never feeds back into them: the entry limit and the stop are placed on the tick grid so they trigger on exactly
the bars where the engine's levels are touched, the targets are added only after the fill bar, and if TradingView's fill simulator ever
disagrees the engine wins (the order is cancelled or the position closed). The old strategy drove its signals from the simulator's fills and
exits, which is why its trades drifted from the indicator's.

The EA's `ProcessBar()` is a line-by-line port of the same engine; it runs on closed bars only and then mirrors the decisions into broker
orders (buy limits and short stops/targets are shifted by the live spread so they trigger at the same bid-chart levels). Its signals follow
the same rules on the broker's own data feed and server-midnight session, so expect small differences where the broker's candles differ from
TradingView's.

## Auction Retest Strategy (backtesting)

Signals and trades are the indicator's. Strategy-only settings never change them; they only decide whether a signal is taken and how big:

| Group | Settings |
|---|---|
| Partial profits | Close % at TP1 / TP2 / TP3 (share of the original position); the trade still ends at the final exit or the stop. |
| Risk | Base $ risk per trade (default $50); quantity = risk ÷ (stop distance × point value + costs per unit), converted to the account currency and rounded down to the lot step. Units per lot: auto by ticker or a fixed broker size. Hard cap with clamp / stop / restart. Leverage cap (default 1:100). Sizes below one lot step: fractional, minimum or skip. |
| Costs | Spread (price units) and commission per lot are counted in the sizing; the table shows the Properties commission per contract to enter (it includes the spread). Earn-back pushes the strategy's targets out by the costs (then the strategy can exit later than the indicator). |
| Streaks | Stop for the day after N losses / N wins in a row; pause 1-3 days after N losses in a row. |
| Force-close, weekend, news | Daily force-close time; close trades when Saturday starts; a daily news window and 5 one-off news events (no new trades from N minutes before, close at the start). |
| Loss recovery | 17 modes (all, over N, %, martingale, exact at final TP, step-up, Fibonacci, D'Alembert, Rule C, Rule C split, Labouchère, Grand Martingale, Paroli, Reverse D'Alembert, delayed, % of equity, Oscar's Grind). |

The table shows SIGNALS · TAKEN · SKIPPED, so any signal that an execution setting blocked is visible. With the defaults every signal is taken.
**Leverage**: TradingView's own margin check is off (margin 0 in Properties); the leverage input limits the position value instead.
The only remaining way the strategy's trade list can differ from the indicator is a single bar that touches both the stop and the target after
the fill bar (the indicator counts the stop; TradingView's simulator decides from the bar's shape). It does not affect any later signal.

## Indicator table and alerts

**Model monitor table** (10 compact rows; hover a row for its tooltip): STATE (scanning / armed / active / day cap / day switched off /
outside hours / skipped by the don't-chase filter) · REGIME / BIAS · ENTRY / STOP (½ = half stop) · TP1 · TP2 · TP3 · TP4 · LIVE · BARS · HIT ·
MODEL DAY (date, W/L, win %, R, fills / cap) · LOADED BARS (last result, win %, total R) · DATA RANGE · WIN 1R · 1.5R · 2R (share of closed
trades that reached each level before the stop).

**Alerts**: fixed alerts for Buy / Sell Retest Armed, Entry Filled, Target Hit, Stop Hit and Retest Cancelled, plus one "Any alert() function
call" alert that sends every event with its prices.

For educational use only. This is not financial advice.
