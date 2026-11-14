# Fractal Breakout Grid: trade rules (v1, 2026-11-14)

Long only. Every strategy runs on its own (its own level, its own position) on the bars of the chart (the "chart bars").
A strategy has: fractal timeframe TF, Right (candles after the swing high), Left (candles before it), buy entry offset (%),
SL (%), TP (%), BE trigger (%), salvage trigger (%). BE trigger 0 or salvage trigger 0 = off.

## 1. Swing high (fractal) on the fractal timeframe

Candles of TF: c = 0, 1, 2, ... with highs Hf[c].
Candle p is a swing high when Hf[p] > Hf[p - i] for every i = 1..Left AND Hf[p] > Hf[p + j] for every j = 1..Right
(strictly higher on both sides; equal highs disqualify). It needs Left candles before it (p >= Left).

It is confirmed when candle p + Right closes, so it is ACTIVE from TF candle k = p + Right + 1 on (if that candle exists).
On the chart: from the first chart bar that belongs to TF candle k (a chart bar belongs to the TF candle whose time bucket contains the
chart bar's start time).

## 2. The level

When a swing high becomes active (at the first chart bar of TF candle k), it becomes the strategy's pending level, replacing any older
pending level (whether or not a trade is open):
  level H = Hf[p],  entry price E = H * (1 + offset / 100)        (offset -0.14 -> E is 0.14 % below the swing high).
The bar on which a level becomes active is its "activation bar".

A pending level is used up by its first breakout (section 4): a trade opens if the strategy has no open trade, otherwise the breakout
is skipped. Either way the level is gone. Only a newer swing high gives a new level.

## 3. Price path inside a chart bar

Every chart bar (open o, high h, low l, close c) is processed as the path
  o -> a -> b -> c,  where a = h and b = l when (h - o) < (o - l), else a = l and b = h   (a tie goes to the low first).
So the bar has 3 segments: (o -> a), (a -> b), (b -> c). Before them comes the jump from the previous bar's close to o (the open).

## 4. Order of processing in a bar

Step 0. If the bar is the first chart bar of a new TF candle and a swing high becomes active there: set the pending level (section 2),
        mark this bar as its activation bar.

Step 1. The open (o):
  a. If a trade is open:
       if o >= TP price: exit at o  (reason TP, or SALV when the salvage moved the TP)
       else if o <= SL price: exit at o  (reason SL, or BE when the BE moved the SL)
       else: if BE is on, neither BE nor salvage happened yet and o >= BE trigger price: BE happens (SL price = entry price)
             else if salvage is on, neither happened yet and o <= salvage trigger price: salvage happens (TP price = entry price)
  b. If a level is pending, this is NOT its activation bar, the previous bar's close < E and o >= E: breakout at the open.
       If no trade is open (also when one just closed in 1a): open a trade at fill price o. The level is used up either way.

Step 2. The three segments in order. For each segment from x to y:
  Up-move (y > x): repeat until nothing is left:
     candidates (each strictly above x and at or below y):
       - TP price (if a trade is open)                                              -> exit at the TP price
       - BE trigger price (if a trade is open, BE on, neither BE nor salvage yet)   -> BE happens (SL price = entry price)
       - E (if a level is pending)                                                  -> breakout at E: open a trade at fill E if
                                                                                       none is open (else skip); level used up
     take the LOWEST candidate price; at equal prices: TP first, then BE, then the breakout. Apply it and repeat
     (the bounds stay x < price <= y; an applied event cannot repeat).
  Down-move (y < x): repeat until nothing is left:
     candidates (each at or above y and strictly below x):
       - SL price (if a trade is open)                                              -> exit at the SL price
       - salvage trigger price (if a trade is open, salvage on, neither yet)        -> salvage happens (TP price = entry price)
     take the HIGHEST; at equal prices the SL first.
  Flat segment (y == x): nothing.

Step 3. Remember c as the previous close.

## 5. A trade

Opened at fill price F (E on the path, or o at the open). Then
  SL price = F * (1 - SL / 100),   TP price = F * (1 + TP / 100),
  BE trigger price = F * (1 + BE / 100),   salvage trigger price = F * (1 - salvage / 100).
BE: once the price reaches the BE trigger price, the SL price becomes F (break-even). Salvage: once the price falls to the salvage trigger
price, the TP price becomes F (exit at break-even when the price comes back). Only the first of the two can happen in a trade.
Exit reasons: TP, SL, BE (stopped at F after the BE), SALV (exited at F after the salvage).
One trade at a time per strategy. A trade still open at the end of the data is not counted.

## 6. Results

Cost per trade (round trip, price units, default 0.23 = gold spread 0.16 + $7 commission per lot of 100 oz):
  P&L = exit price - F - cost;  % = P&L / F * 100;  R = P&L / (F * SL / 100).
A trade is a win when P&L > 0.

## 7. Clock (gold, TradingView)

Times are New York time + 7 h. TF buckets: start = floor(t / seconds) * seconds with M5 300, M15 900, H1 3600, H4 14400, D1 86400
(the daily candle starts at 17:00 New York, the 4 h candles at 17:00 / 21:00 / 01:00 / ... New York).
