// ---- broker simulator for the EA (v4.4 tests): appended to a copy of mql5rt.h whose trade / symbol / account / time stubs were removed ----
// One symbol (gold: tick 0.01, 100 oz per lot -> 1.00 per 0.01 per lot), a hedging account, MT5 order rules (stops level), limit and stop orders,
// stop loss / take profit at the tick price, deals with entry, reason, magic number and position id. The driver feeds ticks (sim_tick) and
// calls the EA's handlers; everything the broker or the EA does is written to stdout as one line ("SIM ...", "EA ...", "BOOK ...").
extern "C" int printf(const char*, ...);
static datetime sim_now = 0; static double sim_bid = 0, sim_ask = 0; static int sim_gmtoff = 0, sim_connected = 1, sim_stops = 0;
static double sim_comm = 0;                                 // commission per lot per side (account currency)
static mql_long sim_magic = 0; static mqlstring sim_ret; static int sim_retcode = 0;
static mql_long sim_chart = 101; static mql_long sim_charts[8] = {101}; static int sim_nch = 1; static const char* sim_chname[8] = {"AuctionRetestEA"};
static ulong sim_nextTk = 1000;
static RtBar* sim_b5 = 0; static RtBar* sim_b1 = 0; static int sim_n5 = 0, sim_n1 = 0, sim_tf = 5;   // bars of both timeframes; the chart's timeframe
struct SimPos { ulong tk; mql_long id; int buy; double vol, open, sl, tp; mql_long magic; datetime t; mqlstring cm; int live; };
struct SimOrd { ulong tk; int type; double vol, px, sl, tp; mql_long magic; datetime t; mqlstring cm; int live; };
struct SimDeal { ulong tk; mql_long pid; int buy, entry, reason; double vol, px, profit, comm; mql_long magic; datetime t; mqlstring cm; };
static const int SIM_MAXP = 64, SIM_MAXO = 64, SIM_MAXD = 200000;
static SimPos* sim_p = 0; static int sim_np = 0; static SimOrd* sim_o = 0; static int sim_no = 0; static SimDeal* sim_d = 0; static int sim_nd = 0;
static int sim_selP = -1, sim_selO = -1;                    // selected position / order (index)
static void sim_alloc() { if(!sim_p) { sim_p = new SimPos[SIM_MAXP]; sim_o = new SimOrd[SIM_MAXO]; sim_d = new SimDeal[SIM_MAXD]; } }
static void sim_cs(char* b, int n, const mqlstring& s) { int k = 0; for(; k < s.n && k < n - 1; k++) b[k] = s.s[k]; b[k] = 0; }
static void sim_timestr(datetime t, char* b) { MqlDateTime d; TimeToStruct(t, d); snprintf(b, 32, "%04d.%02d.%02d %02d:%02d:%02d", d.year, d.mon, d.day, d.hour, d.min, d.sec); }

// ---- Print / Alert: the EA's log ----
static void sim_put(char*& p, char* e, const mqlstring& s) { for(int i = 0; i < s.n && p < e; i++) *p++ = s.s[i]; }
template<class T> static void sim_put(char*& p, char* e, const T& v) { mqlstring s(v); sim_put(p, e, s); }
static int sim_quiet = 0;
template<class... A> void Print(const A&... a)
{ if(sim_quiet) return; char buf[4200]; char* p = buf; char* e = buf + 4000; (sim_put(p, e, a), ...); *p = 0; char tb[32]; sim_timestr(sim_now, tb); printf("EA %s %s\n", tb, buf); }
template<class... A> void Alert(const A&... a)
{ char buf[4200]; char* p = buf; char* e = buf + 4000; (sim_put(p, e, a), ...); *p = 0; char tb[32]; sim_timestr(sim_now, tb); printf("ALERT %s %s\n", tb, buf); }

// ---- time, symbol, account, terminal, chart ----
datetime TimeCurrent() { return sim_now; }
datetime TimeGMT() { return sim_now - sim_gmtoff; }
double SymbolInfoDouble(const string&, ENUM_SYMBOL_INFO_DOUBLE id)
{
   if(id == SYMBOL_POINT || id == SYMBOL_TRADE_TICK_SIZE) return 0.01;
   if(id == SYMBOL_TRADE_TICK_VALUE) return 1.0;
   if(id == SYMBOL_BID) return sim_bid;
   if(id == SYMBOL_ASK) return sim_ask;
   if(id == SYMBOL_VOLUME_MIN || id == SYMBOL_VOLUME_STEP) return 0.01;
   if(id == SYMBOL_VOLUME_MAX) return 100.0;
   return 0;
}
mql_long SymbolInfoInteger(const string&, ENUM_SYMBOL_INFO_INTEGER id) { return id == SYMBOL_DIGITS ? 2 : id == SYMBOL_TRADE_STOPS_LEVEL ? sim_stops : 0; }
double AccountInfoDouble(ENUM_ACCOUNT_INFO_DOUBLE) { return 1e7; }
mql_long AccountInfoInteger(ENUM_ACCOUNT_INFO_INTEGER id) { return id == ACCOUNT_LOGIN ? 1001 : id == ACCOUNT_MARGIN_MODE ? (mql_long)ACCOUNT_MARGIN_MODE_RETAIL_HEDGING : 0; }
int MQLInfoInteger(ENUM_MQL_INFO_INTEGER) { return 0; }   // live: not the Strategy Tester
int TerminalInfoInteger(ENUM_TERMINAL_INFO_INTEGER id) { return id == TERMINAL_CONNECTED ? sim_connected : 0; }
mql_long ChartID() { return sim_chart; }
mql_long ChartFirst() { return sim_nch > 0 ? sim_charts[0] : -1; }
mql_long ChartNext(mql_long id) { for(int i = 0; i + 1 < sim_nch; i++) if(sim_charts[i] == id) return sim_charts[i + 1]; return -1; }
string ChartGetString(mql_long id, ENUM_CHART_PROPERTY_STRING p)
{ if(p != CHART_EXPERT_NAME) return string(); for(int i = 0; i < sim_nch; i++) if(sim_charts[i] == id && sim_chname[i]) return mqlstring(sim_chname[i]); return string(); }
string ChartSymbol(mql_long) { return _Symbol; }
ENUM_TIMEFRAMES ChartPeriod(mql_long) { return _Period; }
string EnumToString(int) { return mqlstring("PERIOD_M5"); }
bool OrderCalcMargin(ENUM_ORDER_TYPE, const string&, double, double, double& margin) { margin = 0; return true; }

// ---- deals ----
static void sim_deal(mql_long pid, int buy, int entry, int reason, double vol, double px, double profit, mql_long magic, const mqlstring& cm)
{
   if(sim_nd >= SIM_MAXD) return;
   SimDeal& d = sim_d[sim_nd++];
   d.tk = sim_nextTk++; d.pid = pid; d.buy = buy; d.entry = entry; d.reason = reason; d.vol = vol; d.px = px; d.profit = profit;
   d.comm = -sim_comm * vol; d.magic = magic; d.t = sim_now; d.cm = cm;
   char tb[32], c[64]; sim_timestr(sim_now, tb); sim_cs(c, 64, cm);
   printf("SIM DEAL %s tk=%llu pos=%lld %s %s vol=%.2f px=%.2f profit=%.2f comm=%.2f magic=%lld reason=%d cm=%s\n", tb, (unsigned long long)d.tk, (long long)pid,
          buy ? "buy" : "sell", entry == 0 ? "IN" : "OUT", vol, px, profit, d.comm, (long long)magic, reason, c);
}
static double sim_pnl(const SimPos& p, double px, double vol) { return (p.buy ? px - p.open : p.open - px) * vol * 100.0; }
static void sim_close(int i, double vol, int reason, mql_long magic)  // close (part of) position i at the current price
{
   SimPos& p = sim_p[i];
   double px = p.buy ? sim_bid : sim_ask;
   if(vol > p.vol - 1e-9) vol = p.vol;
   double pr = MathRound(sim_pnl(p, px, vol) * 100.0) / 100.0;
   sim_deal(p.id, !p.buy, 1, reason, vol, px, pr, magic, mqlstring(reason == DEAL_REASON_SL ? "[sl]" : reason == DEAL_REASON_TP ? "[tp]" : ""));
   p.vol = MathRound((p.vol - vol) * 100.0) / 100.0;
   if(p.vol < 0.005) { p.live = 0; char tb[32]; sim_timestr(sim_now, tb);
      printf("SIM CLOSE %s pos=%lld reason=%d px=%.2f open=%.2f sl=%.2f tp=%.2f\n", tb, (long long)p.id, reason, px, p.open, p.sl, p.tp); }
}
static int sim_open(int buy, double vol, double px, double sl, double tp, mql_long magic, const mqlstring& cm, mql_long id)
{
   int i = -1; for(int k = 0; k < sim_np; k++) if(!sim_p[k].live) { i = k; break; }
   if(i < 0) { if(sim_np >= SIM_MAXP) return -1; i = sim_np++; }
   SimPos& p = sim_p[i];
   p.tk = (ulong)id; p.id = id; p.buy = buy; p.vol = vol; p.open = px; p.sl = sl; p.tp = tp; p.magic = magic; p.t = sim_now; p.cm = cm; p.live = 1;
   sim_deal(id, buy, 0, DEAL_REASON_EXPERT, vol, px, 0, magic, cm);
   char tb[32]; sim_timestr(sim_now, tb);
   printf("SIM OPEN %s pos=%lld %s vol=%.2f px=%.2f sl=%.2f tp=%.2f bid=%.2f ask=%.2f\n", tb, (long long)id, buy ? "buy" : "sell", vol, px, sl, tp, sim_bid, sim_ask);
   return i;
}
// MT5 stop rules (stops level in points; freeze level 0): 0 = valid
static int sim_badStops(int buy, double ref, double sl, double tp)
{
   double lv = sim_stops * 0.01 - 1e-9;
   if(buy)  { if(sl > 0 && !(sl < ref - lv)) return 1; if(tp > 0 && !(tp > ref + lv)) return 1; }
   else     { if(sl > 0 && !(sl > ref + lv)) return 1; if(tp > 0 && !(tp < ref - lv)) return 1; }
   return 0;
}
static bool sim_fail(int code, const char* why) { sim_retcode = code; sim_ret = mqlstring(why); char tb[32]; sim_timestr(sim_now, tb); printf("SIM REJECT %s %s\n", tb, why); return false; }
static bool sim_ok() { sim_retcode = 10009; sim_ret = mqlstring("done"); return true; }

// ---- one tick: pending orders, then stop loss / take profit (the driver then calls OnTick) ----
extern "C" void sim_tick(long long t, double bid, double ask, int gmtoff)
{
   sim_alloc();
   sim_now = (datetime)t; sim_bid = bid; sim_ask = ask; sim_gmtoff = gmtoff;
   for(int k = 0; k < 2; k++)                               // M5 and M1 bars from the same ticks (a timeframe switch shows the other set)
   {
      RtBar* a = k == 0 ? sim_b5 : sim_b1; int& n = k == 0 ? sim_n5 : sim_n1; long long bt = t - t % (k == 0 ? 300 : 60);
      if(n == 0 || a[n - 1].t < bt) { RtBar& b = a[n++]; b.t = bt; b.o = b.h = b.l = b.c = bid; }
      else { RtBar& b = a[n - 1]; if(bid > b.h) b.h = bid; if(bid < b.l) b.l = bid; b.c = bid; }
   }
   rt_bars = sim_tf == 5 ? sim_b5 : sim_b1; rt_n = sim_tf == 5 ? sim_n5 : sim_n1;
   for(int i = 0; i < sim_no; i++)
   {
      SimOrd& o = sim_o[i]; if(!o.live) continue;
      double px = 0; bool hit = false;
      if(o.type == ORDER_TYPE_BUY_LIMIT  && ask <= o.px) { hit = true; px = ask < o.px ? ask : o.px; }
      if(o.type == ORDER_TYPE_SELL_LIMIT && bid >= o.px) { hit = true; px = bid > o.px ? bid : o.px; }
      if(o.type == ORDER_TYPE_BUY_STOP   && ask >= o.px) { hit = true; px = ask; }
      if(o.type == ORDER_TYPE_SELL_STOP  && bid <= o.px) { hit = true; px = bid; }
      if(!hit) continue;
      o.live = 0;
      sim_open(o.type == ORDER_TYPE_BUY_LIMIT || o.type == ORDER_TYPE_BUY_STOP, o.vol, px, o.sl, o.tp, o.magic, o.cm, (mql_long)o.tk);
   }
   for(int i = 0; i < sim_np; i++)
   {
      SimPos& p = sim_p[i]; if(!p.live) continue;
      if(p.buy)  { if(p.sl > 0 && bid <= p.sl) sim_close(i, p.vol, DEAL_REASON_SL, p.magic); else if(p.tp > 0 && bid >= p.tp) sim_close(i, p.vol, DEAL_REASON_TP, p.magic); }
      else       { if(p.sl > 0 && ask >= p.sl) sim_close(i, p.vol, DEAL_REASON_SL, p.magic); else if(p.tp > 0 && ask <= p.tp) sim_close(i, p.vol, DEAL_REASON_TP, p.magic); }
   }
}
extern "C" void sim_load_cap(int n) { sim_b5 = new RtBar[n > 0 ? n : 1]; sim_b1 = new RtBar[n > 0 ? n : 1]; rt_bars = sim_b5; rt_n = 0; rt_tick = 0.01; _Digits = 2; _Point = 0.01; }
extern "C" void sim_set_tf(int m) { sim_tf = m; _Period = m == 1 ? PERIOD_M1 : PERIOD_M5; rt_bars = m == 5 ? sim_b5 : sim_b1; rt_n = m == 5 ? sim_n5 : sim_n1; }
int PeriodSeconds(ENUM_TIMEFRAMES) { return sim_tf * 60; }
extern "C" int  sim_bars() { return rt_n; }
// a close outside the EA: by hand (reason CLIENT 0 / MOBILE 1 / WEB 2) or by another EA (reason EXPERT 3 with its magic number)
extern "C" int sim_ext_close(int reason, long long magic) { for(int i = 0; i < sim_np; i++) if(sim_p[i].live) { sim_close(i, sim_p[i].vol, reason, (mql_long)magic); return 1; } return 0; }
extern "C" int sim_live() { int n = 0; for(int i = 0; i < sim_np; i++) n += sim_p[i].live; return n; }
extern "C" void sim_conn(int c) { sim_connected = c; }
extern "C" void sim_cfg(int stops, double comm) { sim_stops = stops; sim_comm = comm; }
extern "C" void sim_set_chart(long long me, int n, const long long* ids, int withEa)   // the chart list (lock tests)
{ sim_chart = (mql_long)me; sim_nch = n; for(int i = 0; i < n && i < 8; i++) { sim_charts[i] = (mql_long)ids[i]; sim_chname[i] = withEa ? "AuctionRetestEA" : 0; } }
extern "C" void sim_set_quiet(int q) { sim_quiet = q; }
extern "C" void sim_gv_set(const char* n, double v) { GlobalVariableSet(mqlstring(n), v); }
extern "C" double sim_gv_get(const char* n) { return GlobalVariableGet(mqlstring(n)); }

// ---- positions ----
int PositionsTotal() { int n = 0; for(int i = 0; i < sim_np; i++) n += sim_p[i].live; return n; }
ulong PositionGetTicket(int index) { int k = 0; for(int i = 0; i < sim_np; i++) if(sim_p[i].live) { if(k == index) { sim_selP = i; return sim_p[i].tk; } k++; } sim_selP = -1; return 0; }
bool PositionSelectByTicket(ulong tk) { for(int i = 0; i < sim_np; i++) if(sim_p[i].live && sim_p[i].tk == tk) { sim_selP = i; return true; } return false; }
string PositionGetString(ENUM_POSITION_PROPERTY_STRING id)
{ if(sim_selP < 0) return string(); if(id == POSITION_SYMBOL) return _Symbol; if(id == POSITION_COMMENT) return sim_p[sim_selP].cm; return string(); }
mql_long PositionGetInteger(ENUM_POSITION_PROPERTY_INTEGER id)
{
   if(sim_selP < 0) return 0; SimPos& p = sim_p[sim_selP];
   if(id == POSITION_MAGIC) return p.magic; if(id == POSITION_TYPE) return p.buy ? (mql_long)POSITION_TYPE_BUY : (mql_long)POSITION_TYPE_SELL;
   if(id == POSITION_TIME) return (mql_long)p.t; if(id == POSITION_IDENTIFIER || id == POSITION_TICKET) return p.id; return 0;
}
double PositionGetDouble(ENUM_POSITION_PROPERTY_DOUBLE id)
{
   if(sim_selP < 0) return 0; SimPos& p = sim_p[sim_selP];
   if(id == POSITION_VOLUME) return p.vol; if(id == POSITION_PRICE_OPEN) return p.open; if(id == POSITION_SL) return p.sl; if(id == POSITION_TP) return p.tp;
   if(id == POSITION_PRICE_CURRENT) return p.buy ? sim_bid : sim_ask; if(id == POSITION_PROFIT) return sim_pnl(p, p.buy ? sim_bid : sim_ask, p.vol); return 0;
}
// ---- orders ----
int OrdersTotal() { int n = 0; for(int i = 0; i < sim_no; i++) n += sim_o[i].live; return n; }
ulong OrderGetTicket(int index) { int k = 0; for(int i = 0; i < sim_no; i++) if(sim_o[i].live) { if(k == index) { sim_selO = i; return sim_o[i].tk; } k++; } sim_selO = -1; return 0; }
string OrderGetString(ENUM_ORDER_PROPERTY_STRING id)
{ if(sim_selO < 0) return string(); if(id == ORDER_SYMBOL) return _Symbol; if(id == ORDER_COMMENT) return sim_o[sim_selO].cm; return string(); }
mql_long OrderGetInteger(ENUM_ORDER_PROPERTY_INTEGER id) { if(sim_selO < 0) return 0; if(id == ORDER_MAGIC) return sim_o[sim_selO].magic; if(id == ORDER_TYPE) return sim_o[sim_selO].type; return 0; }
double OrderGetDouble(ENUM_ORDER_PROPERTY_DOUBLE id)
{ if(sim_selO < 0) return 0; SimOrd& o = sim_o[sim_selO]; if(id == ORDER_PRICE_OPEN) return o.px; if(id == ORDER_SL) return o.sl; if(id == ORDER_TP) return o.tp; if(id == ORDER_VOLUME_CURRENT) return o.vol; return 0; }
// ---- deal history (everything is selected) ----
bool HistorySelect(datetime, datetime) { return true; }
int HistoryDealsTotal() { return sim_nd; }
ulong HistoryDealGetTicket(int i) { return i >= 0 && i < sim_nd ? sim_d[i].tk : 0; }
static int sim_di(ulong tk) { int i = (int)(tk - 1000); if(i >= 0 && i < sim_nd && sim_d[i].tk == tk) return i; for(int k = 0; k < sim_nd; k++) if(sim_d[k].tk == tk) return k; return -1; }
mql_long HistoryDealGetInteger(ulong tk, ENUM_DEAL_PROPERTY_INTEGER id)
{
   int i = sim_di(tk); if(i < 0) return 0; SimDeal& d = sim_d[i];
   if(id == DEAL_MAGIC) return d.magic; if(id == DEAL_ENTRY) return d.entry == 0 ? (mql_long)DEAL_ENTRY_IN : (mql_long)DEAL_ENTRY_OUT;
   if(id == DEAL_REASON) return d.reason; if(id == DEAL_POSITION_ID) return d.pid; if(id == DEAL_TIME) return (mql_long)d.t;
   if(id == DEAL_TYPE) return d.buy ? (mql_long)DEAL_TYPE_BUY : (mql_long)DEAL_TYPE_SELL; if(id == DEAL_TICKET) return (mql_long)d.tk; return 0;
}
double HistoryDealGetDouble(ulong tk, ENUM_DEAL_PROPERTY_DOUBLE id)
{
   int i = sim_di(tk); if(i < 0) return 0; SimDeal& d = sim_d[i];
   if(id == DEAL_PROFIT) return d.profit; if(id == DEAL_COMMISSION) return d.comm; if(id == DEAL_VOLUME) return d.vol; if(id == DEAL_PRICE) return d.px; return 0;
}
string HistoryDealGetString(ulong tk, ENUM_DEAL_PROPERTY_STRING id) { int i = sim_di(tk); if(i < 0) return string(); if(id == DEAL_SYMBOL) return _Symbol; if(id == DEAL_COMMENT) return sim_d[i].cm; return string(); }

// ---- CTrade ----
void CTrade::SetExpertMagicNumber(ulong m) { sim_magic = (mql_long)m; }
static bool sim_market(int buy, double v, double sl, double tp, const string& cm)
{
   double px = buy ? sim_ask : sim_bid, ref = buy ? sim_bid : sim_ask;
   if(v < 0.01 - 1e-9) return sim_fail(10014, "invalid volume");
   if(sim_badStops(buy, ref, sl, tp)) return sim_fail(10016, "invalid stops (market)");
   sim_open(buy, v, px, sl, tp, sim_magic, cm, (mql_long)sim_nextTk++);
   return sim_ok();
}
static bool sim_pending(int type, double v, double px, double sl, double tp, const string& cm)
{
   double lv = sim_stops * 0.01 - 1e-9;
   bool buy = type == ORDER_TYPE_BUY_LIMIT || type == ORDER_TYPE_BUY_STOP;
   if(type == ORDER_TYPE_BUY_LIMIT  && !(px < sim_ask - lv)) return sim_fail(10015, "invalid price (buy limit)");
   if(type == ORDER_TYPE_SELL_LIMIT && !(px > sim_bid + lv)) return sim_fail(10015, "invalid price (sell limit)");
   if(type == ORDER_TYPE_BUY_STOP   && !(px > sim_ask + lv)) return sim_fail(10015, "invalid price (buy stop)");
   if(type == ORDER_TYPE_SELL_STOP  && !(px < sim_bid - lv)) return sim_fail(10015, "invalid price (sell stop)");
   if(sim_badStops(buy, px, sl, tp)) return sim_fail(10016, "invalid stops (pending)");
   int i = -1; for(int k = 0; k < sim_no; k++) if(!sim_o[k].live) { i = k; break; }
   if(i < 0) { if(sim_no >= SIM_MAXO) return sim_fail(10024, "too many orders"); i = sim_no++; }
   SimOrd& o = sim_o[i]; o.tk = sim_nextTk++; o.type = type; o.vol = v; o.px = px; o.sl = sl; o.tp = tp; o.magic = sim_magic; o.t = sim_now; o.cm = cm; o.live = 1;
   char tb[32]; sim_timestr(sim_now, tb);
   printf("SIM ORDER %s tk=%llu type=%d vol=%.2f px=%.2f sl=%.2f tp=%.2f bid=%.2f ask=%.2f\n", tb, (unsigned long long)o.tk, type, v, px, sl, tp, sim_bid, sim_ask);
   return sim_ok();
}
bool CTrade::Buy(double v, const string&, double, double sl, double tp, const string& cm) { return sim_market(1, v, sl, tp, cm); }
bool CTrade::Sell(double v, const string&, double, double sl, double tp, const string& cm) { return sim_market(0, v, sl, tp, cm); }
bool CTrade::BuyLimit(double v, double px, const string&, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, const string& cm) { return sim_pending(ORDER_TYPE_BUY_LIMIT, v, px, sl, tp, cm); }
bool CTrade::SellLimit(double v, double px, const string&, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, const string& cm) { return sim_pending(ORDER_TYPE_SELL_LIMIT, v, px, sl, tp, cm); }
bool CTrade::BuyStop(double v, double px, const string&, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, const string& cm) { return sim_pending(ORDER_TYPE_BUY_STOP, v, px, sl, tp, cm); }
bool CTrade::SellStop(double v, double px, const string&, double sl, double tp, ENUM_ORDER_TYPE_TIME, datetime, const string& cm) { return sim_pending(ORDER_TYPE_SELL_STOP, v, px, sl, tp, cm); }
bool CTrade::OrderDelete(ulong tk)
{
   for(int i = 0; i < sim_no; i++) if(sim_o[i].live && sim_o[i].tk == tk) { sim_o[i].live = 0; char tb[32]; sim_timestr(sim_now, tb); printf("SIM CANCEL %s tk=%llu\n", tb, (unsigned long long)tk); return sim_ok(); }
   return sim_fail(10013, "no such order");
}
bool CTrade::PositionClose(ulong tk, ulong)
{ for(int i = 0; i < sim_np; i++) if(sim_p[i].live && sim_p[i].tk == tk) { sim_close(i, sim_p[i].vol, DEAL_REASON_EXPERT, sim_magic); return sim_ok(); } return sim_fail(10013, "no such position"); }
bool CTrade::PositionClosePartial(ulong tk, double v, ulong)
{ for(int i = 0; i < sim_np; i++) if(sim_p[i].live && sim_p[i].tk == tk) { sim_close(i, v, DEAL_REASON_EXPERT, sim_magic); return sim_ok(); } return sim_fail(10013, "no such position"); }
bool CTrade::PositionModify(ulong tk, double sl, double tp)
{
   for(int i = 0; i < sim_np; i++) if(sim_p[i].live && sim_p[i].tk == tk)
   {
      SimPos& p = sim_p[i];
      if(sim_badStops(p.buy, p.buy ? sim_bid : sim_ask, sl, tp)) return sim_fail(10016, "invalid stops (modify)");
      char tb[32]; sim_timestr(sim_now, tb);
      printf("SIM MODIFY %s pos=%lld sl=%.2f->%.2f tp=%.2f->%.2f\n", tb, (long long)p.id, p.sl, sl, p.tp, tp);
      p.sl = sl; p.tp = tp; return sim_ok();
   }
   return sim_fail(10013, "no such position");
}
string CTrade::ResultRetcodeDescription() const { return sim_ret; }
// ---- the EA's bookings (hooked into BookClosed) ----
static void sim_book(double pnl, int hg, double risk, double lots) { char tb[32]; sim_timestr(sim_now, tb); printf("BOOK %s pnl=%.2f hedge=%d risk=%.2f lots=%.2f\n", tb, pnl, hg, risk, lots); }
