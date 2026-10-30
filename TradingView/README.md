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

### Settings added in v3.1 (all off by default; identical in the indicator, the strategy and the EA)

| Group | Setting | What it does | Research result |
|---|---|---|---|
| Signal model | **Half stop never wider than the normal stop** | A half stop that would sit further from the entry than the 1.8 ATR stop (after a very tall signal candle) is pulled in to the normal stop | One more logged stop matched (NIFTY futures #27), 3 of 1,190 trades changed, all 80 screenshot stops unchanged |
| Accuracy filters | **Skip choppy sessions: max VWAP crosses per 100 bars** (default limit 12) | Counts how often the close has crossed the VWAP so far in the session (from more than 0.2 ATR on one side to more than 0.2 ATR on the other). Above the limit a new setup is skipped and runs invisibly, like Don't Chase | Average +0.17R → +0.21R per trade, October +0.20R → +0.27R, total +197R → +207R, 82 % of trades kept, 9 of 10 instruments better, natural gas +0.28R → +0.34R. Not proven; it skips mostly the same trades as Don't Chase, so use one or the other |
| Accuracy filters | **Skip when the 1h EMA20 moved more than X ATR in 3 hours** (default 1.65) | Builds 1-hour candles (UTC hours) from the chart and skips a setup when the EMA20 of the last completed hour has moved more than the limit from 3 hours earlier (an over-extended trend); runs invisibly | Average +0.17R → +0.23R, total +197R → +199R, 72 % kept, 8 of 10 instruments better, **natural gas worse** (+0.28R → +0.08R). Not proven |
| Accuracy filters | **Skip signals too close to VWAP: min distance** (default 1.0 ATR) | Skips a long whose signal candle closes less than this many ATR above the VWAP (short: below); runs invisibly like Don't Chase. Together with Don't Chase it makes a band (e.g. 1 ATR to 2σ) | 1:1 win rate 54.0% → 54.7%, 1:2 38.9% → 39.8%, +0.17R → +0.20R per trade, total +197R → +218R, 94 % kept, 8 of 10 instruments better. With Don't Chase at 2.0σ: 1:1 57.5 %, 1:2 43.9 %, +0.32R per trade, about half the trades. Not proven |
| Style | **Show trade markings** (default on) | One switch for the limit line, boxes, entry and TP lines and fill triangles | — |
| Days and hours | **Trade only in kill zones** (Indian time), each zone ticked separately: Asia 05:30-09:30, London 11:30-14:30, New York 16:30-19:30, London close 19:30-21:30; **Shift all kill zones** −2 … +2 hours (e.g. +1: Asia 06:30-10:30) for daylight-saving changes | New setups are armed only inside the ticked zones (bar open time, end not included); open trades and armed limits finish. The table says OUTSIDE KILL ZONES | — |

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

EA setup: set **Broker server clock** (default: auto GMT+2 / GMT+3 with US daylight saving, which most FX brokers use; or a fixed offset) and
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
| Risk | Base $ risk per trade (default $50); quantity = risk ÷ (stop distance × point value + costs per unit), converted to the account currency and rounded down to the lot step. Units per lot: auto by ticker or a fixed broker size. Hard cap with clamp / stop / restart. Leverage cap (default 1:100). Sizes below one lot step: fractional, minimum or skip. |
| Costs | Spread (price units) and commission per lot are counted in the sizing; the table shows the Properties commission per contract to enter (it includes the spread). Earn-back pushes the strategy's targets out by the costs (then the strategy can exit later than the indicator). |
| Streaks | Stop for the day after N losses / N wins in a row; pause 1-3 days after N losses in a row. |
| Force-close, weekend, news | Daily force-close time; close trades when Saturday starts; a daily news window and 5 one-off news events (no new trades from N minutes before, close at the start). |
| Loss recovery | 21 modes (all, over N, %, martingale, exact at final TP, step-up, Fibonacci, D'Alembert, Rule C, Rule C split, Labouchère, Grand Martingale, Paroli, Reverse D'Alembert, delayed, % of equity, Oscar's Grind, Crooks A, Crooks B, Crooks C, Crooks D). **Crooks A**: trades 1 and 2 of a cycle risk the base; from trade 3 every other trade (3, 5, 7 ...) is a recovery trade risking max(base, loss to win back ÷ final target R), e.g. $250 with TP4 (2R) as the final target → $125; the trades between risk the base; losses add to the loss to win back, wins reduce it, and a winning recovery trade starts a new cycle. **Crooks B**: the same alternation, recovery risk = max(base, loss ÷ split ÷ final target R) with the Rule C split setting, and a new cycle only when the whole loss is won back. **Crooks C**: every trade risks the base until a trade wins; the trade after a win is a recovery trade (same size as Crooks A), and if it loses the rule waits for the next win again. E.g. four $50 losses = $200 to win back, trade 5 wins $50 → $150, trade 6 is the recovery trade for $150. **Crooks D**: two base trades between recovery trades: base, base, recovery (trades 3, 6, 9 ...), same size as Crooks A. With C and D a winning recovery trade, or a loss fully won back, starts a new cycle. Keep the hard cap on with them (e.g. $500, Start again). The table row CROOKS: LOSS TO WIN BACK shows the amount, the trade number in the cycle and whether it is a base or recovery trade (Crooks C: base, waiting for a win). **Crooks At Exit TP1** (on by default; EA `InpCrkT1`): with Final Exit At TP1, a recovery trade is doubled: half closes at TP1 and banks the whole recovery amount, the stop of the other half moves to the entry and it closes at TP2; the stop sits where a stop-out loses exactly the recovery amount (TP1 ÷ 2 − 1.5 × costs: 0.3R with TP1 = 0.6R and no costs). While that half runs on, new signals are skipped. On gold 2021–2026 the tight stop was hit on 75% of these trades, so it lost money: see the workbook before using it. **Gold 2021–2026, 25 profitable settings, $500 cap with Start again**: Crooks C made more than fixed $50 on 17 and Crooks D on 21 (Crooks A on 20), but the profit per $ of drawdown was better on only 7 (C) and 6 (D) (A: 10); without a cap Crooks D blew the account on 5 settings (M1, M5, M15). |

The table shows SIGNALS · TAKEN · SKIPPED, so any signal that an execution setting blocked is visible. With the defaults every signal is taken.
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
