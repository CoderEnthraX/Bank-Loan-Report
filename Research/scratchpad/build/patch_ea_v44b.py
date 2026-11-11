"""EA v4.4b: the timeframe the EA trades is the one it was attached to. When the chart is switched to another timeframe (to look at the candles),
MT5 restarts the EA on that timeframe: it then opens no new trades (the open trade keeps its own stop loss and take profit and the force-close /
news rules) until the chart is back. Removing the EA (or closing the chart) forgets it: attach it again to trade another timeframe. Strategy
Tester: no hold. Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n = 0


def rep(old, new):
    global s, n
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n += 1


rep('''string   gLockN = ""; double gLockV = 0;                  // one copy per symbol + magic number (temporary global variable)
''', '''string   gLockN = ""; double gLockV = 0;                  // one copy per symbol + magic number (temporary global variable)
int      gTfTrade = 0;                                    // the timeframe the EA trades: the one it was attached to (0 = not known yet)
''')
# helpers: the hold, and its text
rep('''string SvExtra(string k) { return "ARX" + StringSubstr(gSvBase, 3) + k; }
''', '''string SvExtra(string k) { return "ARX" + StringSubstr(gSvBase, 3) + k; }
//--- the chart shows another timeframe than the one the EA was attached to: no new trades until it is back (live only)
bool   TfHold() { return gTfTrade > 0 && (int)_Period != gTfTrade && MQLInfoInteger(MQL_TESTER) == 0; }
string TfName(int p) { return p == PERIOD_M1 ? "M1" : p == PERIOD_M5 ? "M5" : p == PERIOD_M15 ? "M15" : p == PERIOD_M30 ? "M30" : p == PERIOD_H1 ? "H1" : p == PERIOD_H4 ? "H4" : p == PERIOD_D1 ? "D1" : IntegerToString(p) + " min"; }
''')
# TakeSetup: no new trade while the chart shows another timeframe
rep('''   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock || crkPs || monStop);   // the hard cap acts only on a signal that can be taken''',
    '''   bool tfHold = TfHold();                           // v4.4: the chart shows another timeframe than the one the EA trades
   bool canTake = !(exState != 0 || posNow || newsBlk || flatNow || capStop || paused || dayBlock || crkPs || monStop || tfHold);   // the hard cap acts only on a signal that can be taken''')
rep('''   skipWhy = (exState != 0 || posNow) ? "still in a trade" : (newsBlk || flatNow) ? "news / force-close" :''',
    '''   skipWhy = (exState != 0 || posNow) ? "still in a trade" : tfHold ? "chart on " + TfName((int)_Period) + ", the EA trades " + TfName(gTfTrade) : (newsBlk || flatNow) ? "news / force-close" :''')
# OnInit: the timeframe it trades (kept by MT5 on a timeframe change; read back after a restart; forgotten when the EA is removed)
rep('''   TzPick(true);                                         // the broker's clock (Auto), before the warm-up uses it
''', '''   TzPick(true);                                         // the broker's clock (Auto), before the warm-up uses it
   if(MQLInfoInteger(MQL_TESTER) == 0)                   // the timeframe the EA trades: the one it was attached to (also after a restart)
   {
      string tfN = SvExtra("tf");
      if(gTfTrade == 0) gTfTrade = GlobalVariableCheck(tfN) ? (int)MathRound(GlobalVariableGet(tfN)) : (int)_Period;
      GlobalVariableSet(tfN, gTfTrade);
      if(TfHold())
      {
         string m = "The chart is on " + TfName((int)_Period) + ", but this EA trades " + TfName(gTfTrade) + " (the timeframe it was attached to): no new trades until the chart is back on " +
                    TfName(gTfTrade) + ". The open trade keeps its stop loss and take profit. To trade " + TfName((int)_Period) + ", remove the EA and attach it again.";
         Print(m); Alert(m);
      }
   }
''')
rep('''   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   LockFree();''', '''   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   LockFree();
   if((reason == REASON_REMOVE || reason == REASON_CHARTCLOSE) && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableDel(SvExtra("tf"));   // removed: attach it again on any timeframe''')
# the state line
rep('''   string ex = exState == 2 ? (exHg ? " (hedge pair open)" :''',
    '''   if(TfHold()) s = "CHART ON " + TfName((int)_Period) + ": NO NEW TRADES (EA TRADES " + TfName(gTfTrade) + ")";
   string ex = exState == 2 ? (exHg ? " (hedge pair open)" :''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
