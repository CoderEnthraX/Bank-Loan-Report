//+------------------------------------------------------------------+
//| AuctionRetestEA.mq5                                              |
//| MetaTrader 5 port of the TradingView "Auction Retest" model and  |
//| strategy (v3).                                                   |
//|                                                                  |
//| SAME SIGNALS AS THE TRADINGVIEW FILES: ProcessBar() is a line-by- |
//| line port of the shared ENGINE block of Auction_Retest_Model.pine |
//| and Auction_Retest_Strategy.pine. It decides every setup, fill,   |
//| stop move and exit from closed bars only. The execution part      |
//| copies those decisions into broker orders and never feeds back    |
//| into them, so broker fills cannot change the signals.            |
//|                                                                  |
//| Differences from TradingView that come from the platform:        |
//|  - The broker's own bars and tick volume are used (other feed).  |
//|  - The trading day / VWAP reset is the broker's server midnight. |
//|  - Charts are BID: with "Match bid-chart levels" on, buy limits   |
//|    and short stops/targets are shifted by the live spread so they |
//|    trigger at the same bid levels the engine uses.               |
//|  - Lot size, tick value and volume step come from the broker.    |
//|  - Partials close at market when price reaches the target.       |
//|                                                                  |
//| v3.1: optional filters (half-stop cap, choppy-session VWAP-cross |
//| gate, 1h EMA20 speed gate; all off), on-chart table with target  |
//| and breakeven statistics, trade markings (entry, stop, targets,  |
//| result). Use "Visualization" in the Strategy Tester to see them. |
//| v3.2: optional kill zones (Indian time, four sessions, +-2 h).   |
//| v3.3: optional minimum distance of the signal from the VWAP.     |
//| v3.4: Crooks A and Crooks B loss recovery.                       |
//| v3.5: Crooks at exit TP1: half banks the loss, rest runs to TP2. |
//| v3.6: Crooks C and D; optional max distance from the VWAP.       |
//| v3.7: TP1-rule stop choices, Crooks C over N wins, lot rounding. |
//| v3.7.1: server clock option for EU summer time (e.g. FxPro).     |
//| v3.8: VWAP skip rules (stop beyond / touched / entry too close), |
//| kill zones and daily news follow summer time, TP1 rule % and     |
//| any final exit.                                                  |
//| v3.9: Crooks C rule after N losing recovery trades in a row:     |
//| forget the loss, a % of it, wait for M wins, or skip D days.     |
//| v4.0: defaults = the TradingView strategy's v4.0 defaults (gold, |
//| FxPro): Tue-Thu 06:00-23:00 IST in the Asia / London / New York  |
//| kill zones, exit TP1, Crooks C, news 17:45-18:15 IST,            |
//| force-close 23:55, server clock EU summer time, max 10 fills,    |
//| half-stop cap.                                                   |
//| New Spread input: the costs (sizing, earn-back) use 0.16 like    |
//| TradingView, so lots and target levels match it (0 = live).      |
//| v4.1 (EA only): Crooks C hedge rule: after N losing recovery     |
//| trades in a row, the next signal opens a buy and a sell at the   |
//| same entry (hedging account), with their own stop loss and take  |
//| profit; then forget the loss, or go on from the last trade.      |
//| v4.2: MONTHLY PROFIT LOCK (same as the TradingView strategy):    |
//| stop for the month once it is up $X; lock a % of the month's     |
//| profit once it is up $Y; restart the loss recovery on the 1st.   |
//| v4.3: RESTART MEMORY: the loss recovery, streaks, pauses and the |
//| open trade go on after MT5 or the EA restarts (MT5 global        |
//| variables; trades that closed meanwhile are booked).             |
//| v4.4: no early closes: the take profit goes to the broker with   |
//| the order, and a trade the engine stops following runs to its    |
//| own stop loss and take profit. Trades closed by hand, the phone  |
//| app or another EA are booked with their real profit; the log     |
//| says who closed each trade and why. One copy per symbol and      |
//| magic number. The broker server clock is read from MT5 (Auto).   |
//+------------------------------------------------------------------+
#property copyright "Auction Retest Model"
#property version   "4.40"
#property description "VWAP displacement + retest EA (same engine as the TradingView indicator/strategy) with money management."

#include <Trade/Trade.mqh>

//--- enums
enum ENUM_ENTRY_MODE { ENTRY_MODEL = 0,   // Model (body mid or 6-bar level)
                       ENTRY_PCT   = 1,   // Custom % of signal candle
                       ENTRY_MARKET = 2 };// Market (next bar open)
enum ENUM_EXIT_AT { EXIT_TP1 = 1, EXIT_TP2 = 2, EXIT_TP3 = 3, EXIT_TP4 = 4 };
enum ENUM_REARM { REARM_KEEP = 0,  // Keep first
                  REARM_NEW  = 1 };// Replace with newer
enum ENUM_STOP_MODE { STOP_ATR = 0,    // ATR model
                      STOP_SWING = 1 };// Swing + buffer (ATR capped)
enum ENUM_CAP_ACTION { CAP_CLAMP = 0,  // Clamp risk to the cap
                       CAP_STOP  = 1,  // Stop trading
                       CAP_RESET = 2 };// Start again from the base risk
enum ENUM_VW_UNIT { VWU_ATR   = 0,  // x ATR
                   VWU_PRICE = 1 };// Price
enum ENUM_T1_STOP { T1S_TIGHT = 0,   // Tight: % x TP1 (TP1 / 2 at 50%; a stop-out loses the amount)
                    T1S_K45   = 1,   // 0.45R
                    T1S_K60   = 2,   // 0.6R
                    T1S_FULL  = 3,   // Normal stop
                    T1S_FILL  = 4,   // Normal stop on the entry candle, then tight
                    T1S_PT    = 5,   // Normal stop, tight after a candle closes in profit
                    T1S_PBE   = 6 }; // Normal stop, breakeven after a candle closes in profit
enum ENUM_LOT_ROUND { LOTR_DOWN = 0,  // Down (never risks more)
                      LOTR_NEAR = 1 };// To the nearest lot step
enum ENUM_SMALL_LOT { SMALLL_MIN  = 0,  // Trade the minimum lot (risks more)
                      SMALLL_SKIP = 1 };// Skip the trade
enum ENUM_REC {
   REC_OFF   = 0,  // Off
   REC_ALL   = 1,  // Recover all losses on the next trade
   REC_SPLIT = 2,  // Recover losses over N trades
   REC_PART  = 3,  // Recover a % of losses per trade
   REC_MART  = 4,  // Martingale (multiply after each loss)
   REC_EXACT = 5,  // Exact recovery at final TP
   REC_STEP  = 6,  // Step-up (+$ per loss in a row)
   REC_FIB   = 7,  // Fibonacci (1,1,2,3,5... x base)
   REC_DALE  = 8,  // D'Alembert (+1 unit per loss, -1 per win)
   REC_C     = 9,  // Rule C: carry the losses
   REC_CS    = 10, // Rule C split: carry losses + base grows with profit
   REC_LAB   = 11, // Labouchere (cancellation 1-2-3)
   REC_GMART = 12, // Grand Martingale
   REC_PAR   = 13, // Paroli (double after wins, reset after N)
   REC_RDALE = 14, // Reverse D'Alembert
   REC_DELAY = 15, // Delayed recovery (after N losses)
   REC_EQPCT = 16, // % of equity
   REC_OSC   = 17, // Oscar's Grind
   REC_CRA   = 18, // Crooks A (base, base, then recovery every 2nd trade)
   REC_CRB   = 19, // Crooks B (Crooks A with the loss split over N trades)
   REC_CRC   = 20, // Crooks C (base until a win, then one recovery trade)
   REC_CRD   = 21  // Crooks D (base, base, recovery: every 3rd trade)
};
enum ENUM_CRK_PR { CPR_OFF    = 0,   // Off (Crooks C as now)
                   CPR_FORGET = 1,   // Forget the loss
                   CPR_PCT    = 2,   // Go for a % of the loss, forget it after N
                   CPR_WAIT   = 3,   // Wait for M wins in a row, then a loss and a win
                   CPR_SKIP   = 4,   // Skip D trading days
                   CPR_HEDGE  = 5 }; // Hedge: a buy and a sell on the next signal (hedging account)
enum ENUM_HG_UNIT { HGU_R     = 0,   // R (x the signal's stop distance)
                    HGU_PRICE = 1 }; // Price (e.g. 5.0 = $5 on gold)

//--- ENGINE inputs: same names, order and defaults as the shared Pine inputs
input group "SIGNAL MODEL (same as the indicator)"
input int    InpStructLen    = 10;    // Structure lookback (bars)
input int    InpBrkLen       = 6;     // Signal break lookback (bars)
input int    InpEntryLen     = 6;     // Entry level lookback (bars)
input int    InpRetestBars   = 5;     // Retest window (bars)
input double InpDispAtr      = 0.8;   // Min displacement range (x ATR)
input double InpBodyPct      = 55.0;  // Min displacement body (% of range)
input double InpClosePct     = 25.0;  // Max close distance from extreme (% of range)
input int    InpMomLen       = 10;    // Momentum lookback (bars)
input double InpMomAtr       = 0.85;  // Min momentum (x ATR, 0 = off)
input double InpCmoMin       = 20.0;  // Min CMO, clean move (0 = off)
input ENUM_REARM InpRearm    = REARM_KEEP; // Same-direction re-arm
input ENUM_STOP_MODE InpStopMode = STOP_ATR; // Stop mode
input double InpStopAtr      = 1.8;   // Stop distance (x ATR)
input int    InpStopLen      = 6;     // Swing lookback (bars)
input double InpStopBufAtr   = 0.22;  // Swing buffer (x ATR)
input bool   InpHalfStop     = true;  // Half stop on first counter-bias impulse
input double InpHalfStopAtr  = 0.9;   // Half stop (x ATR)
input int    InpBiasNet      = 3;     // Prev session net impulses
input double InpImpBody      = 50.0;  // Impulse min body (% of range)
input bool   InpHalfOpenOut  = true;  // Half stop when session opens outside prev range
input bool   InpHalfStrict   = false; // Strict bias check (optional)
input bool   InpHalfCap      = true;  // Half stop never wider than the normal stop (optional)
input int    InpCooldown     = 1;     // Cooldown after exit (bars)
input int    InpMaxFills     = 10;    // Max fills per day
input double InpDayStopR     = 0.0;   // Daily stop (R lost, 0 = off)
input bool   InpFillBarStopR = false; // Count fill-bar stops in daily stop
input bool   InpLegReset     = true;  // Re-anchor breakout after a trade
input int    InpAtrLen       = 14;    // ATR length (Wilder / RMA)
input bool   InpVwapFilter   = true;  // Longs above VWAP / shorts below
input int    InpSlopeBars    = 3;     // VWAP slope bars (0 = off)
input bool   InpSlopeCross   = true;  // Slope looks across the session start
input int    InpMinOpenBars  = 0;     // Skip first bars after the daily reset
input bool   InpSkipSunday   = true;  // Skip Sunday (UTC) weekly open
input bool   InpDeepOn       = false; // Deep pullback signal (optional)
input double InpDeepFar      = 2.0;   //   min depth (x ATR)
input bool   InpAllowLong    = true;  // Longs
input bool   InpAllowShort   = true;  // Shorts

enum ENUM_VW_ANCHOR { VW_SESSION = 0, // Session
                      VW_WEEK    = 1, // Week
                      VW_MONTH   = 2 };// Month
input group "VWAP"
input ENUM_VW_ANCHOR     InpVwapAnchor = VW_SESSION;    // Anchor
input ENUM_APPLIED_PRICE InpVwapSrc    = PRICE_TYPICAL; // Source (typical = hlc3)

input group "ENTRY PRICE"
input ENUM_ENTRY_MODE InpEntryMode = ENTRY_MODEL; // Entry price
input double InpEntryPct     = 25.0;  // Custom % (0 = close, 50 = mid, 100 = low/high)

input group "TARGETS, EXIT AND STOP MOVES"
input double InpTp1R = 0.6;  // TP1 (R)
input double InpTp2R = 1.0;  // TP2 (R)
input double InpTp3R = 1.5;  // TP3 (R)
input double InpTp4R = 2.0;  // TP4 (R)
input ENUM_EXIT_AT InpExitAt = EXIT_TP1; // Final exit at
input bool   InpMv1On = false; // When TP1 hits, move stop
input double InpMv1R  = 0.0;   //   ...to (R, 0 = breakeven)
input bool   InpMv2On = false; // When TP2 hits, move stop (breakeven at +1R: on, 0)
input double InpMv2R  = 0.6;   //   ...to (R)
input bool   InpMv3On = false; // When TP3 hits, move stop
input double InpMv3R  = 0.0;   //   ...to (R)

input group "ACCURACY FILTERS (research, off = original)"
input bool   InpNoChase    = false; // Don't chase: skip signals beyond N sigma from VWAP
input double InpNoChaseSig = 2.0;   //   sigma from VWAP
input bool   InpLossBlock  = false; // After a loss, no same-direction trade until a win
input bool   InpChopOn     = false; // Skip choppy sessions (too many VWAP crosses)
input double InpChopMax    = 13.5;  //   max VWAP crosses per 100 bars
input bool   InpEmaOn      = false; // Skip when the 1h EMA20 moved too fast (natural gas: worse)
input double InpEmaMax     = 1.65;  //   max 1h EMA20 move in 3 hours (x ATR)
input bool   InpMinVwOn    = false; // Skip signals too close to VWAP (min distance)
input double InpMinVwAtr   = 1.0;   //   min distance of the signal close from VWAP (x ATR)
input bool   InpMaxVwOn    = false; // Skip signals too far from VWAP (max distance)
input double InpMaxVwDist  = 5.0;   //   max distance of the signal close from VWAP, above or below
input ENUM_VW_UNIT InpMaxVwUnit = VWU_ATR; //   ...measured in ATR or in price
input bool   InpStopVwOn   = false; // Skip when the stop is beyond the VWAP
input double InpStopVwBuf  = 0.0;   //   buffer (x ATR; 0 = stop on the trade's side, -1 = up to 1 ATR past it)
input bool   InpTouchVwOn  = false; // Skip when the VWAP was touched in the last N candles
input int    InpTouchVwN   = 3;     //   N candles (1 = the signal candle only)
input bool   InpEntVwOn    = false; // Skip when the entry is too close to the VWAP
input double InpEntVwAtr   = 0.75;  //   min distance of the entry from the VWAP (x ATR)

input group "DAYS AND HOURS (YOUR time zone)"
enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1,   // Fixed: the GMT offset below
                   SRV_EET     = 2,   // GMT+2 winter / GMT+3 EU summer time (EET brokers, e.g. FxPro)
                   SRV_AUTO    = 3 }; // Auto: read the broker's clock from MT5 (Strategy Tester: EU summer time)
input ENUM_SRV_TZ InpServerTz = SRV_AUTO;    // Broker server clock
input double InpServerGMT = 2.0;   // Broker server time zone if fixed (GMT +h; check Market Watch time)
input double InpUserGMT   = 5.5;   // Your time zone (GMT +h; India = 5.5)
input bool   InpDayOn     = true;  // Trade only on the ticked days
input bool   InpMon       = false; //   Monday
input bool   InpTue       = true;  //   Tuesday
input bool   InpWed       = true;  //   Wednesday
input bool   InpThu       = true;  //   Thursday
input bool   InpFri       = false; //   Friday
input bool   InpSat       = false; //   Saturday
input bool   InpSun       = false; //   Sunday
input bool   InpHoursOn   = true;  // Trade only between
input int    InpStartH    = 6;     //   start hour
input int    InpStartM    = 0;     //   start minute
input int    InpEndH      = 23;    //   end hour
input int    InpEndM      = 0;     //   end minute
enum ENUM_KZ_SHIFT { KZ_M2 = -2,  // -2 hours
                     KZ_M1 = -1,  // -1 hour
                     KZ_0  = 0,   // 0 (as listed)
                     KZ_P1 = 1,   // +1 hour
                     KZ_P2 = 2 }; // +2 hours
input bool   InpKzOn      = true;  // Trade only in kill zones (Indian time, IST)
input bool   InpKzAsia    = true;  //   Asia 05:30-09:30 IST
input bool   InpKzLon     = true;  //   London 11:30-14:30 IST (UK winter time: 1 hour later with the switch below)
input bool   InpKzNy      = true;  //   New York 16:30-19:30 IST (US winter time: 1 hour later with the switch below)
input bool   InpKzLc      = false; //   London close 19:30-21:30 IST (UK winter time: 1 hour later with the switch below)
input bool   InpKzAuto    = true;  //   follow London / New York summer time (winter: those zones 1 hour later)
input ENUM_KZ_SHIFT InpKzShift = KZ_0; //   shift all kill zones (on top of the summer time switch)

//--- EXECUTION inputs (EA only)
input group "PARTIAL PROFITS (EA only)"
input double InpP1   = 0.0;  // Close % at TP1 (0 = no partial)
input double InpP2   = 0.0;  // Close % at TP2
input double InpP3   = 0.0;  // Close % at TP3

input group "RISK AND POSITION SIZE"
input double InpBaseRisk = 50.0;   // Base risk per trade (account currency)
input bool   InpCapOn    = false;  // Hard cap: max loss per trade
input double InpHardCap  = 250.0;  // Hard cap amount
input ENUM_CAP_ACTION InpCapAction = CAP_RESET; // If the risk would exceed the cap
input double InpLeverage = 100.0;  // Leverage cap 1:x (0 = broker margin only)
input double InpLotStep  = 0.0;    // Lot step (0 = broker's volume step)
input ENUM_LOT_ROUND InpLotRound = LOTR_DOWN;  // Lot rounding (nearest: 0.125 -> 0.13; never past the hard cap or leverage)
input ENUM_SMALL_LOT InpSmallLot = SMALLL_MIN; // Size below the minimum lot (e.g. 0.004 -> 0.01)

input group "COMMISSION AND BID/ASK"
input double InpSpread   = 0.16;   // Spread for sizing and earn-back (price, like TradingView's Spread; 0 = the live spread)
input double InpCommLot  = 7.0;    // Commission per lot, round trip (sizing / earn-back; FxPro gold: 7)
input bool   InpEarnBack = true;   // Extend targets to earn back commission + spread
input bool   InpBidChart = true;   // Match bid-chart levels (shift buy-side orders by the spread)

input group "STREAKS AND PAUSES"
input bool InpLStopOn = false; // Stop for the day after N losses in a row
input int  InpLStopN  = 23;    //   N losses
input bool InpWStopOn = false; // Stop for the day after N wins in a row
input int  InpWStopN  = 3;     //   N wins
input bool InpPauseOn = false; // Pause after N losses in a row
input int  InpPauseN  = 3;     //   N losses
input int  InpPauseDays = 1;   //   Days to pause (1-3)

input group "MONTHLY PROFIT LOCK"
input bool   InpMLockOn  = false;  // Stop for the month once it is up (closed profit this month, your time zone)
input double InpMLockAmt = 150.0;  //   amount (account currency)
input bool   InpPLockOn  = false;  // Lock profit once the month is up (stop when it falls back to the locked part)
input double InpPLockAt  = 500.0;  //   amount (account currency)
input double InpPLockPct = 20.0;   //   lock % of the month's highest profit (rises with new highs)
input bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (after a trade still open closes)

input group "RESTART MEMORY"
input bool   InpRemember = true;   // Continue after a restart (keep the loss recovery, streaks and pauses when MT5 or the EA restarts)
input bool   InpMemFresh = false;  // Start fresh once: forget the loss recovery, streaks and pauses (true + OK; set false again later)

input group "FORCE-CLOSE, WEEKEND AND NEWS (YOUR time zone)"
input bool   InpFcOn      = true;  // Force-close open trades daily at
input int    InpFcH       = 23;    //   hour
input int    InpFcM       = 55;    //   minute
input bool   InpWeekendOn = true;  // Close open trades when Saturday starts
input int    InpNewsPre   = 60;    // No new trades before news (minutes)
input bool   InpDNewsOn   = true;  // Daily news window
input int    InpDNewsH    = 17;    //   start hour
input int    InpDNewsM    = 45;    //   start minute
input int    InpDNewsDur  = 30;    //   length (minutes)
input bool   InpDNewsAuto = true;  //   keep the same New York time all year (US winter time: 1 hour later)
input bool     InpN1On = false;        // News 1
input datetime InpN1T  = D'2026.01.01 23:30'; //   date and time (your time zone)
input int      InpN1Dur = 60;          //   length (minutes)
input bool     InpN2On = false;        // News 2
input datetime InpN2T  = D'2026.01.01 23:30'; //   date and time
input int      InpN2Dur = 60;          //   length (minutes)
input bool     InpN3On = false;        // News 3
input datetime InpN3T  = D'2026.01.01 23:30'; //   date and time
input int      InpN3Dur = 60;          //   length (minutes)
input bool     InpN4On = false;        // News 4
input datetime InpN4T  = D'2026.01.01 23:30'; //   date and time
input int      InpN4Dur = 60;          //   length (minutes)
input bool     InpN5On = false;        // News 5
input datetime InpN5T  = D'2026.01.01 23:30'; //   date and time
input int      InpN5Dur = 60;          //   length (minutes)

input group "LOSS RECOVERY"
input ENUM_REC InpRec    = REC_CRC; // Loss recovery
input int    InpRecN     = 3;      // N trades (Over N / Delayed)
input double InpRecPct   = 50.0;   // % of losses (% mode)
input double InpRecMult  = 2.0;    // Multiplier (Martingale / Grand)
input double InpRecStep  = 25.0;   // Step amount (Step-up)
input int    InpCSplit   = 2;      // Rule C / Crooks B: split the loss over this many trades
input bool   InpCrkT1    = false;   // Crooks TP1 rule (exit TP1): bank the loss at TP1 with part, rest to TP2
input ENUM_T1_STOP InpCrkT1Stop = T1S_FULL; //   ...stop before TP1 (the size is the same; the hard cap covers the real stop-out loss)
input double InpCrkT1Pct = 50.0;   //   ...% closed at TP1 (10-90; that part alone banks the whole loss)
input bool   InpCrkT1Any = false;  //   ...with any final exit (not only TP1; the rest still runs to TP2)
input bool   InpCrkCnOn  = false;  // Crooks C: win the loss back over N wins
input int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)
input ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C: after N losing recovery trades in a row
input int    InpCrkPrN   = 2;      //   ...N losing recovery trades in a row
input double InpCrkPrPct = 50.0;   //   ...% of the loss each recovery trade goes for (the % rule, 10-100)
input int    InpCrkPrM   = 2;      //   ...M wins in a row to wait for (the wait rule)
input int    InpCrkPrD   = 4;      //   ...D trading days to skip (the skip rule; the rest of that day is skipped too)
input bool   InpCrkPrForget = false; //   ...forget the loss after the skipped days (the skip rule)
input bool   InpCrkPrAll = false;  //   ...count every day, not only the trading days (the skip rule)
input double InpCrkHgSl  = 1.0;    //   ...hedge rule: stop loss of the buy and the sell (R: 1 = the signal's own stop)
input double InpCrkHgTp  = 0.6;    //   ...hedge rule: take profit of the buy and the sell (R: 0.6 = TP1)
input ENUM_HG_UNIT InpCrkHgUnit = HGU_R; //   ...hedge rule: stop loss and take profit in R or in price
input bool   InpCrkHgForget = true; //   ...hedge rule: forget the loss after the pair (off: Crooks C goes on from the trade that closed last)
input int    InpParN     = 3;      // Paroli: wins before reset
input int    InpDelayN   = 2;      // Delayed: losses before recovery starts
input double InpEqPct    = 1.0;    // % of equity (% mode)

enum ENUM_TBL_POS { TBL_TOP_RIGHT    = 0,  // Top right
                    TBL_TOP_LEFT     = 1,  // Top left
                    TBL_BOTTOM_RIGHT = 2,  // Bottom right
                    TBL_BOTTOM_LEFT  = 3 };// Bottom left
input group "DISPLAY (chart and Strategy Tester visualization)"
input bool   InpDraw      = true;              // Show trade markings (entry, stop, targets, result)
input int    InpMaxDrawn  = 0;                 //   trades kept on the chart (0 = all)
input color  InpColTarget = clrMediumSeaGreen; //   target box and TP lines
input color  InpColStop   = clrIndianRed;      //   stop box
input color  InpColEntry  = clrDodgerBlue;     //   entry line and armed limit
input bool   InpShowTable = true;              // Show the table
input ENUM_TBL_POS InpTablePos = TBL_TOP_RIGHT;//   table position
input int    InpTableFont = 8;                 //   table font size

input group "GENERAL"
input long   InpMagic    = 240611; // Magic number
input int    InpWarmBars = 3000;   // Bars used to warm up the engine (VWAP / ATR / counters / state)

//--- globals ----------------------------------------------------------
CTrade   trade;
datetime gLastBarTime = 0;
long     bi = -1;                  // bar_index of the last processed (closed) bar
bool     gLive = false;            // false while warming up: no orders

// ENGINE state (names as in the Pine engine)
double   cumPV = 0, cumPV2 = 0, cumW = 0, cumP = 0, cumP2 = 0; int cumN = 0; int vwBars = 0; int sessN = 0;
double   vwHist[];                 // vwap of processed bars, [0] = latest
double   atrV = 0; int atrN = 0; double atrSum = 0;
int      lastDayKey = -1;
int      dayFills = 0, dayW = 0, dayL = 0; double dayR = 0, dayRiskR = 0; int lossDirBlk = 0;
int      bullN = 0, bearN = 0, prevNet = 0; bool havePrev = false;
double   sesO = 0, sesH = 0, sesL = 0, pdH = 0, pdL = 0; bool haveSes = false, havePd = false;
int      st = 0;
long     armBar = -1, fillBar = -1, lastExit = -1, lastFill = -1;
int      lastDir = 0;
double   lim = 0, stp = 0, stp0 = 0, trRisk = 0, t1 = 0, t2 = 0, t3 = 0, t4 = 0, tF = 0;
int      tpHit = 0;
bool     trHalf = false, trGhost = false;
int      trSkip = 0;               // why the setup is a ghost: 1 too far from VWAP, 2 choppy VWAP session, 3 1h EMA20 too fast, 4 too close to VWAP, 5 beyond max VWAP distance,
                                   // 6 stop beyond the VWAP, 7 VWAP touched recently, 8 entry too close to the VWAP
int      totW = 0, totL = 0; double totR = 0;
string   lastRes = "-";
double   bestPx = 0;               // best price after the fill (the fill bar and stop bars add nothing)
int      ghW = 0, ghL = 0; double ghR = 0;   // results the skipped (invisible) trades would have had
// optional filters: VWAP crosses of this VWAP period; 1-hour (UTC) candles built from the bars and their EMA20
int      vxSide = 0, vxN = 0;
int      tchL = 1000000, tchS = 1000000;   // candles since the candle range last reached the VWAP (long side: the low, short side: the high); 0 = this candle
long     hK = -1;                  // hour of the last bar (-1 = none yet)
double   hC = 0, hSum = 0;         // close of the forming hour, sum of the first 20 hourly closes
int      hNum = 0;                 // completed hours
double   hE[4];                    // EMA20 of the last four completed hours, [0] = latest; [k] is valid once hNum >= 20 + k
// accuracy of the shown trades (port of the shared Pine STATS block)
int      tpHitN[4];                // closed trades that reached TP1..TP4 before the stop
int      beN = 0, lkN = 0;         // closed at a stop moved to the entry (breakeven) / into profit
datetime gFirstT = 0;              // first bar the engine processed
// events of the last processed bar (shown setups / trades only)
bool     evArm, evArmL, evFill, evFillL, evExit, evWin, evMove, evTp; double evRes; int evCancel; // 0 none, 1 expired, 2 replaced
bool     gNewDay = false, gDayOk = true, gHourOk = true, gKzOk = true;
bool     gT1Seen = false;          // Crooks TP1 rule: TP1 was reached (on a bar caught up after a disconnect, or the partial close failed) and the TP1 part is still to be booked
int      lastAnchorKey = -1;
datetime gLastDone = 0;            // open time of the last bar the engine processed

// EXECUTION state
int      exState = 0;              // 0 nothing, 1 entry order working, 2 in a position
bool     exL = true;
double   exLots = 0, exRiskAmt = 0, exCostPx = 0, exPnl = 0;
long     exArm = -1;               // engine armBar of the setup the EA took
bool     exSynced = false;         // the broker position is the engine's live trade
bool     gRearm = false;           // re-place the engine's armed setup after a restart / catch-up
bool     gVirt = false;            // entry inside the stops distance: VirtualEntry() enters at market at the level
int      gDayPendN = 0;            // new days on bars caught up after a disconnect or replayed after a restart, not counted yet
datetime gPrevT = 0;               // open time of the bar before the one OnNewBar handles (catch-up aware)
bool     pDone[3];
ulong    lastDeal = 0;
int      sigN = 0, takenN = 0, skipN = 0, missN = 0; string skipWhy = "";
datetime gDrawT = 0; bool gDrawOn = false;
bool     gCanDraw = true;          // false in non-visual testing and optimisation (nothing would be seen)
long     gDrawn[];                 // fill times of the drawn trades, oldest first
string   gStateTxt = "SCANNING";   // table: state line
int      gTblW = -1, gTblH = -1;   // chart size the table was laid out for
string   tblKey[], tblVal[]; color tblCol[], tblBg[];
double   dayPnl = 0; int lossRow = 0, winRow = 0; bool dayBlock = false; int pauseLeft = 0; bool paused = false;
double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;
double   labSeq[]; int parWins = 0; int rdUnits = 1; int oscU = 1; double oscP = 0;
double   crkL = 0; int crkN = 0; bool crkRec = false;   // Crooks: $ loss to win back, closed trades in the cycle, the open trade is a recovery trade
bool     crkW = false;                                   // Crooks C: the last closed trade was a win
int      crkP = 0;                                       // Crooks C over N wins: parts of the loss still to win back (0 = not set yet)
int      crkF = 0;                                       // Crooks C rule: losing recovery trades in a row in this cycle
bool     crkWait = false; int crkWW = 0; bool crkNeedL = false;   // wait rule: waiting for M wins in a row (wins so far); then the next recovery needs a loss first
bool     crkSkip = false; int crkSkipLeft = 0; int crkUDay = -1;  // skip rule: trading paused, counted days still to skip, your day of the last live bar
bool     crkHg = false;                                   // hedge rule: the next signal opens a buy and a sell
bool     exHg = false; double exHgS = 0, exHgT = 0;      // hedge rule: the working setup / open trades are the pair; its stop loss and take profit distances
double   gLastOutProfit = 0;                              // profit of the last closing deal (hedge rule: did the trade that closed last win)
int      gMonKey = -1;                                    // monthly lock: the month (your time zone) of the last processed bar
double   monPnl = 0, monPeak = 0;                         //   this month's closed profit (costs included) and its high
bool     monStop = false, monLocked = false, monRestPend = false;   //   no new trades until next month; profit lock armed; restart the recovery once flat
bool     gHedgeOk = false;                                // the account can hold a buy and a sell at the same time (hedging)
long     gPauseArm = -1;                                  // skip rule: armBar of a setup armed on a caught-up bar while trading was paused (never placed)
int      gCrkPrPrev = -1;                                 // the Crooks C rule the state belongs to (a new choice starts its state again)
bool     gInitDone = false;                               // restart memory: OnInit finished once (MT5 keeps globals when inputs or the timeframe change: nothing is reloaded then)
bool     gPersist = false; string gSvBase = "";           //   on (live / demo, not in the Strategy Tester); the names' prefix of this EA (symbol, magic, account)
bool     gRestored = false; datetime gSvT = 0, gSvLast = 0;   //   state reloaded at this start; when it was saved; the last processed bar it belongs to
string   gIoN[]; double gIoV[]; int gIoC = 0; bool gIoSave = true;   //   the values being written / read
string   gSvN[]; double gSvV[]; int gSvC = 0;              //   the values last written (only changes are written)
bool     gBrokerPend = false;                             //   the broker part of the start waits until MT5 is connected (positions and deals visible)
bool     gRestFlat = false;                               //   a force-close, weekend start or news start passed while the EA was off
datetime gSvFullT = 0; long gSvAcc = 0;                   //   the last full rewrite (daily: MT5 deletes global variables not accessed for 4 weeks); the saved account
// v4.4
int      gTzMode = SRV_EET; double gTzFix = 2.0, gTzDet = -99; bool gTzWarned = false;   // broker clock: the rule in use (Auto) and its fixed offset; the offset read now (-99 unknown)
string   gCloseWhy = ""; long gCloseId = 0;                // why this EA closed a trade last, and that trade's position id
long     gClosedIds[8]; int gClosedN = 0;                 // the last positions this EA closed (fully or partly): their reports say "this EA"
string   gLastClose = "-"; bool gLastCloseOut = false;     // table: the last close; closed outside this EA (by hand, phone, another EA)
datetime exArmT = 0; double exLim = 0;                    // the EA's trade: its setup's arm bar time and entry level (re-linked after a restart / new inputs)
double   exTpL[3];                                        // the trade's own TP1-TP3 levels (partials)
bool     gOurFill = false, gOurExit = false, gOurWin = false, gOurMove = false;   // the engine's events for the EA's setup (arm bar exArm) on the last processed bar
bool     gMissFill = false, gMissExit = false, gMissWin = false, gMissMove = false;   //   ... on bars caught up after a disconnect
string   gLockN = ""; double gLockV = 0;                  // one copy per symbol + magic number (temporary global variable)
int      gTfTrade = 0;                                    // the timeframe the EA trades: the one it was attached to (0 = not known yet)
datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
bool     gExitRetry = false; string gExitWhy = "";        // a close that failed: tried again at every bar close, and why it was due
bool     gExitSeen = false, gGoneWait = false;            // a closing deal of the EA's trade was seen; its position is gone but no closing deal yet
bool     exT1MvPend = false;                              // Crooks TP1 rule: a stop move before TP1 still has to reach the broker
bool     exT1 = false, exT1Half = false, exT1Be = false;   // Crooks TP1 rule: this trade, its TP1 half is booked, the rest's stop is at the entry
double   exT1Stop = 0, exT1Tp1 = 0, exT1Tp2 = 0;              // its stop and its own TP1 / TP2 (the engine's levels change with its next setup)
double   exT1Tight = 0, exT1Entry = 0;                    // its tight stop (TP1 / 2) and its entry level (bid chart)
double   exKeepSl = 0;             // restart: the adopted position's stop when it was tighter than the engine's; never widened
double   totalNet = 0; int exW = 0, exLn = 0;

//--- helpers ----------------------------------------------------------
double Pt()        { return SymbolInfoDouble(_Symbol, SYMBOL_POINT); }
double TickSize()  { double t = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE); return t > 0 ? t : Pt(); }
double FloorTick(double p) { double ts = TickSize(); return NormalizeDouble(MathFloor(p / ts + 1e-6) * ts, _Digits); }
double CeilTick(double p)  { double ts = TickSize(); return NormalizeDouble(MathCeil(p / ts - 1e-6) * ts, _Digits); }
// spread counted as a cost (lot size, earn-back, Crooks TP1-rule distance): the Spread input like TradingView, or the live spread when it is 0
double CostSpr() { return InpSpread > 0 ? InpSpread : MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)); }
double RoundTick(double p) { double ts = TickSize(); return NormalizeDouble(MathRound(p / ts) * ts, _Digits); }
int NthSunday(int y, int mon, int n)
{
   MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = 1;
   MqlDateTime f; TimeToStruct(StructToTime(d), f);
   return 1 + (7 - f.day_of_week) % 7 + 7 * (n - 1);
}
int LastSunday(int y, int mon) { int d = NthSunday(y, mon, 1); while(d + 7 <= 31) d += 7; return d; }   // March / October (31 days)
datetime MkTime(int y, int mon, int day, int hr) { MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = day; d.hour = hr; return StructToTime(d); }
// British summer time at a UTC time: 01:00 UTC on the last Sunday of March to 01:00 UTC on the last Sunday of October
bool UkSummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(d.year, 3, LastSunday(d.year, 3), 1) && utc < MkTime(d.year, 10, LastSunday(d.year, 10), 1); }
// New York daylight time at a UTC time: 07:00 UTC on the second Sunday of March to 06:00 UTC on the first Sunday of November
bool NySummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(d.year, 3, NthSunday(d.year, 3, 2), 7) && utc < MkTime(d.year, 11, NthSunday(d.year, 11, 1), 6); }
// the GMT offset of a summer-time rule (SRV_EET or SRV_NYCLOSE) at a server time
double RuleGMT(int md, datetime server)
{
   MqlDateTime d; TimeToStruct(server, d);
   if(md == SRV_EET)                                  // EU summer time: last Sunday of March to last Sunday of October
   {
      int es = LastSunday(d.year, 3), ee = LastSunday(d.year, 10);
      bool sum = (d.mon > 3 && d.mon < 10) || (d.mon == 3 && d.day >= es) || (d.mon == 10 && d.day < ee);
      return sum ? 3.0 : 2.0;
   }
   int ds = NthSunday(d.year, 3, 2), de = NthSunday(d.year, 11, 1);
   bool dst = (d.mon > 3 && d.mon < 11) || (d.mon == 3 && d.day >= ds) || (d.mon == 11 && d.day < de);
   return dst ? 3.0 : 2.0;
}
double SrvGMT(datetime server)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;   // Auto: the rule picked from the broker's clock (TzPick)
   if(md == SRV_FIXED) return InpServerTz == SRV_AUTO ? gTzFix : InpServerGMT;
   return RuleGMT(md, server);
}
datetime UserTime(datetime server) { return server - (datetime)(SrvGMT(server) * 3600) + (datetime)(InpUserGMT * 3600); }
datetime UtcTime(datetime server)  { return server - (datetime)(SrvGMT(server) * 3600); }
//--- names the restart memory never deletes ("Continue after a restart" off): the copy lock, the broker clock, "Start fresh once"
string SvExtra(string k) { return "ARX" + StringSubstr(gSvBase, 3) + k; }
//--- MT5 deletes global variables not used for 4 weeks: the EA's own ones are rewritten once a day (the copy lock is temporary)
void ExtraRefresh()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;
   if(InpMemFresh) GlobalVariableSet(SvExtra("rsd"), 1);
   if(gTfTrade > 0) GlobalVariableSet(SvExtra("tf"), gTfTrade);
}
//--- the chart shows another timeframe than the one the EA was attached to: no new trades until it is back (live only)
bool   TfHold() { return gTfTrade > 0 && (int)_Period != gTfTrade && MQLInfoInteger(MQL_TESTER) == 0; }
string TfName(int p) { return p == PERIOD_M1 ? "M1" : p == PERIOD_M5 ? "M5" : p == PERIOD_M15 ? "M15" : p == PERIOD_M30 ? "M30" : p == PERIOD_H1 ? "H1" : p == PERIOD_H4 ? "H4" : p == PERIOD_D1 ? "D1" : IntegerToString(p) + " min"; }
//--- the broker's GMT offset now, read from MT5 (server time - GMT, to the nearest half hour); live and connected only, -99 = unknown
double TzNow()
{
   if(MQLInfoInteger(MQL_TESTER) != 0 || TerminalInfoInteger(TERMINAL_CONNECTED) == 0) return -99;
   datetime sv = TimeTradeServer(), g = TimeGMT();
   if(sv <= 0 || g <= 0) return -99;
   double d = MathRound((double)(sv - g) / 1800.0) / 2.0;
   return MathAbs(d) <= 14 ? d : -99;
}
string GmtTxt(double h) { return "GMT" + (h >= 0 ? "+" : "") + (MathAbs(h - MathRound(h)) < 0.01 ? IntegerToString((int)MathRound(h)) : DoubleToString(h, 1)); }
string TzTxt()                                          // the broker clock in use now (table)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;
   string r = GmtTxt(SrvGMT(TimeCurrent())) + (InpServerTz == SRV_AUTO ? " auto" : "") + (md == SRV_EET ? " (EU summer time)" : md == SRV_NYCLOSE ? " (US summer time)" : " (fixed)");
   if(gTzDet > -90 && MathAbs(SrvGMT(TimeCurrent()) - gTzDet) > 0.01) r += " | broker " + GmtTxt(gTzDet) + ": CHECK";
   return r;
}
//--- Auto: the summer-time rule that gives the broker's offset now (EU first, as FxPro; then US), else that offset fixed. While MT5 is not
//--- connected yet, the clock read last time. Any choice: one message when the broker's clock differs from it (your days, hours, kill zones,
//--- news and force-close would be off by the difference)
void TzPick(bool atStart)
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;          // Strategy Tester: no real clock (Auto = EU summer time)
   gTzDet = TzNow();
   int md = gTzMode; double fx = gTzFix;
   if(gTzDet > -90)
   {
      datetime now = TimeTradeServer();
      if(RuleGMT(SRV_EET, now) == gTzDet) md = SRV_EET;
      else if(RuleGMT(SRV_NYCLOSE, now) == gTzDet) md = SRV_NYCLOSE;
      else { md = SRV_FIXED; fx = gTzDet; }
      GlobalVariableSet(SvExtra("tzm"), md); GlobalVariableSet(SvExtra("tzf"), fx);
   }
   else if(atStart && GlobalVariableCheck(SvExtra("tzm")))   // not connected yet: the clock read last time
   {
      md = (int)MathRound(GlobalVariableGet(SvExtra("tzm")));
      if(GlobalVariableCheck(SvExtra("tzf"))) fx = GlobalVariableGet(SvExtra("tzf"));
      if(md != SRV_EET && md != SRV_NYCLOSE && md != SRV_FIXED) md = SRV_EET;
   }
   if(InpServerTz == SRV_AUTO)
   {
      bool chg = md != gTzMode || (md == SRV_FIXED && fx != gTzFix);
      gTzMode = md; gTzFix = fx;
      if(chg && !atStart) Print("Broker server clock is ", GmtTxt(SrvGMT(TimeTradeServer())), " now (read from MT5): your times follow it from here on.");
      if(atStart && gTzDet > -90) Print("Broker server clock: ", TzTxt(), " (read from MT5).");
   }
   else if(gTzDet > -90 && MathAbs(SrvGMT(TimeTradeServer()) - gTzDet) > 0.01 && !gTzWarned)
   {
      gTzWarned = true;
      string m = "The broker's server clock is " + GmtTxt(gTzDet) + ", but 'Broker server clock' gives " + GmtTxt(SrvGMT(TimeTradeServer())) +
                 ": your days, hours, kill zones, news and force-close times are off. Choose 'Auto: read the broker's clock from MT5'.";
      Print(m); Alert(m);
   }
}
int      MinOfDay(datetime t) { MqlDateTime d; TimeToStruct(t, d); return d.hour * 60 + d.min; }
int      DowOf(datetime t)    { MqlDateTime d; TimeToStruct(t, d); return d.day_of_week; }   // 0 = Sunday
int      DayKey(datetime t)   { MqlDateTime d; TimeToStruct(t, d); return d.year * 1000 + d.day_of_year; }
double   Hi(int s) { return iHigh(_Symbol, _Period, s); }
double   Lo(int s) { return iLow(_Symbol, _Period, s); }
double   Cl(int s) { return iClose(_Symbol, _Period, s); }
double   Op(int s) { return iOpen(_Symbol, _Period, s); }
// kill zone in Indian minutes of the day, moved by the shift input and by extra minutes (winter time); the end is exclusive
bool     InKz(int m, int startM, int endM, int extra)
{
   int sh = (int)InpKzShift * 60 + extra;
   int ks = (startM + sh + 1440) % 1440, ke = (endM + sh + 1440) % 1440;
   return ks < ke ? (m >= ks && m < ke) : (m >= ks || m < ke);
}
double   ExitR() { return InpExitAt == EXIT_TP1 ? InpTp1R : InpExitAt == EXIT_TP2 ? InpTp2R : InpExitAt == EXIT_TP3 ? InpTp3R : InpTp4R; }

void LabReset() { ArrayResize(labSeq, 3); labSeq[0] = 1; labSeq[1] = 2; labSeq[2] = 3; }
double LabUnits() { int n = ArraySize(labSeq); if(n == 0) { LabReset(); n = 3; } return n > 1 ? labSeq[0] + labSeq[n - 1] : labSeq[0]; }

bool HasPosition(ulong &ticket, double &volume, double &openPrice)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      ticket = tk; volume = PositionGetDouble(POSITION_VOLUME); openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      return true;
   }
   return false;
}

void CancelPending()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong tk = OrderGetTicket(i);
      if(tk == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == _Symbol && OrderGetInteger(ORDER_MAGIC) == InpMagic) trade.OrderDelete(tk);
   }
}

void NoteClose(long pid) { gCloseId = pid; gClosedIds[gClosedN % 8] = pid; gClosedN++; }   // a position this EA closes now (fully or partly)
bool ClosedByUs(long pid) { if(pid > 0 && pid == gCloseId) return true; for(int q = 0; q < 8; q++) if(gClosedIds[q] == pid && pid > 0) return true; return false; }
void CloseAll(string why)
{
   ulong tk; double v, op;
   int guard = 0;
   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      gCloseWhy = why; NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
      Print("Closing #", tk, " (", DoubleToString(v, 2), " lots): ", why);
      if(!trade.PositionClose(tk)) { Print("Close of #", tk, " failed: ", trade.ResultRetcodeDescription()); break; }
   }
}

string DateTxt(datetime tm, bool withYear);            // defined below
// a position this EA opened: a deal with its magic number for that position id in the selected history (n deals)
bool OurPosId(long pid, int n)
{
   if(pid <= 0) return false;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk != 0 && HistoryDealGetInteger(tk, DEAL_POSITION_ID) == pid && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && HistoryDealGetString(tk, DEAL_SYMBOL) == _Symbol) return true;
   }
   return false;
}
bool IsExitDeal(ulong tk) { long e = HistoryDealGetInteger(tk, DEAL_ENTRY); return e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY; }
// a deal of this EA: its magic number, or the exit of a trade it opened (closed by hand, from the phone app or by another EA)
bool DealIsMine(ulong tk, int n)
{
   if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol) return false;
   if(HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic) return true;
   return (gHedgeOk || exState != 0) && IsExitDeal(tk) && OurPosId(HistoryDealGetInteger(tk, DEAL_POSITION_ID), n);   // netting (one position per symbol): while the EA holds a trade
}
// who closed a trade, from its exit deal
string CloseBy(ulong tk)
{
   long rs = HistoryDealGetInteger(tk, DEAL_REASON), mg = HistoryDealGetInteger(tk, DEAL_MAGIC), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   if(rs == DEAL_REASON_SL) return "its stop loss";
   if(rs == DEAL_REASON_TP) return "its take profit";
   if(rs == DEAL_REASON_SO) return "a margin stop-out";
   if(rs == DEAL_REASON_EXPERT)
      return mg != InpMagic ? "ANOTHER EA OR SCRIPT (magic " + IntegerToString(mg) + ")" :
             ClosedByUs(pid) ? (gCloseWhy != "" ? "this EA: " + gCloseWhy : "this EA (before a restart)") : "an EA with this magic number (a second copy of this EA?)";
   if(rs == DEAL_REASON_CLIENT) return "HAND (MetaTrader on the computer)";
   if(rs == DEAL_REASON_MOBILE) return "HAND (the phone app)";
   if(rs == DEAL_REASON_WEB) return "HAND (the web terminal)";
   return "the broker (reason " + IntegerToString(rs) + ")";
}
// one line in the log (Experts tab) and the table for every closing deal of this EA's trades: the trade's P&L from all its deals (n = deals)
void CloseReport(ulong tk, int n)
{
   long rs = HistoryDealGetInteger(tk, DEAL_REASON), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   string who = CloseBy(tk);
   double p = 0;
   for(int i = 0; i < n; i++)
   {
      ulong d = HistoryDealGetTicket(i);
      if(d != 0 && HistoryDealGetInteger(d, DEAL_POSITION_ID) == pid && HistoryDealGetString(d, DEAL_SYMBOL) == _Symbol)
         p += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP) + HistoryDealGetDouble(d, DEAL_FEE);
   }
   gLastCloseOut = !(rs == DEAL_REASON_SL || rs == DEAL_REASON_TP || (rs == DEAL_REASON_EXPERT && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && ClosedByUs(pid)));
   gLastClose = (p >= 0 ? "+" : "") + DoubleToString(p, 2) + " | " + who + " | " + DateTxt(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), false);
   bool still = false;                                  // part of the trade is still open (a partial close)
   for(int q = PositionsTotal() - 1; q >= 0 && !still; q--) { ulong pt = PositionGetTicket(q); if(pt != 0 && PositionGetInteger(POSITION_IDENTIFIER) == pid) still = true; }
   Print("Trade #", pid, still ? " partly closed: " : " closed: ", DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at ", DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),
         " | trade P&L ", (p >= 0 ? "+" : ""), DoubleToString(p, 2), " (costs included) | closed by ", who);
   if(gLastCloseOut && rs != DEAL_REASON_SO) Print("This trade was closed outside this EA's rules. Its profit is booked, and the loss recovery goes on from it.");
}
// realised P&L of this EA's deals since the last call (profit + commission + swap + fee); closed = an exit deal was seen; quiet: no report
// (skipping old history)
double NewDealsPnl(bool &closed, bool quiet = false)
{
   closed = false;
   double sum = 0;
   if(!HistorySelect(0, TimeCurrent() + 86400)) return 0;
   int n = HistoryDealsTotal();
   ulong maxTk = lastDeal;
   if(quiet) { for(int i = 0; i < n; i++) { ulong tq = HistoryDealGetTicket(i); if(tq > maxTk) maxTk = tq; } lastDeal = maxTk; return 0; }   // old history: only the cursor moves
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(tk > maxTk) maxTk = tk;
      if(!DealIsMine(tk, n)) continue;                  // v4.4: also the exit of this EA's trade by hand, from the phone app or by another EA
      double p = HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      sum += p;
      if(IsExitDeal(tk)) { closed = true; gExitSeen = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); if(!quiet) CloseReport(tk, n); }
   }
   lastDeal = maxTk;
   return sum;
}

void DrawBar(datetime bt);   // trade markings, defined below

//=== ENGINE: one CLOSED bar (shift s) = one Pine bar ===================
// Port of the shared Pine ENGINE block. Every step is in the same order as in Pine.
void ProcessBar(int s)
{
   bi++;
   evArm = false; evArmL = false; evFill = false; evFillL = false; evExit = false; evWin = false; evMove = false; evTp = false; evRes = 0; evCancel = 0;
   datetime t = iTime(_Symbol, _Period, s);
   double o = Op(s), h = Hi(s), l = Lo(s), c = Cl(s);
   long   rv = iVolume(_Symbol, _Period, s);
   long   tv = iTickVolume(_Symbol, _Period, s);
   double w  = rv > 0 ? (double)rv : (tv > 0 ? (double)tv : 1.0);
   double src = InpVwapSrc == PRICE_CLOSE ? c : InpVwapSrc == PRICE_OPEN ? o : InpVwapSrc == PRICE_HIGH ? h : InpVwapSrc == PRICE_LOW ? l :
                InpVwapSrc == PRICE_MEDIAN ? (h + l) / 2.0 : InpVwapSrc == PRICE_WEIGHTED ? (h + l + 2.0 * c) / 4.0 : (h + l + c) / 3.0;
   gLastDone = t;

   // VWAP (reset on the broker's server date change, or week / month) and its standard deviation
   int key = DayKey(t);
   bool newDay = (lastDayKey == -1) || (key != lastDayKey);
   lastDayKey = key;
   gNewDay = newDay;
   MqlDateTime md; TimeToStruct(t, md);
   int aKey = InpVwapAnchor == VW_WEEK ? (int)(((long)t + 3 * 86400) / (7 * 86400)) : InpVwapAnchor == VW_MONTH ? md.year * 12 + md.mon : key;   // weeks start Monday 00:00
   bool newAnchor = (lastAnchorKey == -1) || (aKey != lastAnchorKey);
   lastAnchorKey = aKey;
   if(newAnchor) { cumPV = 0; cumPV2 = 0; cumW = 0; cumP = 0; cumP2 = 0; cumN = 0; vwBars = 0; if(bi > 0) sessN++; }
   else vwBars++;
   cumPV += src * w; cumPV2 += src * src * w; cumW += w; cumP += src; cumP2 += src * src; cumN++;
   double vwap = cumW > 0 ? cumPV / cumW : cumP / cumN;
   tchL = l <= vwap ? 0 : (tchL < 1000000 ? tchL + 1 : 1000000);   // candles since the range last reached the VWAP (every bar, warm or not)
   tchS = h >= vwap ? 0 : (tchS < 1000000 ? tchS + 1 : 1000000);
   double vwVar = cumW > 0 ? cumPV2 / cumW - vwap * vwap : cumP2 / cumN - vwap * vwap;
   double vwSd = MathSqrt(MathMax(vwVar, 0.0));
   int hn = ArraySize(vwHist);
   if(hn < 600) ArrayResize(vwHist, hn + 1);
   for(int k = ArraySize(vwHist) - 1; k > 0; k--) vwHist[k] = vwHist[k - 1];
   vwHist[0] = vwap;
   int nHist = (int)MathMin((long)ArraySize(vwHist), bi + 1);

   // ATR (Wilder RMA, like ta.atr: the first value is the SMA of the first N true ranges)
   double pc = Cl(s + 1);
   double tr = bi == 0 ? h - l : MathMax(h - l, MathMax(MathAbs(h - pc), MathAbs(l - pc)));
   if(atrN < InpAtrLen) { atrSum += tr; atrN++; atrV = atrN == InpAtrLen ? atrSum / InpAtrLen : 0; }
   else atrV = (atrV * (InpAtrLen - 1) + tr) / InpAtrLen;
   double atr = atrV;
   bool   haveAtr = atrN >= InpAtrLen;
   bool   warm = bi >= MathMax(MathMax(InpStructLen, InpBrkLen), MathMax(MathMax(InpEntryLen, InpMomLen), MathMax(InpSlopeBars, InpStopLen))) + 1 && haveAtr;

   // optional accuracy filters (off by default)
   // VWAP crosses in this VWAP period: the close moving from more than 0.2 ATR on one side of the VWAP to more than 0.2 ATR on the other
   if(newAnchor) { vxSide = 0; vxN = 0; }
   double vxDev = haveAtr && atr > 0 ? (c - vwap) / atr : 0.0;
   int    vxZ = vxDev > 0.2 ? 1 : (vxDev < -0.2 ? -1 : 0);
   if(vxZ != 0) { if(vxSide != 0 && vxZ != vxSide) vxN++; vxSide = vxZ; }
   double vxRate = 100.0 * vxN / (vwBars + 1);
   // 1-hour candles (UTC hours) built from the bars; the EMA starts from the average of the first 20 hours
   long hKey = (long)UtcTime(t) / 3600;
   if(hK >= 0 && hKey != hK)
   {
      hNum++;
      double hNew = 0;
      if(hNum <= 20) { hSum += hC; hNew = hNum == 20 ? hSum / 20.0 : 0; }
      else hNew = 2.0 / 21.0 * hC + (1.0 - 2.0 / 21.0) * hE[0];
      hE[3] = hE[2]; hE[2] = hE[1]; hE[1] = hE[0]; hE[0] = hNew;
   }
   hK = hKey; hC = c;
   bool   haveSpd = hNum >= 23 && haveAtr && atr > 0;
   double emaSpd = haveSpd ? MathAbs(hE[0] - hE[3]) / atr : 0;

   // market structure and the displacement candle
   double priorHigh = -DBL_MAX, priorLow = DBL_MAX, sigHigh = -DBL_MAX, sigLow = DBL_MAX, entHigh = -DBL_MAX, entLow = DBL_MAX;
   for(int j = 1; j <= InpStructLen; j++) { priorHigh = MathMax(priorHigh, Hi(s + j)); priorLow = MathMin(priorLow, Lo(s + j)); }
   for(int j = 1; j <= InpBrkLen; j++) { sigHigh = MathMax(sigHigh, Hi(s + j)); sigLow = MathMin(sigLow, Lo(s + j)); }
   int eln = (int)MathMin(InpEntryLen, InpStructLen);
   for(int j = 1; j <= eln; j++) { entHigh = MathMax(entHigh, Hi(s + j)); entLow = MathMin(entLow, Lo(s + j)); }
   double swingLow = DBL_MAX, swingHigh = -DBL_MAX;
   for(int j = 0; j < InpStopLen; j++) { swingLow = MathMin(swingLow, Lo(s + j)); swingHigh = MathMax(swingHigh, Hi(s + j)); }
   double rng = h - l, body = MathAbs(c - o), bodyMid = (o + c) / 2.0;
   double momMove = c - Cl(s + InpMomLen);
   double erDen = 0; for(int k = 0; k < InpMomLen; k++) erDen += MathAbs(Cl(s + k) - Cl(s + k + 1));
   bool erUp = InpCmoMin <= 0 || (erDen > 0 && momMove / erDen >= InpCmoMin / 100.0);
   bool erDn = InpCmoMin <= 0 || (erDen > 0 && -momMove / erDen >= InpCmoMin / 100.0);
   bool haveSlope = InpSlopeBars > 0 && vwBars >= InpSlopeBars && nHist > InpSlopeBars;
   double vwSlope = haveSlope ? vwap - vwHist[InpSlopeBars] : 0;
   bool slopeUp = !haveSlope || vwSlope > 0, slopeDn = !haveSlope || vwSlope < 0;
   bool haveSg = InpSlopeBars > 0 && (InpSlopeCross ? nHist > InpSlopeBars : haveSlope);
   double sgSlope = haveSg ? vwap - vwHist[InpSlopeBars] : 0;
   bool sigUp = !haveSg || sgSlope > 0, sigDn = !haveSg || sgSlope < 0;
   bool bigCandle = haveAtr && rng > 0 && rng >= InpDispAtr * atr && body / rng * 100.0 >= InpBodyPct - 1e-7;
   bool bigImp    = haveAtr && rng > 0 && rng >= InpDispAtr * atr && body / rng * 100.0 >= InpImpBody - 1e-7;
   bool closeHi   = rng > 0 && (h - c) / rng * 100.0 <= InpClosePct + 1e-7;
   bool closeLo   = rng > 0 && (c - l) / rng * 100.0 <= InpClosePct + 1e-7;
   bool bullImp   = warm && c > o && h > priorHigh && bigImp && closeHi && slopeUp;
   bool bearImp   = warm && c < o && l < priorLow && bigImp && closeLo && slopeDn;
   bool setupOk   = vwBars >= InpMinOpenBars && !(InpSkipSunday && DowOf(UtcTime(t)) == 0);
   bool bullBase  = warm && InpAllowLong && setupOk && c > o && bigCandle && closeHi && sigUp && (!InpVwapFilter || c > vwap) && (InpMomAtr <= 0 || momMove >= InpMomAtr * atr) && erUp;
   bool bearBase  = warm && InpAllowShort && setupOk && c < o && bigCandle && closeLo && sigDn && (!InpVwapFilter || c < vwap) && (InpMomAtr <= 0 || -momMove >= InpMomAtr * atr) && erDn;
   double momB = c - Cl(s + InpBrkLen);
   double erDenB = 0; for(int k = 0; k < InpBrkLen; k++) erDenB += MathAbs(Cl(s + k) - Cl(s + k + 1));
   bool deepL = warm && InpDeepOn && InpAllowLong && setupOk && c > o && bigCandle && closeHi && sigUp && c > vwap && c > sigHigh && momB >= InpMomAtr * atr && erDenB > 0 && momB / erDenB >= InpCmoMin / 100.0 && priorHigh - c >= InpDeepFar * atr;
   bool deepS = warm && InpDeepOn && InpAllowShort && setupOk && c < o && bigCandle && closeLo && sigDn && c < vwap && c < sigLow && -momB >= InpMomAtr * atr && erDenB > 0 && -momB / erDenB >= InpCmoMin / 100.0 && c - priorLow >= InpDeepFar * atr;

   // session counters: day stats, impulses for the half stop, session range
   if(newDay)
   {
      dayFills = 0; dayW = 0; dayL = 0; dayR = 0; dayRiskR = 0; lossDirBlk = 0;
      if(bi > 0) { prevNet = bullN - bearN; havePrev = true; }
      bullN = 0; bearN = 0;
      if(haveSes) { pdH = sesH; pdL = sesL; havePd = true; }
      sesH = h; sesL = l; sesO = o; haveSes = true;
   }
   else { sesH = MathMax(sesH, h); sesL = MathMin(sesL, l); }
   bool halfL = InpHalfStop && bullN == 0 && havePrev && prevNet <= -InpBiasNet;
   bool halfS = InpHalfStop && bearN == 0 && havePrev && prevNet >= InpBiasNet;
   if(InpHalfStrict && havePrev)
   {
      halfL = halfL && (prevNet <= -5 || (prevNet + bullN - bearN <= -1 && bearN >= 1));
      halfS = halfS && (prevNet >= 5 || (prevNet + bullN - bearN >= 1 && bullN >= 1));
   }
   if(InpHalfOpenOut && havePd)
   {
      halfL = halfL || (InpHalfStop && bullN == 0 && sesO < pdL);
      halfS = halfS || (InpHalfStop && bearN == 0 && sesO > pdH);
   }
   if(bullImp) bullN++;
   if(bearImp) bearN++;

   double exitR = ExitR();
   // 1. live trade: stop first, then the final target, else stop moves (from the next bar)
   if(MathAbs(st) == 2 && bi > fillBar)
   {
      bool isL = st == 2; double d = isL ? 1 : -1;
      double tol = TickSize() * 0.001;   // a print exactly at a level counts (float noise of unrounded levels)
      bool stopHit = isL ? l <= stp + tol : h >= stp - tol;
      bool tgtHit  = isL ? h >= tF - tol : l <= tF + tol;
      int reached = (isL ? h >= t3 : l <= t3) ? 3 : (isL ? h >= t2 : l <= t2) ? 2 : (isL ? h >= t1 : l <= t1) ? 1 : 0;
      int prevHit = tpHit;
      tpHit = (int)MathMax(tpHit, reached);
      if(!stopHit) bestPx = isL ? MathMax(bestPx, h) : MathMin(bestPx, l);
      if(stopHit || tgtHit)
      {
         bool win = !stopHit;
         double res = win ? exitR : (stp == stp0 ? -1.0 : d * (stp - lim) / trRisk);
         if(!trGhost)
         {
            dayRiskR += res;
            lossDirBlk = res < 0 ? (isL ? 1 : -1) : (res > 0 ? 0 : lossDirBlk);
            totR += res; dayR += res;
            if(win) { totW++; dayW++; } else { totL++; dayL++; }
            lastRes = (win ? "TP" + IntegerToString((int)InpExitAt) + " " : "STOP ") + (res >= 0 ? "+" : "") + DoubleToString(res, 2) + "R";
            evExit = true; evWin = win; evRes = res;
         }
         else { if(win) ghW++; else ghL++; ghR += res; }
         lastExit = bi; st = 0;
      }
      else if(tpHit > prevHit)
      {
         double ns = stp;
         if(InpMv1On && tpHit >= 1) ns = isL ? MathMax(ns, lim + InpMv1R * trRisk) : MathMin(ns, lim - InpMv1R * trRisk);
         if(InpMv2On && tpHit >= 2) ns = isL ? MathMax(ns, lim + InpMv2R * trRisk) : MathMin(ns, lim - InpMv2R * trRisk);
         if(InpMv3On && tpHit >= 3) ns = isL ? MathMax(ns, lim + InpMv3R * trRisk) : MathMin(ns, lim - InpMv3R * trRisk);
         if(ns != stp) { stp = ns; evMove = !trGhost; }
         evTp = !trGhost;
      }
   }
   // 2. armed setup: fill (limit touch, or the next bar for market entries) or expiry
   if(MathAbs(st) == 1 && bi > armBar)
   {
      bool isL = st == 1;
      double mt = TickSize();
      bool touched = InpEntryMode == ENTRY_MARKET ? true : (isL ? l <= lim + mt * 0.001 : h >= lim - mt * 0.001);
      if(touched && dayFills < InpMaxFills)
      {
         st = isL ? 2 : -2; fillBar = bi; lastFill = bi; lastDir = isL ? 1 : -1; tpHit = 0; dayFills++;
         bestPx = lim;
         if(!trGhost) { evFill = true; evFillL = isL; }
         if(isL ? l <= stp + mt * 0.001 : h >= stp - mt * 0.001)
         {
            if(!trGhost)
            {
               dayRiskR += InpFillBarStopR ? -1.0 : 0.0;
               lossDirBlk = isL ? 1 : -1;
               totR += -1.0; dayR += -1.0; totL++; dayL++;
               lastRes = "STOP -1.00R";
               evExit = true; evWin = false; evRes = -1.0;
            }
            else { ghL++; ghR += -1.0; }
            lastExit = bi; st = 0;
         }
      }
      else if(bi - armBar >= InpRetestBars)
      {
         st = 0;
         if(!trGhost) evCancel = 1;
      }
   }
   // 3. arm a new setup on the closed displacement candle
   bool cooled = lastExit < 0 || bi - lastExit >= MathMax(InpCooldown, 1);
   bool dayOpen = InpDayStopR <= 0 || dayRiskR > -InpDayStopR;
   long legN = lastFill < 0 ? 0 : bi - lastFill;
   bool legOn = InpLegReset && MathAbs(st) != 2 && legN > 0 && legN < InpStructLen;
   double brkHigh = sigHigh, brkLow = sigLow;
   if(legOn)
   {
      double lh = Hi(s + 1), ll = Lo(s + 1);
      for(int j = 1; j <= legN; j++) { lh = MathMax(lh, Hi(s + j)); ll = MathMin(ll, Lo(s + j)); }
      if(lastDir == 1) brkHigh = lh; else brkLow = ll;
   }
   bool bullDisp = (bullBase && c > brkHigh) || deepL;
   bool bearDisp = (bearBase && c < brkLow) || deepS;
   if(InpLossBlock && lossDirBlk == 1) bullDisp = false;
   if(InpLossBlock && lossDirBlk == -1) bearDisp = false;
   datetime ut = UserTime(t);
   int dw = DowOf(ut);
   gDayOk = !InpDayOn || (dw == 1 && InpMon) || (dw == 2 && InpTue) || (dw == 3 && InpWed) || (dw == 4 && InpThu) || (dw == 5 && InpFri) || (dw == 6 && InpSat) || (dw == 0 && InpSun);
   int cur = MinOfDay(ut), a0 = InpStartH * 60 + InpStartM, b0 = InpEndH * 60 + InpEndM;
   gHourOk = !InpHoursOn || (a0 < b0 ? (cur >= a0 && cur < b0) : (cur >= a0 || cur < b0));
   datetime utcT = UtcTime(t);
   int kzM = MinOfDay(utcT + 19800);   // Indian Standard Time = UTC + 5:30
   // the times are the summer times: London / London close move 1 hour later in London winter time, New York in New York winter time
   int lonSh = InpKzAuto && !UkSummer(utcT) ? 60 : 0, nySh = InpKzAuto && !NySummer(utcT) ? 60 : 0;
   gKzOk = !InpKzOn || (InpKzAsia && InKz(kzM, 330, 570, 0)) || (InpKzLon && InKz(kzM, 690, 870, lonSh)) || (InpKzNy && InKz(kzM, 990, 1170, nySh)) || (InpKzLc && InKz(kzM, 1170, 1290, lonSh));
   bool canArm = gDayOk && gHourOk && gKzOk && MathAbs(st) != 2 && cooled && dayFills < InpMaxFills && dayOpen && atr > 0;
   bool keepArm = InpRearm == REARM_KEEP && ((st == 1 && bullDisp) || (st == -1 && bearDisp));
   if(canArm && (bullDisp || bearDisp) && !keepArm)
   {
      bool isL = bullDisp; double d = isL ? 1 : -1;
      double entry = InpEntryMode == ENTRY_MODEL ? (isL ? MathMax(bodyMid, entHigh) : MathMin(bodyMid, entLow)) : InpEntryMode == ENTRY_PCT ? c - d * InpEntryPct / 100.0 * rng : c;
      bool half = InpStopMode == STOP_ATR && (isL ? halfL : halfS);
      double cStop = entry - d * InpStopAtr * atr;
      double hStop = isL ? MathMin(entry - InpHalfStopAtr * atr, l) : MathMax(entry + InpHalfStopAtr * atr, h);
      if(InpHalfCap) hStop = isL ? MathMax(hStop, cStop) : MathMin(hStop, cStop);
      double sStop = isL ? swingLow - InpStopBufAtr * atr : swingHigh + InpStopBufAtr * atr;
      double stop  = InpStopMode == STOP_ATR ? (half ? hStop : cStop) : (isL ? MathMax(sStop, cStop) : MathMin(sStop, cStop));
      double risk = d * (entry - stop);
      if(risk >= TickSize() && RoundTick(stop) != RoundTick(entry))
      {
         bool haveZ = InpNoChase && vwSd > 0 && vwBars >= 3 && sessN >= 1;
         bool zNo = haveZ && d * (c - vwap) / vwSd > InpNoChaseSig;
         // choppy session (VWAP crosses) / over-extended 1h EMA20; a skipped setup runs on invisibly like the no-chase one
         bool chopNo = InpChopOn && vxRate > InpChopMax;
         bool emaNo = InpEmaOn && haveSpd && emaSpd > InpEmaMax;
         // signal close still hugging the VWAP (less than the minimum distance in ATR on the trade's side)
         bool nearNo = InpMinVwOn && d * (c - vwap) < InpMinVwAtr * atr;
         bool farNo = InpMaxVwOn && MathAbs(c - vwap) > (InpMaxVwUnit == VWU_PRICE ? InpMaxVwDist : InpMaxVwDist * atr);   // above or below
         // signal still on the VWAP: the stop on the other side of it, the VWAP touched in the last N candles, the entry too close to it
         bool stopNo = InpStopVwOn && d * (stop - vwap) < InpStopVwBuf * atr;
         bool tchNo = InpTouchVwOn && (isL ? tchL : tchS) < InpTouchVwN;
         bool entNo = InpEntVwOn && d * (entry - vwap) < InpEntVwAtr * atr;
         bool ghost = zNo || chopNo || emaNo || nearNo || farNo || stopNo || tchNo || entNo;
         if(MathAbs(st) == 1 && !trGhost) evCancel = 2;
         st = isL ? 1 : -1; armBar = bi; lim = entry; stp = stop; stp0 = stop; trRisk = risk; trHalf = half; trGhost = ghost;
         trSkip = zNo ? 1 : (chopNo ? 2 : (emaNo ? 3 : (nearNo ? 4 : (farNo ? 5 : (stopNo ? 6 : (tchNo ? 7 : (entNo ? 8 : 0)))))));
         t1 = lim + d * InpTp1R * risk; t2 = lim + d * InpTp2R * risk; t3 = lim + d * InpTp3R * risk; t4 = lim + d * InpTp4R * risk;
         tF = InpExitAt == EXIT_TP1 ? t1 : InpExitAt == EXIT_TP2 ? t2 : InpExitAt == EXIT_TP3 ? t3 : t4;
         if(!ghost) { evArm = true; evArmL = isL; }
      }
   }

   // accuracy of the shown trades (shared Pine STATS block): a target counts when the best price after the fill reached it
   // before the stop; the final target is reached exactly when the trade is a win
   if(evExit)
   {
      double sd = lastDir == 1 ? 1.0 : -1.0;
      int    xk = (int)InpExitAt;
      for(int k = 1; k <= 4; k++)
      {
         double lvl = k == 1 ? t1 : (k == 2 ? t2 : (k == 3 ? t3 : t4));
         if(evWin ? k <= xk : (k < xk && sd * (bestPx - lvl) >= -TickSize() * 0.001)) tpHitN[k - 1]++;
      }
      if(!evWin && stp != stp0) { if(evRes == 0.0) beN++; else if(evRes > 0.0) lkN++; }
   }
   if(gFirstT == 0) gFirstT = t;
   DrawBar(t);
}

//--- Crooks C rule after N losing recovery trades in a row (Crooks C only)
bool   CrkPrOn()  { return InpRec == REC_CRC && InpCrkPr != CPR_OFF; }
double CrkPrPct() { return CrkPrOn() && InpCrkPr == CPR_PCT ? MathMax(10.0, MathMin(100.0, InpCrkPrPct)) / 100.0 : 1.0; }
bool   CrkPause() { return CrkPrOn() && InpCrkPr == CPR_SKIP && crkSkip; }   // the skip rule pauses trading
bool   CrkHedgeNow() { return CrkPrOn() && InpCrkPr == CPR_HEDGE && crkHg && crkL > 0; }   // hedge rule: this signal opens the pair
//--- Crooks: the next trade is a recovery trade. A / B: trades 3, 5, 7 ... of the cycle; C: the trade after a win while a loss is owed; D: trades 3, 6, 9 ...
bool CrkRecNext()
{
   if(InpRec == REC_CRA || InpRec == REC_CRB) return crkN >= 2 && crkN % 2 == 0;
   if(InpRec == REC_CRC) return (crkW && crkL > 0 && !(CrkPrOn() && InpCrkPr == CPR_WAIT && (crkWait || crkNeedL))) || CrkHedgeNow();   // wait rule: not while waiting; the hedge pair is sized as a recovery trade
   if(InpRec == REC_CRD) return crkN >= 2 && (crkN - 2) % 3 == 0;
   return false;
}
//--- Crooks TP1 rule (exit at TP1, or any exit with InpCrkT1Any; recovery trades): the part p closed at TP1 banks the recovery amount, the rest runs to TP2.
//--- The size is the one whose stop-out at distance d loses exactly that amount: d = p x TP1 - (1 + p) x costs (p = 0.5: TP1 / 2 - 1.5 x costs),
//--- on the tick grid toward the entry (bid chart); 0 = not possible
double CrkT1P() { return MathMax(10.0, MathMin(90.0, InpCrkT1Pct)) / 100.0; }
double CrkT1Dist()
{
   if(!InpCrkT1 || (InpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext() || CrkHedgeNow()) return 0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0) return 0;
   double spr = CostSpr(), p = CrkT1P();
   double d = MathFloor((p * InpTp1R * trRisk - (1.0 + p) * (spr + InpCommLot * ts / tv)) / ts + 1e-9) * ts;
   return d >= ts ? d : 0;
}

//--- Crooks C over N wins: N, and the parts of the loss still to win back
int CrkNp() { return InpCrkCnOn ? MathMax(1, InpCrkCn) : 1; }
int CrkParts() { int np = CrkNp(); return (crkP < 1 || crkP > np) ? np : crkP; }
void   CrkCycle() { crkL = 0; crkN = 0; crkP = CrkNp(); crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkHg = false; }   // a new cycle at the base risk
//--- skip rule: a new day in your time zone while trading is paused; counted days end the pause (the day the count reaches 0 is still skipped)
void   CrkDayCount(bool counted) { if(!crkSkip) return; if(crkSkipLeft <= 0) crkSkip = false; else if(counted) crkSkipLeft--; }
//--- called for every live bar right after ProcessBar() (gDayOk is that bar's day filter): counted = every day, the ticked days, or Monday-Friday
void   CrkDayTick(datetime t)
{
   datetime ut = UserTime(t); int k = DayKey(ut);
   if(crkUDay == -1 || k == crkUDay) { crkUDay = k; return; }
   crkUDay = k;
   int dw = DowOf(ut);
   CrkDayCount(InpCrkPrAll || (InpDayOn ? gDayOk : (dw >= 1 && dw <= 5)));
}
//--- Crooks TP1 rule, stop before TP1: its distance from the entry (bid chart; the size always uses the tight distance d)
double CrkT1Stop0Dist(double d)
{
   double ts = TickSize();
   if(InpCrkT1Stop == T1S_TIGHT || ts <= 0) return d;
   if(InpCrkT1Stop == T1S_K45) return MathFloor(0.45 * trRisk / ts + 1e-9) * ts;
   if(InpCrkT1Stop == T1S_K60) return MathFloor(0.6 * trRisk / ts + 1e-9) * ts;
   return trRisk;                                       // the normal stop
}
//--- stop-out loss at that stop / the recovery amount (1 for the tight stop, and for every trade without the TP1 rule)
double CrkT1Mult()
{
   double d = CrkT1Dist();
   if(d <= 0) return 1.0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   double spr = CostSpr();
   double per = (d + spr) / ts * tv + InpCommLot, perL = (CrkT1Stop0Dist(d) + spr) / ts * tv + InpCommLot;
   return per > 0 ? perL / per : 1.0;
}

//--- monthly profit lock (calendar month in your time zone; closed deals, costs included) and the monthly restart of the loss recovery
void RecoveryRestart()                                // like the hard cap's Start again: the loss recovery starts again from the base risk
{
   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
   crkSkip = false; crkSkipLeft = 0;
}
void MonthTick(datetime ut)                           // a new month: the locks start again; the recovery restart waits until no trade of the old month is left
{
   MqlDateTime d; TimeToStruct(ut, d);
   int k = d.year * 100 + d.mon;
   if(gMonKey != -1 && k != gMonKey) { monPnl = 0; monPeak = 0; monStop = false; monLocked = false; if(InpMRestart) monRestPend = true; }
   gMonKey = k;
}
void MonthCheck()                                     // stop for the month at the lock amount, or when the profit falls back to the locked part of its high
{
   if(InpMLockOn && monPnl >= InpMLockAmt) monStop = true;
   if(InpPLockOn)
   {
      monPeak = MathMax(monPeak, monPnl);
      if(monPnl >= InpPLockAt) monLocked = true;
      if(monLocked && monPnl <= InpPLockPct / 100.0 * monPeak) monStop = true;
   }
}
void MonthFromHistory()                               // after a restart: this month's closed trades, its high and the locks from the deal history
{
   datetime b1 = iTime(_Symbol, _Period, 1), now = TimeCurrent();
   MqlDateTime d; TimeToStruct(UserTime(b1 > 0 ? b1 : now), d);
   gMonKey = d.year * 100 + d.mon;                    // the month of the last closed bar, as MonthTick will see it
   monPnl = 0; monPeak = 0; monLocked = false; monStop = false;
   long open[]; int no = 0;                           // positions still open: their deals are not closed profit yet
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong pt = PositionGetTicket(i);
      if(pt == 0 || PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      ArrayResize(open, no + 1); open[no++] = PositionGetInteger(POSITION_IDENTIFIER);
   }
   if(!HistorySelect(now - 40 * 86400, now + 86400)) return;
   int n = HistoryDealsTotal();
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || !DealIsMine(tk, n)) continue;      // v4.4: also an exit by hand, from the phone app or by another EA
      MqlDateTime dd; TimeToStruct(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), dd);
      if(dd.year * 100 + dd.mon != gMonKey) continue;  // only this month's deals (your time zone)
      long pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID); bool isOpen = false;
      for(int q = 0; q < no; q++) if(open[q] == pid) { isOpen = true; break; }
      if(isOpen) continue;
      monPnl += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      long e = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY) MonthCheck();
   }
}

//--- risk $ for the next trade (loss recovery + hard cap) -------------------
double NextRisk(double exitR, bool canTake = true)
{
   double base = InpBaseRisk, r = base;
   double stepBase = 0;
   if(totalNet >= 1000) { int kk = (int)MathFloor((totalNet - 1000) / 500); stepBase = (1000.0 + 500.0 * kk) / (8 + kk); }
   else if(totalNet >= 500) stepBase = 100.0;
   else if(totalNet >= 200) stepBase = 200.0 / 3.0;
   double baseC = InpRec == REC_CS ? MathMax(base, InpCapOn ? MathMin(stepBase, InpHardCap) : stepBase) : base;
   double fa = 1, fb = 1;
   for(int k = 2; k <= recLosses; k++) { double fc = fa + fb; fa = fb; fb = fc; }
   int oscNeed = exitR > 0 ? (int)MathMax(1, MathCeil((base - oscP) / (base * exitR))) : 1;
   switch(InpRec)
   {
      case REC_ALL:   r = base + recPool; break;
      case REC_SPLIT: r = base + recPool / InpRecN; break;
      case REC_PART:  r = base + recPool * InpRecPct / 100.0; break;
      case REC_MART:  r = base * MathPow(InpRecMult, recLosses); break;
      case REC_EXACT: r = base + recPool / exitR; break;
      case REC_STEP:  r = base + InpRecStep * recLosses; break;
      case REC_FIB:   r = base * (recLosses == 0 ? 1.0 : fb); break;
      case REC_DALE:  r = base * dUnits; break;
      case REC_C:
      case REC_CS:    r = MathMax(baseC, carried / InpCSplit); break;
      case REC_LAB:   r = base * LabUnits(); break;
      case REC_GMART: r = base * MathPow(InpRecMult, recLosses) + base * recLosses; break;
      case REC_PAR:   r = base * MathPow(2, parWins); break;
      case REC_RDALE: r = base * rdUnits; break;
      case REC_DELAY: r = recLosses >= InpDelayN ? base + recPool / InpRecN : base; break;
      case REC_EQPCT: r = AccountInfoDouble(ACCOUNT_EQUITY) * InpEqPct / 100.0; break;
      case REC_OSC:   r = base * MathMin(oscU, oscNeed); break;
      case REC_CRA:
      case REC_CRB:
      case REC_CRC:
      case REC_CRD:
      {
         double x = crkL / (InpRec == REC_CRB ? InpCSplit : InpRec == REC_CRC ? CrkParts() : 1) * (InpRec == REC_CRC ? CrkPrPct() : 1.0);   // % rule: a part of the loss
         r = !CrkRecNext() ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
         break;
      }
      default:        r = base;
   }
   double mul = CrkT1Mult();                       // the hard cap covers the real stop-out loss of a TP1-rule trade
   if(InpCapOn && r * mul > InpHardCap && canTake)   // a signal that is skipped anyway never restarts the cycle or stops trading
   {
      if(InpCapAction == CAP_STOP) capStop = true;
      else if(InpCapAction == CAP_RESET)
      {
         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
         r = MathMin(baseC, InpHardCap);
      }
      else r = InpHardCap / mul;
   }
   return r;
}

//--- the engine's events for the EA's own setup (arm bar exArm): ProcessBar plus which of its events are this trade's. A fill (step 2) is
//--- always the setup armed before the bar; an exit is the live trade's (step 1) or a stop on its fill bar (step 2); a stop move is the
//--- live trade's. ProcessBar itself is untouched (the same engine as the TradingView files)
void EngStep(int s)
{
   long pa = armBar; int ps = st;
   ProcessBar(s);
   bool mine = exArm >= 0 && pa == exArm;
   gOurFill = mine && evFill;
   gOurExit = evExit && ((mine && MathAbs(ps) == 2) || gOurFill);
   gOurWin  = gOurExit && evWin;
   gOurMove = mine && MathAbs(ps) == 2 && evMove;
}
//--- open time of the bar with engine index idx (the last processed bar is shift 1: after OnNewBar, a start, a catch-up)
datetime BarTimeOf(long idx)
{
   if(idx < 0 || idx > bi || gLastDone <= 0) return 0;
   int s0 = iBarShift(_Symbol, _Period, gLastDone, true);   // the last processed bar: shift 1 after a bar close, more when bars arrived since
   if(s0 < 0) return 0;
   int s = s0 + (int)(bi - idx);
   return s < Bars(_Symbol, _Period) ? iTime(_Symbol, _Period, s) : 0;
}

//--- lots for a $ risk and a stop distance --------------------------------
double LotsFor(double riskAmt, double stopDist, double entry, bool isL, double lossDist = 0)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double spr = CostSpr();
   double perLot = (stopDist + MathMax(spr, 0)) / ts * tv + InpCommLot;   // stop-out loss per lot incl. spread and commission
   double lossPerLot = ((lossDist > 0 ? lossDist : stopDist) + MathMax(spr, 0)) / ts * tv + InpCommLot;   // the real stop-out loss per lot
   double v = riskAmt / perLot;
   double notionalPerLot = entry / ts * tv, vLev = DBL_MAX;
   if(InpLeverage > 0 && notionalPerLot > 0) vLev = AccountInfoDouble(ACCOUNT_EQUITY) * InpLeverage / notionalPerLot;
   v = MathMin(v, vLev);
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(step <= 0) step = vmin > 0 ? vmin : 0.01;
   double v0 = v, vDown = MathFloor(v / step + 1e-9) * step, vNear = MathRound(v / step + 1e-9) * step;
   // to the nearest step only while the stop-out loss stays inside the hard cap and the size inside the leverage limit
   bool nearOk = InpLotRound == LOTR_NEAR && vNear > vDown + step * 0.5 && !(InpCapOn && vNear * lossPerLot > InpHardCap + 1e-9) && vNear <= vLev + 1e-9;
   v = nearOk ? vNear : vDown;
   // below the broker's minimum lot: trade the minimum (unless it breaks the hard cap or the leverage limit) or skip
   double vMinT = MathCeil(vmin / step - 1e-9) * step;         // the smallest multiple of the lot step the broker accepts
   if(v < vMinT - 1e-12 && v0 > 0)
      v = (InpSmallLot == SMALLL_MIN && !(InpCapOn && vMinT * lossPerLot > InpHardCap + 1e-9) && vMinT <= vLev + 1e-9) ? vMinT : 0;
   v = MathMin(v, vmax);
   double margin;
   ENUM_ORDER_TYPE ot = isL ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   while(v >= vmin && OrderCalcMargin(ot, _Symbol, v, entry, margin) && margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v -= step;
   if(v < vmin) return 0;
   return NormalizeDouble(v, 8);
}

//--- time filters (execution only) --------------------------------------------
bool NewsBlock(datetime ut, bool &startNow, datetime utPrev)
{
   startNow = false;
   bool blk = false;
   long pre = (long)InpNewsPre * 60;
   bool on[5]; datetime ts[5]; int du[5];
   on[0] = InpN1On; on[1] = InpN2On; on[2] = InpN3On; on[3] = InpN4On; on[4] = InpN5On;
   ts[0] = InpN1T;  ts[1] = InpN2T;  ts[2] = InpN3T;  ts[3] = InpN4T;  ts[4] = InpN5T;
   du[0] = InpN1Dur; du[1] = InpN2Dur; du[2] = InpN3Dur; du[3] = InpN4Dur; du[4] = InpN5Dur;
   for(int k = 0; k < 5; k++)
   {
      if(!on[k]) continue;
      if(ut >= ts[k] - pre && ut < ts[k] + du[k] * 60) blk = true;
      if(ut >= ts[k] && utPrev < ts[k]) startNow = true;
   }
   if(InpDNewsOn)
   {
      // the window is set in summer time; with InpDNewsAuto it moves 1 hour later while New York is on winter time (same New York time all year)
      int sh = InpDNewsAuto && !NySummer(ut - (datetime)(InpUserGMT * 3600)) ? 60 : 0;
      int cur = MinOfDay(ut), prv = MinOfDay(utPrev), s0 = (InpDNewsH * 60 + InpDNewsM + sh) % 1440, e0 = s0 + InpDNewsDur;
      bool inWin = (cur >= s0 && cur < e0) || (e0 > 1440 && cur < e0 - 1440);
      int diff = (s0 - cur + 1440) % 1440;
      if(inWin || (InpNewsPre > 0 && diff > 0 && diff <= InpNewsPre)) blk = true;
      bool prevIn = (prv >= s0 && prv < e0) || (e0 > 1440 && prv < e0 - 1440);
      if(inWin && !prevIn) startNow = true;
   }
   return blk;
}

//--- broker order levels that trigger at the engine's (bid-chart) levels ------
double Spr() { return InpBidChart ? MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)) : 0.0; }
double EntryPx(bool isL) { return isL ? FloorTick(lim + TickSize() * 0.001 + Spr()) : CeilTick(lim - TickSize() * 0.001); }
double StopPx(bool isL)  { double tl = TickSize() * 0.001; return isL ? FloorTick(stp + tl) : CeilTick(stp - tl + Spr()); }
double TgtPx(bool isL, double lvl) { double tl = TickSize() * 0.001; return isL ? CeilTick(lvl + exCostPx - tl) : FloorTick(lvl - exCostPx + tl + Spr()); }
double T1StopPx(bool isL, double d) { return isL ? CeilTick(lim - d) : FloorTick(lim + d + Spr()); }   // Crooks TP1 rule stop, toward the entry
// the TP1-rule trade's first stop (Crooks TP1 rule, stop before TP1)
double T1Stop0Px(bool isL, double d)
{
   if(InpCrkT1Stop == T1S_TIGHT || InpCrkT1Stop == T1S_K45 || InpCrkT1Stop == T1S_K60) return T1StopPx(isL, CrkT1Stop0Dist(d));
   return StopPx(isL);
}

double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
//--- an entry order's stop loss and take profit (v4.4: the target goes to the broker with the order): the engine's levels for this setup, kept
//--- outside the stops level from what MT5 checks them against: the order's price (pending) or the price that closes the trade (market).
//--- SetExits re-sends the engine's levels once it has filled. false: a market entry with the price already past the target (no entry)
bool OrderExits(bool isL, double ep, bool market, double &sl, double &tp)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), minD = MinDist();
   double ref = market ? (isL ? bid : ask) : ep;
   sl = exT1 ? exT1Stop : StopPx(isL);
   tp = exT1 ? TgtPx(isL, exT1Tp2) : TgtPx(isL, tF);   // Crooks TP1 rule: the rest's TP2 (its TP1 part closes at market)
   if(market && (isL ? ref >= tp : ref <= tp)) return false;
   if(isL) { sl = MathMin(sl, FloorTick(MathMin(ep, ref) - minD)); tp = MathMax(tp, CeilTick(ref + minD)); }
   else    { sl = MathMax(sl, CeilTick(MathMax(ep, ref) + minD)); tp = MathMin(tp, FloorTick(ref - minD)); }
   return true;
}
//--- Crooks C hedge rule: a buy and a sell at the engine's entry level with the hedge stop loss and take profit
//--- (bid-chart levels: the buy-side prices are shifted by the spread, like the normal orders)
double HgDist(double x)                                 // at least the stops level + the spread + 1 tick, or the broker rejects the order
{
   double ts = TickSize(), d = InpCrkHgUnit == HGU_R ? x * trRisk : x;
   double sp = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
   return MathMax(MinDist() + sp + ts, MathRound(d / ts) * ts);
}
void   HgLevels(bool buy, double &sl, double &tp)
{
   double tl = TickSize() * 0.001;
   if(buy) { sl = FloorTick(lim - exHgS + tl); tp = CeilTick(lim + exHgT - tl); }
   else    { sl = CeilTick(lim + exHgS - tl + Spr()); tp = FloorTick(lim - exHgT + tl + Spr()); }
}
bool   HgMarket(double v)                                // both trades at market (the level is reached, or Market entry); one trade alone is closed again
{
   double slB, tpB, slS, tpS; HgLevels(true, slB, tpB); HgLevels(false, slS, tpS);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), g = MinDist() + TickSize();
   slB = MathMin(slB, FloorTick(bid - g)); tpB = MathMax(tpB, CeilTick(bid + g));   // the price already past a level (a gap): keep the order valid
   slS = MathMax(slS, CeilTick(ask + g)); tpS = MathMin(tpS, FloorTick(ask - g));
   bool a = trade.Buy(v, _Symbol, 0, slB, tpB, "HEDGE");
   if(!a) Print("Hedge buy failed: ", trade.ResultRetcodeDescription());
   bool b = trade.Sell(v, _Symbol, 0, slS, tpS, "HEDGE");
   if(!b) Print("Hedge sell failed: ", trade.ResultRetcodeDescription());
   if(a != b) { CloseAll("hedge pair: only one of the two trades opened"); return false; }
   return a && b;
}
bool   PlaceHedge(bool isL, double v)                    // the pair's orders: a limit in the signal's direction and a stop the other way, both at the entry level
{
   if(InpEntryMode == ENTRY_MARKET) return HgMarket(v);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), gap = MathMax(MinDist(), TickSize());
   double pB = EntryPx(true), pS = EntryPx(false);       // the buy and the sell trigger when the bid reaches the entry level
   double slB, tpB, slS, tpS; HgLevels(true, slB, tpB); HgLevels(false, slS, tpS);
   if(isL ? (ask <= pB || bid <= pS) : (bid >= pS || ask >= pB)) return HgMarket(v);   // at / through the level: both now
   if(isL ? (ask - pB < gap || bid - pS < gap) : (pS - bid < gap || pB - ask < gap)) { gVirt = true; return true; }   // inside the stops distance: VirtualEntry opens both
   bool a = isL ? trade.BuyLimit(v, pB, _Symbol, slB, tpB, ORDER_TIME_GTC, 0, "HEDGE") : trade.SellLimit(v, pS, _Symbol, slS, tpS, ORDER_TIME_GTC, 0, "HEDGE");
   bool b = a && (isL ? trade.SellStop(v, pS, _Symbol, slS, tpS, ORDER_TIME_GTC, 0, "HEDGE") : trade.BuyStop(v, pB, _Symbol, slB, tpB, ORDER_TIME_GTC, 0, "HEDGE"));
   if(!b) { Print("Hedge orders failed: ", trade.ResultRetcodeDescription()); CancelPending(); return false; }
   return true;
}
bool   HgOpen()                                          // a hedge trade of this EA is open (e.g. after a restart)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic && PositionGetString(POSITION_COMMENT) == "HEDGE") return true;
   }
   return false;
}
void SetExits(bool withTarget)
{
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   double sl = StopPx(exL), tp = withTarget ? TgtPx(exL, tF) : 0;
   if(exT1) { sl = exT1Half ? NormalizeDouble(op, _Digits) : exT1Stop; tp = withTarget ? TgtPx(exL, exT1Tp2) : 0; }   // Crooks TP1 rule: rest to TP2, at the entry after TP1
   if(exKeepSl > 0 && (exL ? exKeepSl > sl : exKeepSl < sl)) sl = exKeepSl;   // an adopted position keeps its tighter stop
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double minD = MinDist();
   // price is already through the engine's stop or target: the engine exits on this bar, so exit now
   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp)))
   { CloseAll((exL ? bid <= sl : ask >= sl) ? "the price is already past the stop" : "the price is already past the target"); return; }
   if(exL) { if(bid - sl < minD) sl = FloorTick(bid - minD); if(tp > 0 && tp - bid < minD) tp = CeilTick(bid + minD); }
   else    { if(sl - ask < minD) sl = CeilTick(ask + minD); if(tp > 0 && ask - tp < minD) tp = FloorTick(ask - minD); }
   bool same = MathAbs(PositionGetDouble(POSITION_SL) - sl) < TickSize() * 0.5 && MathAbs(PositionGetDouble(POSITION_TP) - tp) < TickSize() * 0.5;
   if(same || trade.PositionModify(tk, sl, tp)) { if(exT1 && exT1Half) exT1Be = true; if(exT1 && !exT1Half) exT1MvPend = false; }
   else Print("Stop/target update rejected (", trade.ResultRetcodeDescription(), "): SL ", DoubleToString(sl, _Digits), " TP ", DoubleToString(tp, _Digits));
}

//--- Crooks TP1 rule: move the stop before TP1 at a bar close (entry candle -> tight; a candle closed in profit -> tight or the entry)
void T1StopMove()
{
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   double c1 = iClose(_Symbol, PERIOD_CURRENT, 1);
   bool prof = exL ? c1 > exT1Entry : c1 < exT1Entry;
   double tgt = exT1Stop;
   if(InpCrkT1Stop == T1S_FILL || (InpCrkT1Stop == T1S_PT && prof)) tgt = exT1Tight;
   else if(InpCrkT1Stop == T1S_PBE && prof) tgt = exL ? FloorTick(exT1Entry + TickSize() * 0.001) : CeilTick(exT1Entry - TickSize() * 0.001 + Spr());   // the chart entry, like the strategy
   if(exL ? tgt > exT1Stop : tgt < exT1Stop) { exT1Stop = tgt; exT1MvPend = true; SetExits(true); }
}

//--- Crooks TP1 rule: close the TP1 part at market (rounded UP to the lot step, so it banks at least the recovery amount); the rest's stop then moves to the entry
void T1Half(ulong tk, double vol)
{
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double cv = MathCeil(exLots * CrkT1P() / step - 1e-9) * step;
   if(cv >= vmin && vol - cv >= vmin - 1e-9)
   {
      gCloseWhy = "Crooks TP1 rule: the TP1 part"; if(PositionSelectByTicket(tk)) NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
      if(trade.PositionClosePartial(tk, NormalizeDouble(cv, 8))) { exT1Half = true; SetExits(true); }
      else { Print("TP1 partial close failed (", trade.ResultRetcodeDescription(), "), retrying"); gT1Seen = true; }   // ticks retry while price is past TP1, the next bar close in any case
   }
   else CloseAll("Crooks TP1 rule: TP1 reached, too small to split, all closed");   // too small to split: close it all at TP1
}

//--- text helpers (table and markings) ----------------------------------------
string SgnR(double r) { return (r >= 0 ? "+" : "") + DoubleToString(r, 2) + "R"; }
string Share(int n, int total) { return total > 0 ? IntegerToString((int)MathRound(100.0 * n / total)) + "%" : "-"; }
string AccTxt() { int n = totW + totL; return IntegerToString(n) + " trades | " + Share(totW, n) + " (" + IntegerToString(totW) + "W/" + IntegerToString(totL) + "L) | " + SgnR(totR); }
string TpTxt()
{
   int n = totW + totL, xk = (int)InpExitAt;
   string s = "";
   for(int k = 1; k <= 4; k++) s += (k > 1 ? " | " : "") + "TP" + IntegerToString(k) + " " + (k > xk ? "n/a" : Share(tpHitN[k - 1], n) + " (" + IntegerToString(tpHitN[k - 1]) + ")");
   return s;
}
string BeTxt() { int n = totW + totL; return "BE " + IntegerToString(beN) + " (" + Share(beN, n) + ") | locked profit " + IntegerToString(lkN) + " (" + Share(lkN, n) + ")"; }
string FltTxt() { return IntegerToString(ghW + ghL) + " skipped | would have been " + IntegerToString(ghW) + "W/" + IntegerToString(ghL) + "L | " + SgnR(ghR); }
string MonTxt(int m) { string a[12] = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}; return a[(m + 11) % 12]; }
string DateTxt(datetime tm, bool withYear)
{
   MqlDateTime d; TimeToStruct(tm, d);
   return StringFormat("%02d %s ", d.day, MonTxt(d.mon)) + (withYear ? StringFormat("%02d", d.year % 100) : StringFormat("%02d:%02d", d.hour, d.min));
}

//--- trade markings: drawn for every bar the engine processes (history included), same events as the TradingView files
string TrId(datetime tf) { return "ARM_X" + IntegerToString((long)tf) + "_"; }
void MarkLine(string nm, datetime ta, double pa, datetime tb, double pb, color clr, int width, ENUM_LINE_STYLE sty)
{
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_TREND, 0, ta, pa, tb, pb);
   else { ObjectMove(0, nm, 0, ta, pa); ObjectMove(0, nm, 1, tb, pb); }
   ObjectSetInteger(0, nm, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, nm, OBJPROP_WIDTH, width);
   ObjectSetInteger(0, nm, OBJPROP_STYLE, sty);
   ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, false);
   ObjectSetInteger(0, nm, OBJPROP_BACK, true);
   ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
}
void MarkBox(string nm, datetime ta, double pa, datetime tb, double pb, color clr)
{
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_RECTANGLE, 0, ta, pa, tb, pb);
   else { ObjectMove(0, nm, 0, ta, pa); ObjectMove(0, nm, 1, tb, pb); }
   ObjectSetInteger(0, nm, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, nm, OBJPROP_FILL, true);
   ObjectSetInteger(0, nm, OBJPROP_BACK, true);
   ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
}
void MarkText(string nm, datetime ta, double pa, string txt, color clr, ENUM_ANCHOR_POINT anc)
{
   if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_TEXT, 0, ta, pa);
   else ObjectMove(0, nm, 0, ta, pa);
   ObjectSetString(0, nm, OBJPROP_TEXT, txt);
   ObjectSetString(0, nm, OBJPROP_FONT, "Arial");
   ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, 7);
   ObjectSetInteger(0, nm, OBJPROP_COLOR, clr);
   ObjectSetInteger(0, nm, OBJPROP_ANCHOR, anc);
   ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
}
// one engine bar: armed limit, then a filled trade's boxes, entry / TP lines, fill arrow and price labels, then its result
void DrawBar(datetime bt)
{
   if(!InpDraw || !gCanDraw) return;
   if(evCancel != 0 || evFill) ObjectDelete(0, "ARM_limit");
   if(evArm) MarkLine("ARM_limit", bt, lim, bt + PeriodSeconds() * InpRetestBars, lim, InpColEntry, 1, STYLE_DASH);   // MT5 dashes only width-1 lines
   int xk = (int)InpExitAt;
   if(evFill)
   {
      string id = TrId(bt);
      bool   isL = evFillL;
      MarkBox(id + "tgt", bt, MathMax(lim, tF), bt, MathMin(lim, tF), InpColTarget);
      MarkBox(id + "stp", bt, MathMax(lim, stp0), bt, MathMin(lim, stp0), InpColStop);
      MarkLine(id + "en", bt, lim, bt, lim, InpColEntry, 2, STYLE_SOLID);
      if(xk > 1) MarkLine(id + "tp1", bt, t1, bt, t1, InpColTarget, 1, STYLE_DOT);
      if(xk > 2) MarkLine(id + "tp2", bt, t2, bt, t2, InpColTarget, 1, STYLE_DOT);
      if(xk > 3) MarkLine(id + "tp3", bt, t3, bt, t3, InpColTarget, 1, STYLE_DOT);
      string an = id + "ar";
      if(ObjectFind(0, an) < 0) ObjectCreate(0, an, isL ? OBJ_ARROW_BUY : OBJ_ARROW_SELL, 0, bt, lim);
      ObjectSetInteger(0, an, OBJPROP_COLOR, isL ? InpColEntry : InpColStop);
      ObjectSetInteger(0, an, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, an, OBJPROP_HIDDEN, true);
      MarkText(id + "le", bt, lim, (isL ? "BUY " : "SELL ") + DoubleToString(lim, _Digits), InpColEntry, isL ? ANCHOR_LEFT_LOWER : ANCHOR_LEFT_UPPER);
      MarkText(id + "ls", bt, stp0, "SL " + DoubleToString(stp0, _Digits) + (trHalf ? " (half)" : ""), InpColStop, isL ? ANCHOR_LEFT_UPPER : ANCHOR_LEFT_LOWER);
      MarkText(id + "lt", bt, tF, "TP" + IntegerToString(xk) + " " + DoubleToString(tF, _Digits), InpColTarget, isL ? ANCHOR_LEFT_LOWER : ANCHOR_LEFT_UPPER);
      gDrawT = bt; gDrawOn = true;
      int n = ArraySize(gDrawn);
      ArrayResize(gDrawn, n + 1);
      gDrawn[n] = (long)bt;
      if(InpMaxDrawn > 0 && n + 1 > InpMaxDrawn) { ObjectsDeleteAll(0, TrId((datetime)gDrawn[0])); ArrayRemove(gDrawn, 0, 1); }
   }
   else if(gDrawOn)
   {
      string id = TrId(gDrawT);
      ObjectMove(0, id + "tgt", 1, bt, MathMin(lim, tF));
      ObjectMove(0, id + "stp", 1, bt, MathMin(lim, stp0));
      ObjectMove(0, id + "en", 1, bt, lim);
      if(xk > 1) ObjectMove(0, id + "tp1", 1, bt, t1);
      if(xk > 2) ObjectMove(0, id + "tp2", 1, bt, t2);
      if(xk > 3) ObjectMove(0, id + "tp3", 1, bt, t3);
   }
   if(evExit && gDrawOn)
   {
      bool   above = (lastDir == 1) == evWin;   // long target / short stop: above the level
      string txt = evWin ? "TP" + IntegerToString(xk) + " " + SgnR(evRes) : (stp != stp0 && evRes == 0.0 ? "BE " : "STOP ") + SgnR(evRes);
      color  cl = evWin ? InpColTarget : (evRes >= 0.0 ? clrSilver : InpColStop);
      MarkText(TrId(gDrawT) + "rx", bt, evWin ? tF : stp, txt, cl, above ? ANCHOR_RIGHT_LOWER : ANCHOR_RIGHT_UPPER);
      gDrawOn = false;
   }
}

//--- on-chart table (rebuilt on every new bar so it stays on top of the markings) ----
string StateText(bool newsBlk)
{
   string why = trSkip == 1 ? "TOO FAR FROM VWAP" : (trSkip == 2 ? "CHOPPY VWAP SESSION" : (trSkip == 3 ? "1H EMA20 TOO FAST" : (trSkip == 4 ? "TOO CLOSE TO VWAP" :
                (trSkip == 5 ? "BEYOND MAX VWAP DISTANCE" : (trSkip == 6 ? "STOP BEYOND VWAP" : (trSkip == 7 ? "VWAP TOUCHED RECENTLY" : "ENTRY TOO CLOSE TO VWAP"))))));
   string s = st != 0 && trGhost ? "SKIPPED (" + why + ")" : st == 2 ? "LONG ACTIVE" : st == -2 ? "SHORT ACTIVE" : st == 1 ? "BUY LIMIT ARMED" : st == -1 ? "SELL LIMIT ARMED" :
              capStop ? "HARD CAP: STOPPED" : newsBlk ? "NEWS WINDOW" : paused ? "PAUSED" : CrkPause() ? "CROOKS C PAUSE (" + IntegerToString(crkSkipLeft) + "d left)" : monStop ? "MONTHLY LOCK (until the 1st)" : dayBlock ? "STREAK STOP TODAY" :
              !gDayOk ? "DAY SWITCHED OFF" : !gHourOk ? "OUTSIDE HOURS" : !gKzOk ? "OUTSIDE KILL ZONES" : CrkHedgeNow() ? "SCANNING (HEDGE PAIR ON THE NEXT SIGNAL)" : "SCANNING";
   if(TfHold()) s = "CHART ON " + TfName((int)_Period) + ": NO NEW TRADES (EA TRADES " + TfName(gTfTrade) + ")";
   string ex = exState == 2 ? (exHg ? " (hedge pair open)" : exArm < 0 ? " (in trade, own stop and target)" : " (in trade)") : (exState == 1 ? (gVirt ? " (waiting for the level)" : exHg ? " (hedge orders working)" : " (order working)") : "");
   return s + ex;
}
void TblAdd(string k, string v, color vc, color bg)
{
   int n = ArraySize(tblKey);
   ArrayResize(tblKey, n + 1); ArrayResize(tblVal, n + 1); ArrayResize(tblCol, n + 1); ArrayResize(tblBg, n + 1);
   tblKey[n] = k; tblVal[n] = v; tblCol[n] = vc; tblBg[n] = bg;
}
void TblCell(string nm, int x, int y, int w, int hgt, color bg, string txt, color fg, int fs)
{
   string rb = nm + "b", lb = nm + "t";
   ObjectCreate(0, rb, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, rb, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, rb, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, rb, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, rb, OBJPROP_XSIZE, w);
   ObjectSetInteger(0, rb, OBJPROP_YSIZE, hgt);
   ObjectSetInteger(0, rb, OBJPROP_BGCOLOR, bg);
   ObjectSetInteger(0, rb, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, rb, OBJPROP_COLOR, C'74,78,90');
   ObjectSetInteger(0, rb, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, rb, OBJPROP_HIDDEN, true);
   ObjectCreate(0, lb, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, lb, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, lb, OBJPROP_ANCHOR, ANCHOR_LEFT);
   ObjectSetInteger(0, lb, OBJPROP_XDISTANCE, x + 6);
   ObjectSetInteger(0, lb, OBJPROP_YDISTANCE, y + hgt / 2);
   ObjectSetString(0, lb, OBJPROP_FONT, "Arial");
   ObjectSetInteger(0, lb, OBJPROP_FONTSIZE, fs);
   ObjectSetInteger(0, lb, OBJPROP_COLOR, fg);
   ObjectSetString(0, lb, OBJPROP_TEXT, txt);
   ObjectSetInteger(0, lb, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, lb, OBJPROP_HIDDEN, true);
}
void UpdateTable()
{
   if(!InpShowTable || !gCanDraw) return;
   ObjectsDeleteAll(0, "ARM_TB_");
   ArrayResize(tblKey, 0); ArrayResize(tblVal, 0); ArrayResize(tblCol, 0); ArrayResize(tblBg, 0);
   color  white = clrWhite, posC = C'105,240,174', negC = C'255,128,171', cell = C'30,34,45';
   bool   act = MathAbs(st) == 2 && !trGhost, armed = MathAbs(st) == 1 && !trGhost, has = act || armed;
   int    xk = (int)InpExitAt;
   string tps = has ? DoubleToString(t1, _Digits) + " | " + DoubleToString(t2, _Digits) + " | " + DoubleToString(t3, _Digits) + " | " + DoubleToString(t4, _Digits) : "-";
   bool   isC = InpRec == REC_C || InpRec == REC_CS, isK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;
   bool   kRec = exState != 0 ? crkRec : CrkRecNext();
   string kTxt = DoubleToString(crkL, 2) + (InpRec == REC_CRC ? (kRec ? " | recovery trade" + (CrkNp() > 1 ? ", part " + IntegerToString(CrkNp() - CrkParts() + 1) + " of " + IntegerToString(CrkNp()) : "") : (crkL > 0 ? " | base, waiting for a win" : " | base")) : " | trade " + IntegerToString(crkN + 1) + (kRec ? " recovery" : " base")) + (InpRec == REC_CRB ? " | split " + IntegerToString(InpCSplit) : "")
                 + (exState != 0 && exT1 ? (exT1Half ? " | TP1 booked, rest to TP2" : " | TP1 rule, stop " + DoubleToString(exT1Stop, _Digits)) : "")
                 + (!CrkPrOn() ? "" : CrkPause() ? " | paused, " + IntegerToString(crkSkipLeft) + " days left" : crkWait ? " | waiting for " + IntegerToString(InpCrkPrM) + " wins in a row (" + IntegerToString(crkWW) + ")" :
                    crkNeedL ? " | waiting for a loss, then a win" : crkHg ? " | hedge pair on the next signal" : crkF > 0 ? " | lost recoveries in a row " + IntegerToString(crkF) + "/" + IntegerToString(InpCrkPrN) : "");
   string rec = InpRec == REC_OFF ? "off" : (isC ? DoubleToString(carried, 2) + " | split " + IntegerToString(InpCSplit) : isK ? kTxt : DoubleToString(recPool, 2) + " | " + IntegerToString(recLosses) + " losses in a row");
   TblAdd("AUCTION RETEST", "EA v4.4", white, C'61,143,214');
   TblAdd("STATE", gStateTxt, white, act ? (st == 2 ? C'76,175,80' : C'242,54,69') : (armed ? C'255,152,0' : C'93,96,107'));
   TblAdd("ENTRY / STOP", has ? DoubleToString(lim, _Digits) + " / " + DoubleToString(stp, _Digits) + (trHalf ? " (half stop)" : "") : "-", white, cell);
   TblAdd("TP1 | TP2 | TP3 | TP4 (exit TP" + IntegerToString(xk) + ")", tps, posC, cell);
   TblAdd("RISK | LOTS", exState != 0 ? DoubleToString(exRiskAmt, 2) + " | " + DoubleToString(exLots, 2) : "base " + DoubleToString(InpBaseRisk, 2), white, cell);
   TblAdd(isC ? "LOSSES CARRIED" : isK ? "CROOKS: LOSS TO WIN BACK" : "RECOVERY POOL", rec, (isC ? carried : isK ? crkL : recPool) > 0 ? negC : white, cell);
   TblAdd("STREAK W | L", IntegerToString(winRow) + " | " + IntegerToString(lossRow) + " | total " + IntegerToString(exW) + "W/" + IntegerToString(exLn) + "L", white, cell);
   TblAdd("DAY P&L | FILLS", DoubleToString(dayPnl, 2) + " | " + IntegerToString(dayFills) + "/" + IntegerToString(InpMaxFills) + (InpMLockOn || InpPLockOn ? " | month " + DoubleToString(monPnl, 2) + (monLocked ? " (locked " + DoubleToString(InpPLockPct / 100.0 * monPeak, 2) + ")" : "") : ""), dayPnl >= 0 ? posC : negC, cell);
   TblAdd("SIGNALS | TAKEN | SKIPPED", IntegerToString(sigN) + " | " + IntegerToString(takenN) + " | " + IntegerToString(skipN) + (missN > 0 ? " | missed " + IntegerToString(missN) : "") + (skipWhy != "" ? " (last: " + skipWhy + ")" : ""), skipN + missN > 0 ? negC : white, cell);
   TblAdd("SIGNAL TRADES | WIN % | R", AccTxt() + " | last " + lastRes, totR >= 0 ? posC : negC, cell);
   TblAdd("TP HIT", TpTxt(), posC, cell);
   if(InpMv1On || InpMv2On || InpMv3On) TblAdd("BREAKEVEN", BeTxt(), white, cell);
   if(InpNoChase || InpChopOn || InpEmaOn || InpMinVwOn || InpMaxVwOn || InpStopVwOn || InpTouchVwOn || InpEntVwOn) TblAdd("SKIPPED BY FILTERS", FltTxt(), ghR <= 0 ? posC : negC, cell);
   TblAdd("DATA RANGE", gFirstT > 0 ? DateTxt(UserTime(gFirstT), true) + " -> " + DateTxt(UserTime(gLastDone), false) + " | " + IntegerToString(bi + 1) + " bars" : "-", white, cell);
   TblAdd("RESTART MEMORY", gPersist ? (gRestored ? "on | continued from " + DateTxt(UserTime(gSvT), true) : "on") : InpRemember ? "off in the Strategy Tester" : "off", white, cell);
   TblAdd("LAST CLOSE", gLastClose, gLastCloseOut ? negC : white, cell);
   TblAdd("BROKER CLOCK", MQLInfoInteger(MQL_TESTER) != 0 ? GmtTxt(SrvGMT(TimeCurrent())) + " (Strategy Tester)" : TzTxt(), StringFind(TzTxt(), "CHECK") >= 0 ? negC : white, cell);
   // column widths from the longest text in each column
   int  fs = (int)MathMax(6, InpTableFont), n = ArraySize(tblKey), kw = 0, vw = 0, th = 0;
   uint tw = 0, tht = 0;
   TextSetFont("Arial", -fs * 10);
   for(int i = 0; i < n; i++)
   {
      TextGetSize(tblKey[i], tw, tht); kw = (int)MathMax(kw, (int)tw); th = (int)MathMax(th, (int)tht);
      TextGetSize(tblVal[i], tw, tht); vw = (int)MathMax(vw, (int)tw); th = (int)MathMax(th, (int)tht);
   }
   int  rowH = th + 6, c0 = kw + 12, c1 = vw + 12;
   int  cw = (int)ChartGetInteger(0, CHART_WIDTH_IN_PIXELS), chh = (int)ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);
   gTblW = cw; gTblH = chh;
   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;
   int  x0 = right ? (int)MathMax(0, cw - c0 - c1 - 8) : 8, y0 = bottom ? (int)MathMax(0, chh - n * rowH - 8) : 22;
   for(int i = 0; i < n; i++)
   {
      int y = y0 + i * rowH;
      TblCell("ARM_TB_k" + IntegerToString(i), x0, y, c0, rowH, i == 0 ? C'41,163,224' : C'42,46,57', tblKey[i], i == 0 ? white : C'209,212,220', fs);
      TblCell("ARM_TB_v" + IntegerToString(i), x0 + c0, y, c1, rowH, tblBg[i], tblVal[i], tblCol[i], fs);
   }
   ChartRedraw(0);
}

//--- place the engine's setup at the broker (sizing, filters, pending or market order) ----
void TakeSetup(bool isL, bool newsBlk, bool flatNow)
{
   sigN++;
   gTakenT = BarTimeOf(armBar);                       // decided on now (taken, skipped or rejected): a restart does not take it again
   ulong pTk; double pVol, pOpen;
   bool posNow = HasPosition(pTk, pVol, pOpen);
   bool crkPs = CrkPause();
   bool tfHold = TfHold();                           // v4.4: the chart shows another timeframe than the one the EA trades
   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock || crkPs || monStop || tfHold);   // the hard cap acts only on a signal that can be taken
   double rAmt = NextRisk(ExitR(), canTake);
   bool   hg = CrkHedgeNow();                        // Crooks C hedge rule: a buy and a sell (after NextRisk: a hard-cap restart cancels it)
   double hgS = hg ? HgDist(InpCrkHgSl) : 0, hgT = hg ? HgDist(InpCrkHgTp) : 0;
   if(hg && InpCapOn && hgT > hgS) rAmt = MathMin(rAmt, InpHardCap / 2.0);   // both trades can lose: the pair stays inside the hard cap
   double t1d = CrkT1Dist();                         // after a cap restart this is 0: trade 1 of a new cycle
   double sd = hg ? hgS : t1d > 0 ? t1d : trRisk;    // stop distance used for the size
   double ld = hg ? hgS : t1d > 0 ? CrkT1Stop0Dist(t1d) : trRisk;   // the real stop-out distance (a wider TP1-rule stop)
   double v = (capStop || crkPs) ? 0 : LotsFor(rAmt, sd, lim, isL, ld);
   if(hg && v > 0)                                   // hedge pair: the free margin must carry both trades
   {
      double vst = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmn = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mg;
      if(vst <= 0) vst = vmn > 0 ? vmn : 0.01;
      while(v >= vmn && OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, 2 * v, lim, mg) && mg > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v = NormalizeDouble(v - vst, 8);
      if(v < vmn) v = 0;
   }
   skipWhy = (exState != 0 || posNow) ? "still in a trade" : tfHold ? "chart on " + TfName((int)_Period) + ", the EA trades " + TfName(gTfTrade) : (newsBlk || flatNow) ? "news / force-close" : capStop ? "hard cap stop" : paused ? "paused" : dayBlock ? "streak stop" : crkPs ? "Crooks C pause" : monStop ? "monthly lock" : v <= 0 ? "size 0" : "";
   if(skipWhy != "") { skipN++; return; }
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   double sprNow = CostSpr();
   exCostPx = InpEarnBack && tv > 0 && !hg ? InpCommLot / (tv / ts) + sprNow : 0;   // no earn-back on the hedge pair: its levels are the inputs
   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot);
   exT1 = t1d > 0; exT1Half = false; exT1Be = false; exT1MvPend = false; exT1Stop = exT1 ? T1Stop0Px(isL, t1d) : 0; exT1Tight = exT1 ? T1StopPx(isL, t1d) : 0; exT1Entry = lim;
   exT1Tp1 = t1; exT1Tp2 = t2; exKeepSl = 0; exHg = false; exHgS = hgS; exHgT = hgT; gLastOutProfit = 0;
   exTpL[0] = t1; exTpL[1] = t2; exTpL[2] = t3; exLim = lim;   // the trade's own levels (partials, restart)
   for(int q = 0; q < 3; q++) pDone[q] = false;
   CancelPending();
   gVirt = false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ep = EntryPx(isL), sl = 0, tp = 0;           // v4.4: the stop loss and the take profit go with the order (OrderExits)
   double minD = MinDist();
   bool ok, past = false;
   if(hg) ok = PlaceHedge(isL, v);
   else if(InpEntryMode == ENTRY_MARKET)
   {
      past = !OrderExits(isL, ep, true, sl, tp);
      ok = !past && (isL ? trade.Buy(v, _Symbol, 0, sl, tp, "ARM") : trade.Sell(v, _Symbol, 0, sl, tp, "ARM"));
   }
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) { OrderExits(isL, ep, false, sl, tp); ok = trade.BuyLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM"); }
      else if(ask <= ep)                { past = !OrderExits(isL, ep, true, sl, tp); ok = !past && trade.Buy(v, _Symbol, 0, sl, tp, "ARM"); }   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                  // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) { OrderExits(isL, ep, false, sl, tp); ok = trade.SellLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM"); }
      else if(bid >= ep)                { past = !OrderExits(isL, ep, true, sl, tp); ok = !past && trade.Sell(v, _Symbol, 0, sl, tp, "ARM"); }
      else { ok = true; gVirt = true; }
   }
   if(ok)
   {
      exState = 1; exArm = armBar; exArmT = gTakenT; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg;
      gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false; gT1Seen = false; gExitSeen = false; gGoneWait = false;   // no events of an earlier trade
   }
   else if(past) { skipN++; skipWhy = "price already past the target"; }
   else { skipN++; skipWhy = "order rejected"; Print("ARM order failed: ", trade.ResultRetcodeDescription()); }
}

//--- an entry that could not be a pending order (inside the stops distance): enter at market when the level is reached
void VirtualEntry()
{
   if(!gVirt) return;
   if(exState != 1) { gVirt = false; return; }
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(exHg)                                             // hedge pair: both trades at market when the level is reached
   {
      if(exL ? (ask <= EntryPx(true) || bid <= EntryPx(false)) : (bid >= EntryPx(false) || ask >= EntryPx(true))) { gVirt = false; HgMarket(exLots); }
      return;
   }
   double ep = EntryPx(exL), sl = 0, tp = 0;
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      if(!OrderExits(exL, ep, true, sl, tp)) { Print("ARM entry skipped: the price is already past the target."); return; }   // v4.4: the take profit goes with the order
      if(!(exL ? trade.Buy(exLots, _Symbol, 0, sl, tp, "ARM") : trade.Sell(exLots, _Symbol, 0, sl, tp, "ARM")))
         Print("ARM entry failed: ", trade.ResultRetcodeDescription());
   }
}

//--- close the EA's trade for a rule; if MT5 refuses (off quotes, trading disabled, market closed) it is tried again at every bar close
void CloseRule(string why)
{
   CloseAll(why);
   ulong k; double kv, ko;
   if(HasPosition(k, kv, ko)) { gExitRetry = true; gExitWhy = why; } else gExitRetry = false;
}

//--- an executed trade has closed: streaks, pauses and loss recovery
void BookClosed()
{
   bool win = exPnl > 0;
   monPnl += exPnl;                                     // monthly locks: the whole trade counts in the month it closes
   dayPnl += exPnl;
   if(win) exW++; else exLn++;
   lossRow = win ? 0 : lossRow + 1; winRow = win ? winRow + 1 : 0;
   if(InpLStopOn && lossRow >= InpLStopN) dayBlock = true;
   if(InpWStopOn && winRow >= InpWStopN) dayBlock = true;
   if(InpPauseOn && lossRow >= InpPauseN) { dayBlock = true; pauseLeft = (int)MathMax(1, MathMin(3, InpPauseDays)); lossRow = 0; }
   if(win)
   {
      recPool = MathMax(0.0, recPool - exPnl); recLosses = recPool > 0 ? recLosses : 0;
      dUnits = (int)MathMax(1, dUnits - 1); rdUnits++;
      parWins = parWins + 1 >= InpParN ? 0 : parWins + 1;
      int n = ArraySize(labSeq);
      if(n <= 2) LabReset();
      else { double tmp[]; ArrayResize(tmp, n - 2); for(int q = 0; q < n - 2; q++) tmp[q] = labSeq[q + 1]; ArrayResize(labSeq, n - 2); for(int q = 0; q < n - 2; q++) labSeq[q] = tmp[q]; }
   }
   else
   {
      recPool += -exPnl; recLosses++; dUnits++; rdUnits = (int)MathMax(1, rdUnits - 1); parWins = 0;
      double used = LabUnits(); int n = ArraySize(labSeq); ArrayResize(labSeq, n + 1); labSeq[n] = used;
   }
   oscP += exPnl;
   if(oscP >= InpBaseRisk) { oscU = 1; oscP = 0; } else if(win) oscU++;
   // Crooks: losses add to the loss to win back, wins reduce it; a new cycle when it is all back, less than a cent left (A, D: also when a recovery trade wins; C keeps a leftover)
   bool lastPart = CrkParts() == 1;                     // this recovery trade went for the last part of the loss (Crooks C over N wins)
   crkL = MathMax(0.0, crkL - exPnl);
   if(exHg)                                             // the hedge pair closed (exPnl = both trades): forget the loss, or Crooks C goes on from the trade that closed last
   {
      crkF = 0; crkHg = false;
      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = CrkNp(); }
   }
   else if(crkL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && crkRec)) CrkCycle();
   else
   {
      crkN++; crkP = !win ? CrkNp() : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts();   // Crooks C over N wins: a loss starts the parts again
      if(CrkPrOn())                                     // Crooks C rule after N losing recovery trades in a row
      {
         if(crkWait) { crkWW = win ? crkWW + 1 : 0; if(crkWW >= MathMax(1, InpCrkPrM)) { crkWait = false; crkWW = 0; crkNeedL = true; } }   // M wins in a row end the wait
         else if(crkNeedL && !win) crkNeedL = false;   // ... then a loss: the trade after the next win is the recovery trade
         if(crkRec && win) { crkF = 0; if(InpCrkPr == CPR_PCT && lastPart) CrkCycle(); }   // % rule: the % went for is back, the rest is forgotten
         else if(crkRec && ++crkF >= MathMax(1, InpCrkPrN))
         {
            crkF = 0;
            if(InpCrkPr == CPR_FORGET || InpCrkPr == CPR_PCT) CrkCycle();
            else if(InpCrkPr == CPR_WAIT) { crkWait = true; crkWW = 0; crkNeedL = false; }
            else if(InpCrkPr == CPR_SKIP) { crkSkip = true; crkSkipLeft = MathMax(1, InpCrkPrD); if(InpCrkPrForget) CrkCycle(); }
            else if(InpCrkPr == CPR_HEDGE) { if(gHedgeOk) crkHg = true; else CrkCycle(); }   // hedge rule: the next signal opens the pair (netting account: forget the loss)
         }
      }
   }
   crkW = exHg ? gLastOutProfit > 0 : win;             // hedge pair: the trade that closed last decides (a win -> the next trade is a recovery trade)
   crkRec = false; exT1 = false; exT1Half = false; exT1Be = false; exKeepSl = 0;
   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false; exHg = false;
   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false;
   gT1Seen = false; gExitSeen = false; gGoneWait = false; gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
   CancelPending();
}

//--- every new day since the last booking (more than one after a disconnect or a restart): the day's P&L and streak stop start again, each
//    new day ends one pause day
void DayStart(int nd)
{
   if(nd <= 0) return;
   dayPnl = 0; dayBlock = false;
   for(int q = 0; q < nd; q++) { paused = pauseLeft > 0; if(pauseLeft > 0) pauseLeft--; }
}

//=== EXECUTION: runs once per new bar, after the engine processed the bar that just closed ===
void OnNewBar()
{
   EngStep(1);
   if(gMissFill) gOurFill = true;                       // the engine's events for the EA's setup on bars caught up after a disconnect
   if(gMissMove) gOurMove = true;
   if(gMissExit && !gOurExit) { gOurExit = true; gOurWin = gMissWin; }
   gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
   CrkDayTick(iTime(_Symbol, _Period, 1));              // Crooks C skip rule: a new day in your time zone counts before this bar's booking
   datetime bt = iTime(_Symbol, _Period, 1);
   datetime ut = UserTime(bt), utPrev = UserTime(gPrevT > 0 ? gPrevT : iTime(_Symbol, _Period, 2));
   MonthTick(ut);                                     // a new month (your time zone): its closed deals count from this bar on

   DayStart(gDayPendN + (gNewDay ? 1 : 0)); gDayPendN = 0;   // each new day since the last bar (several after a disconnect or a restart)
   if(gNewDay) { TzPick(false); ExtraRefresh(); }        // the broker's clock and the EA's own global variables, once a day

   // 1. what the broker did since the last bar
   bool closedNew; double newPnl = NewDealsPnl(closedNew);
   exPnl += newPnl; totalNet += newPnl;
   if(newPnl != 0 || closedNew) carried = MathMax(0.0, carried - newPnl);
   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   if(exState == 0 && pos && !exHg)                    // the order filled while it was being cancelled: a trade of this EA, kept on its own levels
   {
      exState = 2; exArm = -1; exSynced = false;
      Print("Position #", pTk, " of this EA filled while its order was being cancelled: kept, it runs to its own stop loss and take profit.");
   }
   bool gone = exState == 2 && !pos;
   if(gone && !closedNew && !gExitSeen && !gGoneWait) { gGoneWait = true; gone = false; }   // no closing deal in the history yet: booked at the next bar, with it
   bool exClosed = (exState == 1 && !pos && closedNew) || gone;

   // 2. an executed trade has closed
   if(exClosed) BookClosed();
   if(gExitRetry)                                       // a close that failed before: again
   {
      if(exState != 2 || !pos) gExitRetry = false;
      else { CloseRule((gExitWhy != "" ? gExitWhy : "a close that failed before a restart") + " (again)"); pos = HasPosition(pTk, pVol, pOpen); }
   }

   // 3. follow the engine for the EA's own setup only (its arm bar exArm). The engine's fill confirms the trade (its levels are re-sent), a stop
   //    move moves the broker's stop, and the engine's stop (or its final target without earn-back) on the bar chart closes it. v4.4: a trade
   //    the engine is not in (filled before the engine on a narrower spread, its setup ended, new inputs, another timeframe) is never closed
   //    early: it runs to its own stop loss and take profit, which went to the broker with the order
   bool exMine = exArm >= 0 && armBar == exArm;
   if(exState == 1 && !(MathAbs(st) == 1 && exMine))   // the engine no longer holds the EA's armed setup: expired, replaced or filled
   {
      CancelPending();
      if(exMine && lastFill > exArm) missN++;          // engine filled, broker did not
      exState = 0; exArm = -1; gVirt = false; exHg = false;
   }
   if(exState == 2 && exArm >= 0 && !exHg)
   {
      if(gOurFill || (exMine && MathAbs(st) == 2)) exSynced = true;   // the engine filled the EA's setup (this bar, a caught-up bar, or before)
      if(!exSynced && !(exMine && MathAbs(st) == 1))   // filled at the broker first, and the engine's setup ended without its fill
      {
         Print("Trade #", pTk, " filled before the engine's fill (bid chart) and its setup ended: kept, it runs to its own stop loss and take profit.");
         exArm = -1;
      }
   }
   // Crooks TP1 rule: TP1 was reached but no tick booked the TP1 part (missed tick, failed close, disconnect): book it now, before the
   // stop / target update below (exit TP1: the engine won on the bar that just closed; any exit: that bar, after the fill bar, reached
   // TP1; or a bar caught up after a disconnect did)
   bool t1Bar = exT1 && exSynced && lastFill >= 0 && lastFill < bi && (exL ? Hi(1) >= exT1Tp1 + exCostPx : Lo(1) <= exT1Tp1 - exCostPx);
   bool t1Due = (gOurExit && gOurWin) || t1Bar || gT1Seen;
   gT1Seen = false;                                                  // a failed close below sets it again: retried at the next bar close
   if(t1Due && exState == 2 && exT1 && !exT1Half && pos) { T1Half(pTk, pVol); pos = HasPosition(pTk, pVol, pOpen); }
   if(exState == 2 && exMine && MathAbs(st) == 2 && !exHg && (gOurFill || gOurMove)) SetExits(true);   // the engine's levels are this trade's only while it is in it
   if(gOurExit && exState == 2 && !exHg)
   {
      // the engine's trade ended: its stop, or its final target without earn-back, closes the trade (earn-back and the Crooks TP1 rule only outlive a win)
      if((!InpEarnBack || !gOurWin) && !(exT1 && (gOurWin || exT1Half)))
         CloseRule(gOurWin ? "the engine's final target was reached (bar close, bid chart)" : "the engine's stop was hit (bar close, bid chart)");
      exArm = -1;                                       // the engine is done with this trade: a runner goes on to its own levels
   }
   // Crooks TP1 rule: stop choices that move the stop at a bar close, before the TP1 half is booked
   if(exState == 2 && exT1 && !exT1Half && (InpCrkT1Stop == T1S_FILL || InpCrkT1Stop == T1S_PT || InpCrkT1Stop == T1S_PBE)) T1StopMove();
   // v4.4: no "engine wins" close any more (v4.3 closed a trade the engine was not in at the next bar, at whatever price it was)

   // 4. force-close time / weekend start / news
   bool nStart; bool newsBlk = NewsBlock(ut, nStart, utPrev);
   int  fcM = InpFcH * 60 + InpFcM, curM = MinOfDay(ut), prvM = MinOfDay(utPrev);
   bool fcNow = InpFcOn && (curM >= prvM ? (prvM < fcM && curM >= fcM) : (fcM > prvM || fcM <= curM));
   bool wkndStart = InpWeekendOn && DowOf(ut) == 6 && DowOf(utPrev) != 6;
   bool flatNow = fcNow || wkndStart || nStart;
   if(flatNow && pos) CloseRule(fcNow ? "the daily force-close time" : wkndStart ? "the weekend starts (Saturday)" : "a news window starts");
   if(exHg && exState == 2 && (flatNow || newsBlk)) CancelPending();   // hedge pair: a trade still waiting is not opened after force-close, weekend or news
   if(exState == 1 && (flatNow || newsBlk)) { CancelPending(); exState = 0; exArm = -1; gVirt = false; exHg = false; }

   // monthly restart (once no trade of the old month is left) and the monthly locks, after every booking of this bar
   if(monRestPend && exState == 0 && !HasPosition(pTk, pVol, pOpen)) { monRestPend = false; RecoveryRestart(); }
   MonthCheck();

   // 5. take the engine's new setup
   if(evArm) TakeSetup(evArmL, newsBlk, flatNow);

   // on-chart table
   gStateTxt = StateText(newsBlk);
   UpdateTable();
}

//--- partial closes, intrabar (execution only) ---------------------------------
void ManagePartials()
{
   if(exState != 2 || exHg) return;
   int exitK = (int)InpExitAt;
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   double px = SymbolInfoDouble(_Symbol, SYMBOL_BID);   // the engine's levels are bid-chart levels for both directions
   double tp[3]; double pp[3];
   bool eng = exArm >= 0 && armBar == exArm && MathAbs(st) == 2;   // the engine's levels are this trade's while it is in it
   tp[0] = exTpL[0] > 0 ? exTpL[0] : eng ? t1 : 0; tp[1] = exTpL[1] > 0 ? exTpL[1] : eng ? t2 : 0; tp[2] = exTpL[2] > 0 ? exTpL[2] : eng ? t3 : 0;   // the trade's own levels (v4.4)
   pp[0] = InpP1; pp[1] = InpP2; pp[2] = InpP3;
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(exT1)
   {
      // Crooks TP1 rule: the TP1 part closes at TP1 and banks the whole recovery amount, then the rest's stop moves to the entry (it runs to TP2)
      if(exT1Half) { if(!exT1Be) SetExits(true); return; }          // retry the move to the entry until the broker accepts it
      if(exT1MvPend) SetExits(true);                                 // retry a stop move before TP1 until the broker accepts it
      if(exL ? px >= exT1Tp1 + exCostPx : px <= exT1Tp1 - exCostPx) T1Half(tk, vol);
      return;
   }
   for(int k = 0; k < 3; k++)
   {
      if(k + 1 >= exitK || pp[k] <= 0 || pDone[k] || tp[k] <= 0) continue;
      if(exL ? px >= tp[k] + exCostPx : px <= tp[k] - exCostPx)
      {
         double cv = MathFloor(exLots * pp[k] / 100.0 / step + 1e-9) * step;
         if(cv >= vmin && vol - cv >= vmin - 1e-9)
         {
            gCloseWhy = "partial close at TP" + IntegerToString(k + 1); if(PositionSelectByTicket(tk)) NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
            trade.PositionClosePartial(tk, NormalizeDouble(cv, 8));
         }
         pDone[k] = true;
      }
   }
}

//=== RESTART MEMORY (v4.3) =================================================================================================
// The loss recovery (every rule's state), streaks and pauses, the Crooks C rule state, the hard-cap stop, total profit, the month-change flag
// and the open trade's bookkeeping live in the EA's memory. MT5 keeps that memory when inputs or the timeframe change, but not when MT5 or
// the EA restarts. They are written to MT5 global variables (Tools -> Global Variables, F3; names ARS|symbol|magic|...) whenever they
// change, flushed to disk, and read back when the EA starts fresh; the bars and broker deals since then are caught up like after a disconnect.
int    SvVer() { return 1; }                            // layout version of the saved values
string SvBaseName()                                     // ARS|symbol|magic| (a short hash when that is too long: names have at most 63 characters)
{
   string b = "ARS|" + _Symbol + "|" + IntegerToString(InpMagic) + "|";
   if(StringLen(b) <= 57) return b;
   string k = _Symbol + "|" + IntegerToString(InpMagic);
   uint h = (uint)2166136261;                           // FNV-1a
   for(int q = 0; q < StringLen(k); q++) { h ^= (uint)StringGetCharacter(k, q); h *= (uint)16777619; }
   return "ARS|" + StringFormat("%08X", h) + "|";
}
//--- one value: collected (save) or read back when it was saved (load)
void IoD(string n, double &x)
{
   if(gIoSave)
   {
      if(gIoC >= ArraySize(gIoN)) { ArrayResize(gIoN, gIoC + 32); ArrayResize(gIoV, gIoC + 32); }
      gIoN[gIoC] = n; gIoV[gIoC] = x; gIoC++;
   }
   else if(GlobalVariableCheck(gSvBase + n)) x = GlobalVariableGet(gSvBase + n);
}
void IoI(string n, int &x)      { double d = x; IoD(n, d); x = (int)MathRound(d); }
void IoB(string n, bool &x)     { double d = x ? 1.0 : 0.0; IoD(n, d); x = d != 0.0; }
void IoT(string n, datetime &x) { double d = (double)x; IoD(n, d); x = (datetime)(long)MathRound(d); }
void IoU(string n, ulong &x)    { double hi = (double)(x >> 32), lo = (double)(x & 0xFFFFFFFF); IoD(n + "h", hi); IoD(n + "l", lo); x = ((ulong)MathRound(hi) << 32) | (ulong)MathRound(lo); }
//--- the saved state: one list for writing and reading, so both always match
void StateIO(bool save)
{
   gIoSave = save; gIoC = 0;
   int ver = SvVer(); IoI("ver", ver);
   datetime lb = gLastDone, sv = TimeCurrent();           // the last processed bar, and when it was saved (both not a reason to write)
   IoT("lb", lb); IoT("sv", sv);
   double acc = (double)AccountInfoInteger(ACCOUNT_LOGIN); IoD("acc", acc);   // the account it belongs to (checked when loading)
   if(!save) { gSvLast = lb; gSvT = sv; }
   // loss recovery (every rule's state, whichever rule is chosen), total profit (Step-up rule), the hard-cap stop
   IoD("rp", recPool); IoI("rl", recLosses); IoI("du", dUnits); IoD("ca", carried); IoI("pw", parWins); IoI("rd", rdUnits);
   IoI("ou", oscU); IoD("op", oscP); IoD("tn", totalNet); IoI("ew", exW); IoI("el", exLn); IoB("cs", capStop);
   IoD("kl", crkL); IoI("kn", crkN); IoB("kw", crkW); IoI("kp", crkP); IoI("kf", crkF); IoB("ka", crkWait); IoI("kb", crkWW);
   IoB("kc", crkNeedL); IoB("ks", crkSkip); IoI("kt", crkSkipLeft); IoI("ku", crkUDay); IoB("kh", crkHg); IoI("kx", gCrkPrPrev);
   // streaks and pauses; the month of the last bar (a new month while the EA was off) and a restart still waiting for a trade to close
   IoD("dp", dayPnl); IoI("lr", lossRow); IoI("wr", winRow); IoB("db", dayBlock); IoI("pl", pauseLeft); IoB("pa", paused);
   IoI("mk", gMonKey); IoB("mr", monRestPend); IoD("mp", monPnl); IoD("mq", monPeak); IoB("ms", monStop); IoB("ml", monLocked);
   // the trade the EA is in, or its working order: its type and what it booked so far; the broker deals already counted
   IoI("xs", exState); IoB("xl", exL); IoD("xv", exLots); IoD("xr", exRiskAmt); IoD("xc", exCostPx); IoD("xp", exPnl); IoD("xk", exKeepSl);
   IoB("kr", crkRec); IoB("xy", exSynced);
   double xe = exLim, x1 = exTpL[0], x2 = exTpL[1], x3 = exTpL[2];   // v4.4: the trade's setup (arm bar time, entry) and its own TP1-TP3
   IoT("xa", exArmT); IoD("xe", xe); IoD("x1", x1); IoD("x2", x2); IoD("x3", x3); IoT("xt", gTakenT); IoB("xq", gExitRetry);
   ulong cw = (ulong)gCloseId; IoU("xw", cw); gCloseId = (long)cw;   // the last position this EA closed (its report after a restart)
   exLim = xe; exTpL[0] = x1; exTpL[1] = x2; exTpL[2] = x3;
   bool p0 = pDone[0], p1 = pDone[1], p2 = pDone[2];
   IoB("p0", p0); IoB("p1", p1); IoB("p2", p2);
   pDone[0] = p0; pDone[1] = p1; pDone[2] = p2;
   IoB("t1", exT1); IoB("th", exT1Half); IoB("tb", exT1Be); IoB("tm", exT1MvPend); IoD("ts", exT1Stop); IoD("tp", exT1Tp1); IoD("tq", exT1Tp2);
   IoD("tt", exT1Tight); IoD("te", exT1Entry); IoB("hg", exHg); IoD("hs", exHgS); IoD("ht", exHgT);
   IoU("ld", lastDeal);
   // the Labouchere list, last (its length changes)
   int ln = ArraySize(labSeq); IoI("ln", ln);
   if(!save) { if(ln < 1 || ln > 10000) ln = 0; ArrayResize(labSeq, ln); }
   for(int q = 0; q < ln; q++) { double x = save ? labSeq[q] : 0.0; IoD("L" + IntegerToString(q), x); if(!save) labSeq[q] = x; }
   if(!save)
   {
      bool ok = ArraySize(labSeq) > 0;
      for(int q = 0; q < ArraySize(labSeq); q++) if(labSeq[q] <= 0) ok = false;
      if(!ok) LabReset();
      if(exState < 0 || exState > 2) exState = 0;
   }
}
//--- write what changed (force: everything), then flush to disk so it survives a crash or a power cut
void StateSave(bool force)
{
   if(!gPersist || gLastDone <= 0 || gBrokerPend) return;   // not before the engine processed a bar (OnDeinit after a failed start) or the broker part ran
   if(TimeCurrent() - gSvFullT >= 86400) force = true;   // every value at least once a day: MT5 deletes global variables not accessed for 4 weeks
   StateIO(true);
   bool ch = force || gIoC != gSvC;
   for(int q = 0; q < gIoC && !ch; q++)
      if(gIoN[q] != gSvN[q] || (gIoV[q] != gSvV[q] && gIoN[q] != "lb" && gIoN[q] != "sv")) ch = true;
   if(!ch) return;
   for(int q = 0; q < gIoC; q++)
      if(force || q >= gSvC || gIoN[q] != gSvN[q] || gIoV[q] != gSvV[q]) GlobalVariableSet(gSvBase + gIoN[q], gIoV[q]);
   for(int q = gIoC; q < gSvC; q++) GlobalVariableDel(gSvBase + gSvN[q]);   // a shorter Labouchere list
   if(ArraySize(gSvN) < gIoC) { ArrayResize(gSvN, gIoC); ArrayResize(gSvV, gIoC); }
   for(int q = 0; q < gIoC; q++) { gSvN[q] = gIoN[q]; gSvV[q] = gIoV[q]; }
   gSvC = gIoC;
   if(force) gSvFullT = TimeCurrent();
   GlobalVariablesFlush();
}
//--- read the saved state back (false: nothing saved for this symbol, magic number and account)
bool StateLoad()
{
   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer())
   {
      if(GlobalVariableCheck(gSvBase + "lb")) Print("Restart memory: the saved state is incomplete (unused for 4 weeks?): starting fresh.");
      return false;
   }
   double svAcc = GlobalVariableCheck(gSvBase + "acc") ? GlobalVariableGet(gSvBase + "acc") : 0, nowAcc = (double)AccountInfoInteger(ACCOUNT_LOGIN);
   if(svAcc != 0 && nowAcc != 0 && svAcc != nowAcc)    // saved by another account (same symbol and magic number): start fresh
   {
      Print("Restart memory: the saved state belongs to account ", (long)svAcc, ", not ", (long)nowAcc, ": starting fresh.");
      return false;
   }
   StateIO(false);
   gSvAcc = (long)MathRound(svAcc);
   for(int q = ArraySize(labSeq); q < 100000 && GlobalVariableCheck(gSvBase + "L" + IntegerToString(q)); q++) GlobalVariableDel(gSvBase + "L" + IntegerToString(q));   // a longer old list
   gSvC = 0;                                            // the next save writes every value again
   return true;
}
//--- restart memory switched off: forget what was saved
void SvWipe() { GlobalVariablesDeleteAll(gSvBase); GlobalVariablesFlush(); gSvC = 0; }
//--- no trade or working order of this EA: its bookkeeping starts again
void TradeClear()
{
   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false; gExitSeen = false; gGoneWait = false;
   crkRec = false; exT1 = false; exT1Half = false; exT1Be = false; exT1MvPend = false; exT1Stop = 0; exT1Tp1 = 0; exT1Tp2 = 0; exT1Tight = 0; exT1Entry = 0;
   exHg = false; exHgS = 0; exHgT = 0;
   for(int q = 0; q < 3; q++) pDone[q] = false;
}
//--- an exit deal of this EA after the deals already counted (a trade closed while the EA was off)
bool ExitDealAfter(ulong cursor)
{
   if(!HistorySelect(0, TimeCurrent() + 86400)) return false;
   int n = HistoryDealsTotal();
   for(int i = n - 1; i >= 0; i--)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= cursor) continue;
      if(IsExitDeal(tk) && DealIsMine(tk, n)) return true;   // v4.4: also closed by hand, from the phone app or by another EA
   }
   return false;
}
//--- the saved trade after a restart: still open or closed meanwhile (its bookkeeping is kept; booked like after a disconnect), or gone
void RestoreTrade()
{
   int sx = exState;
   ulong tk; double v, op;
   bool posNow = HasPosition(tk, v, op);
   if(sx == 2 || (sx == 1 && (posNow || ExitDealAfter(lastDeal)))) { exState = 2; return; }
   if(sx == 1) gTakenT = 0;                             // an order still waiting when the EA stopped: it is placed again (below)
   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)
   bool c; NewDealsPnl(c, true);                        // no trade of this EA was open: later deals are not its trades
}
//--- OnNewBar's steps 1-2 at start-up: the deals since the saved state, and a trade that closed while the EA was off
void BookBrokerDeals()
{
   bool closedNew; double newPnl = NewDealsPnl(closedNew);
   exPnl += newPnl; totalNet += newPnl;
   if(newPnl != 0 || closedNew) carried = MathMax(0.0, carried - newPnl);
   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   if((exState == 1 && !pos && closedNew) || (exState == 2 && !pos && gExitSeen)) BookClosed();   // without a closing deal yet: the next bar books it
}

//--- the saved state was not this account's: the money-management state starts fresh (as without restart memory)
void MemoryFresh()
{
   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; totalNet = 0; exW = 0; exLn = 0; capStop = false;
   crkL = 0; crkN = 0; crkW = false; crkP = 0; crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false;
   dayPnl = 0; lossRow = 0; winRow = 0; dayBlock = false; pauseLeft = 0; paused = false; monRestPend = false;
   TradeClear(); gDayPendN = 0; gRestFlat = false; gPauseArm = -1; gRestored = false;
}
//--- a force-close time, a weekend start or a news start between two bars (your time zone), as OnNewBar checks it
bool FlatBetween(datetime utPrev, datetime ut)
{
   bool nStart; NewsBlock(ut, nStart, utPrev);
   int fcM = InpFcH * 60 + InpFcM, curM = MinOfDay(ut), prvM = MinOfDay(utPrev);
   bool fcNow = InpFcOn && (curM >= prvM ? (prvM < fcM && curM >= fcM) : (fcM > prvM || fcM <= curM));
   bool wkndStart = InpWeekendOn && DowOf(ut) == 6 && DowOf(utPrev) != 6;
   return fcNow || wkndStart || nStart;
}

//--- reset every engine / execution variable (MT5 keeps globals when inputs or the timeframe change) ---
void ResetEngine()
{
   bi = -1; cumPV = 0; cumPV2 = 0; cumW = 0; cumP = 0; cumP2 = 0; cumN = 0; vwBars = 0; sessN = 0; ArrayResize(vwHist, 0);
   atrV = 0; atrN = 0; atrSum = 0; lastDayKey = -1; lastAnchorKey = -1; gLastDone = 0;
   dayFills = 0; dayW = 0; dayL = 0; dayR = 0; dayRiskR = 0; lossDirBlk = 0;
   bullN = 0; bearN = 0; prevNet = 0; havePrev = false;
   sesO = 0; sesH = 0; sesL = 0; pdH = 0; pdL = 0; haveSes = false; havePd = false;
   st = 0; armBar = -1; fillBar = -1; lastExit = -1; lastFill = -1; lastDir = 0;
   lim = 0; stp = 0; stp0 = 0; trRisk = 0; t1 = 0; t2 = 0; t3 = 0; t4 = 0; tF = 0; tpHit = 0; trHalf = false; trGhost = false;
   totW = 0; totL = 0; totR = 0; gNewDay = false; gDayOk = true; gHourOk = true; gKzOk = true;
   exState = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exPnl = 0; exArm = -1; exSynced = false; gRearm = false; gDrawOn = false; exT1 = false; exT1Half = false; exT1Be = false; exT1MvPend = false; exT1Stop = 0; exT1Tp1 = 0; exT1Tp2 = 0; exKeepSl = 0; exHg = false; exHgS = 0; exHgT = 0; gLastOutProfit = 0;
   sigN = 0; takenN = 0; skipN = 0; missN = 0; skipWhy = "";
   gVirt = false; gDayPendN = 0; gPrevT = 0; capStop = false; gT1Seen = false; gPauseArm = -1;   // crkUDay is kept with the pause (MT5 keeps globals)
   for(int q = 0; q < 3; q++) pDone[q] = false;
   trSkip = 0; lastRes = "-"; bestPx = 0; ghW = 0; ghL = 0; ghR = 0;
   vxSide = 0; vxN = 0; tchL = 1000000; tchS = 1000000; hK = -1; hC = 0; hSum = 0; hNum = 0; ArrayInitialize(hE, 0.0);
   ArrayInitialize(tpHitN, 0); beN = 0; lkN = 0; gFirstT = 0;
   gDrawT = 0; ArrayResize(gDrawn, 0); gStateTxt = "SCANNING";
   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = ""; gExitSeen = false; gGoneWait = false;
   gOurFill = false; gOurExit = false; gOurWin = false; gOurMove = false; gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
}

//--- events -----------------------------------------------------------------
//--- the broker part of a start: the deals since the saved state, the month, the saved trade, adoption, orders (restart memory: once connected)
void BrokerStart()
{
   long nowAcc = AccountInfoInteger(ACCOUNT_LOGIN);
   if(gRestored && gSvAcc != 0 && nowAcc != 0 && gSvAcc != nowAcc)   // only known now: the saved state belongs to another account
   {
      Print("Restart memory: the saved state belongs to account ", gSvAcc, ", not ", nowAcc, ": starting fresh.");
      MemoryFresh();
   }
   TzPick(false);                                        // the broker's clock, now that MT5 is connected
   gHedgeOk = (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;   // known for sure once connected
   if(!gRestored) { bool c; NewDealsPnl(c, true); }      // do not count old history (restored: the deals since the saved state are booked below)
   if(!gRestored) MonthFromHistory();                    // this month's closed profit and the monthly locks from the deal history
   else
   {
      datetime b1 = iTime(_Symbol, _Period, 1);
      MonthTick(UserTime(b1 > 0 ? b1 : TimeCurrent()));  // restored: the saved month goes on, or a new month began while the EA was off (locks start again)
      RestoreTrade();                                    // the saved trade: still open, closed while the EA was off, or gone
   }
   // restart: adopt this EA's open position if the engine is in the same trade, keep managing it
   ulong tk; double vol, op;
   if(HgOpen()) { exState = 2; exHg = true; Print("Hedge pair still open: its trades run to their own stop loss and take profit."); }
   else if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      double pSl = PositionGetDouble(POSITION_SL), pTp = PositionGetDouble(POSITION_TP);
      datetime aT = MathAbs(st) >= 1 && !trGhost ? BarTimeOf(armBar) : 0;
      // v4.4: the engine's setup is this trade's when it is the saved setup, re-linked in the warm-up (restart memory) and still the engine's;
      // without a saved setup, when it has the trade's direction and was armed before the trade opened
      bool same = MathAbs(st) >= 1 && !trGhost && (st > 0) == isL &&
                  (gRestored && exArmT > 0 ? exArm >= 0 && armBar == exArm
                                           : aT > 0 && (datetime)PositionGetInteger(POSITION_TIME) >= aT + PeriodSeconds(_Period));
      exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol;   // a restored trade keeps its lots (partials)
      if(same && exTpL[0] <= 0) { exTpL[0] = t1; exTpL[1] = t2; exTpL[2] = t3; }   // the trade's own TP1-TP3 (partials)
      if(same && MathAbs(st) == 2)
      {
         exArm = armBar; if(exArmT <= 0) exArmT = aT; exLim = lim; exSynced = true;
         for(int q = 0; q < 3; q++) pDone[q] = pDone[q] || tpHit >= q + 1;
         Print("Adopted open position #", tk, " (engine is in the same trade).");
         // never widen the stop of an adopted position (a Crooks TP1-rule position is sized for its tighter stop): SetExits keeps it from now on
         exKeepSl = pSl > 0 && (isL ? pSl > StopPx(isL) : pSl < StopPx(isL)) ? pSl : 0;
         SetExits(true);
      }
      else if(same)
      {
         exArm = armBar; if(exArmT <= 0) exArmT = aT; exLim = lim; exSynced = false;
         Print("Open position #", tk, " kept: it filled before the engine's fill (bid chart); the engine's setup is still armed.");
      }
      else
      {
         exArm = -1; exSynced = gRestored && exSynced;
         Print("Open position #", tk, " kept: the engine is not in it (its setup ended, new inputs or another timeframe). It runs to its own stop loss ",
               DoubleToString(pSl, _Digits), " and take profit ", pTp > 0 ? DoubleToString(pTp, _Digits) : "(none)", ".");
      }
   }
   if(!(gRestored && exHg && exState == 2)) CancelPending();   // a pending order from before the restart has no tracked state (a restored hedge pair keeps its waiting trade)
   if(gRestored)                                         // the days and the broker's deals since the saved state, booked like after a disconnect
   {
      DayStart(gDayPendN); gDayPendN = 0;
      // Crooks TP1 rule: TP1 was reached while the EA was off and its part is not booked yet: it is booked at the next bar close
      int s0 = iBarShift(_Symbol, _Period, gLastDone, true); if(s0 < 1) s0 = 1;   // the last processed bar (later bars: the catch-up checks them)
      if(exState == 2 && exT1 && !exT1Half && exSynced)
         for(int s = s0; s < Bars(_Symbol, _Period); s++)
         {
            if(iTime(_Symbol, _Period, s) <= gSvLast || bi - (s - s0) <= lastFill) break;
            if(exL ? Hi(s) >= exT1Tp1 + exCostPx : Lo(s) <= exT1Tp1 - exCostPx) { gT1Seen = true; break; }
         }
      BookBrokerDeals();
      ulong rTk; double rVol, rOp;
      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseRule("a force-close, weekend start or news start passed while the EA was off"); BookBrokerDeals(); }
      // v4.4: the engine's stop (or its final target without earn-back) of this trade was reached while the EA was off: closed now, as after a
      // disconnect (earn-back and the Crooks TP1 rule only outlive a win; its TP1 part is booked at the next bar close)
      if(gMissExit && exState == 2 && !exHg && HasPosition(rTk, rVol, rOp) && (!InpEarnBack || !gMissWin) && !(exT1 && (gMissWin || exT1Half)))
      { CloseRule(gMissWin ? "the engine's final target was reached while the EA was off" : "the engine's stop was hit while the EA was off"); BookBrokerDeals(); }
      if(gRestFlat && exHg && exState == 2) CancelPending();
      if(monRestPend && exState == 0 && !HasPosition(rTk, rVol, rOp)) { monRestPend = false; RecoveryRestart(); }
      MonthCheck();
      bool isCC = InpRec == REC_C || InpRec == REC_CS, isKK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;
      Print("Restart memory: continued from ", DateTxt(UserTime(gSvT), true), " | loss to win back ", DoubleToString(isCC ? carried : isKK ? crkL : recPool, 2),
            " | streak ", winRow, "W / ", lossRow, "L", (paused || pauseLeft > 0) ? " | paused" : "", CrkPause() ? " | Crooks C pause" : "",
            capStop ? " | hard cap stop" : "", exState == 2 ? " | trade still open" : "");
   }
   gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;   // the warm-up's events for the saved trade are handled above
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm && (gTakenT == 0 || BarTimeOf(armBar) != gTakenT);   // re-place the engine's armed setup on the first tick (not one armed while paused, not one already decided on)
}

//--- one copy per symbol + magic number: two copies cancel and close each other's trades and share one restart memory. A temporary global
//--- variable (gone when MT5 closes) holds the chart of the copy that runs; a lock of a chart that no longer runs an EA is taken over
bool LockTake()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return true;
   gLockN = SvExtra("run");
   gLockV = (double)(ChartID() & 0xFFFFFFFFFFFF) + 1.0;  // 48 bits of the chart id (exact in a double), never 0
   if(!GlobalVariableCheck(gLockN)) GlobalVariableTemp(gLockN);
   if(GlobalVariableSetOnCondition(gLockN, gLockV, 0)) return true;
   double cur = GlobalVariableGet(gLockN);
   if(cur == gLockV) return true;                        // this chart (new inputs, another timeframe)
   for(long id = ChartFirst(); id >= 0; id = ChartNext(id))
      if(id != ChartID() && (double)(id & 0xFFFFFFFFFFFF) + 1.0 == cur && ChartGetString(id, CHART_EXPERT_NAME) != "") return false;   // that chart still runs it
   return GlobalVariableSetOnCondition(gLockN, gLockV, cur);   // that chart is gone: take over
}
void LockFree() { if(gLockN != "" && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableSetOnCondition(gLockN, 0, gLockV); }
//--- a note on the other EAs in this MetaTrader: one that manages every trade of the account can close this EA's trades (the log then names
//--- who closed each trade); an alert for an older copy of this EA on the same symbol (it has no lock and may use the same magic number)
void OtherEAs()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;
   string lst = ""; bool twin = false;
   for(long id = ChartFirst(); id >= 0; id = ChartNext(id))
   {
      if(id == ChartID()) continue;
      string nm = ChartGetString(id, CHART_EXPERT_NAME);
      if(nm == "") continue;
      lst += (lst == "" ? "" : ", ") + nm + " (" + ChartSymbol(id) + " " + StringSubstr(EnumToString(ChartPeriod(id)), 7) + ")";
      if(ChartSymbol(id) != _Symbol || StringFind(nm, "AuctionRetest") != 0) continue;
      bool locked = false;                               // a v4.4+ copy holds a lock (its own magic number, else this start would have failed)
      for(int q = GlobalVariablesTotal() - 1; q >= 0 && !locked; q--)
      {
         string g = GlobalVariableName(q);
         if(StringFind(g, "ARX|") == 0 && StringFind(g, "|run") == StringLen(g) - 4 && GlobalVariableGet(g) == (double)(id & 0xFFFFFFFFFFFF) + 1.0) locked = true;
      }
      if(!locked) twin = true;
   }
   if(lst != "") Print("Other EAs running in this MetaTrader: ", lst, ". An EA that manages every trade of the account can close this EA's trades: the log names who closed each trade.");
   if(twin)
   {
      string m = "Another chart on " + _Symbol + " runs an older AuctionRetestEA. If it uses the same magic number (" + IntegerToString(InpMagic) +
                 "), the two copies cancel and close each other's trades: remove one, or give each its own magic number.";
      Print(m); Alert(m);
   }
}

int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(50);
   trade.SetTypeFillingBySymbol(_Symbol);
   ResetEngine();
   if(ArraySize(labSeq) == 0) LabReset();               // the Labouchere list is kept with the other recovery states when inputs change
   // restart memory: on a fresh start (MT5 or the EA restarted) continue from the saved state; switched off: forget it
   gPersist = InpRemember && MQLInfoInteger(MQL_TESTER) == 0 && MQLInfoInteger(MQL_OPTIMIZATION) == 0;
   gSvBase = SvBaseName(); gRestored = false;
   if(!LockTake())
   {
      string m = "Another copy of this EA runs on " + _Symbol + " with magic number " + IntegerToString(InpMagic) + " (another chart). Two copies cancel and close " +
                 "each other's trades: remove one, or give each its own magic number.";
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   TzPick(true);                                         // the broker's clock (Auto), before the warm-up uses it
   if(MQLInfoInteger(MQL_TESTER) == 0)                   // the timeframe the EA trades: the one it was attached to (also after a restart)
   {
      string tfN = SvExtra("tf");
      if(gTfTrade == 0) gTfTrade = GlobalVariableCheck(tfN) ? (int)MathRound(GlobalVariableGet(tfN)) : (int)_Period;
      GlobalVariableSet(tfN, gTfTrade);
      if(TfHold())
      {
         string m = "The chart is on " + TfName((int)_Period) + ", but this EA trades " + TfName(gTfTrade) + " (the timeframe it was attached to): no new trades until the chart is back on " +
                    TfName(gTfTrade) + ". The open trade keeps its stop loss and take profit. To trade " + TfName((int)_Period) + ", remove the EA and attach it again.";
         Print(m); Alert(m);
      }
   }
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();
   gRestFlat = false; gBrokerPend = false;
   // Start fresh once: forget the money-management state (kept by MT5 on new inputs and by the restart memory); done once while it is on
   string rsN = SvExtra("rsd");
   if(MQLInfoInteger(MQL_TESTER) == 0)
   {
      if(!InpMemFresh) GlobalVariableDel(rsN);
      else if(!GlobalVariableCheck(rsN))
      {
         SvWipe(); MemoryFresh(); GlobalVariableSet(rsN, 1);
         Print("Started fresh: the loss recovery, streaks and pauses start again from the base risk. Set 'Start fresh once' back to false.");
      }
   }
   if(gPersist) gRestored = StateLoad();                 // a fresh start or new inputs: continue from the saved state (written at OnDeinit)
   if(gRestored && (gInitDone || !InpCapOn || InpCapAction != CAP_STOP)) capStop = false;   // a hard-cap Stop ends with new inputs (as before) or a cap that no longer stops
   if(gCrkPrPrev != (int)InpCrkPr || InpRec != REC_CRC) { crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; }
   gCrkPrPrev = (int)InpCrkPr;
   gHedgeOk = (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && !gHedgeOk) Print("Crooks C hedge rule: this account cannot hold a buy and a sell together (netting), so the rule forgets the loss instead.");
   // markings and table only where they can be seen (not in non-visual tests or optimisation)
   gCanDraw = MQLInfoInteger(MQL_OPTIMIZATION) == 0 && (MQLInfoInteger(MQL_TESTER) == 0 || MQLInfoInteger(MQL_VISUAL_MODE) != 0);
   ObjectsDeleteAll(0, "ARM_");
   if(InpSpread < 0 || InpCommLot < 0) { Print("Spread and commission must be 0 or more."); return INIT_PARAMETERS_INCORRECT; }
   if(InpTp1R > InpTp2R || InpTp2R > InpTp3R || InpTp3R > InpTp4R) { Print("Targets must be in order: TP1 <= TP2 <= TP3 <= TP4."); return INIT_PARAMETERS_INCORRECT; }
   if(InpMaxVwOn && InpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpTouchVwOn && InpTouchVwN < 1) { Print("VWAP touched in the last N candles: N must be 1 or more."); return INIT_PARAMETERS_INCORRECT; }
   if(InpCrkT1 && (InpCrkT1Pct < 10 || InpCrkT1Pct > 90)) { Print("Crooks TP1 rule: % closed at TP1 must be 10 to 90."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr != CPR_OFF && (InpCrkPrN < 1 || InpCrkPrM < 1 || InpCrkPrD < 1)) { Print("Crooks C rule: N, M and D must be 1 or more."); return INIT_PARAMETERS_INCORRECT; }
   if((InpMLockOn && InpMLockAmt <= 0) || (InpPLockOn && (InpPLockAt <= 0 || InpPLockPct < 1 || InpPLockPct > 100))) { Print("Monthly profit lock: the amounts must be above 0 and the lock % 1 to 100."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0 || InpCrkHgTp <= 0)) { Print("Crooks C hedge rule: stop loss and take profit must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100)) { Print("Crooks C rule: % of the loss must be 10 to 100."); return INIT_PARAMETERS_INCORRECT; }
   // warm up the engine on history (no orders): it ends in the same state as the TradingView engine would
   int bars = Bars(_Symbol, _Period);
   int look = (int)MathMax(MathMax(InpStructLen, InpBrkLen + 1), MathMax(InpMomLen + 1, InpStopLen)) + 2;
   int need = look + InpAtrLen + 10;
   if(bars < need) { Print("Not enough chart history yet (", bars, " bars, need ", need, "); scroll the chart back or load more history, then attach the EA again."); return INIT_FAILED; }
   int start = (int)MathMin(InpWarmBars, bars - look - 1);
   if(gRestored && gSvLast > 0)                         // reach back to the saved bar, so every day since then is counted (at most 100,000 bars)
   {
      int sh = iBarShift(_Symbol, _Period, gSvLast, false);
      if(sh < 0 || sh > start) start = (int)MathMin(sh < 0 ? 100000 : MathMin(sh, 100000), bars - look - 1);
   }
   gLive = false;
   for(int s = start; s >= 1; s--)
   {
      bool offBar = gRestored && gSvLast > 0 && iTime(_Symbol, _Period, s) > gSvLast;   // the bars since the saved state count like bars missed in a disconnect
      if(offBar) EngStep(s); else ProcessBar(s);
      // v4.4: the saved trade's setup is re-linked when the engine arms it again (its arm bar, direction and entry): its fill, stop moves and
      // exit on the bars since the saved state then reach the trade (gMiss*), like after a disconnect
      if(gRestored && exArmT > 0 && exState != 0 && !exHg && evArm && iTime(_Symbol, _Period, s) == exArmT && (st > 0) == exL &&
         (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5)) exArm = armBar;
      if(offBar)
      {
         if(gOurFill) gMissFill = true;
         if(gOurMove) gMissMove = true;
         if(gOurExit) { gMissExit = true; gMissWin = gOurWin; }
         if(gNewDay) gDayPendN++;
         CrkDayTick(iTime(_Symbol, _Period, s));          // Crooks C skip rule: the days that passed
         if(evArm && CrkPause()) gPauseArm = armBar;      // armed while paused: the strategy skips it, so it is not placed now
         if(FlatBetween(UserTime(iTime(_Symbol, _Period, s + 1)), UserTime(iTime(_Symbol, _Period, s)))) gRestFlat = true;
      }
   }
   gLive = true;
   gLastBarTime = iTime(_Symbol, _Period, 0);
   // the broker part (deals, positions, orders): now when MT5 is connected, else at the first tick once it is (positions are not visible before)
   gBrokerPend = MQLInfoInteger(MQL_TESTER) == 0 && (TerminalInfoInteger(TERMINAL_CONNECTED) == 0 || AccountInfoInteger(ACCOUNT_LOGIN) == 0);
   if(gBrokerPend) Print("Waiting for the connection to the trade server before checking positions and deals.");
   else BrokerStart();
   gStateTxt = StateText(false);
   UpdateTable();
   StateSave(true);                                      // restart memory: the state after this start
   OtherEAs();
   gInitDone = true;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   LockFree();
   bool gone = reason == REASON_REMOVE || reason == REASON_CHARTCLOSE || reason == REASON_INITFAILED || reason == REASON_PROGRAM || reason == REASON_TEMPLATE;
   if(gone && gTfTrade > 0 && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableDel(SvExtra("tf"));   // left the chart: attach it again on any timeframe
   Comment("");
   // after a Strategy Tester run the markings stay on the visual chart; everywhere else they are removed with the EA
   if(MQLInfoInteger(MQL_TESTER) == 0) ObjectsDeleteAll(0, "ARM_");
}

void OnChartEvent(const int id, const long &lparam, const double &dparam, const string &sparam)
{
   if(id != CHARTEVENT_CHART_CHANGE || !InpShowTable || !gCanDraw) return;
   // keep the table in its corner when the chart window is resized (scrolling does not move it)
   int cw = (int)ChartGetInteger(0, CHART_WIDTH_IN_PIXELS), chh = (int)ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);
   if(cw != gTblW || chh != gTblH) UpdateTable();
}

void OnTick()
{
   if(gBrokerPend)                                       // restart memory: the broker part of the start, once MT5 is connected
   {
      if(TerminalInfoInteger(TERMINAL_CONNECTED) == 0 || AccountInfoInteger(ACCOUNT_LOGIN) == 0) return;
      gBrokerPend = false; BrokerStart(); gStateTxt = StateText(false); UpdateTable();
   }
   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 != gLastBarTime)
   {
      gLastBarTime = t0;
      int sh = gLastDone > 0 ? iBarShift(_Symbol, _Period, gLastDone, true) : -1;   // 2 = nothing missed, 1 = bar 1 already processed
      if(sh == 1) { VirtualEntry(); ManagePartials(); StateSave(false); return; }
      gPrevT = gLastDone;
      bool caught = false; long biBefore = bi;
      for(int s = sh - 1; s >= 2; s--)                                 // bars missed while offline: engine only
      {
         EngStep(s); caught = true; if(gNewDay) gDayPendN++;
         if(gOurFill) gMissFill = true;                                  // this trade's fill, stop move or exit on a missed bar: handled by OnNewBar
         if(gOurMove) gMissMove = true;
         if(gOurExit) { gMissExit = true; gMissWin = gOurWin; }
         CrkDayTick(iTime(_Symbol, _Period, s));                          // Crooks C skip rule: count the missed days too
         if(evArm && CrkPause()) gPauseArm = armBar;                      // armed while paused: the strategy skips it, so it is not placed on reconnect
         // Crooks TP1 rule: a missed bar after the engine's fill of this setup reached TP1 and the TP1 part is not booked: book it on this bar
         // (exState may still be 1 when the broker filled during the disconnect; with no position nothing is booked)
         if(exState != 0 && exT1 && !exT1Half && exArm >= 0 && exArm == armBar && lastFill > exArm && lastFill < bi && (exL ? Hi(s) >= exT1Tp1 + exCostPx : Lo(s) <= exT1Tp1 - exCostPx)) gT1Seen = true;
      }
      OnNewBar();
      if(caught && exState == 2 && MathAbs(st) == 2 && exArm == armBar && !exHg) SetExits(true);   // re-sync stop moves of the missed bars
      if(caught && !evArm && MathAbs(st) == 1 && !trGhost && exState == 0 && armBar > biBefore && armBar != gPauseArm) gRearm = true;   // armed on a caught-up bar: place it now
   }
   if(gRearm)
   {
      gRearm = false;
      if(MathAbs(st) == 1 && !trGhost && exState == 0)
      {
         bool ns; datetime un = UserTime(TimeCurrent());
         bool nb = NewsBlock(un, ns, un);
         TakeSetup(st == 1, nb, false);
      }
   }
   VirtualEntry();
   ManagePartials();
   StateSave(false);                                    // restart memory: written only when something changed
}
//+------------------------------------------------------------------+
