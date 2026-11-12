"""EA v4.4j: the VWAP line on the chart (asked 2026-11-12: "I don't see any VWAP line ... by default enable it, with an option to turn it
off"). The line is the engine's own VWAP (same anchor, source and volume as the signals), drawn like the TradingView indicator's plot
(#4DD0E1, width 2, on by default): one trend-line segment per processed bar for the last InpVwapBars bars (older segments are removed as new
bars come), drawn on the chart and in visual tests only, removed with the EA (prefix ARM_). ProcessBar is untouched: DrawBar, which it calls
at the end of every bar, draws the segment from vwHist[0] (this bar's VWAP). Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''//| magic number. The broker server clock is read from MT5 (Auto).   |
''', '''//| magic number. The broker server clock is read from MT5 (Auto).   |
//| The VWAP line the EA trades on is drawn on the chart (on by      |
//| default; DISPLAY inputs).                                        |
''')
rep('''input color  InpColEntry  = clrDodgerBlue;     //   entry line and armed limit
''', '''input color  InpColEntry  = clrDodgerBlue;     //   entry line and armed limit
input bool   InpVwapShow  = true;              // Show the VWAP line (the one the EA trades on)
input color  InpVwapColor = C'77,208,225';     //   VWAP color
input int    InpVwapWidth = 2;                 //   VWAP line width (1-5)
input int    InpVwapBars  = 1500;              //   bars of VWAP drawn (50-20000; older parts are removed)
''')
rep('''datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
''', '''datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
datetime gVwPrevT = 0, gVwCut = 0; double gVwPrev = 0; int gVwN = 1500;   // VWAP line: the previous bar and its VWAP, the oldest bar drawn, bars kept
''')
rep('''// one engine bar: armed limit, then a filled trade's boxes, entry / TP lines, fill arrow and price labels, then its result
void DrawBar(datetime bt)
{
   if(!InpDraw || !gCanDraw) return;''', '''//--- the VWAP line: the engine's VWAP of this bar (vwHist[0], same anchor, source and volume as the signals), one segment from the previous
//--- bar, for the last gVwN bars (live: the segment that falls out of the window is removed); like the TradingView indicator's VWAP plot
void VwDraw(datetime bt)
{
   double v = ArraySize(vwHist) > 0 ? vwHist[0] : 0;
   if(InpVwapShow && gCanDraw && gVwPrevT > 0 && v > 0 && gVwPrev > 0 && bt >= gVwCut)
   {
      string nm = "ARM_VW" + IntegerToString((long)bt);
      if(ObjectFind(0, nm) < 0) ObjectCreate(0, nm, OBJ_TREND, 0, gVwPrevT, gVwPrev, bt, v);
      else { ObjectMove(0, nm, 0, gVwPrevT, gVwPrev); ObjectMove(0, nm, 1, bt, v); }
      ObjectSetInteger(0, nm, OBJPROP_COLOR, InpVwapColor);
      ObjectSetInteger(0, nm, OBJPROP_WIDTH, (int)MathMax(1, MathMin(5, InpVwapWidth)));
      ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, nm, OBJPROP_BACK, true);
      ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false);
      ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true);
      ObjectSetString(0, nm, OBJPROP_TOOLTIP, "VWAP " + DoubleToString(v, _Digits));
      if(gLive)
      {
         datetime old = iTime(_Symbol, _Period, gVwN + 1);
         if(old > 0) ObjectDelete(0, "ARM_VW" + IntegerToString((long)old));
      }
   }
   gVwPrevT = bt; gVwPrev = v;
}

// one engine bar: armed limit, then a filled trade's boxes, entry / TP lines, fill arrow and price labels, then its result
void DrawBar(datetime bt)
{
   VwDraw(bt);                                          // v4.4: the VWAP line (its own switch, also with the markings off)
   if(!InpDraw || !gCanDraw) return;''')
rep('''   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = ""; gExitSeen = false; gGoneWait = false;''',
    '''   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = ""; gExitSeen = false; gGoneWait = false;
   gVwPrevT = 0; gVwPrev = 0;''')
rep('''   gLive = false;
   for(int s = start; s >= 1; s--)''', '''   gVwN = (int)MathMax(50, MathMin(20000, InpVwapBars));   // the VWAP line: the last gVwN bars
   gVwCut = iTime(_Symbol, _Period, (int)MathMin(gVwN, bars - 1));
   gLive = false;
   for(int s = start; s >= 1; s--)''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
