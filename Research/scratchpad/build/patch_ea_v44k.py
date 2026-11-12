"""EA v4.4k (the VWAP line, checked on the broker simulator):
1  The window cleanup removes every segment that left the window (by bar time, from the last cutoff), not one per bar: bars caught up after
   a disconnect (several bars in one tick) left extra segments and could delete one inside the window.
2  The line is drawn over the candles, like the TradingView plot (the trade markings stay behind them).
3  The chart is redrawn at the end of the start, so the line shows at once (also with the market closed and the table off).
Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''      if(gLive)
      {
         datetime old = iTime(_Symbol, _Period, gVwN + 1);
         if(old > 0) ObjectDelete(0, "ARM_VW" + IntegerToString((long)old));
      }''', '''      if(gLive)                                         // the bars that left the window since the last cutoff (several after a disconnect)
      {
         for(int q = gVwN + 1; q < Bars(_Symbol, _Period); q++)
         {
            datetime ot = iTime(_Symbol, _Period, q);
            if(ot <= 0 || ot < gVwCut) break;
            ObjectDelete(0, "ARM_VW" + IntegerToString((long)ot));
         }
         datetime cut = iTime(_Symbol, _Period, gVwN);
         if(cut > gVwCut) gVwCut = cut;
      }''')
rep('''      ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, nm, OBJPROP_BACK, true);''', '''      ObjectSetInteger(0, nm, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(0, nm, OBJPROP_RAY_RIGHT, false);
      ObjectSetInteger(0, nm, OBJPROP_BACK, false);           // over the candles, like the TradingView plot''')
rep('''   gStateTxt = StateText(false);
   UpdateTable();
   StateSave(true);                                      // restart memory: the state after this start''', '''   gStateTxt = StateText(false);
   UpdateTable();
   if(gCanDraw) ChartRedraw(0);                          // the VWAP line and markings show at once (also with the market closed)
   StateSave(true);                                      // restart memory: the state after this start''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
