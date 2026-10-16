# VWAP Orderflow Sniper [Absorption + Aggression]

A TradingView indicator (Pine Script v6) built on top of TradingView's built-in **VWAP** indicator. The original VWAP, anchor periods and the three bands work exactly as before. On top of them it adds orderflow-based **BUY / SELL signals** with **Entry / Stop Loss / Target boxes**.

File: [`VWAP_Orderflow_Sniper.pine`](VWAP_Orderflow_Sniper.pine)

## Install

1. In TradingView, open **Pine Editor**, then choose **Open → New blank indicator**.
2. Delete everything in the editor, then paste the full contents of `VWAP_Orderflow_Sniper.pine`.
3. Click **Save**, then **Add to chart**.
4. The symbol needs volume data. Forex/CFD gold such as `OANDA:XAUUSD` provides tick volume, which works. Symbols without volume show the original *"No volume is provided"* error.

## Signal logic

| Step | What it means | Chart output |
|---|---|---|
| **VWAP side** | Buys only when the candle closes **above** VWAP, sells only when it closes **below** VWAP. | Dashboard: *ABOVE ▲ BUYS ONLY* / *BELOW ▼ SELLS ONLY* |
| **Delta** | Aggressive buy volume minus aggressive sell volume. Read from lower-timeframe intrabars (1m on intraday charts). If no intrabar data exists, it is estimated from the candle. | Dashboard: Bar Delta, Session CVD |
| **Absorption** | High effort with a low result: heavy volume that fails to move price. Four detectors: rejection wick on high volume, delta against the candle, churn (huge volume with a tiny range at a local extreme), and delta divergence over N bars. It must happen at VWAP or Band #1. | **Pre Buy / Pre Sell Warning** bubble + absorption zone box |
| **Aggression** | Initiative market orders. One side trades at least *Aggression Ratio* × the other side, on a full-bodied candle with at least average volume. | — |
| **Signal** (Sniper mode) | An armed absorption setup, followed by aggression in the same direction, on the correct VWAP side, after the filters (CVD, distance from VWAP, optional VWAP slope, optional session). | **Buy / Sell Bubble**, trade boxes, signal label |

Other signal modes: **Aggression Only** (no absorption needed) and **Absorption Breakout** (a close beyond the absorption zone).

Signals are confirmed on bar close by default (*Confirm On Bar Close*), so they do not repaint.

## Settings

**INSTITUTIONAL FLOW SETTINGS** (same three inputs as the reference screenshot)
- **Aggression Ratio** `2.2`: the minimum buy/sell volume ratio for an aggressive candle.
- **Absorption Sensitivity** `1.2`: the minimum relative volume for absorption. Lower values detect more absorption.
- **Dynamic RR Base** `1.5`: the TP1 reward:risk in *Dynamic RR* mode, scaled up to 1.5× by the signal score (0–100). TP2 = 2× and TP3 = 3× that RR.

**VWAP Settings / Bands Settings**: unchanged from the built-in VWAP.

**TRADE LEVELS (ENTRY / STOP / TARGET)**: all levels can be set manually.
- Entry: *Signal Close*, *Signal Bar Midpoint* (limit) or *VWAP Retest* (limit), plus an optional offset.
- Stop Loss: *Absorption / Swing* (beyond the absorption zone + an ATR buffer, clamped between min and max ATR), *ATR*, *Fixed Points*, or *Percent*.
- Targets: *Dynamic RR*, *Fixed RR* (TP1/TP2/TP3), or *Fixed Points* (TP1/TP2/TP3), with 1–3 targets.
- Stop management: *None*, *Breakeven after TP1*, or *Step Trail* (BE after TP1, then TP1 after TP2).

**BUY / SELL BOX SETTINGS**
- Fill and border colours for the buy box (target / stop) and the sell box (target / stop).
- Border width and border style (solid, dashed, dotted).
- Box length (this is also the maximum trade duration), cutting boxes at the exit bar, price text inside boxes, and text colour and size.
- Absorption zone boxes (bull/bear colours and length).

**SIGNAL LABELS**: a BUY/SELL label with score, Entry, SL and TPs. Hover over it for aggression ratio, relative volume, delta and risk. The result (✓ TP hit / ✗ SL / ⌛ time exit) is added to the label when the trade closes.

**Style tab**: Buy Bubble, Sell Bubble, Pre Buy Warning and Pre Sell Warning (colour, shape, location), VWAP and bands, plus Boxes / Labels / Tables visibility.

**DASHBOARD**: VWAP, price side, bar delta, session CVD, aggression, absorption, setup state, relative volume, delta feed, the open trade, signal count, win rate (TP1 reached vs. stop hit) and TP1/TP2/TP3 hit counts.

## Alerts

- Fixed alerts: **Buy Signal**, **Sell Signal**, **Pre Buy Warning**, **Pre Sell Warning**.
- Full trade plan: create an alert with **Any alert() function call** to get `BUY XAUUSD [5] Entry … | SL … | TP1 … | TP2 … | TP3 … | Score …`.

## Notes

- Pine Script cannot read real footprint or bid/ask data on most plans. Delta here is built from lower-timeframe intrabars (or a candle estimate), which is the standard approximation for orderflow in Pine.
- Intrabar data is limited to 100,000 lower-timeframe bars. Older chart bars fall back to the candle estimate automatically, and the dashboard shows which feed is active.
- The win-rate statistics are a rough guide: stops are checked before targets inside the same candle. Use them to tune settings, not as a backtest.
- For educational use only. This is not financial advice.
