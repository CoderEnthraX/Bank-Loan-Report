"""EA v4.4g: fixes from review 2 (Opus, high), each verified against the code first.
R1 (high) The engine events collected in the warm-up for the saved trade (gMiss*) were kept until the first bar close: if that trade had
   already closed at the broker, a NEW trade placed on the first tick (gRearm) was closed there as if the engine's stop had hit it. They are
   now handled in BrokerStart and cleared at its end; a new setup and a booking clear them (and gT1Seen, the same pattern from v4.3).
R2 Netting: an exit by hand / phone / another EA is booked while the EA holds a trade (one position per symbol; v4.4e skipped it).
R3 gRearm: a missing bar time no longer blocks re-placing a waiting order (gTakenT == 0 lets it through).
R4 Every setup the EA decided on (taken, skipped, past the target, rejected) is remembered, so a restart never takes a setup the live run
   did not take.
R5 The last position this EA closed is saved ("xw"): a close right before a restart is reported as this EA's.
R6 A trade whose position is gone is booked with its closing deal: if no closing deal of it is in the history yet, the booking waits one bar
   (gExitSeen / gGoneWait); BookBrokerDeals books only with a closing deal (else the next bar does).
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
rep('''bool     gExitRetry = false; string gExitWhy = "";        // a close that failed: tried again at every bar close, and why it was due
''', '''bool     gExitRetry = false; string gExitWhy = "";        // a close that failed: tried again at every bar close, and why it was due
bool     gExitSeen = false, gGoneWait = false;            // a closing deal of the EA's trade was seen; its position is gone but no closing deal yet
''')
# ---- R2 netting
rep('''   return gHedgeOk && IsExitDeal(tk) && OurPosId(HistoryDealGetInteger(tk, DEAL_POSITION_ID), n);   // netting: one position per symbol is shared''',
    '''   return (gHedgeOk || exState != 0) && IsExitDeal(tk) && OurPosId(HistoryDealGetInteger(tk, DEAL_POSITION_ID), n);   // netting (one position per symbol): while the EA holds a trade''')
# ---- R6 an exit deal of the EA's trade was seen
rep('''      if(IsExitDeal(tk)) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); if(!quiet) CloseReport(tk, n); }''',
    '''      if(IsExitDeal(tk)) { closed = true; gExitSeen = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); if(!quiet) CloseReport(tk, n); }''')
# ---- R5 the last closed position: saved, and known to the report
rep('''bool ClosedByUs(long pid) { for(int q = 0; q < 8; q++) if(gClosedIds[q] == pid && pid > 0) return true; return false; }''',
    '''bool ClosedByUs(long pid) { if(pid > 0 && pid == gCloseId) return true; for(int q = 0; q < 8; q++) if(gClosedIds[q] == pid && pid > 0) return true; return false; }''')
rep('''             ClosedByUs(pid) && gCloseWhy != "" ? "this EA: " + gCloseWhy : "an EA with this magic number (a second copy of this EA?)";''',
    '''             ClosedByUs(pid) ? (gCloseWhy != "" ? "this EA: " + gCloseWhy : "this EA (before a restart)") : "an EA with this magic number (a second copy of this EA?)";''')
rep('''IoT("xt", gTakenT); IoB("xq", gExitRetry);''', '''IoT("xt", gTakenT); IoB("xq", gExitRetry);
   ulong cw = (ulong)gCloseId; IoU("xw", cw); gCloseId = (long)cw;   // the last position this EA closed (its report after a restart)''')
# ---- R4 every setup the EA decided on is remembered; R1 a new setup starts without carried events
rep('''void TakeSetup(bool isL, bool newsBlk, bool flatNow)
{
   sigN++;''', '''void TakeSetup(bool isL, bool newsBlk, bool flatNow)
{
   sigN++;
   gTakenT = BarTimeOf(armBar);                       // decided on now (taken, skipped or rejected): a restart does not take it again''')
rep('''   if(ok) { exState = 1; exArm = armBar; exArmT = BarTimeOf(armBar); gTakenT = exArmT; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }''',
    '''   if(ok)
   {
      exState = 1; exArm = armBar; exArmT = gTakenT; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg;
      gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false; gT1Seen = false; gExitSeen = false; gGoneWait = false;   // no events of an earlier trade
   }''')
# ---- R1 / R6 a booking clears the trade's flags
rep('''   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false;
   CancelPending();
}''', '''   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false;
   gT1Seen = false; gExitSeen = false; gGoneWait = false; gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
   CancelPending();
}''')
rep('''   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false;
''', '''   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0; gExitRetry = false; gExitSeen = false; gGoneWait = false;
''')
rep('''   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = "";''',
    '''   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0); gExitRetry = false; gExitWhy = ""; gExitSeen = false; gGoneWait = false;''')
# ---- R6 OnNewBar: a gone position is booked with its closing deal
rep('''   bool exClosed = (exState == 1 && !pos && closedNew) || (exState == 2 && !pos);

   // 2. an executed trade has closed''', '''   bool gone = exState == 2 && !pos;
   if(gone && !closedNew && !gExitSeen && !gGoneWait) { gGoneWait = true; gone = false; }   // no closing deal in the history yet: booked at the next bar, with it
   bool exClosed = (exState == 1 && !pos && closedNew) || gone;

   // 2. an executed trade has closed''')
rep('''   if((exState == 1 && !pos && closedNew) || (exState == 2 && !pos)) BookClosed();
}''', '''   if((exState == 1 && !pos && closedNew) || (exState == 2 && !pos && gExitSeen)) BookClosed();   // without a closing deal yet: the next bar books it
}''')
# ---- R1 BrokerStart: the warm-up's events are handled here and cleared; R3 gTakenT == 0
rep('''   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm && BarTimeOf(armBar) != gTakenT;   // re-place the engine's armed setup on the first tick (not one armed while paused, not one already traded)''',
    '''   gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;   // the warm-up's events for the saved trade are handled above
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm && (gTakenT == 0 || BarTimeOf(armBar) != gTakenT);   // re-place the engine's armed setup on the first tick (not one armed while paused, not one already decided on)''')
open(P, 'w', encoding='utf8').write(s)
print(n, 'edits; lines', s.count('\n'))
