#include "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/sim/mql5rt_sim.h"
#line 1 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/sim/EA_sim51.mq5"
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
//| The VWAP line the EA trades on is drawn on the chart (on by      |
//| default; DISPLAY inputs).                                        |
//| v4.5: Crooks E - J: Crooks C with smaller trades or a limit on   |
//| the recovery trade, so a long losing run costs less.             |
//| v4.6: PROFIT LADDER for Crooks F - J: after a first profit the   |
//| risk grows, paid only from the profit above a lock (5 levels).   |
//| v4.7: POSITION SIZE: Fixed $ risk, Fixed lots or % of equity at  |
//| risk; the loss recovery sizes every trade from that base.        |
//| v4.8: STRATEGY PRESET (top of the inputs): Custom or one of the  |
//| 25 tested catalogue strategies (M1 S1-S4, M5 S1-S4, M15 S1-S9,   |
//| H1 S1-S8), each on its own chart timeframe; "Add my filters"     |
//| adds your days, hours, kill zones and news. The monthly restart  |
//| also restarts the profit ladder and a hard-cap stop.             |
//| v4.9: BE TRIGGER (stop to the entry once the trade is X R up)    |
//| and SALVAGE TRIGGER (target to the entry once it is X R down),   |
//| off by default; they work with any preset (TradingView too).     |
//| v5.0: SIZE BY: the base and every loss-recovery amount can be    |
//| the PROFIT at the final TP (the stop-out loss follows from it).  |
//| Crooks K: Crooks J above the start, below it a careful size      |
//| after a win (lots, $ or % of base) and 0.01 lot after a loss.    |
//| Crooks L: 0.01 lot until a win, then the loss is split by the    |
//| drawdown (below the start / below the best); at a new best the   |
//| base grows with the profit.                                      |
//| v5.1: Size by Profit includes the costs: a final-TP win is the   |
//| amount itself (v5.0 came short by the spread and commission).    |
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
enum ENUM_SIZE_MODE { PSZ_USD = 0,     // Fixed $ risk (Base risk per trade)
                      PSZ_LOT = 1,     // Fixed lots (Base lots)
                      PSZ_PCT = 2 };   // % of equity at risk (Risk % of equity)
enum ENUM_SIZE_BY   { SZB_RISK   = 0,  // Risk: the loss at the stop
                      SZB_PROFIT = 1 };// Profit: the win at the final TP
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
   REC_CRD   = 21, // Crooks D (base, base, recovery: every 3rd trade)
   REC_CRE   = 22, // Crooks E (Crooks C, 0.01 lot while waiting for a win)
   REC_CRF   = 23, // Crooks F (Crooks C, recovery at most K x base)
   REC_CRG   = 24, // Crooks G (Crooks C, loss to win back at most X x base)
   REC_CRH   = 25, // Crooks H (Crooks C, recovery at most % of equity)
   REC_CRI   = 26, // Crooks I (Crooks E + recovery at most K x base)
   REC_CRJ   = 27, // Crooks J (Crooks C, recovery shrinks in a drawdown)
   REC_CRK   = 28, // Crooks K (Crooks J above the start, careful size below it)
   REC_CRL   = 29  // Crooks L (0.01 lot until a win, the loss split by the drawdown)
};
enum ENUM_CRK_PR { CPR_OFF    = 0,   // Off (Crooks C as now)
                   CPR_FORGET = 1,   // Forget the loss
                   CPR_PCT    = 2,   // Go for a % of the loss, forget it after N
                   CPR_WAIT   = 3,   // Wait for M wins in a row, then a loss and a win
                   CPR_SKIP   = 4,   // Skip D trading days
                   CPR_HEDGE  = 5 }; // Hedge: a buy and a sell on the next signal (hedging account)
enum ENUM_HG_UNIT { HGU_R     = 0,   // R (x the signal's stop distance)
                    HGU_PRICE = 1 }; // Price (e.g. 5.0 = $5 on gold)

//--- v4.8 STRATEGY PRESET (the top of the inputs): Custom = your settings below; a preset = a tested catalogue strategy (every signal setting,
//--- its own hours or kill zone, the 70% partial close of M15-S2 / S4 / S5 and H1-S2 / S4 / S5), only on its own chart timeframe
enum ENUM_PRESET { PRE_CUSTOM  =  0, // Custom (my settings below)
                   PRE_M1_S1   =  1, // M1-S1 Most profit
                   PRE_M1_S2   =  2, // M1-S2 Shortest losing streak
                   PRE_M1_S3   =  3, // M1-S3 Most trades a day
                   PRE_M1_S4   =  4, // M1-S4 Simplest
                   PRE_M5_S1   =  5, // M5-S1 Most profit
                   PRE_M5_S2   =  6, // M5-S2 Shortest losing streak
                   PRE_M5_S3   =  7, // M5-S3 Most trades a day
                   PRE_M5_S4   =  8, // M5-S4 Simplest
                   PRE_M15_S1  =  9, // M15-S1 Most profit
                   PRE_M15_S2  = 10, // M15-S2 Shortest losing streak (70% closed at TP1)
                   PRE_M15_S3  = 11, // M15-S3 Shortest losing streak, no partial close
                   PRE_M15_S4  = 12, // M15-S4 Longest winning streak (70% closed at TP1)
                   PRE_M15_S5  = 13, // M15-S5 Highest win rate (70% closed at TP1)
                   PRE_M15_S6  = 14, // M15-S6 Most trades a day
                   PRE_M15_S7  = 15, // M15-S7 Every year positive
                   PRE_M15_S8  = 16, // M15-S8 Simplest
                   PRE_M15_S9  = 17, // M15-S9 Asia session only
                   PRE_H1_S1   = 18, // H1-S1 Most profit
                   PRE_H1_S2   = 19, // H1-S2 Shortest losing streak (70% closed at TP1)
                   PRE_H1_S3   = 20, // H1-S3 Shortest losing streak, no partial close
                   PRE_H1_S4   = 21, // H1-S4 Longest winning streak (70% closed at TP1)
                   PRE_H1_S5   = 22, // H1-S5 Highest win rate (70% closed at TP1)
                   PRE_H1_S6   = 23, // H1-S6 Most trades a day
                   PRE_H1_S7   = 24, // H1-S7 Smoothest
                   PRE_H1_S8   = 25  // H1-S8 Simplest
                 };
  
 ENUM_PRESET InpPreset = PRE_CUSTOM; // Strategy preset (only on its own chart timeframe; force-close, risk, recovery stay yours)
 bool   InpAddMine  = false;  // Add my filters to the preset (days, news; my hours / kill zones replace its own)

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
 bool   InpBeOn  = false; // BE trigger: stop to the entry once the trade is up (R; works with any preset)
 double InpBeR   = 1.5;   //   ...R in profit (gold test: 1.5 best on M5 and M15; early values lose)
 bool   InpSvOn  = false; // Salvage trigger: target to the entry once the trade is down (R; any preset)
 double InpSvR   = 0.9;   //   ...R against the trade (below 1; gold test: best off, 0.9 the least harm)

  
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

  
enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1,   // Fixed: the GMT offset below
                   SRV_EET     = 2,   // GMT+2 winter / GMT+3 EU summer time (EET brokers, e.g. FxPro)
                   SRV_AUTO    = 3 }; // Auto: read the broker's clock from MT5 (Strategy Tester: EU summer time)
 ENUM_SRV_TZ InpServerTz = SRV_AUTO;    // Broker server clock
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

  
 ENUM_SIZE_MODE InpSizeMode = PSZ_USD; // Position size: the base trade (the loss recovery sizes every trade from it)
 ENUM_SIZE_BY InpSizeBy = SZB_RISK;     // Base and recovery amounts are (Risk: lost at the stop; Profit: won at the final TP)
 double InpBaseRisk = 50.0;   // Base risk per trade (account currency; Fixed $ risk)
 double InpBaseLots = 0.01;   // Base lots (Fixed lots)
 double InpEqPct    = 1.0;    // Risk % of equity (% of equity at risk, and the % of equity rule)
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
 bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (also the profit ladder and a hard-cap stop; after a trade still open closes)

  
 bool   InpRemember = true;   // Continue after a restart (keep the loss recovery, streaks and pauses when MT5 or the EA restarts)
 bool   InpMemFresh = false;  // Start fresh once: forget the loss recovery, streaks and pauses (true + OK; set false again later)

  
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

enum ENUM_LADDER { LAD_OFF   = 0,  // Off
                   LAD_LOW   = 1,  // Low (keeps 80% of the best profit, base up to 2x)
                   LAD_MED   = 2,  // Medium (keeps 70%, base up to 3x)
                   LAD_HIGH  = 3,  // High (keeps 60%, base up to 5x)
                   LAD_XHIGH = 4,  // Extra high (keeps 50%, base up to 8x)
                   LAD_MAX   = 5   // Max (keeps 40%, base up to 12x)
};
enum ENUM_CRK_K { CKM_LOTS = 0,  // Lots
                  CKM_USD  = 1,  // Fixed amount (account currency)
                  CKM_PCT  = 2 };// % of the base
  
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
 bool   InpCrkCnOn  = false;  // Crooks C (and E-J): win the loss back over N wins
 int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)
 ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C (and E-J): after N losing recovery trades in a row
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
 double InpCrkELot  = 0.01;   // Crooks E / I / K / L: lot of the trades while a loss waits for a win (the normal size if smaller)
 double InpCrkFK    = 3.0;    // Crooks F / I: a recovery trade risks at most this many x the base risk
 double InpCrkGX    = 10.0;   // Crooks G: the loss to win back is at most this many x the base risk (the rest is accepted)
 double InpCrkHPct  = 1.0;    // Crooks H: a recovery trade risks at most this % of the equity
 double InpCrkJX    = 20.0;   // Crooks J / K: drawdown (x the base risk) at which a recovery trade is back to the base risk
 ENUM_CRK_K InpCrkKMode = CKM_LOTS; // Crooks K: careful size below the start, after a win (after a loss: the E / I lot)
 double InpCrkKLots = 0.02;   //   ...lots (Lots)
 double InpCrkKUsd  = 25.0;   //   ...amount (Fixed amount; with Size by Profit: the win at the final TP)
 double InpCrkKPct  = 50.0;   //   ...% of the base (% of the base)
 double InpCrkLZ1   = 2.0;    // Crooks L: below the start, 1 part per this many x base of drawdown (from the start)
 int    InpCrkLZ1N  = 6;      //   ...most parts below the start
 double InpCrkLZ2   = 5.0;    // Crooks L: above the start, 1 part per this many x base below the best
 int    InpCrkLZ2N  = 3;      //   ...most parts above the start
 double InpCrkLGrow = 10.0;   // Crooks L: at a new best the base grows by this % of the profit
 double InpCrkLGrowX = 4.0;   //   ...base at most this many x
 ENUM_LADDER InpLadder = LAD_OFF; // Profit ladder (Crooks F-K): risk appetite once the profit target is reached
 double InpLadT     = 1000.0; //   ...profit target before the risk goes up ($, closed profit of this EA)
 int    InpParN     = 3;      // Paroli: wins before reset
 int    InpDelayN   = 2;      // Delayed: losses before recovery starts

enum ENUM_TBL_POS { TBL_TOP_RIGHT    = 0,  // Top right
                    TBL_TOP_LEFT     = 1,  // Top left
                    TBL_BOTTOM_RIGHT = 2,  // Bottom right
                    TBL_BOTTOM_LEFT  = 3 };// Bottom left
  
 bool   InpDraw      = true;              // Show trade markings (entry, stop, targets, result)
 int    InpMaxDrawn  = 0;                 //   trades kept on the chart (0 = all)
 color  InpColTarget = clrMediumSeaGreen; //   target box and TP lines
 color  InpColStop   = clrIndianRed;      //   stop box
 color  InpColEntry  = clrDodgerBlue;     //   entry line and armed limit
 bool   InpVwapShow  = true;              // Show the VWAP line (the one the EA trades on)
 color  InpVwapColor = ((color)14798925);     //   VWAP color
 int    InpVwapWidth = 2;                 //   VWAP line width (1-5)
 int    InpVwapBars  = 1500;              //   bars of VWAP drawn (50-20000; older parts are removed)
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
int      trTrig = 0;                                     // v4.9: the trigger that acted in the live trade (0 none, 1 BE, 2 salvage)
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
int      svN = 0;                  // v4.9: closed at the entry by the salvage target (0R)
datetime gFirstT = 0;              // first bar the engine processed
// events of the last processed bar (shown setups / trades only)
bool     evArm, evArmL, evFill, evFillL, evExit, evWin, evMove, evTp; double evRes; int evCancel; // 0 none, 1 expired, 2 replaced
bool     evSalv; int evTrig;            // v4.9: an exit at the entry by the salvage target; a BE (1) / salvage (2) trigger acted on this bar
bool     gNewDay = false, gDayOk = true, gHourOk = true, gKzOk = true;
bool     gT1Seen = false;          // Crooks TP1 rule: TP1 was reached (on a bar caught up after a disconnect, or the partial close failed) and the TP1 part is still to be booked
int      lastAnchorKey = -1;
datetime gLastDone = 0;            // open time of the last bar the engine processed

// EXECUTION state
int      exState = 0;              // 0 nothing, 1 entry order working, 2 in a position
bool     exL = true;
double   exLots = 0, exRiskAmt = 0, exCostPx = 0, exPnl = 0;
double   gBase = 0;    // v4.7: the base risk of the setup being sized (NextRisk); the trade keeps it in exBase
double   exBase = 0;   // v4.7: the base risk of the EA's trade (its booking: Oscar's Grind, Crooks G)
double   gBaseWin = 0, exBaseWin = 0;   // v5.1: the base WIN at the final TP of the setup being sized / of the EA's trade (Profit: Oscar's goal)
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
//--- v4.8 the values the EA uses: the inputs (Custom) or the preset's (PresetApply)
int gpStructLen;
int gpBrkLen;
int gpEntryLen;
int gpRetestBars;
double gpDispAtr;
double gpBodyPct;
double gpClosePct;
int gpMomLen;
double gpMomAtr;
double gpCmoMin;
ENUM_REARM gpRearm;
ENUM_STOP_MODE gpStopMode;
double gpStopAtr;
int gpStopLen;
double gpStopBufAtr;
bool gpHalfStop;
double gpHalfStopAtr;
int gpBiasNet;
double gpImpBody;
bool gpHalfOpenOut;
bool gpHalfStrict;
bool gpHalfCap;
int gpCooldown;
int gpMaxFills;
double gpDayStopR;
bool gpFillBarStopR;
bool gpLegReset;
int gpAtrLen;
bool gpVwapFilter;
int gpSlopeBars;
bool gpSlopeCross;
int gpMinOpenBars;
bool gpSkipSunday;
bool gpDeepOn;
double gpDeepFar;
bool gpAllowLong;
bool gpAllowShort;
ENUM_VW_ANCHOR gpVwapAnchor;
ENUM_APPLIED_PRICE gpVwapSrc;
ENUM_ENTRY_MODE gpEntryMode;
double gpEntryPct;
double gpTp1R;
double gpTp2R;
double gpTp3R;
double gpTp4R;
ENUM_EXIT_AT gpExitAt;
bool gpMv1On;
double gpMv1R;
bool gpMv2On;
double gpMv2R;
bool gpMv3On;
double gpMv3R;
bool gpNoChase;
double gpNoChaseSig;
bool gpLossBlock;
bool gpMinVwOn;
double gpMinVwAtr;
bool gpMaxVwOn;
double gpMaxVwDist;
ENUM_VW_UNIT gpMaxVwUnit;
bool gpStopVwOn;
double gpStopVwBuf;
bool gpTouchVwOn;
int gpTouchVwN;
bool gpEntVwOn;
double gpEntVwAtr;
bool gpChopOn;
double gpChopMax;
bool gpEmaOn;
double gpEmaMax;
bool gpDayOn;
bool gpHoursOn;
int gpStartH;
int gpStartM;
int gpEndH;
int gpEndM;
bool gpKzOn;
bool gpKzAsia;
bool gpKzLon;
bool gpKzNy;
bool gpKzLc;
bool gpKzAuto;
int gpKzShift;
bool gpDNewsOn;
bool gpN1On;
bool gpN2On;
bool gpN3On;
bool gpN4On;
bool gpN5On;
double gpP1;
double gpP2;
double gpP3;
bool   gpHrIst = false;                // the preset's own hours: Indian times
bool   gpTfOk = true;                  // the chart is on the preset's timeframe (always with Custom)
int    gpTf = 0;                       // the preset's timeframe (0 = Custom)
double gNet0 = 0;                      // v4.8 monthly restart: the closed profit at the last restart (the money rules count from it)
double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;
MqlArr<double>   labSeq; int parWins = 0; int rdUnits = 1; int oscU = 1; double oscP = 0;
double   crkL = 0; int crkN = 0; bool crkRec = false;   // Crooks: $ loss to win back, closed trades in the cycle, the open trade is a recovery trade
double   crkPk = 0;                                      // v4.5 Crooks J: the highest closed profit so far (its drawdown = crkPk - totalNet)
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
// v4.4
int      gTzMode = SRV_EET; double gTzFix = 2.0, gTzDet = -99; bool gTzWarned = false;   // broker clock: the rule in use (Auto) and its fixed offset; the offset read now (-99 unknown)
string   gCloseWhy = ""_mq; mql_long gCloseId = 0;                // why this EA closed a trade last, and that trade's position id
mql_long     gClosedIds[8]; int gClosedN = 0;                 // the last positions this EA closed (fully or partly): their reports say "this EA"
string   gLastClose = "-"_mq; bool gLastCloseOut = false;     // table: the last close; closed outside this EA (by hand, phone, another EA)
datetime exArmT = 0; double exLim = 0;                    // the EA's trade: its setup's arm bar time and entry level (re-linked after a restart / new inputs)
double   exTpL[3];                                        // the trade's own TP1-TP3 levels (partials)
bool     gOurFill = false, gOurExit = false, gOurWin = false, gOurMove = false;   // the engine's events for the EA's setup (arm bar exArm) on the last processed bar
bool     gMissFill = false, gMissExit = false, gMissWin = false, gMissMove = false;   //   ... on bars caught up after a disconnect
string   gLockN = ""_mq; double gLockV = 0;                  // one copy per symbol + magic number (temporary global variable)
int      gTfTrade = 0;                                    // the timeframe the EA trades: the one it was attached to (0 = not known yet)
datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
datetime gVwPrevT = 0, gVwCut = 0; double gVwPrev = 0; int gVwN = 1500;   // VWAP line: the previous bar and its VWAP, the oldest bar drawn, bars kept
bool     gExitRetry = false; string gExitWhy = ""_mq;        // a close that failed: tried again at every bar close, and why it was due
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
// the GMT offset of a summer-time rule (SRV_EET or SRV_NYCLOSE) at a server time
double RuleGMT(int md, datetime server)
{
   MqlDateTime d; TimeToStruct(server, d);
   if(md == SRV_EET)                                  // EU summer time: last Sunday of March to last Sunday of October
   {
      int es = LastSunday(mq_dot(d).year, 3), ee = LastSunday(mq_dot(d).year, 10);
      bool sum = (mq_dot(d).mon > 3 && mq_dot(d).mon < 10) || (mq_dot(d).mon == 3 && mq_dot(d).day >= es) || (mq_dot(d).mon == 10 && mq_dot(d).day < ee);
      return sum ? 3.0 : 2.0;
   }
   int ds = NthSunday(mq_dot(d).year, 3, 2), de = NthSunday(mq_dot(d).year, 11, 1);
   bool dst = (mq_dot(d).mon > 3 && mq_dot(d).mon < 11) || (mq_dot(d).mon == 3 && mq_dot(d).day >= ds) || (mq_dot(d).mon == 11 && mq_dot(d).day < de);
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
string SvExtra(string k) { return "ARX"_mq + StringSubstr(gSvBase, 3) + k; }
//--- MT5 deletes global variables not used for 4 weeks: the EA's own ones are rewritten once a day (the copy lock is temporary)
void ExtraRefresh()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;
   if(InpMemFresh) GlobalVariableSet(SvExtra("rsd"_mq), 1);
   if(gTfTrade > 0) GlobalVariableSet(SvExtra("tf"_mq), gTfTrade);
}
//--- the chart shows another timeframe than the one the EA was attached to: no new trades until it is back (live only)
bool   TfHold() { return gTfTrade > 0 && (int)_Period != gTfTrade && MQLInfoInteger(MQL_TESTER) == 0; }
string TfName(int p) { return p == PERIOD_M1 ? "M1"_mq : p == PERIOD_M5 ? "M5"_mq : p == PERIOD_M15 ? "M15"_mq : p == PERIOD_M30 ? "M30"_mq : p == PERIOD_H1 ? "H1"_mq : p == PERIOD_H4 ? "H4"_mq : p == PERIOD_D1 ? "D1"_mq : IntegerToString(p) + " min"_mq; }
//--- the broker's GMT offset now, read from MT5 (server time - GMT, to the nearest half hour); live and connected only, -99 = unknown
double TzNow()
{
   if(MQLInfoInteger(MQL_TESTER) != 0 || TerminalInfoInteger(TERMINAL_CONNECTED) == 0) return -99;
   datetime sv = TimeTradeServer(), g = TimeGMT();
   if(sv <= 0 || g <= 0) return -99;
   double d = MathRound((double)(sv - g) / 1800.0) / 2.0;
   return MathAbs(d) <= 14 ? d : -99;
}
string GmtTxt(double h) { return "GMT"_mq + (h >= 0 ? "+"_mq : ""_mq) + (MathAbs(h - MathRound(h)) < 0.01 ? IntegerToString((int)MathRound(h)) : DoubleToString(h, 1)); }
string TzTxt()                                          // the broker clock in use now (table)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;
   string r = GmtTxt(SrvGMT(TimeCurrent())) + (InpServerTz == SRV_AUTO ? " auto"_mq : ""_mq) + (md == SRV_EET ? " (EU summer time)"_mq : md == SRV_NYCLOSE ? " (US summer time)"_mq : " (fixed)"_mq);
   if(gTzDet > -90 && MathAbs(SrvGMT(TimeCurrent()) - gTzDet) > 0.01) r += " | broker "_mq + GmtTxt(gTzDet) + ": CHECK"_mq;
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
      GlobalVariableSet(SvExtra("tzm"_mq), md); GlobalVariableSet(SvExtra("tzf"_mq), fx);
   }
   else if(atStart && GlobalVariableCheck(SvExtra("tzm"_mq)))   // not connected yet: the clock read last time
   {
      md = (int)MathRound(GlobalVariableGet(SvExtra("tzm"_mq)));
      if(GlobalVariableCheck(SvExtra("tzf"_mq))) fx = GlobalVariableGet(SvExtra("tzf"_mq));
      if(md != SRV_EET && md != SRV_NYCLOSE && md != SRV_FIXED) md = SRV_EET;
   }
   if(InpServerTz == SRV_AUTO)
   {
      bool chg = md != gTzMode || (md == SRV_FIXED && fx != gTzFix);
      gTzMode = md; gTzFix = fx;
      if(chg && !atStart) Print("Broker server clock is "_mq, GmtTxt(SrvGMT(TimeTradeServer())), " now (read from MT5): your times follow it from here on."_mq);
      if(atStart && gTzDet > -90) Print("Broker server clock: "_mq, TzTxt(), " (read from MT5)."_mq);
   }
   else if(gTzDet > -90 && MathAbs(SrvGMT(TimeTradeServer()) - gTzDet) > 0.01 && !gTzWarned)
   {
      gTzWarned = true;
      string m = "The broker's server clock is "_mq + GmtTxt(gTzDet) + ", but 'Broker server clock' gives "_mq + GmtTxt(SrvGMT(TimeTradeServer())) +
                 ": your days, hours, kill zones, news and force-close times are off. Choose 'Auto: read the broker's clock from MT5'."_mq;
      Print(m); Alert(m);
   }
}
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
   int sh = gpKzShift * 60 + extra;
   int ks = (startM + sh + 1440) % 1440, ke = (endM + sh + 1440) % 1440;
   return ks < ke ? (m >= ks && m < ke) : (m >= ks || m < ke);
}
double   ExitR() { return gpExitAt == EXIT_TP1 ? gpTp1R : gpExitAt == EXIT_TP2 ? gpTp2R : gpExitAt == EXIT_TP3 ? gpTp3R : gpTp4R; }

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

void NoteClose(mql_long pid) { gCloseId = pid; gClosedIds[gClosedN % 8] = pid; gClosedN++; }   // a position this EA closes now (fully or partly)
bool ClosedByUs(mql_long pid) { if(pid > 0 && pid == gCloseId) return true; for(int q = 0; q < 8; q++) if(gClosedIds[q] == pid && pid > 0) return true; return false; }
void CloseAll(string why)
{
   ulong tk; double v, op;
   int guard = 0;
   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      gCloseWhy = why; NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
      Print("Closing #"_mq, tk, " ("_mq, DoubleToString(v, 2), " lots): "_mq, why);
      if(!mq_dot(trade).PositionClose(tk)) { Print("Close of #"_mq, tk, " failed: "_mq, mq_dot(trade).ResultRetcodeDescription()); break; }
   }
}

string DateTxt(datetime tm, bool withYear);            // defined below
// a position this EA opened: a deal with its magic number for that position id in the selected history (n deals)
bool OurPosId(mql_long pid, int n)
{
   if(pid <= 0) return false;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk != 0 && HistoryDealGetInteger(tk, DEAL_POSITION_ID) == pid && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && HistoryDealGetString(tk, DEAL_SYMBOL) == _Symbol) return true;
   }
   return false;
}
bool IsExitDeal(ulong tk) { mql_long e = HistoryDealGetInteger(tk, DEAL_ENTRY); return e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY; }
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
   mql_long rs = HistoryDealGetInteger(tk, DEAL_REASON), mg = HistoryDealGetInteger(tk, DEAL_MAGIC), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   if(rs == DEAL_REASON_SL) return "its stop loss"_mq;
   if(rs == DEAL_REASON_TP) return "its take profit"_mq;
   if(rs == DEAL_REASON_SO) return "a margin stop-out"_mq;
   if(rs == DEAL_REASON_EXPERT)
      return mg != InpMagic ? "ANOTHER EA OR SCRIPT (magic "_mq + IntegerToString(mg) + ")"_mq :
             ClosedByUs(pid) ? (gCloseWhy != ""_mq ? "this EA: "_mq + gCloseWhy : "this EA (before a restart)"_mq) : "an EA with this magic number (a second copy of this EA?)"_mq;
   if(rs == DEAL_REASON_CLIENT) return "HAND (MetaTrader on the computer)"_mq;
   if(rs == DEAL_REASON_MOBILE) return "HAND (the phone app)"_mq;
   if(rs == DEAL_REASON_WEB) return "HAND (the web terminal)"_mq;
   return "the broker (reason "_mq + IntegerToString(rs) + ")"_mq;
}
// one line in the log (Experts tab) and the table for every closing deal of this EA's trades: the trade's P&L from all its deals (n = deals)
void CloseReport(ulong tk, int n)
{
   mql_long rs = HistoryDealGetInteger(tk, DEAL_REASON), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   string who = CloseBy(tk);
   double p = 0;
   for(int i = 0; i < n; i++)
   {
      ulong d = HistoryDealGetTicket(i);
      if(d != 0 && HistoryDealGetInteger(d, DEAL_POSITION_ID) == pid && HistoryDealGetString(d, DEAL_SYMBOL) == _Symbol)
         p += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP) + HistoryDealGetDouble(d, DEAL_FEE);
   }
   gLastCloseOut = !(rs == DEAL_REASON_SL || rs == DEAL_REASON_TP || (rs == DEAL_REASON_EXPERT && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && ClosedByUs(pid)));
   gLastClose = (p >= 0 ? "+"_mq : ""_mq) + DoubleToString(p, 2) + " | "_mq + who + " | "_mq + DateTxt(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), false);
   bool still = false;                                  // part of the trade is still open (a partial close)
   for(int q = PositionsTotal() - 1; q >= 0 && !still; q--) { ulong pt = PositionGetTicket(q); if(pt != 0 && PositionGetInteger(POSITION_IDENTIFIER) == pid) still = true; }
   Print("Trade #"_mq, pid, still ? " partly closed: "_mq : " closed: "_mq, DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at "_mq, DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),
         " | trade P&L "_mq, (p >= 0 ? "+"_mq : ""_mq), DoubleToString(p, 2), " (costs included) | closed by "_mq, who);
   if(gLastCloseOut && rs != DEAL_REASON_SO) Print("This trade was closed outside this EA's rules. Its profit is booked, and the loss recovery goes on from it."_mq);
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
   evSalv = false; evTrig = 0;
   datetime t = iTime(_Symbol, _Period, s);
   double o = Op(s), h = Hi(s), l = Lo(s), c = Cl(s);
   mql_long   rv = iVolume(_Symbol, _Period, s);
   mql_long   tv = iTickVolume(_Symbol, _Period, s);
   double w  = rv > 0 ? (double)rv : (tv > 0 ? (double)tv : 1.0);
   double src = gpVwapSrc == PRICE_CLOSE ? c : gpVwapSrc == PRICE_OPEN ? o : gpVwapSrc == PRICE_HIGH ? h : gpVwapSrc == PRICE_LOW ? l :
                gpVwapSrc == PRICE_MEDIAN ? (h + l) / 2.0 : gpVwapSrc == PRICE_WEIGHTED ? (h + l + 2.0 * c) / 4.0 : (h + l + c) / 3.0;
   gLastDone = t;

   // VWAP (reset on the broker's server date change, or week / month) and its standard deviation
   int key = DayKey(t);
   bool newDay = (lastDayKey == -1) || (key != lastDayKey);
   lastDayKey = key;
   gNewDay = newDay;
   MqlDateTime md; TimeToStruct(t, md);
   int aKey = gpVwapAnchor == VW_WEEK ? (int)(((mql_long)t + 3 * 86400) / (7 * 86400)) : gpVwapAnchor == VW_MONTH ? mq_dot(md).year * 12 + mq_dot(md).mon : key;   // weeks start Monday 00:00
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
   if(atrN < gpAtrLen) { atrSum += tr; atrN++; atrV = atrN == gpAtrLen ? atrSum / gpAtrLen : 0; }
   else atrV = (atrV * (gpAtrLen - 1) + tr) / gpAtrLen;
   double atr = atrV;
   bool   haveAtr = atrN >= gpAtrLen;
   bool   warm = bi >= MathMax(MathMax(gpStructLen, gpBrkLen), MathMax(MathMax(gpEntryLen, gpMomLen), MathMax(gpSlopeBars, gpStopLen))) + 1 && haveAtr;

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
   for(int j = 1; j <= gpStructLen; j++) { priorHigh = MathMax(priorHigh, Hi(s + j)); priorLow = MathMin(priorLow, Lo(s + j)); }
   for(int j = 1; j <= gpBrkLen; j++) { sigHigh = MathMax(sigHigh, Hi(s + j)); sigLow = MathMin(sigLow, Lo(s + j)); }
   int eln = (int)MathMin(gpEntryLen, gpStructLen);
   for(int j = 1; j <= eln; j++) { entHigh = MathMax(entHigh, Hi(s + j)); entLow = MathMin(entLow, Lo(s + j)); }
   double swingLow = DBL_MAX, swingHigh = -DBL_MAX;
   for(int j = 0; j < gpStopLen; j++) { swingLow = MathMin(swingLow, Lo(s + j)); swingHigh = MathMax(swingHigh, Hi(s + j)); }
   double rng = h - l, body = MathAbs(c - o), bodyMid = (o + c) / 2.0;
   double momMove = c - Cl(s + gpMomLen);
   double erDen = 0; for(int k = 0; k < gpMomLen; k++) erDen += MathAbs(Cl(s + k) - Cl(s + k + 1));
   bool erUp = gpCmoMin <= 0 || (erDen > 0 && momMove / erDen >= gpCmoMin / 100.0);
   bool erDn = gpCmoMin <= 0 || (erDen > 0 && -momMove / erDen >= gpCmoMin / 100.0);
   bool haveSlope = gpSlopeBars > 0 && vwBars >= gpSlopeBars && nHist > gpSlopeBars;
   double vwSlope = haveSlope ? vwap - vwHist[gpSlopeBars] : 0;
   bool slopeUp = !haveSlope || vwSlope > 0, slopeDn = !haveSlope || vwSlope < 0;
   bool haveSg = gpSlopeBars > 0 && (gpSlopeCross ? nHist > gpSlopeBars : haveSlope);
   double sgSlope = haveSg ? vwap - vwHist[gpSlopeBars] : 0;
   bool sigUp = !haveSg || sgSlope > 0, sigDn = !haveSg || sgSlope < 0;
   bool bigCandle = haveAtr && rng > 0 && rng >= gpDispAtr * atr && body / rng * 100.0 >= gpBodyPct - 1e-7;
   bool bigImp    = haveAtr && rng > 0 && rng >= gpDispAtr * atr && body / rng * 100.0 >= gpImpBody - 1e-7;
   bool closeHi   = rng > 0 && (h - c) / rng * 100.0 <= gpClosePct + 1e-7;
   bool closeLo   = rng > 0 && (c - l) / rng * 100.0 <= gpClosePct + 1e-7;
   bool bullImp   = warm && c > o && h > priorHigh && bigImp && closeHi && slopeUp;
   bool bearImp   = warm && c < o && l < priorLow && bigImp && closeLo && slopeDn;
   bool setupOk   = vwBars >= gpMinOpenBars && !(gpSkipSunday && DowOf(UtcTime(t)) == 0);
   bool bullBase  = warm && gpAllowLong && setupOk && c > o && bigCandle && closeHi && sigUp && (!gpVwapFilter || c > vwap) && (gpMomAtr <= 0 || momMove >= gpMomAtr * atr) && erUp;
   bool bearBase  = warm && gpAllowShort && setupOk && c < o && bigCandle && closeLo && sigDn && (!gpVwapFilter || c < vwap) && (gpMomAtr <= 0 || -momMove >= gpMomAtr * atr) && erDn;
   double momB = c - Cl(s + gpBrkLen);
   double erDenB = 0; for(int k = 0; k < gpBrkLen; k++) erDenB += MathAbs(Cl(s + k) - Cl(s + k + 1));
   bool deepL = warm && gpDeepOn && gpAllowLong && setupOk && c > o && bigCandle && closeHi && sigUp && c > vwap && c > sigHigh && momB >= gpMomAtr * atr && erDenB > 0 && momB / erDenB >= gpCmoMin / 100.0 && priorHigh - c >= gpDeepFar * atr;
   bool deepS = warm && gpDeepOn && gpAllowShort && setupOk && c < o && bigCandle && closeLo && sigDn && c < vwap && c < sigLow && -momB >= gpMomAtr * atr && erDenB > 0 && -momB / erDenB >= gpCmoMin / 100.0 && c - priorLow >= gpDeepFar * atr;

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
   bool halfL = gpHalfStop && bullN == 0 && havePrev && prevNet <= -gpBiasNet;
   bool halfS = gpHalfStop && bearN == 0 && havePrev && prevNet >= gpBiasNet;
   if(gpHalfStrict && havePrev)
   {
      halfL = halfL && (prevNet <= -5 || (prevNet + bullN - bearN <= -1 && bearN >= 1));
      halfS = halfS && (prevNet >= 5 || (prevNet + bullN - bearN >= 1 && bullN >= 1));
   }
   if(gpHalfOpenOut && havePd)
   {
      halfL = halfL || (gpHalfStop && bullN == 0 && sesO < pdL);
      halfS = halfS || (gpHalfStop && bearN == 0 && sesO > pdH);
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
         bool salv = !stopHit && trTrig == 2;           // v4.9: the salvage target (the entry): 0R, not a win
         bool win = !stopHit && !salv;
         double res = win ? exitR : (salv ? 0.0 : (stp == stp0 ? -1.0 : d * (stp - lim) / trRisk));
         if(!trGhost)
         {
            dayRiskR += res;
            lossDirBlk = res < 0 ? (isL ? 1 : -1) : (res > 0 ? 0 : lossDirBlk);
            totR += res; dayR += res;
            if(win) { totW++; dayW++; } else { totL++; dayL++; }
            lastRes = (win ? "TP"_mq + IntegerToString((int)gpExitAt) + " "_mq : (salv ? "SALVAGE "_mq : "STOP "_mq)) + (res >= 0 ? "+"_mq : ""_mq) + DoubleToString(res, 2) + "R"_mq;
            evExit = true; evWin = win; evRes = res; evSalv = salv;
         }
         else { if(win) ghW++; else ghL++; ghR += res; }
         lastExit = bi; st = 0;
      }
      else
      {
         if(tpHit > prevHit)
         {
            double ns = stp;
            if(gpMv1On && tpHit >= 1) ns = isL ? MathMax(ns, lim + gpMv1R * trRisk) : MathMin(ns, lim - gpMv1R * trRisk);
            if(gpMv2On && tpHit >= 2) ns = isL ? MathMax(ns, lim + gpMv2R * trRisk) : MathMin(ns, lim - gpMv2R * trRisk);
            if(gpMv3On && tpHit >= 3) ns = isL ? MathMax(ns, lim + gpMv3R * trRisk) : MathMin(ns, lim - gpMv3R * trRisk);
            if(ns != stp) { stp = ns; evMove = !trGhost; }
            evTp = !trGhost;
         }
         // v4.9 BE / salvage trigger: only the first acts in a trade; both on one bar: the extreme nearer the open came first (from the next bar)
         if(trTrig == 0 && (InpBeOn || InpSvOn))
         {
            double beL = lim + d * InpBeR * trRisk, svL = lim - d * InpSvR * trRisk;
            bool beH = InpBeOn && (isL ? h >= beL - tol : l <= beL + tol);
            bool svH = InpSvOn && (isL ? l <= svL + tol : h >= svL - tol);
            if(beH && svH)
            {
               bool hiFirst = MathAbs(h - o) < MathAbs(o - l);
               if(hiFirst == isL) svH = false; else beH = false;
            }
            if(beH)
            {
               trTrig = 1; evTrig = trGhost ? 0 : 1;
               double nb = isL ? MathMax(stp, lim) : MathMin(stp, lim);
               if(nb != stp) { stp = nb; evMove = !trGhost; }
            }
            else if(svH) { trTrig = 2; evTrig = trGhost ? 0 : 2; tF = lim; evMove = !trGhost; }
         }
      }
   }
   // 2. armed setup: fill (limit touch, or the next bar for market entries) or expiry
   if(MathAbs(st) == 1 && bi > armBar)
   {
      bool isL = st == 1;
      double mt = TickSize();
      bool touched = gpEntryMode == ENTRY_MARKET ? true : (isL ? l <= lim + mt * 0.001 : h >= lim - mt * 0.001);
      if(touched && dayFills < gpMaxFills)
      {
         st = isL ? 2 : -2; fillBar = bi; lastFill = bi; lastDir = isL ? 1 : -1; tpHit = 0; trTrig = 0; dayFills++;
         bestPx = lim;
         if(!trGhost) { evFill = true; evFillL = isL; }
         if(isL ? l <= stp + mt * 0.001 : h >= stp - mt * 0.001)
         {
            if(!trGhost)
            {
               dayRiskR += gpFillBarStopR ? -1.0 : 0.0;
               lossDirBlk = isL ? 1 : -1;
               totR += -1.0; dayR += -1.0; totL++; dayL++;
               lastRes = "STOP -1.00R"_mq;
               evExit = true; evWin = false; evRes = -1.0;
            }
            else { ghL++; ghR += -1.0; }
            lastExit = bi; st = 0;
         }
      }
      else if(bi - armBar >= gpRetestBars)
      {
         st = 0;
         if(!trGhost) evCancel = 1;
      }
   }
   // 3. arm a new setup on the closed displacement candle
   bool cooled = lastExit < 0 || bi - lastExit >= MathMax(gpCooldown, 1);
   bool dayOpen = gpDayStopR <= 0 || dayRiskR > -gpDayStopR;
   mql_long legN = lastFill < 0 ? 0 : bi - lastFill;
   bool legOn = gpLegReset && MathAbs(st) != 2 && legN > 0 && legN < gpStructLen;
   double brkHigh = sigHigh, brkLow = sigLow;
   if(legOn)
   {
      double lh = Hi(s + 1), ll = Lo(s + 1);
      for(int j = 1; j <= legN; j++) { lh = MathMax(lh, Hi(s + j)); ll = MathMin(ll, Lo(s + j)); }
      if(lastDir == 1) brkHigh = lh; else brkLow = ll;
   }
   bool bullDisp = (bullBase && c > brkHigh) || deepL;
   bool bearDisp = (bearBase && c < brkLow) || deepS;
   if(gpLossBlock && lossDirBlk == 1) bullDisp = false;
   if(gpLossBlock && lossDirBlk == -1) bearDisp = false;
   datetime ut = UserTime(t);
   int dw = DowOf(ut);
   gDayOk = !gpDayOn || (dw == 1 && InpMon) || (dw == 2 && InpTue) || (dw == 3 && InpWed) || (dw == 4 && InpThu) || (dw == 5 && InpFri) || (dw == 6 && InpSat) || (dw == 0 && InpSun);
   int cur = gpHrIst ? MinOfDay(UtcTime(t) + 19800) : MinOfDay(ut), a0 = gpStartH * 60 + gpStartM, b0 = gpEndH * 60 + gpEndM;   // v4.8: a preset's hours are IST
   gHourOk = !gpHoursOn || (a0 < b0 ? (cur >= a0 && cur < b0) : (cur >= a0 || cur < b0));
   datetime utcT = UtcTime(t);
   int kzM = MinOfDay(utcT + 19800);   // Indian Standard Time = UTC + 5:30
   // the times are the summer times: London / London close move 1 hour later in London winter time, New York in New York winter time
   int lonSh = gpKzAuto && !UkSummer(utcT) ? 60 : 0, nySh = gpKzAuto && !NySummer(utcT) ? 60 : 0;
   gKzOk = !gpKzOn || (gpKzAsia && InKz(kzM, 330, 570, 0)) || (gpKzLon && InKz(kzM, 690, 870, lonSh)) || (gpKzNy && InKz(kzM, 990, 1170, nySh)) || (gpKzLc && InKz(kzM, 1170, 1290, lonSh));
   bool canArm = gpTfOk && gDayOk && gHourOk && gKzOk && MathAbs(st) != 2 && cooled && dayFills < gpMaxFills && dayOpen && atr > 0;
   bool keepArm = gpRearm == REARM_KEEP && ((st == 1 && bullDisp) || (st == -1 && bearDisp));
   if(canArm && (bullDisp || bearDisp) && !keepArm)
   {
      bool isL = bullDisp; double d = isL ? 1 : -1;
      double entry = gpEntryMode == ENTRY_MODEL ? (isL ? MathMax(bodyMid, entHigh) : MathMin(bodyMid, entLow)) : gpEntryMode == ENTRY_PCT ? c - d * gpEntryPct / 100.0 * rng : c;
      bool half = gpStopMode == STOP_ATR && (isL ? halfL : halfS);
      double cStop = entry - d * gpStopAtr * atr;
      double hStop = isL ? MathMin(entry - gpHalfStopAtr * atr, l) : MathMax(entry + gpHalfStopAtr * atr, h);
      if(gpHalfCap) hStop = isL ? MathMax(hStop, cStop) : MathMin(hStop, cStop);
      double sStop = isL ? swingLow - gpStopBufAtr * atr : swingHigh + gpStopBufAtr * atr;
      double stop  = gpStopMode == STOP_ATR ? (half ? hStop : cStop) : (isL ? MathMax(sStop, cStop) : MathMin(sStop, cStop));
      double risk = d * (entry - stop);
      if(risk >= TickSize() && RoundTick(stop) != RoundTick(entry))
      {
         bool haveZ = gpNoChase && vwSd > 0 && vwBars >= 3 && sessN >= 1;
         bool zNo = haveZ && d * (c - vwap) / vwSd > gpNoChaseSig;
         // choppy session (VWAP crosses) / over-extended 1h EMA20; a skipped setup runs on invisibly like the no-chase one
         bool chopNo = gpChopOn && vxRate > gpChopMax;
         bool emaNo = gpEmaOn && haveSpd && emaSpd > gpEmaMax;
         // signal close still hugging the VWAP (less than the minimum distance in ATR on the trade's side)
         bool nearNo = gpMinVwOn && d * (c - vwap) < gpMinVwAtr * atr;
         bool farNo = gpMaxVwOn && MathAbs(c - vwap) > (gpMaxVwUnit == VWU_PRICE ? gpMaxVwDist : gpMaxVwDist * atr);   // above or below
         // signal still on the VWAP: the stop on the other side of it, the VWAP touched in the last N candles, the entry too close to it
         bool stopNo = gpStopVwOn && d * (stop - vwap) < gpStopVwBuf * atr;
         bool tchNo = gpTouchVwOn && (isL ? tchL : tchS) < gpTouchVwN;
         bool entNo = gpEntVwOn && d * (entry - vwap) < gpEntVwAtr * atr;
         bool ghost = zNo || chopNo || emaNo || nearNo || farNo || stopNo || tchNo || entNo;
         if(MathAbs(st) == 1 && !trGhost) evCancel = 2;
         st = isL ? 1 : -1; armBar = bi; lim = entry; stp = stop; stp0 = stop; trRisk = risk; trHalf = half; trGhost = ghost;
         trSkip = zNo ? 1 : (chopNo ? 2 : (emaNo ? 3 : (nearNo ? 4 : (farNo ? 5 : (stopNo ? 6 : (tchNo ? 7 : (entNo ? 8 : 0)))))));
         t1 = lim + d * gpTp1R * risk; t2 = lim + d * gpTp2R * risk; t3 = lim + d * gpTp3R * risk; t4 = lim + d * gpTp4R * risk;
         tF = gpExitAt == EXIT_TP1 ? t1 : gpExitAt == EXIT_TP2 ? t2 : gpExitAt == EXIT_TP3 ? t3 : t4;
         if(!ghost) { evArm = true; evArmL = isL; }
      }
   }

   // accuracy of the shown trades (shared Pine STATS block): a target counts when the best price after the fill reached it
   // before the stop; the final target is reached exactly when the trade is a win
   if(evExit)
   {
      double sd = lastDir == 1 ? 1.0 : -1.0;
      int    xk = (int)gpExitAt;
      for(int k = 1; k <= 4; k++)
      {
         double lvl = k == 1 ? t1 : (k == 2 ? t2 : (k == 3 ? t3 : t4));
         if(evWin ? k <= xk : (k < xk && sd * (bestPx - lvl) >= -TickSize() * 0.001)) tpHitN[k - 1]++;
      }
      if(evSalv) svN++;
      else if(!evWin && stp != stp0) { if(evRes == 0.0) beN++; else if(evRes > 0.0) lkN++; }
   }
   if(gFirstT == 0) gFirstT = t;
   DrawBar(t);
}

//--- v4.5: Crooks C and the rules built on it (E - J): everything of Crooks C applies to them
bool   CrkCFam()  { return InpRec == REC_CRC || (InpRec >= REC_CRE && InpRec <= REC_CRL); }   // v5.0: + K, L
//--- Crooks C rule after N losing recovery trades in a row (Crooks C and E - J)
bool   CrkPrOn()  { return CrkCFam() && InpCrkPr != CPR_OFF; }
double CrkPrPct() { return CrkPrOn() && InpCrkPr == CPR_PCT ? MathMax(10.0, MathMin(100.0, InpCrkPrPct)) / 100.0 : 1.0; }
bool   CrkPause() { return CrkPrOn() && InpCrkPr == CPR_SKIP && crkSkip; }   // the skip rule pauses trading
bool   CrkHedgeNow() { return CrkPrOn() && InpCrkPr == CPR_HEDGE && crkHg && crkL > 0; }   // hedge rule: this signal opens the pair
//--- Crooks: the next trade is a recovery trade. A / B: trades 3, 5, 7 ... of the cycle; C: the trade after a win while a loss is owed; D: trades 3, 6, 9 ...
bool CrkRecNext()
{
   if(InpRec == REC_CRA || InpRec == REC_CRB) return crkN >= 2 && crkN % 2 == 0;
   if(CrkCFam()) return (crkW && crkL > 0 && !(CrkPrOn() && InpCrkPr == CPR_WAIT && (crkWait || crkNeedL))) || CrkHedgeNow();   // wait rule: not while waiting; the hedge pair is sized as a recovery trade
   if(InpRec == REC_CRD) return crkN >= 2 && (crkN - 2) % 3 == 0;
   return false;
}
//--- v4.6 PROFIT LADDER (Crooks F - J): once the highest closed profit has reached InpLadT, the trades grow with the profit above a lock and the
//--- extra risk is paid from that profit only; back at the start (closed profit 0 or less) every trade is the 0.01 lot until it is in profit again
bool   LadFam()   { return (InpRec >= REC_CRF && InpRec <= REC_CRJ) || InpRec == REC_CRK; }   // v5.0: + K
bool   LadOn()    { return InpLadder != LAD_OFF && LadFam() && InpLadT > 0 && crkPk >= InpLadT; }
bool   LadGuard() { return LadOn() && InpRec != REC_CRK && totalNet - gNet0 <= 0; }   // v5.0: Crooks K has its own zone below the start instead
//--- the level: lock (share of the best profit kept out of the extra risk), share of the cushion added to the base, most base (x), most extra loss
void   LadPar(double &lam, double &phi, double &bmax, double &gam)
{
   lam = 0.8; phi = 0.10; bmax = 2.0; gam = 0.25;
   if(InpLadder == LAD_MED)   { lam = 0.7; phi = 0.15; bmax = 3.0;  gam = 0.30; }
   if(InpLadder == LAD_HIGH)  { lam = 0.6; phi = 0.20; bmax = 5.0;  gam = 0.35; }
   if(InpLadder == LAD_XHIGH) { lam = 0.5; phi = 0.25; bmax = 8.0;  gam = 0.40; }
   if(InpLadder == LAD_MAX)   { lam = 0.4; phi = 0.30; bmax = 12.0; gam = 0.50; }
}
//--- the ladder's base (the plain base while it is off) and the cushion (the closed profit above the lock)
double LadBase(double base, double &cush)
{
   cush = 0;
   if(!LadOn()) return base;
   double lam = 0, phi = 0, bmax = 0, gam = 0; LadPar(lam, phi, bmax, gam);
   cush = MathMax(0.0, totalNet - gNet0 - lam * crkPk);
   return base + MathMin((bmax - 1.0) * base, phi * cush);
}
//--- v4.7 position size: the base trade's $ risk on a setup with this stop distance: Fixed $ risk, the Fixed lots' stop-out loss (spread and
//--- commission included, like LotsFor), or % of the equity. 0 = no base (no equity, no tick value): the setup gets size 0
double BaseRisk(double stopDist)
{
   if(InpSizeMode == PSZ_PCT) return MathMax(0.0, AccountInfoDouble(ACCOUNT_EQUITY)) * InpEqPct / 100.0;
   if(InpSizeMode == PSZ_LOT)
   {
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
      if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
      return InpBaseLots * ((stopDist + MathMax(CostSpr(), 0)) / ts * tv + InpCommLot);
   }
   return InpBaseRisk;
}
//--- the base of the EA's trade for its booking (Fixed $ risk: the input, as in v4.6)
//--- v5.0 SIZE BY: with Profit the base and the amounts a recovery rule adds are the win at the final TP (the risk = amount / its R)
bool   SizeProfit() { return InpSizeBy == SZB_PROFIT; }
//--- v5.1 Size by Profit: what a final-TP win brings per $ of stop-out loss on this setup, costs included (with earn-back the target is
//--- pushed by the costs, so a win nets the R x the stop distance); no tick value / stop distance, or a target inside the costs: the R alone
double PDiv(double exitR)
{
   if(exitR <= 0) return 1.0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0 || trRisk <= 0) return exitR;
   double spr = MathMax(CostSpr(), 0), loss = (trRisk + spr) / ts * tv + InpCommLot;
   double win = exitR * trRisk / ts * tv;
   if(!InpEarnBack) win -= spr / ts * tv + InpCommLot;
   return (loss > 0 && win > 0) ? win / loss : exitR;
}
double BookBase() { return InpSizeMode == PSZ_USD && !SizeProfit() ? InpBaseRisk : (exBase > 0 ? exBase : SizeProfit() && InpSizeMode != PSZ_LOT && ExitR() > 0 ? InpBaseRisk / ExitR() : InpBaseRisk); }
//--- the base shown in the table (Fixed lots: on the last setup's stop)
double ShowBase() { double b = InpSizeMode == PSZ_USD ? InpBaseRisk : BaseRisk(trRisk); return SizeProfit() && InpSizeMode != PSZ_LOT && ExitR() > 0 ? b / PDiv(ExitR()) : b; }
string BaseTxt(double &cush)
{
   cush = 0;
   if(InpSizeMode == PSZ_LOT && !LadOn()) return "base "_mq + DoubleToString(InpBaseLots, 2) + " lot"_mq;
   double b = LadBase(ShowBase(), cush);
   string pct = InpSizeMode == PSZ_PCT ? " ("_mq + DoubleToString(InpEqPct, 2) + "% of equity"_mq + (SizeProfit() ? " as the win"_mq : ""_mq) + ")"_mq : ""_mq;
   if(SizeProfit() && InpSizeMode != PSZ_LOT) return "base risk "_mq + DoubleToString(b, 2) + " = win "_mq + DoubleToString(b * PDiv(ExitR()), 2) + " at TP"_mq + IntegerToString((int)gpExitAt) + pct;   // v5.0
   return "base "_mq + DoubleToString(b, 2) + pct;
}
string LadTxt()
{
   string lv = InpLadder == LAD_LOW ? "Low"_mq : InpLadder == LAD_MED ? "Medium"_mq : InpLadder == LAD_HIGH ? "High"_mq : InpLadder == LAD_XHIGH ? "Extra high"_mq : "Max"_mq;
   if(!LadFam()) return lv + " | only with Crooks F, G, H, I, J or K"_mq;
   if(!LadOn()) return lv + " | best profit "_mq + DoubleToString(MathMax(0.0, crkPk), 2) + " of "_mq + DoubleToString(InpLadT, 0) + " to start"_mq;
   if(LadGuard()) return lv + " | back at the start: 0.01 lot until in profit"_mq;
   double cush = 0, lam = 0, phi = 0, bmax = 0, gam = 0;
   double b = LadBase(ShowBase(), cush); LadPar(lam, phi, bmax, gam);
   return lv + " | lock "_mq + DoubleToString(lam * crkPk, 2) + " | cushion "_mq + DoubleToString(cush, 2) + " | base "_mq + DoubleToString(b, 2);
}
//--- v5.0 Crooks K: below the start (the closed profit since the restart is under 0): after a win the careful size, after a loss the E / I lot
bool   KZone() { return InpRec == REC_CRK && totalNet - gNet0 < 0; }
double KCare(double base, double dv, double kRisk)
{
   if(InpCrkKMode == CKM_USD) return SizeProfit() && dv > 0 ? InpCrkKUsd / dv : InpCrkKUsd;   // v5.1: dv = PDiv (Risk: 1)
   if(InpCrkKMode == CKM_PCT) return base * InpCrkKPct / 100.0;
   return kRisk > 0 ? kRisk : base;                     // the careful lots' stop-out loss on this setup (0 = not known: the base)
}
//--- v5.0 Crooks L: at a new best (the closed profit since the restart at its high; also at the start) the base grows with the profit
double LBase(double base, double dv)
{
   double nr = totalNet - gNet0;
   if(InpRec != REC_CRL || nr < crkPk) return base;
   double g = InpCrkLGrow / 100.0 * nr / (SizeProfit() && dv > 0 ? dv : 1.0);   // v5.1: dv = PDiv (Risk: 1)
   return base + MathMin((MathMax(1.0, InpCrkLGrowX) - 1.0) * base, MathMax(0.0, g));
}
//--- v5.0 Crooks L: the parts of a loss just booked, from the drawdown after it (below the start: from the start; above it: from the best)
int LParts()
{
   double b = BookBase(), nr = totalNet - gNet0, dd = 0, step = 0; int mx = 1;
   if(nr < 0) { dd = -nr; step = InpCrkLZ1 * b; mx = InpCrkLZ1N > 1 ? InpCrkLZ1N : 1; }
   else if(nr < crkPk) { dd = crkPk - nr; step = InpCrkLZ2 * b; mx = InpCrkLZ2N > 1 ? InpCrkLZ2N : 1; }
   else return 1;
   if(step <= 0) return 1;
   double np = MathCeil(dd / step - 1e-9);
   if(np > mx) np = mx;
   if(np < 1) np = 1;
   return (int)np;
}

//--- Crooks TP1 rule (exit at TP1, or any exit with InpCrkT1Any; recovery trades): the part p closed at TP1 banks the recovery amount, the rest runs to TP2.
//--- The size is the one whose stop-out at distance d loses exactly that amount: d = p x TP1 - (1 + p) x costs (p = 0.5: TP1 / 2 - 1.5 x costs),
//--- on the tick grid toward the entry (bid chart); 0 = not possible
double CrkT1P() { return MathMax(10.0, MathMin(90.0, InpCrkT1Pct)) / 100.0; }
double CrkT1Dist()
{
   if(!InpCrkT1 || (gpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext() || CrkHedgeNow() || LadGuard() || KZone()) return 0;   // v4.6: not while the ladder's guard is on (v5.0: nor in the Crooks K zone)
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0) return 0;
   double spr = CostSpr(), p = CrkT1P();
   double d = MathFloor((p * gpTp1R * trRisk - (1.0 + p) * (spr + InpCommLot * ts / tv)) / ts + 1e-9) * ts;
   return d >= ts ? d : 0;
}

//--- Crooks C over N wins: N, and the parts of the loss still to win back
int CrkNp() { return InpRec == REC_CRL ? 1 : InpCrkCnOn ? MathMax(1, InpCrkCn) : 1; }   // v5.0: Crooks L takes its parts from the drawdown
int CrkParts()
{
   if(InpRec == REC_CRL) { int mx = InpCrkLZ1N > InpCrkLZ2N ? InpCrkLZ1N : InpCrkLZ2N; if(mx < 1) mx = 1; return crkP < 1 ? 1 : crkP > mx ? mx : crkP; }
   int np = CrkNp(); return (crkP < 1 || crkP > np) ? np : crkP;
}
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
   CrkDayCount(InpCrkPrAll || (gpDayOn ? gDayOk : (dw >= 1 && dw <= 5)));
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

//--- v4.8: the values the EA uses: the inputs (Custom) or the preset's tested values (written by build/patch_ea_v48.py from presets/preset_data.py)
void PresetApply()
{
   int  pi = (int)InpPreset;
   bool pc = pi == 0;
   gpStructLen = pc ? InpStructLen : ((pi == 19 || pi == 21 || pi == 23 || pi == 24) ? 20 : 10);
   gpBrkLen = pc ? InpBrkLen : ((pi == 15) ? 8 : 6);
   gpEntryLen = pc ? InpEntryLen : ((pi == 17) ? 8 : 6);
   gpRetestBars = pc ? InpRetestBars : (5);
   gpDispAtr = pc ? InpDispAtr : ((pi == 3) ? 0.4 : (pi == 18) ? 0.65 : (pi == 21 || pi == 23) ? 0.5 : 0.8);
   gpBodyPct = pc ? InpBodyPct : ((pi == 20) ? 60.0 : (pi == 23) ? 45.0 : 55.0);
   gpClosePct = pc ? InpClosePct : (25.0);
   gpMomLen = pc ? InpMomLen : ((pi == 7 || pi == 18 || pi == 21) ? 5 : 10);
   gpMomAtr = pc ? InpMomAtr : (0.85);
   gpCmoMin = pc ? InpCmoMin : ((pi == 10) ? 30.0 : 20.0);
   gpRearm = pc ? InpRearm : (ENUM_REARM)(REARM_KEEP);
   gpStopMode = pc ? InpStopMode : (ENUM_STOP_MODE)(STOP_ATR);
   gpStopAtr = pc ? InpStopAtr : ((pi == 5 || pi == 6 || pi == 7 || pi == 18) ? 2.4 : (pi == 8 || pi == 25) ? 1.8 : (pi == 19 || pi == 20 || pi == 21 || pi == 22 || pi == 23 || pi == 24) ? 2.2 : 4.0);
   gpStopLen = pc ? InpStopLen : (6);
   gpStopBufAtr = pc ? InpStopBufAtr : (0.22);
   gpHalfStop = pc ? InpHalfStop : (true);
   gpHalfStopAtr = pc ? InpHalfStopAtr : ((pi == 9 || pi == 10 || pi == 11 || pi == 12 || pi == 13 || pi == 14 || pi == 15 || pi == 17) ? 1.2 : 0.9);
   gpBiasNet = pc ? InpBiasNet : (3);
   gpImpBody = pc ? InpImpBody : (50.0);
   gpHalfOpenOut = pc ? InpHalfOpenOut : (true);
   gpHalfStrict = pc ? InpHalfStrict : (false);
   gpHalfCap = pc ? InpHalfCap : (false);
   gpCooldown = pc ? InpCooldown : ((pi == 1) ? 8 : (pi == 2) ? 30 : (pi == 18) ? 12 : 1);
   gpMaxFills = pc ? InpMaxFills : ((pi == 19 || pi == 22) ? 1 : 5);
   gpDayStopR = pc ? InpDayStopR : (0.0);
   gpFillBarStopR = pc ? InpFillBarStopR : (false);
   gpLegReset = pc ? InpLegReset : (true);
   gpAtrLen = pc ? InpAtrLen : (14);
   gpVwapFilter = pc ? InpVwapFilter : (true);
   gpSlopeBars = pc ? InpSlopeBars : ((pi == 11) ? 0 : 3);
   gpSlopeCross = pc ? InpSlopeCross : (true);
   gpMinOpenBars = pc ? InpMinOpenBars : (0);
   gpSkipSunday = pc ? InpSkipSunday : ((pi == 24) ? false : true);
   gpDeepOn = pc ? InpDeepOn : (false);
   gpDeepFar = pc ? InpDeepFar : (2.0);
   gpAllowLong = pc ? InpAllowLong : (true);
   gpAllowShort = pc ? InpAllowShort : (true);
   gpVwapAnchor = pc ? InpVwapAnchor : (ENUM_VW_ANCHOR)((pi == 9 || pi == 10 || pi == 11 || pi == 12 || pi == 13 || pi == 14 || pi == 15 || pi == 16 || pi == 17 || pi == 18 || pi == 20) ? VW_SESSION : VW_MONTH);
   gpVwapSrc = pc ? InpVwapSrc : (ENUM_APPLIED_PRICE)(PRICE_TYPICAL);
   gpEntryMode = pc ? InpEntryMode : (ENUM_ENTRY_MODE)((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? ENTRY_MARKET : ENTRY_MODEL);
   gpEntryPct = pc ? InpEntryPct : (50.0);
   gpTp1R = pc ? InpTp1R : ((pi == 13) ? 0.5 : 0.6);
   gpTp2R = pc ? InpTp2R : (1.0);
   gpTp3R = pc ? InpTp3R : (1.5);
   gpTp4R = pc ? InpTp4R : ((pi == 5) ? 2.5 : (pi == 23) ? 3.0 : 2.0);
   gpExitAt = pc ? InpExitAt : (ENUM_EXIT_AT)(EXIT_TP4);
   gpMv1On = pc ? InpMv1On : (false);
   gpMv1R = pc ? InpMv1R : (0.0);
   gpMv2On = pc ? InpMv2On : ((pi == 6 || pi == 14) ? true : false);
   gpMv2R = pc ? InpMv2R : (0.6);
   gpMv3On = pc ? InpMv3On : ((pi == 9 || pi == 10 || pi == 11 || pi == 12 || pi == 13 || pi == 14 || pi == 15 || pi == 17) ? true : false);
   gpMv3R = pc ? InpMv3R : (1.0);
   gpNoChase = pc ? InpNoChase : ((pi == 18 || pi == 19 || pi == 20 || pi == 21 || pi == 22 || pi == 24 || pi == 25) ? true : false);
   gpNoChaseSig = pc ? InpNoChaseSig : ((pi == 18 || pi == 20) ? 2.0 : (pi == 19 || pi == 21 || pi == 22 || pi == 24) ? 1.25 : (pi == 25) ? 2.2 : 2.4);
   gpLossBlock = pc ? InpLossBlock : (false);
   gpMinVwOn = pc ? InpMinVwOn : (false);
   gpMinVwAtr = pc ? InpMinVwAtr : (1.0);
   gpMaxVwOn = pc ? InpMaxVwOn : (false);
   gpMaxVwDist = pc ? InpMaxVwDist : (5.0);
   gpMaxVwUnit = pc ? InpMaxVwUnit : (ENUM_VW_UNIT)(VWU_ATR);
   gpStopVwOn = pc ? InpStopVwOn : (false);
   gpStopVwBuf = pc ? InpStopVwBuf : (0.0);
   gpTouchVwOn = pc ? InpTouchVwOn : (false);
   gpTouchVwN = pc ? InpTouchVwN : (3);
   gpEntVwOn = pc ? InpEntVwOn : (false);
   gpEntVwAtr = pc ? InpEntVwAtr : (0.75);
   gpChopOn = pc ? InpChopOn : ((pi == 5 || pi == 6 || pi == 7 || pi == 8 || pi == 12) ? true : false);
   gpChopMax = pc ? InpChopMax : ((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? 8.0 : (pi == 12) ? 16.0 : 12.0);
   gpEmaOn = pc ? InpEmaOn : ((pi == 8 || pi == 10 || pi == 11 || pi == 17) ? true : false);
   gpEmaMax = pc ? InpEmaMax : ((pi == 8) ? 1.4 : (pi == 10 || pi == 11 || pi == 17) ? 1.2 : 1.65);
   // time filters: your days and news windows only for Custom or with Add my filters; the preset's own hours / kill zone unless your hours or kill zones replace them
   bool myF = pc || InpAddMine;
   bool ownS = !pc && !(InpAddMine && (InpHoursOn || InpKzOn));
   gpDayOn = myF && InpDayOn;
   gpHoursOn = ownS ? ((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? true : false) : InpHoursOn;
   gpStartH = ownS ? ((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? 18 : 0) : InpStartH;
   gpStartM = ownS ? ((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? 30 : 0) : InpStartM;
   gpEndH = ownS ? ((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? 22 : 0) : InpEndH;
   gpEndM = ownS ? ((pi == 5 || pi == 6 || pi == 7 || pi == 8) ? 30 : 0) : InpEndM;
   gpHrIst = ownS;
   gpKzOn = ownS ? ((pi == 1 || pi == 2 || pi == 3 || pi == 4 || pi == 17) ? true : false) : InpKzOn;
   gpKzAsia = ownS ? ((pi == 17) ? true : false) : InpKzAsia;
   gpKzLon = ownS ? (false) : InpKzLon;
   gpKzNy = ownS ? (false) : InpKzNy;
   gpKzLc = ownS ? ((pi == 1 || pi == 2 || pi == 3 || pi == 4) ? true : false) : InpKzLc;
   gpKzAuto = ownS ? (false) : InpKzAuto;
   gpKzShift = ownS ? (0) : (int)InpKzShift;
   gpDNewsOn = myF && InpDNewsOn;
   gpN1On = myF && InpN1On;
   gpN2On = myF && InpN2On;
   gpN3On = myF && InpN3On;
   gpN4On = myF && InpN4On;
   gpN5On = myF && InpN5On;
   gpP1 = pc ? InpP1 : (pi == 10 || pi == 12 || pi == 13 || pi == 19 || pi == 21 || pi == 22) ? 70.0 : 0.0;
   gpP2 = pc ? InpP2 : 0.0;
   gpP3 = pc ? InpP3 : 0.0;
   gpTf = pc ? 0 : ((pi == 1 || pi == 2 || pi == 3 || pi == 4) ? (int)PERIOD_M1 : (pi == 5 || pi == 6 || pi == 7 || pi == 8) ? (int)PERIOD_M5 : (pi == 18 || pi == 19 || pi == 20 || pi == 21 || pi == 22 || pi == 23 || pi == 24 || pi == 25) ? (int)PERIOD_H1 : (int)PERIOD_M15);
   gpTfOk = pc || (int)_Period == gpTf;
}
string PresetName()
{
   switch(InpPreset)
   {
      case PRE_M1_S1: return "M1-S1"_mq;
      case PRE_M1_S2: return "M1-S2"_mq;
      case PRE_M1_S3: return "M1-S3"_mq;
      case PRE_M1_S4: return "M1-S4"_mq;
      case PRE_M5_S1: return "M5-S1"_mq;
      case PRE_M5_S2: return "M5-S2"_mq;
      case PRE_M5_S3: return "M5-S3"_mq;
      case PRE_M5_S4: return "M5-S4"_mq;
      case PRE_M15_S1: return "M15-S1"_mq;
      case PRE_M15_S2: return "M15-S2"_mq;
      case PRE_M15_S3: return "M15-S3"_mq;
      case PRE_M15_S4: return "M15-S4"_mq;
      case PRE_M15_S5: return "M15-S5"_mq;
      case PRE_M15_S6: return "M15-S6"_mq;
      case PRE_M15_S7: return "M15-S7"_mq;
      case PRE_M15_S8: return "M15-S8"_mq;
      case PRE_M15_S9: return "M15-S9"_mq;
      case PRE_H1_S1: return "H1-S1"_mq;
      case PRE_H1_S2: return "H1-S2"_mq;
      case PRE_H1_S3: return "H1-S3"_mq;
      case PRE_H1_S4: return "H1-S4"_mq;
      case PRE_H1_S5: return "H1-S5"_mq;
      case PRE_H1_S6: return "H1-S6"_mq;
      case PRE_H1_S7: return "H1-S7"_mq;
      case PRE_H1_S8: return "H1-S8"_mq;
      default: break;
   }
   return "Custom"_mq;
}

//--- monthly profit lock (calendar month in your time zone; closed deals, costs included) and the monthly restart of the loss recovery
void RecoveryRestart()                                // like the hard cap's Start again: the loss recovery starts again from the base risk
{
   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
   crkSkip = false; crkSkipLeft = 0;
}
void MonthRestart()                                   // v4.8: the monthly restart: the loss recovery, the profit ladder / Crooks J / Rule C split count from here, a hard-cap stop ends
{
   RecoveryRestart(); gNet0 = totalNet; crkPk = 0; capStop = false;
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
      if(tk == 0 || !DealIsMine(tk, n)) continue;      // v4.4: also an exit by hand, from the phone app or by another EA
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
//--- v4.5 Crooks F / H / I / J: the most a recovery trade may risk (F / H / I: its real stop-out loss, a TP1-rule trade's wider stop included)
double CrkRecLimit(double r, double base)
{
   double mul = CrkT1Mult();
   if(InpRec == REC_CRF || InpRec == REC_CRI) r = MathMin(r, MathMax(1.0, InpCrkFK) * base / mul);
   else if(InpRec == REC_CRH) r = MathMin(r, MathMax(base, AccountInfoDouble(ACCOUNT_EQUITY) * InpCrkHPct / 100.0) / mul);
   else if((InpRec == REC_CRJ || InpRec == REC_CRK) && InpCrkJX > 0) r = MathMax(base, r * MathMax(0.0, 1.0 - MathMax(0.0, crkPk - (totalNet - gNet0)) / (InpCrkJX * base)));   // v5.0: K too
   return r;
}
//--- the risk of a Crooks rule's next trade at this base (v4.6: also at the profit ladder's base)
double CrkRule(double base, double exitR, double minRisk)
{
   double x = crkL / (InpRec == REC_CRB ? InpCSplit : CrkCFam() ? CrkParts() : 1) * (CrkCFam() ? CrkPrPct() : 1.0);   // % rule: a part of the loss
   bool rn = CrkRecNext();
   double r = !rn ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
   if(rn) r = CrkRecLimit(r, base);                                  // v4.5 Crooks F / H / I / J
   else if(crkL > 0 && (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL) && minRisk > 0) r = MathMin(base, minRisk);   // v4.5 Crooks E / I (v5.0: L): the small lot while waiting
   return r;
}
//--- the $ risk of the next trade; minRisk: the stop-out loss of the 0.01 lot (Crooks E / I lot) on this setup (0 = not known: the base is used);
//--- kRisk: the stop-out loss of the Crooks K careful lots on this setup (0 = not known: the base)
double NextRisk(double exitR, bool canTake = true, double minRisk = 0, double kRisk = 0)
{
   double base = BaseRisk(trRisk);                    // v4.7: the base of this setup (Position size)
   double dv = SizeProfit() ? PDiv(exitR) : 1.0;      // v5.1: Profit: a final-TP win per $ of stop-out loss here, costs included (Risk: 1)
   double xr = SizeProfit() ? dv : exitR;             //   Exact and the Crooks recovery divide by it (Risk: the final TP's R)
   if(SizeProfit() && InpSizeMode != PSZ_LOT && dv > 0) base = base / dv;   // v5.0: the base is the win at the final TP (v5.1: with costs)
   double r = base;
   gBase = base; gBaseWin = SizeProfit() ? base * dv : base;
   if(base <= 0) return 0;                            // no base: size 0 (never a zero divide below)
   double stepBase = 0;
   double netR = totalNet - gNet0;                    // v4.8: the closed profit since the monthly restart
   if(netR >= 1000) { int kk = (int)MathFloor((netR - 1000) / 500); stepBase = (1000.0 + 500.0 * kk) / (8 + kk); }
   else if(netR >= 500) stepBase = 100.0;
   else if(netR >= 200) stepBase = 200.0 / 3.0;
   stepBase = stepBase / dv;                          // v5.0: a base amount
   double baseC = InpRec == REC_CS ? MathMax(base, InpCapOn ? MathMin(stepBase, InpHardCap) : stepBase) : base;
   double fa = 1, fb = 1;
   for(int k = 2; k <= recLosses; k++) { double fc = fa + fb; fa = fb; fb = fc; }
   double oscGoal = SizeProfit() ? base * dv : base;   // v5.0: with Profit the cycle goal is one base win
   int oscNeed = xr > 0 ? (int)MathMax(1, MathMin(1e9, MathCeil((oscGoal - oscP) / (base * xr)))) : 1;   // v4.7: no int overflow
   switch(InpRec)
   {
      case REC_ALL:   r = base + recPool / dv; break;
      case REC_SPLIT: r = base + recPool / InpRecN / dv; break;
      case REC_PART:  r = base + recPool * InpRecPct / 100.0 / dv; break;
      case REC_MART:  r = base * MathPow(InpRecMult, recLosses); break;
      case REC_EXACT: r = base + recPool / xr; break;
      case REC_STEP:  r = base + InpRecStep * recLosses / dv; break;
      case REC_FIB:   r = base * (recLosses == 0 ? 1.0 : fb); break;
      case REC_DALE:  r = base * dUnits; break;
      case REC_C:
      case REC_CS:    r = MathMax(baseC, carried / InpCSplit / dv); break;
      case REC_LAB:   r = base * LabUnits(); break;
      case REC_GMART: r = base * MathPow(InpRecMult, recLosses) + base * recLosses; break;
      case REC_PAR:   r = base * MathPow(2, parWins); break;
      case REC_RDALE: r = base * rdUnits; break;
      case REC_DELAY: r = recLosses >= InpDelayN ? base + recPool / InpRecN / dv : base; break;
      case REC_EQPCT: r = AccountInfoDouble(ACCOUNT_EQUITY) * InpEqPct / 100.0 / dv; break;
      case REC_OSC:   r = base * MathMin(oscU, oscNeed); break;
      case REC_CRA:
      case REC_CRB:
      case REC_CRC:
      case REC_CRD:
      case REC_CRE:
      case REC_CRF:
      case REC_CRG:
      case REC_CRH:
      case REC_CRI:
      case REC_CRJ:
      case REC_CRK:
      case REC_CRL:
      {
         r = CrkRule(LBase(base, dv), xr, minRisk);   // v5.0 Crooks L: the base grows at a new best (v5.1: Profit divides by dv)
         if(LadOn())                                                       // v4.6 profit ladder: the rule at the ladder's base, the extra paid from the cushion
         {
            double cush = 0, lam = 0, phi = 0, bmax = 0, gam = 0;
            double lb = LadBase(base, cush); LadPar(lam, phi, bmax, gam);
            r = LadGuard() ? (minRisk > 0 ? MathMin(base, minRisk) : base) : MathMin(CrkRule(lb, xr, minRisk), r + gam * cush / CrkT1Mult());
         }
         if(KZone()) r = crkW ? KCare(base, dv, kRisk) : (minRisk > 0 ? MathMin(base, minRisk) : base);   // v5.0 Crooks K below the start
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
   mql_long pa = armBar; int ps = st;
   ProcessBar(s);
   bool mine = exArm >= 0 && pa == exArm;
   gOurFill = mine && evFill;
   gOurExit = evExit && ((mine && MathAbs(ps) == 2) || gOurFill);
   gOurWin  = gOurExit && evWin;
   gOurMove = mine && MathAbs(ps) == 2 && evMove;
}
//--- open time of the bar with engine index idx (the last processed bar is shift 1: after OnNewBar, a start, a catch-up)
datetime BarTimeOf(mql_long idx)
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
//--- v4.5 Crooks E / I: the stop-out loss (spread and commission included, as LotsFor) of the lot used while a loss waits for a win:
//--- InpCrkELot, at least the broker's minimum, on its lot grid (LotsFor turns this amount back into exactly that lot)
double LotRisk(double lotsIn, double stopDist)        // v5.0: any lot (the E / I lot, the Crooks K careful lots)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   if(step <= 0) step = vmin > 0 ? vmin : 0.01;
   double lots = MathCeil(MathMax(lotsIn, vmin) / step - 1e-9) * step;
   return lots * ((stopDist + MathMax(CostSpr(), 0)) / ts * tv + InpCommLot);
}
double MinLotRisk(double stopDist) { return LotRisk(InpCrkELot, stopDist); }

//--- time filters (execution only) --------------------------------------------
bool NewsBlock(datetime ut, bool &startNow, datetime utPrev)
{
   startNow = false;
   bool blk = false;
   mql_long pre = (mql_long)InpNewsPre * 60;
   bool on[5]; datetime ts[5]; int du[5];
   on[0] = gpN1On; on[1] = gpN2On; on[2] = gpN3On; on[3] = gpN4On; on[4] = gpN5On;
   ts[0] = InpN1T;  ts[1] = InpN2T;  ts[2] = InpN3T;  ts[3] = InpN4T;  ts[4] = InpN5T;
   du[0] = InpN1Dur; du[1] = InpN2Dur; du[2] = InpN3Dur; du[3] = InpN4Dur; du[4] = InpN5Dur;
   for(int k = 0; k < 5; k++)
   {
      if(!on[k]) continue;
      if(ut >= ts[k] - pre && ut < ts[k] + du[k] * 60) blk = true;
      if(ut >= ts[k] && utPrev < ts[k]) startNow = true;
   }
   if(gpDNewsOn)
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
double TgtPx0(bool isL, double lvl) { double tl = TickSize() * 0.001; return isL ? CeilTick(lvl - tl) : FloorTick(lvl + tl + Spr()); }   // v4.9: the salvage target (the entry), no earn-back push
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
   bool a = mq_dot(trade).Buy(v, _Symbol, 0, slB, tpB, "HEDGE"_mq);
   if(!a) Print("Hedge buy failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
   bool b = mq_dot(trade).Sell(v, _Symbol, 0, slS, tpS, "HEDGE"_mq);
   if(!b) Print("Hedge sell failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
   if(a != b) { CloseAll("hedge pair: only one of the two trades opened"_mq); return false; }
   return a && b;
}
bool   PlaceHedge(bool isL, double v)                    // the pair's orders: a limit in the signal's direction and a stop the other way, both at the entry level
{
   if(gpEntryMode == ENTRY_MARKET) return HgMarket(v);
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
   double sl = StopPx(exL), tp = withTarget ? (trTrig == 2 && exArm == armBar ? TgtPx0(exL, tF) : TgtPx(exL, tF)) : 0;   // v4.9: salvage: at the entry
   if(exT1) { sl = exT1Half ? NormalizeDouble(op, _Digits) : exT1Stop; tp = withTarget ? TgtPx(exL, exT1Tp2) : 0; }   // Crooks TP1 rule: rest to TP2, at the entry after TP1
   if(exKeepSl > 0 && (exL ? exKeepSl > sl : exKeepSl < sl)) sl = exKeepSl;   // an adopted position keeps its tighter stop
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double minD = MinDist();
   // price is already through the engine's stop or target: the engine exits on this bar, so exit now
   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp)))
   { CloseAll((exL ? bid <= sl : ask >= sl) ? "the price is already past the stop"_mq : "the price is already past the target"_mq); return; }
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
      gCloseWhy = "Crooks TP1 rule: the TP1 part"_mq; if(PositionSelectByTicket(tk)) NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
      if(mq_dot(trade).PositionClosePartial(tk, NormalizeDouble(cv, 8))) { exT1Half = true; SetExits(true); }
      else { Print("TP1 partial close failed ("_mq, mq_dot(trade).ResultRetcodeDescription(), "), retrying"_mq); gT1Seen = true; }   // ticks retry while price is past TP1, the next bar close in any case
   }
   else CloseAll("Crooks TP1 rule: TP1 reached, too small to split, all closed"_mq);   // too small to split: close it all at TP1
}

//--- text helpers (table and markings) ----------------------------------------
string SgnR(double r) { return (r >= 0 ? "+"_mq : ""_mq) + DoubleToString(r, 2) + "R"_mq; }
string Share(int n, int total) { return total > 0 ? IntegerToString((int)MathRound(100.0 * n / total)) + "%"_mq : "-"_mq; }
string AccTxt() { int n = totW + totL; return IntegerToString(n) + " trades | "_mq + Share(totW, n) + " ("_mq + IntegerToString(totW) + "W/"_mq + IntegerToString(totL) + "L) | "_mq + SgnR(totR); }
string TpTxt()
{
   int n = totW + totL, xk = (int)gpExitAt;
   string s = ""_mq;
   for(int k = 1; k <= 4; k++) s += (k > 1 ? " | "_mq : ""_mq) + "TP"_mq + IntegerToString(k) + " "_mq + (k > xk ? "n/a"_mq : Share(tpHitN[k - 1], n) + " ("_mq + IntegerToString(tpHitN[k - 1]) + ")"_mq);
   return s;
}
string BeTxt() { int n = totW + totL; return "BE "_mq + IntegerToString(beN) + " ("_mq + Share(beN, n) + ") | locked profit "_mq + IntegerToString(lkN) + " ("_mq + Share(lkN, n) + ")"_mq +
                 (InpSvOn ? " | salvage "_mq + IntegerToString(svN) + " ("_mq + Share(svN, n) + ")"_mq : ""_mq); }
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
//--- the VWAP line: the engine's VWAP of this bar (vwHist[0], same anchor, source and volume as the signals), one segment from the previous
//--- bar, for the last gVwN bars (live: the segment that falls out of the window is removed); like the TradingView indicator's VWAP plot
void VwDraw(datetime bt)
{
   double v = ArraySize(vwHist) > 0 ? vwHist[0] : 0;
   if(InpVwapShow && gCanDraw && gVwPrevT > 0 && v > 0 && gVwPrev > 0 && bt >= gVwCut)
   {
      string nm = "ARM_VW"_mq + IntegerToString((mql_long)bt);
      if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_TREND, 0, gVwPrevT, gVwPrev, bt, v);
      else { ObjectMove(0, nm, 0, gVwPrevT, gVwPrev); ObjectMove(0, nm, 1, bt, v); }
      ObjectSetInteger(0, nm, OBJPROP_COLOR, InpVwapColor);
      ObjectSetInteger(0, nm, OBJPROP_WIDTH, (int)MathMax(1, MathMin(5, InpVwapWidth)));
      ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, nm, OBJPROP_BACK, false);           // over the candles, like the TradingView plot
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetString(0, nm, OBJPROP_TOOLTIP, "VWAP "_mq + DoubleToString(v, _Digits));
      if(gLive)                                         // the bars that left the window since the last cutoff (several after a disconnect)
      {
         for(int q = gVwN + 1; q < Bars(_Symbol, _Period); q++)
         {
            datetime ot = iTime(_Symbol, _Period, q);
            if(ot <= 0 || ot < gVwCut) break;
            ObjectDelete(0, "ARM_VW"_mq + IntegerToString((mql_long)ot));
         }
         datetime cut = iTime(_Symbol, _Period, gVwN);
         if(cut > gVwCut) gVwCut = cut;
      }
   }
   gVwPrevT = bt; gVwPrev = v;
}

// one engine bar: armed limit, then a filled trade's boxes, entry / TP lines, fill arrow and price labels, then its result
void DrawBar(datetime bt)
{
   VwDraw(bt);                                          // v4.4: the VWAP line (its own switch, also with the markings off)
   if(!InpDraw || !gCanDraw) return;
   if(evCancel != 0 || evFill) ObjectDelete(0, "ARM_limit"_mq);
   if(evArm) MarkLine("ARM_limit"_mq, bt, lim, bt + PeriodSeconds() * gpRetestBars, lim, InpColEntry, 1, STYLE_DASH);   // MT5 dashes only width-1 lines
   int xk = (int)gpExitAt;
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
   if(TfHold()) s = "CHART ON "_mq + TfName((int)_Period) + ": NO NEW TRADES (EA TRADES "_mq + TfName(gTfTrade) + ")"_mq;
   if(!gpTfOk) s = "WRONG CHART: "_mq + TfName(gpTf) + " PRESET, NO TRADES"_mq;
   string ex = exState == 2 ? (exHg ? " (hedge pair open)"_mq : exArm < 0 ? " (in trade, own stop and target)"_mq : " (in trade)"_mq) : (exState == 1 ? (gVirt ? " (waiting for the level)"_mq : exHg ? " (hedge orders working)"_mq : " (order working)"_mq) : ""_mq);
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
   int    xk = (int)gpExitAt;
   string tps = has ? DoubleToString(t1, _Digits) + " | "_mq + DoubleToString(t2, _Digits) + " | "_mq + DoubleToString(t3, _Digits) + " | "_mq + DoubleToString(t4, _Digits) : "-"_mq;
   bool   isC = InpRec == REC_C || InpRec == REC_CS, isK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRD || CrkCFam();
   bool   kRec = exState != 0 ? crkRec : CrkRecNext();
   string kLim = InpRec == REC_CRF || InpRec == REC_CRI ? ", at most "_mq + DoubleToString(InpCrkFK, 1) + "x base"_mq : InpRec == REC_CRH ? ", at most "_mq + DoubleToString(InpCrkHPct, 1) + "% of equity"_mq :
                 InpRec == REC_CRJ || InpRec == REC_CRK ? ", drawdown "_mq + DoubleToString(MathMax(0.0, crkPk - (totalNet - gNet0)), 2) : ""_mq;
   string kWait = InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRL ? " | "_mq + DoubleToString(InpCrkELot, 2) + " lot, waiting for a win"_mq : " | base, waiting for a win"_mq;
   double nrT = totalNet - gNet0;                       // v5.0 Crooks K / L: where the closed profit is (since the restart)
   string kCare = InpCrkKMode == CKM_USD ? DoubleToString(InpCrkKUsd, 2) + (SizeProfit() ? " win"_mq : ""_mq) : InpCrkKMode == CKM_PCT ? DoubleToString(InpCrkKPct, 0) + "% of the base"_mq : DoubleToString(InpCrkKLots, 2) + " lot"_mq;
   string kZn = InpRec == REC_CRK ? (KZone() ? " | below the start: "_mq + (crkW ? "careful "_mq + kCare + " after a win"_mq : DoubleToString(InpCrkELot, 2) + " lot until a win"_mq) : " | above the start (Crooks J)"_mq) :
                InpRec == REC_CRL ? (nrT < 0 ? " | below the start"_mq : nrT < crkPk ? " | below the best"_mq : " | at the best, base "_mq + DoubleToString(LBase(ShowBase(), SizeProfit() ? PDiv(ExitR()) : 1.0), 2)) : ""_mq;
   string kTxt = DoubleToString(crkL, 2) + (InpRec == REC_CRG ? " (at most "_mq + DoubleToString(InpCrkGX * ShowBase(), 0) + ")"_mq : ""_mq) +
                 (CrkCFam() ? (kRec ? " | recovery trade"_mq + (CrkNp() > 1 ? ", part "_mq + IntegerToString(CrkNp() - CrkParts() + 1) + " of "_mq + IntegerToString(CrkNp()) : ""_mq) +
                  (InpRec == REC_CRL ? ", "_mq + IntegerToString(CrkParts()) + (CrkParts() == 1 ? " part"_mq : " parts"_mq) + " to go"_mq : ""_mq) + kLim : (crkL > 0 ? kWait : " | base"_mq)) + kZn : " | trade "_mq + IntegerToString(crkN + 1) + (kRec ? " recovery"_mq : " base"_mq)) + (InpRec == REC_CRB ? " | split "_mq + IntegerToString(InpCSplit) : ""_mq)
                 + (exState != 0 && exT1 ? (exT1Half ? " | TP1 booked, rest to TP2"_mq : " | TP1 rule, stop "_mq + DoubleToString(exT1Stop, _Digits)) : ""_mq)
                 + (!CrkPrOn() ? ""_mq : CrkPause() ? " | paused, "_mq + IntegerToString(crkSkipLeft) + " days left"_mq : crkWait ? " | waiting for "_mq + IntegerToString(InpCrkPrM) + " wins in a row ("_mq + IntegerToString(crkWW) + ")"_mq :
                    crkNeedL ? " | waiting for a loss, then a win"_mq : crkHg ? " | hedge pair on the next signal"_mq : crkF > 0 ? " | lost recoveries in a row "_mq + IntegerToString(crkF) + "/"_mq + IntegerToString(InpCrkPrN) : ""_mq);
   string rec = InpRec == REC_OFF ? "off"_mq : (isC ? DoubleToString(carried, 2) + " | split "_mq + IntegerToString(InpCSplit) : isK ? kTxt : DoubleToString(recPool, 2) + " | "_mq + IntegerToString(recLosses) + " losses in a row"_mq);
   TblAdd("AUCTION RETEST"_mq, "EA v5.1"_mq, white, ((color)14061373));
   if(InpPreset != PRE_CUSTOM) TblAdd("PRESET"_mq, PresetName() + (gpTfOk ? ""_mq : " | needs an "_mq + TfName(gpTf) + " chart"_mq) + (InpAddMine ? " | + my filters"_mq : ""_mq), gpTfOk ? posC : negC, cell);
   TblAdd("STATE"_mq, gStateTxt, white, act ? (st == 2 ? ((color)5287756) : ((color)4536050)) : (armed ? ((color)39167) : ((color)7037021)));
   TblAdd("ENTRY / STOP"_mq, has ? DoubleToString(lim, _Digits) + " / "_mq + DoubleToString(stp, _Digits) + (trHalf ? " (half stop)"_mq : ""_mq) : "-"_mq, white, cell);
   TblAdd("TP1 | TP2 | TP3 | TP4 (exit TP"_mq + IntegerToString(xk) + ")"_mq, tps, posC, cell);
   double lCu = 0;
   TblAdd("RISK | LOTS"_mq, exState != 0 ? DoubleToString(exRiskAmt, 2) + " | "_mq + DoubleToString(exLots, 2) : BaseTxt(lCu), white, cell);
   TblAdd(isC ? "LOSSES CARRIED"_mq : isK ? "CROOKS: LOSS TO WIN BACK"_mq : "RECOVERY POOL"_mq, rec, (isC ? carried : isK ? crkL : recPool) > 0 ? negC : white, cell);
   if(InpLadder != LAD_OFF) TblAdd("PROFIT LADDER"_mq, LadTxt(), LadGuard() ? negC : LadOn() ? posC : white, cell);
   TblAdd("STREAK W | L"_mq, IntegerToString(winRow) + " | "_mq + IntegerToString(lossRow) + " | total "_mq + IntegerToString(exW) + "W/"_mq + IntegerToString(exLn) + "L"_mq, white, cell);
   TblAdd("DAY P&L | FILLS"_mq, DoubleToString(dayPnl, 2) + " | "_mq + IntegerToString(dayFills) + "/"_mq + IntegerToString(gpMaxFills) + (InpMLockOn || InpPLockOn ? " | month "_mq + DoubleToString(monPnl, 2) + (monLocked ? " (locked "_mq + DoubleToString(InpPLockPct / 100.0 * monPeak, 2) + ")"_mq : ""_mq) : ""_mq), dayPnl >= 0 ? posC : negC, cell);
   TblAdd("SIGNALS | TAKEN | SKIPPED"_mq, IntegerToString(sigN) + " | "_mq + IntegerToString(takenN) + " | "_mq + IntegerToString(skipN) + (missN > 0 ? " | missed "_mq + IntegerToString(missN) : ""_mq) + (skipWhy != ""_mq ? " (last: "_mq + skipWhy + ")"_mq : ""_mq), skipN + missN > 0 ? negC : white, cell);
   TblAdd("SIGNAL TRADES | WIN % | R"_mq, AccTxt() + " | last "_mq + lastRes, totR >= 0 ? posC : negC, cell);
   TblAdd("TP HIT"_mq, TpTxt(), posC, cell);
   if(gpMv1On || gpMv2On || gpMv3On || InpBeOn || InpSvOn) TblAdd("BREAKEVEN"_mq, BeTxt(), white, cell);
   if(gpNoChase || gpChopOn || gpEmaOn || gpMinVwOn || gpMaxVwOn || gpStopVwOn || gpTouchVwOn || gpEntVwOn) TblAdd("SKIPPED BY FILTERS"_mq, FltTxt(), ghR <= 0 ? posC : negC, cell);
   TblAdd("DATA RANGE"_mq, gFirstT > 0 ? DateTxt(UserTime(gFirstT), true) + " -> "_mq + DateTxt(UserTime(gLastDone), false) + " | "_mq + IntegerToString(bi + 1) + " bars"_mq : "-"_mq, white, cell);
   TblAdd("RESTART MEMORY"_mq, gPersist ? (gRestored ? "on | continued from "_mq + DateTxt(UserTime(gSvT), true) : "on"_mq) : InpRemember ? "off in the Strategy Tester"_mq : "off"_mq, white, cell);
   TblAdd("LAST CLOSE"_mq, gLastClose, gLastCloseOut ? negC : white, cell);
   TblAdd("BROKER CLOCK"_mq, MQLInfoInteger(MQL_TESTER) != 0 ? GmtTxt(SrvGMT(TimeCurrent())) + " (Strategy Tester)"_mq : TzTxt(), StringFind(TzTxt(), "CHECK"_mq) >= 0 ? negC : white, cell);
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
   if(!TfHold()) gTakenT = BarTimeOf(armBar);         // decided on now (taken, skipped or rejected): a restart does not take it again (not on another timeframe)
   ulong pTk; double pVol, pOpen;
   bool posNow = HasPosition(pTk, pVol, pOpen);
   bool crkPs = CrkPause();
   bool tfHold = TfHold();                           // v4.4: the chart shows another timeframe than the one the EA trades
   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock || crkPs || monStop || tfHold);   // the hard cap acts only on a signal that can be taken
   double minR = (InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL || LadOn()) ? MinLotRisk(trRisk) : 0;   // v4.5 Crooks E / I, v4.6 ladder guard, v5.0 K / L: the 0.01 lot on this setup
   double kR = InpRec == REC_CRK && InpCrkKMode == CKM_LOTS ? LotRisk(InpCrkKLots, trRisk) : 0;   // v5.0 Crooks K: the careful lots on this setup
   double rAmt = NextRisk(ExitR(), canTake, minR, kR);
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
   skipWhy = (exState != 0 || posNow) ? "still in a trade"_mq : tfHold ? "chart on "_mq + TfName((int)_Period) + ", the EA trades "_mq + TfName(gTfTrade) : (newsBlk || flatNow) ? "news / force-close"_mq : capStop ? "hard cap stop"_mq : paused ? "paused"_mq : dayBlock ? "streak stop"_mq : crkPs ? "Crooks C pause"_mq : monStop ? "monthly lock"_mq : v <= 0 ? "size 0"_mq : ""_mq;
   if(skipWhy != ""_mq) { skipN++; return; }
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   double sprNow = CostSpr();
   exCostPx = InpEarnBack && tv > 0 && !hg ? InpCommLot / (tv / ts) + sprNow : 0;   // no earn-back on the hedge pair: its levels are the inputs
   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((ld + sprNow) / ts * tv + InpCommLot); exBase = gBase; exBaseWin = gBaseWin;
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
   else if(gpEntryMode == ENTRY_MARKET)
   {
      past = !OrderExits(isL, ep, true, sl, tp);
      ok = !past && (isL ? mq_dot(trade).Buy(v, _Symbol, 0, sl, tp, "ARM"_mq) : mq_dot(trade).Sell(v, _Symbol, 0, sl, tp, "ARM"_mq));
   }
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) { OrderExits(isL, ep, false, sl, tp); ok = mq_dot(trade).BuyLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM"_mq); }
      else if(ask <= ep)                { past = !OrderExits(isL, ep, true, sl, tp); ok = !past && mq_dot(trade).Buy(v, _Symbol, 0, sl, tp, "ARM"_mq); }   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                  // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) { OrderExits(isL, ep, false, sl, tp); ok = mq_dot(trade).SellLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM"_mq); }
      else if(bid >= ep)                { past = !OrderExits(isL, ep, true, sl, tp); ok = !past && mq_dot(trade).Sell(v, _Symbol, 0, sl, tp, "ARM"_mq); }
      else { ok = true; gVirt = true; }
   }
   if(ok)
   {
      exState = 1; exArm = armBar; exArmT = gTakenT; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg;
      gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false; gT1Seen = false; gExitSeen = false; gGoneWait = false;   // no events of an earlier trade
   }
   else if(past) { skipN++; skipWhy = "price already past the target"_mq; }
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
   double ep = EntryPx(exL), sl = 0, tp = 0;
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      if(!OrderExits(exL, ep, true, sl, tp)) { Print("ARM entry skipped: the price is already past the target."_mq); return; }   // v4.4: the take profit goes with the order
      if(!(exL ? mq_dot(trade).Buy(exLots, _Symbol, 0, sl, tp, "ARM"_mq) : mq_dot(trade).Sell(exLots, _Symbol, 0, sl, tp, "ARM"_mq)))
         Print("ARM entry failed: "_mq, mq_dot(trade).ResultRetcodeDescription());
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
void BookClosed_ea();
void BookClosed() { sim_book(exPnl, exHg ? 1 : 0, exRiskAmt, exLots); BookClosed_ea(); }
void BookClosed_ea()
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
   if(oscP >= (SizeProfit() ? (exBaseWin > 0 ? exBaseWin : BookBase() * ExitR()) : BookBase())) { oscU = 1; oscP = 0; } else if(win) oscU++;   // v5.0: with Profit the goal is one base win (v5.1: the trade's own)
   // Crooks: losses add to the loss to win back, wins reduce it; a new cycle when it is all back, less than a cent left (A, D: also when a recovery trade wins; C keeps a leftover)
   bool lastPart = CrkParts() == 1;                     // this recovery trade went for the last part of the loss (Crooks C over N wins)
   crkL = MathMax(0.0, crkL - exPnl);
   crkPk = MathMax(crkPk, totalNet - gNet0);            // v4.5 Crooks J, v4.6 ladder: the highest closed profit (whatever the rule, so a switch knows it; v4.8: since the monthly restart)
   double gCush = 0;
   if(InpRec == REC_CRG && InpCrkGX > 0) crkL = MathMin(crkL, InpCrkGX * LadBase(BookBase(), gCush));   // v4.5 Crooks G: never more than X x base (v4.6: the ladder's base)
   if(exHg)                                             // the hedge pair closed (exPnl = both trades): forget the loss, or Crooks C goes on from the trade that closed last
   {
      crkF = 0; crkHg = false;
      if(InpCrkHgForget || crkL < 0.01) CrkCycle(); else { crkN++; crkP = InpRec == REC_CRL ? LParts() : CrkNp(); }
   }
   else if(crkL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && crkRec)) CrkCycle();
   else
   {
      crkN++; crkP = !win ? (InpRec == REC_CRL ? LParts() : CrkNp()) : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts();   // Crooks C over N wins: a loss starts the parts again (v5.0 L: from the drawdown)
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
      Print("Position #"_mq, pTk, " of this EA filled while its order was being cancelled: kept, it runs to its own stop loss and take profit."_mq);
   }
   bool gone = exState == 2 && !pos;
   if(gone && !closedNew && !gExitSeen && !gGoneWait) { gGoneWait = true; gone = false; }   // no closing deal in the history yet: booked at the next bar, with it
   bool exClosed = (exState == 1 && !pos && closedNew) || gone;

   // 2. an executed trade has closed
   if(exClosed) BookClosed();
   if(gExitRetry)                                       // a close that failed before: again
   {
      if(exState != 2 || !pos) gExitRetry = false;
      else { CloseRule((gExitWhy != ""_mq ? gExitWhy : "a close that failed before a restart"_mq) + " (again)"_mq); pos = HasPosition(pTk, pVol, pOpen); }
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
         Print("Trade #"_mq, pTk, " filled before the engine's fill (bid chart) and its setup ended: kept, it runs to its own stop loss and take profit."_mq);
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
         CloseRule(gOurWin ? "the engine's final target was reached (bar close, bid chart)"_mq : "the engine's stop was hit (bar close, bid chart)"_mq);
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
   if(flatNow && pos) CloseRule(fcNow ? "the daily force-close time"_mq : wkndStart ? "the weekend starts (Saturday)"_mq : "a news window starts"_mq);
   if(exHg && exState == 2 && (flatNow || newsBlk)) CancelPending();   // hedge pair: a trade still waiting is not opened after force-close, weekend or news
   if(exState == 1 && (flatNow || newsBlk)) { CancelPending(); exState = 0; exArm = -1; gVirt = false; exHg = false; }

   // monthly restart (once no trade of the old month is left) and the monthly locks, after every booking of this bar
   if(monRestPend && exState == 0 && !HasPosition(pTk, pVol, pOpen)) { monRestPend = false; MonthRestart(); }
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
   int exitK = (int)gpExitAt;
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   double px = SymbolInfoDouble(_Symbol, SYMBOL_BID);   // the engine's levels are bid-chart levels for both directions
   double tp[3]; double pp[3];
   bool eng = exArm >= 0 && armBar == exArm && MathAbs(st) == 2;   // the engine's levels are this trade's while it is in it
   tp[0] = exTpL[0] > 0 ? exTpL[0] : eng ? t1 : 0; tp[1] = exTpL[1] > 0 ? exTpL[1] : eng ? t2 : 0; tp[2] = exTpL[2] > 0 ? exTpL[2] : eng ? t3 : 0;   // the trade's own levels (v4.4)
   pp[0] = gpP1; pp[1] = gpP2; pp[2] = gpP3;
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
            gCloseWhy = "partial close at TP"_mq + IntegerToString(k + 1); if(PositionSelectByTicket(tk)) NoteClose(PositionGetInteger(POSITION_IDENTIFIER));
            mq_dot(trade).PositionClosePartial(tk, NormalizeDouble(cv, 8));
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
   IoI("ou"_mq, oscU); IoD("op"_mq, oscP); IoD("tn"_mq, totalNet); IoD("pk"_mq, crkPk); IoD("rn"_mq, gNet0); IoI("ew"_mq, exW); IoI("el"_mq, exLn); IoB("cs"_mq, capStop);
   IoD("kl"_mq, crkL); IoI("kn"_mq, crkN); IoB("kw"_mq, crkW); IoI("kp"_mq, crkP); IoI("kf"_mq, crkF); IoB("ka"_mq, crkWait); IoI("kb"_mq, crkWW);
   IoB("kc"_mq, crkNeedL); IoB("ks"_mq, crkSkip); IoI("kt"_mq, crkSkipLeft); IoI("ku"_mq, crkUDay); IoB("kh"_mq, crkHg); IoI("kx"_mq, gCrkPrPrev);
   // streaks and pauses; the month of the last bar (a new month while the EA was off) and a restart still waiting for a trade to close
   IoD("dp"_mq, dayPnl); IoI("lr"_mq, lossRow); IoI("wr"_mq, winRow); IoB("db"_mq, dayBlock); IoI("pl"_mq, pauseLeft); IoB("pa"_mq, paused);
   IoI("mk"_mq, gMonKey); IoB("mr"_mq, monRestPend); IoD("mp"_mq, monPnl); IoD("mq"_mq, monPeak); IoB("ms"_mq, monStop); IoB("ml"_mq, monLocked);
   // the trade the EA is in, or its working order: its type and what it booked so far; the broker deals already counted
   IoI("xs"_mq, exState); IoB("xl"_mq, exL); IoD("xv"_mq, exLots); IoD("xr"_mq, exRiskAmt); IoD("xb"_mq, exBase); IoD("xw"_mq, exBaseWin); IoD("xc"_mq, exCostPx); IoD("xp"_mq, exPnl); IoD("xk"_mq, exKeepSl);
   IoB("kr"_mq, crkRec); IoB("xy"_mq, exSynced);
   double xe = exLim, x1 = exTpL[0], x2 = exTpL[1], x3 = exTpL[2];   // v4.4: the trade's setup (arm bar time, entry) and its own TP1-TP3
   IoT("xa"_mq, exArmT); IoD("xe"_mq, xe); IoD("x1"_mq, x1); IoD("x2"_mq, x2); IoD("x3"_mq, x3); IoT("xt"_mq, gTakenT); IoB("xq"_mq, gExitRetry);
   ulong cw = (ulong)gCloseId; IoU("xw"_mq, cw); gCloseId = (mql_long)cw;   // the last position this EA closed (its report after a restart)
   exLim = xe; exTpL[0] = x1; exTpL[1] = x2; exTpL[2] = x3;
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
   bool pkSaved = GlobalVariableCheck(gSvBase + "pk"_mq);  // v4.5: Crooks J's peak (a state saved before v4.5 has none)
   StateIO(false);
   if(!pkSaved) crkPk = MathMax(crkPk, totalNet - gNet0);   // ... then the closed profit itself is the peak
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
   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; totalNet = 0; crkPk = 0; gNet0 = 0; exW = 0; exLn = 0; capStop = false;
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
   ArrayInitialize(tpHitN, 0); beN = 0; lkN = 0; svN = 0; gFirstT = 0; trTrig = 0;
   gDrawT = 0; ArrayResize(gDrawn, 0); gStateTxt = "SCANNING"_mq;
   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = ""_mq; gExitSeen = false; gGoneWait = false;
   gVwPrevT = 0; gVwPrev = 0;
   gOurFill = false; gOurExit = false; gOurWin = false; gOurMove = false; gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
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
   if(HgOpen()) { exState = 2; exHg = true; Print("Hedge pair still open: its trades run to their own stop loss and take profit."_mq); }
   else if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      double pSl = PositionGetDouble(POSITION_SL), pTp = PositionGetDouble(POSITION_TP);
      datetime aT = MathAbs(st) >= 1 && !trGhost ? BarTimeOf(armBar) : 0;
      // v4.4: the engine's setup is this trade's when it is the saved setup, re-linked in the warm-up (restart memory) and still the engine's;
      // without a saved setup, when it has the trade's direction and was armed before the trade opened. Never on another timeframe than
      // the one the EA trades: the trade keeps its own stop loss and take profit until the chart is back
      bool same = !TfHold() && MathAbs(st) >= 1 && !trGhost && (st > 0) == isL &&
                  (gRestored && exArmT > 0 ? exArm >= 0 && armBar == exArm
                                           : aT > 0 && (datetime)PositionGetInteger(POSITION_TIME) >= aT + PeriodSeconds(_Period));
      exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol;   // a restored trade keeps its lots (partials)
      if(same && exTpL[0] <= 0) { exTpL[0] = t1; exTpL[1] = t2; exTpL[2] = t3; }   // the trade's own TP1-TP3 (partials)
      if(same && MathAbs(st) == 2)
      {
         exArm = armBar; if(exArmT <= 0) exArmT = aT; exLim = lim; exSynced = true;
         for(int q = 0; q < 3; q++) pDone[q] = pDone[q] || tpHit >= q + 1;
         Print("Adopted open position #"_mq, tk, " (engine is in the same trade)."_mq);
         // never widen the stop of an adopted position (a Crooks TP1-rule position is sized for its tighter stop): SetExits keeps it from now on
         exKeepSl = pSl > 0 && (isL ? pSl > StopPx(isL) : pSl < StopPx(isL)) ? pSl : 0;
         SetExits(true);
      }
      else if(same)
      {
         exArm = armBar; if(exArmT <= 0) exArmT = aT; exLim = lim; exSynced = false;
         Print("Open position #"_mq, tk, " kept: it filled before the engine's fill (bid chart); the engine's setup is still armed."_mq);
      }
      else
      {
         exArm = -1; exSynced = gRestored && exSynced;
         Print("Open position #"_mq, tk, " kept: the engine is not in it (its setup ended, new inputs or another timeframe). It runs to its own stop loss "_mq,
               DoubleToString(pSl, _Digits), " and take profit "_mq, pTp > 0 ? DoubleToString(pTp, _Digits) : "(none)"_mq, "."_mq);
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
      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseRule("a force-close, weekend start or news start passed while the EA was off"_mq); BookBrokerDeals(); }
      // v4.4: the engine's stop (or its final target without earn-back) of this trade was reached while the EA was off: closed now, as after a
      // disconnect (earn-back and the Crooks TP1 rule only outlive a win; its TP1 part is booked at the next bar close)
      if(gMissExit && exState == 2 && !exHg && HasPosition(rTk, rVol, rOp) && (!InpEarnBack || !gMissWin) && !(exT1 && (gMissWin || exT1Half)))
      { CloseRule(gMissWin ? "the engine's final target was reached while the EA was off"_mq : "the engine's stop was hit while the EA was off"_mq); BookBrokerDeals(); }
      if(gRestFlat && exHg && exState == 2) CancelPending();
      if(monRestPend && exState == 0 && !HasPosition(rTk, rVol, rOp)) { monRestPend = false; MonthRestart(); }
      MonthCheck();
      bool isCC = InpRec == REC_C || InpRec == REC_CS, isKK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRD || CrkCFam();
      Print("Restart memory: continued from "_mq, DateTxt(UserTime(gSvT), true), " | loss to win back "_mq, DoubleToString(isCC ? carried : isKK ? crkL : recPool, 2),
            " | streak "_mq, winRow, "W / "_mq, lossRow, "L"_mq, (paused || pauseLeft > 0) ? " | paused"_mq : ""_mq, CrkPause() ? " | Crooks C pause"_mq : ""_mq,
            capStop ? " | hard cap stop"_mq : ""_mq, exState == 2 ? " | trade still open"_mq : ""_mq);
   }
   gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;   // the warm-up's events for the saved trade are handled above
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm && (gTakenT == 0 || BarTimeOf(armBar) != gTakenT);   // re-place the engine's armed setup on the first tick (not one armed while paused, not one already decided on)
}

//--- one copy per symbol + magic number: two copies cancel and close each other's trades and share one restart memory. A temporary global
//--- variable (gone when MT5 closes) holds the chart of the copy that runs; a lock of a chart that no longer runs an EA is taken over
bool LockTake()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return true;
   gLockN = SvExtra("run"_mq);
   gLockV = (double)(ChartID() & 0xFFFFFFFFFFFF) + 1.0;  // 48 bits of the chart id (exact in a double), never 0
   if(!GlobalVariableCheck(gLockN)) GlobalVariableTemp(gLockN);
   if(GlobalVariableSetOnCondition(gLockN, gLockV, 0)) return true;
   double cur = GlobalVariableGet(gLockN);
   if(cur == gLockV) return true;                        // this chart (new inputs, another timeframe)
   for(mql_long id = ChartFirst(); id >= 0; id = ChartNext(id))
      if(id != ChartID() && (double)(id & 0xFFFFFFFFFFFF) + 1.0 == cur && ChartGetString(id, CHART_EXPERT_NAME) != ""_mq) return false;   // that chart still runs it
   return GlobalVariableSetOnCondition(gLockN, gLockV, cur);   // that chart is gone: take over
}
void LockFree() { if(gLockN != ""_mq && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableSetOnCondition(gLockN, 0, gLockV); }
//--- a note on the other EAs in this MetaTrader: one that manages every trade of the account can close this EA's trades (the log then names
//--- who closed each trade); an alert for an older copy of this EA on the same symbol (it has no lock and may use the same magic number)
void OtherEAs()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;
   string lst = ""_mq; bool twin = false;
   for(mql_long id = ChartFirst(); id >= 0; id = ChartNext(id))
   {
      if(id == ChartID()) continue;
      string nm = ChartGetString(id, CHART_EXPERT_NAME);
      if(nm == ""_mq) continue;
      lst += (lst == ""_mq ? ""_mq : ", "_mq) + nm + " ("_mq + ChartSymbol(id) + " "_mq + StringSubstr(EnumToString(ChartPeriod(id)), 7) + ")"_mq;
      if(ChartSymbol(id) != _Symbol || StringFind(nm, "AuctionRetest"_mq) != 0) continue;
      bool locked = false;                               // a v4.4+ copy holds a lock (its own magic number, else this start would have failed)
      for(int q = GlobalVariablesTotal() - 1; q >= 0 && !locked; q--)
      {
         string g = GlobalVariableName(q);
         if(StringFind(g, "ARX|"_mq) == 0 && StringFind(g, "|run"_mq) == StringLen(g) - 4 && GlobalVariableGet(g) == (double)(id & 0xFFFFFFFFFFFF) + 1.0) locked = true;
      }
      if(!locked) twin = true;
   }
   if(lst != ""_mq) Print("Other EAs running in this MetaTrader: "_mq, lst, ". An EA that manages every trade of the account can close this EA's trades: the log names who closed each trade."_mq);
   if(twin)
   {
      string m = "Another chart on "_mq + _Symbol + " runs an older AuctionRetestEA. If it uses the same magic number ("_mq + IntegerToString(InpMagic) +
                 "), the two copies cancel and close each other's trades: remove one, or give each its own magic number."_mq;
      Print(m); Alert(m);
   }
}

int OnInit()
{
   mq_dot(trade).SetExpertMagicNumber(InpMagic);
   mq_dot(trade).SetDeviationInPoints(50);
   mq_dot(trade).SetTypeFillingBySymbol(_Symbol);
   PresetApply();                                        // v4.8: the preset's values (or the inputs) before anything uses them
   ResetEngine();
   if(ArraySize(labSeq) == 0) LabReset();               // the Labouchere list is kept with the other recovery states when inputs change
   // restart memory: on a fresh start (MT5 or the EA restarted) continue from the saved state; switched off: forget it
   gPersist = InpRemember && MQLInfoInteger(MQL_TESTER) == 0 && MQLInfoInteger(MQL_OPTIMIZATION) == 0;
   gSvBase = SvBaseName(); gRestored = false;
   if(!LockTake())
   {
      string m = "Another copy of this EA runs on "_mq + _Symbol + " with magic number "_mq + IntegerToString(InpMagic) + " (another chart). Two copies cancel and close "_mq +
                 "each other's trades: remove one, or give each its own magic number."_mq;
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   TzPick(true);                                         // the broker's clock (Auto), before the warm-up uses it
   if(MQLInfoInteger(MQL_TESTER) == 0)                   // the timeframe the EA trades: the one it was attached to (also after a restart)
   {
      string tfN = SvExtra("tf"_mq);
      string tpN = SvExtra("tfp"_mq);                      // v4.8: 1 = the timeframe was set by a preset
      bool fromPreset = GlobalVariableCheck(tpN) && GlobalVariableGet(tpN) > 0;
      if(gpTf > 0) gTfTrade = gpTf;                     // v4.8: a preset trades only its own timeframe
      else if(fromPreset) gTfTrade = (int)_Period;      // back to Custom after a preset: the chart's timeframe, as if attached now
      else if(gTfTrade == 0) gTfTrade = GlobalVariableCheck(tfN) ? (int)MathRound(GlobalVariableGet(tfN)) : (int)_Period;
      GlobalVariableSet(tfN, gTfTrade);
      GlobalVariableSet(tpN, gpTf > 0 ? 1 : 0);
      if(TfHold() && gpTf == 0)                         // (a preset on another chart has its own message below)
      {
         string m = "The chart is on "_mq + TfName((int)_Period) + ", but this EA trades "_mq + TfName(gTfTrade) + " (the timeframe it was attached to): no new trades until the chart is back on "_mq +
                    TfName(gTfTrade) + ". The open trade keeps its stop loss and take profit. To trade "_mq + TfName((int)_Period) + ", remove the EA and attach it again."_mq;
         Print(m); Alert(m);
      }
   }
   if(!gpTfOk)                                          // v4.8: a preset trades only on its own chart timeframe
   {
      string m = "Strategy preset "_mq + PresetName() + " trades only on an "_mq + TfName(gpTf) + " chart; this chart is "_mq + TfName((int)_Period) +
                 ": no trades. Switch the chart to "_mq + TfName(gpTf) + ", or choose another preset or Custom."_mq;
      Print(m); Alert(m);
   }
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();
   gRestFlat = false; gBrokerPend = false;
   // Start fresh once: forget the money-management state (kept by MT5 on new inputs and by the restart memory); done once while it is on
   string rsN = SvExtra("rsd"_mq);
   if(MQLInfoInteger(MQL_TESTER) == 0)
   {
      if(!InpMemFresh) GlobalVariableDel(rsN);
      else if(!GlobalVariableCheck(rsN))
      {
         SvWipe(); MemoryFresh(); GlobalVariableSet(rsN, 1);
         Print("Started fresh: the loss recovery, streaks and pauses start again from the base risk. Set 'Start fresh once' back to false."_mq);
      }
   }
   if(gPersist) gRestored = StateLoad();                 // a fresh start or new inputs: continue from the saved state (written at OnDeinit)
   if(gRestored && (gInitDone || !InpCapOn || InpCapAction != CAP_STOP)) capStop = false;   // a hard-cap Stop ends with new inputs (as before) or a cap that no longer stops
   if(gCrkPrPrev != (int)InpCrkPr || !CrkCFam()) { crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; }
   gCrkPrPrev = (int)InpCrkPr;
   gHedgeOk = (ENUM_ACCOUNT_MARGIN_MODE)AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_HEDGING;
   if(CrkCFam() && InpCrkPr == CPR_HEDGE && !gHedgeOk) Print("Crooks C hedge rule: this account cannot hold a buy and a sell together (netting), so the rule forgets the loss instead."_mq);
   // markings and table only where they can be seen (not in non-visual tests or optimisation)
   gCanDraw = MQLInfoInteger(MQL_OPTIMIZATION) == 0 && (MQLInfoInteger(MQL_TESTER) == 0 || MQLInfoInteger(MQL_VISUAL_MODE) != 0);
   ObjectsDeleteAll(0, "ARM_"_mq);
   if(InpSpread < 0 || InpCommLot < 0) { Print("Spread and commission must be 0 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((InpSizeMode == PSZ_USD && InpBaseRisk <= 0) || (InpSizeMode == PSZ_LOT && InpBaseLots <= 0) || (InpSizeMode == PSZ_PCT && InpEqPct <= 0))
   { Print("Position size: the base risk, base lots or risk % of equity must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpTp1R > gpTp2R || gpTp2R > gpTp3R || gpTp3R > gpTp4R) { Print("Targets must be in order: TP1 <= TP2 <= TP3 <= TP4."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpMaxVwOn && gpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpBeOn && InpBeR <= 0) { Print("BE trigger: the R in profit must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpSvOn && (InpSvR <= 0 || InpSvR >= 1)) { Print("Salvage trigger: the R against the trade must be above 0 and below 1 (the stop is at 1R)."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(gpTouchVwOn && gpTouchVwN < 1) { Print("VWAP touched in the last N candles: N must be 1 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpCrkT1 && (InpCrkT1Pct < 10 || InpCrkT1Pct > 90)) { Print("Crooks TP1 rule: % closed at TP1 must be 10 to 90."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(CrkCFam() && InpCrkPr != CPR_OFF && (InpCrkPrN < 1 || InpCrkPrM < 1 || InpCrkPrD < 1)) { Print("Crooks C rule: N, M and D must be 1 or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((InpMLockOn && InpMLockAmt <= 0) || (InpPLockOn && (InpPLockAt <= 0 || InpPLockPct < 1 || InpPLockPct > 100))) { Print("Monthly profit lock: the amounts must be above 0 and the lock % 1 to 100."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(CrkCFam() && InpCrkPr == CPR_HEDGE && (InpCrkHgSl <= 0 || InpCrkHgTp <= 0)) { Print("Crooks C hedge rule: stop loss and take profit must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(CrkCFam() && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100)) { Print("Crooks C rule: % of the loss must be 10 to 100."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((InpRec == REC_CRE || InpRec == REC_CRI || InpRec == REC_CRK || InpRec == REC_CRL) && InpCrkELot <= 0) { Print("Crooks E / I / K / L: the lot while waiting for a win must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((InpRec == REC_CRF || InpRec == REC_CRI) && InpCrkFK < 1) { Print("Crooks F / I: the recovery limit must be 1 x the base risk or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRG && InpCrkGX <= 0) { Print("Crooks G: the limit of the loss to win back must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRH && InpCrkHPct <= 0) { Print("Crooks H: the % of the equity must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if((InpRec == REC_CRJ || InpRec == REC_CRK) && InpCrkJX <= 0) { Print("Crooks J / K: the drawdown must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRK && ((InpCrkKMode == CKM_LOTS && InpCrkKLots <= 0) || (InpCrkKMode == CKM_USD && InpCrkKUsd <= 0) || (InpCrkKMode == CKM_PCT && InpCrkKPct <= 0)))
   { Print("Crooks K: the careful size must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRL && (InpCrkLZ1 <= 0 || InpCrkLZ2 <= 0 || InpCrkLZ1N < 1 || InpCrkLZ2N < 1 || InpCrkLGrow < 0 || InpCrkLGrowX < 1))
   { Print("Crooks L: the part steps must be above 0, the most parts 1 or more, the growth 0 or more and its limit 1 x or more."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(SizeProfit() && ExitR() <= 0) { Print("Size by Profit: the final TP must be above 0 R."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpLadder != LAD_OFF && InpLadT <= 0) { Print("Profit ladder: the profit target must be above 0."_mq); return INIT_PARAMETERS_INCORRECT; }
   if(InpLadder != LAD_OFF && !LadFam()) Print("Profit ladder: it works with Crooks F, G, H, I or J only; with this loss recovery it is off."_mq);
   // warm up the engine on history (no orders): it ends in the same state as the TradingView engine would
   int bars = Bars(_Symbol, _Period);
   int look = (int)MathMax(MathMax(gpStructLen, gpBrkLen + 1), MathMax(gpMomLen + 1, gpStopLen)) + 2;
   int need = look + gpAtrLen + 10;
   if(bars < need) { Print("Not enough chart history yet ("_mq, bars, " bars, need "_mq, need, "); scroll the chart back or load more history, then attach the EA again."_mq); return INIT_FAILED; }
   int start = (int)MathMin(InpWarmBars, bars - look - 1);
   if(gRestored && gSvLast > 0)                         // reach back to the saved bar, so every day since then is counted (at most 100,000 bars)
   {
      int sh = iBarShift(_Symbol, _Period, gSvLast, false);
      if(sh < 0 || sh > start) start = (int)MathMin(sh < 0 ? 100000 : MathMin(sh, 100000), bars - look - 1);
   }
   if(gpVwapAnchor != VW_SESSION)                       // v4.8: a Week / Month VWAP needs its whole current week / month (at most 100,000 bars)
   {
      datetime vwT = iTime(_Symbol, _Period, 1);
      MqlDateTime vwM; TimeToStruct(vwT, vwM);
      datetime vwA = gpVwapAnchor == VW_MONTH ? StringToTime(StringFormat("%04d.%02d.01 00:00"_mq, mq_dot(vwM).year, mq_dot(vwM).mon))
                                             : (datetime)((((mql_long)vwT + 3 * 86400) / (7 * 86400)) * (7 * 86400) - 3 * 86400);   // Monday 00:00 (server)
      int vwS = iBarShift(_Symbol, _Period, vwA, false), vwL = (int)MathMin(100000, bars - look - 1);
      int vwN = vwS >= 0 ? vwS + 1 : vwL;
      if(vwN > start) start = (int)MathMin(vwN, vwL);
      if(iTime(_Symbol, _Period, bars - 1) > vwA || vwN > vwL)
         Print("VWAP "_mq, gpVwapAnchor == VW_MONTH ? "Month"_mq : "Week"_mq, ": the chart history does not reach back to "_mq, TimeToString(vwA, TIME_DATE),
               ", so the VWAP starts later than TradingView's; scroll the chart back to load more history, then attach the EA again."_mq);
   }
   gVwN = (int)MathMax(50, MathMin(20000, InpVwapBars));   // the VWAP line: the last gVwN bars
   gVwCut = iTime(_Symbol, _Period, (int)MathMin(gVwN, bars - 1));
   gLive = false;
   for(int s = start; s >= 1; s--)
   {
      bool offBar = gRestored && gSvLast > 0 && iTime(_Symbol, _Period, s) > gSvLast;   // the bars since the saved state count like bars missed in a disconnect
      if(offBar) EngStep(s); else ProcessBar(s);
      // v4.4: the saved trade's setup is re-linked when the engine arms it again (its arm bar, direction and entry): its fill, stop moves and
      // exit on the bars since the saved state then reach the trade (gMiss*), like after a disconnect
      if(gRestored && exArmT > 0 && exState != 0 && !exHg && evArm && iTime(_Symbol, _Period, s) == exArmT && (st > 0) == exL &&
         (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5) && !TfHold()) exArm = armBar;   // not on another timeframe
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
   if(gBrokerPend) Print("Waiting for the connection to the trade server before checking positions and deals."_mq);
   else BrokerStart();
   gStateTxt = StateText(false);
   UpdateTable();
   if(gCanDraw) ChartRedraw(0);                          // the VWAP line and markings show at once (also with the market closed)
   StateSave(true);                                      // restart memory: the state after this start
   OtherEAs();
   gInitDone = true;
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   // restart memory off, new inputs or another timeframe: MT5 keeps the money management, but the start that follows skips earlier deals,
   // so a trade that has just closed is booked now
   if(!gPersist && (reason == REASON_PARAMETERS || reason == REASON_CHARTCHANGE) && exState != 0) BookBrokerDeals();
   LockFree();
   bool gone = reason == REASON_REMOVE || reason == REASON_CHARTCLOSE || reason == REASON_INITFAILED || reason == REASON_PROGRAM || reason == REASON_TEMPLATE;
   if(gone && gTfTrade > 0 && MQLInfoInteger(MQL_TESTER) == 0) { GlobalVariableDel(SvExtra("tf"_mq)); GlobalVariableDel(SvExtra("tfp"_mq)); }   // left the chart: attach it again on any timeframe
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

#line 2990 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/sim/EA_sim51.mq5"
typedef void (*mq_t_OnTick)();
static mq_t_OnTick mq_chk_OnTick = &OnTick;
#line 2968 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/sim/EA_sim51.mq5"
typedef void (*mq_t_OnDeinit)(const int);
static mq_t_OnDeinit mq_chk_OnDeinit = &OnDeinit;
#line 2982 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/sim/EA_sim51.mq5"
typedef void (*mq_t_OnChartEvent)(const int, const mql_long&, const double&, const string&);
static mq_t_OnChartEvent mq_chk_OnChartEvent = &OnChartEvent;
#line 1 "<rt-wrapper>"
extern "C" int rt_SetInput(const char* name, double v)
{
   if(__builtin_strcmp(name, "InpPreset") == 0) { InpPreset = (ENUM_PRESET)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpAddMine") == 0) { InpAddMine = (v != 0); return 1; }
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
   if(__builtin_strcmp(name, "InpBeOn") == 0) { InpBeOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpBeR") == 0) { InpBeR = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpSvOn") == 0) { InpSvOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpSvR") == 0) { InpSvR = (double)v; return 1; }
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
   if(__builtin_strcmp(name, "InpSizeMode") == 0) { InpSizeMode = (ENUM_SIZE_MODE)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpSizeBy") == 0) { InpSizeBy = (ENUM_SIZE_BY)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpBaseRisk") == 0) { InpBaseRisk = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpBaseLots") == 0) { InpBaseLots = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpEqPct") == 0) { InpEqPct = (double)v; return 1; }
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
   if(__builtin_strcmp(name, "InpMemFresh") == 0) { InpMemFresh = (v != 0); return 1; }
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
   if(__builtin_strcmp(name, "InpCrkELot") == 0) { InpCrkELot = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkFK") == 0) { InpCrkFK = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkGX") == 0) { InpCrkGX = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkHPct") == 0) { InpCrkHPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkJX") == 0) { InpCrkJX = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkKMode") == 0) { InpCrkKMode = (ENUM_CRK_K)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkKLots") == 0) { InpCrkKLots = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkKUsd") == 0) { InpCrkKUsd = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkKPct") == 0) { InpCrkKPct = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkLZ1") == 0) { InpCrkLZ1 = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkLZ1N") == 0) { InpCrkLZ1N = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkLZ2") == 0) { InpCrkLZ2 = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkLZ2N") == 0) { InpCrkLZ2N = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkLGrow") == 0) { InpCrkLGrow = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpCrkLGrowX") == 0) { InpCrkLGrowX = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpLadder") == 0) { InpLadder = (ENUM_LADDER)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpLadT") == 0) { InpLadT = (double)v; return 1; }
   if(__builtin_strcmp(name, "InpParN") == 0) { InpParN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDelayN") == 0) { InpDelayN = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDraw") == 0) { InpDraw = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpMaxDrawn") == 0) { InpMaxDrawn = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpColTarget") == 0) { InpColTarget = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpColStop") == 0) { InpColStop = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpColEntry") == 0) { InpColEntry = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpVwapShow") == 0) { InpVwapShow = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpVwapColor") == 0) { InpVwapColor = (color)v; return 1; }
   if(__builtin_strcmp(name, "InpVwapWidth") == 0) { InpVwapWidth = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpVwapBars") == 0) { InpVwapBars = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpShowTable") == 0) { InpShowTable = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpTablePos") == 0) { InpTablePos = (ENUM_TBL_POS)(int)v; return 1; }
   if(__builtin_strcmp(name, "InpTableFont") == 0) { InpTableFont = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpMagic") == 0) { InpMagic = (mql_long)v; return 1; }
   if(__builtin_strcmp(name, "InpWarmBars") == 0) { InpWarmBars = (int)v; return 1; }
   return 0;
}
struct RtEv { int fill, fillL, exit, win; long long bi, armBar; double lim, stp, stp0, res; };
extern "C" void rt_reset() { PresetApply(); ResetEngine(); }
extern "C" int rt_look() { return (int)MathMax(MathMax(gpStructLen, gpBrkLen + 1), MathMax(gpMomLen + 1, gpStopLen)) + 2; }
extern "C" void rt_period(int p) { _Period = (ENUM_TIMEFRAMES)p; }
extern "C" void rt_step(int s, RtEv* e) { ProcessBar(s); e->fill = evFill; e->fillL = evFillL; e->exit = evExit; e->win = evWin; e->bi = bi; e->armBar = armBar; e->lim = lim; e->stp = stp; e->stp0 = stp0; e->res = evRes; }
extern "C" void rt_stats(double* o) { o[0] = totW; o[1] = totL; o[2] = totR; o[3] = tpHitN[0]; o[4] = tpHitN[1]; o[5] = tpHitN[2]; o[6] = tpHitN[3]; o[7] = beN; o[8] = lkN; o[9] = ghW; o[10] = ghL; o[11] = ghR; }

#line 1 "<sim-wrapper>"
extern "C" int sim_init() { return OnInit(); }
extern "C" void sim_ontick() { OnTick(); }
extern "C" void sim_deinit(int r) { OnDeinit(r); }
extern "C" int sim_exstate() { return exState; }
extern "C" double sim_crkl() { return crkL; }
extern "C" double sim_vwap() { return ArraySize(vwHist) > 0 ? vwHist[0] : 0.0; }
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
   trTrig = 0;
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
   svN = 0;
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
   evSalv = false;
   evTrig = 0;
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
   gBase = 0;
   exBase = 0;
   gBaseWin = 0;
   exBaseWin = 0;
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
   gpStructLen = 0;
   gpBrkLen = 0;
   gpEntryLen = 0;
   gpRetestBars = 0;
   gpDispAtr = 0;
   gpBodyPct = 0;
   gpClosePct = 0;
   gpMomLen = 0;
   gpMomAtr = 0;
   gpCmoMin = 0;
   gpStopAtr = 0;
   gpStopLen = 0;
   gpStopBufAtr = 0;
   gpHalfStop = false;
   gpHalfStopAtr = 0;
   gpBiasNet = 0;
   gpImpBody = 0;
   gpHalfOpenOut = false;
   gpHalfStrict = false;
   gpHalfCap = false;
   gpCooldown = 0;
   gpMaxFills = 0;
   gpDayStopR = 0;
   gpFillBarStopR = false;
   gpLegReset = false;
   gpAtrLen = 0;
   gpVwapFilter = false;
   gpSlopeBars = 0;
   gpSlopeCross = false;
   gpMinOpenBars = 0;
   gpSkipSunday = false;
   gpDeepOn = false;
   gpDeepFar = 0;
   gpAllowLong = false;
   gpAllowShort = false;
   gpEntryPct = 0;
   gpTp1R = 0;
   gpTp2R = 0;
   gpTp3R = 0;
   gpTp4R = 0;
   gpMv1On = false;
   gpMv1R = 0;
   gpMv2On = false;
   gpMv2R = 0;
   gpMv3On = false;
   gpMv3R = 0;
   gpNoChase = false;
   gpNoChaseSig = 0;
   gpLossBlock = false;
   gpMinVwOn = false;
   gpMinVwAtr = 0;
   gpMaxVwOn = false;
   gpMaxVwDist = 0;
   gpStopVwOn = false;
   gpStopVwBuf = 0;
   gpTouchVwOn = false;
   gpTouchVwN = 0;
   gpEntVwOn = false;
   gpEntVwAtr = 0;
   gpChopOn = false;
   gpChopMax = 0;
   gpEmaOn = false;
   gpEmaMax = 0;
   gpDayOn = false;
   gpHoursOn = false;
   gpStartH = 0;
   gpStartM = 0;
   gpEndH = 0;
   gpEndM = 0;
   gpKzOn = false;
   gpKzAsia = false;
   gpKzLon = false;
   gpKzNy = false;
   gpKzLc = false;
   gpKzAuto = false;
   gpKzShift = 0;
   gpDNewsOn = false;
   gpN1On = false;
   gpN2On = false;
   gpN3On = false;
   gpN4On = false;
   gpN5On = false;
   gpP1 = 0;
   gpP2 = 0;
   gpP3 = 0;
   gpHrIst = false;
   gpTfOk = true;
   gpTf = 0;
   gNet0 = 0;
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
   crkPk = 0;
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
   gTzMode = SRV_EET;
   gTzFix = 2.0;
   gTzDet = -99;
   gTzWarned = false;
   gCloseWhy = "";
   gCloseId = 0;
   for(int q_ = 0; q_ < 8; q_++) gClosedIds[q_] = 0;
   gClosedN = 0;
   gLastClose = "-";
   gLastCloseOut = false;
   exArmT = 0;
   exLim = 0;
   for(int q_ = 0; q_ < 3; q_++) exTpL[q_] = 0;
   gOurFill = false;
   gOurExit = false;
   gOurWin = false;
   gOurMove = false;
   gMissFill = false;
   gMissExit = false;
   gMissWin = false;
   gMissMove = false;
   gLockN = "";
   gLockV = 0;
   gTfTrade = 0;
   gTakenT = 0;
   gVwPrevT = 0;
   gVwCut = 0;
   gVwPrev = 0;
   gVwN = 1500;
   gExitRetry = false;
   gExitWhy = "";
   gExitSeen = false;
   gGoneWait = false;
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
