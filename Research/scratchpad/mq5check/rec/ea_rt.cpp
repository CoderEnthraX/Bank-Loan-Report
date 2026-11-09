#include "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/mql5rt_rec.h"
#line 1 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
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
//+------------------------------------------------------------------+






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
  
 int    InpStructLen    = 10;    // Structure lookback (bars)
 int    InpBrkLen       = 6;     // Signal break lookback (bars)
 int    InpEntryLen     = 6;     // Entry level lookback (bars)
 int    InpRetestBars   = 5;     // Retest window (bars)
 double InpDispAtr      = 0.8;   // Min displacement range (x ATR)
 double InpBodyPct      = 55.0;  // Min displacement body (% of range)
 double InpClosePct     = 25.0;  // Max close distance from extreme (% of range)
 int    InpMomLen       = 10;    // Momentum lookback (bars)
 double InpMomAtr       = 0.85;  // Min momentum (x ATR, 0 = off)
 double InpCmoMin       = 20.0;  // Min CMO, clean move (0 = off)
 ENUM_REARM InpRearm    = REARM_KEEP; // Same-direction re-arm
 ENUM_STOP_MODE InpStopMode = STOP_ATR; // Stop mode
 double InpStopAtr      = 1.8;   // Stop distance (x ATR)
 int    InpStopLen      = 6;     // Swing lookback (bars)
 double InpStopBufAtr   = 0.22;  // Swing buffer (x ATR)
 bool   InpHalfStop     = true;  // Half stop on first counter-bias impulse
 double InpHalfStopAtr  = 0.9;   // Half stop (x ATR)
 int    InpBiasNet      = 3;     // Prev session net impulses
 double InpImpBody      = 50.0;  // Impulse min body (% of range)
 bool   InpHalfOpenOut  = true;  // Half stop when session opens outside prev range
 bool   InpHalfStrict   = false; // Strict bias check (optional)
 bool   InpHalfCap      = true;  // Half stop never wider than the normal stop (optional)
 int    InpCooldown     = 1;     // Cooldown after exit (bars)
 int    InpMaxFills     = 10;    // Max fills per day
 double InpDayStopR     = 0.0;   // Daily stop (R lost, 0 = off)
 bool   InpFillBarStopR = false; // Count fill-bar stops in daily stop
 bool   InpLegReset     = true;  // Re-anchor breakout after a trade
 int    InpAtrLen       = 14;    // ATR length (Wilder / RMA)
 bool   InpVwapFilter   = true;  // Longs above VWAP / shorts below
 int    InpSlopeBars    = 3;     // VWAP slope bars (0 = off)
 bool   InpSlopeCross   = true;  // Slope looks across the session start
 int    InpMinOpenBars  = 0;     // Skip first bars after the daily reset
 bool   InpSkipSunday   = true;  // Skip Sunday (UTC) weekly open
 bool   InpDeepOn       = false; // Deep pullback signal (optional)
 double InpDeepFar      = 2.0;   //   min depth (x ATR)
 bool   InpAllowLong    = true;  // Longs
 bool   InpAllowShort   = true;  // Shorts

enum ENUM_VW_ANCHOR { VW_SESSION = 0, // Session
                      VW_WEEK    = 1, // Week
                      VW_MONTH   = 2 };// Month
  
 ENUM_VW_ANCHOR     InpVwapAnchor = VW_SESSION;    // Anchor
 ENUM_APPLIED_PRICE InpVwapSrc    = PRICE_TYPICAL; // Source (typical = hlc3)

  
 ENUM_ENTRY_MODE InpEntryMode = ENTRY_MODEL; // Entry price
 double InpEntryPct     = 25.0;  // Custom % (0 = close, 50 = mid, 100 = low/high)

  
 double InpTp1R = 0.6;  // TP1 (R)
 double InpTp2R = 1.0;  // TP2 (R)
 double InpTp3R = 1.5;  // TP3 (R)
 double InpTp4R = 2.0;  // TP4 (R)
 ENUM_EXIT_AT InpExitAt = EXIT_TP1; // Final exit at
 bool   InpMv1On = false; // When TP1 hits, move stop
 double InpMv1R  = 0.0;   //   ...to (R, 0 = breakeven)
 bool   InpMv2On = false; // When TP2 hits, move stop (breakeven at +1R: on, 0)
 double InpMv2R  = 0.6;   //   ...to (R)
 bool   InpMv3On = false; // When TP3 hits, move stop
 double InpMv3R  = 0.0;   //   ...to (R)

  
 bool   InpNoChase    = false; // Don't chase: skip signals beyond N sigma from VWAP
 double InpNoChaseSig = 2.0;   //   sigma from VWAP
 bool   InpLossBlock  = false; // After a loss, no same-direction trade until a win
 bool   InpChopOn     = false; // Skip choppy sessions (too many VWAP crosses)
 double InpChopMax    = 13.5;  //   max VWAP crosses per 100 bars
 bool   InpEmaOn      = false; // Skip when the 1h EMA20 moved too fast (natural gas: worse)
 double InpEmaMax     = 1.65;  //   max 1h EMA20 move in 3 hours (x ATR)
 bool   InpMinVwOn    = false; // Skip signals too close to VWAP (min distance)
 double InpMinVwAtr   = 1.0;   //   min distance of the signal close from VWAP (x ATR)
 bool   InpMaxVwOn    = false; // Skip signals too far from VWAP (max distance)
 double InpMaxVwDist  = 5.0;   //   max distance of the signal close from VWAP, above or below
 ENUM_VW_UNIT InpMaxVwUnit = VWU_ATR; //   ...measured in ATR or in price
 bool   InpStopVwOn   = false; // Skip when the stop is beyond the VWAP
 double InpStopVwBuf  = 0.0;   //   buffer (x ATR; 0 = stop on the trade's side, -1 = up to 1 ATR past it)
 bool   InpTouchVwOn  = false; // Skip when the VWAP was touched in the last N candles
 int    InpTouchVwN   = 3;     //   N candles (1 = the signal candle only)
 bool   InpEntVwOn    = false; // Skip when the entry is too close to the VWAP
 double InpEntVwAtr   = 0.75;  //   min distance of the entry from the VWAP (x ATR)

  
enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // Auto: GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1,   // Fixed: the GMT offset below
                   SRV_EET     = 2 }; // Auto: GMT+2 winter / GMT+3 EU summer time (EET brokers, e.g. FxPro)
 ENUM_SRV_TZ InpServerTz = SRV_EET;     // Broker server clock
 double InpServerGMT = 2.0;   // Broker server time zone if fixed (GMT +h; check Market Watch time)
 double InpUserGMT   = 5.5;   // Your time zone (GMT +h; India = 5.5)
 bool   InpDayOn     = true;  // Trade only on the ticked days
 bool   InpMon       = false; //   Monday
 bool   InpTue       = true;  //   Tuesday
 bool   InpWed       = true;  //   Wednesday
 bool   InpThu       = true;  //   Thursday
 bool   InpFri       = false; //   Friday
 bool   InpSat       = false; //   Saturday
 bool   InpSun       = false; //   Sunday
 bool   InpHoursOn   = true;  // Trade only between
 int    InpStartH    = 6;     //   start hour
 int    InpStartM    = 0;     //   start minute
 int    InpEndH      = 23;    //   end hour
 int    InpEndM      = 0;     //   end minute
enum ENUM_KZ_SHIFT { KZ_M2 = -2,  // -2 hours
                     KZ_M1 = -1,  // -1 hour
                     KZ_0  = 0,   // 0 (as listed)
                     KZ_P1 = 1,   // +1 hour
                     KZ_P2 = 2 }; // +2 hours
 bool   InpKzOn      = true;  // Trade only in kill zones (Indian time, IST)
 bool   InpKzAsia    = true;  //   Asia 05:30-09:30 IST
 bool   InpKzLon     = true;  //   London 11:30-14:30 IST (UK winter time: 1 hour later with the switch below)
 bool   InpKzNy      = true;  //   New York 16:30-19:30 IST (US winter time: 1 hour later with the switch below)
 bool   InpKzLc      = false; //   London close 19:30-21:30 IST (UK winter time: 1 hour later with the switch below)
 bool   InpKzAuto    = true;  //   follow London / New York summer time (winter: those zones 1 hour later)
 ENUM_KZ_SHIFT InpKzShift = KZ_0; //   shift all kill zones (on top of the summer time switch)

//--- EXECUTION inputs (EA only)
  
 double InpP1   = 0.0;  // Close % at TP1 (0 = no partial)
 double InpP2   = 0.0;  // Close % at TP2
 double InpP3   = 0.0;  // Close % at TP3

  
 double InpBaseRisk = 50.0;   // Base risk per trade (account currency)
 bool   InpCapOn    = false;  // Hard cap: max loss per trade
 double InpHardCap  = 250.0;  // Hard cap amount
 ENUM_CAP_ACTION InpCapAction = CAP_RESET; // If the risk would exceed the cap
 double InpLeverage = 100.0;  // Leverage cap 1:x (0 = broker margin only)
 double InpLotStep  = 0.0;    // Lot step (0 = broker's volume step)
 ENUM_LOT_ROUND InpLotRound = LOTR_DOWN;  // Lot rounding (nearest: 0.125 -> 0.13; never past the hard cap or leverage)
 ENUM_SMALL_LOT InpSmallLot = SMALLL_MIN; // Size below the minimum lot (e.g. 0.004 -> 0.01)

  
 double InpSpread   = 0.16;   // Spread for sizing and earn-back (price, like TradingView's Spread; 0 = the live spread)
 double InpCommLot  = 7.0;    // Commission per lot, round trip (sizing / earn-back; FxPro gold: 7)
 bool   InpEarnBack = true;   // Extend targets to earn back commission + spread
 bool   InpBidChart = true;   // Match bid-chart levels (shift buy-side orders by the spread)

  
 bool InpLStopOn = false; // Stop for the day after N losses in a row
 int  InpLStopN  = 23;    //   N losses
 bool InpWStopOn = false; // Stop for the day after N wins in a row
 int  InpWStopN  = 3;     //   N wins
 bool InpPauseOn = false; // Pause after N losses in a row
 int  InpPauseN  = 3;     //   N losses
 int  InpPauseDays = 1;   //   Days to pause (1-3)

  
 bool   InpMLockOn  = false;  // Stop for the month once it is up (closed profit this month, your time zone)
 double InpMLockAmt = 150.0;  //   amount (account currency)
 bool   InpPLockOn  = false;  // Lock profit once the month is up (stop when it falls back to the locked part)
 double InpPLockAt  = 500.0;  //   amount (account currency)
 double InpPLockPct = 20.0;   //   lock % of the month's highest profit (rises with new highs)
 bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (after a trade still open closes)

  
 bool   InpRemember = true;   // Continue after a restart (keep the loss recovery, streaks and pauses when MT5 or the EA restarts)

  
 bool   InpFcOn      = true;  // Force-close open trades daily at
 int    InpFcH       = 23;    //   hour
 int    InpFcM       = 55;    //   minute
 bool   InpWeekendOn = true;  // Close open trades when Saturday starts
 int    InpNewsPre   = 60;    // No new trades before news (minutes)
 bool   InpDNewsOn   = true;  // Daily news window
 int    InpDNewsH    = 17;    //   start hour
 int    InpDNewsM    = 45;    //   start minute
 int    InpDNewsDur  = 30;    //   length (minutes)
 bool   InpDNewsAuto = true;  //   keep the same New York time all year (US winter time: 1 hour later)
 bool     InpN1On = false;        // News 1
 datetime InpN1T  = ((datetime)1767310200LL); //   date and time (your time zone)
 int      InpN1Dur = 60;          //   length (minutes)
 bool     InpN2On = false;        // News 2
 datetime InpN2T  = ((datetime)1767310200LL); //   date and time
 int      InpN2Dur = 60;          //   length (minutes)
 bool     InpN3On = false;        // News 3
 datetime InpN3T  = ((datetime)1767310200LL); //   date and time
 int      InpN3Dur = 60;          //   length (minutes)
 bool     InpN4On = false;        // News 4
 datetime InpN4T  = ((datetime)1767310200LL); //   date and time
 int      InpN4Dur = 60;          //   length (minutes)
 bool     InpN5On = false;        // News 5
 datetime InpN5T  = ((datetime)1767310200LL); //   date and time
 int      InpN5Dur = 60;          //   length (minutes)

  
 ENUM_REC InpRec    = REC_CRC; // Loss recovery
 int    InpRecN     = 3;      // N trades (Over N / Delayed)
 double InpRecPct   = 50.0;   // % of losses (% mode)
 double InpRecMult  = 2.0;    // Multiplier (Martingale / Grand)
 double InpRecStep  = 25.0;   // Step amount (Step-up)
 int    InpCSplit   = 2;      // Rule C / Crooks B: split the loss over this many trades
 bool   InpCrkT1    = false;   // Crooks TP1 rule (exit TP1): bank the loss at TP1 with part, rest to TP2
 ENUM_T1_STOP InpCrkT1Stop = T1S_FULL; //   ...stop before TP1 (the size is the same; the hard cap covers the real stop-out loss)
 double InpCrkT1Pct = 50.0;   //   ...% closed at TP1 (10-90; that part alone banks the whole loss)
 bool   InpCrkT1Any = false;  //   ...with any final exit (not only TP1; the rest still runs to TP2)
 bool   InpCrkCnOn  = false;  // Crooks C: win the loss back over N wins
 int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)
 ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C: after N losing recovery trades in a row
 int    InpCrkPrN   = 2;      //   ...N losing recovery trades in a row
 double InpCrkPrPct = 50.0;   //   ...% of the loss each recovery trade goes for (the % rule, 10-100)
 int    InpCrkPrM   = 2;      //   ...M wins in a row to wait for (the wait rule)
 int    InpCrkPrD   = 4;      //   ...D trading days to skip (the skip rule; the rest of that day is skipped too)
 bool   InpCrkPrForget = false; //   ...forget the loss after the skipped days (the skip rule)
 bool   InpCrkPrAll = false;  //   ...count every day, not only the trading days (the skip rule)
 double InpCrkHgSl  = 1.0;    //   ...hedge rule: stop loss of the buy and the sell (R: 1 = the signal's own stop)
 double InpCrkHgTp  = 0.6;    //   ...hedge rule: take profit of the buy and the sell (R: 0.6 = TP1)
 ENUM_HG_UNIT InpCrkHgUnit = HGU_R; //   ...hedge rule: stop loss and take profit in R or in price
 bool   InpCrkHgForget = true; //   ...hedge rule: forget the loss after the pair (off: Crooks C goes on from the trade that closed last)
 int    InpParN     = 3;      // Paroli: wins before reset
 int    InpDelayN   = 2;      // Delayed: losses before recovery starts
 double InpEqPct    = 1.0;    // % of equity (% mode)

enum ENUM_TBL_POS { TBL_TOP_RIGHT    = 0,  // Top right
                    TBL_TOP_LEFT     = 1,  // Top left
                    TBL_BOTTOM_RIGHT = 2,  // Bottom right
                    TBL_BOTTOM_LEFT  = 3 };// Bottom left
  
 bool   InpDraw      = true;              // Show trade markings (entry, stop, targets, result)
 int    InpMaxDrawn  = 0;                 //   trades kept on the chart (0 = all)
 color  InpColTarget = clrMediumSeaGreen; //   target box and TP lines
 color  InpColStop   = clrIndianRed;      //   stop box
 color  InpColEntry  = clrDodgerBlue;     //   entry line and armed limit
 bool   InpShowTable = true;              // Show the table
 ENUM_TBL_POS InpTablePos = TBL_TOP_RIGHT;//   table position
 int    InpTableFont = 8;                 //   table font size

  
 mql_long   InpMagic    = 240611; // Magic number
 int    InpWarmBars = 3000;   // Bars used to warm up the engine (VWAP / ATR / counters / state)

//--- globals ----------------------------------------------------------
CTrade   trade;
datetime gLastBarTime = 0;
mql_long     bi = -1;                  // bar_index of the last processed (closed) bar
bool     gLive = false;            // false while warming up: no orders

// ENGINE state (names as in the Pine engine)
double   cumPV = 0, cumPV2 = 0, cumW = 0, cumP = 0, cumP2 = 0; int cumN = 0; int vwBars = 0; int sessN = 0;
MqlArr<double>   vwHist;                 // vwap of processed bars, [0] = latest
double   atrV = 0; int atrN = 0; double atrSum = 0;
int      lastDayKey = -1;
int      dayFills = 0, dayW = 0, dayL = 0; double dayR = 0, dayRiskR = 0; int lossDirBlk = 0;
int      bullN = 0, bearN = 0, prevNet = 0; bool havePrev = false;
double   sesO = 0, sesH = 0, sesL = 0, pdH = 0, pdL = 0; bool haveSes = false, havePd = false;
int      st = 0;
mql_long     armBar = -1, fillBar = -1, lastExit = -1, lastFill = -1;
int      lastDir = 0;
double   lim = 0, stp = 0, stp0 = 0, trRisk = 0, t1 = 0, t2 = 0, t3 = 0, t4 = 0, tF = 0;
int      tpHit = 0;
bool     trHalf = false, trGhost = false;
int      trSkip = 0;               // why the setup is a ghost: 1 too far from VWAP, 2 choppy VWAP session, 3 1h EMA20 too fast, 4 too close to VWAP, 5 beyond max VWAP distance,
                                   // 6 stop beyond the VWAP, 7 VWAP touched recently, 8 entry too close to the VWAP
int      totW = 0, totL = 0; double totR = 0;
string   lastRes = "-"_mq;
double   bestPx = 0;               // best price after the fill (the fill bar and stop bars add nothing)
int      ghW = 0, ghL = 0; double ghR = 0;   // results the skipped (invisible) trades would have had
// optional filters: VWAP crosses of this VWAP period; 1-hour (UTC) candles built from the bars and their EMA20
int      vxSide = 0, vxN = 0;
int      tchL = 1000000, tchS = 1000000;   // candles since the candle range last reached the VWAP (long side: the low, short side: the high); 0 = this candle
mql_long     hK = -1;                  // hour of the last bar (-1 = none yet)
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
mql_long     exArm = -1;               // engine armBar of the setup the EA took
bool     exSynced = false;         // the broker position is the engine's live trade
bool     gRearm = false;           // re-place the engine's armed setup after a restart / catch-up
bool     gVirt = false;            // entry inside the stops distance: VirtualEntry() enters at market at the level
int      gDayPendN = 0;            // new days on bars caught up after a disconnect or replayed after a restart, not counted yet
datetime gPrevT = 0;               // open time of the bar before the one OnNewBar handles (catch-up aware)
bool     pDone[3];
ulong    lastDeal = 0;
int      sigN = 0, takenN = 0, skipN = 0, missN = 0; string skipWhy = ""_mq;
datetime gDrawT = 0; bool gDrawOn = false;
bool     gCanDraw = true;          // false in non-visual testing and optimisation (nothing would be seen)
MqlArr<mql_long>     gDrawn;                 // fill times of the drawn trades, oldest first
string   gStateTxt = "SCANNING"_mq;   // table: state line
int      gTblW = -1, gTblH = -1;   // chart size the table was laid out for
MqlArr<string>   tblKey, tblVal; MqlArr<color> tblCol, tblBg;
double   dayPnl = 0; int lossRow = 0, winRow = 0; bool dayBlock = false; int pauseLeft = 0; bool paused = false;
double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;
MqlArr<double>   labSeq; int parWins = 0; int rdUnits = 1; int oscU = 1; double oscP = 0;
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
mql_long     gPauseArm = -1;                                  // skip rule: armBar of a setup armed on a caught-up bar while trading was paused (never placed)
int      gCrkPrPrev = -1;                                 // the Crooks C rule the state belongs to (a new choice starts its state again)
bool     gInitDone = false;                               // restart memory: OnInit finished once (MT5 keeps globals when inputs or the timeframe change: nothing is reloaded then)
bool     gPersist = false; string gSvBase = ""_mq;           //   on (live / demo, not in the Strategy Tester); the names' prefix of this EA (symbol, magic, account)
bool     gRestored = false; datetime gSvT = 0, gSvLast = 0;   //   state reloaded at this start; when it was saved; the last processed bar it belongs to
MqlArr<string>   gIoN; MqlArr<double> gIoV; int gIoC = 0; bool gIoSave = true;   //   the values being written / read
MqlArr<string>   gSvN; MqlArr<double> gSvV; int gSvC = 0;              //   the values last written (only changes are written)
bool     gBrokerPend = false;                             //   the broker part of the start waits until MT5 is connected (positions and deals visible)
bool     gRestFlat = false;                               //   a force-close, weekend start or news start passed while the EA was off
datetime gSvFullT = 0; mql_long gSvAcc = 0;                   //   the last full rewrite (daily: MT5 deletes global variables not accessed for 4 weeks); the saved account
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
   MqlDateTime d; ZeroMemory(d); mq_dot(d).year = y; mq_dot(d).mon = mon; mq_dot(d).day = 1;
   MqlDateTime f; TimeToStruct(StructToTime(d), f);
   return 1 + (7 - mq_dot(f).day_of_week) % 7 + 7 * (n - 1);
}
int LastSunday(int y, int mon) { int d = NthSunday(y, mon, 1); while(d + 7 <= 31) d += 7; return d; }   // March / October (31 days)
datetime MkTime(int y, int mon, int day, int hr) { MqlDateTime d; ZeroMemory(d); mq_dot(d).year = y; mq_dot(d).mon = mon; mq_dot(d).day = day; mq_dot(d).hour = hr; return StructToTime(d); }
// British summer time at a UTC time: 01:00 UTC on the last Sunday of March to 01:00 UTC on the last Sunday of October
bool UkSummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(mq_dot(d).year, 3, LastSunday(mq_dot(d).year, 3), 1) && utc < MkTime(mq_dot(d).year, 10, LastSunday(mq_dot(d).year, 10), 1); }
// New York daylight time at a UTC time: 07:00 UTC on the second Sunday of March to 06:00 UTC on the first Sunday of November
bool NySummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(mq_dot(d).year, 3, NthSunday(mq_dot(d).year, 3, 2), 7) && utc < MkTime(mq_dot(d).year, 11, NthSunday(mq_dot(d).year, 11, 1), 6); }
double SrvGMT(datetime server)
{
   if(InpServerTz == SRV_FIXED) return InpServerGMT;
   MqlDateTime d; TimeToStruct(server, d);
   if(InpServerTz == SRV_EET)                         // EU summer time: last Sunday of March to last Sunday of October
   {
      int es = LastSunday(mq_dot(d).year, 3), ee = LastSunday(mq_dot(d).year, 10);
      bool sum = (mq_dot(d).mon > 3 && mq_dot(d).mon < 10) || (mq_dot(d).mon == 3 && mq_dot(d).day >= es) || (mq_dot(d).mon == 10 && mq_dot(d).day < ee);
      return sum ? 3.0 : 2.0;
   }
   int ds = NthSunday(mq_dot(d).year, 3, 2), de = NthSunday(mq_dot(d).year, 11, 1);
   bool dst = (mq_dot(d).mon > 3 && mq_dot(d).mon < 11) || (mq_dot(d).mon == 3 && mq_dot(d).day >= ds) || (mq_dot(d).mon == 11 && mq_dot(d).day < de);
   return dst ? 3.0 : 2.0;
}
datetime UserTime(datetime server) { return server - (datetime)(SrvGMT(server) * 3600) + (datetime)(InpUserGMT * 3600); }
datetime UtcTime(datetime server)  { return server - (datetime)(SrvGMT(server) * 3600); }
int      MinOfDay(datetime t) { MqlDateTime d; TimeToStruct(t, d); return mq_dot(d).hour * 60 + mq_dot(d).min; }
int      DowOf(datetime t)    { MqlDateTime d; TimeToStruct(t, d); return mq_dot(d).day_of_week; }   // 0 = Sunday
int      DayKey(datetime t)   { MqlDateTime d; TimeToStruct(t, d); return mq_dot(d).year * 1000 + mq_dot(d).day_of_year; }
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
      if(OrderGetString(ORDER_SYMBOL) == _Symbol && OrderGetInteger(ORDER_MAGIC) == InpMagic) mq_dot(trade).OrderDelete(tk);
   }
}

void CloseAll()
{
   ulong tk; double v, op;
   int guard = 0;
   while(HasPosition(tk, v, op) && guard++ < 5) { if(!mq_dot(trade).PositionClose(tk)) break; }
}

// realised P&L of this EA's deals since the last call (profit + commission + swap + fee); closed = an exit deal was seen
double NewDealsPnl(bool &closed)
{
   closed = false;
   double sum = 0;
   if(!HistorySelect(0, TimeCurrent() + 86400)) return 0;
   int n = HistoryDealsTotal();
   ulong maxTk = lastDeal;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(tk > maxTk) maxTk = tk;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      sum += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      mql_long entry = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); }
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
   mql_long   rv = iVolume(_Symbol, _Period, s);
   mql_long   tv = iTickVolume(_Symbol, _Period, s);
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
   int aKey = InpVwapAnchor == VW_WEEK ? (int)(((mql_long)t + 3 * 86400) / (7 * 86400)) : InpVwapAnchor == VW_MONTH ? mq_dot(md).year * 12 + mq_dot(md).mon : key;   // weeks start Monday 00:00
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
   int nHist = (int)MathMin((mql_long)ArraySize(vwHist), bi + 1);

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
   mql_long hKey = (mql_long)UtcTime(t) / 3600;
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
            lastRes = (win ? "TP"_mq + IntegerToString((int)InpExitAt) + " "_mq : "STOP "_mq) + (res >= 0 ? "+"_mq : ""_mq) + DoubleToString(res, 2) + "R"_mq;
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
               lastRes = "STOP -1.00R"_mq;
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
   mql_long legN = lastFill < 0 ? 0 : bi - lastFill;
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
   int k = mq_dot(d).year * 100 + mq_dot(d).mon;
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
   gMonKey = mq_dot(d).year * 100 + mq_dot(d).mon;                    // the month of the last closed bar, as MonthTick will see it
   monPnl = 0; monPeak = 0; monLocked = false; monStop = false;
   MqlArr<mql_long> open; int no = 0;                           // positions still open: their deals are not closed profit yet
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
      if(tk == 0 || HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      MqlDateTime dd; TimeToStruct(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), dd);
      if(mq_dot(dd).year * 100 + mq_dot(dd).mon != gMonKey) continue;  // only this month's deals (your time zone)
      mql_long pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID); bool isOpen = false;
      for(int q = 0; q < no; q++) if(open[q] == pid) { isOpen = true; break; }
      if(isOpen) continue;
      monPnl += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      mql_long e = HistoryDealGetInteger(tk, DEAL_ENTRY);
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
   mql_long pre = (mql_long)InpNewsPre * 60;
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
   bool a = mq_dot(trade).Buy(v, _Symbol, 0, slB, tpB, "HEDGE"_mq);
   if(!a) Print("Hedge buy failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
   bool b = mq_dot(trade).Sell(v, _Symbol, 0, slS, tpS, "HEDGE"_mq);
   if(!b) Print("Hedge sell failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
   if(a != b) { CloseAll(); Print("Hedge: only one of the two trades opened, so it was closed again."_mq); return false; }
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
   bool a = isL ? mq_dot(trade).BuyLimit(v, pB, _Symbol, slB, tpB, ORDER_TIME_GTC, 0, "HEDGE"_mq) : mq_dot(trade).SellLimit(v, pS, _Symbol, slS, tpS, ORDER_TIME_GTC, 0, "HEDGE"_mq);
   bool b = a && (isL ? mq_dot(trade).SellStop(v, pS, _Symbol, slS, tpS, ORDER_TIME_GTC, 0, "HEDGE"_mq) : mq_dot(trade).BuyStop(v, pB, _Symbol, slB, tpB, ORDER_TIME_GTC, 0, "HEDGE"_mq));
   if(!b) { Print("Hedge orders failed: "_mq, mq_dot(trade).ResultRetcodeDescription()); CancelPending(); return false; }
   return true;
}
bool   HgOpen()                                          // a hedge trade of this EA is open (e.g. after a restart)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == InpMagic && PositionGetString(POSITION_COMMENT) == "HEDGE"_mq) return true;
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
   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp))) { CloseAll(); return; }
   if(exL) { if(bid - sl < minD) sl = FloorTick(bid - minD); if(tp > 0 && tp - bid < minD) tp = CeilTick(bid + minD); }
   else    { if(sl - ask < minD) sl = CeilTick(ask + minD); if(tp > 0 && ask - tp < minD) tp = FloorTick(ask - minD); }
   bool same = MathAbs(PositionGetDouble(POSITION_SL) - sl) < TickSize() * 0.5 && MathAbs(PositionGetDouble(POSITION_TP) - tp) < TickSize() * 0.5;
   if(same || mq_dot(trade).PositionModify(tk, sl, tp)) { if(exT1 && exT1Half) exT1Be = true; if(exT1 && !exT1Half) exT1MvPend = false; }
   else Print("Stop/target update rejected ("_mq, mq_dot(trade).ResultRetcodeDescription(), "): SL "_mq, DoubleToString(sl, _Digits), " TP "_mq, DoubleToString(tp, _Digits));
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
      if(mq_dot(trade).PositionClosePartial(tk, NormalizeDouble(cv, 8))) { exT1Half = true; SetExits(true); }
      else { Print("TP1 partial close failed ("_mq, mq_dot(trade).ResultRetcodeDescription(), "), retrying"_mq); gT1Seen = true; }   // ticks retry while price is past TP1, the next bar close in any case
   }
   else CloseAll();                                   // too small to split: close it all at TP1
}

//--- text helpers (table and markings) ----------------------------------------
string SgnR(double r) { return (r >= 0 ? "+"_mq : ""_mq) + DoubleToString(r, 2) + "R"_mq; }
string Share(int n, int total) { return total > 0 ? IntegerToString((int)MathRound(100.0 * n / total)) + "%"_mq : "-"_mq; }
string AccTxt() { int n = totW + totL; return IntegerToString(n) + " trades | "_mq + Share(totW, n) + " ("_mq + IntegerToString(totW) + "W/"_mq + IntegerToString(totL) + "L) | "_mq + SgnR(totR); }
string TpTxt()
{
   int n = totW + totL, xk = (int)InpExitAt;
   string s = ""_mq;
   for(int k = 1; k <= 4; k++) s += (k > 1 ? " | "_mq : ""_mq) + "TP"_mq + IntegerToString(k) + " "_mq + (k > xk ? "n/a"_mq : Share(tpHitN[k - 1], n) + " ("_mq + IntegerToString(tpHitN[k - 1]) + ")"_mq);
   return s;
}
string BeTxt() { int n = totW + totL; return "BE "_mq + IntegerToString(beN) + " ("_mq + Share(beN, n) + ") | locked profit "_mq + IntegerToString(lkN) + " ("_mq + Share(lkN, n) + ")"_mq; }
string FltTxt() { return IntegerToString(ghW + ghL) + " skipped | would have been "_mq + IntegerToString(ghW) + "W/"_mq + IntegerToString(ghL) + "L | "_mq + SgnR(ghR); }
string MonTxt(int m) { string a[12] = {"Jan"_mq, "Feb"_mq, "Mar"_mq, "Apr"_mq, "May"_mq, "Jun"_mq, "Jul"_mq, "Aug"_mq, "Sep"_mq, "Oct"_mq, "Nov"_mq, "Dec"_mq}; return a[(m + 11) % 12]; }
string DateTxt(datetime tm, bool withYear)
{
   MqlDateTime d; TimeToStruct(tm, d);
   return StringFormat("%02d %s "_mq, mq_dot(d).day, MonTxt(mq_dot(d).mon)) + (withYear ? StringFormat("%02d"_mq, mq_dot(d).year % 100) : StringFormat("%02d:%02d"_mq, mq_dot(d).hour, mq_dot(d).min));
}

//--- trade markings: drawn for every bar the engine processes (history included), same events as the TradingView files
string TrId(datetime tf) { return "ARM_X"_mq + IntegerToString((mql_long)tf) + "_"_mq; }
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
   ObjectSetString(0, nm, OBJPROP_FONT, "Arial"_mq);
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
   if(evCancel != 0 || evFill) ObjectDelete(0, "ARM_limit"_mq);
   if(evArm) MarkLine("ARM_limit"_mq, bt, lim, bt + PeriodSeconds() * InpRetestBars, lim, InpColEntry, 1, STYLE_DASH);   // MT5 dashes only width-1 lines
   int xk = (int)InpExitAt;
   if(evFill)
   {
      string id = TrId(bt);
      bool   isL = evFillL;
      MarkBox(id + "tgt"_mq, bt, MathMax(lim, tF), bt, MathMin(lim, tF), InpColTarget);
      MarkBox(id + "stp"_mq, bt, MathMax(lim, stp0), bt, MathMin(lim, stp0), InpColStop);
      MarkLine(id + "en"_mq, bt, lim, bt, lim, InpColEntry, 2, STYLE_SOLID);
      if(xk > 1) MarkLine(id + "tp1"_mq, bt, t1, bt, t1, InpColTarget, 1, STYLE_DOT);
      if(xk > 2) MarkLine(id + "tp2"_mq, bt, t2, bt, t2, InpColTarget, 1, STYLE_DOT);
      if(xk > 3) MarkLine(id + "tp3"_mq, bt, t3, bt, t3, InpColTarget, 1, STYLE_DOT);
      string an = id + "ar"_mq;
      if(ObjectFind(0, an) < 0) ObjectCreate(0, an, isL ? OBJ_ARROW_BUY : OBJ_ARROW_SELL, 0, bt, lim);
      ObjectSetInteger(0, an, OBJPROP_COLOR, isL ? InpColEntry : InpColStop);
      ObjectSetInteger(0, an, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, an, OBJPROP_HIDDEN, true);
      MarkText(id + "le"_mq, bt, lim, (isL ? "BUY "_mq : "SELL "_mq) + DoubleToString(lim, _Digits), InpColEntry, isL ? ANCHOR_LEFT_LOWER : ANCHOR_LEFT_UPPER);
      MarkText(id + "ls"_mq, bt, stp0, "SL "_mq + DoubleToString(stp0, _Digits) + (trHalf ? " (half)"_mq : ""_mq), InpColStop, isL ? ANCHOR_LEFT_UPPER : ANCHOR_LEFT_LOWER);
      MarkText(id + "lt"_mq, bt, tF, "TP"_mq + IntegerToString(xk) + " "_mq + DoubleToString(tF, _Digits), InpColTarget, isL ? ANCHOR_LEFT_LOWER : ANCHOR_LEFT_UPPER);
      gDrawT = bt; gDrawOn = true;
      int n = ArraySize(gDrawn);
      ArrayResize(gDrawn, n + 1);
      gDrawn[n] = (mql_long)bt;
      if(InpMaxDrawn > 0 && n + 1 > InpMaxDrawn) { ObjectsDeleteAll(0, TrId((datetime)gDrawn[0])); ArrayRemove(gDrawn, 0, 1); }
   }
   else if(gDrawOn)
   {
      string id = TrId(gDrawT);
      ObjectMove(0, id + "tgt"_mq, 1, bt, MathMin(lim, tF));
      ObjectMove(0, id + "stp"_mq, 1, bt, MathMin(lim, stp0));
      ObjectMove(0, id + "en"_mq, 1, bt, lim);
      if(xk > 1) ObjectMove(0, id + "tp1"_mq, 1, bt, t1);
      if(xk > 2) ObjectMove(0, id + "tp2"_mq, 1, bt, t2);
      if(xk > 3) ObjectMove(0, id + "tp3"_mq, 1, bt, t3);
   }
   if(evExit && gDrawOn)
   {
      bool   above = (lastDir == 1) == evWin;   // long target / short stop: above the level
      string txt = evWin ? "TP"_mq + IntegerToString(xk) + " "_mq + SgnR(evRes) : (stp != stp0 && evRes == 0.0 ? "BE "_mq : "STOP "_mq) + SgnR(evRes);
      color  cl = evWin ? InpColTarget : (evRes >= 0.0 ? clrSilver : InpColStop);
      MarkText(TrId(gDrawT) + "rx"_mq, bt, evWin ? tF : stp, txt, cl, above ? ANCHOR_RIGHT_LOWER : ANCHOR_RIGHT_UPPER);
      gDrawOn = false;
   }
}

//--- on-chart table (rebuilt on every new bar so it stays on top of the markings) ----
string StateText(bool newsBlk)
{
   string why = trSkip == 1 ? "TOO FAR FROM VWAP"_mq : (trSkip == 2 ? "CHOPPY VWAP SESSION"_mq : (trSkip == 3 ? "1H EMA20 TOO FAST"_mq : (trSkip == 4 ? "TOO CLOSE TO VWAP"_mq :
                (trSkip == 5 ? "BEYOND MAX VWAP DISTANCE"_mq : (trSkip == 6 ? "STOP BEYOND VWAP"_mq : (trSkip == 7 ? "VWAP TOUCHED RECENTLY"_mq : "ENTRY TOO CLOSE TO VWAP"_mq))))));
   string s = st != 0 && trGhost ? "SKIPPED ("_mq + why + ")"_mq : st == 2 ? "LONG ACTIVE"_mq : st == -2 ? "SHORT ACTIVE"_mq : st == 1 ? "BUY LIMIT ARMED"_mq : st == -1 ? "SELL LIMIT ARMED"_mq :
              capStop ? "HARD CAP: STOPPED"_mq : newsBlk ? "NEWS WINDOW"_mq : paused ? "PAUSED"_mq : CrkPause() ? "CROOKS C PAUSE ("_mq + IntegerToString(crkSkipLeft) + "d left)"_mq : monStop ? "MONTHLY LOCK (until the 1st)"_mq : dayBlock ? "STREAK STOP TODAY"_mq :
              !gDayOk ? "DAY SWITCHED OFF"_mq : !gHourOk ? "OUTSIDE HOURS"_mq : !gKzOk ? "OUTSIDE KILL ZONES"_mq : CrkHedgeNow() ? "SCANNING (HEDGE PAIR ON THE NEXT SIGNAL)"_mq : "SCANNING"_mq;
   string ex = exState == 2 ? (exHg ? " (hedge pair open)"_mq : " (in trade)"_mq) : (exState == 1 ? (gVirt ? " (waiting for the level)"_mq : exHg ? " (hedge orders working)"_mq : " (order working)"_mq) : ""_mq);
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
   string rb = nm + "b"_mq, lb = nm + "t"_mq;
   ObjectCreate(0, rb, OBJ_RECTANGLE_LABEL, 0, 0, 0);
   ObjectSetInteger(0, rb, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, rb, OBJPROP_XDISTANCE, x);
   ObjectSetInteger(0, rb, OBJPROP_YDISTANCE, y);
   ObjectSetInteger(0, rb, OBJPROP_XSIZE, w);
   ObjectSetInteger(0, rb, OBJPROP_YSIZE, hgt);
   ObjectSetInteger(0, rb, OBJPROP_BGCOLOR, bg);
   ObjectSetInteger(0, rb, OBJPROP_BORDER_TYPE, BORDER_FLAT);
   ObjectSetInteger(0, rb, OBJPROP_COLOR, ((color)5918282));
   ObjectSetInteger(0, rb, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, rb, OBJPROP_HIDDEN, true);
   ObjectCreate(0, lb, OBJ_LABEL, 0, 0, 0);
   ObjectSetInteger(0, lb, OBJPROP_CORNER, CORNER_LEFT_UPPER);
   ObjectSetInteger(0, lb, OBJPROP_ANCHOR, ANCHOR_LEFT);
   ObjectSetInteger(0, lb, OBJPROP_XDISTANCE, x + 6);
   ObjectSetInteger(0, lb, OBJPROP_YDISTANCE, y + hgt / 2);
   ObjectSetString(0, lb, OBJPROP_FONT, "Arial"_mq);
   ObjectSetInteger(0, lb, OBJPROP_FONTSIZE, fs);
   ObjectSetInteger(0, lb, OBJPROP_COLOR, fg);
   ObjectSetString(0, lb, OBJPROP_TEXT, txt);
   ObjectSetInteger(0, lb, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, lb, OBJPROP_HIDDEN, true);
}
void UpdateTable()
{
   if(!InpShowTable || !gCanDraw) return;
   ObjectsDeleteAll(0, "ARM_TB_"_mq);
   ArrayResize(tblKey, 0); ArrayResize(tblVal, 0); ArrayResize(tblCol, 0); ArrayResize(tblBg, 0);
   color  white = clrWhite, posC = ((color)11464809), negC = ((color)11239679), cell = ((color)2957854);
   bool   act = MathAbs(st) == 2 && !trGhost, armed = MathAbs(st) == 1 && !trGhost, has = act || armed;
   int    xk = (int)InpExitAt;
   string tps = has ? DoubleToString(t1, _Digits) + " | "_mq + DoubleToString(t2, _Digits) + " | "_mq + DoubleToString(t3, _Digits) + " | "_mq + DoubleToString(t4, _Digits) : "-"_mq;
   bool   isC = InpRec == REC_C || InpRec == REC_CS, isK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;
   bool   kRec = exState != 0 ? crkRec : CrkRecNext();
   string kTxt = DoubleToString(crkL, 2) + (InpRec == REC_CRC ? (kRec ? " | recovery trade"_mq + (CrkNp() > 1 ? ", part "_mq + IntegerToString(CrkNp() - CrkParts() + 1) + " of "_mq + IntegerToString(CrkNp()) : ""_mq) : (crkL > 0 ? " | base, waiting for a win"_mq : " | base"_mq)) : " | trade "_mq + IntegerToString(crkN + 1) + (kRec ? " recovery"_mq : " base"_mq)) + (InpRec == REC_CRB ? " | split "_mq + IntegerToString(InpCSplit) : ""_mq)
                 + (exState != 0 && exT1 ? (exT1Half ? " | TP1 booked, rest to TP2"_mq : " | TP1 rule, stop "_mq + DoubleToString(exT1Stop, _Digits)) : ""_mq)
                 + (!CrkPrOn() ? ""_mq : CrkPause() ? " | paused, "_mq + IntegerToString(crkSkipLeft) + " days left"_mq : crkWait ? " | waiting for "_mq + IntegerToString(InpCrkPrM) + " wins in a row ("_mq + IntegerToString(crkWW) + ")"_mq :
                    crkNeedL ? " | waiting for a loss, then a win"_mq : crkHg ? " | hedge pair on the next signal"_mq : crkF > 0 ? " | lost recoveries in a row "_mq + IntegerToString(crkF) + "/"_mq + IntegerToString(InpCrkPrN) : ""_mq);
   string rec = InpRec == REC_OFF ? "off"_mq : (isC ? DoubleToString(carried, 2) + " | split "_mq + IntegerToString(InpCSplit) : isK ? kTxt : DoubleToString(recPool, 2) + " | "_mq + IntegerToString(recLosses) + " losses in a row"_mq);
   TblAdd("AUCTION RETEST"_mq, "EA v4.3"_mq, white, ((color)14061373));
   TblAdd("STATE"_mq, gStateTxt, white, act ? (st == 2 ? ((color)5287756) : ((color)4536050)) : (armed ? ((color)39167) : ((color)7037021)));
   TblAdd("ENTRY / STOP"_mq, has ? DoubleToString(lim, _Digits) + " / "_mq + DoubleToString(stp, _Digits) + (trHalf ? " (half stop)"_mq : ""_mq) : "-"_mq, white, cell);
   TblAdd("TP1 | TP2 | TP3 | TP4 (exit TP"_mq + IntegerToString(xk) + ")"_mq, tps, posC, cell);
   TblAdd("RISK | LOTS"_mq, exState != 0 ? DoubleToString(exRiskAmt, 2) + " | "_mq + DoubleToString(exLots, 2) : "base "_mq + DoubleToString(InpBaseRisk, 2), white, cell);
   TblAdd(isC ? "LOSSES CARRIED"_mq : isK ? "CROOKS: LOSS TO WIN BACK"_mq : "RECOVERY POOL"_mq, rec, (isC ? carried : isK ? crkL : recPool) > 0 ? negC : white, cell);
   TblAdd("STREAK W | L"_mq, IntegerToString(winRow) + " | "_mq + IntegerToString(lossRow) + " | total "_mq + IntegerToString(exW) + "W/"_mq + IntegerToString(exLn) + "L"_mq, white, cell);
   TblAdd("DAY P&L | FILLS"_mq, DoubleToString(dayPnl, 2) + " | "_mq + IntegerToString(dayFills) + "/"_mq + IntegerToString(InpMaxFills) + (InpMLockOn || InpPLockOn ? " | month "_mq + DoubleToString(monPnl, 2) + (monLocked ? " (locked "_mq + DoubleToString(InpPLockPct / 100.0 * monPeak, 2) + ")"_mq : ""_mq) : ""_mq), dayPnl >= 0 ? posC : negC, cell);
   TblAdd("SIGNALS | TAKEN | SKIPPED"_mq, IntegerToString(sigN) + " | "_mq + IntegerToString(takenN) + " | "_mq + IntegerToString(skipN) + (missN > 0 ? " | missed "_mq + IntegerToString(missN) : ""_mq) + (skipWhy != ""_mq ? " (last: "_mq + skipWhy + ")"_mq : ""_mq), skipN + missN > 0 ? negC : white, cell);
   TblAdd("SIGNAL TRADES | WIN % | R"_mq, AccTxt() + " | last "_mq + lastRes, totR >= 0 ? posC : negC, cell);
   TblAdd("TP HIT"_mq, TpTxt(), posC, cell);
   if(InpMv1On || InpMv2On || InpMv3On) TblAdd("BREAKEVEN"_mq, BeTxt(), white, cell);
   if(InpNoChase || InpChopOn || InpEmaOn || InpMinVwOn || InpMaxVwOn || InpStopVwOn || InpTouchVwOn || InpEntVwOn) TblAdd("SKIPPED BY FILTERS"_mq, FltTxt(), ghR <= 0 ? posC : negC, cell);
   TblAdd("DATA RANGE"_mq, gFirstT > 0 ? DateTxt(UserTime(gFirstT), true) + " -> "_mq + DateTxt(UserTime(gLastDone), false) + " | "_mq + IntegerToString(bi + 1) + " bars"_mq : "-"_mq, white, cell);
   TblAdd("RESTART MEMORY"_mq, gPersist ? (gRestored ? "on | continued from "_mq + DateTxt(UserTime(gSvT), true) : "on"_mq) : InpRemember ? "off in the Strategy Tester"_mq : "off"_mq, white, cell);
   // column widths from the longest text in each column
   int  fs = (int)MathMax(6, InpTableFont), n = ArraySize(tblKey), kw = 0, vw = 0, th = 0;
   uint tw = 0, tht = 0;
   TextSetFont("Arial"_mq, -fs * 10);
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
      TblCell("ARM_TB_k"_mq + IntegerToString(i), x0, y, c0, rowH, i == 0 ? ((color)14721833) : ((color)3747370), tblKey[i], i == 0 ? white : ((color)14472401), fs);
      TblCell("ARM_TB_v"_mq + IntegerToString(i), x0 + c0, y, c1, rowH, tblBg[i], tblVal[i], tblCol[i], fs);
   }
   ChartRedraw(0);
}

//--- place the engine's setup at the broker (sizing, filters, pending or market order) ----
void TakeSetup(bool isL, bool newsBlk, bool flatNow)
{
   sigN++;
   ulong pTk; double pVol, pOpen;
   bool posNow = HasPosition(pTk, pVol, pOpen);
   bool crkPs = CrkPause();
   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock || crkPs || monStop);   // the hard cap acts only on a signal that can be taken
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
   skipWhy = (exState != 0 || posNow) ? "still in a trade"_mq : (newsBlk || flatNow) ? "news / force-close"_mq : capStop ? "hard cap stop"_mq : paused ? "paused"_mq : dayBlock ? "streak stop"_mq : crkPs ? "Crooks C pause"_mq : monStop ? "monthly lock"_mq : v <= 0 ? "size 0"_mq : ""_mq;
   if(skipWhy != ""_mq) { skipN++; return; }
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   double sprNow = CostSpr();
   exCostPx = InpEarnBack && tv > 0 && !hg ? InpCommLot / (tv / ts) + sprNow : 0;   // no earn-back on the hedge pair: its levels are the inputs
   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot);
   exT1 = t1d > 0; exT1Half = false; exT1Be = false; exT1MvPend = false; exT1Stop = exT1 ? T1Stop0Px(isL, t1d) : 0; exT1Tight = exT1 ? T1StopPx(isL, t1d) : 0; exT1Entry = lim;
   exT1Tp1 = t1; exT1Tp2 = t2; exKeepSl = 0; exHg = false; exHgS = hgS; exHgT = hgT; gLastOutProfit = 0;
   for(int q = 0; q < 3; q++) pDone[q] = false;
   CancelPending();
   gVirt = false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ep = EntryPx(isL), sl = exT1 ? exT1Stop : StopPx(isL);
   double minD = MinDist();
   // the order's SL must respect the stops level; SetExits re-sends the engine's stop once the engine has filled
   if(isL) sl = MathMin(sl, FloorTick(MathMin(ep, bid) - minD));
   else    sl = MathMax(sl, CeilTick(MathMax(ep, ask) + minD));
   bool ok;
   if(hg) ok = PlaceHedge(isL, v);
   else if(InpEntryMode == ENTRY_MARKET)
      ok = isL ? mq_dot(trade).Buy(v, _Symbol, 0, sl, 0, "ARM"_mq) : mq_dot(trade).Sell(v, _Symbol, 0, sl, 0, "ARM"_mq);
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) ok = mq_dot(trade).BuyLimit(v, ep, _Symbol, sl, 0, ORDER_TIME_GTC, 0, "ARM"_mq);
      else if(ask <= ep)                ok = mq_dot(trade).Buy(v, _Symbol, 0, sl, 0, "ARM"_mq);   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                 // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) ok = mq_dot(trade).SellLimit(v, ep, _Symbol, sl, 0, ORDER_TIME_GTC, 0, "ARM"_mq);
      else if(bid >= ep)                ok = mq_dot(trade).Sell(v, _Symbol, 0, sl, 0, "ARM"_mq);
      else { ok = true; gVirt = true; }
   }
   if(ok) { exState = 1; exArm = armBar; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }
   else { skipN++; skipWhy = "order rejected"_mq; Print("ARM order failed: "_mq, mq_dot(trade).ResultRetcodeDescription()); }
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
   double ep = EntryPx(exL), sl = exT1 ? exT1Stop : StopPx(exL);
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      if(!(exL ? mq_dot(trade).Buy(exLots, _Symbol, 0, sl, 0, "ARM"_mq) : mq_dot(trade).Sell(exLots, _Symbol, 0, sl, 0, "ARM"_mq)))
         Print("ARM entry failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
   }
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
      else { MqlArr<double> tmp; ArrayResize(tmp, n - 2); for(int q = 0; q < n - 2; q++) tmp[q] = labSeq[q + 1]; ArrayResize(labSeq, n - 2); for(int q = 0; q < n - 2; q++) labSeq[q] = tmp[q]; }
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
   ProcessBar(1);
   CrkDayTick(iTime(_Symbol, _Period, 1));              // Crooks C skip rule: a new day in your time zone counts before this bar's booking
   datetime bt = iTime(_Symbol, _Period, 1);
   datetime ut = UserTime(bt), utPrev = UserTime(gPrevT > 0 ? gPrevT : iTime(_Symbol, _Period, 2));
   MonthTick(ut);                                     // a new month (your time zone): its closed deals count from this bar on

   DayStart(gDayPendN + (gNewDay ? 1 : 0)); gDayPendN = 0;   // each new day since the last bar (several after a disconnect or a restart)

   // 1. what the broker did since the last bar
   bool closedNew; double newPnl = NewDealsPnl(closedNew);
   exPnl += newPnl; totalNet += newPnl;
   if(newPnl != 0 || closedNew) carried = MathMax(0.0, carried - newPnl);
   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   bool exClosed = (exState == 1 && !pos && closedNew) || (exState == 2 && !pos);

   // 2. an executed trade has closed
   if(exClosed) BookClosed();

   // 3. follow the engine (only the setup the EA took); state based, so it also covers bars caught up after a disconnect
   bool exMine = exArm >= 0 && armBar == exArm;
   if(exState == 1 && !(MathAbs(st) == 1 && exMine))   // the engine no longer holds the EA's armed setup: expired, replaced or filled
   {
      CancelPending();
      if(exMine && lastFill > exArm) missN++;          // engine filled, broker did not
      exState = 0; exArm = -1; gVirt = false; exHg = false;
   }
   if(exState == 2 && exMine && MathAbs(st) == 2) exSynced = true;   // the engine is in the EA's setup (filled on this bar or a caught-up bar)
   // Crooks TP1 rule: TP1 was reached but no tick booked the TP1 part (missed tick, failed close, disconnect): book it now, before the
   // stop / target update below (exit TP1: the engine won on the bar that just closed; any exit: that bar, after the fill bar, reached
   // TP1; or a bar caught up after a disconnect did)
   bool t1Bar = exT1 && exSynced && lastFill >= 0 && lastFill < bi && (exL ? Hi(1) >= exT1Tp1 + exCostPx : Lo(1) <= exT1Tp1 - exCostPx);
   bool t1Due = (((evExit && evWin) || t1Bar) && exMine) || gT1Seen;
   gT1Seen = false;                                                  // a failed close below sets it again: retried at the next bar close
   if(t1Due && exState == 2 && exT1 && !exT1Half && pos) { T1Half(pTk, pVol); pos = HasPosition(pTk, pVol, pOpen); }
   if(exState == 2 && exMine && !exHg && (evFill || evMove)) SetExits(true);
   if(evExit && exState == 2 && exMine && !exHg && (!InpEarnBack || !evWin) && !(exT1 && (evWin || exT1Half))) CloseAll();   // engine exited: never stay in (earn-back and the Crooks TP1 rule only outlive a win)
   // Crooks TP1 rule: stop choices that move the stop at a bar close, before the TP1 half is booked
   if(exState == 2 && exT1 && !exT1Half && (InpCrkT1Stop == T1S_FILL || InpCrkT1Stop == T1S_PT || InpCrkT1Stop == T1S_PBE)) T1StopMove();
   // engine wins: close a broker position the engine is not in (early fill on a spread spike, a fill racing a cancel,
   // or an engine exit on a bar caught up after a disconnect); with earn-back a synced trade may outlive the engine exit
   bool engHolds = (MathAbs(st) == 2 && exSynced && exMine) || (MathAbs(st) == 1 && !exSynced && exState == 2 && exMine);
   if(pos && !exClosed && !evExit && !engHolds && !(InpEarnBack && exSynced) && !(exT1 && exSynced) && !exHg)
   {
      CloseAll(); exState = 2;   // booked on the next bar unless the exit deal is already visible
      ulong cTk; double cVol, cOp;
      if(!HasPosition(cTk, cVol, cOp))
      {
         bool cn; double np = NewDealsPnl(cn);
         exPnl += np; totalNet += np; if(np != 0 || cn) carried = MathMax(0.0, carried - np);
         if(cn) BookClosed();   // closed now: the engine's new setup on this bar can be taken
      }
   }

   // 4. force-close time / weekend start / news
   bool nStart; bool newsBlk = NewsBlock(ut, nStart, utPrev);
   int  fcM = InpFcH * 60 + InpFcM, curM = MinOfDay(ut), prvM = MinOfDay(utPrev);
   bool fcNow = InpFcOn && (curM >= prvM ? (prvM < fcM && curM >= fcM) : (fcM > prvM || fcM <= curM));
   bool wkndStart = InpWeekendOn && DowOf(ut) == 6 && DowOf(utPrev) != 6;
   bool flatNow = fcNow || wkndStart || nStart;
   if(flatNow && pos) CloseAll();
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
   tp[0] = t1; tp[1] = t2; tp[2] = t3;
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
      if(k + 1 >= exitK || pp[k] <= 0 || pDone[k]) continue;
      if(exL ? px >= tp[k] + exCostPx : px <= tp[k] - exCostPx)
      {
         double cv = MathFloor(exLots * pp[k] / 100.0 / step + 1e-9) * step;
         if(cv >= vmin && vol - cv >= vmin - 1e-9) mq_dot(trade).PositionClosePartial(tk, NormalizeDouble(cv, 8));
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
   string b = "ARS|"_mq + _Symbol + "|"_mq + IntegerToString(InpMagic) + "|"_mq;
   if(StringLen(b) <= 57) return b;
   string k = _Symbol + "|"_mq + IntegerToString(InpMagic);
   uint h = (uint)2166136261;                           // FNV-1a
   for(int q = 0; q < StringLen(k); q++) { h ^= (uint)StringGetCharacter(k, q); h *= (uint)16777619; }
   return "ARS|"_mq + StringFormat("%08X"_mq, h) + "|"_mq;
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
void IoT(string n, datetime &x) { double d = (double)x; IoD(n, d); x = (datetime)(mql_long)MathRound(d); }
void IoU(string n, ulong &x)    { double hi = (double)(x >> 32), lo = (double)(x & 0xFFFFFFFF); IoD(n + "h"_mq, hi); IoD(n + "l"_mq, lo); x = ((ulong)MathRound(hi) << 32) | (ulong)MathRound(lo); }
//--- the saved state: one list for writing and reading, so both always match
void StateIO(bool save)
{
   gIoSave = save; gIoC = 0;
   int ver = SvVer(); IoI("ver"_mq, ver);
   datetime lb = gLastDone, sv = TimeCurrent();           // the last processed bar, and when it was saved (both not a reason to write)
   IoT("lb"_mq, lb); IoT("sv"_mq, sv);
   double acc = (double)AccountInfoInteger(ACCOUNT_LOGIN); IoD("acc"_mq, acc);   // the account it belongs to (checked when loading)
   if(!save) { gSvLast = lb; gSvT = sv; }
   // loss recovery (every rule's state, whichever rule is chosen), total profit (Step-up rule), the hard-cap stop
   IoD("rp"_mq, recPool); IoI("rl"_mq, recLosses); IoI("du"_mq, dUnits); IoD("ca"_mq, carried); IoI("pw"_mq, parWins); IoI("rd"_mq, rdUnits);
   IoI("ou"_mq, oscU); IoD("op"_mq, oscP); IoD("tn"_mq, totalNet); IoI("ew"_mq, exW); IoI("el"_mq, exLn); IoB("cs"_mq, capStop);
   IoD("kl"_mq, crkL); IoI("kn"_mq, crkN); IoB("kw"_mq, crkW); IoI("kp"_mq, crkP); IoI("kf"_mq, crkF); IoB("ka"_mq, crkWait); IoI("kb"_mq, crkWW);
   IoB("kc"_mq, crkNeedL); IoB("ks"_mq, crkSkip); IoI("kt"_mq, crkSkipLeft); IoI("ku"_mq, crkUDay); IoB("kh"_mq, crkHg); IoI("kx"_mq, gCrkPrPrev);
   // streaks and pauses; the month of the last bar (a new month while the EA was off) and a restart still waiting for a trade to close
   IoD("dp"_mq, dayPnl); IoI("lr"_mq, lossRow); IoI("wr"_mq, winRow); IoB("db"_mq, dayBlock); IoI("pl"_mq, pauseLeft); IoB("pa"_mq, paused);
   IoI("mk"_mq, gMonKey); IoB("mr"_mq, monRestPend); IoD("mp"_mq, monPnl); IoD("mq"_mq, monPeak); IoB("ms"_mq, monStop); IoB("ml"_mq, monLocked);
   // the trade the EA is in, or its working order: its type and what it booked so far; the broker deals already counted
   IoI("xs"_mq, exState); IoB("xl"_mq, exL); IoD("xv"_mq, exLots); IoD("xr"_mq, exRiskAmt); IoD("xc"_mq, exCostPx); IoD("xp"_mq, exPnl); IoD("xk"_mq, exKeepSl);
   IoB("kr"_mq, crkRec); IoB("xy"_mq, exSynced);
   bool p0 = pDone[0], p1 = pDone[1], p2 = pDone[2];
   IoB("p0"_mq, p0); IoB("p1"_mq, p1); IoB("p2"_mq, p2);
   pDone[0] = p0; pDone[1] = p1; pDone[2] = p2;
   IoB("t1"_mq, exT1); IoB("th"_mq, exT1Half); IoB("tb"_mq, exT1Be); IoB("tm"_mq, exT1MvPend); IoD("ts"_mq, exT1Stop); IoD("tp"_mq, exT1Tp1); IoD("tq"_mq, exT1Tp2);
   IoD("tt"_mq, exT1Tight); IoD("te"_mq, exT1Entry); IoB("hg"_mq, exHg); IoD("hs"_mq, exHgS); IoD("ht"_mq, exHgT);
   IoU("ld"_mq, lastDeal);
   // the Labouchere list, last (its length changes)
   int ln = ArraySize(labSeq); IoI("ln"_mq, ln);
   if(!save) { if(ln < 1 || ln > 10000) ln = 0; ArrayResize(labSeq, ln); }
   for(int q = 0; q < ln; q++) { double x = save ? labSeq[q] : 0.0; IoD("L"_mq + IntegerToString(q), x); if(!save) labSeq[q] = x; }
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
      if(gIoN[q] != gSvN[q] || (gIoV[q] != gSvV[q] && gIoN[q] != "lb"_mq && gIoN[q] != "sv"_mq)) ch = true;
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
   if(!GlobalVariableCheck(gSvBase + "ver"_mq) || (int)MathRound(GlobalVariableGet(gSvBase + "ver"_mq)) != SvVer())
   {
      if(GlobalVariableCheck(gSvBase + "lb"_mq)) Print("Restart memory: the saved state is incomplete (unused for 4 weeks?): starting fresh."_mq);
      return false;
   }
   double svAcc = GlobalVariableCheck(gSvBase + "acc"_mq) ? GlobalVariableGet(gSvBase + "acc"_mq) : 0, nowAcc = (double)AccountInfoInteger(ACCOUNT_LOGIN);
   if(svAcc != 0 && nowAcc != 0 && svAcc != nowAcc)    // saved by another account (same symbol and magic number): start fresh
   {
      Print("Restart memory: the saved state belongs to account "_mq, (mql_long)svAcc, ", not "_mq, (mql_long)nowAcc, ": starting fresh."_mq);
      return false;
   }
   StateIO(false);
   gSvAcc = (mql_long)MathRound(svAcc);
   for(int q = ArraySize(labSeq); q < 100000 && GlobalVariableCheck(gSvBase + "L"_mq + IntegerToString(q)); q++) GlobalVariableDel(gSvBase + "L"_mq + IntegerToString(q));   // a longer old list
   gSvC = 0;                                            // the next save writes every value again
   return true;
}
//--- restart memory switched off: forget what was saved
void SvWipe() { GlobalVariablesDeleteAll(gSvBase); GlobalVariablesFlush(); gSvC = 0; }
//--- no trade or working order of this EA: its bookkeeping starts again
void TradeClear()
{
   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
   crkRec = false; exT1 = false; exT1Half = false; exT1Be = false; exT1MvPend = false; exT1Stop = 0; exT1Tp1 = 0; exT1Tp2 = 0; exT1Tight = 0; exT1Entry = 0;
   exHg = false; exHgS = 0; exHgT = 0;
   for(int q = 0; q < 3; q++) pDone[q] = false;
}
//--- an exit deal of this EA after the deals already counted (a trade closed while the EA was off)
bool ExitDealAfter(ulong cursor)
{
   if(!HistorySelect(0, TimeCurrent() + 86400)) return false;
   for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= cursor) continue;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      mql_long e = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY) return true;
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
   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)
   bool c; NewDealsPnl(c);                              // no trade of this EA was open: later deals are not its trades
}
//--- OnNewBar's steps 1-2 at start-up: the deals since the saved state, and a trade that closed while the EA was off
void BookBrokerDeals()
{
   bool closedNew; double newPnl = NewDealsPnl(closedNew);
   exPnl += newPnl; totalNet += newPnl;
   if(newPnl != 0 || closedNew) carried = MathMax(0.0, carried - newPnl);
   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   if((exState == 1 && !pos && closedNew) || (exState == 2 && !pos)) BookClosed();
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
   sigN = 0; takenN = 0; skipN = 0; missN = 0; skipWhy = ""_mq;
   gVirt = false; gDayPendN = 0; gPrevT = 0; capStop = false; gT1Seen = false; gPauseArm = -1;   // crkUDay is kept with the pause (MT5 keeps globals)
   for(int q = 0; q < 3; q++) pDone[q] = false;
   trSkip = 0; lastRes = "-"_mq; bestPx = 0; ghW = 0; ghL = 0; ghR = 0;
   vxSide = 0; vxN = 0; tchL = 1000000; tchS = 1000000; hK = -1; hC = 0; hSum = 0; hNum = 0; ArrayInitialize(hE, 0.0);
   ArrayInitialize(tpHitN, 0); beN = 0; lkN = 0; gFirstT = 0;
   gDrawT = 0; ArrayResize(gDrawn, 0); gStateTxt = "SCANNING"_mq;
}

//--- events -----------------------------------------------------------------
//--- the broker part of a start: the deals since the saved state, the month, the saved trade, adoption, orders (restart memory: once connected)
void BrokerStart()
{
   mql_long nowAcc = AccountInfoInteger(ACCOUNT_LOGIN);
   if(gRestored && gSvAcc != 0 && nowAcc != 0 && gSvAcc != nowAcc)   // only known now: the saved state belongs to another account
   {
      Print("Restart memory: the saved state belongs to account "_mq, gSvAcc, ", not "_mq, nowAcc, ": starting fresh."_mq);
      MemoryFresh();
   }
   if(!gRestored) { bool c; NewDealsPnl(c); }            // do not count old history (restored: the deals since the saved state are booked below)
   if(!gRestored) MonthFromHistory();                    // this month's closed profit and the monthly locks from the deal history
   else
   {
      datetime b1 = iTime(_Symbol, _Period, 1);
      MonthTick(UserTime(b1 > 0 ? b1 : TimeCurrent()));  // restored: the saved month goes on, or a new month began while the EA was off (locks start again)
      RestoreTrade();                                    // the saved trade: still open, closed while the EA was off, or gone
   }
   // restart: adopt this EA's open position if the engine is in the same trade, keep managing it
   ulong tk; double vol, op;
   if(HgOpen()) { exState = 2; exHg = true; Print("Hedge pair still open: its trades run to their own stop loss and take profit."_mq); }
   else if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      if((isL && st == 2) || (!isL && st == -2))
      {
         double oldSl = PositionGetDouble(POSITION_SL);
         exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol; exArm = armBar; exSynced = true;   // a restored trade keeps its lots (partials)
         for(int q = 0; q < 3; q++) pDone[q] = pDone[q] || tpHit >= q + 1;
         Print("Adopted open position #"_mq, tk, " (engine is in the same trade)."_mq);
         // never widen the stop of an adopted position (a Crooks TP1-rule position is sized for its tighter stop): SetExits keeps it from now on
         exKeepSl = oldSl > 0 && (isL ? oldSl > StopPx(isL) : oldSl < StopPx(isL)) ? oldSl : 0;
         SetExits(true);
      }
      else
      {
         exState = 2;
         bool early = gRestored && MathAbs(st) == 1 && (st > 0) == isL;          // restored: the broker filled before the engine's fill bar
         bool runner = gRestored && exSynced && (exT1 || InpEarnBack);           // restored: a Crooks TP1-rule rest or an earn-back trade outliving the engine's exit
         if(early) { exL = isL; exArm = armBar; exSynced = false; }
         Print("Open position #"_mq, tk, early ? " kept: it filled before the engine's fill bar (restored trade)."_mq : runner ? " kept: the restored trade runs on after the engine's exit."_mq :
               " does not match the engine state; it will be closed on the next bar (the engine wins)."_mq);
      }
   }
   if(!(gRestored && exHg && exState == 2)) CancelPending();   // a pending order from before the restart has no tracked state (a restored hedge pair keeps its waiting trade)
   if(gRestored)                                         // the days and the broker's deals since the saved state, booked like after a disconnect
   {
      DayStart(gDayPendN); gDayPendN = 0;
      // Crooks TP1 rule: TP1 was reached while the EA was off and its part is not booked yet: it is booked at the next bar close
      if(exState == 2 && exT1 && !exT1Half && exSynced)
         for(int s = 1; s < Bars(_Symbol, _Period); s++)
         {
            if(iTime(_Symbol, _Period, s) <= gSvLast || bi - (s - 1) <= lastFill) break;
            if(exL ? Hi(s) >= exT1Tp1 + exCostPx : Lo(s) <= exT1Tp1 - exCostPx) { gT1Seen = true; break; }
         }
      BookBrokerDeals();
      ulong rTk; double rVol, rOp;
      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseAll(); BookBrokerDeals(); }   // a force-close, weekend start or news start passed while the EA was off
      if(gRestFlat && exHg && exState == 2) CancelPending();
      if(monRestPend && exState == 0 && !HasPosition(rTk, rVol, rOp)) { monRestPend = false; RecoveryRestart(); }
      MonthCheck();
      bool isCC = InpRec == REC_C || InpRec == REC_CS, isKK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;
      Print("Restart memory: continued from "_mq, DateTxt(UserTime(gSvT), true), " | loss to win back "_mq, DoubleToString(isCC ? carried : isKK ? crkL : recPool, 2),
            " | streak "_mq, winRow, "W / "_mq, lossRow, "L"_mq, (paused || pauseLeft > 0) ? " | paused"_mq : ""_mq, CrkPause() ? " | Crooks C pause"_mq : ""_mq,
            capStop ? " | hard cap stop"_mq : ""_mq, exState == 2 ? " | trade still open"_mq : ""_mq);
   }
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm;   // re-place the engine's armed setup on the first tick (not one armed while paused)
}

int OnInit()
{
   mq_dot(trade).SetExpertMagicNumber(InpMagic);
   mq_dot(trade).SetDeviationInPoints(50);
   mq_dot(trade).SetTypeFillingBySymbol(_Symbol);
   ResetEngine();
   if(ArraySize(labSeq) == 0) LabReset();               // the Labouchere list is kept with the other recovery states when inputs change
   // restart memory: on a fresh start (MT5 or the EA restarted) continue from the saved state; switched off: forget it
   gPersist = InpRemember && MQLInfoInteger(MQL_TESTER) == 0 && MQLInfoInteger(MQL_OPTIMIZATION) == 0;
   gSvBase = SvBaseName(); gRestored = false;
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();
   gRestFlat = false; gBrokerPend = false;
   if(gPersist) gRestored = StateLoad();                 // a fresh start or new inputs: continue from the saved state (written at OnDeinit)
   if(gRestored && (gInitDone || !InpCapOn || InpCapAction != CAP_STOP)) capStop = false;   // a hard-cap Stop ends with new inputs (as before) or a cap that no longer stops
   if(gCrkPrPrev != (int)InpCrkPr || InpRec != REC_CRC) { crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; }
   gCrkPrPrev = (int)InpCrkPr;
   gHedgeOk = (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && !gHedgeOk) Print("Crooks C hedge rule: this account cannot hold a buy and a sell together (netting), so the rule forgets the loss instead."_mq);
   // markings and table only where they can be seen (not in non-visual tests or optimisation)
   gCanDraw = MQLInfoInteger(MQL_OPTIMIZATION) == 0 && (MQLInfoInteger(MQL_TESTER) == 0 || MQLInfoInteger(MQL_VISUAL_MODE) != 0);
   ObjectsDeleteAll(0, "ARM_"_mq);
   if(InpSpread < 0 || InpCommLot < 0) { Print("Spread and commission must be 0 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpTp1R > InpTp2R || InpTp2R > InpTp3R || InpTp3R > InpTp4R) { Print("Targets must be in order: TP1 <= TP2 <= TP3 <= TP4."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpMaxVwOn && InpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpTouchVwOn && InpTouchVwN < 1) { Print("VWAP touched in the last N candles: N must be 1 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpCrkT1 && (InpCrkT1Pct < 10 || InpCrkT1Pct > 90)) { Print("Crooks TP1 rule: % closed at TP1 must be 10 to 90."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr != CPR_OFF && (InpCrkPrN < 1 || InpCrkPrM < 1 || InpCrkPrD < 1)) { Print("Crooks C rule: N, M and D must be 1 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((InpMLockOn && InpMLockAmt <= 0) || (InpPLockOn && (InpPLockAt <= 0 || InpPLockPct < 1 || InpPLockPct > 100))) { Print("Monthly profit lock: the amounts must be above 0 and the lock % 1 to 100."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0 || InpCrkHgTp <= 0)) { Print("Crooks C hedge rule: stop loss and take profit must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100)) { Print("Crooks C rule: % of the loss must be 10 to 100."_mq); return INIT_PARAMETERS_INCORRECT; }
   // warm up the engine on history (no orders): it ends in the same state as the TradingView engine would
   int bars = Bars(_Symbol, _Period);
   int look = (int)MathMax(MathMax(InpStructLen, InpBrkLen + 1), MathMax(InpMomLen + 1, InpStopLen)) + 2;
   int need = look + InpAtrLen + 10;
   if(bars < need) { Print("Not enough chart history yet ("_mq, bars, " bars, need "_mq, need, "); scroll the chart back or load more history, then attach the EA again."_mq); return INIT_FAILED; }
   int start = (int)MathMin(InpWarmBars, bars - look - 1);
   if(gRestored && gSvLast > 0)                         // reach back to the saved bar, so every day since then is counted (at most 100,000 bars)
   {
      int sh = iBarShift(_Symbol, _Period, gSvLast, false);
      if(sh < 0 || sh > start) start = (int)MathMin(sh < 0 ? 100000 : MathMin(sh, 100000), bars - look - 1);
   }
   gLive = false;
   for(int s = start; s >= 1; s--)
   {
      ProcessBar(s);
      if(gRestored && gSvLast > 0 && iTime(_Symbol, _Period, s) > gSvLast)   // the bars since the saved state count like bars missed in a disconnect
      {
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
   if(gBrokerPend) Print("Waiting for the connection to the trade server before checking positions and deals."_mq);
   else BrokerStart();
   gStateTxt = StateText(false);
   UpdateTable();
   StateSave(true);                                      // restart memory: the state after this start
   gInitDone = true;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   Comment(""_mq);
   // after a Strategy Tester run the markings stay on the visual chart; everywhere else they are removed with the EA
   if(MQLInfoInteger(MQL_TESTER) == 0) ObjectsDeleteAll(0, "ARM_"_mq);
}

void OnChartEvent(const int id, const mql_long &lparam, const double &dparam, const string &sparam)
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
      bool caught = false; mql_long biBefore = bi;
      for(int s = sh - 1; s >= 2; s--)                                 // bars missed while offline: engine only
      {
         ProcessBar(s); caught = true; if(gNewDay) gDayPendN++;
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

#line 1980 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
typedef void (*mq_t_OnTick)();
static mq_t_OnTick mq_chk_OnTick = &OnTick;
#line 1964 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
typedef void (*mq_t_OnDeinit)(const int);
static mq_t_OnDeinit mq_chk_OnDeinit = &OnDeinit;
#line 1972 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
typedef void (*mq_t_OnChartEvent)(const int, const mql_long&, const double&, const string&);
static mq_t_OnChartEvent mq_chk_OnChartEvent = &OnChartEvent;
#line 1 "<rt-wrapper>"
extern "C" int rt_SetInput(const char* name, double v)
{
   if(__builtin_strcmp(name, "InpStructLen") == 0) { InpStructLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpBrkLen") == 0) { InpBrkLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpEntryLen") == 0) { InpEntryLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpRetestBars") == 0) { InpRetestBars = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDispAtr") == 0) { InpDispAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpBodyPct") == 0) { InpBodyPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpClosePct") == 0) { InpClosePct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMomLen") == 0) { InpMomLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMomAtr") == 0) { InpMomAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCmoMin") == 0) { InpCmoMin = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpRearm") == 0) { InpRearm = (ENUM_REARM)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpStopMode") == 0) { InpStopMode = (ENUM_STOP_MODE)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpStopAtr") == 0) { InpStopAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpStopLen") == 0) { InpStopLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpStopBufAtr") == 0) { InpStopBufAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpHalfStop") == 0) { InpHalfStop = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHalfStopAtr") == 0) { InpHalfStopAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpBiasNet") == 0) { InpBiasNet = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpImpBody") == 0) { InpImpBody = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpHalfOpenOut") == 0) { InpHalfOpenOut = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHalfStrict") == 0) { InpHalfStrict = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHalfCap") == 0) { InpHalfCap = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpCooldown") == 0) { InpCooldown = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMaxFills") == 0) { InpMaxFills = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDayStopR") == 0) { InpDayStopR = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpFillBarStopR") == 0) { InpFillBarStopR = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpLegReset") == 0) { InpLegReset = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpAtrLen") == 0) { InpAtrLen = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpVwapFilter") == 0) { InpVwapFilter = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpSlopeBars") == 0) { InpSlopeBars = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpSlopeCross") == 0) { InpSlopeCross = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMinOpenBars") == 0) { InpMinOpenBars = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpSkipSunday") == 0) { InpSkipSunday = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpDeepOn") == 0) { InpDeepOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpDeepFar") == 0) { InpDeepFar = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpAllowLong") == 0) { InpAllowLong = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpAllowShort") == 0) { InpAllowShort = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpVwapAnchor") == 0) { InpVwapAnchor = (ENUM_VW_ANCHOR)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpVwapSrc") == 0) { InpVwapSrc = (ENUM_APPLIED_PRICE)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpEntryMode") == 0) { InpEntryMode = (ENUM_ENTRY_MODE)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpEntryPct") == 0) { InpEntryPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTp1R") == 0) { InpTp1R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTp2R") == 0) { InpTp2R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTp3R") == 0) { InpTp3R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTp4R") == 0) { InpTp4R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpExitAt") == 0) { InpExitAt = (ENUM_EXIT_AT)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpMv1On") == 0) { InpMv1On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMv1R") == 0) { InpMv1R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMv2On") == 0) { InpMv2On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMv2R") == 0) { InpMv2R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMv3On") == 0) { InpMv3On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMv3R") == 0) { InpMv3R = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpNoChase") == 0) { InpNoChase = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpNoChaseSig") == 0) { InpNoChaseSig = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpLossBlock") == 0) { InpLossBlock = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpChopOn") == 0) { InpChopOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpChopMax") == 0) { InpChopMax = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpEmaOn") == 0) { InpEmaOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpEmaMax") == 0) { InpEmaMax = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMinVwOn") == 0) { InpMinVwOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMinVwAtr") == 0) { InpMinVwAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMaxVwOn") == 0) { InpMaxVwOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMaxVwDist") == 0) { InpMaxVwDist = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMaxVwUnit") == 0) { InpMaxVwUnit = (ENUM_VW_UNIT)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpStopVwOn") == 0) { InpStopVwOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpStopVwBuf") == 0) { InpStopVwBuf = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpTouchVwOn") == 0) { InpTouchVwOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTouchVwN") == 0) { InpTouchVwN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpEntVwOn") == 0) { InpEntVwOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpEntVwAtr") == 0) { InpEntVwAtr = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpServerTz") == 0) { InpServerTz = (ENUM_SRV_TZ)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpServerGMT") == 0) { InpServerGMT = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpUserGMT") == 0) { InpUserGMT = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpDayOn") == 0) { InpDayOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMon") == 0) { InpMon = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTue") == 0) { InpTue = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpWed") == 0) { InpWed = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpThu") == 0) { InpThu = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpFri") == 0) { InpFri = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpSat") == 0) { InpSat = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpSun") == 0) { InpSun = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHoursOn") == 0) { InpHoursOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpStartH") == 0) { InpStartH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpStartM") == 0) { InpStartM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpEndH") == 0) { InpEndH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpEndM") == 0) { InpEndM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpKzOn") == 0) { InpKzOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpKzAsia") == 0) { InpKzAsia = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpKzLon") == 0) { InpKzLon = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpKzNy") == 0) { InpKzNy = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpKzLc") == 0) { InpKzLc = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpKzAuto") == 0) { InpKzAuto = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpKzShift") == 0) { InpKzShift = (ENUM_KZ_SHIFT)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpP1") == 0) { InpP1 = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpP2") == 0) { InpP2 = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpP3") == 0) { InpP3 = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpBaseRisk") == 0) { InpBaseRisk = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCapOn") == 0) { InpCapOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpHardCap") == 0) { InpHardCap = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCapAction") == 0) { InpCapAction = (ENUM_CAP_ACTION)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpLeverage") == 0) { InpLeverage = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpLotStep") == 0) { InpLotStep = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpLotRound") == 0) { InpLotRound = (ENUM_LOT_ROUND)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpSmallLot") == 0) { InpSmallLot = (ENUM_SMALL_LOT)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpSpread") == 0) { InpSpread = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCommLot") == 0) { InpCommLot = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpEarnBack") == 0) { InpEarnBack = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpBidChart") == 0) { InpBidChart = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpLStopOn") == 0) { InpLStopOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpLStopN") == 0) { InpLStopN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpWStopOn") == 0) { InpWStopOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpWStopN") == 0) { InpWStopN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpPauseOn") == 0) { InpPauseOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpPauseN") == 0) { InpPauseN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpPauseDays") == 0) { InpPauseDays = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMLockOn") == 0) { InpMLockOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMLockAmt") == 0) { InpMLockAmt = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpPLockOn") == 0) { InpPLockOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpPLockAt") == 0) { InpPLockAt = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpPLockPct") == 0) { InpPLockPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpMRestart") == 0) { InpMRestart = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpRemember") == 0) { InpRemember = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpFcOn") == 0) { InpFcOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpFcH") == 0) { InpFcH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpFcM") == 0) { InpFcM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpWeekendOn") == 0) { InpWeekendOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpNewsPre") == 0) { InpNewsPre = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsOn") == 0) { InpDNewsOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpDNewsH") == 0) { InpDNewsH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsM") == 0) { InpDNewsM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsDur") == 0) { InpDNewsDur = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsAuto") == 0) { InpDNewsAuto = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpN1On") == 0) { InpN1On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpN1T") == 0) { InpN1T = (datetime)v; return 1; }
   if(__builtin_strcmp(name, "InpN1Dur") == 0) { InpN1Dur = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpN2On") == 0) { InpN2On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpN2T") == 0) { InpN2T = (datetime)v; return 1; }
   if(__builtin_strcmp(name, "InpN2Dur") == 0) { InpN2Dur = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpN3On") == 0) { InpN3On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpN3T") == 0) { InpN3T = (datetime)v; return 1; }
   if(__builtin_strcmp(name, "InpN3Dur") == 0) { InpN3Dur = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpN4On") == 0) { InpN4On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpN4T") == 0) { InpN4T = (datetime)v; return 1; }
   if(__builtin_strcmp(name, "InpN4Dur") == 0) { InpN4Dur = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpN5On") == 0) { InpN5On = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpN5T") == 0) { InpN5T = (datetime)v; return 1; }
   if(__builtin_strcmp(name, "InpN5Dur") == 0) { InpN5Dur = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpRec") == 0) { InpRec = (ENUM_REC)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpRecN") == 0) { InpRecN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpRecPct") == 0) { InpRecPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpRecMult") == 0) { InpRecMult = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpRecStep") == 0) { InpRecStep = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCSplit") == 0) { InpCSplit = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkT1") == 0) { InpCrkT1 = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpCrkT1Stop") == 0) { InpCrkT1Stop = (ENUM_T1_STOP)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkT1Pct") == 0) { InpCrkT1Pct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkT1Any") == 0) { InpCrkT1Any = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpCrkCnOn") == 0) { InpCrkCnOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpCrkCn") == 0) { InpCrkCn = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPr") == 0) { InpCrkPr = (ENUM_CRK_PR)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrN") == 0) { InpCrkPrN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrPct") == 0) { InpCrkPrPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrM") == 0) { InpCrkPrM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrD") == 0) { InpCrkPrD = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkPrForget") == 0) { InpCrkPrForget = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpCrkPrAll") == 0) { InpCrkPrAll = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpCrkHgSl") == 0) { InpCrkHgSl = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkHgTp") == 0) { InpCrkHgTp = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkHgUnit") == 0) { InpCrkHgUnit = (ENUM_HG_UNIT)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkHgForget") == 0) { InpCrkHgForget = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpParN") == 0) { InpParN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDelayN") == 0) { InpDelayN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpEqPct") == 0) { InpEqPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpDraw") == 0) { InpDraw = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMaxDrawn") == 0) { InpMaxDrawn = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpColTarget") == 0) { InpColTarget = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpColStop") == 0) { InpColStop = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpColEntry") == 0) { InpColEntry = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpShowTable") == 0) { InpShowTable = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTablePos") == 0) { InpTablePos = (ENUM_TBL_POS)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpTableFont") == 0) { InpTableFont = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMagic") == 0) { InpMagic = (mql_long)v; return 1; }
   if(__builtin_strcmp(name, "InpWarmBars") == 0) { InpWarmBars = (int)v; return 1; }
   return 0;
}
struct RtEv { int fill, fillL, exit, win; long long bi, armBar; double lim, stp, stp0, res; };
extern "C" void rt_reset() { ResetEngine(); }
extern "C" int rt_look() { return (int)MathMax(MathMax(InpStructLen, InpBrkLen + 1), MathMax(InpMomLen + 1, InpStopLen)) + 2; }
extern "C" void rt_step(int s, RtEv* e) { ProcessBar(s); e->fill = evFill; e->fillL = evFillL; e->exit = evExit; e->win = evWin; e->bi = bi; e->armBar = armBar; e->lim = lim; e->stp = stp; e->stp0 = stp0; e->res = evRes; }
extern "C" void rt_stats(double* o) { o[0] = totW; o[1] = totL; o[2] = totR; o[3] = tpHitN[0]; o[4] = tpHitN[1]; o[5] = tpHitN[2]; o[6] = tpHitN[3]; o[7] = beN; o[8] = lkN; o[9] = ghW; o[10] = ghL; o[11] = ghR; }
#line 1 "<rec-wrapper>"
// what TakeSetup / the per-bar P&L update / BookClosed do with the money-management state (no broker calls)
extern "C" void rec_init() { LabReset(); gCrkPrPrev = (int)InpCrkPr; }   // as after the first OnInit
extern "C" double rec_next(double exitR) { return NextRisk(exitR); }
extern "C" void rec_take() { crkRec = CrkRecNext(); }
extern "C" void rec_part(double np) { exPnl += np; totalNet += np; if(np != 0) carried = MathMax(0.0, carried - np); }
extern "C" void rec_close() { BookClosed(); }
extern "C" int rec_capstop() { return capStop ? 1 : 0; }
// TP1 rule: the engine's stop distance and the spread of the next setup, then whether the EA uses the TP1 rule for it
extern "C" void rec_setup(double risk, double spread) { trRisk = risk; rec_tv = 1.0; rec_bid = 1000.0; rec_ask = 1000.0 + spread; }
extern "C" int rec_t1() { return CrkT1Dist() > 0 ? 1 : 0; }
// Crooks C skip rule: a new day (counted or not) while trading is paused, and whether the next signal is skipped by the pause
extern "C" void rec_day(int counted) { CrkDayCount(counted != 0); }
extern "C" int rec_paused() { return CrkPause() ? 1 : 0; }
// v4.1 hedge rule: hedging account on/off, close the pair (lastOut = profit of the trade that closed last), state getters
extern "C" void rec_hgok(int on) { gHedgeOk = on != 0; }
extern "C" void rec_hgclose(double lastOut) { exHg = true; gLastOutProfit = lastOut; BookClosed(); }
extern "C" int rec_hgnow() { return CrkHedgeNow() ? 1 : 0; }
extern "C" double rec_owed() { return crkL; }
// v4.2 monthly profit lock: a month tick (your time zone), closed P&L, the checks, the restart once flat
extern "C" void rec_mtick(long long t) { MonthTick((datetime)t); }
extern "C" void rec_mpnl(double p) { monPnl += p; }
extern "C" int rec_mcheck() { MonthCheck(); return monStop ? 1 : 0; }
extern "C" int rec_mrestart() { if(monRestPend && exState == 0) { monRestPend = false; RecoveryRestart(); return 1; } return 0; }
extern "C" double rec_mpeak() { return monPeak; }
// lot sizing test: the EA's own LotsFor() with a set lot step / minimum / maximum, equity, tick value and spread
extern "C" double rec_lots(double risk, double sd, double entry, int isL, double ld, double tv, double spread, double vstep, double vmin, double eq)
{ rec_tv = tv; rec_bid = entry; rec_ask = entry + spread; rec_vstep = vstep; rec_vmin = vmin; rec_vmax = 100.0; rec_eq = eq; return LotsFor(risk, sd, entry, isL != 0, ld); }
// v4.3 restart memory: save, a fresh program load (every global back to its initial value), then what OnInit does with the saved state
extern "C" void rec_fresh();
extern "C" void rec_restart()
{
   bool hgOk = gHedgeOk;                                  // from the account in OnInit, not saved
   gPersist = true; gSvBase = "T|"; if(gLastDone <= 0) gLastDone = 1;   // as if a bar was processed (the harness has no bars)
   StateSave(true);
   rec_fresh();
   gPersist = true; gSvBase = "T|"; gHedgeOk = hgOk;
   if(ArraySize(labSeq) == 0) LabReset();
   if(!StateLoad()) Print("restart memory: nothing saved");
   if(gCrkPrPrev != (int)InpCrkPr || InpRec != REC_CRC) { crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; }
   gCrkPrPrev = (int)InpCrkPr;
}
extern "C" void rec_fresh()
{
   gLastBarTime = 0;
   bi = -1;
   gLive = false;
   cumPV = 0;
   cumPV2 = 0;
   cumW = 0;
   cumP = 0;
   cumP2 = 0;
   cumN = 0;
   vwBars = 0;
   sessN = 0;
   ArrayResize(vwHist, 0);
   atrV = 0;
   atrN = 0;
   atrSum = 0;
   lastDayKey = -1;
   dayFills = 0;
   dayW = 0;
   dayL = 0;
   dayR = 0;
   dayRiskR = 0;
   lossDirBlk = 0;
   bullN = 0;
   bearN = 0;
   prevNet = 0;
   havePrev = false;
   sesO = 0;
   sesH = 0;
   sesL = 0;
   pdH = 0;
   pdL = 0;
   haveSes = false;
   havePd = false;
   st = 0;
   armBar = -1;
   fillBar = -1;
   lastExit = -1;
   lastFill = -1;
   lastDir = 0;
   lim = 0;
   stp = 0;
   stp0 = 0;
   trRisk = 0;
   t1 = 0;
   t2 = 0;
   t3 = 0;
   t4 = 0;
   tF = 0;
   tpHit = 0;
   trHalf = false;
   trGhost = false;
   trSkip = 0;
   totW = 0;
   totL = 0;
   totR = 0;
   lastRes = "-";
   bestPx = 0;
   ghW = 0;
   ghL = 0;
   ghR = 0;
   vxSide = 0;
   vxN = 0;
   tchL = 1000000;
   tchS = 1000000;
   hK = -1;
   hC = 0;
   hSum = 0;
   hNum = 0;
   for(int q_ = 0; q_ < 4; q_++) hE[q_] = 0;
   for(int q_ = 0; q_ < 4; q_++) tpHitN[q_] = 0;
   beN = 0;
   lkN = 0;
   gFirstT = 0;
   evArm = false;
   evArmL = false;
   evFill = false;
   evFillL = false;
   evExit = false;
   evWin = false;
   evMove = false;
   evTp = false;
   evRes = 0;
   evCancel = 0;
   gNewDay = false;
   gDayOk = true;
   gHourOk = true;
   gKzOk = true;
   gT1Seen = false;
   lastAnchorKey = -1;
   gLastDone = 0;
   exState = 0;
   exL = true;
   exLots = 0;
   exRiskAmt = 0;
   exCostPx = 0;
   exPnl = 0;
   exArm = -1;
   exSynced = false;
   gRearm = false;
   gVirt = false;
   gDayPendN = 0;
   gPrevT = 0;
   for(int q_ = 0; q_ < 3; q_++) pDone[q_] = false;
   lastDeal = 0;
   sigN = 0;
   takenN = 0;
   skipN = 0;
   missN = 0;
   skipWhy = "";
   gDrawT = 0;
   gDrawOn = false;
   gCanDraw = true;
   ArrayResize(gDrawn, 0);
   gStateTxt = "SCANNING";
   gTblW = -1;
   gTblH = -1;
   ArrayResize(tblKey, 0);
   ArrayResize(tblVal, 0);
   ArrayResize(tblCol, 0);
   ArrayResize(tblBg, 0);
   dayPnl = 0;
   lossRow = 0;
   winRow = 0;
   dayBlock = false;
   pauseLeft = 0;
   paused = false;
   recPool = 0;
   recLosses = 0;
   dUnits = 1;
   carried = 0;
   capStop = false;
   ArrayResize(labSeq, 0);
   parWins = 0;
   rdUnits = 1;
   oscU = 1;
   oscP = 0;
   crkL = 0;
   crkN = 0;
   crkRec = false;
   crkW = false;
   crkP = 0;
   crkF = 0;
   crkWait = false;
   crkWW = 0;
   crkNeedL = false;
   crkSkip = false;
   crkSkipLeft = 0;
   crkUDay = -1;
   crkHg = false;
   exHg = false;
   exHgS = 0;
   exHgT = 0;
   gLastOutProfit = 0;
   gMonKey = -1;
   monPnl = 0;
   monPeak = 0;
   monStop = false;
   monLocked = false;
   monRestPend = false;
   gHedgeOk = false;
   gPauseArm = -1;
   gCrkPrPrev = -1;
   gInitDone = false;
   gPersist = false;
   gSvBase = "";
   gRestored = false;
   gSvT = 0;
   gSvLast = 0;
   ArrayResize(gIoN, 0);
   ArrayResize(gIoV, 0);
   gIoC = 0;
   gIoSave = true;
   ArrayResize(gSvN, 0);
   ArrayResize(gSvV, 0);
   gSvC = 0;
   gBrokerPend = false;
   gRestFlat = false;
   gSvFullT = 0;
   gSvAcc = 0;
   exT1MvPend = false;
   exT1 = false;
   exT1Half = false;
   exT1Be = false;
   exT1Stop = 0;
   exT1Tp1 = 0;
   exT1Tp2 = 0;
   exT1Tight = 0;
   exT1Entry = 0;
   exKeepSl = 0;
   totalNet = 0;
   exW = 0;
   exLn = 0;
}
