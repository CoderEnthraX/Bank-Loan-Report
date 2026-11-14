# Fractal Breakout Grid v2: added settings (2026-11-15). Everything in SPEC.md still holds; all new settings are off by default
# except the money management (sizing only: it never changes a trade, except "Stop trading" and a blown account, which end the trades).

## A. Filters on a breakout (all off by default)

A breakout (SPEC section 4) that a filter does not allow is skipped: no trade opens and the buy stop is used up, exactly like a
breakout while a trade is open. The filters are read on the chart bar where the breakout happens.
1. Days: when "Trade only on the ticked days" is on, the bar's day of week in the chosen time zone must be ticked.
2. Hours: when "Trade only between" is on, the bar's open time must be inside the session (start inclusive, end exclusive) in the chosen
   time zone (Pine: not na(time(timeframe.period, session, tz))).
3. Trend: when on, the last completed candle of the trend timeframe (the candle before the one containing the bar) closed above its
   EMA(length) (EMA seeded with the first close: e = close on the first candle, then e = a close + (1 - a) e, a = 2 / (length + 1)).
4. Weekend: when the weekend close is on, no breakout is allowed on bars that open on Friday at or after the set hour (New York time).
5. Most entries per day (0 = no limit): the strategy's entries counted per day in the chosen time zone.
6. A strategy stopped by the hard cap ("Stop trading") or with a blown account (equity <= 0) takes no more trades.

## B. Buy stop expiry (0 = never)

The pending buy stop is dropped at the first chart bar of fractal-TF candle kAct + N, where kAct is the candle where it became active
(checked after a new swing high is set, before the open is processed).

## C. Entry on a candle close (instead of the buy stop)

The buy stop is armed by a chart candle that closes below E (the activation bar included). After that, the first chart candle that
closes at or above E is the breakout: the trade fills at that close (if allowed and flat; the level is used up either way). The exits
start on the next bar. No gap or in-candle breakouts in this mode.

## D. Exits added

At the open of a bar, in this order (all at the open price): (a) trailing update, (b) TP / SL gaps (as before), (c) time exit,
(d) weekend close, then BE / salvage at the open and the gap entry as before.
1. Trailing stop (distance 0 = off): hi = the highest price since the fill (the fill included). Once hi >= F (1 + start %), the SL
   becomes max(SL, hi (1 - distance %)). The SL is updated at the open (with the highest price before the open) and at the start of every
   down segment; hi grows at the end of every up segment and with the open. An SL hit after the trail raised it is a TRAIL exit.
   The BE trigger sets the SL to max(SL, F).
2. Time exit (hours, 0 = off): at the open of the first bar whose open time is at least the entry bar's open time + hours.
3. Weekend close: at the open of the first bar that opens on Friday at or after the set hour (New York time).
Exit reasons: TP, SL, BE, SALV, TRAIL, TIME, WKND.

## E. Money management (per strategy, its own account)

Every strategy has its own account: start balance (default $10,000) and base risk (default $50). The rules are those of the Auction
Retest strategy / EA (`gold/recovery.py`, `simulate`), applied to the strategy's trades in order:
- At an entry, the rule gives the $ risk r for this trade (including the hard cap and the leverage limit).
  units = r / (SL distance + costs), where SL distance = F x SL % / 100 and costs = the costs per trade (price units).
- At the exit, P&L $ = units x (exit price - F - costs). It updates the rule's state as `simulate` does after a trade.
- Per trade, recovery.py sees res = (exit - F) / SL distance, c = costs / SL distance, exitR = TP % / SL %, leverage limit
  LEV x (SL distance + costs) / F (risk per $1 of equity; LEV = 100), and the Crooks E / I lot risk = lot x contract size x (SL distance + costs).
- Modes: the 28 of `recovery.MODES`, with the Crooks C options "over N wins" (cN) and "after N losing recovery trades": forget / % / wait
  (the "skip days" option is not offered). Profit ladder for Crooks F - J. Hard cap: clamp / start again / stop trading.
- Only trades that open at or after the table's start date are booked (the account starts with the first of them).
- The next trade's risk and lots (units / contract size, rounded to the lot step, at least one step) are shown for the waiting buy stop.
