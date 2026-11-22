"""v6.1 VWAP Orderflow Sniper setup: MQL5 text pieces for build_sn_ea.py (the same steps as sn_pine_parts.ENGINE / ARM)."""

INPUTS = r'''//--- v6.1 SETUPS: the VWAP retest setup, the VWAP Orderflow Sniper setup, or both (one trade at a time; or the true grid: each setup its own
//--- trade, magic and money)
enum ENUM_SETUPS { SET_VWAP = 0,   // VWAP retest only
                   SET_SN   = 1,   // Sniper only
                   SET_ONE  = 2,   // Both: one trade at a time
                   SET_GRID = 3 }; // Both: true grid (hedging account; Sniper magic = magic + 1)
enum ENUM_SN_DS   { SNDS_LTF = 0,   // Intrabar (lower timeframe)
                    SNDS_EST = 1 }; // Candle estimate
enum ENUM_SN_MODE { SNM_SNIPER = 0, // Sniper (absorption + aggression)
                    SNM_AGGR   = 1, // Aggression only
                    SNM_BRK    = 2 };// Absorption breakout
enum ENUM_SN_ZONE { SNZ_VWAP = 0,   // VWAP
                    SNZ_BAND = 1,   // VWAP or band #1
                    SNZ_ANY  = 2 }; // Anywhere
enum ENUM_SN_BAND { SNB_SD  = 0,    // Standard deviation
                    SNB_PCT = 1 };  // Percentage
enum ENUM_SN_CVD  { SNC_OFF  = 0,   // Off
                    SNC_ROLL = 1,   // Rolling delta
                    SNC_SESS = 2 }; // Session CVD
enum ENUM_SN_ENTRY { SNE_CLOSE = 0, // Signal close (market)
                     SNE_MID   = 1, // Signal bar midpoint (limit)
                     SNE_VWAP  = 2 };// VWAP retest (limit)
enum ENUM_SN_STOP { SNS_STRUCT = 0, // Absorption / swing
                    SNS_ATR    = 1, // ATR
                    SNS_PTS    = 2, // Fixed points
                    SNS_PCT    = 3 };// Percent

input group "SETUPS AND VWAP ORDERFLOW SNIPER"
input ENUM_SETUPS InpSetups    = SET_ONE;      // Setups to trade (a strategy preset: VWAP retest only, as tested)
input double InpSnAggRatio  = 2.2;     // Sniper: aggression ratio (one side x the other)
input double InpSnAbsSens   = 1.2;     // Sniper: absorption sensitivity (relative volume)
input ENUM_SN_DS InpSnDelta = SNDS_LTF; // Sniper: delta source (intrabar: lower-timeframe candles; candle estimate below 2 of them)
input bool   InpSnCustOn    = false;   // Sniper: custom lower timeframe
input ENUM_TIMEFRAMES InpSnCustLtf = PERIOD_M1; //   ...lower timeframe (used when below the chart's; else auto: M1 up to H1, M5 up to H4, M15 on D1)
input int    InpSnVolLen    = 20;      // Sniper: volume average length (2 - 200)
input int    InpSnAtrLen    = 14;      // Sniper: ATR length (1 - 200)
input int    InpSnAbsLen    = 5;       // Sniper: absorption lookback (bars, 2 - 200)
input double InpSnDivMin    = 15.0;    // Sniper: delta divergence min %
input double InpSnWickPct   = 40.0;    // Sniper: rejection wick min %
input double InpSnAggRelV   = 1.0;     // Sniper: aggression min relative volume
input double InpSnAggBody   = 50.0;    // Sniper: aggression min body %
input ENUM_SN_MODE InpSnMode = SNM_SNIPER; // Sniper: signal mode
input int    InpSnExpiry    = 10;      // Sniper: setup expiry (bars)
input ENUM_SN_ZONE InpSnZone = SNZ_BAND; // Sniper: absorption location
input ENUM_SN_BAND InpSnBandMode = SNB_SD; // Sniper: band #1 by
input double InpSnBandMult  = 1.0;     //   ...band #1 x
input double InpSnZoneAtr   = 0.75;    // Sniper: VWAP zone width (ATR)
input double InpSnMaxDist   = 2.5;     // Sniper: max distance from the VWAP (ATR, 0 = off)
input ENUM_SN_CVD InpSnCvd  = SNC_ROLL; // Sniper: CVD confirmation
input int    InpSnCvdLen    = 3;       //   ...rolling delta length (1 - 200)
input bool   InpSnSlopeOn   = false;   // Sniper: VWAP slope filter
input int    InpSnSlopeLen  = 5;       //   ...slope length (1 - 200)
input int    InpSnCool      = 3;       // Sniper: bars between signals
input ENUM_SN_ENTRY InpSnEntry = SNE_CLOSE; // Sniper: entry (a limit waits for the retest window)
input double InpSnOffset    = 0.0;     // Sniper: entry offset (price, a better price; above 0 = a limit)
input ENUM_SN_STOP InpSnSlMode = SNS_STRUCT; // Sniper: stop
input double InpSnSlAtr     = 1.5;     //   ...ATR x
input double InpSnSlPts     = 5.0;     //   ...fixed points (price)
input double InpSnSlPct     = 0.25;    //   ...percent %
input double InpSnSlBuf     = 0.15;    //   ...structure buffer (ATR)
input int    InpSnSwingLen  = 5;       //   ...swing lookback (bars, 1 - 200)
input double InpSnMinRisk   = 0.3;     //   ...structure risk min (ATR)
input double InpSnMaxRisk   = 4.0;     //   ...structure risk max (ATR)
input bool   InpSnShowZone  = true;    // Sniper: draw the absorption zones
ENUM_SETUPS SetupsUse() { return InpPreset == PRE_CUSTOM ? InpSetups : SET_VWAP; }   // a strategy preset trades the VWAP retest setup only

'''

GLOBALS = r'''bool     trMkt = false;            // v6.1: the setup enters at market (a Sniper signal at its close)
int      trSrc = 0;                // v6.1: the setup's source: 1 VWAP retest, 2 Sniper
//--- v6.1 VWAP Orderflow Sniper state (the same steps as the TradingView file; per bar values kept in rings of the last SN_RING bars)
#define  SN_RING 256
bool     gSrcV = true, gSrcO = false;   // the setups this engine arms: VWAP retest, Sniper
int      gLeg = 0;                      // 0 = the VWAP retest leg (or the only one), 1 = the Sniper leg of the true grid
double   snDl[SN_RING], snTv[SN_RING], snRv[SN_RING], snVw[SN_RING];   // delta, buy + sell volume, volume, VWAP of each bar
double   snTrSum = 0, snAtrV = 0; int snTrN = 0;                      // the Sniper ATR (Wilder, like ta.atr)
double   snCvdS = 0;                                                    // the delta since the VWAP started
long     snBullArm = -1, snBearArm = -1, snLastSig = -1;               // armed setups (bar index; -1 = none), the last signal
double   snBullLo = 0, snBullHi = 0, snBearLo = 0, snBearHi = 0;
long     snBullBox = 0, snBearBox = 0, snBoxSeq = 0;                     // their drawn zones (0 = none)
int      snSig = 0; double snEnt = 0, snStp = 0;                        // this bar's Sniper signal, its entry and stop
'''

FUNCS = r'''//=== v6.1 VWAP ORDERFLOW SNIPER (same as the TradingView file) ===========
double SnVol(ENUM_TIMEFRAMES tf, int s)
{
   long rv = iVolume(_Symbol, tf, s), tv = iTickVolume(_Symbol, tf, s);
   return rv > 0 ? (double)rv : (double)tv;
}
//--- the lower timeframe of the intrabar delta: custom when below the chart's, else M1 up to H1, M5 up to H4, M15 up to D1, H1 above
ENUM_TIMEFRAMES SnLtf()
{
   int cs = PeriodSeconds(_Period);
   if(InpSnCustOn && PeriodSeconds(InpSnCustLtf) < cs) return InpSnCustLtf;
   return cs <= 60 ? _Period : cs <= 3600 ? PERIOD_M1 : cs <= 14400 ? PERIOD_M5 : cs <= 86400 ? PERIOD_M15 : PERIOD_H1;
}
//--- the chart bar opening at t split into its lower-timeframe candles: up = buying, down = selling, unchanged = by the previous close
bool SnIntra(datetime t, double &bv, double &sv)
{
   bv = 0; sv = 0;
   ENUM_TIMEFRAMES lt = SnLtf();
   int cs = PeriodSeconds(_Period), nb = Bars(_Symbol, lt), k = iBarShift(_Symbol, lt, t, false), n = 0;
   if(k < 0) return false;
   if(iTime(_Symbol, lt, k) < t) k--;
   for(; k >= 0; k--)
   {
      datetime tk = iTime(_Symbol, lt, k);
      if(tk >= t + cs) break;
      if(tk < t) continue;
      double o1 = iOpen(_Symbol, lt, k), c1 = iClose(_Symbol, lt, k), pc = k + 1 < nb ? iClose(_Symbol, lt, k + 1) : c1;
      double dr = c1 > o1 ? 1.0 : c1 < o1 ? -1.0 : (c1 > pc ? 1.0 : c1 < pc ? -1.0 : 0.0);
      double v = SnVol(lt, k);
      bv += dr > 0 ? v : dr < 0 ? 0.0 : v * 0.5;
      sv += dr < 0 ? v : dr > 0 ? 0.0 : v * 0.5;
      n++;
   }
   return n >= 2;
}
//--- the sum of the last n values of a ring (oldest first)
double SnSum(const double &r[], int n)
{
   double sm = 0;
   for(int i = n - 1; i >= 0; i--) sm += r[(int)((bi - i) % SN_RING)];
   return sm;
}
void SnZoneDraw(long &id, datetime t, double hi, double lo, bool bull)
{
   if(!gCanDraw || !InpSnShowZone) return;
   if(id == 0)
   {
      snBoxSeq++; id = snBoxSeq;
      string nm = "ARM_SNZ" + IntegerToString(id);
      ObjectCreate(0, nm, OBJ_RECTANGLE, 0, t, hi, t + PeriodSeconds(_Period) * InpSnExpiry, lo);
      ObjectSetInteger(0, nm, OBJPROP_COLOR, bull ? C'41,98,255' : C'255,152,0');
      ObjectSetInteger(0, nm, OBJPROP_FILL, false);
      ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_DOT);
      ObjectSetInteger(0, nm, OBJPROP_BACK, true);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
   }
   else
   {
      string nm = "ARM_SNZ" + IntegerToString(id);
      ObjectSetDouble(0, nm, OBJPROP_PRICE, 0, hi);
      ObjectSetDouble(0, nm, OBJPROP_PRICE, 1, lo);
   }
}
void SnReset()
{
   ArrayInitialize(snDl, 0.0); ArrayInitialize(snTv, 0.0); ArrayInitialize(snRv, 0.0); ArrayInitialize(snVw, 0.0);
   snTrSum = 0; snAtrV = 0; snTrN = 0; snCvdS = 0;
   snBullArm = -1; snBearArm = -1; snLastSig = -1; snBullLo = 0; snBullHi = 0; snBearLo = 0; snBearHi = 0;
   snBullBox = 0; snBearBox = 0; snBoxSeq = 0; snSig = 0; snEnt = 0; snStp = 0;
}
//--- one closed chart bar (shift s, open time t) with the engine's VWAP: buy / sell volume, absorption, aggression, the armed setups and
//--- the signal -> snSig (1 buy, -1 sell, 0 none) with its entry snEnt and stop snStp
void SnBar(int s, datetime t, double o, double h, double l, double c, double vwap, double vwSd, bool newAnchor)
{
   snSig = 0; snEnt = 0; snStp = 0;
   int ri = (int)(bi % SN_RING);
   long nb = bi + 1;                                     // bars processed (Pine: na until a window is full)
   double v = SnVol(_Period, s);
   double tr = bi == 0 ? h - l : MathMax(MathMax(h - l, MathAbs(h - Cl(s + 1))), MathAbs(l - Cl(s + 1)));
   if(snTrN < InpSnAtrLen) { snTrSum += tr; snTrN++; if(snTrN == InpSnAtrLen) snAtrV = snTrSum / InpSnAtrLen; }
   else snAtrV = (1.0 / InpSnAtrLen) * tr + (1.0 - 1.0 / InpSnAtrLen) * snAtrV;
   bool atrOk = snTrN >= InpSnAtrLen;
   double sAtr = atrOk ? snAtrV : 0.0;
   bool avgOk = nb >= InpSnVolLen;
   double avg = 0;
   if(avgOk) { for(int j = InpSnVolLen - 1; j >= 0; j--) avg += SnVol(_Period, s + j); avg /= InpSnVolLen; }
   double relV = avgOk && avg > 0 ? v / avg : 0.0;
   double rng = h - l, bodyP = rng > 0 ? MathAbs(c - o) / rng : 0.0, clPos = rng > 0 ? (c - l) / rng : 0.5;
   double loW = MathMin(o, c) - l, upW = h - MathMax(o, c);
   double buyV = 0, sellV = 0;
   bool intra = InpSnDelta == SNDS_LTF && SnIntra(t, buyV, sellV);
   if(!intra) { buyV = rng > 0 ? v * (c - l) / rng : v * 0.5; sellV = v - buyV; }
   double totV = buyV + sellV, delta = buyV - sellV;
   double bullR = buyV / MathMax(MathMax(sellV, totV * 0.01), 0.000001), bearR = sellV / MathMax(MathMax(buyV, totV * 0.01), 0.000001);
   snDl[ri] = delta; snTv[ri] = totV; snRv[ri] = v; snVw[ri] = vwap;
   snCvdS = newAnchor ? delta : snCvdS + delta;
   bool rollOk = nb >= InpSnCvdLen; double roll = rollOk ? SnSum(snDl, InpSnCvdLen) : 0.0;
   bool bullAg = c > o && bullR >= InpSnAggRatio && relV >= InpSnAggRelV && bodyP * 100.0 >= InpSnAggBody;
   bool bearAg = c < o && bearR >= InpSnAggRatio && relV >= InpSnAggRelV && bodyP * 100.0 >= InpSnAggBody;
   bool winOk = nb >= InpSnAbsLen;
   double loL = 0, hiH = 0, winD = 0, winV = 0, winRV = 0;
   if(winOk)
   {
      loL = Lo(s); hiH = Hi(s);
      for(int j = 1; j < InpSnAbsLen; j++) { loL = MathMin(loL, Lo(s + j)); hiH = MathMax(hiH, Hi(s + j)); }
      winD = SnSum(snDl, InpSnAbsLen); winV = SnSum(snTv, InpSnAbsLen); winRV = SnSum(snRv, InpSnAbsLen);
   }
   double winDP = winOk && winV > 0 ? 100.0 * winD / winV : 0.0;
   double winRel = avgOk && avg > 0 && winOk ? winRV / (avg * InpSnAbsLen) : 0.0;
   bool backOk = nb > InpSnAbsLen; double back = backOk ? Cl(s + InpSnAbsLen) : 0.0;
   bool effort = relV >= InpSnAbsSens;
   bool bullAb = (effort && loW >= rng * InpSnWickPct / 100.0 && clPos >= 0.5) || (intra && effort && delta < 0 && c >= o) ||
                 (relV >= InpSnAbsSens * 1.5 && atrOk && rng <= sAtr * 0.7 && winOk && l <= loL) || (winDP <= -InpSnDivMin && backOk && c >= back && winRel >= 1.0);
   bool bearAb = (effort && upW >= rng * InpSnWickPct / 100.0 && clPos <= 0.5) || (intra && effort && delta > 0 && c <= o) ||
                 (relV >= InpSnAbsSens * 1.5 && atrOk && rng <= sAtr * 0.7 && winOk && h >= hiH) || (winDP >= InpSnDivMin && backOk && c <= back && winRel >= 1.0);
   double basis = InpSnBandMode == SNB_SD ? vwSd : vwap * 0.01;
   double up1 = vwap + basis * InpSnBandMult, lo1 = vwap - basis * InpSnBandMult;
   double zw = InpSnZoneAtr * sAtr;
   bool tV = atrOk && l <= vwap + zw && h >= vwap - zw, tU = atrOk && l <= up1 + zw && h >= up1 - zw, tL = atrOk && l <= lo1 + zw && h >= lo1 - zw;
   bool bullCtx = atrOk && c >= vwap - zw && (InpSnZone == SNZ_ANY || tV || (InpSnZone == SNZ_BAND && tU));
   bool bearCtx = atrOk && c <= vwap + zw && (InpSnZone == SNZ_ANY || tV || (InpSnZone == SNZ_BAND && tL));
   double dist = atrOk && sAtr > 0 ? MathAbs(c - vwap) / sAtr : 0.0;
   bool distOk = InpSnMaxDist <= 0 || dist <= InpSnMaxDist;
   bool slopeOk = nb > InpSnSlopeLen; double slope = slopeOk ? vwap - snVw[(int)((bi - InpSnSlopeLen) % SN_RING)] : 0.0;
   bool swOk = nb >= InpSnSwingLen;
   double swLo = 0, swHi = 0;
   if(swOk) { swLo = Lo(s); swHi = Hi(s); for(int j = 1; j < InpSnSwingLen; j++) { swLo = MathMin(swLo, Lo(s + j)); swHi = MathMax(swHi, Hi(s + j)); } }
   bool bullArmed = snBullArm >= 0 && bi - snBullArm <= InpSnExpiry;
   bool bearArmed = snBearArm >= 0 && bi - snBearArm <= InpSnExpiry;
   if(bullArmed && ((atrOk && c < vwap - zw) || c < snBullLo)) { snBullArm = -1; bullArmed = false; }   // the setup ends: the VWAP side lost or the zone broken
   if(bearArmed && ((atrOk && c > vwap + zw) || c > snBearHi)) { snBearArm = -1; bearArmed = false; }
   if(bullAb && bullCtx)
   {
      if(bullArmed) { snBullLo = MathMin(snBullLo, l); snBullHi = MathMax(snBullHi, h); if(snBullBox != 0) SnZoneDraw(snBullBox, t, snBullHi, snBullLo, true); }
      else { snBullLo = l; snBullHi = h; snBullBox = 0; SnZoneDraw(snBullBox, t, h, l, true); }
      snBullArm = bi; bullArmed = true;
   }
   if(bearAb && bearCtx)
   {
      if(bearArmed) { snBearLo = MathMin(snBearLo, l); snBearHi = MathMax(snBearHi, h); if(snBearBox != 0) SnZoneDraw(snBearBox, t, snBearHi, snBearLo, false); }
      else { snBearLo = l; snBearHi = h; snBearBox = 0; SnZoneDraw(snBearBox, t, h, l, false); }
      snBearArm = bi; bearArmed = true;
   }
   bool coolOk = snLastSig < 0 || bi - snLastSig >= InpSnCool;
   bool bullF = c > vwap && distOk && (!InpSnSlopeOn || (slopeOk && slope > 0)) && (InpSnCvd == SNC_OFF || (InpSnCvd == SNC_ROLL ? (rollOk && roll > 0) : snCvdS > 0)) && coolOk;
   bool bearF = c < vwap && distOk && (!InpSnSlopeOn || (slopeOk && slope < 0)) && (InpSnCvd == SNC_OFF || (InpSnCvd == SNC_ROLL ? (rollOk && roll < 0) : snCvdS < 0)) && coolOk;
   bool buy  = bullF && (InpSnMode == SNM_AGGR ? bullAg : InpSnMode == SNM_BRK ? (bullArmed && c > snBullHi && c > o) : (bullArmed && bullAg));
   bool sell = bearF && !buy && (InpSnMode == SNM_AGGR ? bearAg : InpSnMode == SNM_BRK ? (bearArmed && c < snBearLo && c < o) : (bearArmed && bearAg));
   if(!buy && !sell) return;
   int sd = buy ? 1 : -1;
   bool hasZ = sd == 1 ? bullArmed : bearArmed;
   double zExt = sd == 1 ? snBullLo : snBearHi;
   double base = InpSnEntry == SNE_MID ? (h + l) / 2.0 : InpSnEntry == SNE_VWAP ? (sd == 1 ? MathMin(c, vwap) : MathMax(c, vwap)) : c;
   double ent = base - sd * InpSnOffset;
   bool strOk = hasZ || swOk;
   double sStr = sd == 1 ? (hasZ ? MathMin(zExt, l) : swLo) - InpSnSlBuf * sAtr : (hasZ ? MathMax(zExt, h) : swHi) + InpSnSlBuf * sAtr;
   double risk = InpSnSlMode == SNS_ATR ? sAtr * InpSnSlAtr : InpSnSlMode == SNS_PTS ? InpSnSlPts : InpSnSlMode == SNS_PCT ? ent * InpSnSlPct / 100.0 : sd * (ent - sStr);
   if(InpSnSlMode == SNS_STRUCT) risk = MathMax(InpSnMinRisk * sAtr, MathMin(InpSnMaxRisk * sAtr, strOk ? risk : InpSnMinRisk * sAtr));
   if(!(risk > 0)) risk = MathMax(sAtr * 0.5, TickSize() * 10);
   snSig = sd; snEnt = ent; snStp = ent - sd * risk; snLastSig = bi;
   if(sd == 1) snBullArm = -1; else snBearArm = -1;
}

'''

ARM = r'''   // v6.1 Sniper setup: its entry (market at the signal close, or a limit) and stop (one trade at a time: a VWAP setup armed on this bar comes first)
   if(gSrcO && !vArmed && canArm && snSig != 0)
   {
      bool isL = snSig == 1; double d = isL ? 1 : -1;
      double risk = d * (snEnt - snStp);
      if(risk >= TickSize() && RoundTick(snStp) != RoundTick(snEnt))
      {
         if(MathAbs(st) == 1 && !trGhost) evCancel = 2;
         st = isL ? 1 : -1; armBar = bi; lim = snEnt; stp = snStp; stp0 = snStp; trRisk = risk; trHalf = false; trGhost = false; trSkip = 0; trMkt = snEnt == c; trSrc = 2;
         t1 = lim + d * gpTp1R * risk; t2 = lim + d * gpTp2R * risk; t3 = lim + d * gpTp3R * risk; t4 = lim + d * gpTp4R * risk;
         tF = gpExitAt == EXIT_TP1 ? t1 : gpExitAt == EXIT_TP2 ? t2 : gpExitAt == EXIT_TP3 ? t3 : t4;
         evArm = true; evArmL = isL;
      }
   }
'''

CHECKS = r'''   if(InpSnAggRatio < 1 || InpSnAbsSens <= 0 || InpSnVolLen < 2 || InpSnVolLen > 200 || InpSnAtrLen < 1 || InpSnAtrLen > 200 || InpSnAbsLen < 2 || InpSnAbsLen > 200 ||
      InpSnCvdLen < 1 || InpSnCvdLen > 200 || InpSnSlopeLen < 1 || InpSnSlopeLen > 200 || InpSnSwingLen < 1 || InpSnSwingLen > 200 || InpSnExpiry < 1 || InpSnCool < 0 ||
      InpSnDivMin < 1 || InpSnDivMin > 100 || InpSnWickPct < 10 || InpSnWickPct > 90 || InpSnAggRelV < 0 || InpSnAggBody < 0 || InpSnAggBody > 100 || InpSnBandMult < 0 ||
      InpSnZoneAtr < 0.05 || InpSnMaxDist < 0 || InpSnOffset < 0 || InpSnSlAtr < 0.1 || InpSnSlPts < 0.01 || InpSnSlPct < 0.01 || InpSnSlBuf < 0 || InpSnMinRisk < 0 || InpSnMaxRisk < 0.1)
   { Print("Sniper: aggression ratio 1 or more, the lengths 1 - 200 (volume average and absorption lookback 2 - 200), expiry 1 or more, divergence 1 - 100 %, wick 10 - 90 %, body 0 - 100 %, the zone width 0.05 ATR or more, the stop values above 0 and the offset 0 or more."); return INIT_PARAMETERS_INCORRECT; }
'''
