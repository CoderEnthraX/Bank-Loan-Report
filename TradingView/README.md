# TradingView indicators

| File | What it is |
|---|---|
| [`Auction_Retest_Model.pine`](Auction_Retest_Model.pine) | **Auction Retest Model**: session VWAP + displacement + time-limited retest. It reproduces the trade logic seen on the *Auction Retest Pro* reference screenshots. |
| [`Auction_Retest_Strategy.pine`](Auction_Retest_Strategy.pine) | The same engine as a **strategy** for backtesting (identical signals and trades), with money-management settings (from v4.0 the defaults are the gold / FxPro settings, see v4.0 below). |
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
  take profit. To trade another timeframe, remove the EA and attach it again on that timeframe.
- **One copy per symbol and magic number.** A second copy with the same symbol and magic number does not start (alert). Two copies cancel
  and close each other's trades and share one restart memory. Another EA on the account is listed in the Experts tab at start.
- **Broker server clock: Auto (new default).** The EA reads the broker's GMT offset from MT5 (server time minus GMT) and picks the EU or US
  summer-time rule, or that fixed offset. A new broker no longer needs the clock set by hand. With any other choice, an alert appears when
  the broker's clock differs from it, because your days, hours, kill zones, news and force-close times would be off. The table row `BROKER
  CLOCK` shows the offset in use. In the Strategy Tester Auto means the EU rule, as before.
- **VWAP line on the chart** (new, on by default). The EA draws the VWAP it trades on: the same anchor (session / week / month), source and
  tick volume as its signals. It looks like the TradingView indicator's VWAP (#4DD0E1, width 2). The DISPLAY inputs are **Show the VWAP
  line** (on), its colour, its width, and how many candles of VWAP are drawn (1,500; older parts are removed as new candles come). The line
  is drawn on the chart and in the Strategy Tester's visual mode, and removed with the EA. Switch it off with **Show the VWAP line = false**.
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
- **Over the 17 scenarios:**

  |                                   | v4.3  | v4.4  |
  |-----------------------------------|-------|-------|
  | Trades                            | 1,659 | 1,568 |
  | Opened without a take profit      | 1,659 | 0     |
  | Closed early by "engine wins"     | 67    | 0     |
  | Booked wrong                      | 81    | 0     |
- **v4.4 on all 33 runs (3,443 trades):**
  - 0 early closes, 0 signals traded twice, 0 rejected orders, 0 failed starts;
  - a take profit on every order;
  - every booking equal to the broker's profit;
  - the only closes by the EA were its rules: the engine's stop, a stop the price had already passed after a move, and a news start;
  - restarts and same-input re-initialisations give the same trades as no restart (a sell's take profit can move by the live spread when it
    is re-sent);
  - the copy lock and the clock detection work (GMT+3 / +2 / 0 / +5.5 / -4).
- **Two independent code reviews** (Opus, high effort; the second on the fixes of the first). Every finding was checked against the code
  first, the serious ones were reproduced in the simulator, and all were fixed.
- **Compile check:** 0 errors, 0 warnings. The money-management parity suites (normal, and with a restart after every step) and the engine
  parity (three date shifts) were re-run on the final file (`Research/scratchpad/v40/final_v44.txt`).

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
| Loss recovery | 21 modes (all, over N, %, martingale, exact at final TP, step-up, Fibonacci, D'Alembert, Rule C, Rule C split, Labouchère, Grand Martingale, Paroli, Reverse D'Alembert, delayed, % of equity, Oscar's Grind, Crooks A, Crooks B, Crooks C, Crooks D). **Crooks A**: trades 1 and 2 of a cycle risk the base; from trade 3 every other trade (3, 5, 7 ...) is a recovery trade risking max(base, loss to win back ÷ final target R), e.g. $250 with TP4 (2R) as the final target → $125; the trades between risk the base; losses add to the loss to win back, wins reduce it, and a winning recovery trade starts a new cycle. **Crooks B**: the same alternation, recovery risk = max(base, loss ÷ split ÷ final target R) with the Rule C split setting, and a new cycle only when the whole loss is won back. **Crooks C**: every trade risks the base until a trade wins; the trade after a win is a recovery trade (same size as Crooks A), and if it loses the rule waits for the next win again. E.g. four $50 losses = $200 to win back, trade 5 wins $50 → $150, trade 6 is the recovery trade for $150. Crooks C starts a new cycle only when the whole loss is won back: if a recovery trade wins but leaves part of the loss (leverage limit, hard cap Clamp, costs), the next trade is a recovery trade again for the rest. **Crooks D**: two base trades between recovery trades: base, base, recovery (trades 3, 6, 9 ...), same size as Crooks A; a winning recovery trade, or a loss fully won back, starts a new cycle. Keep the hard cap on with them (e.g. $500, Start again). **Crooks C: After N Losing Recovery Trades In A Row** (v3.9) can forget the loss, go for a part of it, wait for M wins in a row or skip D trading days after N losing recovery trades. The table row CROOKS: LOSS TO WIN BACK shows the amount, the trade number in the cycle and whether it is a base or recovery trade (Crooks C: base, waiting for a win). **Crooks At Exit TP1** (off by default from v4.0; EA `InpCrkT1`): with Final Exit At TP1 (any final exit with *Works With Any Final Exit*), a recovery trade is made bigger: the part set in *% Closed At TP1* (default half) closes at TP1 and banks the whole recovery amount, the stop of the rest moves to the entry and it closes at TP2; the default stop sits where a stop-out loses exactly the recovery amount (% × TP1 − (1 + %) × costs: 0.3R with half, TP1 = 0.6R and no costs; *Stop Before TP1* can widen it, e.g. to the normal stop). While that half runs on, new signals are skipped. On gold 2021–2026 the tight stop was hit on 75% of these trades, so it lost money: see the workbook before using it. **Gold 2021–2026, 25 profitable settings, $500 cap with Start again**: Crooks C made more than fixed $50 on 18 and Crooks D on 21 (Crooks A on 20), but the profit per $ of drawdown was better on only 5 (C) and 6 (D) (A: 10); without a cap Crooks D blew the account on 5 settings (M1, M5, M15). |

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
