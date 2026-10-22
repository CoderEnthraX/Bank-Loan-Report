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
//+------------------------------------------------------------------+
#property copyright "Auction Retest Model"
#property version   "3.00"
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
   REC_OSC   = 17  // Oscar's Grind
};

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
input int    InpCooldown     = 1;     // Cooldown after exit (bars)
input int    InpMaxFills     = 5;     // Max fills per day
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
input double InpEntryPct     = 50.0;  // Custom % (0 = close, 50 = mid, 100 = low/high)

input group "TARGETS, EXIT AND STOP MOVES"
input double InpTp1R = 0.6;  // TP1 (R)
input double InpTp2R = 1.0;  // TP2 (R)
input double InpTp3R = 1.5;  // TP3 (R)
input double InpTp4R = 2.0;  // TP4 (R)
input ENUM_EXIT_AT InpExitAt = EXIT_TP4; // Final exit at
input bool   InpMv1On = false; // When TP1 hits, move stop
input double InpMv1R  = 0.0;   //   ...to (R, 0 = breakeven)
input bool   InpMv2On = false; // When TP2 hits, move stop (breakeven at +1R: on, 0)
input double InpMv2R  = 0.6;   //   ...to (R)
input bool   InpMv3On = false; // When TP3 hits, move stop
input double InpMv3R  = 1.0;   //   ...to (R)

input group "ACCURACY FILTERS (research, off = original)"
input bool   InpNoChase    = false; // Don't chase: skip signals beyond N sigma from VWAP
input double InpNoChaseSig = 2.4;   //   sigma from VWAP
input bool   InpLossBlock  = false; // After a loss, no same-direction trade until a win

input group "DAYS AND HOURS (YOUR time zone)"
enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // Auto: GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1 }; // Fixed: the GMT offset below
input ENUM_SRV_TZ InpServerTz = SRV_NYCLOSE; // Broker server clock
input double InpServerGMT = 2.0;   // Broker server time zone if fixed (GMT +h; check Market Watch time)
input double InpUserGMT   = 5.5;   // Your time zone (GMT +h; India = 5.5)
input bool   InpDayOn     = false; // Trade only on the ticked days
input bool   InpMon       = true;  //   Monday
input bool   InpTue       = true;  //   Tuesday
input bool   InpWed       = true;  //   Wednesday
input bool   InpThu       = true;  //   Thursday
input bool   InpFri       = true;  //   Friday
input bool   InpSat       = true;  //   Saturday
input bool   InpSun       = true;  //   Sunday
input bool   InpHoursOn   = false; // Trade only between
input int    InpStartH    = 6;     //   start hour
input int    InpStartM    = 0;     //   start minute
input int    InpEndH      = 23;    //   end hour
input int    InpEndM      = 0;     //   end minute

//--- EXECUTION inputs (EA only)
input group "PARTIAL PROFITS (EA only)"
input double InpP1   = 0.0;  // Close % at TP1 (0 = no partial)
input double InpP2   = 0.0;  // Close % at TP2
input double InpP3   = 0.0;  // Close % at TP3

input group "RISK AND POSITION SIZE"
input double InpBaseRisk = 50.0;   // Base risk per trade (account currency)
input bool   InpCapOn    = false;  // Hard cap: max loss per trade
input double InpHardCap  = 500.0;  // Hard cap amount
input ENUM_CAP_ACTION InpCapAction = CAP_CLAMP; // If the risk would exceed the cap
input double InpLeverage = 100.0;  // Leverage cap 1:x (0 = broker margin only)
input double InpLotStep  = 0.0;    // Lot step (0 = broker's volume step)

input group "COMMISSION AND BID/ASK"
input double InpCommLot  = 0.0;    // Commission per lot, round trip (sizing / earn-back)
input bool   InpEarnBack = false;  // Extend targets to earn back commission + spread
input bool   InpBidChart = true;   // Match bid-chart levels (shift buy-side orders by the spread)

input group "STREAKS AND PAUSES"
input bool InpLStopOn = false; // Stop for the day after N losses in a row
input int  InpLStopN  = 2;     //   N losses
input bool InpWStopOn = false; // Stop for the day after N wins in a row
input int  InpWStopN  = 3;     //   N wins
input bool InpPauseOn = false; // Pause after N losses in a row
input int  InpPauseN  = 3;     //   N losses
input int  InpPauseDays = 1;   //   Days to pause (1-3)

input group "FORCE-CLOSE, WEEKEND AND NEWS (YOUR time zone)"
input bool   InpFcOn      = false; // Force-close open trades daily at
input int    InpFcH       = 2;     //   hour
input int    InpFcM       = 0;     //   minute
input bool   InpWeekendOn = false; // Close open trades when Saturday starts
input int    InpNewsPre   = 60;    // No new trades before news (minutes)
input bool   InpDNewsOn   = false; // Daily news window
input int    InpDNewsH    = 18;    //   start hour
input int    InpDNewsM    = 0;     //   start minute
input int    InpDNewsDur  = 60;    //   length (minutes)
input bool     InpN1On = false;        // News 1
input datetime InpN1T  = D'2026.01.01 18:00'; //   date and time (your time zone)
input int      InpN1Dur = 60;          //   length (minutes)
input bool     InpN2On = false;        // News 2
input datetime InpN2T  = D'2026.01.01 18:00'; //   date and time
input int      InpN2Dur = 60;          //   length (minutes)
input bool     InpN3On = false;        // News 3
input datetime InpN3T  = D'2026.01.01 18:00'; //   date and time
input int      InpN3Dur = 60;          //   length (minutes)
input bool     InpN4On = false;        // News 4
input datetime InpN4T  = D'2026.01.01 18:00'; //   date and time
input int      InpN4Dur = 60;          //   length (minutes)
input bool     InpN5On = false;        // News 5
input datetime InpN5T  = D'2026.01.01 18:00'; //   date and time
input int      InpN5Dur = 60;          //   length (minutes)

input group "LOSS RECOVERY"
input ENUM_REC InpRec    = REC_OFF; // Loss recovery
input int    InpRecN     = 3;      // N trades (Over N / Delayed)
input double InpRecPct   = 50.0;   // % of losses (% mode)
input double InpRecMult  = 2.0;    // Multiplier (Martingale / Grand)
input double InpRecStep  = 25.0;   // Step amount (Step-up)
input int    InpCSplit   = 3;      // Rule C: split the loss over this many trades
input int    InpParN     = 3;      // Paroli: wins before reset
input int    InpDelayN   = 2;      // Delayed: losses before recovery starts
input double InpEqPct    = 1.0;    // % of equity (% mode)

input group "GENERAL"
input long   InpMagic    = 240611; // Magic number
input int    InpWarmBars = 3000;   // Bars used to warm up the engine (VWAP / ATR / counters / state)
input bool   InpDraw     = true;   // Draw trade boxes

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
int      totW = 0, totL = 0; double totR = 0;
// events of the last processed bar (shown setups / trades only)
bool     evArm, evArmL, evFill, evFillL, evExit, evWin, evMove, evTp; double evRes; int evCancel; // 0 none, 1 expired, 2 replaced
bool     gNewDay = false, gDayOk = true, gHourOk = true;
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
bool     gDayPend = false;         // the day changed on a caught-up bar
datetime gPrevT = 0;               // open time of the bar before the one OnNewBar handles (catch-up aware)
bool     pDone[3];
ulong    lastDeal = 0;
int      sigN = 0, takenN = 0, skipN = 0, missN = 0; string skipWhy = "";
datetime gDrawT = 0; bool gDrawOn = false;
double   dayPnl = 0; int lossRow = 0, winRow = 0; bool dayBlock = false; int pauseLeft = 0; bool paused = false;
double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;
double   labSeq[]; int parWins = 0; int rdUnits = 1; int oscU = 1; double oscP = 0;
double   totalNet = 0; int exW = 0, exLn = 0;

//--- helpers ----------------------------------------------------------
double Pt()        { return SymbolInfoDouble(_Symbol, SYMBOL_POINT); }
double TickSize()  { double t = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE); return t > 0 ? t : Pt(); }
double FloorTick(double p) { double ts = TickSize(); return NormalizeDouble(MathFloor(p / ts + 1e-6) * ts, _Digits); }
double CeilTick(double p)  { double ts = TickSize(); return NormalizeDouble(MathCeil(p / ts - 1e-6) * ts, _Digits); }
double RoundTick(double p) { double ts = TickSize(); return NormalizeDouble(MathRound(p / ts) * ts, _Digits); }
int NthSunday(int y, int mon, int n)
{
   MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = 1;
   MqlDateTime f; TimeToStruct(StructToTime(d), f);
   return 1 + (7 - f.day_of_week) % 7 + 7 * (n - 1);
}
double SrvGMT(datetime server)
{
   if(InpServerTz == SRV_FIXED) return InpServerGMT;
   MqlDateTime d; TimeToStruct(server, d);
   int ds = NthSunday(d.year, 3, 2), de = NthSunday(d.year, 11, 1);
   bool dst = (d.mon > 3 && d.mon < 11) || (d.mon == 3 && d.day >= ds) || (d.mon == 11 && d.day < de);
   return dst ? 3.0 : 2.0;
}
datetime UserTime(datetime server) { return server - (datetime)(SrvGMT(server) * 3600) + (datetime)(InpUserGMT * 3600); }
datetime UtcTime(datetime server)  { return server - (datetime)(SrvGMT(server) * 3600); }
int      MinOfDay(datetime t) { MqlDateTime d; TimeToStruct(t, d); return d.hour * 60 + d.min; }
int      DowOf(datetime t)    { MqlDateTime d; TimeToStruct(t, d); return d.day_of_week; }   // 0 = Sunday
int      DayKey(datetime t)   { MqlDateTime d; TimeToStruct(t, d); return d.year * 1000 + d.day_of_year; }
double   Hi(int s) { return iHigh(_Symbol, _Period, s); }
double   Lo(int s) { return iLow(_Symbol, _Period, s); }
double   Cl(int s) { return iClose(_Symbol, _Period, s); }
double   Op(int s) { return iOpen(_Symbol, _Period, s); }
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

void CloseAll()
{
   ulong tk; double v, op;
   int guard = 0;
   while(HasPosition(tk, v, op) && guard++ < 5) { if(!trade.PositionClose(tk)) break; }
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
      long entry = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) closed = true;
   }
   lastDeal = maxTk;
   return sum;
}

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
            evExit = true; evWin = win; evRes = res;
         }
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
         if(!trGhost) { evFill = true; evFillL = isL; }
         if(isL ? l <= stp + mt * 0.001 : h >= stp - mt * 0.001)
         {
            if(!trGhost)
            {
               dayRiskR += InpFillBarStopR ? -1.0 : 0.0;
               lossDirBlk = isL ? 1 : -1;
               totR += -1.0; dayR += -1.0; totL++; dayL++;
               evExit = true; evWin = false; evRes = -1.0;
            }
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
   bool canArm = gDayOk && gHourOk && MathAbs(st) != 2 && cooled && dayFills < InpMaxFills && dayOpen && atr > 0;
   bool keepArm = InpRearm == REARM_KEEP && ((st == 1 && bullDisp) || (st == -1 && bearDisp));
   if(canArm && (bullDisp || bearDisp) && !keepArm)
   {
      bool isL = bullDisp; double d = isL ? 1 : -1;
      double entry = InpEntryMode == ENTRY_MODEL ? (isL ? MathMax(bodyMid, entHigh) : MathMin(bodyMid, entLow)) : InpEntryMode == ENTRY_PCT ? c - d * InpEntryPct / 100.0 * rng : c;
      bool half = InpStopMode == STOP_ATR && (isL ? halfL : halfS);
      double cStop = entry - d * InpStopAtr * atr;
      double hStop = isL ? MathMin(entry - InpHalfStopAtr * atr, l) : MathMax(entry + InpHalfStopAtr * atr, h);
      double sStop = isL ? swingLow - InpStopBufAtr * atr : swingHigh + InpStopBufAtr * atr;
      double stop  = InpStopMode == STOP_ATR ? (half ? hStop : cStop) : (isL ? MathMax(sStop, cStop) : MathMin(sStop, cStop));
      double risk = d * (entry - stop);
      if(risk >= TickSize() && RoundTick(stop) != RoundTick(entry))
      {
         bool haveZ = InpNoChase && vwSd > 0 && vwBars >= 3 && sessN >= 1;
         bool ghost = haveZ && d * (c - vwap) / vwSd > InpNoChaseSig;
         if(MathAbs(st) == 1 && !trGhost) evCancel = 2;
         st = isL ? 1 : -1; armBar = bi; lim = entry; stp = stop; stp0 = stop; trRisk = risk; trHalf = half; trGhost = ghost;
         t1 = lim + d * InpTp1R * risk; t2 = lim + d * InpTp2R * risk; t3 = lim + d * InpTp3R * risk; t4 = lim + d * InpTp4R * risk;
         tF = InpExitAt == EXIT_TP1 ? t1 : InpExitAt == EXIT_TP2 ? t2 : InpExitAt == EXIT_TP3 ? t3 : t4;
         if(!ghost) { evArm = true; evArmL = isL; }
      }
   }
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
      default:        r = base;
   }
   if(InpCapOn && r > InpHardCap)
   {
      if(InpCapAction == CAP_STOP) capStop = true;
      else if(InpCapAction == CAP_RESET)
      {
         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0;
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

double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
void SetExits(bool withTarget)
{
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   double sl = StopPx(exL), tp = withTarget ? TgtPx(exL, tF) : 0;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double minD = MinDist();
   // price is already through the engine's stop or target: the engine exits on this bar, so exit now
   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp))) { CloseAll(); return; }
   if(exL) { if(bid - sl < minD) sl = FloorTick(bid - minD); if(tp > 0 && tp - bid < minD) tp = CeilTick(bid + minD); }
   else    { if(sl - ask < minD) sl = CeilTick(ask + minD); if(tp > 0 && ask - tp < minD) tp = FloorTick(ask - minD); }
   if(!trade.PositionModify(tk, sl, tp))
      Print("Stop/target update rejected (", trade.ResultRetcodeDescription(), "): SL ", DoubleToString(sl, _Digits), " TP ", DoubleToString(tp, _Digits));
}

//--- drawing -----------------------------------------------------------------
void DrawLimit(datetime bt, bool on)
{
   ObjectDelete(0, "ARM_limit");
   if(!InpDraw || !on) return;
   ObjectCreate(0, "ARM_limit", OBJ_TREND, 0, bt, lim, bt + PeriodSeconds() * InpRetestBars, lim);
   ObjectSetInteger(0, "ARM_limit", OBJPROP_STYLE, STYLE_DASH); ObjectSetInteger(0, "ARM_limit", OBJPROP_COLOR, clrWhite);
   ObjectSetInteger(0, "ARM_limit", OBJPROP_RAY_RIGHT, false);
}
void DrawTrade(datetime t0)
{
   if(!InpDraw) return;
   string id = "ARM_" + IntegerToString((long)t0);
   ObjectCreate(0, id + "_tgt", OBJ_RECTANGLE, 0, t0, MathMax(lim, tF), t0, MathMin(lim, tF));
   ObjectSetInteger(0, id + "_tgt", OBJPROP_COLOR, clrMediumSeaGreen); ObjectSetInteger(0, id + "_tgt", OBJPROP_FILL, true); ObjectSetInteger(0, id + "_tgt", OBJPROP_BACK, true);
   ObjectCreate(0, id + "_stp", OBJ_RECTANGLE, 0, t0, MathMax(lim, stp0), t0, MathMin(lim, stp0));
   ObjectSetInteger(0, id + "_stp", OBJPROP_COLOR, clrIndianRed); ObjectSetInteger(0, id + "_stp", OBJPROP_FILL, true); ObjectSetInteger(0, id + "_stp", OBJPROP_BACK, true);
   gDrawT = t0; gDrawOn = true;
}
void ExtendTrade(datetime t1x)
{
   if(!InpDraw || !gDrawOn) return;
   string id = "ARM_" + IntegerToString((long)gDrawT);
   ObjectMove(0, id + "_tgt", 1, t1x, MathMin(lim, tF)); ObjectMove(0, id + "_tgt", 0, gDrawT, MathMax(lim, tF));
   ObjectMove(0, id + "_stp", 1, t1x, MathMin(lim, stp0)); ObjectMove(0, id + "_stp", 0, gDrawT, MathMax(lim, stp0));
}

//--- place the engine's setup at the broker (sizing, filters, pending or market order) ----
void TakeSetup(bool isL, bool newsBlk, bool flatNow)
{
   sigN++;
   ulong pTk; double pVol, pOpen;
   double rAmt = NextRisk(ExitR());
   double v = capStop ? 0 : LotsFor(rAmt, trRisk, lim, isL);
   bool posNow = HasPosition(pTk, pVol, pOpen);
   skipWhy = (exState != 0 || posNow) ? "still in a trade" : (newsBlk || flatNow) ? "news / force-close" : capStop ? "hard cap stop" : paused ? "paused" : dayBlock ? "streak stop" : v <= 0 ? "size 0" : "";
   if(skipWhy != "") { skipN++; return; }
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   double sprNow = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
   exCostPx = InpEarnBack && tv > 0 ? InpCommLot / (tv / ts) + sprNow : 0;
   exL = isL; exLots = v; exPnl = 0; exRiskAmt = v * ((trRisk + sprNow) / ts * tv + InpCommLot);
   for(int q = 0; q < 3; q++) pDone[q] = false;
   CancelPending();
   gVirt = false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ep = EntryPx(isL), sl = StopPx(isL);
   double minD = MinDist();
   // the order's SL must respect the stops level; SetExits re-sends the engine's stop once the engine has filled
   if(isL) sl = MathMin(sl, FloorTick(MathMin(ep, bid) - minD));
   else    sl = MathMax(sl, CeilTick(MathMax(ep, ask) + minD));
   bool ok;
   if(InpEntryMode == ENTRY_MARKET)
      ok = isL ? trade.Buy(v, _Symbol, 0, sl, 0, "ARM") : trade.Sell(v, _Symbol, 0, sl, 0, "ARM");
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) ok = trade.BuyLimit(v, ep, _Symbol, sl, 0, ORDER_TIME_GTC, 0, "ARM");
      else if(ask <= ep)                ok = trade.Buy(v, _Symbol, 0, sl, 0, "ARM");   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                 // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) ok = trade.SellLimit(v, ep, _Symbol, sl, 0, ORDER_TIME_GTC, 0, "ARM");
      else if(bid >= ep)                ok = trade.Sell(v, _Symbol, 0, sl, 0, "ARM");
      else { ok = true; gVirt = true; }
   }
   if(ok) { exState = 1; exArm = armBar; exSynced = false; takenN++; }
   else { skipN++; skipWhy = "order rejected"; Print("ARM order failed: ", trade.ResultRetcodeDescription()); }
}

//--- an entry that could not be a pending order (inside the stops distance): enter at market when the level is reached
void VirtualEntry()
{
   if(!gVirt) return;
   if(exState != 1) { gVirt = false; return; }
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ep = EntryPx(exL), sl = StopPx(exL);
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      if(!(exL ? trade.Buy(exLots, _Symbol, 0, sl, 0, "ARM") : trade.Sell(exLots, _Symbol, 0, sl, 0, "ARM")))
         Print("ARM entry failed: ", trade.ResultRetcodeDescription());
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
      else { double tmp[]; ArrayResize(tmp, n - 2); for(int q = 0; q < n - 2; q++) tmp[q] = labSeq[q + 1]; ArrayResize(labSeq, n - 2); for(int q = 0; q < n - 2; q++) labSeq[q] = tmp[q]; }
   }
   else
   {
      recPool += -exPnl; recLosses++; dUnits++; rdUnits = (int)MathMax(1, rdUnits - 1); parWins = 0;
      double used = LabUnits(); int n = ArraySize(labSeq); ArrayResize(labSeq, n + 1); labSeq[n] = used;
   }
   oscP += exPnl;
   if(oscP >= InpBaseRisk) { oscU = 1; oscP = 0; } else if(win) oscU++;
   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false;
   CancelPending();
}

//=== EXECUTION: runs once per new bar, after the engine processed the bar that just closed ===
void OnNewBar()
{
   ProcessBar(1);
   datetime bt = iTime(_Symbol, _Period, 1);
   datetime ut = UserTime(bt), utPrev = UserTime(gPrevT > 0 ? gPrevT : iTime(_Symbol, _Period, 2));

   // drawings of the engine's shown trades (same events as the TradingView files)
   if(evCancel != 0 || evFill) ObjectDelete(0, "ARM_limit");
   if(evArm) DrawLimit(bt, true);
   if(evFill) DrawTrade(bt); else ExtendTrade(bt);
   if(evExit) gDrawOn = false;

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
   if(evExit && exState == 2 && exMine && (!InpEarnBack || !evWin)) CloseAll();               // engine exited: never stay in (earn-back only outlives a win)
   // engine wins: close a broker position the engine is not in (early fill on a spread spike, a fill racing a cancel,
   // or an engine exit on a bar caught up after a disconnect); with earn-back a synced trade may outlive the engine exit
   bool engHolds = (MathAbs(st) == 2 && exSynced && exMine) || (MathAbs(st) == 1 && !exSynced && exState == 2 && exMine);
   if(pos && !exClosed && !evExit && !engHolds && !(InpEarnBack && exSynced))
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

   // status panel
   string state = st != 0 && trGhost ? "SKIPPED (too far from VWAP)" : st == 2 ? "LONG ACTIVE" : st == -2 ? "SHORT ACTIVE" : st == 1 ? "BUY LIMIT ARMED" : st == -1 ? "SELL LIMIT ARMED" :
                  capStop ? "HARD CAP: STOPPED" : newsBlk ? "NEWS WINDOW" : paused ? "PAUSED" : dayBlock ? "STREAK STOP TODAY" :
                  !gDayOk ? "DAY SWITCHED OFF" : !gHourOk ? "OUTSIDE HOURS" : "SCANNING";
   string ex = exState == 2 ? " (in trade)" : exState == 1 ? (gVirt ? " (waiting for the level)" : " (order working)") : "";
   Comment(StringFormat("AUCTION RETEST EA v3\nState: %s%s\nEntry/Stop: %s / %s   Exit target: %s\nRisk: %.2f  Lots: %.2f\nRecovery pool: %.2f  Carried: %.2f\nStreak W/L: %d/%d   Total %dW/%dL\nDay P&L: %.2f  Fills: %d/%d\nSignals %d · taken %d · skipped %d%s%s",
           state, ex, DoubleToString(lim, _Digits), DoubleToString(stp, _Digits), DoubleToString(tF, _Digits), exRiskAmt, exLots,
           recPool, carried, winRow, lossRow, exW, exLn, dayPnl, dayFills, InpMaxFills, sigN, takenN, skipN,
           missN > 0 ? StringFormat(" · missed %d", missN) : "", skipWhy != "" ? " (last: " + skipWhy + ")" : ""));
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
   for(int k = 0; k < 3; k++)
   {
      if(k + 1 >= exitK || pp[k] <= 0 || pDone[k]) continue;
      if(exL ? px >= tp[k] + exCostPx : px <= tp[k] - exCostPx)
      {
         double cv = MathFloor(exLots * pp[k] / 100.0 / step + 1e-9) * step;
         if(cv >= vmin && vol - cv >= vmin - 1e-9) trade.PositionClosePartial(tk, NormalizeDouble(cv, 8));
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
   totW = 0; totL = 0; totR = 0; gNewDay = false; gDayOk = true; gHourOk = true;
   exState = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exPnl = 0; exArm = -1; exSynced = false; gRearm = false; gDrawOn = false;
   sigN = 0; takenN = 0; skipN = 0; missN = 0; skipWhy = "";
   gVirt = false; gDayPend = false; gPrevT = 0; capStop = false;
   for(int q = 0; q < 3; q++) pDone[q] = false;
}

//--- events -----------------------------------------------------------------
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(50);
   trade.SetTypeFillingBySymbol(_Symbol);
   ResetEngine();
   LabReset();
   if(InpTp1R > InpTp2R || InpTp2R > InpTp3R || InpTp3R > InpTp4R) { Print("Targets must be in order: TP1 <= TP2 <= TP3 <= TP4."); return INIT_PARAMETERS_INCORRECT; }
   // warm up the engine on history (no orders): it ends in the same state as the TradingView engine would
   int bars = Bars(_Symbol, _Period);
   int look = (int)MathMax(MathMax(InpStructLen, InpBrkLen + 1), MathMax(InpMomLen + 1, InpStopLen)) + 2;
   int need = look + InpAtrLen + 10;
   if(bars < need) { Print("Not enough chart history yet (", bars, " bars, need ", need, "); scroll the chart back or load more history, then attach the EA again."); return INIT_FAILED; }
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
      if((isL && st == 2) || (!isL && st == -2)) { exState = 2; exL = isL; exLots = vol; exArm = armBar; exSynced = true; for(int q = 0; q < 3; q++) pDone[q] = tpHit >= q + 1; Print("Adopted open position #", tk, " (engine is in the same trade)."); SetExits(true); }
      else { exState = 2; Print("Open position #", tk, " does not match the engine state; it will be closed on the next bar (the engine wins)."); }
   }
   CancelPending();   // a pending order from before the restart has no tracked state
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0;   // re-place the engine's armed setup on the first tick
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { Comment(""); }

void OnTick()
{
   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 != gLastBarTime)
   {
      gLastBarTime = t0;
      int sh = gLastDone > 0 ? iBarShift(_Symbol, _Period, gLastDone, true) : -1;   // 2 = nothing missed, 1 = bar 1 already processed
      if(sh == 1) { VirtualEntry(); ManagePartials(); return; }
      gPrevT = gLastDone;
      bool caught = false; long biBefore = bi;
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
