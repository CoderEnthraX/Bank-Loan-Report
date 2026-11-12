"""EA v4.4l (found with the restart memory switched off in the broker simulator, then checked for the default too):
1  On another timeframe than the one the EA trades (TfHold), the open trade is never linked to that timeframe's engine: not in the warm-up
   (restart memory) and not in BrokerStart. It keeps its own stop loss and take profit, as the alert says, and is linked again when the
   chart is back. With the memory off, 12 of 155 trades open at a switch to M1 were taken over by the M1 engine (its stop and target).
2  Restart memory off, new inputs or another timeframe: MT5 keeps the money management in memory, but the start that follows skips every
   earlier deal, so a trade that closed in the seconds before the change was never booked. OnDeinit now books it first.
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


rep('''      if(gRestored && exArmT > 0 && exState != 0 && !exHg && evArm && iTime(_Symbol, _Period, s) == exArmT && (st > 0) == exL &&
         (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5)) exArm = armBar;''', '''      if(gRestored && exArmT > 0 && exState != 0 && !exHg && evArm && iTime(_Symbol, _Period, s) == exArmT && (st > 0) == exL &&
         (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5) && !TfHold()) exArm = armBar;   // not on another timeframe''')
rep('''      // v4.4: the engine's setup is this trade's when it is the saved setup, re-linked in the warm-up (restart memory) and still the engine's;
      // without a saved setup, when it has the trade's direction and was armed before the trade opened
      bool same = MathAbs(st) >= 1 && !trGhost && (st > 0) == isL &&''', '''      // v4.4: the engine's setup is this trade's when it is the saved setup, re-linked in the warm-up (restart memory) and still the engine's;
      // without a saved setup, when it has the trade's direction and was armed before the trade opened. Never on another timeframe than
      // the one the EA trades: the trade keeps its own stop loss and take profit until the chart is back
      bool same = !TfHold() && MathAbs(st) >= 1 && !trGhost && (st > 0) == isL &&''')
rep('''   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   LockFree();''', '''   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   // restart memory off, new inputs or another timeframe: MT5 keeps the money management, but the start that follows skips earlier deals,
   // so a trade that has just closed is booked now
   if(!gPersist && (reason == REASON_PARAMETERS || reason == REASON_CHARTCHANGE) && exState != 0) BookBrokerDeals();
   LockFree();''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\\n'))
