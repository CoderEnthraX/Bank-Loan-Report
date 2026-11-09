"""EA v4.3 review fixes (independent review, verified):
F1  a restored runner (Crooks TP1 rest, earn-back) or an order filled before the engine's fill bar is kept, not closed at the first bar:
    exSynced is saved; an early fill is linked to the engine's armed setup (exArm).
F4  every saved value is rewritten once a day (MT5 deletes global variables not accessed for 4 weeks); a message when a state is incomplete.
F5  the broker part of a start (deals, positions, orders) waits until MT5 is connected, so an open trade is never booked as closed because
    positions were not visible yet; nothing is saved meanwhile. A state of another account found after connecting starts fresh.
L1  a hard-cap Stop ends with new inputs (as before) or when the cap no longer stops.
L2  a restored hedge pair keeps its waiting trade.  L3  new inputs also restore the open trade's bookkeeping (saved at OnDeinit).
L4  a restored trade keeps its lots (partials).  L6  a force-close, weekend start or news start that passed while the EA was off closes a
    restored open trade at the restart, like after a disconnect.  L8  stale Labouchere values are deleted.  Every replacement must match once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()

# ---- the broker part of OnInit becomes BrokerStart() ----
a = s.index('   if(!gRestored) { bool c; NewDealsPnl(c); }            // do not count old history')
z_mark = '   gRearm = MathAbs(st) == 1 && !trGhost && exState == 0 && armBar != gPauseArm;   // re-place the engine\'s armed setup on the first tick (not one armed while paused)\n'
z = s.index(z_mark) + len(z_mark)
body = s[a:z]
assert s.count(body) == 1
DEFER = '''   // the broker part (deals, positions, orders): now when MT5 is connected, else at the first tick once it is (positions are not visible before)
   gBrokerPend = MQLInfoInteger(MQL_TESTER) == 0 && (TerminalInfoInteger(TERMINAL_CONNECTED) == 0 || AccountInfoInteger(ACCOUNT_LOGIN) == 0);
   if(gBrokerPend) Print("Waiting for the connection to the trade server before checking positions and deals.");
   else BrokerStart();
'''
s = s[:a] + DEFER + s[z:]

B = body
def rb(old, new):
    global B
    assert B.count(old) == 1, old[:90]
    B = B.replace(old, new)
rb('''         exState = 2; exL = isL; exLots = vol; exArm = armBar; exSynced = true; for(int q = 0; q < 3; q++) pDone[q] = tpHit >= q + 1; Print("Adopted open position #", tk, " (engine is in the same trade).");''',
   '''         exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol; exArm = armBar; exSynced = true;   // a restored trade keeps its lots (partials)
         for(int q = 0; q < 3; q++) pDone[q] = pDone[q] || tpHit >= q + 1;
         Print("Adopted open position #", tk, " (engine is in the same trade).");''')
rb('''      else { exState = 2; Print("Open position #", tk, " does not match the engine state; it will be closed on the next bar (the engine wins)."); }''',
   '''      else
      {
         exState = 2;
         bool early = gRestored && MathAbs(st) == 1 && (st > 0) == isL;          // restored: the broker filled before the engine's fill bar
         bool runner = gRestored && exSynced && (exT1 || InpEarnBack);           // restored: a Crooks TP1-rule rest or an earn-back trade outliving the engine's exit
         if(early) { exL = isL; exArm = armBar; exSynced = false; }
         Print("Open position #", tk, early ? " kept: it filled before the engine's fill bar (restored trade)." : runner ? " kept: the restored trade runs on after the engine's exit." :
               " does not match the engine state; it will be closed on the next bar (the engine wins).");
      }''')
rb('''   CancelPending();   // a pending order from before the restart has no tracked state
''', '''   if(!(gRestored && exHg && exState == 2)) CancelPending();   // a pending order from before the restart has no tracked state (a restored hedge pair keeps its waiting trade)
''')
rb('''         for(int s = 1; s < bars; s++)''', '''         for(int s = 1; s < Bars(_Symbol, _Period); s++)''')
rb('''      BookBrokerDeals();
      ulong rTk; double rVol, rOp;
''', '''      BookBrokerDeals();
      ulong rTk; double rVol, rOp;
      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseAll(); BookBrokerDeals(); }   // a force-close, weekend start or news start passed while the EA was off
      if(gRestFlat && exHg && exState == 2) CancelPending();
''')
BROKER = '''//--- the broker part of a start: the deals since the saved state, the month, the saved trade, adoption, orders (restart memory: once connected)
void BrokerStart()
{
   long nowAcc = AccountInfoInteger(ACCOUNT_LOGIN);
   if(gRestored && gSvAcc != 0 && nowAcc != 0 && gSvAcc != nowAcc)   // only known now: the saved state belongs to another account
   {
      Print("Restart memory: the saved state belongs to account ", gSvAcc, ", not ", nowAcc, ": starting fresh.");
      MemoryFresh();
   }
''' + B + '''}

int OnInit()'''
assert s.count('\nint OnInit()') == 1
s = s.replace('\nint OnInit()', '\n' + BROKER, 1)

REPS = [
    # globals
    ('string   gSvN[]; double gSvV[]; int gSvC = 0;              //   the values last written (only changes are written)\n',
     '''string   gSvN[]; double gSvV[]; int gSvC = 0;              //   the values last written (only changes are written)
bool     gBrokerPend = false;                             //   the broker part of the start waits until MT5 is connected (positions and deals visible)
bool     gRestFlat = false;                               //   a force-close, weekend start or news start passed while the EA was off
datetime gSvFullT = 0; long gSvAcc = 0;                   //   the last full rewrite (daily: MT5 deletes global variables not accessed for 4 weeks); the saved account
'''),
    # exSynced saved
    ('   IoB("kr", crkRec);\n', '   IoB("kr", crkRec); IoB("xy", exSynced);\n'),
    # daily full rewrite, nothing saved while the broker part waits
    ('   if(!gPersist || gLastDone <= 0) return;                // not before the engine processed a bar (e.g. OnDeinit after a failed start)\n   StateIO(true);\n',
     '''   if(!gPersist || gLastDone <= 0 || gBrokerPend) return;   // not before the engine processed a bar (OnDeinit after a failed start) or the broker part ran
   if(TimeCurrent() - gSvFullT >= 86400) force = true;   // every value at least once a day: MT5 deletes global variables not accessed for 4 weeks
   StateIO(true);
'''),
    ('   gSvC = gIoC;\n   GlobalVariablesFlush();\n', '   gSvC = gIoC;\n   if(force) gSvFullT = TimeCurrent();\n   GlobalVariablesFlush();\n'),
    # load: incomplete-state message, the saved account, stale Labouchere values
    ('''   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer()) return false;
''', '''   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer())
   {
      if(GlobalVariableCheck(gSvBase + "lb")) Print("Restart memory: the saved state is incomplete (unused for 4 weeks?): starting fresh.");
      return false;
   }
'''),
    ('''   StateIO(false);
   gSvC = 0;                                            // the next save writes every value again
''', '''   StateIO(false);
   gSvAcc = (long)MathRound(svAcc);
   for(int q = ArraySize(labSeq); q < 100000 && GlobalVariableCheck(gSvBase + "L" + IntegerToString(q)); q++) GlobalVariableDel(gSvBase + "L" + IntegerToString(q));   // a longer old list
   gSvC = 0;                                            // the next save writes every value again
'''),
    # MemoryFresh + FlatBetween, before ResetEngine
    ('//--- reset every engine / execution variable (MT5 keeps globals when inputs or the timeframe change) ---',
     '''//--- the saved state was not this account's: the money-management state starts fresh (as without restart memory)
void MemoryFresh()
{
   recPool = 0; recLosses = 0; dUnits = 1; carried = 0; LabReset(); parWins = 0; rdUnits = 1; oscU = 1; oscP = 0; totalNet = 0; exW = 0; exLn = 0; capStop = false;
   crkL = 0; crkN = 0; crkW = false; crkP = 0; crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false;
   dayPnl = 0; lossRow = 0; winRow = 0; dayBlock = false; pauseLeft = 0; paused = false; monRestPend = false;
   TradeClear(); gDayPendN = 0; gRestFlat = false; gPauseArm = -1; gRestored = false;
}
//--- a force-close time, a weekend start or a news start between two bars (your time zone), as OnNewBar checks it
bool FlatBetween(datetime utPrev, datetime ut)
{
   bool nStart; NewsBlock(ut, nStart, utPrev);
   int fcM = InpFcH * 60 + InpFcM, curM = MinOfDay(ut), prvM = MinOfDay(utPrev);
   bool fcNow = InpFcOn && (curM >= prvM ? (prvM < fcM && curM >= fcM) : (fcM > prvM || fcM <= curM));
   bool wkndStart = InpWeekendOn && DowOf(ut) == 6 && DowOf(utPrev) != 6;
   return fcNow || wkndStart || nStart;
}

//--- reset every engine / execution variable (MT5 keeps globals when inputs or the timeframe change) ---'''),
    # OnInit: load also on new inputs; the hard-cap Stop
    ('''   if(gPersist && !gInitDone) gRestored = StateLoad();
''', '''   gRestFlat = false; gBrokerPend = false;
   if(gPersist) gRestored = StateLoad();                 // a fresh start or new inputs: continue from the saved state (written at OnDeinit)
   if(gRestored && (gInitDone || !InpCapOn || InpCapAction != CAP_STOP)) capStop = false;   // a hard-cap Stop ends with new inputs (as before) or a cap that no longer stops
'''),
    # warm-up replay: force-close / weekend / news while the EA was off
    ('''         if(evArm && CrkPause()) gPauseArm = armBar;      // armed while paused: the strategy skips it, so it is not placed now
''', '''         if(evArm && CrkPause()) gPauseArm = armBar;      // armed while paused: the strategy skips it, so it is not placed now
         if(FlatBetween(UserTime(iTime(_Symbol, _Period, s + 1)), UserTime(iTime(_Symbol, _Period, s)))) gRestFlat = true;
'''),
    # OnTick: the broker part once connected
    ('''void OnTick()
{
''', '''void OnTick()
{
   if(gBrokerPend)                                       // restart memory: the broker part of the start, once MT5 is connected
   {
      if(TerminalInfoInteger(TERMINAL_CONNECTED) == 0 || AccountInfoInteger(ACCOUNT_LOGIN) == 0) return;
      gBrokerPend = false; BrokerStart(); gStateTxt = StateText(false); UpdateTable();
   }
'''),
]
for old, new in REPS:
    n = s.count(old); assert n == 1, (n, old[:100]); s = s.replace(old, new)
# svAcc must exist in StateLoad: it is declared in the account check of v43c
assert 'double svAcc = GlobalVariableCheck(gSvBase + "acc")' in s
open(P, 'w', encoding='utf8').write(s); print(len(REPS) + 7, 'edits; lines', s.count('\n'))
