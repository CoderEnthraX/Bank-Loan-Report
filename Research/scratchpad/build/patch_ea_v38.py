"""v3.8 EA patch: VWAP skip rules, kill zones / daily news follow summer time, Crooks TP1 rule % and any final exit."""
import sys
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(F).read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('count %d != %d for: %s' % (c, n, old[:90]))
    s = s.replace(old, new)

# header box (same width as the line above it)
ref = '//| v3.7.1: server clock option for EU summer time (e.g. FxPro).     |'
w = len(ref)
def box(t): return '//| ' + t.ljust(w - 6) + ' |'
add = [box('v3.8: VWAP skip rules (stop beyond / touched / entry too close),'),
       box('kill zones and daily news follow summer time, TP1 rule % and'),
       box('any final exit.')]
for a in add: assert len(a) == w, a
rep(ref + '\n', ref + '\n' + '\n'.join(add) + '\n')
rep('#property version   "3.71"', '#property version   "3.80"')
rep('TblAdd("AUCTION RETEST", "EA v3.7.1", white', 'TblAdd("AUCTION RETEST", "EA v3.8", white')

# inputs
rep('input ENUM_VW_UNIT InpMaxVwUnit = VWU_ATR; //   ...measured in ATR or in price\n',
    'input ENUM_VW_UNIT InpMaxVwUnit = VWU_ATR; //   ...measured in ATR or in price\n'
    'input bool   InpStopVwOn   = false; // Skip when the stop is beyond the VWAP\n'
    'input double InpStopVwBuf  = 0.0;   //   buffer (x ATR; 0 = stop on the trade\'s side, -1 = up to 1 ATR past it)\n'
    'input bool   InpTouchVwOn  = false; // Skip when the VWAP was touched in the last N candles\n'
    'input int    InpTouchVwN   = 3;     //   N candles (1 = the signal candle only)\n'
    'input bool   InpEntVwOn    = false; // Skip when the entry is too close to the VWAP\n'
    'input double InpEntVwAtr   = 0.75;  //   min distance of the entry from the VWAP (x ATR)\n')
rep('input ENUM_KZ_SHIFT InpKzShift = KZ_0; //   shift all kill zones (daylight saving)\n',
    'input bool   InpKzAuto    = true;  //   follow London / New York summer time (winter: those zones 1 hour later)\n'
    'input ENUM_KZ_SHIFT InpKzShift = KZ_0; //   shift all kill zones (on top of the summer time switch)\n')
rep('input int    InpDNewsDur  = 60;    //   length (minutes)\n',
    'input int    InpDNewsDur  = 60;    //   length (minutes)\n'
    'input bool   InpDNewsAuto = true;  //   keep the same New York time all year (US winter time: 1 hour later)\n')
rep('input bool   InpCrkT1    = true;   // Crooks at exit TP1: bank the loss at TP1 with half, rest to TP2\n',
    'input bool   InpCrkT1    = true;   // Crooks TP1 rule (exit TP1): bank the loss at TP1 with part, rest to TP2\n')
rep('input ENUM_T1_STOP InpCrkT1Stop = T1S_TIGHT; //   ...stop before TP1 (the size is the same; the hard cap covers the real stop-out loss)\n',
    'input ENUM_T1_STOP InpCrkT1Stop = T1S_TIGHT; //   ...stop before TP1 (the size is the same; the hard cap covers the real stop-out loss)\n'
    'input double InpCrkT1Pct = 50.0;   //   ...% closed at TP1 (10-90; that part alone banks the whole loss)\n'
    'input bool   InpCrkT1Any = false;  //   ...with any final exit (not only TP1; the rest still runs to TP2)\n')

# globals
rep('int      trSkip = 0;               // why the setup is a ghost: 1 too far from VWAP, 2 choppy VWAP session, 3 1h EMA20 too fast, 4 too close to VWAP, 5 beyond max VWAP distance\n',
    'int      trSkip = 0;               // why the setup is a ghost: 1 too far from VWAP, 2 choppy VWAP session, 3 1h EMA20 too fast, 4 too close to VWAP, 5 beyond max VWAP distance,\n'
    '                                   // 6 stop beyond the VWAP, 7 VWAP touched recently, 8 entry too close to the VWAP\n')
rep('int      vxSide = 0, vxN = 0;\n',
    'int      vxSide = 0, vxN = 0;\n'
    'int      tchL = 1000000, tchS = 1000000;   // candles since the candle range last reached the VWAP (long side: the low, short side: the high); 0 = this candle\n')

# summer time and kill zones
rep('int LastSunday(int y, int mon) { int d = NthSunday(y, mon, 1); while(d + 7 <= 31) d += 7; return d; }   // March / October (31 days)\n',
    'int LastSunday(int y, int mon) { int d = NthSunday(y, mon, 1); while(d + 7 <= 31) d += 7; return d; }   // March / October (31 days)\n'
    'datetime MkTime(int y, int mon, int day, int hr) { MqlDateTime d; ZeroMemory(d); d.year = y; d.mon = mon; d.day = day; d.hour = hr; return StructToTime(d); }\n'
    '// British summer time at a UTC time: 01:00 UTC on the last Sunday of March to 01:00 UTC on the last Sunday of October\n'
    'bool UkSummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(d.year, 3, LastSunday(d.year, 3), 1) && utc < MkTime(d.year, 10, LastSunday(d.year, 10), 1); }\n'
    '// New York daylight time at a UTC time: 07:00 UTC on the second Sunday of March to 06:00 UTC on the first Sunday of November\n'
    'bool NySummer(datetime utc) { MqlDateTime d; TimeToStruct(utc, d); return utc >= MkTime(d.year, 3, NthSunday(d.year, 3, 2), 7) && utc < MkTime(d.year, 11, NthSunday(d.year, 11, 1), 6); }\n')
rep('''// kill zone in Indian minutes of the day, moved by the shift input; the end is exclusive
bool     InKz(int m, int startM, int endM)
{
   int sh = (int)InpKzShift * 60;''',
'''// kill zone in Indian minutes of the day, moved by the shift input and by extra minutes (winter time); the end is exclusive
bool     InKz(int m, int startM, int endM, int extra)
{
   int sh = (int)InpKzShift * 60 + extra;''')
rep('''   int kzM = MinOfDay(UtcTime(t) + 19800);   // Indian Standard Time = UTC + 5:30
   gKzOk = !InpKzOn || (InpKzAsia && InKz(kzM, 330, 570)) || (InpKzLon && InKz(kzM, 690, 870)) || (InpKzNy && InKz(kzM, 990, 1170)) || (InpKzLc && InKz(kzM, 1170, 1290));''',
'''   datetime utcT = UtcTime(t);
   int kzM = MinOfDay(utcT + 19800);   // Indian Standard Time = UTC + 5:30
   // the times are the summer times: London / London close move 1 hour later in London winter time, New York in New York winter time
   int lonSh = InpKzAuto && !UkSummer(utcT) ? 60 : 0, nySh = InpKzAuto && !NySummer(utcT) ? 60 : 0;
   gKzOk = !InpKzOn || (InpKzAsia && InKz(kzM, 330, 570, 0)) || (InpKzLon && InKz(kzM, 690, 870, lonSh)) || (InpKzNy && InKz(kzM, 990, 1170, nySh)) || (InpKzLc && InKz(kzM, 1170, 1290, lonSh));''')

# touch counters, every bar
rep('''   double vwap = cumW > 0 ? cumPV / cumW : cumP / cumN;
''', '''   double vwap = cumW > 0 ? cumPV / cumW : cumP / cumN;
   tchL = l <= vwap ? 0 : (tchL < 1000000 ? tchL + 1 : 1000000);   // candles since the range last reached the VWAP (every bar, warm or not)
   tchS = h >= vwap ? 0 : (tchS < 1000000 ? tchS + 1 : 1000000);
''')

# the three skip rules
rep('''         bool ghost = zNo || chopNo || emaNo || nearNo || farNo;''',
'''         // signal still on the VWAP: the stop on the other side of it, the VWAP touched in the last N candles, the entry too close to it
         bool stopNo = InpStopVwOn && d * (stop - vwap) < InpStopVwBuf * atr;
         bool tchNo = InpTouchVwOn && (isL ? tchL : tchS) < InpTouchVwN;
         bool entNo = InpEntVwOn && d * (entry - vwap) < InpEntVwAtr * atr;
         bool ghost = zNo || chopNo || emaNo || nearNo || farNo || stopNo || tchNo || entNo;''')
rep('''         trSkip = zNo ? 1 : (chopNo ? 2 : (emaNo ? 3 : (nearNo ? 4 : (farNo ? 5 : 0))));''',
'''         trSkip = zNo ? 1 : (chopNo ? 2 : (emaNo ? 3 : (nearNo ? 4 : (farNo ? 5 : (stopNo ? 6 : (tchNo ? 7 : (entNo ? 8 : 0)))))));''')
rep('''   string why = trSkip == 1 ? "TOO FAR FROM VWAP" : (trSkip == 2 ? "CHOPPY VWAP SESSION" : (trSkip == 3 ? "1H EMA20 TOO FAST" : (trSkip == 4 ? "TOO CLOSE TO VWAP" : "BEYOND MAX VWAP DISTANCE")));''',
'''   string why = trSkip == 1 ? "TOO FAR FROM VWAP" : (trSkip == 2 ? "CHOPPY VWAP SESSION" : (trSkip == 3 ? "1H EMA20 TOO FAST" : (trSkip == 4 ? "TOO CLOSE TO VWAP" :
                (trSkip == 5 ? "BEYOND MAX VWAP DISTANCE" : (trSkip == 6 ? "STOP BEYOND VWAP" : (trSkip == 7 ? "VWAP TOUCHED RECENTLY" : "ENTRY TOO CLOSE TO VWAP"))))));''')
rep('''   if(InpNoChase || InpChopOn || InpEmaOn || InpMinVwOn || InpMaxVwOn) TblAdd("SKIPPED BY FILTERS"''',
    '''   if(InpNoChase || InpChopOn || InpEmaOn || InpMinVwOn || InpMaxVwOn || InpStopVwOn || InpTouchVwOn || InpEntVwOn) TblAdd("SKIPPED BY FILTERS"''')
rep('''   vxSide = 0; vxN = 0; hK = -1;''', '''   vxSide = 0; vxN = 0; tchL = 1000000; tchS = 1000000; hK = -1;''')

# Crooks TP1 rule: part p at TP1, any final exit
rep('''//--- Crooks TP1 rule (exit at TP1, recovery trades): half of a double position banks the recovery amount at TP1, the rest runs to TP2.
//--- Stop distance (bid chart) where a stop-out loses exactly that amount: TP1 / 2 - 1.5 x costs, on the tick grid toward the entry; 0 = not possible
double CrkT1Dist()
{
   if(!InpCrkT1 || InpExitAt != EXIT_TP1 || !CrkRecNext()) return 0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0) return 0;
   double spr = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID));
   double d = MathFloor((InpTp1R * trRisk / 2.0 - 1.5 * (spr + InpCommLot * ts / tv)) / ts + 1e-9) * ts;
   return d >= ts ? d : 0;
}''',
'''//--- Crooks TP1 rule (exit at TP1, or any exit with InpCrkT1Any; recovery trades): the part p closed at TP1 banks the recovery amount, the rest runs to TP2.
//--- The size is the one whose stop-out at distance d loses exactly that amount: d = p x TP1 - (1 + p) x costs (p = 0.5: TP1 / 2 - 1.5 x costs),
//--- on the tick grid toward the entry (bid chart); 0 = not possible
double CrkT1P() { return MathMax(10.0, MathMin(90.0, InpCrkT1Pct)) / 100.0; }
double CrkT1Dist()
{
   if(!InpCrkT1 || (InpExitAt != EXIT_TP1 && !InpCrkT1Any) || !CrkRecNext()) return 0;
   double tv = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE), ts = TickSize();
   if(tv <= 0 || ts <= 0) return 0;
   double spr = MathMax(0.0, SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)), p = CrkT1P();
   double d = MathFloor((p * InpTp1R * trRisk - (1.0 + p) * (spr + InpCommLot * ts / tv)) / ts + 1e-9) * ts;
   return d >= ts ? d : 0;
}''')
rep('''//--- Crooks TP1 rule: close half at market (rounded UP to the lot step, so at least half banks the recovery amount); the rest's stop then moves to the entry
void T1Half(ulong tk, double vol)
{
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double cv = MathCeil(exLots * 0.5 / step - 1e-9) * step;''',
'''//--- Crooks TP1 rule: close the TP1 part at market (rounded UP to the lot step, so it banks at least the recovery amount); the rest's stop then moves to the entry
void T1Half(ulong tk, double vol)
{
   double step = InpLotStep > 0 ? InpLotStep : SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double cv = MathCeil(exLots * CrkT1P() / step - 1e-9) * step;''')
rep('''      // Crooks TP1 rule: half closes at TP1 and banks the whole recovery amount, then the rest's stop moves to the entry (it runs to TP2)''',
    '''      // Crooks TP1 rule: the TP1 part closes at TP1 and banks the whole recovery amount, then the rest's stop moves to the entry (it runs to TP2)''')
rep('''   // Crooks TP1 rule: the engine counted TP1 on the bar that just closed but no tick booked the half (missed tick, failed close): book it now
   if(evExit && evWin && exState == 2 && exMine && exT1 && !exT1Half && pos) T1Half(pTk, pVol);''',
'''   // Crooks TP1 rule: TP1 was reached but no tick booked the TP1 part (missed tick, failed close): book it now
   // (exit TP1: the engine won on the bar that just closed; any exit: that bar, after the fill bar, reached TP1)
   bool t1Bar = exT1 && exSynced && lastFill >= 0 && lastFill < bi && (exL ? Hi(1) >= exT1Tp1 + exCostPx : Lo(1) <= exT1Tp1 - exCostPx);
   if(((evExit && evWin) || t1Bar) && exState == 2 && exMine && exT1 && !exT1Half && pos) T1Half(pTk, pVol);''')

# news window follows New York time
rep('''   if(InpDNewsOn)
   {
      int cur = MinOfDay(ut), prv = MinOfDay(utPrev), s0 = InpDNewsH * 60 + InpDNewsM, e0 = s0 + InpDNewsDur;''',
'''   if(InpDNewsOn)
   {
      // the window is set in summer time; with InpDNewsAuto it moves 1 hour later while New York is on winter time (same New York time all year)
      int sh = InpDNewsAuto && !NySummer(ut - (datetime)(InpUserGMT * 3600)) ? 60 : 0;
      int cur = MinOfDay(ut), prv = MinOfDay(utPrev), s0 = (InpDNewsH * 60 + InpDNewsM + sh) % 1440, e0 = s0 + InpDNewsDur;''')

# input checks
rep('''   if(InpMaxVwOn && InpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."); return INIT_PARAMETERS_INCORRECT; }''',
'''   if(InpMaxVwOn && InpMaxVwDist <= 0) { Print("Max distance from VWAP must be above 0."); return INIT_PARAMETERS_INCORRECT; }
   if(InpTouchVwOn && InpTouchVwN < 1) { Print("VWAP touched in the last N candles: N must be 1 or more."); return INIT_PARAMETERS_INCORRECT; }
   if(InpCrkT1 && (InpCrkT1Pct < 10 || InpCrkT1Pct > 90)) { Print("Crooks TP1 rule: % closed at TP1 must be 10 to 90."); return INIT_PARAMETERS_INCORRECT; }''')
open(F, 'w').write(s)
print('patched', len(s))
