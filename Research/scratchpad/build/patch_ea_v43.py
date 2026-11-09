"""EA v4.3: RESTART MEMORY. The loss recovery (every rule's state), streaks and pauses, the Crooks C rule state, the hard-cap stop, total
profit, the month-change flag and the open trade's bookkeeping are written to MT5 global variables whenever they change (and flushed to
disk), and read back when the EA starts fresh (MT5 or the EA restarted, a crash). The bars and broker deals since the saved state are then
caught up like after a disconnect (same code path). Also: several missed days now count as several days for the streak pause (was one),
and the Labouchere list is kept with the other recovery states when inputs change. Off in the Strategy Tester. Every replacement must
match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()

# header lines, same width as the existing box
anchor_hdr = next(l for l in s.split('\n') if l.startswith("//| profit once it is up $Y; restart the loss recovery on the 1st."))
W = len(anchor_hdr)
def hl(t):
    line = '//| ' + t
    assert len(line) <= W - 2, t
    return line.ljust(W - 1) + '|'
hdr_new = anchor_hdr + '\n' + '\n'.join(hl(t) for t in (
    'v4.3: RESTART MEMORY: the loss recovery, streaks, pauses and the',
    'open trade go on after MT5 or the EA restarts (MT5 global',
    'variables; trades that closed meanwhile are booked).'))

INPUT = '''input bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (after a trade still open closes)

input group "RESTART MEMORY"
input bool   InpRemember = true;   // Continue after a restart (keep the loss recovery, streaks and pauses when MT5 or the EA restarts)
'''

GLOBALS = '''int      gCrkPrPrev = -1;                                 // the Crooks C rule the state belongs to (a new choice starts its state again)
bool     gInitDone = false;                               // restart memory: OnInit finished once (MT5 keeps globals when inputs or the timeframe change: nothing is reloaded then)
bool     gPersist = false; string gSvBase = "";           //   on (live / demo, not in the Strategy Tester); the names' prefix of this EA (symbol, magic, account)
bool     gRestored = false; datetime gSvT = 0, gSvLast = 0;   //   state reloaded at this start; when it was saved; the last processed bar it belongs to
string   gIoN[]; double gIoV[]; int gIoC = 0; bool gIoSave = true;   //   the values being written / read
string   gSvN[]; double gSvV[]; int gSvC = 0;              //   the values last written (only changes are written)
'''

DAYSTART = '''//--- every new day since the last booking (more than one after a disconnect or a restart): the day's P&L and streak stop start again, each
//    new day ends one pause day
void DayStart(int nd)
{
   if(nd <= 0) return;
   dayPnl = 0; dayBlock = false;
   for(int q = 0; q < nd; q++) { paused = pauseLeft > 0; if(pauseLeft > 0) pauseLeft--; }
}

//=== EXECUTION: runs once per new bar, after the engine processed the bar that just closed ==='''

MEMORY = r'''//=== RESTART MEMORY (v4.3) =================================================================================================
// The loss recovery (every rule's state), streaks and pauses, the Crooks C rule state, the hard-cap stop, total profit, the month-change flag
// and the open trade's bookkeeping live in the EA's memory. MT5 keeps that memory when inputs or the timeframe change, but not when MT5 or
// the EA restarts. They are written to MT5 global variables (Tools -> Global Variables, F3; names ARS|symbol|magic|account|...) whenever they
// change, flushed to disk, and read back when the EA starts fresh; the bars and broker deals since then are caught up like after a disconnect.
int    SvVer() { return 1; }                            // layout version of the saved values
string SvBaseName()                                     // ARS|symbol|magic|account| (a short hash when that is too long: names have at most 63 characters)
{
   string acc = IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
   string b = "ARS|" + _Symbol + "|" + IntegerToString(InpMagic) + "|" + acc + "|";
   if(StringLen(b) <= 57) return b;
   string k = _Symbol + "|" + IntegerToString(InpMagic) + "|" + acc;
   uint h = (uint)2166136261;                           // FNV-1a
   for(int q = 0; q < StringLen(k); q++) { h ^= (uint)StringGetCharacter(k, q); h *= (uint)16777619; }
   return "ARS|" + StringFormat("%08X", h) + "|";
}
//--- one value: collected (save) or read back when it was saved (load)
void IoD(string n, double &x)
{
   if(gIoSave)
   {
      if(gIoC >= ArraySize(gIoN)) { ArrayResize(gIoN, gIoC + 32); ArrayResize(gIoV, gIoC + 32); }
      gIoN[gIoC] = n; gIoV[gIoC] = x; gIoC++;
   }
   else if(GlobalVariableCheck(gSvBase + n)) x = GlobalVariableGet(gSvBase + n);
}
void IoI(string n, int &x)      { double d = x; IoD(n, d); x = (int)MathRound(d); }
void IoB(string n, bool &x)     { double d = x ? 1.0 : 0.0; IoD(n, d); x = d != 0.0; }
void IoT(string n, datetime &x) { double d = (double)x; IoD(n, d); x = (datetime)(long)MathRound(d); }
void IoU(string n, ulong &x)    { double hi = (double)(x >> 32), lo = (double)(x & 0xFFFFFFFF); IoD(n + "h", hi); IoD(n + "l", lo); x = ((ulong)MathRound(hi) << 32) | (ulong)MathRound(lo); }
//--- the saved state: one list for writing and reading, so both always match
void StateIO(bool save)
{
   gIoSave = save; gIoC = 0;
   int ver = SvVer(); IoI("ver", ver);
   datetime lb = gLastDone, sv = TimeCurrent();           // the last processed bar, and when it was saved (both not a reason to write)
   IoT("lb", lb); IoT("sv", sv);
   if(!save) { gSvLast = lb; gSvT = sv; }
   // loss recovery (every rule's state, whichever rule is chosen), total profit (Step-up rule), the hard-cap stop
   IoD("rp", recPool); IoI("rl", recLosses); IoI("du", dUnits); IoD("ca", carried); IoI("pw", parWins); IoI("rd", rdUnits);
   IoI("ou", oscU); IoD("op", oscP); IoD("tn", totalNet); IoI("ew", exW); IoI("el", exLn); IoB("cs", capStop);
   IoD("kl", crkL); IoI("kn", crkN); IoB("kw", crkW); IoI("kp", crkP); IoI("kf", crkF); IoB("ka", crkWait); IoI("kb", crkWW);
   IoB("kc", crkNeedL); IoB("ks", crkSkip); IoI("kt", crkSkipLeft); IoI("ku", crkUDay); IoB("kh", crkHg); IoI("kx", gCrkPrPrev);
   // streaks and pauses; the month of the last bar (a new month while the EA was off) and a restart still waiting for a trade to close
   IoD("dp", dayPnl); IoI("lr", lossRow); IoI("wr", winRow); IoB("db", dayBlock); IoI("pl", pauseLeft); IoB("pa", paused);
   IoI("mk", gMonKey); IoB("mr", monRestPend);
   // the trade the EA is in, or its working order: its type and what it booked so far; the broker deals already counted
   IoI("xs", exState); IoB("xl", exL); IoD("xv", exLots); IoD("xr", exRiskAmt); IoD("xc", exCostPx); IoD("xp", exPnl); IoD("xk", exKeepSl);
   IoB("kr", crkRec);
   bool p0 = pDone[0], p1 = pDone[1], p2 = pDone[2];
   IoB("p0", p0); IoB("p1", p1); IoB("p2", p2);
   pDone[0] = p0; pDone[1] = p1; pDone[2] = p2;
   IoB("t1", exT1); IoB("th", exT1Half); IoB("tb", exT1Be); IoB("tm", exT1MvPend); IoD("ts", exT1Stop); IoD("tp", exT1Tp1); IoD("tq", exT1Tp2);
   IoD("tt", exT1Tight); IoD("te", exT1Entry); IoB("hg", exHg); IoD("hs", exHgS); IoD("ht", exHgT);
   IoU("ld", lastDeal);
   // the Labouchere list, last (its length changes)
   int ln = ArraySize(labSeq); IoI("ln", ln);
   if(!save) { if(ln < 1 || ln > 10000) ln = 0; ArrayResize(labSeq, ln); }
   for(int q = 0; q < ln; q++) { double x = save ? labSeq[q] : 0.0; IoD("L" + IntegerToString(q), x); if(!save) labSeq[q] = x; }
   if(!save)
   {
      bool ok = ArraySize(labSeq) > 0;
      for(int q = 0; q < ArraySize(labSeq); q++) if(labSeq[q] <= 0) ok = false;
      if(!ok) LabReset();
      if(exState < 0 || exState > 2) exState = 0;
   }
}
//--- write what changed (force: everything), then flush to disk so it survives a crash or a power cut
void StateSave(bool force)
{
   if(!gPersist) return;
   StateIO(true);
   bool ch = force || gIoC != gSvC;
   for(int q = 0; q < gIoC && !ch; q++)
      if(gIoN[q] != gSvN[q] || (gIoV[q] != gSvV[q] && gIoN[q] != "lb" && gIoN[q] != "sv")) ch = true;
   if(!ch) return;
   for(int q = 0; q < gIoC; q++)
      if(force || q >= gSvC || gIoN[q] != gSvN[q] || gIoV[q] != gSvV[q]) GlobalVariableSet(gSvBase + gIoN[q], gIoV[q]);
   for(int q = gIoC; q < gSvC; q++) GlobalVariableDel(gSvBase + gSvN[q]);   // a shorter Labouchere list
   if(ArraySize(gSvN) < gIoC) { ArrayResize(gSvN, gIoC); ArrayResize(gSvV, gIoC); }
   for(int q = 0; q < gIoC; q++) { gSvN[q] = gIoN[q]; gSvV[q] = gIoV[q]; }
   gSvC = gIoC;
   GlobalVariablesFlush();
}
//--- read the saved state back (false: nothing saved for this symbol, magic number and account)
bool StateLoad()
{
   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer()) return false;
   StateIO(false);
   gSvC = 0;                                            // the next save writes every value again
   return true;
}
//--- restart memory switched off: forget what was saved
void SvWipe() { GlobalVariablesDeleteAll(gSvBase); GlobalVariablesFlush(); gSvC = 0; }
//--- no trade or working order of this EA: its bookkeeping starts again
void TradeClear()
{
   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
   crkRec = false; exT1 = false; exT1Half = false; exT1Be = false; exT1MvPend = false; exT1Stop = 0; exT1Tp1 = 0; exT1Tp2 = 0; exT1Tight = 0; exT1Entry = 0;
   exHg = false; exHgS = 0; exHgT = 0;
   for(int q = 0; q < 3; q++) pDone[q] = false;
}
//--- an exit deal of this EA after the deals already counted (a trade closed while the EA was off)
bool ExitDealAfter(ulong cursor)
{
   if(!HistorySelect(0, TimeCurrent() + 86400)) return false;
   for(int i = HistoryDealsTotal() - 1; i >= 0; i--)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= cursor) continue;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      long e = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY) return true;
   }
   return false;
}
//--- the saved trade after a restart: still open or closed meanwhile (its bookkeeping is kept; booked like after a disconnect), or gone
void RestoreTrade()
{
   int sx = exState;
   ulong tk; double v, op;
   bool posNow = HasPosition(tk, v, op);
   if(sx == 2 || (sx == 1 && (posNow || ExitDealAfter(lastDeal)))) { exState = 2; return; }
   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)
   bool c; NewDealsPnl(c);                              // no trade of this EA was open: later deals are not its trades
}
//--- OnNewBar's steps 1-2 at start-up: the deals since the saved state, and a trade that closed while the EA was off
void BookBrokerDeals()
{
   bool closedNew; double newPnl = NewDealsPnl(closedNew);
   exPnl += newPnl; totalNet += newPnl;
   if(newPnl != 0 || closedNew) carried = MathMax(0.0, carried - newPnl);
   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   if((exState == 1 && !pos && closedNew) || (exState == 2 && !pos)) BookClosed();
}

//--- reset every engine / execution variable (MT5 keeps globals when inputs or the timeframe change) ---'''

INIT_A_OLD = '''   ResetEngine();
   LabReset();
'''
INIT_A_NEW = '''   ResetEngine();
   if(ArraySize(labSeq) == 0) LabReset();               // the Labouchere list is kept with the other recovery states when inputs change
   // restart memory: on a fresh start (MT5 or the EA restarted) continue from the saved state; switched off: forget it
   gPersist = InpRemember && MQLInfoInteger(MQL_TESTER) == 0 && MQLInfoInteger(MQL_OPTIMIZATION) == 0;
   gSvBase = SvBaseName(); gRestored = false;
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();
   if(gPersist && !gInitDone) gRestored = StateLoad();
'''
INIT_B_OLD = '''   int start = (int)MathMin(InpWarmBars, bars - look - 1);
   gLive = false;
   for(int s = start; s >= 1; s--) ProcessBar(s);
   gLive = true;
'''
INIT_B_NEW = '''   int start = (int)MathMin(InpWarmBars, bars - look - 1);
   if(gRestored && gSvLast > 0)                         // reach back to the saved bar, so every day since then is counted (at most 100,000 bars)
   {
      int sh = iBarShift(_Symbol, _Period, gSvLast, false);
      if(sh < 0 || sh > start) start = (int)MathMin(sh < 0 ? 100000 : MathMin(sh, 100000), bars - look - 1);
   }
   gLive = false;
   for(int s = start; s >= 1; s--)
   {
      ProcessBar(s);
      if(gRestored && iTime(_Symbol, _Period, s) > gSvLast)   // the bars since the saved state count like bars missed in a disconnect
      {
         if(gNewDay) gDayPendN++;
         CrkDayTick(iTime(_Symbol, _Period, s));          // Crooks C skip rule: the days that passed
         if(evArm && CrkPause()) gPauseArm = armBar;      // armed while paused: the strategy skips it, so it is not placed now
      }
   }
   gLive = true;
'''
INIT_C_OLD = '''   bool c; NewDealsPnl(c);   // do not count old history
   MonthFromHistory();       // this month's closed profit and the monthly locks (a restart in the middle of a month keeps them)
'''
INIT_C_NEW = '''   if(!gRestored) { bool c; NewDealsPnl(c); }            // do not count old history (restored: the deals since the saved state are booked below)
   int svMon = gMonKey;
   MonthFromHistory();       // this month's closed profit and the monthly locks (a restart in the middle of a month keeps them)
   if(gRestored && InpMRestart && svMon != -1 && svMon != gMonKey) monRestPend = true;   // a new month began while the EA was off
   if(gRestored) RestoreTrade();                         // the saved trade: still open, closed while the EA was off, or gone
'''
INIT_D_OLD = '''   CancelPending();   // a pending order from before the restart has no tracked state
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0;   // re-place the engine's armed setup on the first tick
'''
INIT_D_NEW = '''   CancelPending();   // a pending order from before the restart has no tracked state
   if(gRestored)                                         // the days and the broker's deals since the saved state, booked like after a disconnect
   {
      DayStart(gDayPendN); gDayPendN = 0;
      // Crooks TP1 rule: TP1 was reached while the EA was off and its part is not booked yet: it is booked at the next bar close
      if(exState == 2 && exT1 && !exT1Half && exSynced)
         for(int s = 1; s < bars; s++)
         {
            if(iTime(_Symbol, _Period, s) <= gSvLast || bi - (s - 1) <= lastFill) break;
            if(exL ? Hi(s) >= exT1Tp1 + exCostPx : Lo(s) <= exT1Tp1 - exCostPx) { gT1Seen = true; break; }
         }
      BookBrokerDeals();
      ulong rTk; double rVol, rOp;
      if(monRestPend && exState == 0 && !HasPosition(rTk, rVol, rOp)) { monRestPend = false; RecoveryRestart(); }
      MonthCheck();
      bool isCC = InpRec == REC_C || InpRec == REC_CS, isKK = InpRec == REC_CRA || InpRec == REC_CRB || InpRec == REC_CRC || InpRec == REC_CRD;
      Print("Restart memory: continued from ", DateTxt(UserTime(gSvT), true), " | loss to win back ", DoubleToString(isCC ? carried : isKK ? crkL : recPool, 2),
            " | streak ", winRow, "W / ", lossRow, "L", (paused || pauseLeft > 0) ? " | paused" : "", CrkPause() ? " | Crooks C pause" : "",
            capStop ? " | hard cap stop" : "", exState == 2 ? " | trade still open" : "");
   }
   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm;   // re-place the engine's armed setup on the first tick (not one armed while paused)
'''
INIT_E_OLD = '''   UpdateTable();
   return INIT_SUCCEEDED;
}'''
INIT_E_NEW = '''   UpdateTable();
   StateSave(true);                                      // restart memory: the state after this start
   gInitDone = true;
   return INIT_SUCCEEDED;
}'''

REPS = [
    (anchor_hdr, hdr_new),
    ('#property version   "4.20"', '#property version   "4.30"'),
    ('TblAdd("AUCTION RETEST", "EA v4.2"', 'TblAdd("AUCTION RETEST", "EA v4.3"'),
    ('input bool   InpMRestart = false;  // Restart the loss recovery on the 1st of each month (after a trade still open closes)\n', INPUT),
    ('bool     gDayPend = false;         // the day changed on a caught-up bar\n',
     'int      gDayPendN = 0;            // new days on bars caught up after a disconnect or replayed after a restart, not counted yet\n'),
    ('int      gCrkPrPrev = -1;                                 // the Crooks C rule the state belongs to (a new choice starts its state again)\n', GLOBALS),
    ('''   if(gNewDay || gDayPend)
   {
      gDayPend = false;
      dayPnl = 0; dayBlock = false;
      paused = pauseLeft > 0; if(pauseLeft > 0) pauseLeft--;
   }
''', '''   DayStart(gDayPendN + (gNewDay ? 1 : 0)); gDayPendN = 0;   // each new day since the last bar (several after a disconnect or a restart)
'''),
    ('ProcessBar(s); caught = true; if(gNewDay) gDayPend = true;', 'ProcessBar(s); caught = true; if(gNewDay) gDayPendN++;'),
    ('gVirt = false; gDayPend = false; gPrevT = 0;', 'gVirt = false; gDayPendN = 0; gPrevT = 0;'),
    ('//=== EXECUTION: runs once per new bar, after the engine processed the bar that just closed ===', DAYSTART),
    ('//--- reset every engine / execution variable (MT5 keeps globals when inputs or the timeframe change) ---', MEMORY),
    (INIT_A_OLD, INIT_A_NEW), (INIT_B_OLD, INIT_B_NEW), (INIT_C_OLD, INIT_C_NEW), (INIT_D_OLD, INIT_D_NEW), (INIT_E_OLD, INIT_E_NEW),
    ('void OnDeinit(const int reason)\n{\n   Comment("");\n',
     'void OnDeinit(const int reason)\n{\n   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)\n   Comment("");\n'),
    ('      if(sh == 1) { VirtualEntry(); ManagePartials(); return; }', '      if(sh == 1) { VirtualEntry(); ManagePartials(); StateSave(false); return; }'),
    ('   VirtualEntry();\n   ManagePartials();\n}\n',
     '   VirtualEntry();\n   ManagePartials();\n   StateSave(false);                                    // restart memory: written only when something changed\n}\n'),
]
TABLE_OLD = next(l for l in s.split('\n') if l.lstrip().startswith('TblAdd("DATA RANGE"')) + '\n'
TABLE_NEW = TABLE_OLD + '''   TblAdd("RESTART MEMORY", gPersist ? (gRestored ? "on | continued from " + DateTxt(UserTime(gSvT), true) : "on") : InpRemember ? "off in the Strategy Tester" : "off", white, cell);
'''
REPS.append((TABLE_OLD, TABLE_NEW))
for old, new in REPS:
    n = s.count(old)
    assert n == 1, (n, old[:120])
    s = s.replace(old, new)
assert 'gDayPend ' not in s and 'gDayPend;' not in s and 'gDayPend=' not in s and 'gDayPend)' not in s, 'gDayPend left'
open(P, 'w', encoding='utf8').write(s)
print(len(REPS), 'replacements; lines', s.count('\n'))
