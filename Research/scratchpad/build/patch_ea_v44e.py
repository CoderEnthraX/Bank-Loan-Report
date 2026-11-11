"""EA v4.4e: fixes from the independent review (Opus, high), each verified against the code first.
F1  BarTimeOf: the last processed bar is found by its time (iBarShift of gLastDone), not assumed at shift 1: a start before MT5 connected
    runs BrokerStart on the first tick, before the bars that arrived meanwhile are processed.
F2  Restart: the saved trade's setup is re-linked in the warm-up when the engine arms it again (arm bar time, direction, entry); the bars
    since the saved state run through EngStep, so the engine's fill, stop moves and exit while the EA was off reach the trade like after a
    disconnect (gMiss*). An exit (stop, or final target without earn-back) is closed at the start; BrokerStart adopts only the re-linked
    setup when the engine still holds it. The TP1-rule catch-up loop uses the real shift of the last processed bar.
F3  MT5 deletes global variables not used for 4 weeks: the EA's own ones ("Start fresh once" done, the timeframe) are rewritten daily.
F4  A close that fails (engine exit, force-close / weekend / news, restart closes) is tried again at every bar close (gExitRetry, saved).
F5  The EA's own partial closes (partials, Crooks TP1 part) carry their reason (no "another copy" / outside report); a close that leaves the
    trade open is reported as "partly closed".
F6  Skipping old history (a fresh start) only moves the deal cursor (no per-deal position search).
F7  An adopted trade without saved levels gets the engine's TP1-TP3 (partials).
F8  The saved timeframe is forgotten whenever the EA leaves the chart (removed, chart closed, failed start, template, program).
N   Netting accounts share one position per symbol: deals count by magic number only there (as v4.3).
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


# ---- globals
rep('''datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
''', '''datetime gTakenT = 0;                                     // arm bar time of the last setup the EA placed: never placed again (restart, new inputs)
bool     gExitRetry = false; string gExitWhy = "";        // a close that failed: tried again at every bar close, and why it was due
''')
# ---- F1 BarTimeOf
rep('''datetime BarTimeOf(long idx)
{
   if(idx < 0) return 0;
   int s = (int)(bi - idx) + 1;
   return s >= 1 && s < Bars(_Symbol, _Period) ? iTime(_Symbol, _Period, s) : 0;
}''', '''datetime BarTimeOf(long idx)
{
   if(idx < 0 || idx > bi || gLastDone <= 0) return 0;
   int s0 = iBarShift(_Symbol, _Period, gLastDone, true);   // the last processed bar: shift 1 after a bar close, more when bars arrived since
   if(s0 < 0) return 0;
   int s = s0 + (int)(bi - idx);
   return s < Bars(_Symbol, _Period) ? iTime(_Symbol, _Period, s) : 0;
}''')
# ---- N + F6 deals
rep('''   if(HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic) return true;
   return IsExitDeal(tk) && OurPosId(HistoryDealGetInteger(tk, DEAL_POSITION_ID), n);''',
    '''   if(HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic) return true;
   return gHedgeOk && IsExitDeal(tk) && OurPosId(HistoryDealGetInteger(tk, DEAL_POSITION_ID), n);   // netting: one position per symbol is shared''')
rep('''   int n = HistoryDealsTotal();
   ulong maxTk = lastDeal;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(tk > maxTk) maxTk = tk;
      if(!DealIsMine(tk, n)) continue;                  // v4.4: also the exit of this EA's trade by hand, from the phone app or by another EA''',
    '''   int n = HistoryDealsTotal();
   ulong maxTk = lastDeal;
   if(quiet) { for(int i = 0; i < n; i++) { ulong tq = HistoryDealGetTicket(i); if(tq > maxTk) maxTk = tq; } lastDeal = maxTk; return 0; }   // old history: only the cursor moves
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(tk > maxTk) maxTk = tk;
      if(!DealIsMine(tk, n)) continue;                  // v4.4: also the exit of this EA's trade by hand, from the phone app or by another EA''')
# ---- F5 report: partly closed
rep('''   Print("Trade #", pid, " closed: ", DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at ", DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),''',
    '''   bool still = false;                                  // part of the trade is still open (a partial close)
   for(int q = PositionsTotal() - 1; q >= 0 && !still; q--) { ulong pt = PositionGetTicket(q); if(pt != 0 && PositionGetInteger(POSITION_IDENTIFIER) == pid) still = true; }
   Print("Trade #", pid, still ? " partly closed: " : " closed: ", DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at ", DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),''')
rep('''      if(trade.PositionClosePartial(tk, NormalizeDouble(cv, 8))) { exT1Half = true; SetExits(true); }''',
    '''      gCloseWhy = "Crooks TP1 rule: the TP1 part"; if(PositionSelectByTicket(tk)) gCloseId = PositionGetInteger(POSITION_IDENTIFIER);
      if(trade.PositionClosePartial(tk, NormalizeDouble(cv, 8))) { exT1Half = true; SetExits(true); }''')
rep('''         if(cv >= vmin && vol - cv >= vmin - 1e-9) trade.PositionClosePartial(tk, NormalizeDouble(cv, 8));''',
    '''         if(cv >= vmin && vol - cv >= vmin - 1e-9)
         {
            gCloseWhy = "partial close at TP" + IntegerToString(k + 1); if(PositionSelectByTicket(tk)) gCloseId = PositionGetInteger(POSITION_IDENTIFIER);
            trade.PositionClosePartial(tk, NormalizeDouble(cv, 8));
         }''')
# ---- F4 retry: BookClosed / TradeClear / ResetEngine clear it; saved
rep('''   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0;
   CancelPending();
}''', '''   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false;
   CancelPending();
}''')
rep('''   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0;
''', '''   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false;
''')
rep('''   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0);
''', '''   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = "";
''')
rep('''   IoT("xa", exArmT); IoD("xe", xe); IoD("x1", x1); IoD("x2", x2); IoD("x3", x3); IoT("xt", gTakenT);''',
    '''   IoT("xa", exArmT); IoD("xe", xe); IoD("x1", x1); IoD("x2", x2); IoD("x3", x3); IoT("xt", gTakenT); IoB("xq", gExitRetry);''')
# a close that may fail: tried again at the next bar closes
rep('''//--- an executed trade has closed: streaks, pauses and loss recovery
void BookClosed()''', '''//--- close the EA's trade for a rule; if MT5 refuses (off quotes, trading disabled, market closed) it is tried again at every bar close
void CloseRule(string why)
{
   CloseAll(why);
   ulong k; double kv, ko;
   if(HasPosition(k, kv, ko)) { gExitRetry = true; gExitWhy = why; } else gExitRetry = false;
}

//--- an executed trade has closed: streaks, pauses and loss recovery
void BookClosed()''')
rep('''   // 2. an executed trade has closed
   if(exClosed) BookClosed();
''', '''   // 2. an executed trade has closed
   if(exClosed) BookClosed();
   if(gExitRetry)                                       // a close that failed before: again
   {
      if(exState != 2 || !pos) gExitRetry = false;
      else { CloseRule((gExitWhy != "" ? gExitWhy : "a close that failed before a restart") + " (again)"); pos = HasPosition(pTk, pVol, pOpen); }
   }
''')
rep('''      if((!InpEarnBack || !gOurWin) && !(exT1 && (gOurWin || exT1Half)))
         CloseAll(gOurWin ? "the engine's final target was reached (bar close, bid chart)" : "the engine's stop was hit (bar close, bid chart)");''',
    '''      if((!InpEarnBack || !gOurWin) && !(exT1 && (gOurWin || exT1Half)))
         CloseRule(gOurWin ? "the engine's final target was reached (bar close, bid chart)" : "the engine's stop was hit (bar close, bid chart)");''')
rep('''   if(flatNow && pos) CloseAll(fcNow ? "the daily force-close time" : wkndStart ? "the weekend starts (Saturday)" : "a news window starts");''',
    '''   if(flatNow && pos) CloseRule(fcNow ? "the daily force-close time" : wkndStart ? "the weekend starts (Saturday)" : "a news window starts");''')
# ---- F3 daily refresh of the EA's own global variables
rep('''   if(gNewDay) TzPick(false);                           // the broker's clock, once a day''',
    '''   if(gNewDay) { TzPick(false); ExtraRefresh(); }        // the broker's clock and the EA's own global variables, once a day''')
rep('''//--- the chart shows another timeframe than the one the EA was attached to: no new trades until it is back (live only)''',
    '''//--- MT5 deletes global variables not used for 4 weeks: the EA's own ones are rewritten once a day (the copy lock is temporary)
void ExtraRefresh()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;
   if(InpMemFresh) GlobalVariableSet(SvExtra("rsd"), 1);
   if(gTfTrade > 0) GlobalVariableSet(SvExtra("tf"), gTfTrade);
}
//--- the chart shows another timeframe than the one the EA was attached to: no new trades until it is back (live only)''')
# ---- F8 the timeframe is forgotten whenever the EA leaves the chart
rep('''   if((reason == REASON_REMOVE || reason == REASON_CHARTCLOSE) && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableDel(SvExtra("tf"));   // removed: attach it again on any timeframe''',
    '''   bool gone = reason == REASON_REMOVE || reason == REASON_CHARTCLOSE || reason == REASON_INITFAILED || reason == REASON_PROGRAM || reason == REASON_TEMPLATE;
   if(gone && gTfTrade > 0 && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableDel(SvExtra("tf"));   // left the chart: attach it again on any timeframe''')
# ---- F2 warm-up: re-link the saved setup; the bars since the saved state through EngStep
rep('''   for(int s = start; s >= 1; s--)
   {
      ProcessBar(s);
      if(gRestored && gSvLast > 0 && iTime(_Symbol, _Period, s) > gSvLast)   // the bars since the saved state count like bars missed in a disconnect
      {''', '''   for(int s = start; s >= 1; s--)
   {
      bool offBar = gRestored && gSvLast > 0 && iTime(_Symbol, _Period, s) > gSvLast;   // the bars since the saved state count like bars missed in a disconnect
      if(offBar) EngStep(s); else ProcessBar(s);
      // v4.4: the saved trade's setup is re-linked when the engine arms it again (its arm bar, direction and entry): its fill, stop moves and
      // exit on the bars since the saved state then reach the trade (gMiss*), like after a disconnect
      if(gRestored && exArmT > 0 && exState != 0 && !exHg && evArm && iTime(_Symbol, _Period, s) == exArmT && (st > 0) == exL &&
         (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5)) exArm = armBar;
      if(offBar)
      {
         if(gOurFill) gMissFill = true;
         if(gOurMove) gMissMove = true;
         if(gOurExit) { gMissExit = true; gMissWin = gOurWin; }''')
# ---- F2 / F7 BrokerStart adoption
rep('''      datetime aT = MathAbs(st) >= 1 && !trGhost ? BarTimeOf(armBar) : 0;
      // v4.4: the engine's setup is this trade's when it is the saved setup (arm bar time and entry, restart memory); without a saved setup,
      // when it has the trade's direction and was armed before the trade opened
      bool same = aT > 0 && (st > 0) == isL &&
                  (gRestored && exArmT > 0 ? aT == exArmT && (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5)
                                           : (datetime)PositionGetInteger(POSITION_TIME) >= aT + PeriodSeconds(_Period));
      exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol;   // a restored trade keeps its lots (partials)
      if(same && MathAbs(st) == 2)
      {
         exArm = armBar; exArmT = aT; exLim = lim; exSynced = true;''',
    '''      datetime aT = MathAbs(st) >= 1 && !trGhost ? BarTimeOf(armBar) : 0;
      // v4.4: the engine's setup is this trade's when it is the saved setup, re-linked in the warm-up (restart memory) and still the engine's;
      // without a saved setup, when it has the trade's direction and was armed before the trade opened
      bool same = MathAbs(st) >= 1 && !trGhost && (st > 0) == isL &&
                  (gRestored && exArmT > 0 ? exArm >= 0 && armBar == exArm
                                           : aT > 0 && (datetime)PositionGetInteger(POSITION_TIME) >= aT + PeriodSeconds(_Period));
      exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol;   // a restored trade keeps its lots (partials)
      if(same && exTpL[0] <= 0) { exTpL[0] = t1; exTpL[1] = t2; exTpL[2] = t3; }   // the trade's own TP1-TP3 (partials)
      if(same && MathAbs(st) == 2)
      {
         exArm = armBar; if(exArmT <= 0) exArmT = aT; exLim = lim; exSynced = true;''')
rep('''      else if(same)
      {
         exArm = armBar; exArmT = aT; exLim = lim; exSynced = false;''', '''      else if(same)
      {
         exArm = armBar; if(exArmT <= 0) exArmT = aT; exLim = lim; exSynced = false;''')
rep('''      if(exState == 2 && exT1 && !exT1Half && exSynced)
         for(int s = 1; s < Bars(_Symbol, _Period); s++)
         {
            if(iTime(_Symbol, _Period, s) <= gSvLast || bi - (s - 1) <= lastFill) break;''',
    '''      int s0 = iBarShift(_Symbol, _Period, gLastDone, true); if(s0 < 1) s0 = 1;   // the last processed bar (later bars: the catch-up checks them)
      if(exState == 2 && exT1 && !exT1Half && exSynced)
         for(int s = s0; s < Bars(_Symbol, _Period); s++)
         {
            if(iTime(_Symbol, _Period, s) <= gSvLast || bi - (s - s0) <= lastFill) break;''')
rep('''      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseAll("a force-close, weekend start or news start passed while the EA was off"); BookBrokerDeals(); }''',
    '''      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseRule("a force-close, weekend start or news start passed while the EA was off"); BookBrokerDeals(); }
      // v4.4: the engine's stop (or its final target without earn-back) of this trade was reached while the EA was off: closed now, as after a
      // disconnect (earn-back and the Crooks TP1 rule only outlive a win; its TP1 part is booked at the next bar close)
      if(gMissExit && exState == 2 && !exHg && HasPosition(rTk, rVol, rOp) && (!InpEarnBack || !gMissWin) && !(exT1 && (gMissWin || exT1Half)))
      { CloseRule(gMissWin ? "the engine's final target was reached while the EA was off" : "the engine's stop was hit while the EA was off"); BookBrokerDeals(); }''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
