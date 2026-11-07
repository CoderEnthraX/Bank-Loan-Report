"""v3.9 EA patch: Crooks C rule after N losing recovery trades in a row (forget / % of the loss / wait for M wins / skip D trading days)."""
import sys
F = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(F).read()
def rep(old, new, n=1):
    global s
    c = s.count(old)
    if c != n: sys.exit('count %d != %d for: %s' % (c, n, old[:100]))
    s = s.replace(old, new)

# header and version
ref = '//| any final exit.                                                  |'
w = len(ref)
def box(t): return '//| ' + t.ljust(w - 6) + ' |'
add = [box('v3.9: Crooks C rule after N losing recovery trades in a row:'), box('forget the loss, a % of it, wait for M wins, or skip D days.')]
for a in add: assert len(a) == w, a
rep(ref + '\n', ref + '\n' + '\n'.join(add) + '\n')
rep('#property version   "3.80"', '#property version   "3.90"')
rep('TblAdd("AUCTION RETEST", "EA v3.8", white', 'TblAdd("AUCTION RETEST", "EA v3.9", white')

# enum + inputs
rep('''   REC_CRD   = 21  // Crooks D (base, base, recovery: every 3rd trade)
};
''', '''   REC_CRD   = 21  // Crooks D (base, base, recovery: every 3rd trade)
};
enum ENUM_CRK_PR { CPR_OFF    = 0,   // Off (Crooks C as now)
                   CPR_FORGET = 1,   // Forget the loss
                   CPR_PCT    = 2,   // Go for a % of the loss, forget it after N
                   CPR_WAIT   = 3,   // Wait for M wins in a row, then a loss and a win
                   CPR_SKIP   = 4 }; // Skip D trading days
''')
rep('''input int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)
''', '''input int    InpCrkCn    = 1;      //   ...N (1 = all on the trade after a win, 2 = half then the rest, ...)
input ENUM_CRK_PR InpCrkPr = CPR_OFF; // Crooks C: after N losing recovery trades in a row
input int    InpCrkPrN   = 2;      //   ...N losing recovery trades in a row
input double InpCrkPrPct = 50.0;   //   ...% of the loss each recovery trade goes for (the % rule, 10-100)
input int    InpCrkPrM   = 2;      //   ...M wins in a row to wait for (the wait rule)
input int    InpCrkPrD   = 3;      //   ...D trading days to skip (the skip rule; the rest of that day is skipped too)
input bool   InpCrkPrForget = false; //   ...forget the loss after the skipped days (the skip rule)
input bool   InpCrkPrAll = false;  //   ...count every day, not only the trading days (the skip rule)
''')

# state
rep('''int      crkP = 0;                                       // Crooks C over N wins: parts of the loss still to win back (0 = not set yet)
''', '''int      crkP = 0;                                       // Crooks C over N wins: parts of the loss still to win back (0 = not set yet)
int      crkF = 0;                                       // Crooks C rule: losing recovery trades in a row in this cycle
bool     crkWait = false; int crkWW = 0; bool crkNeedL = false;   // wait rule: waiting for M wins in a row (wins so far); then the next recovery needs a loss first
bool     crkSkip = false; int crkSkipLeft = 0; int crkUDay = -1;  // skip rule: trading paused, counted days still to skip, your day of the last live bar
''')

# helpers next to CrkParts()
rep('''int CrkParts() { int np = CrkNp(); return (crkP < 1 || crkP > np) ? np : crkP; }
''', '''int CrkParts() { int np = CrkNp(); return (crkP < 1 || crkP > np) ? np : crkP; }
//--- Crooks C rule after N losing recovery trades in a row (Crooks C only)
bool   CrkPrOn()  { return InpRec == REC_CRC && InpCrkPr != CPR_OFF; }
double CrkPrPct() { return CrkPrOn() && InpCrkPr == CPR_PCT ? MathMax(10.0, MathMin(100.0, InpCrkPrPct)) / 100.0 : 1.0; }
bool   CrkPause() { return CrkPrOn() && InpCrkPr == CPR_SKIP && crkSkip; }   // the skip rule pauses trading
void   CrkCycle() { crkL = 0; crkN = 0; crkP = CrkNp(); crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; }   // a new cycle at the base risk
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
''')

# recovery decision: the wait rule holds the recovery trade back
rep('''   if(InpRec == REC_CRC) return crkW && crkL > 0;''',
    '''   if(InpRec == REC_CRC) return crkW && crkL > 0 && !(CrkPrOn() && InpCrkPr == CPR_WAIT && (crkWait || crkNeedL));   // wait rule: not while waiting''')

# recovery amount: the % rule
rep('''         double x = crkL / (InpRec == REC_CRB ? InpCSplit : InpRec == REC_CRC ? CrkParts() : 1);
''', '''         double x = crkL / (InpRec == REC_CRB ? InpCSplit : InpRec == REC_CRC ? CrkParts() : 1) * (InpRec == REC_CRC ? CrkPrPct() : 1.0);   // % rule: a part of the loss
''')
rep('''         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; crkL = 0; crkN = 0; crkW = false; crkP = CrkNp();
''', '''         recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; CrkCycle(); crkW = false;
''')

# booking
rep('''   crkL = MathMax(0.0, crkL - exPnl);
   if(crkL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && crkRec)) { crkL = 0; crkN = 0; crkP = CrkNp(); }
   else { crkN++; crkP = !win ? CrkNp() : crkRec ? MathMax(1, CrkParts() - 1) : CrkParts(); }   // Crooks C over N wins: a loss starts the parts again
''', '''   bool lastPart = CrkParts() == 1;                     // this recovery trade went for the last part of the loss (Crooks C over N wins)
   crkL = MathMax(0.0, crkL - exPnl);
   if(crkL < 0.01 || ((InpRec == REC_CRA || InpRec == REC_CRD) && win && crkRec)) CrkCycle();
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
         }
      }
   }
''')

# taking a setup: the pause
rep('''   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock);   // the hard cap acts only on a signal that can be taken''',
    '''   bool crkPs = CrkPause();
   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock || crkPs);   // the hard cap acts only on a signal that can be taken''')
rep('''paused ? "paused" : dayBlock ? "streak stop" : v <= 0 ? "size 0" : "";''',
    '''paused ? "paused" : dayBlock ? "streak stop" : crkPs ? "Crooks C pause" : v <= 0 ? "size 0" : "";''')
rep('''   double v = capStop ? 0 : LotsFor(rAmt, sd, lim, isL, ld);''', '''   double v = (capStop || crkPs) ? 0 : LotsFor(rAmt, sd, lim, isL, ld);''')

# day counting for every live bar: caught-up bars and the bar that just closed (before the trade booking, like the strategy)
rep('''         ProcessBar(s); caught = true; if(gNewDay) gDayPend = true;
''', '''         ProcessBar(s); caught = true; if(gNewDay) gDayPend = true;
         CrkDayTick(iTime(_Symbol, _Period, s));                          // Crooks C skip rule: count the missed days too
''')
rep('''void OnNewBar()
{
   ProcessBar(1);
''', '''void OnNewBar()
{
   ProcessBar(1);
   CrkDayTick(iTime(_Symbol, _Period, 1));              // Crooks C skip rule: a new day in your time zone counts before this bar's booking
''')

# state text and the CROOKS row
rep('''capStop ? "HARD CAP: STOPPED" : newsBlk ? "NEWS WINDOW" : paused ? "PAUSED" : dayBlock ? "STREAK STOP TODAY" :''',
    '''capStop ? "HARD CAP: STOPPED" : newsBlk ? "NEWS WINDOW" : paused ? "PAUSED" : CrkPause() ? "CROOKS C PAUSE (" + IntegerToString(crkSkipLeft) + " days left)" : dayBlock ? "STREAK STOP TODAY" :''')
rep('''                 + (exState != 0 && exT1 ? (exT1Half ? " | TP1 booked, rest to TP2" : " | TP1 rule, stop " + DoubleToString(exT1Stop, _Digits)) : "");
''', '''                 + (exState != 0 && exT1 ? (exT1Half ? " | TP1 booked, rest to TP2" : " | TP1 rule, stop " + DoubleToString(exT1Stop, _Digits)) : "")
                 + (!CrkPrOn() ? "" : CrkPause() ? " | paused, " + IntegerToString(crkSkipLeft) + " days left" : crkWait ? " | waiting for " + IntegerToString(InpCrkPrM) + " wins in a row (" + IntegerToString(crkWW) + ")" :
                    crkNeedL ? " | waiting for a loss, then a win" : crkF > 0 ? " | lost recoveries in a row " + IntegerToString(crkF) + "/" + IntegerToString(InpCrkPrN) : "");
''')

# reset (the day tracker only: the money state is kept like the other recovery state) and input checks
rep('''   gVirt = false; gDayPend = false; gPrevT = 0; capStop = false; gT1Seen = false;''',
    '''   gVirt = false; gDayPend = false; gPrevT = 0; capStop = false; gT1Seen = false; crkUDay = -1;''')
rep('''   if(InpCrkT1 && (InpCrkT1Pct < 10 || InpCrkT1Pct > 90)) { Print("Crooks TP1 rule: % closed at TP1 must be 10 to 90."); return INIT_PARAMETERS_INCORRECT; }''',
    '''   if(InpCrkT1 && (InpCrkT1Pct < 10 || InpCrkT1Pct > 90)) { Print("Crooks TP1 rule: % closed at TP1 must be 10 to 90."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr != CPR_OFF && (InpCrkPrN < 1 || InpCrkPrM < 1 || InpCrkPrD < 1)) { Print("Crooks C rule: N, M and D must be 1 or more."); return INIT_PARAMETERS_INCORRECT; }
   if(InpRec == REC_CRC && InpCrkPr == CPR_PCT && (InpCrkPrPct < 10 || InpCrkPrPct > 100)) { Print("Crooks C rule: % of the loss must be 10 to 100."); return INIT_PARAMETERS_INCORRECT; }''')
open(F, 'w').write(s)
print('patched', len(s))
