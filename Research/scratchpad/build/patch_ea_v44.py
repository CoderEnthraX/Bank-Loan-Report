"""EA v4.4: a trade of this EA is never closed early; outside closes are booked right; who closed each trade is logged.
A  The take profit goes to the broker with the order (OrderExits), not only when the engine confirms the fill at the next bar close.
B  No "engine wins" close: a trade the engine is not in (filled before the engine on a narrower spread, its setup ended, new inputs,
   another timeframe, an order that filled while being cancelled) runs to its own stop loss and take profit. The engine's events count for
   the EA's own setup only (EngStep: the arm bar; ProcessBar is untouched). Exits that still close at market: the engine's stop, or its
   final target without earn-back, for the trade it is in; force-close / weekend / news start (as before).
C  Deals are the EA's by magic number OR by the position it opened: a trade closed by hand, from the phone app or by another EA is booked
   with its real profit (v4.3 booked it as a $0 loss). Same in ExitDealAfter (restart) and MonthFromHistory.
D  Every close is logged: the EA's reason, or who closed it (stop loss, take profit, stop-out, this EA, by hand, phone, web, another EA).
E  One copy per symbol + magic number (a temporary global variable lock); a note on other EAs in the terminal.
F  Broker server clock: new choice Auto (default): read from MT5 (server time - GMT) live; Strategy Tester: EU summer time as before.
   Any choice: a message when the broker's clock differs from it.
G  Restart / new inputs / another timeframe: the trade's setup is identified by its arm bar time and entry (saved: xa, xe), so the trade is
   re-linked to the engine only when it is the same setup; otherwise kept on its own levels. Partial levels are the trade's own (x1-x3).
H  Input "Start fresh once" (restart memory group): forgets the loss recovery, streaks and pauses once.
Every replacement must match exactly once."""
P = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5'
s = open(P, encoding='utf8').read()
n_edits = 0


def rep(old, new):
    global s, n_edits
    c = s.count(old)
    assert c == 1, (c, old[:120])
    s = s.replace(old, new)
    n_edits += 1


def box(lines):
    w = len('//| v4.3: RESTART MEMORY: the loss recovery, streaks, pauses and the |')
    out = []
    for t in lines:
        ln = '//| ' + t
        assert len(ln) <= w - 2, t
        out.append(ln + ' ' * (w - 2 - len(ln)) + ' |')
    return '\n'.join(out) + '\n'


# ---------------------------------------------------------------- header, version
rep('''//| variables; trades that closed meanwhile are booked).             |
//+------------------------------------------------------------------+
#property copyright "Auction Retest Model"
#property version   "4.30"''',
    '''//| variables; trades that closed meanwhile are booked).             |
''' + box(['v4.4: no early closes: the take profit goes to the broker with',
           'the order, and a trade the engine stops following runs to its',
           'own stop loss and take profit. Trades closed by hand, the phone',
           'app or another EA are booked with their real profit; the log',
           'says who closed each trade and why. One copy per symbol and',
           'magic number. The broker server clock is read from MT5 (Auto).']) +
    '''//+------------------------------------------------------------------+
#property copyright "Auction Retest Model"
#property version   "4.40"''')

# ---------------------------------------------------------------- inputs
rep('''enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // Auto: GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1,   // Fixed: the GMT offset below
                   SRV_EET     = 2 }; // Auto: GMT+2 winter / GMT+3 EU summer time (EET brokers, e.g. FxPro)
input ENUM_SRV_TZ InpServerTz = SRV_EET;     // Broker server clock''',
    '''enum ENUM_SRV_TZ { SRV_NYCLOSE = 0,   // GMT+2 winter / GMT+3 US summer time (most FX brokers)
                   SRV_FIXED   = 1,   // Fixed: the GMT offset below
                   SRV_EET     = 2,   // GMT+2 winter / GMT+3 EU summer time (EET brokers, e.g. FxPro)
                   SRV_AUTO    = 3 }; // Auto: read the broker's clock from MT5 (Strategy Tester: EU summer time)
input ENUM_SRV_TZ InpServerTz = SRV_AUTO;    // Broker server clock''')
rep('''input bool   InpRemember = true;   // Continue after a restart (keep the loss recovery, streaks and pauses when MT5 or the EA restarts)
''', '''input bool   InpRemember = true;   // Continue after a restart (keep the loss recovery, streaks and pauses when MT5 or the EA restarts)
input bool   InpMemFresh = false;  // Start fresh once: forget the loss recovery, streaks and pauses (true + OK; set false again later)
''')

# ---------------------------------------------------------------- globals
rep('''datetime gSvFullT = 0; long gSvAcc = 0;                   //   the last full rewrite (daily: MT5 deletes global variables not accessed for 4 weeks); the saved account
''', '''datetime gSvFullT = 0; long gSvAcc = 0;                   //   the last full rewrite (daily: MT5 deletes global variables not accessed for 4 weeks); the saved account
// v4.4
int      gTzMode = SRV_EET; double gTzFix = 2.0, gTzDet = -99; bool gTzWarned = false;   // broker clock: the rule in use (Auto) and its fixed offset; the offset read now (-99 unknown)
string   gCloseWhy = ""; long gCloseId = 0;                // why this EA closed a trade last, and that trade's position id
string   gLastClose = "-"; bool gLastCloseOut = false;     // table: the last close; closed outside this EA (by hand, phone, another EA)
datetime exArmT = 0; double exLim = 0;                    // the EA's trade: its setup's arm bar time and entry level (re-linked after a restart / new inputs)
double   exTpL[3];                                        // the trade's own TP1-TP3 levels (partials)
bool     gOurFill = false, gOurExit = false, gOurWin = false, gOurMove = false;   // the engine's events for the EA's setup (arm bar exArm) on the last processed bar
bool     gMissFill = false, gMissExit = false, gMissWin = false, gMissMove = false;   //   ... on bars caught up after a disconnect
string   gLockN = ""; double gLockV = 0;                  // one copy per symbol + magic number (temporary global variable)
''')

# ---------------------------------------------------------------- server clock
rep('''double SrvGMT(datetime server)
{
   if(InpServerTz == SRV_FIXED) return InpServerGMT;
   MqlDateTime d; TimeToStruct(server, d);
   if(InpServerTz == SRV_EET)                         // EU summer time: last Sunday of March to last Sunday of October
   {''', '''// the GMT offset of a summer-time rule (SRV_EET or SRV_NYCLOSE) at a server time
double RuleGMT(int md, datetime server)
{
   MqlDateTime d; TimeToStruct(server, d);
   if(md == SRV_EET)                                  // EU summer time: last Sunday of March to last Sunday of October
   {''')
rep('''   int ds = NthSunday(d.year, 3, 2), de = NthSunday(d.year, 11, 1);
   bool dst = (d.mon > 3 && d.mon < 11) || (d.mon == 3 && d.day >= ds) || (d.mon == 11 && d.day < de);
   return dst ? 3.0 : 2.0;
}
''', '''   int ds = NthSunday(d.year, 3, 2), de = NthSunday(d.year, 11, 1);
   bool dst = (d.mon > 3 && d.mon < 11) || (d.mon == 3 && d.day >= ds) || (d.mon == 11 && d.day < de);
   return dst ? 3.0 : 2.0;
}
double SrvGMT(datetime server)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;   // Auto: the rule picked from the broker's clock (TzPick)
   if(md == SRV_FIXED) return InpServerTz == SRV_AUTO ? gTzFix : InpServerGMT;
   return RuleGMT(md, server);
}
''')
rep('''datetime UtcTime(datetime server)  { return server - (datetime)(SrvGMT(server) * 3600); }
''', '''datetime UtcTime(datetime server)  { return server - (datetime)(SrvGMT(server) * 3600); }
//--- names the restart memory never deletes ("Continue after a restart" off): the copy lock, the broker clock, "Start fresh once"
string SvExtra(string k) { return "ARX" + StringSubstr(gSvBase, 3) + k; }
//--- the broker's GMT offset now, read from MT5 (server time - GMT, to the nearest half hour); live and connected only, -99 = unknown
double TzNow()
{
   if(MQLInfoInteger(MQL_TESTER) != 0 || TerminalInfoInteger(TERMINAL_CONNECTED) == 0) return -99;
   datetime sv = TimeTradeServer(), g = TimeGMT();
   if(sv <= 0 || g <= 0) return -99;
   double d = MathRound((double)(sv - g) / 1800.0) / 2.0;
   return MathAbs(d) <= 14 ? d : -99;
}
string GmtTxt(double h) { return "GMT" + (h >= 0 ? "+" : "") + (MathAbs(h - MathRound(h)) < 0.01 ? IntegerToString((int)MathRound(h)) : DoubleToString(h, 1)); }
string TzTxt()                                          // the broker clock in use now (table)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;
   string r = GmtTxt(SrvGMT(TimeCurrent())) + (InpServerTz == SRV_AUTO ? " auto" : "") + (md == SRV_EET ? " (EU summer time)" : md == SRV_NYCLOSE ? " (US summer time)" : " (fixed)");
   if(gTzDet > -90 && MathAbs(SrvGMT(TimeCurrent()) - gTzDet) > 0.01) r += " | broker " + GmtTxt(gTzDet) + ": CHECK";
   return r;
}
//--- Auto: the summer-time rule that gives the broker's offset now (EU first, as FxPro; then US), else that offset fixed. While MT5 is not
//--- connected yet, the clock read last time. Any choice: one message when the broker's clock differs from it (your days, hours, kill zones,
//--- news and force-close would be off by the difference)
void TzPick(bool atStart)
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;          // Strategy Tester: no real clock (Auto = EU summer time)
   gTzDet = TzNow();
   int md = gTzMode; double fx = gTzFix;
   if(gTzDet > -90)
   {
      datetime now = TimeTradeServer();
      if(RuleGMT(SRV_EET, now) == gTzDet) md = SRV_EET;
      else if(RuleGMT(SRV_NYCLOSE, now) == gTzDet) md = SRV_NYCLOSE;
      else { md = SRV_FIXED; fx = gTzDet; }
      GlobalVariableSet(SvExtra("tzm"), md); GlobalVariableSet(SvExtra("tzf"), fx);
   }
   else if(atStart && GlobalVariableCheck(SvExtra("tzm")))   // not connected yet: the clock read last time
   {
      md = (int)MathRound(GlobalVariableGet(SvExtra("tzm")));
      if(GlobalVariableCheck(SvExtra("tzf"))) fx = GlobalVariableGet(SvExtra("tzf"));
      if(md != SRV_EET && md != SRV_NYCLOSE && md != SRV_FIXED) md = SRV_EET;
   }
   if(InpServerTz == SRV_AUTO)
   {
      bool chg = md != gTzMode || (md == SRV_FIXED && fx != gTzFix);
      gTzMode = md; gTzFix = fx;
      if(chg && !atStart) Print("Broker server clock is ", GmtTxt(SrvGMT(TimeTradeServer())), " now (read from MT5): your times follow it from here on.");
      if(atStart && gTzDet > -90) Print("Broker server clock: ", TzTxt(), " (read from MT5).");
   }
   else if(gTzDet > -90 && MathAbs(SrvGMT(TimeTradeServer()) - gTzDet) > 0.01 && !gTzWarned)
   {
      gTzWarned = true;
      string m = "The broker's server clock is " + GmtTxt(gTzDet) + ", but 'Broker server clock' gives " + GmtTxt(SrvGMT(TimeTradeServer())) +
                 ": your days, hours, kill zones, news and force-close times are off. Choose 'Auto: read the broker's clock from MT5'.";
      Print(m); Alert(m);
   }
}
''')

# ---------------------------------------------------------------- CloseAll with a reason
rep('''void CloseAll()
{
   ulong tk; double v, op;
   int guard = 0;
   while(HasPosition(tk, v, op) && guard++ < 5) { if(!trade.PositionClose(tk)) break; }
}''', '''void CloseAll(string why)
{
   ulong tk; double v, op;
   int guard = 0;
   if(HasPosition(tk, v, op)) { gCloseWhy = why; gCloseId = PositionGetInteger(POSITION_IDENTIFIER); Print("Closing #", tk, " (", DoubleToString(v, 2), " lots): ", why); }
   while(HasPosition(tk, v, op) && guard++ < 5)
   {
      gCloseId = PositionGetInteger(POSITION_IDENTIFIER);
      if(!trade.PositionClose(tk)) { Print("Close of #", tk, " failed: ", trade.ResultRetcodeDescription()); break; }
   }
}''')

# ---------------------------------------------------------------- deals: by magic number or by the position this EA opened; close report
rep('''// realised P&L of this EA's deals since the last call (profit + commission + swap + fee); closed = an exit deal was seen
double NewDealsPnl(bool &closed)
{
   closed = false;
   double sum = 0;
   if(!HistorySelect(0, TimeCurrent() + 86400)) return 0;
   int n = HistoryDealsTotal();
   ulong maxTk = lastDeal;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(tk > maxTk) maxTk = tk;
      if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      sum += HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      long entry = HistoryDealGetInteger(tk, DEAL_ENTRY);
      if(entry == DEAL_ENTRY_OUT || entry == DEAL_ENTRY_INOUT || entry == DEAL_ENTRY_OUT_BY) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); }
   }
   lastDeal = maxTk;
   return sum;
}
''', '''string DateTxt(datetime tm, bool withYear);            // defined below
// a position this EA opened: a deal with its magic number for that position id in the selected history (n deals)
bool OurPosId(long pid, int n)
{
   if(pid <= 0) return false;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk != 0 && HistoryDealGetInteger(tk, DEAL_POSITION_ID) == pid && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && HistoryDealGetString(tk, DEAL_SYMBOL) == _Symbol) return true;
   }
   return false;
}
bool IsExitDeal(ulong tk) { long e = HistoryDealGetInteger(tk, DEAL_ENTRY); return e == DEAL_ENTRY_OUT || e == DEAL_ENTRY_INOUT || e == DEAL_ENTRY_OUT_BY; }
// a deal of this EA: its magic number, or the exit of a trade it opened (closed by hand, from the phone app or by another EA)
bool DealIsMine(ulong tk, int n)
{
   if(HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol) return false;
   if(HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic) return true;
   return IsExitDeal(tk) && OurPosId(HistoryDealGetInteger(tk, DEAL_POSITION_ID), n);
}
// who closed a trade, from its exit deal
string CloseBy(ulong tk)
{
   long rs = HistoryDealGetInteger(tk, DEAL_REASON), mg = HistoryDealGetInteger(tk, DEAL_MAGIC), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   if(rs == DEAL_REASON_SL) return "its stop loss";
   if(rs == DEAL_REASON_TP) return "its take profit";
   if(rs == DEAL_REASON_SO) return "a margin stop-out";
   if(rs == DEAL_REASON_EXPERT)
      return mg != InpMagic ? "ANOTHER EA OR SCRIPT (magic " + IntegerToString(mg) + ")" :
             pid == gCloseId && gCloseWhy != "" ? "this EA: " + gCloseWhy : "an EA with this magic number (a second copy of this EA?)";
   if(rs == DEAL_REASON_CLIENT) return "HAND (MetaTrader on the computer)";
   if(rs == DEAL_REASON_MOBILE) return "HAND (the phone app)";
   if(rs == DEAL_REASON_WEB) return "HAND (the web terminal)";
   return "the broker (reason " + IntegerToString(rs) + ")";
}
// one line in the log (Experts tab) and the table for every closing deal of this EA's trades
void CloseReport(ulong tk, double p)
{
   long rs = HistoryDealGetInteger(tk, DEAL_REASON), pid = HistoryDealGetInteger(tk, DEAL_POSITION_ID);
   string who = CloseBy(tk);
   gLastCloseOut = !(rs == DEAL_REASON_SL || rs == DEAL_REASON_TP || (rs == DEAL_REASON_EXPERT && HistoryDealGetInteger(tk, DEAL_MAGIC) == InpMagic && pid == gCloseId));
   gLastClose = (p >= 0 ? "+" : "") + DoubleToString(p, 2) + " | " + who + " | " + DateTxt(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), false);
   Print("Trade #", pid, " closed: ", DoubleToString(HistoryDealGetDouble(tk, DEAL_VOLUME), 2), " lots at ", DoubleToString(HistoryDealGetDouble(tk, DEAL_PRICE), _Digits),
         ", ", (p >= 0 ? "+" : ""), DoubleToString(p, 2), " | closed by ", who);
   if(gLastCloseOut && rs != DEAL_REASON_SO) Print("This trade was closed outside this EA's rules. Its profit is booked, and the loss recovery goes on from it.");
}
// realised P&L of this EA's deals since the last call (profit + commission + swap + fee); closed = an exit deal was seen; quiet: no report
// (skipping old history)
double NewDealsPnl(bool &closed, bool quiet = false)
{
   closed = false;
   double sum = 0;
   if(!HistorySelect(0, TimeCurrent() + 86400)) return 0;
   int n = HistoryDealsTotal();
   ulong maxTk = lastDeal;
   for(int i = 0; i < n; i++)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= lastDeal) continue;
      if(tk > maxTk) maxTk = tk;
      if(!DealIsMine(tk, n)) continue;                  // v4.4: also the exit of this EA's trade by hand, from the phone app or by another EA
      double p = HistoryDealGetDouble(tk, DEAL_PROFIT) + HistoryDealGetDouble(tk, DEAL_COMMISSION) + HistoryDealGetDouble(tk, DEAL_SWAP) + HistoryDealGetDouble(tk, DEAL_FEE);
      sum += p;
      if(IsExitDeal(tk)) { closed = true; gLastOutProfit = HistoryDealGetDouble(tk, DEAL_PROFIT); if(!quiet) CloseReport(tk, p); }
   }
   lastDeal = maxTk;
   return sum;
}
''')

# ---------------------------------------------------------------- the engine's events for the EA's own setup; bar times
rep('''//--- lots for a $ risk and a stop distance --------------------------------
''', '''//--- the engine's events for the EA's own setup (arm bar exArm): ProcessBar plus which of its events are this trade's. A fill (step 2) is
//--- always the setup armed before the bar; an exit is the live trade's (step 1) or a stop on its fill bar (step 2); a stop move is the
//--- live trade's. ProcessBar itself is untouched (the same engine as the TradingView files)
void EngStep(int s)
{
   long pa = armBar; int ps = st;
   ProcessBar(s);
   bool mine = exArm >= 0 && pa == exArm;
   gOurFill = mine && evFill;
   gOurExit = evExit && ((mine && MathAbs(ps) == 2) || gOurFill);
   gOurWin  = gOurExit && evWin;
   gOurMove = mine && MathAbs(ps) == 2 && evMove;
}
//--- open time of the bar with engine index idx (the last processed bar is shift 1: after OnNewBar, a start, a catch-up)
datetime BarTimeOf(long idx)
{
   if(idx < 0) return 0;
   int s = (int)(bi - idx) + 1;
   return s >= 1 && s < Bars(_Symbol, _Period) ? iTime(_Symbol, _Period, s) : 0;
}

//--- lots for a $ risk and a stop distance --------------------------------
''')

# ---------------------------------------------------------------- order levels: the take profit with the order
rep('''double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
''', '''double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
//--- an entry order's stop loss and take profit (v4.4: the target goes to the broker with the order): the engine's levels for this setup, kept
//--- outside the stops level from the order price (pending) and the price (market); SetExits re-sends the engine's levels once it has filled
void OrderExits(bool isL, double ep, double &sl, double &tp)
{
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), minD = MinDist();
   sl = exT1 ? exT1Stop : StopPx(isL);
   tp = exT1 ? TgtPx(isL, exT1Tp2) : TgtPx(isL, tF);   // Crooks TP1 rule: the rest's TP2 (its TP1 part closes at market)
   if(isL) { sl = MathMin(sl, FloorTick(MathMin(ep, bid) - minD)); tp = MathMax(tp, CeilTick(MathMax(ep, bid) + minD)); }
   else    { sl = MathMax(sl, CeilTick(MathMax(ep, ask) + minD)); tp = MathMin(tp, FloorTick(MathMin(ep, ask) - minD)); }
}
''')
rep('''   if(a != b) { CloseAll(); Print("Hedge: only one of the two trades opened, so it was closed again."); return false; }''',
    '''   if(a != b) { CloseAll("hedge pair: only one of the two trades opened"); return false; }''')
rep('''   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp))) { CloseAll(); return; }''',
    '''   if(exL ? (bid <= sl || (tp > 0 && bid >= tp)) : (ask >= sl || (tp > 0 && ask <= tp)))
   { CloseAll((exL ? bid <= sl : ask >= sl) ? "the price is already past the stop" : "the price is already past the target"); return; }''')
rep('''   else CloseAll();                                   // too small to split: close it all at TP1''',
    '''   else CloseAll("Crooks TP1 rule: TP1 reached, too small to split, all closed");   // too small to split: close it all at TP1''')

# ---------------------------------------------------------------- TakeSetup / VirtualEntry
rep('''   exT1Tp1 = t1; exT1Tp2 = t2; exKeepSl = 0; exHg = false; exHgS = hgS; exHgT = hgT; gLastOutProfit = 0;
   for(int q = 0; q < 3; q++) pDone[q] = false;
   CancelPending();
   gVirt = false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ep = EntryPx(isL), sl = exT1 ? exT1Stop : StopPx(isL);
   double minD = MinDist();
   // the order's SL must respect the stops level; SetExits re-sends the engine's stop once the engine has filled
   if(isL) sl = MathMin(sl, FloorTick(MathMin(ep, bid) - minD));
   else    sl = MathMax(sl, CeilTick(MathMax(ep, ask) + minD));
   bool ok;
   if(hg) ok = PlaceHedge(isL, v);
   else if(InpEntryMode == ENTRY_MARKET)
      ok = isL ? trade.Buy(v, _Symbol, 0, sl, 0, "ARM") : trade.Sell(v, _Symbol, 0, sl, 0, "ARM");
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) ok = trade.BuyLimit(v, ep, _Symbol, sl, 0, ORDER_TIME_GTC, 0, "ARM");
      else if(ask <= ep)                ok = trade.Buy(v, _Symbol, 0, sl, 0, "ARM");   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                 // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) ok = trade.SellLimit(v, ep, _Symbol, sl, 0, ORDER_TIME_GTC, 0, "ARM");
      else if(bid >= ep)                ok = trade.Sell(v, _Symbol, 0, sl, 0, "ARM");
      else { ok = true; gVirt = true; }
   }
   if(ok) { exState = 1; exArm = armBar; exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }''',
    '''   exT1Tp1 = t1; exT1Tp2 = t2; exKeepSl = 0; exHg = false; exHgS = hgS; exHgT = hgT; gLastOutProfit = 0;
   exTpL[0] = t1; exTpL[1] = t2; exTpL[2] = t3; exLim = lim;   // the trade's own levels (partials, restart)
   for(int q = 0; q < 3; q++) pDone[q] = false;
   CancelPending();
   gVirt = false;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ep = EntryPx(isL), sl, tp;
   double minD = MinDist();
   OrderExits(isL, ep, sl, tp);                        // v4.4: the stop loss and the take profit go with the order
   bool ok;
   if(hg) ok = PlaceHedge(isL, v);
   else if(InpEntryMode == ENTRY_MARKET)
      ok = isL ? trade.Buy(v, _Symbol, 0, sl, tp, "ARM") : trade.Sell(v, _Symbol, 0, sl, tp, "ARM");
   else if(isL)
   {
      if(ask - ep >= MathMax(minD, ts)) ok = trade.BuyLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM");
      else if(ask <= ep)                ok = trade.Buy(v, _Symbol, 0, sl, tp, "ARM");   // at / through the level: the engine fills on this bar
      else { ok = true; gVirt = true; }                                                  // inside the stops distance: wait for the level (VirtualEntry)
   }
   else
   {
      if(ep - bid >= MathMax(minD, ts)) ok = trade.SellLimit(v, ep, _Symbol, sl, tp, ORDER_TIME_GTC, 0, "ARM");
      else if(bid >= ep)                ok = trade.Sell(v, _Symbol, 0, sl, tp, "ARM");
      else { ok = true; gVirt = true; }
   }
   if(ok) { exState = 1; exArm = armBar; exArmT = BarTimeOf(armBar); exSynced = false; takenN++; crkRec = CrkRecNext(); exHg = hg; }''')
rep('''   double ep = EntryPx(exL), sl = exT1 ? exT1Stop : StopPx(exL);
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      if(!(exL ? trade.Buy(exLots, _Symbol, 0, sl, 0, "ARM") : trade.Sell(exLots, _Symbol, 0, sl, 0, "ARM")))''',
    '''   double ep = EntryPx(exL), sl, tp;
   if(exL ? ask <= ep : bid >= ep)
   {
      gVirt = false;
      OrderExits(exL, ep, sl, tp);                     // v4.4: the take profit goes with the order
      if(!(exL ? trade.Buy(exLots, _Symbol, 0, sl, tp, "ARM") : trade.Sell(exLots, _Symbol, 0, sl, tp, "ARM")))''')

# ---------------------------------------------------------------- BookClosed: the trade's own levels are cleared
rep('''   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false; exHg = false;
   CancelPending();
}''', '''   exState = 0; exPnl = 0; exArm = -1; exSynced = false; gVirt = false; exHg = false;
   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0;
   CancelPending();
}''')

# ---------------------------------------------------------------- OnNewBar
rep('''void OnNewBar()
{
   ProcessBar(1);
''', '''void OnNewBar()
{
   EngStep(1);
   if(gMissFill) gOurFill = true;                       // the engine's events for the EA's setup on bars caught up after a disconnect
   if(gMissMove) gOurMove = true;
   if(gMissExit && !gOurExit) { gOurExit = true; gOurWin = gMissWin; }
   gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
''')
rep('''   DayStart(gDayPendN + (gNewDay ? 1 : 0)); gDayPendN = 0;   // each new day since the last bar (several after a disconnect or a restart)
''', '''   DayStart(gDayPendN + (gNewDay ? 1 : 0)); gDayPendN = 0;   // each new day since the last bar (several after a disconnect or a restart)
   if(gNewDay) TzPick(false);                           // the broker's clock, once a day
''')
rep('''   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   bool exClosed = (exState == 1 && !pos && closedNew) || (exState == 2 && !pos);
''', '''   ulong pTk; double pVol, pOpen; bool pos = HasPosition(pTk, pVol, pOpen);
   if(exState == 1 && pos) exState = 2;
   if(exState == 0 && pos && !exHg)                    // the order filled while it was being cancelled: a trade of this EA, kept on its own levels
   {
      exState = 2; exArm = -1; exSynced = false;
      Print("Position #", pTk, " of this EA filled while its order was being cancelled: kept, it runs to its own stop loss and take profit.");
   }
   bool exClosed = (exState == 1 && !pos && closedNew) || (exState == 2 && !pos);
''')
rep('''   // 3. follow the engine (only the setup the EA took); state based, so it also covers bars caught up after a disconnect
   bool exMine = exArm >= 0 && armBar == exArm;
   if(exState == 1 && !(MathAbs(st) == 1 && exMine))   // the engine no longer holds the EA's armed setup: expired, replaced or filled
   {
      CancelPending();
      if(exMine && lastFill > exArm) missN++;          // engine filled, broker did not
      exState = 0; exArm = -1; gVirt = false; exHg = false;
   }
   if(exState == 2 && exMine && MathAbs(st) == 2) exSynced = true;   // the engine is in the EA's setup (filled on this bar or a caught-up bar)
''', '''   // 3. follow the engine for the EA's own setup only (its arm bar exArm). The engine's fill confirms the trade (its levels are re-sent), a stop
   //    move moves the broker's stop, and the engine's stop (or its final target without earn-back) on the bar chart closes it. v4.4: a trade
   //    the engine is not in (filled before the engine on a narrower spread, its setup ended, new inputs, another timeframe) is never closed
   //    early: it runs to its own stop loss and take profit, which went to the broker with the order
   bool exMine = exArm >= 0 && armBar == exArm;
   if(exState == 1 && !(MathAbs(st) == 1 && exMine))   // the engine no longer holds the EA's armed setup: expired, replaced or filled
   {
      CancelPending();
      if(exMine && lastFill > exArm) missN++;          // engine filled, broker did not
      exState = 0; exArm = -1; gVirt = false; exHg = false;
   }
   if(exState == 2 && exArm >= 0 && !exHg)
   {
      if(gOurFill || (exMine && MathAbs(st) == 2)) exSynced = true;   // the engine filled the EA's setup (this bar, a caught-up bar, or before)
      if(!exSynced && !(exMine && MathAbs(st) == 1))   // filled at the broker first, and the engine's setup ended without its fill
      {
         Print("Trade #", pTk, " filled before the engine's fill (bid chart) and its setup ended: kept, it runs to its own stop loss and take profit.");
         exArm = -1;
      }
   }
''')
rep('''   bool t1Due = (((evExit && evWin) || t1Bar) && exMine) || gT1Seen;''',
    '''   bool t1Due = (gOurExit && gOurWin) || t1Bar || gT1Seen;''')
rep('''   if(exState == 2 && exMine && !exHg && (evFill || evMove)) SetExits(true);
   if(evExit && exState == 2 && exMine && !exHg && (!InpEarnBack || !evWin) && !(exT1 && (evWin || exT1Half))) CloseAll();   // engine exited: never stay in (earn-back and the Crooks TP1 rule only outlive a win)
''', '''   if(exState == 2 && exMine && MathAbs(st) == 2 && !exHg && (gOurFill || gOurMove)) SetExits(true);   // the engine's levels are this trade's only while it is in it
   if(gOurExit && exState == 2 && !exHg)
   {
      // the engine's trade ended: its stop, or its final target without earn-back, closes the trade (earn-back and the Crooks TP1 rule only outlive a win)
      if((!InpEarnBack || !gOurWin) && !(exT1 && (gOurWin || exT1Half)))
         CloseAll(gOurWin ? "the engine's final target was reached (bar close, bid chart)" : "the engine's stop was hit (bar close, bid chart)");
      exArm = -1;                                       // the engine is done with this trade: a runner goes on to its own levels
   }
''')
rep('''   // engine wins: close a broker position the engine is not in (early fill on a spread spike, a fill racing a cancel,
   // or an engine exit on a bar caught up after a disconnect); with earn-back a synced trade may outlive the engine exit
   bool engHolds = (MathAbs(st) == 2 && exSynced && exMine) || (MathAbs(st) == 1 && !exSynced && exState == 2 && exMine);
   if(pos && !exClosed && !evExit && !engHolds && !(InpEarnBack && exSynced) && !(exT1 && exSynced) && !exHg)
   {
      CloseAll(); exState = 2;   // booked on the next bar unless the exit deal is already visible
      ulong cTk; double cVol, cOp;
      if(!HasPosition(cTk, cVol, cOp))
      {
         bool cn; double np = NewDealsPnl(cn);
         exPnl += np; totalNet += np; if(np != 0 || cn) carried = MathMax(0.0, carried - np);
         if(cn) BookClosed();   // closed now: the engine's new setup on this bar can be taken
      }
   }
''', '''   // v4.4: no "engine wins" close any more (v4.3 closed a trade the engine was not in at the next bar, at whatever price it was)
''')
rep('''   if(flatNow && pos) CloseAll();''',
    '''   if(flatNow && pos) CloseAll(fcNow ? "the daily force-close time" : wkndStart ? "the weekend starts (Saturday)" : "a news window starts");''')

# ---------------------------------------------------------------- partials: the trade's own levels
rep('''   tp[0] = t1; tp[1] = t2; tp[2] = t3;
''', '''   bool eng = exArm >= 0 && armBar == exArm && MathAbs(st) == 2;   // the engine's levels are this trade's while it is in it
   tp[0] = exTpL[0] > 0 ? exTpL[0] : eng ? t1 : 0; tp[1] = exTpL[1] > 0 ? exTpL[1] : eng ? t2 : 0; tp[2] = exTpL[2] > 0 ? exTpL[2] : eng ? t3 : 0;   // the trade's own levels (v4.4)
''')
rep('''      if(k + 1 >= exitK || pp[k] <= 0 || pDone[k]) continue;''',
    '''      if(k + 1 >= exitK || pp[k] <= 0 || pDone[k] || tp[k] <= 0) continue;''')

# ---------------------------------------------------------------- restart memory: the trade's setup and levels
rep('''   IoB("kr", crkRec); IoB("xy", exSynced);
''', '''   IoB("kr", crkRec); IoB("xy", exSynced);
   double xe = exLim, x1 = exTpL[0], x2 = exTpL[1], x3 = exTpL[2];   // v4.4: the trade's setup (arm bar time, entry) and its own TP1-TP3
   IoT("xa", exArmT); IoD("xe", xe); IoD("x1", x1); IoD("x2", x2); IoD("x3", x3);
   exLim = xe; exTpL[0] = x1; exTpL[1] = x2; exTpL[2] = x3;
''')
rep('''   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
''', '''   exState = 0; exPnl = 0; exLots = 0; exRiskAmt = 0; exCostPx = 0; exKeepSl = 0; exArm = -1; exSynced = false; gVirt = false;
   exArmT = 0; exLim = 0; for(int q = 0; q < 3; q++) exTpL[q] = 0;
''')
rep('''bool ExitDealAfter(ulong cursor)
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
}''', '''bool ExitDealAfter(ulong cursor)
{
   if(!HistorySelect(0, TimeCurrent() + 86400)) return false;
   int n = HistoryDealsTotal();
   for(int i = n - 1; i >= 0; i--)
   {
      ulong tk = HistoryDealGetTicket(i);
      if(tk == 0 || tk <= cursor) continue;
      if(IsExitDeal(tk) && DealIsMine(tk, n)) return true;   // v4.4: also closed by hand, from the phone app or by another EA
   }
   return false;
}''')
rep('''   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)
   bool c; NewDealsPnl(c);                              // no trade of this EA was open: later deals are not its trades''',
    '''   TradeClear();                                        // nothing filled: a waiting order is re-placed from the engine's setup (CancelPending, gRearm)
   bool c; NewDealsPnl(c, true);                        // no trade of this EA was open: later deals are not its trades''')
rep('''      if(tk == 0 || HistoryDealGetString(tk, DEAL_SYMBOL) != _Symbol || HistoryDealGetInteger(tk, DEAL_MAGIC) != InpMagic) continue;
      MqlDateTime dd; TimeToStruct(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), dd);''',
    '''      if(tk == 0 || !DealIsMine(tk, n)) continue;      // v4.4: also an exit by hand, from the phone app or by another EA
      MqlDateTime dd; TimeToStruct(UserTime((datetime)HistoryDealGetInteger(tk, DEAL_TIME)), dd);''')

# ---------------------------------------------------------------- ResetEngine
rep('''   gDrawT = 0; ArrayResize(gDrawn, 0); gStateTxt = "SCANNING";
}''', '''   gDrawT = 0; ArrayResize(gDrawn, 0); gStateTxt = "SCANNING";
   exArmT = 0; exLim = 0; ArrayInitialize(exTpL, 0.0);
   gOurFill = false; gOurExit = false; gOurWin = false; gOurMove = false; gMissFill = false; gMissExit = false; gMissWin = false; gMissMove = false;
}''')

# ---------------------------------------------------------------- BrokerStart
rep('''   if(!gRestored) { bool c; NewDealsPnl(c); }            // do not count old history (restored: the deals since the saved state are booked below)''',
    '''   TzPick(false);                                        // the broker's clock, now that MT5 is connected
   if(!gRestored) { bool c; NewDealsPnl(c, true); }      // do not count old history (restored: the deals since the saved state are booked below)''')
rep('''   else if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      if((isL && st == 2) || (!isL && st == -2))
      {
         double oldSl = PositionGetDouble(POSITION_SL);
         exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol; exArm = armBar; exSynced = true;   // a restored trade keeps its lots (partials)
         for(int q = 0; q < 3; q++) pDone[q] = pDone[q] || tpHit >= q + 1;
         Print("Adopted open position #", tk, " (engine is in the same trade).");
         // never widen the stop of an adopted position (a Crooks TP1-rule position is sized for its tighter stop): SetExits keeps it from now on
         exKeepSl = oldSl > 0 && (isL ? oldSl > StopPx(isL) : oldSl < StopPx(isL)) ? oldSl : 0;
         SetExits(true);
      }
      else
      {
         exState = 2;
         bool early = gRestored && MathAbs(st) == 1 && (st > 0) == isL;          // restored: the broker filled before the engine's fill bar
         bool runner = gRestored && exSynced && (exT1 || InpEarnBack);           // restored: a Crooks TP1-rule rest or an earn-back trade outliving the engine's exit
         if(early) { exL = isL; exArm = armBar; exSynced = false; }
         Print("Open position #", tk, early ? " kept: it filled before the engine's fill bar (restored trade)." : runner ? " kept: the restored trade runs on after the engine's exit." :
               " does not match the engine state; it will be closed on the next bar (the engine wins).");
      }
   }''', '''   else if(HasPosition(tk, vol, op) && PositionSelectByTicket(tk))
   {
      bool isL = PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY;
      double pSl = PositionGetDouble(POSITION_SL), pTp = PositionGetDouble(POSITION_TP);
      datetime aT = MathAbs(st) >= 1 && !trGhost ? BarTimeOf(armBar) : 0;
      // v4.4: the engine's setup is this trade's when it is the saved setup (arm bar time and entry, restart memory); without a saved setup,
      // when it has the trade's direction and was armed before the trade opened
      bool same = aT > 0 && (st > 0) == isL &&
                  (gRestored && exArmT > 0 ? aT == exArmT && (exLim <= 0 || MathAbs(lim - exLim) <= TickSize() * 2.5)
                                           : (datetime)PositionGetInteger(POSITION_TIME) >= aT + PeriodSeconds(_Period));
      exState = 2; exL = isL; if(!(gRestored && exLots > 0)) exLots = vol;   // a restored trade keeps its lots (partials)
      if(same && MathAbs(st) == 2)
      {
         exArm = armBar; exArmT = aT; exLim = lim; exSynced = true;
         for(int q = 0; q < 3; q++) pDone[q] = pDone[q] || tpHit >= q + 1;
         Print("Adopted open position #", tk, " (engine is in the same trade).");
         // never widen the stop of an adopted position (a Crooks TP1-rule position is sized for its tighter stop): SetExits keeps it from now on
         exKeepSl = pSl > 0 && (isL ? pSl > StopPx(isL) : pSl < StopPx(isL)) ? pSl : 0;
         SetExits(true);
      }
      else if(same)
      {
         exArm = armBar; exArmT = aT; exLim = lim; exSynced = false;
         Print("Open position #", tk, " kept: it filled before the engine's fill (bid chart); the engine's setup is still armed.");
      }
      else
      {
         exArm = -1; exSynced = gRestored && exSynced;
         Print("Open position #", tk, " kept: the engine is not in it (its setup ended, new inputs or another timeframe). It runs to its own stop loss ",
               DoubleToString(pSl, _Digits), " and take profit ", pTp > 0 ? DoubleToString(pTp, _Digits) : "(none)", ".");
      }
   }''')
rep('''      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseAll(); BookBrokerDeals(); }   // a force-close, weekend start or news start passed while the EA was off''',
    '''      if(gRestFlat && HasPosition(rTk, rVol, rOp)) { CloseAll("a force-close, weekend start or news start passed while the EA was off"); BookBrokerDeals(); }''')

# ---------------------------------------------------------------- the copy lock, other EAs, OnInit, OnDeinit
rep('''int OnInit()
{''', '''//--- one copy per symbol + magic number: two copies cancel and close each other's trades and share one restart memory. A temporary global
//--- variable (gone when MT5 closes) holds the chart of the copy that runs; a lock of a chart that no longer runs an EA is taken over
bool LockTake()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return true;
   gLockN = SvExtra("run");
   gLockV = (double)(ChartID() & 0xFFFFFFFFFFFF) + 1.0;  // 48 bits of the chart id (exact in a double), never 0
   if(!GlobalVariableCheck(gLockN)) GlobalVariableTemp(gLockN);
   if(GlobalVariableSetOnCondition(gLockN, gLockV, 0)) return true;
   double cur = GlobalVariableGet(gLockN);
   if(cur == gLockV) return true;                        // this chart (new inputs, another timeframe)
   for(long id = ChartFirst(); id >= 0; id = ChartNext(id))
      if(id != ChartID() && (double)(id & 0xFFFFFFFFFFFF) + 1.0 == cur && ChartGetString(id, CHART_EXPERT_NAME) != "") return false;   // that chart still runs it
   return GlobalVariableSetOnCondition(gLockN, gLockV, cur);   // that chart is gone: take over
}
void LockFree() { if(gLockN != "" && MQLInfoInteger(MQL_TESTER) == 0) GlobalVariableSetOnCondition(gLockN, 0, gLockV); }
//--- a note on the other EAs in this MetaTrader: one that manages every trade of the account can close this EA's trades (the log then names
//--- who closed each trade); an alert for an older copy of this EA on the same symbol (it has no lock and may use the same magic number)
void OtherEAs()
{
   if(MQLInfoInteger(MQL_TESTER) != 0) return;
   string lst = ""; bool twin = false;
   for(long id = ChartFirst(); id >= 0; id = ChartNext(id))
   {
      if(id == ChartID()) continue;
      string nm = ChartGetString(id, CHART_EXPERT_NAME);
      if(nm == "") continue;
      lst += (lst == "" ? "" : ", ") + nm + " (" + ChartSymbol(id) + " " + StringSubstr(EnumToString(ChartPeriod(id)), 7) + ")";
      if(ChartSymbol(id) != _Symbol || StringFind(nm, "AuctionRetest") != 0) continue;
      bool locked = false;                               // a v4.4+ copy holds a lock (its own magic number, else this start would have failed)
      for(int q = GlobalVariablesTotal() - 1; q >= 0 && !locked; q--)
      {
         string g = GlobalVariableName(q);
         if(StringFind(g, "ARX|") == 0 && StringFind(g, "|run") == StringLen(g) - 4 && GlobalVariableGet(g) == (double)(id & 0xFFFFFFFFFFFF) + 1.0) locked = true;
      }
      if(!locked) twin = true;
   }
   if(lst != "") Print("Other EAs running in this MetaTrader: ", lst, ". An EA that manages every trade of the account can close this EA's trades: the log names who closed each trade.");
   if(twin)
   {
      string m = "Another chart on " + _Symbol + " runs an older AuctionRetestEA. If it uses the same magic number (" + IntegerToString(InpMagic) +
                 "), the two copies cancel and close each other's trades: remove one, or give each its own magic number.";
      Print(m); Alert(m);
   }
}

int OnInit()
{''')
rep('''   gSvBase = SvBaseName(); gRestored = false;
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();
   gRestFlat = false; gBrokerPend = false;
   if(gPersist) gRestored = StateLoad();                 // a fresh start or new inputs: continue from the saved state (written at OnDeinit)''',
    '''   gSvBase = SvBaseName(); gRestored = false;
   if(!LockTake())
   {
      string m = "Another copy of this EA runs on " + _Symbol + " with magic number " + IntegerToString(InpMagic) + " (another chart). Two copies cancel and close " +
                 "each other's trades: remove one, or give each its own magic number.";
      Print(m); Alert(m);
      return INIT_FAILED;
   }
   TzPick(true);                                         // the broker's clock (Auto), before the warm-up uses it
   if(!InpRemember && MQLInfoInteger(MQL_TESTER) == 0) SvWipe();
   gRestFlat = false; gBrokerPend = false;
   // Start fresh once: forget the money-management state (kept by MT5 on new inputs and by the restart memory); done once while it is on
   string rsN = SvExtra("rsd");
   if(MQLInfoInteger(MQL_TESTER) == 0)
   {
      if(!InpMemFresh) GlobalVariableDel(rsN);
      else if(!GlobalVariableCheck(rsN))
      {
         SvWipe(); MemoryFresh(); GlobalVariableSet(rsN, 1);
         Print("Started fresh: the loss recovery, streaks and pauses start again from the base risk. Set 'Start fresh once' back to false.");
      }
   }
   if(gPersist) gRestored = StateLoad();                 // a fresh start or new inputs: continue from the saved state (written at OnDeinit)''')
rep('''   gStateTxt = StateText(false);
   UpdateTable();
   StateSave(true);                                      // restart memory: the state after this start
   gInitDone = true;
   return INIT_SUCCEEDED;''', '''   gStateTxt = StateText(false);
   UpdateTable();
   StateSave(true);                                      // restart memory: the state after this start
   OtherEAs();
   gInitDone = true;
   return INIT_SUCCEEDED;''')
rep('''   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   Comment("");''', '''   StateSave(true);                                      // restart memory: the latest state on disk (MT5 closing, the EA removed, new inputs)
   LockFree();
   Comment("");''')

# ---------------------------------------------------------------- OnTick catch-up: the engine's events for the EA's setup on missed bars
rep('''         ProcessBar(s); caught = true; if(gNewDay) gDayPendN++;''',
    '''         EngStep(s); caught = true; if(gNewDay) gDayPendN++;
         if(gOurFill) gMissFill = true;                                  // this trade's fill, stop move or exit on a missed bar: handled by OnNewBar
         if(gOurMove) gMissMove = true;
         if(gOurExit) { gMissExit = true; gMissWin = gOurWin; }''')

# ---------------------------------------------------------------- table and state text
rep('''   TblAdd("AUCTION RETEST", "EA v4.3", white, C'61,143,214');''', '''   TblAdd("AUCTION RETEST", "EA v4.4", white, C'61,143,214');''')
rep('''   TblAdd("RESTART MEMORY", gPersist ? (gRestored ? "on | continued from " + DateTxt(UserTime(gSvT), true) : "on") : InpRemember ? "off in the Strategy Tester" : "off", white, cell);
''', '''   TblAdd("RESTART MEMORY", gPersist ? (gRestored ? "on | continued from " + DateTxt(UserTime(gSvT), true) : "on") : InpRemember ? "off in the Strategy Tester" : "off", white, cell);
   TblAdd("LAST CLOSE", gLastClose, gLastCloseOut ? negC : white, cell);
   TblAdd("BROKER CLOCK", MQLInfoInteger(MQL_TESTER) != 0 ? GmtTxt(SrvGMT(TimeCurrent())) + " (Strategy Tester)" : TzTxt(), StringFind(TzTxt(), "CHECK") >= 0 ? negC : white, cell);
''')
rep('''   string ex = exState == 2 ? (exHg ? " (hedge pair open)" : " (in trade)") :''',
    '''   string ex = exState == 2 ? (exHg ? " (hedge pair open)" : exArm < 0 ? " (in trade, own stop and target)" : " (in trade)") :''')

open(P, 'w', encoding='utf8').write(s)
print(n_edits, 'edits; lines', s.count('\n'))
