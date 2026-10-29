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
   REC_CRB   = 19  // Crooks B (Crooks A with the loss split over N trades)
};

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
 bool   InpHalfCap      = false; // Half stop never wider than the normal stop (optional)
 int    InpCooldown     = 1;     // Cooldown after exit (bars)
 int    InpMaxFills     = 5;     // Max fills per day
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
 double InpEntryPct     = 50.0;  // Custom % (0 = close, 50 = mid, 100 = low/high)

  
 double InpTp1R = 0.6;  // TP1 (R)
 double InpTp2R = 1.0;  // TP2 (R)
 double InpTp3R = 1.5;  // TP3 (R)
 double InpTp4R = 2.0;  // TP4 (R)
 ENUM_EXIT_AT InpExitAt = EXIT_TP4; // Final exit at
 bool   InpMv1On = false; // When TP1 hits, move stop
 double InpMv1R  = 0.0;   //   ...to (R, 0 = breakeven)
 bool   InpMv2On = false; // When TP2 hits, move stop (breakeven at +1R: on, 0)
 double InpMv2R  = 0.6;   //   ...to (R)
 bool   InpMv3On = false; // When TP3 hits, move stop
 double InpMv3R  = 1.0;   //   ...to (R)

  
 bool   InpNoChase    = false; // Don't chase: skip signals beyond N sigma from VWAP
 double InpNoChaseSig = 2.4;   //   sigma from VWAP
 bool   InpLossBlock  = false; // After a loss, no same-direction trade until a win
 bool   InpChopOn     = false; // Skip choppy sessions (too many VWAP crosses)
 double InpChopMax    = 12.0;  //   max VWAP crosses per 100 bars
 bool   InpEmaOn      = false; // Skip when the 1h EMA20 moved too fast (natural gas: worse)
 double InpEmaMax     = 1.65;  //   max 1h EMA20 move in 3 hours (x ATR)
 bool   InpMinVwOn    = false; // Skip signals too close to VWAP (min distance)
 double InpMinVwAtr   = 1.0;   //   min distance of the signal close from VWAP (x ATR)

  
enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // Auto: GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1 }; // Fixed: the GMT offset below
 ENUM_SRV_TZ InpServerTz = SRV_NYCLOSE; // Broker server clock
 double InpServerGMT = 2.0;   // Broker server time zone if fixed (GMT +h; check Market Watch time)
 double InpUserGMT   = 5.5;   // Your time zone (GMT +h; India = 5.5)
 bool   InpDayOn     = false; // Trade only on the ticked days
 bool   InpMon       = true;  //   Monday
 bool   InpTue       = true;  //   Tuesday
 bool   InpWed       = true;  //   Wednesday
 bool   InpThu       = true;  //   Thursday
 bool   InpFri       = true;  //   Friday
 bool   InpSat       = true;  //   Saturday
 bool   InpSun       = true;  //   Sunday
 bool   InpHoursOn   = false; // Trade only between
 int    InpStartH    = 6;     //   start hour
 int    InpStartM    = 0;     //   start minute
 int    InpEndH      = 23;    //   end hour
 int    InpEndM      = 0;     //   end minute
enum ENUM_KZ_SHIFT { KZ_M2 = -2,  // -2 hours
                     KZ_M1 = -1,  // -1 hour
                     KZ_0  = 0,   // 0 (as listed)
                     KZ_P1 = 1,   // +1 hour
                     KZ_P2 = 2 }; // +2 hours
 bool   InpKzOn      = false; // Trade only in kill zones (Indian time, IST)
 bool   InpKzAsia    = true;  //   Asia 05:30-09:30 IST
 bool   InpKzLon     = true;  //   London 11:30-14:30 IST
 bool   InpKzNy      = true;  //   New York 16:30-19:30 IST
 bool   InpKzLc      = true;  //   London close 19:30-21:30 IST
 ENUM_KZ_SHIFT InpKzShift = KZ_0; //   shift all kill zones (daylight saving)

//--- EXECUTION inputs (EA only)
  
 double InpP1   = 0.0;  // Close % at TP1 (0 = no partial)
 double InpP2   = 0.0;  // Close % at TP2
 double InpP3   = 0.0;  // Close % at TP3

  
 double InpBaseRisk = 50.0;   // Base risk per trade (account currency)
 bool   InpCapOn    = false;  // Hard cap: max loss per trade
 double InpHardCap  = 500.0;  // Hard cap amount
 ENUM_CAP_ACTION InpCapAction = CAP_CLAMP; // If the risk would exceed the cap
 double InpLeverage = 100.0;  // Leverage cap 1:x (0 = broker margin only)
 double InpLotStep  = 0.0;    // Lot step (0 = broker's volume step)

  
 double InpCommLot  = 0.0;    // Commission per lot, round trip (sizing / earn-back)
 bool   InpEarnBack = false;  // Extend targets to earn back commission + spread
 bool   InpBidChart = true;   // Match bid-chart levels (shift buy-side orders by the spread)

  
 bool InpLStopOn = false; // Stop for the day after N losses in a row
 int  InpLStopN  = 2;     //   N losses
 bool InpWStopOn = false; // Stop for the day after N wins in a row
 int  InpWStopN  = 3;     //   N wins
 bool InpPauseOn = false; // Pause after N losses in a row
 int  InpPauseN  = 3;     //   N losses
 int  InpPauseDays = 1;   //   Days to pause (1-3)

  
 bool   InpFcOn      = false; // Force-close open trades daily at
 int    InpFcH       = 2;     //   hour
 int    InpFcM       = 0;     //   minute
 bool   InpWeekendOn = false; // Close open trades when Saturday starts
 int    InpNewsPre   = 60;    // No new trades before news (minutes)
 bool   InpDNewsOn   = false; // Daily news window
 int    InpDNewsH    = 18;    //   start hour
 int    InpDNewsM    = 0;     //   start minute
 int    InpDNewsDur  = 60;    //   length (minutes)
 bool     InpN1On = false;        // News 1
 datetime InpN1T  = ((datetime)1767290400LL); //   date and time (your time zone)
 int      InpN1Dur = 60;          //   length (minutes)
 bool     InpN2On = false;        // News 2
 datetime InpN2T  = ((datetime)1767290400LL); //   date and time
 int      InpN2Dur = 60;          //   length (minutes)
 bool     InpN3On = false;        // News 3
 datetime InpN3T  = ((datetime)1767290400LL); //   date and time
 int      InpN3Dur = 60;          //   length (minutes)
 bool     InpN4On = false;        // News 4
 datetime InpN4T  = ((datetime)1767290400LL); //   date and time
 int      InpN4Dur = 60;          //   length (minutes)
 bool     InpN5On = false;        // News 5
 datetime InpN5T  = ((datetime)1767290400LL); //   date and time
 int      InpN5Dur = 60;          //   length (minutes)

  
 ENUM_REC InpRec    = REC_OFF; // Loss recovery
 int    InpRecN     = 3;      // N trades (Over N / Delayed)
 double InpRecPct   = 50.0;   // % of losses (% mode)
 double InpRecMult  = 2.0;    // Multiplier (Martingale / Grand)
 double InpRecStep  = 25.0;   // Step amount (Step-up)
 int    InpCSplit   = 3;      // Rule C / Crooks B: split the loss over this many trades
 bool   InpCrkT1    = true;   // Crooks at exit TP1: bank the loss at TP1 with half, rest to TP2
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
int      trSkip = 0;               // why the setup is a ghost: 1 too far from VWAP, 2 choppy VWAP session, 3 1h EMA20 too fast, 4 too close to VWAP
int      totW = 0, totL = 0; double totR = 0;
string   lastRes = "-"_mq;
double   bestPx = 0;               // best price after the fill (the fill bar and stop bars add nothing)
int      ghW = 0, ghL = 0; double ghR = 0;   // results the skipped (invisible) trades would have had
// optional filters: VWAP crosses of this VWAP period; 1-hour (UTC) candles built from the bars and their EMA20
int      vxSide = 0, vxN = 0;
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
bool     gDayPend = false;         // the day changed on a caught-up bar
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
bool     exT1 = false, exT1Half = false, exT1Be = false;   // Crooks TP1 rule: this trade, its TP1 half is booked, the rest's stop is at the entry
double   exT1Stop = 0, exT1Tp1 = 0, exT1Tp2 = 0;              // its stop and its own TP1 / TP2 (the engine's levels change with its next setup)
double   totalNet = 0; int exW = 0, exLn = 0;

//--- helpers ----------------------------------------------------------
double Pt()        { return SymbolInfoDouble(_Symbol, SYMBOL_POINT); }
double TickSize()  { double t = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE); return t > 0 ? t : Pt(); }
double FloorTick(double p) { double ts = TickSize(); return NormalizeDouble(MathFloor(p / ts + 1e-6) * ts, _Digits); }
double CeilTick(double p)  { double ts = TickSize(); return NormalizeDouble(MathCeil(p / ts - 1e-6) * ts, _Digits); }
double RoundTick(double p) { double ts = TickSize(); return NormalizeDouble(MathRound(p / ts) * ts, _Digits); }
int NthSunday(int y, int mon, int n)
{
   MqlDateTime d; ZeroMemory(d); mq_dot(d).year = y; mq_dot(d).mon = mon; mq_dot(d).day = 1;
   MqlDateTime f; TimeToStruct(StructToTime(d), f);
   return 1 + (7 - mq_dot(f).day_of_week) % 7 + 7 * (n - 1);
}
double SrvGMT(datetime server)
{
   if(InpServerTz == SRV_FIXED) return InpServerGMT;
   MqlDateTime d; TimeToStruct(server, d);
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
// kill zone in Indian minutes of the day, moved by the shift input; the end is exclusive
bool     InKz(int m, int startM, int endM)
{
   int sh = (int)InpKzShift * 60;
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
      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) closed = true;
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
   int kzM = MinOfDay(UtcTime(t) + 19800);   // Indian Standard Time = UTC + 5:30
   gKzOk = !InpKzOn || (InpKzAsia && InKz(kzM, 330, 570)) || (InpKzLon && InKz(kzM, 690, 870)) || (InpKzNy && InKz(kzM, 990, 1170)) || (InpKzLc && InKz(kzM, 1170, 1290));
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
         bool ghost = zNo || chopNo || emaNo || nearNo;
         if(MathAbs(st) == 1 && !trGhost) evCancel = 2;
         st = isL ? 1 : -1; armBar = bi; lim = entry; stp = stop; stp0 = stop; trRisk = risk; trHalf = half; trGhost = ghost;
         trSkip = zNo ? 1 : (chopNo ? 2 : (emaNo ? 3 : (nearNo ? 4 : 0)));
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

//--- Crooks: the next trade is a recovery trade (trades 3, 5, 7 ... of the cycle)
bool CrkRecNext() { return (InpRec == REC_CRA || InpRec == REC_CRB) && crkN >= 2 && crkN % 2 == 0; }
//--- Crooks TP1 rule (exit at TP1, recovery trades): half of a double position banks the recovery amount at TP1, the rest runs to TP2.
//--- Stop distance (bid chart) where a stop-out loses exactly that amount: TP1 / 2 - 1.5 x costs, on the tick grid toward the entry; 0 = not possible
double CrkT1Dist()
{
   if(!InpCrkT1 || InpExitAt != EXIT_TP1 || !CrkRecNext()) return 0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0) return 0;
   double spr = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
   double d = MathFloor((InpTp1R * trRisk / 2.0 - 1.5 * (spr + InpCommLot * ts / tv)) / ts + 1e-9) * ts;
   return d >= ts ? d : 0;
}

//--- risk $ for the next trade (loss recovery + hard cap) -------------------
double NextRisk(double exitR)
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
      {
         double x = crkL / (InpRec == REC_CRB ? InpCSplit : 1);
         r = !CrkRecNext() ? base : CrkT1Dist() > 0 ? MathMax(base, x) : exitR > 0 ? MathMax(base, x / exitR) : base;   // TP1 rule: a stop-out loses x
         break;
      }
      default:        r = base;
   }
   if(InpCapOn && r > InpHardCap)
   {
      if(InpCapAction == CAP_STOP) capStop = true;
      else if(InpCapAction == CAP_RESET)
      {
         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; crkL = 0; crkN = 0;
         r = MathMin(baseC, InpHardCap);
      }
      else r = InpHardCap;
   }
   return r;
}

//--- lots for a $ risk and a stop distance --------------------------------
double LotsFor(double riskAmt, double stopDist, double entry, bool isL)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double spr = SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double perLot = (stopDist + MathMax(spr, 0)) / ts * tv + InpCommLot;   // stop-out loss per lot incl. spread and commission
   double v = riskAmt / perLot;
   double notionalPerLot = entry / ts * tv;
   if(InpLeverage > 0 && notionalPerLot > 0) v = MathMin(v, AccountInfoDouble(ACCOUNT_EQUITY) * InpLeverage / notionalPerLot);
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   v = MathFloor(v / step + 1e-9) * step;
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
      int cur = MinOfDay(ut), prv = MinOfDay(utPrev), s0 = InpDNewsH * 60 + InpDNewsM, e0 = s0 + InpDNewsDur;
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

double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
void SetExits(bool withTarget)
{
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   double sl = StopPx(exL), tp = withTarget ? TgtPx(exL, tF) : 0;
   if(exT1) { sl = exT1Half ? NormalizeDouble(op, _Digits) : exT1Stop; tp = withTarget ? TgtPx(exL, exT1Tp2) : 0; }   // Crooks TP1 rule: rest to TP2, at the entry after TP1
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double minD = MinDist();
   // price is already through the engine's stop or target: the engine exits on this bar, so exit now
   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp))) { CloseAll(); return; }
   if(exL) { if(bid - sl < minD) sl = FloorTick(bid - minD); if(tp > 0 && tp - bid < minD) tp = CeilTick(bid + minD); }
   else    { if(sl - ask < minD) sl = CeilTick(ask + minD); if(tp > 0 && ask - tp < minD) tp = FloorTick(ask - minD); }
   bool same = MathAbs(PositionGetDouble(POSITION_SL) - sl) < TickSize() * 0.5 && MathAbs(PositionGetDouble(POSITION_TP) - tp) < TickSize() * 0.5;
   if(same || mq_dot(trade).PositionModify(tk, sl, tp)) { if(exT1 && exT1Half) exT1Be = true; }
   else Print("Stop/target update rejected ("_mq, mq_dot(trade).ResultRetcodeDescription(), "): SL "_mq, DoubleToString(sl, _Digits), " TP "_mq, DoubleToString(tp, _Digits));
}

//--- Crooks TP1 rule: close half at market (rounded UP to the lot step, so at least half banks the recovery amount); the rest's stop then moves to the entry
void T1Half(ulong tk, double vol)
{
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double cv = MathCeil(exLots * 0.5 / step - 1e-9) * step;
   if(cv >= vmin && vol - cv >= vmin - 1e-9)
   {
      if(mq_dot(trade).PositionClosePartial(tk, NormalizeDouble(cv, 8))) { exT1Half = true; SetExits(true); }
      else Print("TP1 partial close failed ("_mq, mq_dot(trade).ResultRetcodeDescription(), "), retrying"_mq);
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
   string why = trSkip == 1 ? "TOO FAR FROM VWAP"_mq : (trSkip == 2 ? "CHOPPY VWAP SESSION"_mq : (trSkip == 3 ? "1H EMA20 TOO FAST"_mq : "TOO CLOSE TO VWAP"_mq));
   string s = st != 0 && trGhost ? "SKIPPED ("_mq + why + ")"_mq : st == 2 ? "LONG ACTIVE"_mq : st == -2 ? "SHORT ACTIVE"_mq : st == 1 ? "BUY LIMIT ARMED"_mq : st == -1 ? "SELL LIMIT ARMED"_mq :
              capStop ? "HARD CAP: STOPPED"_mq : newsBlk ? "NEWS WINDOW"_mq : paused ? "PAUSED"_mq : dayBlock ? "STREAK STOP TODAY"_mq :
              !gDayOk ? "DAY SWITCHED OFF"_mq : !gHourOk ? "OUTSIDE HOURS"_mq : !gKzOk ? "OUTSIDE KILL ZONES"_mq : "SCANNING"_mq;
   string ex = exState == 2 ? " (in trade)"_mq : (exState == 1 ? (gVirt ? " (waiting for the level)"_mq : " (order working)"_mq) : ""_mq);
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
   bool   isC = InpRec == REC_C || InpRec == REC_CS, isK = InpRec == REC_CRA || InpRec == REC_CRB;
   string kTxt = DoubleToString(crkL, 2) + " | trade "_mq + IntegerToString(crkN + 1) + ((exState != 0 ? crkRec : CrkRecNext()) ? " recovery"_mq : " base"_mq) + (InpRec == REC_CRB ? " | split "_mq + IntegerToString(InpCSplit) : ""_mq)
                 + (exState != 0 && exT1 ? (exT1Half ? " | TP1 booked, rest to TP2"_mq : " | TP1 rule, stop "_mq + DoubleToString(exT1Stop, _Digits)) : ""_mq);
   string rec = InpRec == REC_OFF ? "off"_mq : (isC ? DoubleToString(carried, 2) + " | split "_mq + IntegerToString(InpCSplit) : isK ? kTxt : DoubleToString(recPool, 2) + " | "_mq + IntegerToString(recLosses) + " losses in a row"_mq);
   TblAdd("AUCTION RETEST"_mq, "EA v3.5"_mq, white, ((color)14061373));
   TblAdd("STATE"_mq, gStateTxt, white, act ? (st == 2 ? ((color)5287756) : ((color)4536050)) : (armed ? ((color)39167) : ((color)7037021)));
   TblAdd("ENTRY / STOP"_mq, has ? DoubleToString(lim, _Digits) + " / "_mq + DoubleToString(stp, _Digits) + (trHalf ? " (half stop)"_mq : ""_mq) : "-"_mq, white, cell);
   TblAdd("TP1 | TP2 | TP3 | TP4 (exit TP"_mq + IntegerToString(xk) + ")"_mq, tps, posC, cell);
   TblAdd("RISK | LOTS"_mq, exState != 0 ? DoubleToString(exRiskAmt, 2) + " | "_mq + DoubleToString(exLots, 2) : "base "_mq + DoubleToString(InpBaseRisk, 2), white, cell);
   TblAdd(isC ? "LOSSES CARRIED"_mq : isK ? "CROOKS: LOSS TO WIN BACK"_mq : "RECOVERY POOL"_mq, rec, (isC ? carried : isK ? crkL : recPool) > 0 ? negC : white, cell);
   TblAdd("STREAK W | L"_mq, IntegerToString(winRow) + " | "_mq + IntegerToString(lossRow) + " | total "_mq + IntegerToString(exW) + "W/"_mq + IntegerToString(exLn) + "L"_mq, white, cell);
   TblAdd("DAY P&L | FILLS"_mq, DoubleToString(dayPnl, 2) + " | "_mq + IntegerToString(dayFills) + "/"_mq + IntegerToString(InpMaxFills), dayPnl >= 0 ? posC : negC, cell);
   TblAdd("SIGNALS | TAKEN | SKIPPED"_mq, IntegerToString(sigN) + " | "_mq + IntegerToString(takenN) + " | "_mq + IntegerToString(skipN) + (missN > 0 ? " | missed "_mq + IntegerToString(missN) : ""_mq) + (skipWhy != ""_mq ? " (last: "_mq + skipWhy + ")"_mq : ""_mq), skipN + missN > 0 ? negC : white, cell);
   TblAdd("SIGNAL TRADES | WIN % | R"_mq, AccTxt() + " | last "_mq + lastRes, totR >= 0 ? posC : negC, cell);
   TblAdd("TP HIT"_mq, TpTxt(), posC, cell);
   if(InpMv1On || InpMv2On || InpMv3On) TblAdd("BREAKEVEN"_mq, BeTxt(), white, cell);
   if(InpNoChase || InpChopOn || InpEmaOn || InpMinVwOn) TblAdd("SKIPPED BY FILTERS"_mq, FltTxt(), ghR <= 0 ? posC : negC, cell);
   TblAdd("DATA RANGE"_mq, gFirstT > 0 ? DateTxt(UserTime(gFirstT), true) + " -> "_mq + DateTxt(UserTime(gLastDone), false) + " | "_mq + IntegerToString(bi + 1) + " bars"_mq : "-"_mq, white, cell);
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
   double rAmt = NextRisk(ExitR());
   double t1d = CrkT1Dist();                         // after a cap restart this is 0: trade 1 of a new cycle
   double sd = t1d > 0 ? t1d : trRisk;               // stop distance used for the size
   double v = capStop ? 0 : LotsFor(rAmt, sd, lim, isL);
   bool posNow = HasPosition(pTk, pVol, pOpen);
   skipWhy = (exState != 0 || posNow) ? "still in a trade"_mq : (newsBlk || flatNow) ? "news / force-close"_mq : capStop ? "hard cap stop"_mq : paused ? "paused"_mq : dayBlock ? "streak stop"_mq : v <= 0 ? "size 0"_mq : ""_mq;
   if(skipWhy != ""_mq) { skipN++; return; }
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   double sprNow = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
   exCostPx = InpEarnBack && tv > 0 ? InpCommLot / (tv / ts) + sprNow : 0;
   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((sd + sprNow) / ts * tv + InpCommLot);
   exT1 = t1d > 0; exT1Half = false; exT1Be = false; exT1Stop = exT1 ? T1StopPx(isL, t1d) : 0; exT1Tp1 = t1; exT1Tp2 = t2;
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
   if(InpEntryMode == ENTRY_MARKET)
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
   if(ok) { exState = 1; exArm = armBar; exSynced = false; takenN++; crkRec = CrkRecNext(); }
   else { skipN++; skipWhy = "order rejected"_mq; Print("ARM order failed: "_mq, mq_dot(trade).ResultRetcodeDescription()); }
}

//--- an entry that could not be a pending order (inside the stops distance): enter at market when the level is reached
void VirtualEntry()
{
   if(!gVirt) return;
   if(exState != 1) { gVirt = false; return; }
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
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
   // Crooks: losses add to the loss to win back, wins reduce it; a new cycle when it is all back, less than a cent left (A: also when a recovery trade wins)
   crkL = MathMax(0.0, crkL - exPnl);
   if(crkL < 0.01 || (InpRec == REC_CRA && win && crkRec)) { crkL = 0; crkN = 0; } else crkN++;
   crkRec = false; exT1 = false; exT1Half = false; exT1Be = false;
   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false;
   CancelPending();
}

//=== EXECUTION: runs once per new bar, after the engine processed the bar that just closed ===
void OnNewBar()
{
   ProcessBar(1);
   datetime bt = iTime(_Symbol, _Period, 1);
   datetime ut = UserTime(bt), utPrev = UserTime(gPrevT > 0 ? gPrevT : iTime(_Symbol, _Period, 2));

   if(gNewDay || gDayPend)
   {
      gDayPend = false;
      dayPnl = 0; dayBlock = false;
      paused = pauseLeft > 0; if(pauseLeft > 0) pauseLeft--;
   }

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
      exState = 0; exArm = -1; gVirt = false;
   }
   if(exState == 2 && exMine && MathAbs(st) == 2) exSynced = true;   // the engine is in the EA's setup (filled on this bar or a caught-up bar)
   if(exState == 2 && exMine && (evFill || evMove)) SetExits(true);
   // Crooks TP1 rule: the engine counted TP1 on the bar that just closed but no tick booked the half (missed tick, failed close): book it now
   if(evExit && evWin && exState == 2 && exMine && exT1 && !exT1Half && pos) T1Half(pTk, pVol);
   if(evExit && exState == 2 && exMine && (!InpEarnBack || !evWin) && !(exT1 && (evWin || exT1Half))) CloseAll();   // engine exited: never stay in (earn-back and the Crooks TP1 rule only outlive a win)
   // engine wins: close a broker position the engine is not in (early fill on a spread spike, a fill racing a cancel,
   // or an engine exit on a bar caught up after a disconnect); with earn-back a synced trade may outlive the engine exit
   bool engHolds = (MathAbs(st) == 2 && exSynced && exMine) || (MathAbs(st) == 1 && !exSynced && exState == 2 && exMine);
   if(pos && !exClosed && !evExit && !engHolds && !(InpEarnBack && exSynced) && !(exT1 && exSynced))
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
   if(exState == 1 && (flatNow || newsBlk)) { CancelPending(); exState = 0; exArm = -1; gVirt = false; }

   // 5. take the engine's new setup
   if(evArm) TakeSetup(evArmL, newsBlk, flatNow);

   // on-chart table
   gStateTxt = StateText(newsBlk);
   UpdateTable();
}

//--- partial closes, intrabar (execution only) ---------------------------------
void ManagePartials()
{
   if(exState != 2) return;
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
      // Crooks TP1 rule: half closes at TP1 and banks the whole recovery amount, then the rest's stop moves to the entry (it runs to TP2)
      if(exT1Half) { if(!exT1Be) SetExits(true); return; }          // retry the move to the entry until the broker accepts it
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
   exState = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exPnl = 0; exArm = -1; exSynced = false; gRearm = false; gDrawOn = false; exT1 = false; exT1Half = false; exT1Be = false; exT1Stop = 0; exT1Tp1 = 0; exT1Tp2 = 0;
   sigN = 0; takenN = 0; skipN = 0; missN = 0; skipWhy = ""_mq;
   gVirt = false; gDayPend = false; gPrevT = 0; capStop = false;
   for(int q = 0; q < 3; q++) pDone[q] = false;
   trSkip = 0; lastRes = "-"_mq; bestPx = 0; ghW = 0; ghL = 0; ghR = 0;
   vxSide = 0; vxN = 0; hK = -1; hC = 0; hSum = 0; hNum = 0; ArrayInitialize(hE, 0.0);
   ArrayInitialize(tpHitN, 0); beN = 0; lkN = 0; gFirstT = 0;
   gDrawT = 0; ArrayResize(gDrawn, 0); gStateTxt = "SCANNING"_mq;
}

//--- events -----------------------------------------------------------------
int OnInit()
{
   mq_dot(trade).SetExpertMagicNumber(InpMagic);
   mq_dot(trade).SetDeviationInPoints(50);
   mq_dot(trade).SetTypeFillingBySymbol(_Symbol);
   ResetEngine();
   LabReset();
   // markings and table only where they can be seen (not in non-visual tests or optimisation)
   gCanDraw = MQLInfoInteger(MQL_OPTIMIZATION) == 0 && (MQLInfoInteger(MQL_TESTER) == 0 || MQLInfoInteger(MQL_VISUAL_MODE) != 0);
   ObjectsDeleteAll(0, "ARM_"_mq);
   if(InpTp1R > InpTp2R || InpTp2R > InpTp3R || InpTp3R > InpTp4R) { Print("Targets must be in order: TP1 <= TP2 <= TP3 <= TP4."_mq); return INIT_PARAMETERS_INCORRECT; }
   // warm up the engine on history (no orders): it ends in the same state as the TradingView engine would
   int bars = Bars(_Symbol, _Period);
   int look = (int)MathMax(MathMax(InpStructLen, InpBrkLen + 1), MathMax(InpMomLen + 1, InpStopLen)) + 2;
   int need = look + InpAtrLen + 10;
   if(bars < need) { Print("Not enough chart history yet ("_mq, bars, " bars, need "_mq, need, "); scroll the chart back or load more history, then attach the EA again."_mq); return INIT_FAILED; }
   int start = (int)MathMin(InpWarmBars, bars - look - 1);
   gLive = false;
   for(int s = start; s >= 1; s--) ProcessBar(s);
   gLive = true;
   gLastBarTime = iTime(_Symbol, _Period, 0);
   bool c; NewDealsPnl(c);   // do not count old history
   // restart: adopt this EA's open position if the engine is in the same trade, keep managing it
   ulong tk; double vol, op;
   if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      if((isL && st == 2) || (!isL && st == -2))
      {
         double oldSl = PositionGetDouble(POSITION_SL);
         exState = 2; exL = isL; exLots = vol; exArm = armBar; exSynced = true; for(int q = 0; q < 3; q++) pDone[q] = tpHit >= q + 1; Print("Adopted open position #"_mq, tk, " (engine is in the same trade)."_mq); SetExits(true);
         // never widen the stop of an adopted position: a Crooks TP1-rule position is sized for its tighter stop
         if(oldSl > 0 && (isL ? oldSl > StopPx(isL) : oldSl < StopPx(isL)) && PositionSelectByTicket(tk)) mq_dot(trade).PositionModify(tk, oldSl, PositionGetDouble(POSITION_TP));
      }
      else { exState = 2; Print("Open position #"_mq, tk, " does not match the engine state; it will be closed on the next bar (the engine wins)."_mq); }
   }
   CancelPending();   // a pending order from before the restart has no tracked state
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0;   // re-place the engine's armed setup on the first tick
   gStateTxt = StateText(false);
   UpdateTable();
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason)
{
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
   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 != gLastBarTime)
   {
      gLastBarTime = t0;
      int sh = gLastDone > 0 ? iBarShift(_Symbol, _Period, gLastDone, true) : -1;   // 2 = nothing missed, 1 = bar 1 already processed
      if(sh == 1) { VirtualEntry(); ManagePartials(); return; }
      gPrevT = gLastDone;
      bool caught = false; mql_long biBefore = bi;
      for(int s = sh - 1; s >= 2; s--) { ProcessBar(s); caught = true; if(gNewDay) gDayPend = true; }   // bars missed while offline: engine only
      OnNewBar();
      if(caught && exState == 2 && MathAbs(st) == 2 && exArm == armBar) SetExits(true);   // re-sync stop moves of the missed bars
      if(caught && !evArm && MathAbs(st) == 1 && !trGhost && exState == 0 && armBar > biBefore) gRearm = true;   // armed on a caught-up bar: place it now
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
}
//+------------------------------------------------------------------+

#line 1321 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
typedef void (*mq_t_OnTick)();
static mq_t_OnTick mq_chk_OnTick = &OnTick;
#line 1306 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
typedef void (*mq_t_OnDeinit)(const int);
static mq_t_OnDeinit mq_chk_OnDeinit = &OnDeinit;
#line 1313 "/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec/EA_copy.mq5"
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
   if(__builtin_strcmp(name, "InpFcOn") == 0) { InpFcOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpFcH") == 0) { InpFcH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpFcM") == 0) { InpFcM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpWeekendOn") == 0) { InpWeekendOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpNewsPre") == 0) { InpNewsPre = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsOn") == 0) { InpDNewsOn = (v != 0); return 1; }
   if(__builtin_strcmp(name, "InpDNewsH") == 0) { InpDNewsH = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsM") == 0) { InpDNewsM = (int)v; return 1; }
   if(__builtin_strcmp(name, "InpDNewsDur") == 0) { InpDNewsDur = (int)v; return 1; }
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
extern "C" void rec_init() { LabReset(); }
extern "C" double rec_next(double exitR) { return NextRisk(exitR); }
extern "C" void rec_take() { crkRec = CrkRecNext(); }
extern "C" void rec_part(double np) { exPnl += np; totalNet += np; if(np != 0) carried = MathMax(0.0, carried - np); }
extern "C" void rec_close() { BookClosed(); }
extern "C" int rec_capstop() { return capStop ? 1 : 0; }
// TP1 rule: the engine's stop distance and the spread of the next setup, then whether the EA uses the TP1 rule for it
extern "C" void rec_setup(double risk, double spread) { trRisk = risk; rec_tv = 1.0; rec_bid = 1000.0; rec_ask = 1000.0 + spread; }
extern "C" int rec_t1() { return CrkT1Dist() > 0 ? 1 : 0; }
