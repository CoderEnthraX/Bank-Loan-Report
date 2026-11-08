"""EA v4.2 review fixes (monthly lock): the month counts a trade when it has fully closed (BookClosed, like TradingView's closed trades; covers
the engine-wins close path too); the restart and the checks run after every booking, right before a new setup is taken; MonthFromHistory keys the
month on the last closed bar, filters deals by their own month (no DST hour off) and skips open positions; lock % 1-100. Must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
OLD_HIST = s[s.index('void MonthFromHistory()'):s.index('//--- risk $ for the next trade (loss recovery + hard cap)')]
NEW_HIST = r'''void MonthFromHistory()                               // after a restart: this month's closed trades, its high and the locks from the deal history
{
   datetime b1 = iTime(_Symbol, _Period, 1), now = TimeCurrent();
   MqlDateTime d; TimeToStruct(UserTime(b1 > 0 ? b1 : now), d);
   gMonKey = d.year * 100 + d.mon;                    // the month of the last closed bar, as MonthTick will see it
   monPnl = 0; monPeak = 0; monLocked = false; monStop = false;
   long open[]; int no = 0;                           // positions still open: their deals are not closed profit yet
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong pt = PositionGetTicket(i);
      if(pt == 0 || PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic) continue;
      ArrayResize(open, no + 1); open[no++] = PositionGetInteger(POSITION_IDENTIFIER);
   }
   if(!HistorySelect(now - 40 * 86400, now + 86400)) return;
   int n = HistoryDealsTotal();
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      MqlDateTime dd; TimeToStruct(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), dd);
      if(dd.year * 100 + dd.mon != gMonKey) continue;  // only this month's deals (your time zone)
      long pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID); bool isOpen = false;
      for(int q = 0; q < no; q++) if(open[q] == pid) { isOpen = true; break; }
      if(isOpen) continue;
      monPnl += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      long e = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY) MonthCheck();
   }
}

'''
REPS = [
    (OLD_HIST, NEW_HIST),
    # the month counts a trade when it has fully closed (all its deals, entry commission included), like TradingView's closed trades
    ('void BookClosed()\n{\n   bool win = exPnl > 0;\n',
     'void BookClosed()\n{\n   bool win = exPnl > 0;\n   monPnl += exPnl;                                     // monthly locks: the whole trade counts in the month it closes\n'),
    ('   exPnl += newPnl; totalNet += newPnl; monPnl += newPnl;\n', '   exPnl += newPnl; totalNet += newPnl;\n'),
    ('   if(monRestPend && exState == 0 && !pos) { monRestPend = false; RecoveryRestart(); }   // monthly restart, once no trade of the old month is left\n   MonthCheck();\n', ''),
    ('   // 5. take the engine\'s new setup\n   if(evArm) TakeSetup(evArmL, newsBlk, flatNow);',
     '   // monthly restart (once no trade of the old month is left) and the monthly locks, after every booking of this bar\n'
     '   if(monRestPend && exState == 0 && !HasPosition(pTk, pVol, pOpen)) { monRestPend = false; RecoveryRestart(); }\n'
     '   MonthCheck();\n\n'
     '   // 5. take the engine\'s new setup\n   if(evArm) TakeSetup(evArmL, newsBlk, flatNow);'),
    ('InpPLockPct <= 0 || InpPLockPct > 100', 'InpPLockPct < 1 || InpPLockPct > 100'),
]
for old, new in REPS:
    n = s.count(old)
    assert n == 1, (n, old[:100])
    s = s.replace(old, new)
open(P, 'w', encoding='utf8').write(s)
print(len(REPS), 'replacements; lines', s.count('\n'))
