"""v6.0 order block: MQL5 text pieces used by build_ob_ea.py (the same algorithm as ob/ob_stream.py and the Pine files)."""

INPUTS = r'''//--- v6.0 SETUPS: the VWAP setup, the order block setup, or both (one trade at a time; or the true grid: each setup its own trade, magic and money)
enum ENUM_SETUPS { SET_VWAP = 0,   // VWAP only
                   SET_OB   = 1,   // Order block only
                   SET_ONE  = 2,   // Both: one trade at a time
                   SET_GRID = 3 }; // Both: true grid (hedging account; order block magic = magic + 1)
enum ENUM_OB_TF  { OBTF_AUTO = 0,  // Auto (M1: M3 + M5; M5: M15 + M30 + H1; M15: H1 + H4)
                   OBTF_OFF  = 1,  // Off
                   OBTF_M3   = 3,  // M3
                   OBTF_M5   = 5,  // M5
                   OBTF_M15  = 15, // M15
                   OBTF_M30  = 30, // M30
                   OBTF_H1   = 60, // H1
                   OBTF_H4   = 240 };// H4
enum ENUM_OB_STOP { OBS_CANDLE = 0,  // Beyond the aggression candle
                    OBS_SWING  = 1 };// Beyond the last swing (pivot 2 / 2)

input group "SETUPS AND ORDER BLOCK"
@@SETUPS@@
input ENUM_OB_TF  InpObTf1     = OBTF_AUTO;  // Order block timeframe 1 (above the chart's)
input ENUM_OB_TF  InpObTf2     = OBTF_AUTO;  // Order block timeframe 2
input ENUM_OB_TF  InpObTf3     = OBTF_AUTO;  // Order block timeframe 3
input int    InpObFvgN    = 3;     // Fair value gap within N candles of the block (2 - 5)
input int    InpObEpi     = 30;    // Episode: candles from the first touch to find the entry
input int    InpObDays    = 20;    // A block waits for its first touch at most (days)
input int    InpObVolN    = 20;    // Absorption: volume average of the last N candles
input double InpObVolMult = 1.0;   // Absorption: volume above the average x
input double InpObAbsBody = 40.0;  // Absorption: body below (% of the candle's range)
input double InpObAbsWick = 50.0;  // Absorption: wick into the zone at least (% of the range)
input double InpObAggBody = 55.0;  // Aggression: body at least (% of the range), market entry at its close
input ENUM_OB_STOP InpObStop   = OBS_CANDLE; // Order block stop
input int    InpObBufTk   = 1;     // Stop buffer (ticks)
input int    InpObMinTk   = 5;     // Smallest stop distance (ticks)
input bool   InpObShow    = true;  // Draw the order block zones

'''

SETUPS_INPUT = 'input ENUM_SETUPS InpSetups    = SET_ONE;    // Setups to trade'
SETUPS_CONST = 'const ENUM_SETUPS InpSetups    = SET_OB;     // this EA trades the order block setup only'

GLOBALS = r'''bool     trMkt = false;            // v6.0: the setup enters at market (order block)
int      trSrc = 0;                // v6.0: the setup's source: 1 VWAP, 2 order block
//--- v6.0 order block engine: the higher-timeframe candles are built from the chart's own closed bars (server time), so the history and the
//--- live bars give the same blocks; a block's zone acts from the bar after its candle closed
#define  OB_ZMAX 100
#define  OB_PMAX 200
bool     gSrcV = true, gSrcO = false;   // the setups this engine arms: VWAP, order block
int      obTfN = 0; int obTfM[3];        // the order block timeframes in use (minutes)
bool     obCurOn[3]; long obCurK[3]; double obCurO[3], obCurH[3], obCurL[3], obCurC[3];   // the higher-timeframe candle being built
double   obDO[18], obDH[18], obDL[18], obDC[18]; int obDN[3];                      // its last closed candles, oldest first
int      obZN = 0; int obZD[OB_ZMAX]; double obZLo[OB_ZMAX], obZHi[OB_ZMAX]; datetime obZT0[OB_ZMAX]; int obZSt[OB_ZMAX]; long obZTb[OB_ZMAX]; bool obZAb[OB_ZMAX]; long obZId[OB_ZMAX];
long     obZSeq = 0;
double   obPL[OB_PMAX], obPH[OB_PMAX]; int obPLN = 0, obPHN = 0;   // confirmed swing lows / highs (pivot 2 / 2), oldest first
int      gLeg = 0;                         // v6.0: 0 = the VWAP leg (or the only one), 1 = the order block leg of the true grid
int      obSig = 0; double obStopC = 0, obStopS = 0;               // this bar's order block signal and its two stops (0 = none)
'''

FUNCS = r'''//=== v6.0 ORDER BLOCK ENGINE (same as the TradingView files) ==========
//--- the timeframe of slot q (minutes; 0 = off): Auto by the chart, only above the chart's, a whole multiple of it, and a whole part of a day
int ObTfPick(int q, ENUM_OB_TF v)
{
   int cm = PeriodSeconds(_Period) / 60;
   if(v == OBTF_OFF || cm <= 0) return 0;
   int m = (int)v;
   if(v == OBTF_AUTO)
      m = cm == 1 ? (q == 0 ? 3 : (q == 1 ? 5 : 0)) : cm == 3 ? (q == 0 ? 15 : (q == 1 ? 30 : 0)) : cm == 5 ? (q == 0 ? 15 : (q == 1 ? 30 : 60)) :
          cm == 15 ? (q == 0 ? 60 : (q == 1 ? 240 : 0)) : (cm == 30 || cm == 60) ? (q == 0 ? 240 : 0) : 0;
   return m > cm && m % cm == 0 && 1440 % m == 0 ? m : 0;
}
void ObDelZone(int k)
{
   if(gCanDraw && InpObShow) ObjectDelete(0, "ARM_OBZ" + IntegerToString(obZId[k]));
   for(int j = k; j < obZN - 1; j++)
   {
      obZD[j] = obZD[j + 1]; obZLo[j] = obZLo[j + 1]; obZHi[j] = obZHi[j + 1]; obZT0[j] = obZT0[j + 1];
      obZSt[j] = obZSt[j + 1]; obZTb[j] = obZTb[j + 1]; obZAb[j] = obZAb[j + 1]; obZId[j] = obZId[j + 1];
   }
   obZN--;
}
void ObReset()
{
   obTfN = 0;
   for(int q = 0; q < 3; q++)
   {
      int m = ObTfPick(q, q == 0 ? InpObTf1 : (q == 1 ? InpObTf2 : InpObTf3));
      bool dup = false;
      for(int j = 0; j < obTfN; j++) if(obTfM[j] == m) dup = true;
      if(m > 0 && !dup) { obTfM[obTfN] = m; obTfN++; }
   }
   for(int q = 0; q < 3; q++) { obCurOn[q] = false; obCurK[q] = 0; obCurO[q] = 0; obCurH[q] = 0; obCurL[q] = 0; obCurC[q] = 0; obDN[q] = 0; }
   ArrayInitialize(obDO, 0.0); ArrayInitialize(obDH, 0.0); ArrayInitialize(obDL, 0.0); ArrayInitialize(obDC, 0.0);
   while(obZN > 0) ObDelZone(obZN - 1);
   obZSeq = 0; obPLN = 0; obPHN = 0; obSig = 0; obStopC = 0; obStopS = 0;
}
string ObTfText()
{
   string s = "";
   for(int q = 0; q < obTfN; q++) s += (q > 0 ? " + " : "") + (obTfM[q] < 60 ? "M" + IntegerToString(obTfM[q]) : "H" + IntegerToString(obTfM[q] / 60));
   return s == "" ? "none" : s;
}
double ObVol(int s)
{
   long rv = iVolume(_Symbol, _Period, s), tv = iTickVolume(_Symbol, _Period, s);
   return rv > 0 ? (double)rv : (tv > 0 ? (double)tv : 1.0);
}
void ObAddZone(int dir, double lo, double hi, datetime t0)
{
   if(obZN >= OB_ZMAX) ObDelZone(0);                     // the oldest goes
   int k = obZN; obZN++; obZSeq++;
   obZD[k] = dir; obZLo[k] = lo; obZHi[k] = hi; obZT0[k] = t0; obZSt[k] = 0; obZTb[k] = -1; obZAb[k] = false; obZId[k] = obZSeq;
   if(gCanDraw && InpObShow)
   {
      string nm = "ARM_OBZ" + IntegerToString(obZSeq);
      if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_RECTANGLE, 0, t0, hi, t0 + PeriodSeconds(_Period), lo);
      ObjectSetInteger(0, nm, OBJPROP_COLOR, dir == 1 ? C'38,166,154' : C'239,83,80');
      ObjectSetInteger(0, nm, OBJPROP_FILL, false);
      ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_DOT);
      ObjectSetInteger(0, nm, OBJPROP_BACK, true);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
   }
}
//--- the fair value gap (kk - 2, kk) of candle kk and its close beyond block candle i
bool ObFvg(int q, int dir, int i, int kk)
{
   if(dir == 1) return obDL[q * 6 + kk] > obDH[q * 6 + kk - 2] && obDC[q * 6 + kk] > obDH[q * 6 + i];
   return obDH[q * 6 + kk] < obDL[q * 6 + kk - 2] && obDC[q * 6 + kk] < obDL[q * 6 + i];
}
//--- a higher-timeframe candle closed: keep it, then the order blocks it completes (the last opposite candle i, its gap within N candles,
//--- found at the first candle that makes it), acting from t0
void ObClose(int q, datetime t0)
{
   int n = obDN[q];
   if(n == 6)
   {
      for(int j = 0; j < 5; j++) { obDO[q * 6 + j] = obDO[q * 6 + j + 1]; obDH[q * 6 + j] = obDH[q * 6 + j + 1]; obDL[q * 6 + j] = obDL[q * 6 + j + 1]; obDC[q * 6 + j] = obDC[q * 6 + j + 1]; }
      n = 5;
   }
   obDO[q * 6 + n] = obCurO[q]; obDH[q * 6 + n] = obCurH[q]; obDL[q * 6 + n] = obCurL[q]; obDC[q * 6 + n] = obCurC[q];
   n++; obDN[q] = n; obCurOn[q] = false;
   int k = n - 1;
   for(int dd = 0; dd < 2; dd++)
   {
      int dir = dd == 0 ? 1 : -1;
      for(int i = k - InpObFvgN; i <= k - 2; i++)
      {
         if(i < 0) continue;
         if(dir == 1 ? !(obDC[q * 6 + i] < obDO[q * 6 + i]) : !(obDC[q * 6 + i] > obDO[q * 6 + i])) continue;
         if(!ObFvg(q, dir, i, k)) continue;
         bool early = false;
         for(int kk = i + 2; kk < k; kk++) if(ObFvg(q, dir, i, kk)) { early = true; break; }
         if(!early) ObAddZone(dir, obDL[q * 6 + i], obDH[q * 6 + i], t0);
      }
   }
}
//--- one closed chart bar (shift s, open time t): the candles, the swings, the zones (age, death, touch, the episode: break, aggression,
//--- absorption) -> obSig (1 buy, -1 sell, 0 none) with its candle stop obStopC and swing stop obStopS
void ObBar(int s, datetime t, double o, double h, double l, double c)
{
   obSig = 0; obStopC = 0; obStopS = 0;
   for(int q = 0; q < obTfN; q++)
   {
      long kq = (long)t / (obTfM[q] * 60);
      if(obCurOn[q] && obCurK[q] != kq) ObClose(q, t);  // the previous candle ended without a bar at its end (a gap): it acts from this bar
      if(!obCurOn[q]) { obCurOn[q] = true; obCurK[q] = kq; obCurO[q] = o; obCurH[q] = h; obCurL[q] = l; obCurC[q] = c; }
      else { obCurH[q] = MathMax(obCurH[q], h); obCurL[q] = MathMin(obCurL[q], l); obCurC[q] = c; }
   }
   if(bi >= 4)                                           // the swing 2 bars back is confirmed now
   {
      double pl = Lo(s + 2), ph = Hi(s + 2);
      if(pl <= Lo(s) && pl <= Lo(s + 1) && pl <= Lo(s + 3) && pl <= Lo(s + 4))
      {
         if(obPLN == OB_PMAX) { for(int j = 0; j < OB_PMAX - 1; j++) obPL[j] = obPL[j + 1]; obPLN--; }
         obPL[obPLN] = pl; obPLN++;
      }
      if(ph >= Hi(s) && ph >= Hi(s + 1) && ph >= Hi(s + 3) && ph >= Hi(s + 4))
      {
         if(obPHN == OB_PMAX) { for(int j = 0; j < OB_PMAX - 1; j++) obPH[j] = obPH[j + 1]; obPHN--; }
         obPH[obPHN] = ph; obPHN++;
      }
   }
   bool haveV = bi >= InpObVolN;
   double vavg = 0, v = ObVol(s);
   if(haveV) { for(int j = 1; j <= InpObVolN; j++) vavg += ObVol(s + j); vavg /= InpObVolN; }
   double rng = h - l, body = MathAbs(c - o);
   int sig = 0, k = 0;
   while(k < obZN)
   {
      if(obZT0[k] > t) { k++; continue; }               // its candle closed on this bar: from the next bar
      int d = obZD[k]; double lo = obZLo[k], hi = obZHi[k];
      bool dead = d == 1 ? c < lo : c > hi;              // a close beyond the far side ends the block
      if(obZSt[k] == 0)
      {
         if((long)(t - obZT0[k]) > (long)InpObDays * 86400 || dead) { ObDelZone(k); continue; }
         if(l <= hi && h >= lo) { obZSt[k] = 1; obZTb[k] = bi; }   // the first touch starts the episode
         else { k++; continue; }
      }
      if(bi - obZTb[k] >= InpObEpi || dead) { ObDelZone(k); continue; }
      if(rng <= 0) { k++; continue; }
      if(obZAb[k] && (d == 1 ? c > o : c < o) && body >= InpObAggBody / 100.0 * rng) { sig = d; ObDelZone(k); continue; }   // aggression: traded once
      if(haveV && l <= hi && h >= lo)
      {
         double wk = d == 1 ? MathMin(o, c) - l : h - MathMax(o, c);
         if(v > InpObVolMult * vavg && body < InpObAbsBody / 100.0 * rng && wk >= InpObAbsWick / 100.0 * rng) obZAb[k] = true;   // absorption
      }
      k++;
   }
   datetime tc = t + PeriodSeconds(_Period);
   for(int q = 0; q < obTfN; q++) if(obCurOn[q] && (long)tc / (obTfM[q] * 60) != obCurK[q]) ObClose(q, tc);   // this bar ends the candle
   if(gCanDraw && InpObShow)
      for(int z = 0; z < obZN; z++) ObjectSetInteger(0, "ARM_OBZ" + IntegerToString(obZId[z]), OBJPROP_TIME, 1, tc);
   if(sig == 0) return;
   double buf = InpObBufTk * TickSize();
   obSig = sig;
   obStopC = sig == 1 ? l - buf : h + buf;
   if(sig == 1) { for(int j = obPLN - 1; j >= 0; j--) if(obPL[j] < c) { obStopS = obPL[j] - buf; break; } }
   else         { for(int j = obPHN - 1; j >= 0; j--) if(obPH[j] > c) { obStopS = obPH[j] + buf; break; } }
}

'''

ARM = r'''   // v6.0 order block setup: at the aggression candle's close, a market entry on the next bar (one trade at a time: a VWAP setup armed on this bar comes first)
   if(gSrcO && !vArmed && canArm && obSig != 0)
   {
      bool isL = obSig == 1; double d = isL ? 1 : -1;
      double stop = InpObStop == OBS_CANDLE ? obStopC : obStopS;
      double risk = d * (c - stop);
      if(stop > 0 && risk >= MathMax(TickSize(), InpObMinTk * TickSize()) && RoundTick(stop) != RoundTick(c))
      {
         if(MathAbs(st) == 1 && !trGhost) evCancel = 2;
         st = isL ? 1 : -1; armBar = bi; lim = c; stp = stop; stp0 = stop; trRisk = risk; trHalf = false; trGhost = false; trSkip = 0; trMkt = true; trSrc = 2;
         t1 = lim + d * gpTp1R * risk; t2 = lim + d * gpTp2R * risk; t3 = lim + d * gpTp3R * risk; t4 = lim + d * gpTp4R * risk;
         tF = gpExitAt == EXIT_TP1 ? t1 : gpExitAt == EXIT_TP2 ? t2 : gpExitAt == EXIT_TP3 ? t3 : t4;
         evArm = true; evArmL = isL;
      }
   }
'''

CHECKS = r'''   if(InpObFvgN < 2 || InpObFvgN > 5 || InpObEpi < 1 || InpObDays < 1 || InpObVolN < 1 || InpObVolN > 500 || InpObVolMult <= 0 || InpObAbsBody <= 0 || InpObAbsBody > 100 ||
      InpObAbsWick <= 0 || InpObAbsWick > 100 || InpObAggBody <= 0 || InpObAggBody > 100 || InpObBufTk < 0 || InpObMinTk < 1)
   { Print("Order block: the gap within 2 - 5 candles, the episode, the days and the volume average 1 or more (volume average at most 500), the volume x above 0, the % 1 - 100, the buffer 0 or more and the smallest stop 1 tick or more."); return INIT_PARAMETERS_INCORRECT; }
   if(gSrcO && obTfN == 0) Print("Order block: no order block timeframe above this chart's (", TfName((int)_Period), "), so no order block trades. Choose M3 - H4 above the chart's timeframe.");
'''
