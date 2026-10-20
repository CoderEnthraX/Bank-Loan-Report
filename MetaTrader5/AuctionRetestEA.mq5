//+------------------------------------------------------------------+
//| AuctionRetestEA.mq5                                              |
//| MetaTrader 5 port of the TradingView "Auction Retest Strategy".  |
//|                                                                  |
//| Signal: session VWAP + displacement candle + limit retest, the   |
//| same rules as Auction_Retest_Model.pine / _Strategy.pine.        |
//| Money management: $ risk sizing, hard cap, leverage cap,         |
//| commission earn-back, partials, stop moves, final-exit choice,   |
//| streak stops / pauses, 17 loss-recovery modes, trading hours,    |
//| force-close time, weekend filter and news windows.               |
//|                                                                  |
//| Differences from TradingView, by design:                         |
//|  - Lot size, lot step and tick value come from the broker's      |
//|    symbol specification, so every symbol sizes correctly.        |
//|  - Spread is the broker's real Bid/Ask (no spread input).        |
//|  - The trading day / VWAP reset is the broker's server midnight. |
//|  - Partials close at market when price reaches the target.       |
//+------------------------------------------------------------------+
#property copyright "Auction Retest Model"
#property version   "1.00"
#property description "VWAP displacement + retest EA with money management (port of the TradingView strategy)."

#include <Trade/Trade.mqh>

//--- enums
enum ENUM_ENTRY_MODE { ENTRY_MODEL = 0,   // Model (body mid or 6-bar level)
                       ENTRY_PCT   = 1,   // Custom % of signal candle
                       ENTRY_MARKET = 2 };// Market (next bar open)
enum ENUM_EXIT_AT { EXIT_TP1 = 1, EXIT_TP2 = 2, EXIT_TP3 = 3, EXIT_TP4 = 4 };
enum ENUM_REARM { REARM_KEEP = 0,  // Keep first
                  REARM_NEW  = 1 };// Replace with newer
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

//--- signal model (same defaults as the indicator)
input group "SIGNAL MODEL"
input int    InpStructLen    = 10;    // Breakout lookback (bars)
input int    InpEntryLen     = 6;     // Entry level lookback (bars)
input int    InpRetestBars   = 5;     // Retest window (bars)
input double InpDispAtr      = 0.8;   // Min displacement range (x ATR)
input double InpBodyPct      = 55.0;  // Min body (% of range)
input double InpClosePct     = 25.0;  // Max close distance from extreme (% of range)
input int    InpMomLen       = 10;    // Momentum lookback (bars)
input double InpMomAtr       = 0.85;  // Min momentum (x ATR, 0 = off)
input ENUM_REARM InpRearm    = REARM_KEEP; // Same-direction re-arm
input double InpStopAtr      = 1.8;   // Stop distance (x ATR)
input bool   InpHalfStop     = true;  // Half stop on counter-bias first signal
input double InpHalfStopAtr  = 0.9;   // Half stop (x ATR)
input int    InpBiasNet      = 3;     // Prev session net impulses
input int    InpCooldown     = 2;     // Cooldown after exit (bars)
input int    InpMaxFills     = 5;     // Max fills per day
input double InpDayStopR     = 3.0;   // Daily stop (R lost, 0 = off)
input bool   InpFillBarStopR = false; // Count fill-bar stops in daily stop
input bool   InpLegReset     = true;  // Re-anchor breakout after a trade
input int    InpAtrLen       = 14;    // ATR length (Wilder / RMA)
input bool   InpVwapFilter   = true;  // Longs above VWAP / shorts below
input int    InpSlopeBars    = 3;     // VWAP slope bars (0 = off)
input int    InpMinOpenBars  = 1;     // Skip first bars after the daily reset
input bool   InpSkipSunday   = true;  // Skip Sunday (UTC) weekly open
input bool   InpAllowLong    = true;  // Longs
input bool   InpAllowShort   = true;  // Shorts

input group "ENTRY PRICE"
input ENUM_ENTRY_MODE InpEntryMode = ENTRY_MODEL; // Entry price
input double InpEntryPct     = 50.0;  // Custom % (0 = close, 50 = mid, 100 = low/high)

input group "TARGETS, PARTIALS AND STOP MOVES"
input double InpTp1R = 0.6;  // TP1 (R)
input double InpP1   = 0.0;  // TP1 close % (0 = no partial)
input double InpTp2R = 1.0;  // TP2 (R)
input double InpP2   = 0.0;  // TP2 close %
input double InpTp3R = 1.5;  // TP3 (R)
input double InpP3   = 0.0;  // TP3 close %
input double InpTp4R = 2.0;  // TP4 (R)
input ENUM_EXIT_AT InpExitAt = EXIT_TP4; // Final exit at
input bool   InpMv1On = false; // When TP1 hits, move stop
input double InpMv1R  = 0.0;   //   ...to (R, 0 = breakeven)
input bool   InpMv2On = false; // When TP2 hits, move stop
input double InpMv2R  = 0.6;   //   ...to (R)
input bool   InpMv3On = false; // When TP3 hits, move stop
input double InpMv3R  = 1.0;   //   ...to (R)

input group "RISK AND POSITION SIZE"
input double InpBaseRisk = 50.0;   // Base risk per trade (account currency)
input bool   InpCapOn    = false;  // Hard cap: max loss per trade
input double InpHardCap  = 500.0;  // Hard cap amount
input ENUM_CAP_ACTION InpCapAction = CAP_CLAMP; // If the risk would exceed the cap
input double InpLeverage = 100.0;  // Leverage cap 1:x (0 = broker margin only)
input double InpLotStep  = 0.0;    // Lot step (0 = broker's volume step)

input group "COMMISSION"
input double InpCommLot  = 0.0;    // Commission per lot, round trip (for sizing / earn-back)
input bool   InpEarnBack = false;  // Extend targets to earn back commission + spread

input group "STREAKS AND PAUSES"
input bool InpLStopOn = false; // Stop for the day after N losses in a row
input int  InpLStopN  = 2;     //   N losses
input bool InpWStopOn = false; // Stop for the day after N wins in a row
input int  InpWStopN  = 3;     //   N wins
input bool InpPauseOn = false; // Pause after N losses in a row
input int  InpPauseN  = 3;     //   N losses
input int  InpPauseDays = 1;   //   Days to pause (1-3)

input group "TIME FILTERS AND NEWS (times in YOUR time zone)"
input double InpServerGMT = 2.0;   // Broker server time zone (GMT +h; check Market Watch time)
input double InpUserGMT   = 5.5;   // Your time zone (GMT +h; India = 5.5)
input bool   InpHoursOn   = false; // Trade only between
input int    InpStartH    = 6;     //   start hour
input int    InpStartM    = 0;     //   start minute
input int    InpEndH      = 23;    //   end hour
input int    InpEndM      = 0;     //   end minute
input bool   InpFcOn      = false; // Force-close open trades daily at
input int    InpFcH       = 2;     //   hour
input int    InpFcM       = 0;     //   minute
input bool   InpWeekendOn = false; // No trading on Saturday and Sunday
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
input int    InpWarmBars = 3000;   // Bars used to warm up VWAP / ATR / counters
input bool   InpDraw     = true;   // Draw trade boxes

//--- globals ----------------------------------------------------------
CTrade   trade;
datetime gLastBarTime = 0;
long     gBarNo = 0;            // running number of processed (closed) bars

// signal state
double   cumPV = 0, cumW = 0, cumP = 0; int cumN = 0; int vwBars = 0;
double   vwHist[];             // vwap of processed bars, [0] = latest
double   atr = 0; int atrN = 0; double atrSum = 0;
int      bullN = 0, bearN = 0, prevNet = 0; bool havePrev = false;
int      lastDayKey = -1;
// per-bar outputs of the last processed bar
bool     sNewDay = false, sBullBase = false, sBearBase = false, sHalfL = false, sHalfS = false;
double   sPriorHigh = 0, sPriorLow = 0, sEntHigh = 0, sEntLow = 0, sBodyMid = 0, sAtr = 0, sRng = 0;

// trade state
int      st = 0;                // 0 flat, +-1 armed, +-2 in position
long     armBar = -1, fillBar = -1, lastExit = -1, lastFill = -1;
int      lastDir = 0;
double   lim = 0, stp0 = 0, stp = 0, t1 = 0, t2 = 0, t3 = 0, t4 = 0, tF = 0;
double   riskPx = 0, riskUsd = 0, lots = 0;
int      tpHit = 0;
bool     pDone[4];
double   trPnl = 0;
ulong    lastDeal = 0;
ulong    pendTicket = 0;
datetime gDrawT = 0;

int      dayFills = 0; double dayRiskR = 0, dayPnl = 0;
int      lossRow = 0, winRow = 0; bool dayBlock = false; int pauseLeft = 0; bool paused = false;
double   recPool = 0; int recLosses = 0; int dUnits = 1; double carried = 0; bool capStop = false;
double   labSeq[]; int parWins = 0; int rdUnits = 1; int oscU = 1; double oscP = 0;
double   totalNet = 0; int totW = 0, totL = 0;

//--- helpers ----------------------------------------------------------
double Pt()        { return SymbolInfoDouble(_Symbol, SYMBOL_POINT); }
double TickSize()  { double t = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE); return t > 0 ? t : Pt(); }
double NormP(double p) { double ts = TickSize(); return NormalizeDouble(MathRound(p / ts) * ts, _Digits); }
datetime UserTime(datetime server) { return server - (datetime)(InpServerGMT * 3600) + (datetime)(InpUserGMT * 3600); }
datetime UtcTime(datetime server)  { return server - (datetime)(InpServerGMT * 3600); }
int      MinOfDay(datetime t) { MqlDateTime d; TimeToStruct(t, d); return d.hour * 60 + d.min; }
int      DowOf(datetime t)    { MqlDateTime d; TimeToStruct(t, d); return d.day_of_week; }
int      DayKey(datetime t)   { MqlDateTime d; TimeToStruct(t, d); return d.year * 1000 + d.day_of_year; }

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

bool HasPending()
{
   for(int i = OrdersTotal() - 1; i >= 0; i--)
   {
      ulong tk = OrderGetTicket(i);
      if(tk == 0) continue;
      if(OrderGetString(ORDER_SYMBOL) == _Symbol && OrderGetInteger(ORDER_MAGIC) == InpMagic) return true;
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
   pendTicket = 0;
   ObjectDelete(0, "ARM_limit");
}

void CloseAll()
{
   ulong tk; double v, op;
   while(HasPosition(tk, v, op)) { if(!trade.PositionClose(tk)) break; }
}

// realised P&L of this EA's deals since the last call (profit + commission + swap + fee); closed = an exit deal was seen
double NewDealsPnl(bool &closed)
{
   closed = false;
   double sum = 0;
   if(!HistorySelect(0, TimeCurrent() + 86400)) return 0;
   int n = HistoryDealsTotal();
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      sum += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      long entry = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) closed = true;
   }
   for(int i = 0; i < n; i++) { ulong tk = HistoryDealGetTicket(i); if(tk > lastDeal) lastDeal = tk; }
   return sum;
}

//--- signal model: process one CLOSED bar (shift s), like one Pine bar --------
void ProcessBar(int s)
{
   datetime t = iTime(_Symbol, _Period, s);
   double o = iOpen(_Symbol, _Period, s), h = iHigh(_Symbol, _Period, s), l = iLow(_Symbol, _Period, s), c = iClose(_Symbol, _Period, s);
   long   rv = iVolume(_Symbol, _Period, s);
   long   tv = iTickVolume(_Symbol, _Period, s);
   double w  = rv > 0 ? (double)rv : (tv > 0 ? (double)tv : 1.0);
   double hlc3 = (h + l + c) / 3.0;

   // new trading day = broker server date change (the VWAP and the daily counters reset)
   int key = DayKey(t);
   sNewDay = (lastDayKey != -1 && key != lastDayKey);
   if(lastDayKey == -1) sNewDay = true;
   lastDayKey = key;

   // VWAP
   if(sNewDay) { cumPV = 0; cumW = 0; cumP = 0; cumN = 0; vwBars = 0; } else vwBars++;
   cumPV += hlc3 * w; cumW += w; cumP += hlc3; cumN++;
   double vwap = cumW > 0 ? cumPV / cumW : cumP / cumN;
   int hn = ArraySize(vwHist);
   if(hn < 600) ArrayResize(vwHist, hn + 1);
   for(int k = ArraySize(vwHist) - 1; k > 0; k--) vwHist[k] = vwHist[k - 1];
   vwHist[0] = vwap;

   // ATR (Wilder RMA, like ta.atr)
   double pc = iClose(_Symbol, _Period, s + 1);
   double tr = MathMax(h - l, MathMax(MathAbs(h - pc), MathAbs(l - pc)));
   if(atrN < InpAtrLen) { atrSum += tr; atrN++; atr = atrN == InpAtrLen ? atrSum / InpAtrLen : 0; }
   else atr = (atr * (InpAtrLen - 1) + tr) / InpAtrLen;
   sAtr = atr;

   // structure
   double ph = -DBL_MAX, pl = DBL_MAX, eh = -DBL_MAX, el = DBL_MAX;
   for(int j = 1; j <= InpStructLen; j++) { ph = MathMax(ph, iHigh(_Symbol, _Period, s + j)); pl = MathMin(pl, iLow(_Symbol, _Period, s + j)); }
   int el_n = (int)MathMin(InpEntryLen, InpStructLen);
   for(int j = 1; j <= el_n; j++) { eh = MathMax(eh, iHigh(_Symbol, _Period, s + j)); el = MathMin(el, iLow(_Symbol, _Period, s + j)); }
   sPriorHigh = ph; sPriorLow = pl; sEntHigh = eh; sEntLow = el;
   double rng = h - l, body = MathAbs(c - o);
   sRng = rng; sBodyMid = (o + c) / 2.0;
   double mom = c - iClose(_Symbol, _Period, s + InpMomLen);
   bool haveSlope = InpSlopeBars > 0 && vwBars >= InpSlopeBars && ArraySize(vwHist) > InpSlopeBars;
   double slope = haveSlope ? vwap - vwHist[InpSlopeBars] : 0;
   bool slopeUp = !haveSlope || slope > 0, slopeDn = !haveSlope || slope < 0;
   bool big = rng > 0 && atr > 0 && rng >= InpDispAtr * atr && body / rng * 100.0 >= InpBodyPct - 1e-7;
   bool bullShape = c > o && big && (h - c) / rng * 100.0 <= InpClosePct + 1e-7 && slopeUp;
   bool bearShape = c < o && big && (c - l) / rng * 100.0 <= InpClosePct + 1e-7 && slopeDn;
   bool setupOk = vwBars >= InpMinOpenBars && !(InpSkipSunday && DowOf(UtcTime(t)) == 0);
   sBullBase = InpAllowLong  && setupOk && bullShape && (!InpVwapFilter || c > vwap) && (InpMomAtr <= 0 || mom >= InpMomAtr * atr);
   sBearBase = InpAllowShort && setupOk && bearShape && (!InpVwapFilter || c < vwap) && (InpMomAtr <= 0 || -mom >= InpMomAtr * atr);

   // counter-bias half stop: per-session impulse counters
   bool bullImp = bullShape && h > ph;
   bool bearImp = bearShape && l < pl;
   if(sNewDay) { if(gBarNo > 0) { prevNet = bullN - bearN; havePrev = true; } bullN = 0; bearN = 0; }
   sHalfL = InpHalfStop && bullN == 0 && havePrev && prevNet <= -InpBiasNet;
   sHalfS = InpHalfStop && bearN == 0 && havePrev && prevNet >= InpBiasNet;
   if(bullImp) bullN++;
   if(bearImp) bearN++;
   gBarNo++;
}

//--- risk $ for the next trade (loss recovery + hard cap) -------------------
double NextRisk(double exitR)
{
   double base = InpBaseRisk, r = base;
   // Rule C split step base
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
double LotsFor(double riskAmt, double stopDist, double entry)
{
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double ts = TickSize();
   if(tv <= 0 || ts <= 0 || stopDist <= 0) return 0;
   double perLot = stopDist / ts * tv + InpCommLot;           // stop-out loss per lot incl. commission
   double v = riskAmt / perLot;
   // leverage cap: position value <= equity x leverage
   double notionalPerLot = entry / ts * tv;
   if(InpLeverage > 0 && notionalPerLot > 0) v = MathMin(v, AccountInfoDouble(ACCOUNT_EQUITY) * InpLeverage / notionalPerLot);
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   v = MathFloor(v / step + 1e-9) * step;
   v = MathMin(v, vmax);
   // broker margin check
   double margin;
   ENUM_ORDER_TYPE ot = ORDER_TYPE_BUY;
   while(v >= vmin && OrderCalcMargin(ot, _Symbol, v, entry, margin) && margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v -= step;
   if(v < vmin) return 0;
   return NormalizeDouble(v, 8);
}

//--- time filters -----------------------------------------------------------
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

bool InHours(datetime ut)
{
   if(!InpHoursOn) return true;
   int cur = MinOfDay(ut), a = InpStartH * 60 + InpStartM, b = InpEndH * 60 + InpEndM;
   return a <= b ? (cur >= a && cur < b) : (cur >= a || cur < b);
}

//--- drawing -----------------------------------------------------------------
void DrawTrade(datetime t0)
{
   if(!InpDraw) return;
   string id = "ARM_" + IntegerToString((long)t0);
   ObjectCreate(0, id + "_tgt", OBJ_RECTANGLE, 0, t0, MathMax(lim, tF), t0, MathMin(lim, tF));
   ObjectSetInteger(0, id + "_tgt", OBJPROP_COLOR, clrMediumSeaGreen); ObjectSetInteger(0, id + "_tgt", OBJPROP_FILL, true); ObjectSetInteger(0, id + "_tgt", OBJPROP_BACK, true);
   ObjectCreate(0, id + "_stp", OBJ_RECTANGLE, 0, t0, MathMax(lim, stp0), t0, MathMin(lim, stp0));
   ObjectSetInteger(0, id + "_stp", OBJPROP_COLOR, clrIndianRed); ObjectSetInteger(0, id + "_stp", OBJPROP_FILL, true); ObjectSetInteger(0, id + "_stp", OBJPROP_BACK, true);
   gDrawT = t0;
}
void ExtendTrade(datetime t1x)
{
   if(!InpDraw) return;
   datetime t0 = gDrawT;
   string id = "ARM_" + IntegerToString((long)t0);
   ObjectMove(0, id + "_tgt", 1, t1x, MathMin(lim, tF)); ObjectMove(0, id + "_tgt", 0, t0, MathMax(lim, tF));
   ObjectMove(0, id + "_stp", 1, t1x, MathMin(lim, stp0)); ObjectMove(0, id + "_stp", 0, t0, MathMax(lim, stp0));
}

//--- the per-bar trading step (runs once on the first tick of each new bar, for the bar that just closed) ---
void OnNewBar()
{
   ProcessBar(1);
   long     bar   = gBarNo - 1;                         // number of the bar that just closed
   datetime bt    = iTime(_Symbol, _Period, 1);
   datetime ut    = UserTime(bt), utPrev = UserTime(iTime(_Symbol, _Period, 2));
   double   hi    = iHigh(_Symbol, _Period, 1), lo = iLow(_Symbol, _Period, 1), cl = iClose(_Symbol, _Period, 1);
   double   spr   = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD) * Pt();

   if(sNewDay)
   {
      dayFills = 0; dayRiskR = 0; dayPnl = 0; dayBlock = false;
      paused = pauseLeft > 0; if(pauseLeft > 0) pauseLeft--;
   }

   // 1. deals since the last bar -> fills / closes / Rule C carried
   bool closedNew; double newPnl = NewDealsPnl(closedNew);
   bool anyDeal = newPnl != 0 || closedNew;
   trPnl += newPnl; totalNet += newPnl;
   if(anyDeal) carried = MathMax(0.0, carried - newPnl);
   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   bool filled = MathAbs(st) == 1 && (pos || closedNew);
   if(filled)
   {
      bool isL = st == 1;
      st = isL ? 2 : -2; fillBar = bar; lastFill = bar; lastDir = isL ? 1 : -1; dayFills++; tpHit = 0;
      for(int q = 0; q < 4; q++) pDone[q] = false;
      if(InpEntryMode == ENTRY_MARKET && pos) lim = pOpen;
      ObjectDelete(0, "ARM_limit");
      DrawTrade(bt);
   }

   // 2. open trade: TP tracking and stop moves (on the closed bar, like the strategy)
   if(MathAbs(st) == 2 && pos && bar > fillBar)
   {
      ExtendTrade(bt);
      bool isL = st == 2; double d = isL ? 1 : -1;
      int reached = (isL ? hi >= t3 : lo + spr <= t3) ? 3 : (isL ? hi >= t2 : lo + spr <= t2) ? 2 : (isL ? hi >= t1 : lo + spr <= t1) ? 1 : 0;
      if(reached > tpHit)
      {
         double ns = stp;
         if(reached >= 1 && InpMv1On) ns = isL ? MathMax(ns, lim + InpMv1R * riskPx) : MathMin(ns, lim - InpMv1R * riskPx);
         if(reached >= 2 && InpMv2On) ns = isL ? MathMax(ns, lim + InpMv2R * riskPx) : MathMin(ns, lim - InpMv2R * riskPx);
         if(reached >= 3 && InpMv3On) ns = isL ? MathMax(ns, lim + InpMv3R * riskPx) : MathMin(ns, lim - InpMv3R * riskPx);
         tpHit = reached;
         if(ns != stp)
         {
            if(trade.PositionModify(pTk, NormP(ns), NormP(tF))) stp = ns;
            else Print("Stop move rejected (", trade.ResultRetcodeDescription(), "), keeping the stop at ", DoubleToString(stp, _Digits));
         }
      }
   }

   // 3. trade closed (including a stop on the fill bar)
   if(MathAbs(st) == 2 && !pos)
   {
      ExtendTrade(bt);
      bool sameBar = bar == fillBar;
      double r = riskUsd > 0 ? trPnl / riskUsd : 0;
      bool win = trPnl > 0;
      dayPnl += trPnl;
      dayRiskR += (sameBar && !win && !InpFillBarStopR) ? 0.0 : r;
      if(win) totW++; else totL++;
      lossRow = win ? 0 : lossRow + 1; winRow = win ? winRow + 1 : 0;
      if(InpLStopOn && lossRow >= InpLStopN) dayBlock = true;
      if(InpWStopOn && winRow >= InpWStopN) dayBlock = true;
      if(InpPauseOn && lossRow >= InpPauseN) { dayBlock = true; pauseLeft = (int)MathMax(1, MathMin(3, InpPauseDays)); lossRow = 0; }
      if(win)
      {
         recPool = MathMax(0.0, recPool - trPnl); recLosses = recPool > 0 ? recLosses : 0;
         dUnits = (int)MathMax(1, dUnits - 1); rdUnits++;
         parWins = parWins + 1 >= InpParN ? 0 : parWins + 1;
         int n = ArraySize(labSeq);
         if(n <= 2) LabReset();
         else { double tmp[]; ArrayResize(tmp, n - 2); for(int q = 0; q < n - 2; q++) tmp[q] = labSeq[q + 1]; ArrayResize(labSeq, n - 2); for(int q = 0; q < n - 2; q++) labSeq[q] = tmp[q]; }
      }
      else
      {
         recPool += -trPnl; recLosses++; dUnits++; rdUnits = (int)MathMax(1, rdUnits - 1); parWins = 0;
         double used = LabUnits(); int n = ArraySize(labSeq); ArrayResize(labSeq, n + 1); labSeq[n] = used;
      }
      oscP += trPnl;
      if(oscP >= InpBaseRisk) { oscU = 1; oscP = 0; } else if(win) oscU++;
      lastExit = bar; st = 0; trPnl = 0;
      CancelPending();
   }

   // 4. time filters
   bool nStart; bool newsBlk = NewsBlock(ut, nStart, utPrev);
   int  fcM = InpFcH * 60 + InpFcM, curM = MinOfDay(ut), prvM = MinOfDay(utPrev);
   bool fcNow = InpFcOn && (curM >= prvM ? (prvM < fcM && curM >= fcM) : (fcM > prvM || fcM <= curM));
   int  dw = DowOf(ut); bool wknd = InpWeekendOn && (dw == 6 || dw == 0);
   int  dwp = DowOf(utPrev); bool wkndPrev = InpWeekendOn && (dwp == 6 || dwp == 0);
   bool wkndStart = wknd && !wkndPrev;
   bool flatNow = fcNow || wkndStart || nStart;
   bool timeOk  = InHours(ut) && !wknd && !newsBlk;
   if(flatNow && MathAbs(st) == 2 && pos) CloseAll();

   // armed limit: expire after the retest window, when the day cap is used up, or when trading is not allowed
   if(MathAbs(st) == 1 && !pos && (bar - armBar >= InpRetestBars || dayFills >= InpMaxFills || !timeOk || flatNow))
   {
      CancelPending(); st = 0;
   }

   // 5. arm a new setup
   bool cooled  = lastExit < 0 || bar - lastExit >= MathMax(InpCooldown, 1);
   bool dayOpen = (InpDayStopR <= 0 || dayRiskR > -InpDayStopR) && !dayBlock && !paused && !capStop;
   long legN = lastFill < 0 ? 0 : bar - lastFill;
   bool legOn = InpLegReset && MathAbs(st) != 2 && legN > 0 && legN < InpStructLen;
   double brkH = sPriorHigh, brkL = sPriorLow;
   if(legOn)
   {
      double lh = -DBL_MAX, ll = DBL_MAX;
      for(int j = 1; j <= legN; j++) { lh = MathMax(lh, iHigh(_Symbol, _Period, 1 + j)); ll = MathMin(ll, iLow(_Symbol, _Period, 1 + j)); }
      if(lastDir == 1) brkH = lh; else brkL = ll;
   }
   bool bullDisp = sBullBase && cl > brkH;
   bool bearDisp = sBearBase && cl < brkL;
   bool canArm = timeOk && !flatNow && MathAbs(st) != 2 && !pos && cooled && dayFills < InpMaxFills && dayOpen && sAtr > 0;
   bool keepArm = InpRearm == REARM_KEEP && ((st == 1 && bullDisp) || (st == -1 && bearDisp));
   if(canArm && (bullDisp || bearDisp) && !keepArm)
   {
      bool isL = bullDisp; double d = isL ? 1 : -1;
      double model = isL ? MathMax(sBodyMid, sEntHigh) : MathMin(sBodyMid, sEntLow);
      double entry = InpEntryMode == ENTRY_MODEL ? model : InpEntryMode == ENTRY_PCT ? cl - d * InpEntryPct / 100.0 * sRng : cl;
      bool half = isL ? sHalfL : sHalfS;
      double stop = half ? (isL ? MathMin(entry - InpHalfStopAtr * sAtr, lo) : MathMax(entry + InpHalfStopAtr * sAtr, hi)) : entry - d * InpStopAtr * sAtr;
      double rp = d * (entry - stop);
      int exitK = (int)InpExitAt;
      double exitR = exitK == 1 ? InpTp1R : exitK == 2 ? InpTp2R : exitK == 3 ? InpTp3R : InpTp4R;
      double rAmt = NextRisk(exitR);
      double v = capStop ? 0 : LotsFor(rAmt, rp, entry);
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
      double costPx = InpEarnBack && tv > 0 ? InpCommLot / (tv / ts) + spr : 0;
      if(rp >= TickSize() && v > 0)
      {
         CancelPending();
         st = isL ? 1 : -1; armBar = bar; lim = entry; stp0 = stop; stp = stop; riskPx = rp; lots = v;
         riskUsd = v * (rp / ts * tv + InpCommLot);
         t1 = entry + d * (InpTp1R * rp + costPx); t2 = entry + d * (InpTp2R * rp + costPx);
         t3 = entry + d * (InpTp3R * rp + costPx); t4 = entry + d * (InpTp4R * rp + costPx);
         tF = exitK == 1 ? t1 : exitK == 2 ? t2 : exitK == 3 ? t3 : t4;
         double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         double lvl = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * Pt();
         bool ok;
         if(InpEntryMode == ENTRY_MARKET)
            ok = isL ? trade.Buy(v, _Symbol, 0, NormP(stop), NormP(tF), "ARM") : trade.Sell(v, _Symbol, 0, NormP(stop), NormP(tF), "ARM");
         else if(isL)
            ok = entry < ask ? trade.BuyLimit(v, NormP(entry), _Symbol, NormP(stop), NormP(tF), ORDER_TIME_GTC, 0, "ARM")
                                   : trade.Buy(v, _Symbol, 0, NormP(stop), NormP(tF), "ARM");   // already through the limit: better price now
         else
            ok = entry > bid ? trade.SellLimit(v, NormP(entry), _Symbol, NormP(stop), NormP(tF), ORDER_TIME_GTC, 0, "ARM")
                                   : trade.Sell(v, _Symbol, 0, NormP(stop), NormP(tF), "ARM");
         if(!ok) { st = 0; Print("ARM order failed: ", trade.ResultRetcodeDescription()); }
         else if(InpDraw)
         {
            ObjectDelete(0, "ARM_limit");
            ObjectCreate(0, "ARM_limit", OBJ_TREND, 0, bt, entry, bt + PeriodSeconds() * InpRetestBars, entry);
            ObjectSetInteger(0, "ARM_limit", OBJPROP_STYLE, STYLE_DASH); ObjectSetInteger(0, "ARM_limit", OBJPROP_COLOR, clrWhite);
            ObjectSetInteger(0, "ARM_limit", OBJPROP_RAY_RIGHT, false);
         }
      }
   }

   // status panel
   string state = st == 2 ? "LONG ACTIVE" : st == -2 ? "SHORT ACTIVE" : st == 1 ? "BUY LIMIT ARMED" : st == -1 ? "SELL LIMIT ARMED" :
                  capStop ? "HARD CAP: STOPPED" : newsBlk ? "NEWS WINDOW" : wknd ? "WEEKEND" : !InHours(ut) ? "OUTSIDE HOURS" :
                  paused ? "PAUSED" : dayBlock ? "STREAK STOP TODAY" : !dayOpen ? "DAILY STOP HIT" : "SCANNING";
   Comment(StringFormat("AUCTION RETEST EA\nState: %s\nEntry/Stop: %s / %s   Final TP: %s\nRisk: %.2f  Lots: %.2f\nRecovery pool: %.2f  Carried: %.2f\nStreak W/L: %d/%d   Total %dW/%dL\nDay P&L: %.2f  R: %.2f  Fills: %d/%d",
           state, DoubleToString(lim, _Digits), DoubleToString(stp, _Digits), DoubleToString(tF, _Digits), riskUsd, lots,
           recPool, carried, winRow, lossRow, totW, totL, dayPnl, dayRiskR, dayFills, InpMaxFills));
}

//--- partial closes, intrabar ---------------------------------------------------
void ManagePartials()
{
   if(MathAbs(st) != 2) return;
   ulong tk; double vol, op;
   if(!HasPosition(tk, vol, op)) return;
   bool isL = st == 2;
   double px = isL ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   int exitK = (int)InpExitAt;
   double tp[3]; double pp[3];
   tp[0] = t1; tp[1] = t2; tp[2] = t3;
   pp[0] = InpP1; pp[1] = InpP2; pp[2] = InpP3;
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   for(int k = 0; k < 3; k++)
   {
      if(k + 1 >= exitK || pp[k] <= 0 || pDone[k]) continue;
      if(isL ? px >= tp[k] : px <= tp[k])
      {
         double cv = MathFloor(lots * pp[k] / 100.0 / step + 1e-9) * step;
         if(cv >= vmin && cv < vol) trade.PositionClosePartial(tk, NormalizeDouble(cv, 8));
         pDone[k] = true;
      }
   }
}

//--- events -----------------------------------------------------------------
int OnInit()
{
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(50);
   trade.SetTypeFillingBySymbol(_Symbol);
   LabReset();
   ArrayResize(vwHist, 0);
   // warm up the signal state on history (no trading)
   int bars = Bars(_Symbol, _Period);
   int need = InpStructLen + InpMomLen + InpAtrLen + 10;
   if(bars < need) { Print("Not enough chart history yet (", bars, " bars); the EA will retry."); return INIT_FAILED; }
   int start = (int)MathMin(InpWarmBars, bars - InpStructLen - InpMomLen - 5);
   for(int s = start; s >= 1; s--) ProcessBar(s);
   gLastBarTime = iTime(_Symbol, _Period, 0);
   // remember the last deal so old history is not counted
   bool c; NewDealsPnl(c);
   // restart recovery: adopt an open position of this EA so it keeps being managed
   ulong tk; double vol, op;
   if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      st = isL ? 2 : -2; lim = op; lots = vol;
      stp = PositionGetDouble(POSITION_SL); stp0 = stp; tF = PositionGetDouble(POSITION_TP);
      riskPx = MathAbs(op - stp);
      double d = isL ? 1 : -1;
      t1 = lim + d * InpTp1R * riskPx; t2 = lim + d * InpTp2R * riskPx; t3 = lim + d * InpTp3R * riskPx; t4 = lim + d * InpTp4R * riskPx;
      double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      riskUsd = TickSize() > 0 ? vol * riskPx / TickSize() * tv : 0;
      fillBar = gBarNo - 2; lastFill = fillBar; lastDir = isL ? 1 : -1; tpHit = 0;
      for(int q = 0; q < 4; q++) pDone[q] = false;
      Print("Adopted open position #", tk, " after restart (partial-close progress is not restored).");
   }
   CancelPending();   // a pending limit from before the restart has no tracked state; it is re-armed by new signals
   return INIT_SUCCEEDED;
}

void OnDeinit(const int reason) { Comment(""); }

void OnTick()
{
   datetime t0 = iTime(_Symbol, _Period, 0);
   if(t0 != gLastBarTime)
   {
      gLastBarTime = t0;
      OnNewBar();
   }
   ManagePartials();
}
//+------------------------------------------------------------------+
