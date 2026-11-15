
//--- notes ------------------------------------------------------------------------------------------------------------------------
void Note(Strat &s, string m, bool loud)
{
   if(gSim || (gNoEntry && !loud)) return;
   gDirty = true;
   string t = "FBG S" + IntegerToString(s.id) + (gNoEntry ? " (catch-up) " : " ") + m;
   Print(t);
   if(loud && !gNoEntry && InpAlerts) Alert(_Symbol + " " + t);
   if(loud && !gNoEntry && InpPush) SendNotification(_Symbol + " " + t);
}

//--- broker -----------------------------------------------------------------------------------------------------------------------
double MinDist() { return MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL), (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL)) * _Point; }
//--- lots for a number of units: to the nearest lot step, at least the minimum lot, at most the maximum
double LotsOf(double units)
{
   double st = LotStep(), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), vmax = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double v = MathRound(units / Contract() / st + 1e-9) * st;
   if(v < vmin) v = vmin;
   if(vmax > 0 && v > vmax) v = vmax;
   return NormalizeDouble(v, 8);
}
//--- the strategy's position at the broker (its magic number), newest first; 0 = none
ulong FindPos(Strat &s)
{
   ulong best = 0; datetime bt = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong tk = PositionGetTicket(i);
      if(tk == 0 || PositionGetString(POSITION_SYMBOL) != _Symbol || PositionGetInteger(POSITION_MAGIC) != InpMagic + s.id) continue;
      datetime t = (datetime)PositionGetInteger(POSITION_TIME);
      if(best == 0 || t > bt) { best = tk; bt = t; }
   }
   return best;
}
//--- a market buy for the strategy's new trade (the SL / TP are the rules' levels; one too close to the price waits, the EA watches it)
bool BrokerOpen(Strat &s)
{
   if(gSim) { s.ticket = 0; s.lots = s.units / Contract(); return true; }
   if(gNoEntry) return false;
   double v = LotsOf(s.units), st = LotStep(), vmin = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN), mg = 0;
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK), bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   while(v >= vmin && OrderCalcMargin(ORDER_TYPE_BUY, _Symbol, v, ask, mg) && mg > AccountInfoDouble(ACCOUNT_MARGIN_FREE)) v = NormalizeDouble(v - st, 8);
   if(v < vmin) { Print("FBG S", s.id, ": not enough free margin for the minimum lot: trade skipped."); return false; }
   double md = MinDist() + TickSize();
   double sl = NormP(s.SLp), tp = NormP(s.TPp);
   if(sl > bid - md) sl = 0;
   if(tp < bid + md) tp = 0;
   trade.SetExpertMagicNumber((ulong)(InpMagic + s.id));
   if(!trade.Buy(v, _Symbol, 0, sl, tp, "FBG S" + IntegerToString(s.id)))
   {
      Print("FBG S", s.id, ": buy failed: ", trade.ResultRetcodeDescription());
      return false;
   }
   uint rc = trade.ResultRetcode();
   if(rc != TRADE_RETCODE_DONE && rc != TRADE_RETCODE_DONE_PARTIAL && rc != TRADE_RETCODE_PLACED)
   {
      Print("FBG S", s.id, ": buy not done: ", trade.ResultRetcodeDescription());
      return false;
   }
   ulong tk = trade.ResultOrder();
   if(tk == 0 || !PositionSelectByTicket(tk)) tk = FindPos(s);
   if(tk == 0) { Print("FBG S", s.id, ": the position was not found after the buy."); return false; }
   s.ticket = tk; s.lots = v; gDirty = true;
   return true;
}
//--- the real result of a closed position (all its deals: profit, commission, swap, fee); false = not closed yet / not found
bool PosResult(ulong pos, double &usd, double &px, int &why)
{
   usd = 0; px = 0; why = -1;
   if(pos == 0 || !HistorySelectByPosition(pos)) return false;
   bool out = false;
   for(int i = 0; i < HistoryDealsTotal(); i++)
   {
      ulong d = HistoryDealGetTicket(i);
      if(d == 0) continue;
      usd += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP) + HistoryDealGetDouble(d, DEAL_FEE);
      long en = HistoryDealGetInteger(d, DEAL_ENTRY);
      if(en == DEAL_ENTRY_OUT || en == DEAL_ENTRY_OUT_BY) { out = true; px = HistoryDealGetDouble(d, DEAL_PRICE); why = (int)HistoryDealGetInteger(d, DEAL_REASON); }
   }
   return out;
}
//--- close the strategy's position (the rules exit) and read its real result (the model's result if its deals are not there yet).
//--- false: the broker refused the close (the trade stays open, retried on the next ticks)
bool BrokerClose(Strat &s, double model, double &usd)
{
   usd = model;
   if(s.ticket == 0) return true;
   if(PositionSelectByTicket(s.ticket))
   {
      trade.SetExpertMagicNumber((ulong)(InpMagic + s.id));
      if(!trade.PositionClose(s.ticket) && PositionSelectByTicket(s.ticket))
      {
         Print("FBG S", s.id, ": close failed (", trade.ResultRetcodeDescription(), "): retried on the next ticks.");
         return false;
      }
   }
   double px = 0; int why = -1;
   bool got = PosResult(s.ticket, usd, px, why);
   for(int tries = 0; !got && tries < 3; tries++) { Sleep(50); got = PosResult(s.ticket, usd, px, why); }
   if(!got) usd = model;
   return true;
}
//--- the broker closed a position itself (its SL / TP, a stop-out, by hand): book it as the rules' exit of that kind
void Reconcile()
{
   if(gSim) return;
   for(int i = 0; i < 12; i++)
   {
      if(S[i].pos && S[i].exitDue > 0) { CloseAt(S[i], S[i].exitPx, S[i].exitDue, TimeCurrent()); continue; }   // a refused close: again
      if(!S[i].pos || S[i].ticket == 0 || PositionSelectByTicket(S[i].ticket)) continue;
      double usd = 0, px = 0; int why = -1;
      if(!PosResult(S[i].ticket, usd, px, why)) continue;     // the deals are not in the history yet: next tick
      int rsn = why == DEAL_REASON_SL ? (S[i].trOn ? 5 : (S[i].beOn ? 3 : 2)) : why == DEAL_REASON_TP ? (S[i].svOn ? 4 : 1) : 8;
      CloseAt(S[i], px > 0 ? px : SymbolInfoDouble(_Symbol, SYMBOL_BID), rsn, TimeCurrent());
      gDirty = true;
   }
}
//--- the broker's SL / TP follow the rules' levels (BE, salvage, trailing); a level too close to the price stays with the EA.
//--- A change the broker refused is tried again after 10 seconds (not on every tick)
double   gSyS[12], gSyT[12]; datetime gSyAt[12];
void Sync()
{
   if(gSim) return;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID), ts = TickSize(), md = MinDist() + ts;
   for(int i = 0; i < 12; i++)
   {
      if(!S[i].pos || S[i].ticket == 0 || !PositionSelectByTicket(S[i].ticket)) continue;
      double cs = PositionGetDouble(POSITION_SL), ct = PositionGetDouble(POSITION_TP);
      double ws = NormP(S[i].SLp), wt = NormP(S[i].TPp);
      double ns = MathAbs(ws - cs) > ts * 0.5 && ws <= bid - md ? ws : cs;
      double nt = MathAbs(wt - ct) > ts * 0.5 && wt >= bid + md ? wt : ct;
      if(MathAbs(ns - cs) <= ts * 0.5 && MathAbs(nt - ct) <= ts * 0.5) continue;
      if(ns == gSyS[i] && nt == gSyT[i] && TimeCurrent() - gSyAt[i] < 10) continue;
      gSyS[i] = ns; gSyT[i] = nt; gSyAt[i] = TimeCurrent();
      trade.SetExpertMagicNumber((ulong)(InpMagic + S[i].id));
      if(!trade.PositionModify(S[i].ticket, ns, nt)) Print("FBG S", S[i].id, ": SL / TP change failed: ", trade.ResultRetcodeDescription());
   }
}

//--- the broker's clock -----------------------------------------------------------------------------------------------------------
int    gTzMode = SRV_NYCLOSE; double gTzFix = 2.0;
double RuleGMT(int md, datetime server)
{
   MqlDateTime d; TimeToStruct(server, d);
   if(md == SRV_EET)
   {
      int es = LastSunday(d.year, 3), ee = LastSunday(d.year, 10);
      bool sum = (d.mon > 3 && d.mon < 10) || (d.mon == 3 && d.day >= es) || (d.mon == 10 && d.day < ee);
      return sum ? 3.0 : 2.0;
   }
   int ds = NthSunday(d.year, 3, 2), de = NthSunday(d.year, 11, 1);
   bool dst = (d.mon > 3 && d.mon < 11) || (d.mon == 3 && d.day >= ds) || (d.mon == 11 && d.day < de);
   return dst ? 3.0 : 2.0;
}
double SrvGMT(datetime server)
{
   int md = InpServerTz == SRV_AUTO ? gTzMode : (int)InpServerTz;
   if(md == SRV_FIXED) return InpServerTz == SRV_AUTO ? gTzFix : InpServerGMT;
   return RuleGMT(md, server);
}
//--- Auto: the summer-time rule that gives the broker's offset now (US first, as most FX brokers; then EU), else that offset fixed
void TzPick()
{
   if(InpServerTz != SRV_AUTO || MQLInfoInteger(MQL_TESTER) != 0 || TerminalInfoInteger(TERMINAL_CONNECTED) == 0) return;
   datetime sv = TimeTradeServer(), g = TimeGMT();
   if(sv <= 0 || g <= 0) return;
   double d = MathRound((double)(sv - g) / 1800.0) / 2.0;
   if(MathAbs(d) > 14) return;
   if(RuleGMT(SRV_NYCLOSE, sv) == d) gTzMode = SRV_NYCLOSE;
   else if(RuleGMT(SRV_EET, sv) == d) gTzMode = SRV_EET;
   else { gTzMode = SRV_FIXED; gTzFix = d; }
}

//--- replay of the 1-minute history (warm-up at a fresh start, catch-up after a restart) ------------------------------------------------
//--- one strategy over the closed 1-minute bars [from, to): the candles of its timeframe that closed by each bar are pushed first
//--- (those closed by pushedTo were pushed before). No new trade opens (gNoEntry); an open trade follows the rules. Returns the bars replayed.
int ReplayStrat(Strat &s, datetime from, datetime to, datetime pushedTo, BarCtx &c, bool closePrev)
{
   MqlRates m1[], tf[];
   if(to <= from) return 0;
   int n = CopyRates(_Symbol, PERIOD_M1, (datetime)(from - 7 * 86400), (datetime)(to - 1), m1);   // with the bar before the replay (its close)
   if(n <= 0) return 0;
   int i0 = 0;
   while(i0 < n && m1[i0].time < from) i0++;
   if(i0 > 0)                                            // the bar before: its close is the previous close of the first bar replayed
   {
      c.T = m1[i0 - 1].time; c.last = m1[i0 - 1].close; Filters(c.T, c.okb, c.wk, c.dno);
   }
   bool skipEnd = !closePrev;                            // a fresh start: the bar before closed before the buy stop started
   int ps = PeriodSeconds(s.tf);
   int nt = CopyRates(_Symbol, s.tf, (datetime)(pushedTo - ps), (datetime)(to - 1), tf);
   int j = 0;
   while(j < nt && tf[j].time + ps <= pushedTo) j++;    // closed before the replay: already pushed
   bool ne = gNoEntry; gNoEntry = true;
   for(int i = i0; i < n; i++)
   {
      datetime T = m1[i].time;
      if(T >= to) break;
      if(!skipEnd) BarEnd(s, c);
      skipEnd = false;
      while(j < nt && tf[j].time + ps <= T) { PushTf(s, tf[j].high, tf[j].time, T, true); j++; }
      CtxBegin(c, T, m1[i].open);
      BarBegin(s, c, m1[i].open);
      double o = m1[i].open, h = m1[i].high, lo = m1[i].low, cl = m1[i].close;
      bool hf = (h - o) < (o - lo);
      double a = hf ? h : lo, b = hf ? lo : h;
      Move(s, c, a); c.last = a; Move(s, c, b); c.last = b; Move(s, c, cl); c.last = cl;
   }
   gNoEntry = ne;
   return n;
}
//--- live: the candle of the strategy's timeframe that holds the last minute processed (PushLive pushes the ones after it as they close)
void TfMark(Strat &s, datetime lastT)
{
   int sh = lastT > 0 ? iBarShift(_Symbol, s.tf, lastT, false) : 0;
   datetime t = sh >= 0 ? iTime(_Symbol, s.tf, sh) : 0;
   s.tfLast = t > 0 ? t : iTime(_Symbol, s.tf, 0);
}
//--- a fresh start: the candles of the strategy's timeframe up to its latest swing high's start, then the 1-minute bars since (the buy
//--- stop is used up if the price went through it)
void WarmStrat(Strat &s, datetime now, BarCtx &c)
{
   MqlRates tf[];
   int ps = PeriodSeconds(s.tf);
   int nt = CopyRates(_Symbol, s.tf, 1, 3000, tf);      // closed candles, oldest first
   if(nt <= s.l + s.r + 1) { Print("FBG S", s.id, ": not enough ", EnumToString(s.tf), " history yet (", nt, " candles)."); s.tfLast = iTime(_Symbol, s.tf, 0); return; }
   // the latest swing high: pushed in a scratch copy, then again up to its start
   datetime act = 0;
   {
      int w = s.l + s.r + 1;
      for(int k = nt - 1; k >= w - 1; k--)                // newest first: candle k is the last right candle of the candidate k - r
      {
         int p = k - s.r; double v = tf[p].high; bool ok = true;
         for(int i = 1; i <= s.l && ok; i++) if(tf[p - i].high >= v) ok = false;
         for(int q = 1; q <= s.r && ok; q++) if(tf[p + q].high >= v) ok = false;
         if(ok) { act = k + 1 < nt ? tf[k + 1].time : tf[k].time + (datetime)ps; break; }
      }
   }
   datetime from = MathMax(act, now - (datetime)(MathMax(1, InpWarmDays) * 86400));
   from = from - from % 60;
   int k0 = 0;
   for(; k0 < nt && tf[k0].time + ps <= from; k0++) PushTf(s, tf[k0].high, tf[k0].time, tf[k0].time + (datetime)ps, true);
   if(act > 0 && act < from && s.lvlOn)
   {
      double hm = 0;
      for(int k = 0; k < nt; k++) if(tf[k].time >= act && tf[k].time + ps <= from) hm = MathMax(hm, tf[k].high);
      if(hm >= s.E) s.lvlOn = false;
      Print("FBG S", s.id, ": its buy stop started ", TimeToString(act), ", before the 1-minute history read (", InpWarmDays, " days): ",
            s.lvlOn ? "still waiting (the price stayed below it)." : "used up (the price reached it).");
   }
   c.T = 0; c.last = 0; c.prevC = 0;
   ReplayStrat(s, from, now, from, c, false);
   TfMark(s, c.T);
}
//--- the trend timeframe's closed candles (EMA)
void TrendLoad()
{
   gTrSeed = false; gTrUp = false; gTrLast = 0;
   if(!InpTrnOn) return;
   MqlRates r[]; int n = CopyRates(_Symbol, InpTrnTf, 1, 5000, r);
   for(int i = 0; i < n; i++) PushTrend(r[i].close);
   gTrLast = iTime(_Symbol, InpTrnTf, 0);
}
void TrendLive()
{
   if(!InpTrnOn) return;
   datetime t0 = iTime(_Symbol, InpTrnTf, 0);
   if(t0 <= 0 || t0 <= gTrLast) return;
   if(gTrLast > 0)
   {
      MqlRates r[]; int n = CopyRates(_Symbol, InpTrnTf, gTrLast, (datetime)(t0 - 1), r);
      for(int i = 0; i < n; i++) if(r[i].time >= gTrLast && r[i].time < t0) PushTrend(r[i].close);
   }
   gTrLast = t0;
}
//--- live: the candles of the strategy's timeframe that closed since the last tick
void PushLive(Strat &s)
{
   datetime t0 = iTime(_Symbol, s.tf, 0);
   if(t0 <= 0 || t0 <= s.tfLast) return;
   if(s.tfLast > 0)
   {
      MqlRates r[]; int n = CopyRates(_Symbol, s.tf, s.tfLast, (datetime)(t0 - 1), r);
      for(int i = 0; i < n; i++) if(r[i].time >= s.tfLast && r[i].time < t0) PushTf(s, r[i].high, r[i].time, t0, true);
   }
   s.tfLast = t0;
   gDirty = true;
}

//--- restart memory -----------------------------------------------------------------------------------------------------------------
string   gSvBase = "";
bool     gIoSave = false;
string   gIoN[]; double gIoV[]; int gIoC = 0;
string   gSvN[]; double gSvV[]; int gSvC = 0;
datetime gSvT = 0;
bool     gRestored = false;
int SvVer() { return 1; }
void IoD(string n, double &x)
{
   if(gIoSave)
   {
      if(gIoC >= ArraySize(gIoN)) { ArrayResize(gIoN, gIoC + 64); ArrayResize(gIoV, gIoC + 64); }
      gIoN[gIoC] = n; gIoV[gIoC] = x; gIoC++;
   }
   else if(GlobalVariableCheck(gSvBase + n)) x = GlobalVariableGet(gSvBase + n);
}
void IoI(string n, int &x)      { double d = x; IoD(n, d); x = (int)MathRound(d); }
void IoB(string n, bool &x)     { double d = x ? 1.0 : 0.0; IoD(n, d); x = d != 0.0; }
void IoT(string n, datetime &x) { double d = (double)x; IoD(n, d); x = (datetime)(long)MathRound(d); }
void IoU(string n, ulong &x)    { double hi = (double)(x >> 32), lo = (double)(x & 0xFFFFFFFF); IoD(n + "h", hi); IoD(n + "l", lo); x = ((ulong)MathRound(hi) << 32) | (ulong)MathRound(lo); }
//--- what identifies a strategy's swing highs: a change forgets its buy stop
double Fp(Strat &s) { return (double)s.tf * 1e6 + s.r * 1e3 + s.l + s.off * 1e-3; }
void StratIO(Strat &s)
{
   string p = "s" + IntegerToString(s.id);
   double fp = Fp(s); IoD(p + "fp", fp);
   IoB(p + "lo", s.lvlOn); IoD(p + "lh", s.lvlH); IoD(p + "le", s.E); IoT(p + "lt", s.lvlT); IoT(p + "la", s.actT); IoB(p + "ar", s.armed);
   if(!gIoSave && MathAbs(fp - Fp(s)) > 1e-9) { s.lvlOn = false; s.lvlT = 0; }
   IoI(p + "xd", s.exitDue); IoD(p + "xp", s.exitPx);
   IoB(p + "ps", s.pos); IoD(p + "f", s.F); IoD(p + "sl", s.SLp); IoD(p + "tp", s.TPp); IoD(p + "be", s.BEl); IoD(p + "sv", s.SVl); IoD(p + "hi", s.hi);
   IoB(p + "bo", s.beOn); IoB(p + "so", s.svOn); IoB(p + "to", s.trOn); IoT(p + "et", s.eTime); IoB(p + "cn", s.cnt); IoU(p + "tk", s.ticket); IoD(p + "lv", s.lots);
   IoI(p + "dc", s.dCnt); IoI(p + "dp", s.dPrev); IoB(p + "st", s.stopped);
   int sw = s.stopWhy == "account blown" ? 2 : s.stopWhy != "" ? 1 : 0; IoI(p + "sw", sw);
   if(!gIoSave) s.stopWhy = sw == 2 ? "account blown" : sw == 1 ? "stopped by the hard cap" : "";
   IoD(p + "eq", s.eq); IoD(p + "pe", s.pkEq); IoD(p + "du", s.ddU); IoD(p + "dq", s.ddP); IoD(p + "nt", s.net); IoD(p + "pn", s.peakNet);
   IoD(p + "rp", s.recPool); IoD(p + "ca", s.carried); IoD(p + "op", s.oscP); IoD(p + "kl", s.crL); IoD(p + "rk", s.risk); IoD(p + "un", s.units); IoD(p + "br", s.bR);
   IoI(p + "rl", s.recLosses); IoI(p + "dn", s.dUnits); IoI(p + "pw", s.parWins); IoI(p + "rd", s.rdUnits); IoI(p + "ou", s.oscU);
   IoI(p + "kn", s.crN); IoI(p + "kp", s.crP); IoI(p + "kf", s.crF); IoI(p + "kb", s.crWW);
   IoB(p + "kw", s.crW); IoB(p + "ka", s.crWait); IoB(p + "kc", s.crNeedL); IoB(p + "kr", s.crRecT);
   IoI(p + "n", s.n); IoI(p + "nw", s.nW); IoI(p + "n1", s.nTP); IoI(p + "n2", s.nSL); IoI(p + "n3", s.nBE); IoI(p + "n4", s.nSV); IoI(p + "n5", s.nOth);
   IoI(p + "ss", s.st); IoI(p + "sm", s.mst); IoD(p + "gw", s.gw); IoD(p + "gl", s.gl); IoD(p + "cu", s.cum); IoD(p + "pk", s.pk); IoD(p + "dd", s.dd);
   int ln = ArraySize(s.lab); IoI(p + "ln", ln);
   if(!gIoSave) { if(ln < 1 || ln > 2000) ln = 3; ArrayResize(s.lab, ln); }
   for(int q = 0; q < ln; q++) { double x = gIoSave ? s.lab[q] : (q < 3 ? q + 1.0 : 1.0); IoD(p + "L" + IntegerToString(q), x); if(!gIoSave) s.lab[q] = x; }
   if(!gIoSave)
   {
      bool ok = ArraySize(s.lab) > 0;
      for(int q = 0; q < ArraySize(s.lab); q++) if(s.lab[q] <= 0) ok = false;
      if(!ok) { ArrayResize(s.lab, 3); s.lab[0] = 1.0; s.lab[1] = 2.0; s.lab[2] = 3.0; }
      if(s.crP < 1) s.crP = 1;
   }
}
void StateIO(bool save)
{
   gIoSave = save; gIoC = 0;
   int ver = SvVer(); IoI("ver", ver);
   datetime lt = gC.T, sv = TimeCurrent(); IoT("lt", lt); IoT("sv", sv);
   double acc = (double)AccountInfoInteger(ACCOUNT_LOGIN); IoD("acc", acc);
   if(!save) { gSvT = lt; }
   for(int i = 0; i < 12; i++) StratIO(S[i]);
}
void StateSave(bool force)
{
   if(!InpRemember || gSim || MQLInfoInteger(MQL_TESTER) != 0 || gC.T <= 0) return;
   StateIO(true);
   bool ch = force || gIoC != gSvC;
   for(int q = 0; q < gIoC && !ch; q++) if(gIoN[q] != gSvN[q] || (gIoV[q] != gSvV[q] && gIoN[q] != "sv")) ch = true;
   if(!ch) return;
   for(int q = 0; q < gIoC; q++) if(force || q >= gSvC || gIoN[q] != gSvN[q] || gIoV[q] != gSvV[q]) GlobalVariableSet(gSvBase + gIoN[q], gIoV[q]);
   for(int q = gIoC; q < gSvC; q++) GlobalVariableDel(gSvBase + gSvN[q]);
   if(ArraySize(gSvN) < gIoC) { ArrayResize(gSvN, gIoC); ArrayResize(gSvV, gIoC); }
   for(int q = 0; q < gIoC; q++) { gSvN[q] = gIoN[q]; gSvV[q] = gIoV[q]; }
   gSvC = gIoC;
   GlobalVariablesFlush();
}
//--- the saved state of this symbol, magic number and account (false: none, or another account)
bool StateLoad()
{
   if(!InpRemember || MQLInfoInteger(MQL_TESTER) != 0) return false;
   if(!GlobalVariableCheck(gSvBase + "ver") || (int)MathRound(GlobalVariableGet(gSvBase + "ver")) != SvVer()) return false;
   if(!GlobalVariableCheck(gSvBase + "acc") || (long)MathRound(GlobalVariableGet(gSvBase + "acc")) != AccountInfoInteger(ACCOUNT_LOGIN))
   {
      Print("Restart memory: saved for another account: starting fresh.");
      return false;
   }
   StateIO(false);
   return gSvT > 0;
}
//--- after a restart: the candles up to the last minute processed, then the minutes missed (caught up)
void Restore(datetime now)
{
   for(int i = 0; i < 12; i++)
   {
      int ps = PeriodSeconds(S[i].tf);
      MqlRates tf[]; int nt = CopyRates(_Symbol, S[i].tf, 1, 3000, tf);
      S[i].nC = 0; int kA = 0;
      for(int k = 0; k < nt && tf[k].time + ps <= gSvT; k++) { PushTf(S[i], tf[k].high, tf[k].time, tf[k].time + (datetime)ps, false); if(tf[k].time < S[i].actT) kA = S[i].nC; }
      S[i].kAct = kA;
   }
   BarCtx c;
   for(int i = 0; i < 12; i++)
   {
      c.T = 0; c.last = 0; c.prevC = 0; c.okb = false; c.wk = false; c.dno = 0;
      if(S[i].ok) ReplayStrat(S[i], gSvT + 60, now, gSvT, c, true);
      TfMark(S[i], c.T > 0 ? c.T : gSvT);
      if(c.T > 0) gC = c;
   }
}

//--- table and lines -----------------------------------------------------------------------------------------------------------------
color  gCol[12] = { C'41,98,255', C'0,188,212', C'76,175,80', C'255,152,0', C'156,39,176', C'233,30,99', C'0,150,136', C'205,220,57', C'121,85,72', C'96,125,139', C'255,82,82', C'255,235,59' };
string gRows[]; color gRowC[];
datetime gDrawT = 0;
string TfTxt(ENUM_TIMEFRAMES t) { return t == PERIOD_M1 ? "M1" : t == PERIOD_M5 ? "M5" : t == PERIOD_M15 ? "M15" : t == PERIOD_M30 ? "M30" : t == PERIOD_H1 ? "H1" : t == PERIOD_H4 ? "H4" : t == PERIOD_D1 ? "D1" : EnumToString(t); }
string RecTxt() { string e = EnumToString(InpRec); return StringSubstr(e, 4); }
string Usd(double v) { return (v < 0 ? "-" : "") + DoubleToString(MathAbs(v), 2); }
string NowTxt(Strat &s)
{
   if(!s.ok) return "off";
   if(s.stopped) return s.stopWhy;
   if(s.pos)
   {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      return "LONG " + DoubleToString(s.lots, 2) + " lot @ " + DoubleToString(s.F, _Digits) + " " + (bid >= s.F ? "+" : "") + DoubleToString((bid - s.F) / s.F * 100.0, 2) + "% | SL " +
             DoubleToString(s.SLp, _Digits) + (s.beOn ? " (BE)" : s.trOn ? " (trail)" : "") + " TP " + DoubleToString(s.TPp, _Digits) + (s.svOn ? " (salvage)" : "");
   }
   if(s.lvlOn)
   {
      double r = FNext(s, s.E);
      string nx = r > 0 ? " | next " + DoubleToString(LotsOf(r / ((s.E * s.sl / 100.0 + Costs()) * Vpu())), 2) + " lot, risk " + DoubleToString(r, 2) : r < 0 ? " | the hard cap would stop it" : "";
      return "buy stop " + DoubleToString(s.E, _Digits) + nx;
   }
   return "waiting for a swing high";
}
void Row(string t, color c) { int n = ArraySize(gRows); ArrayResize(gRows, n + 1); ArrayResize(gRowC, n + 1); gRows[n] = t; gRowC[n] = c; }
string Pad(string t, int w) { string r = t; while(StringLen(r) < w) r += " "; return r; }
void HLine(string nm, double p, color c, ENUM_LINE_STYLE st)
{
   if(p <= 0) { ObjectDelete(0, nm); return; }
   if(ObjectFind(0, nm) < 0) { ObjectCreate(0, nm, OBJ_HLINE, 0, 0, p); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false); ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true); }
   ObjectSetDouble(0, nm, OBJPROP_PRICE, p); ObjectSetInteger(0, nm, OBJPROP_COLOR, c); ObjectSetInteger(0, nm, OBJPROP_STYLE, st);
}
void Draw(bool force)
{
   if(gSim || (MQLInfoInteger(MQL_TESTER) != 0 && MQLInfoInteger(MQL_VISUAL_MODE) == 0)) return;
   if(!force && TimeLocal() - gDrawT < 2) return;
   gDrawT = TimeLocal();
   for(int i = 0; i < 12; i++)
   {
      string id = IntegerToString(i + 1);
      bool on = InpLines && S[i].ok;
      HLine("FBG_E" + id, on && S[i].lvlOn && !S[i].pos ? S[i].E : 0, gCol[i], STYLE_DOT);
      HLine("FBG_SL" + id, on && S[i].pos ? S[i].SLp : 0, C'242,54,69', STYLE_DASH);
      HLine("FBG_TP" + id, on && S[i].pos ? S[i].TPp : 0, C'76,175,80', STYLE_DASH);
   }
   ArrayResize(gRows, 0); ArrayResize(gRowC, 0);
   if(InpTable)
   {
      Row("FRACTAL BREAKOUT GRID EA v1.0 | " + _Symbol + " | magic " + IntegerToString(InpMagic) + " + N", C'41,163,224');
      string sz = InpSizeMode == PSZ_LOT ? DoubleToString(InpBaseLots, 2) + " lot" : InpSizeMode == PSZ_PCT ? DoubleToString(InpEqPct, 2) + "% of equity" : Usd(InpBaseRisk);
      Row("MONEY: " + RecTxt() + (LadFam() && InpLadder != LAD_OFF ? " + ladder " + StringSubstr(EnumToString(InpLadder), 4) : "") + " | base " + sz + " | start " + Usd(InpStartB) +
          " each" + (InpCapOn ? " | cap " + Usd(InpHardCap) : ""), C'209,212,220');
      Row(Pad("#", 3) + Pad("TF", 4) + Pad("R/L", 8) + Pad("Trades", 7) + Pad("Win%", 6) + Pad("Net $", 11) + Pad("TP/SL/BE/SV", 16) + "Now", C'209,212,220');
      int tn = 0, tw = 0; double tnet = 0;
      for(int i = 0; i < 12; i++)
      {
         string rl = IntegerToString(S[i].r) + "/" + IntegerToString(S[i].l);
         string wr = S[i].n > 0 ? DoubleToString(100.0 * S[i].nW / S[i].n, 0) : "-";
         string cs = IntegerToString(S[i].nTP) + "/" + IntegerToString(S[i].nSL) + "/" + IntegerToString(S[i].nBE) + "/" + IntegerToString(S[i].nSV);
         Row(Pad(IntegerToString(i + 1), 3) + Pad(TfTxt(S[i].tf), 4) + Pad(rl, 8) + Pad(IntegerToString(S[i].n), 7) + Pad(wr, 6) + Pad(Usd(S[i].cum), 11) + Pad(cs, 16) + NowTxt(S[i]),
             !S[i].ok ? C'120,123,134' : S[i].pos ? (SymbolInfoDouble(_Symbol, SYMBOL_BID) >= S[i].F ? C'76,175,80' : C'242,54,69') : gCol[i]);
         tn += S[i].n; tw += S[i].nW; tnet += S[i].cum;
      }
      Row("TOTAL: " + IntegerToString(tn) + " trades | win " + (tn > 0 ? DoubleToString(100.0 * tw / tn, 0) : "-") + "% | net " + Usd(tnet) + (gRestored ? " | continued after a restart" : ""), C'209,212,220');
   }
   int fs = MathMax(6, InpTableFont), n = ArraySize(gRows), wmax = 0, th = 0;
   uint tw2 = 0, tht = 0;
   TextSetFont("Courier New", -fs * 10);
   for(int i = 0; i < n; i++) { TextGetSize(gRows[i], tw2, tht); wmax = MathMax(wmax, (int)tw2); th = MathMax(th, (int)tht); }
   int rowH = th + 4, cw = (int)ChartGetInteger(0, CHART_WIDTH_IN_PIXELS), chh = (int)ChartGetInteger(0, CHART_HEIGHT_IN_PIXELS);
   bool right = InpTablePos == TBL_TOP_RIGHT || InpTablePos == TBL_BOTTOM_RIGHT, bottom = InpTablePos == TBL_BOTTOM_RIGHT || InpTablePos == TBL_BOTTOM_LEFT;
   int x0 = right ? MathMax(0, cw - wmax - 16) : 6, y0 = bottom ? MathMax(0, chh - n * rowH - 10) : 20;
   string bg = "FBG_TBbg";
   if(n > 0)
   {
      if(ObjectFind(0, bg) < 0) { ObjectCreate(0, bg, OBJ_RECTANGLE_LABEL, 0, 0, 0); ObjectSetInteger(0, bg, OBJPROP_SELECTABLE, false); ObjectSetInteger(0, bg, OBJPROP_HIDDEN, true); }
      ObjectSetInteger(0, bg, OBJPROP_CORNER, CORNER_LEFT_UPPER); ObjectSetInteger(0, bg, OBJPROP_XDISTANCE, x0 - 4); ObjectSetInteger(0, bg, OBJPROP_YDISTANCE, y0 - 3);
      ObjectSetInteger(0, bg, OBJPROP_XSIZE, wmax + 10); ObjectSetInteger(0, bg, OBJPROP_YSIZE, n * rowH + 6);
      ObjectSetInteger(0, bg, OBJPROP_BGCOLOR, C'19,23,34'); ObjectSetInteger(0, bg, OBJPROP_BORDER_TYPE, BORDER_FLAT); ObjectSetInteger(0, bg, OBJPROP_COLOR, C'67,70,81');
   }
   else ObjectDelete(0, bg);
   for(int i = 0; i < 40; i++)
   {
      string nm = "FBG_TB" + IntegerToString(i);
      if(i >= n) { ObjectDelete(0, nm); continue; }
      if(ObjectFind(0, nm) < 0) { ObjectCreate(0, nm, OBJ_LABEL, 0, 0, 0); ObjectSetInteger(0, nm, OBJPROP_SELECTABLE, false); ObjectSetInteger(0, nm, OBJPROP_HIDDEN, true); }
      ObjectSetInteger(0, nm, OBJPROP_CORNER, CORNER_LEFT_UPPER); ObjectSetInteger(0, nm, OBJPROP_ANCHOR, ANCHOR_LEFT_UPPER);
      ObjectSetInteger(0, nm, OBJPROP_XDISTANCE, x0); ObjectSetInteger(0, nm, OBJPROP_YDISTANCE, y0 + i * rowH);
      ObjectSetString(0, nm, OBJPROP_TEXT, gRows[i]); ObjectSetString(0, nm, OBJPROP_FONT, "Courier New");
      ObjectSetInteger(0, nm, OBJPROP_FONTSIZE, fs); ObjectSetInteger(0, nm, OBJPROP_COLOR, gRowC[i]);
   }
   ChartRedraw(0);
}

//--- MetaTrader events ---------------------------------------------------------------------------------------------------------------
bool Runs(int i, bool ticked) { return InpRun == RUN_ALL ? true : InpRun == RUN_TICKED ? ticked : InpRunOne == i; }
