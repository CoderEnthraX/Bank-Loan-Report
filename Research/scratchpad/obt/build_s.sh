#!/bin/bash
# build.sh EA.mq5 NAME [v43]  -> sim/NAME (the EA on the broker simulator). v43: tag v4.3's closes in the log (it has no close reasons)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; RUN="$(cd "$HERE/../mq5check/run" && pwd)"; REC="$(cd "$HERE/../mq5check/rec" && pwd)"
EA="$1"; NAME="$2"; MODE="${3:-}"
python3 -I "$RUN/create_rt.py" >/dev/null
cp "$EA" "$HERE/EA_$NAME.mq5"
if [ "$MODE" = v43 ]; then python3 -I - "$HERE/EA_$NAME.mq5" <<'EOP'
import sys
p = sys.argv[1]; s = open(p, encoding='utf8').read()
for a, b in [('      CloseAll(); exState = 2;   // booked on the next bar', '      Print("SIMTAG close: engine wins (the engine is not in this trade)"); CloseAll(); exState = 2;   // booked on the next bar'),
             ('!(exT1 && (evWin || exT1Half))) CloseAll();', '!(exT1 && (evWin || exT1Half))) { Print("SIMTAG close: engine exit"); CloseAll(); }'),
             ('   if(flatNow && pos) CloseAll();', '   if(flatNow && pos) { Print("SIMTAG close: force-close / weekend / news"); CloseAll(); }'),
             ('{ CloseAll(); return; }', '{ Print("SIMTAG close: price past the stop / target"); CloseAll(); return; }')]:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, 'w', encoding='utf8').write(s)
EOP
fi
python3 -I "$RUN/mq5rt.py" "$HERE/EA_$NAME.mq5" "$HERE/ea_$NAME.cpp" >/dev/null
python3 -I - "$RUN/mql5rt.h" "$HERE/mql5rt_sim.h" "$HERE/sim_impl.h" "$HERE/ea_$NAME.cpp" <<'EOP'
import sys, re
src, dst, simh, cpp = sys.argv[1:5]
h = open(src).read()
DROP = ['template<class... A> void Print(const A&...) {}', 'template<class... A> void Alert(const A&...) {}',
        'datetime TimeCurrent() { return rt_n ? rt_bars[rt_n - 1].t : 0; }', 'datetime TimeGMT() { return TimeCurrent(); }',
        'double SymbolInfoDouble(const string&, ENUM_SYMBOL_INFO_DOUBLE id)\n{\n   if(id == SYMBOL_POINT || id == SYMBOL_TRADE_TICK_SIZE) return rt_tick;\n   return 0;\n}',
        'mql_long SymbolInfoInteger(const string&, ENUM_SYMBOL_INFO_INTEGER id) { return id == SYMBOL_DIGITS ? _Digits : 0; }',
        'double AccountInfoDouble(ENUM_ACCOUNT_INFO_DOUBLE) { return 0; }', 'mql_long AccountInfoInteger(ENUM_ACCOUNT_INFO_INTEGER) { return 0; }',
        'int MQLInfoInteger(ENUM_MQL_INFO_INTEGER) { return 0; }', 'int TerminalInfoInteger(ENUM_TERMINAL_INFO_INTEGER) { return 0; }',
        'mql_long ChartID() { return 0; }', 'int PositionsTotal() { return 0; }', 'int OrdersTotal() { return 0; }', 'ulong PositionGetTicket(int) { return 0; }',
        'ulong OrderGetTicket(int) { return 0; }', 'bool HistorySelect(datetime, datetime) { return true; }', 'int HistoryDealsTotal() { return 0; }',
        'void CTrade::SetExpertMagicNumber(ulong) {}',
        'bool CTrade::Buy(double, const string&, double, double, double, const string&) { return false; }',
        'bool CTrade::Sell(double, const string&, double, double, double, const string&) { return false; }',
        'bool CTrade::BuyLimit(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }',
        'bool CTrade::SellLimit(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }',
        'bool CTrade::BuyStop(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }',
        'bool CTrade::SellStop(double, double, const string&, double, double, ENUM_ORDER_TYPE_TIME, datetime, const string&) { return false; }',
        'bool CTrade::OrderDelete(ulong) { return false; }', 'bool CTrade::PositionClose(ulong, ulong) { return false; }',
        'bool CTrade::PositionModify(ulong, double, double) { return false; }', 'bool CTrade::PositionClosePartial(ulong, double, ulong) { return false; }',
        'string CTrade::ResultRetcodeDescription() const { return string(); }',
        'ulong HistoryDealGetTicket(int) { return 0; }', 'mql_long HistoryDealGetInteger(ulong, ENUM_DEAL_PROPERTY_INTEGER) { return 0; }',
        'double HistoryDealGetDouble(ulong, ENUM_DEAL_PROPERTY_DOUBLE) { return 0; }', 'string HistoryDealGetString(ulong, ENUM_DEAL_PROPERTY_STRING) { return string(); }',
        'mql_long ChartFirst() { return -1; }', 'mql_long ChartNext(mql_long) { return -1; }', 'string ChartGetString(mql_long, ENUM_CHART_PROPERTY_STRING) { return string(); }',
        'string ChartSymbol(mql_long) { return _Symbol; }', 'ENUM_TIMEFRAMES ChartPeriod(mql_long) { return _Period; }', 'string EnumToString(int) { return string(); }', 'int PeriodSeconds(ENUM_TIMEFRAMES p) { return 300; }', 'bool PositionSelectByTicket(ulong) { return false; }', 'mql_long PositionGetInteger(ENUM_POSITION_PROPERTY_INTEGER) { return 0; }', 'bool ObjectCreate(mql_long, const string&, ENUM_OBJECT, int, datetime, double, datetime, double, datetime, double) { return true; }', 'bool ObjectDelete(mql_long, const string&) { return true; }', 'int ObjectsDeleteAll(mql_long, const string&, int, int) { return 0; }', 'int ObjectFind(mql_long, const string&) { return -1; }', 'bool ObjectMove(mql_long, const string&, int, datetime, double) { return true; }']
for d in DROP:
    assert h.count(d) == 1, d
    h = h.replace(d, '')
h += '\n' + open(simh).read()
DECL = 'static RtBar* sim_b5 = 0; static RtBar* sim_b1 = 0; static int sim_n5 = 0, sim_n1 = 0, sim_tf = 5;'
assert h.count(DECL) == 1
h = h.replace(DECL, '')
SER0 = h.index('// ---- series (MT5 indexing: shift 0 = newest bar) ----')
SER1 = h.index('int iBarShift(const string&, ENUM_TIMEFRAMES, datetime t, bool exact)')
SER2 = h.index('\n}\n', SER1) + 3
NEW = DECL + r"""
// ---- series: PERIOD_M1 on the M5 chart reads the simulator's M1 bars (the Sniper's intrabars); volumes from OBVOL (M5) / OBVOL1 (M1) ----
extern "C" void* fopen(const char*, const char*); extern "C" int fscanf(void*, const char*, ...); extern "C" int fclose(void*); extern "C" char* getenv(const char*);
static void rt_sel(ENUM_TIMEFRAMES tf, RtBar*& b, int& n) { if(tf == PERIOD_M1 && sim_tf == 5) { b = sim_b1; n = sim_n1; } else { b = rt_bars; n = rt_n; } }
double iOpen(const string&, ENUM_TIMEFRAMES tf, int s) { RtBar* b; int n; rt_sel(tf, b, n); return s < 0 || s >= n ? 0 : b[n - 1 - s].o; }
double iHigh(const string&, ENUM_TIMEFRAMES tf, int s) { RtBar* b; int n; rt_sel(tf, b, n); return s < 0 || s >= n ? 0 : b[n - 1 - s].h; }
double iLow(const string&, ENUM_TIMEFRAMES tf, int s) { RtBar* b; int n; rt_sel(tf, b, n); return s < 0 || s >= n ? 0 : b[n - 1 - s].l; }
double iClose(const string&, ENUM_TIMEFRAMES tf, int s) { RtBar* b; int n; rt_sel(tf, b, n); return s < 0 || s >= n ? 0 : b[n - 1 - s].c; }
datetime iTime(const string&, ENUM_TIMEFRAMES tf, int s) { RtBar* b; int n; rt_sel(tf, b, n); return s < 0 || s >= n ? 0 : b[n - 1 - s].t; }
mql_long iVolume(const string&, ENUM_TIMEFRAMES, int) { return 0; }
static long long obv_t[2][300000]; static double obv_v[2][300000]; static int obv_n[2] = {-1, -1};
mql_long iTickVolume(const string&, ENUM_TIMEFRAMES tf, int s)
{
   RtBar* b; int n; rt_sel(tf, b, n); int w = (tf == PERIOD_M1 && sim_tf == 5) ? 1 : 0;
   if(obv_n[w] < 0) { obv_n[w] = 0; void* f = fopen(getenv(w ? "OBVOL1" : "OBVOL"), "r"); long long t; double v; while(f && obv_n[w] < 300000 && fscanf(f, "%lld %lf", &t, &v) == 2) { obv_t[w][obv_n[w]] = t; obv_v[w][obv_n[w]] = v; obv_n[w]++; } if(f) fclose(f); }
   if(s < 0 || s >= n) return 0;
   long long t = b[n - 1 - s].t; int lo = 0, hi = obv_n[w] - 1;
   while(lo <= hi) { int m = (lo + hi) / 2; if(obv_t[w][m] == t) return (mql_long)obv_v[w][m]; if(obv_t[w][m] < t) lo = m + 1; else hi = m - 1; }
   return 0;
}
mql_long iRealVolume(const string&, ENUM_TIMEFRAMES, int) { return 0; }
int Bars(const string&, ENUM_TIMEFRAMES tf) { RtBar* b; int n; rt_sel(tf, b, n); return n; }
int iBars(const string&, ENUM_TIMEFRAMES tf) { RtBar* b; int n; rt_sel(tf, b, n); return n; }
int iBarShift(const string&, ENUM_TIMEFRAMES tf, datetime t, bool exact)
{
   RtBar* b; int n; rt_sel(tf, b, n);
   int lo = 0, hi = n - 1, ans = -1;
   while(lo <= hi) { int mid = (lo + hi) / 2; if(b[mid].t <= t) { ans = mid; lo = mid + 1; } else hi = mid - 1; }
   if(ans < 0) return -1;
   if(exact && b[ans].t != t) return -1;
   return n - 1 - ans;
}
"""
h = h[:SER0] + NEW + h[SER2:]
open(dst, 'w').write(h)
c = open(cpp).read()
inc = '#include "%s"' % src
assert c.count(inc) == 1
c = c.replace(inc, '#include "%s"' % dst)
a = '\nvoid CLeg::BookClosed()\n{'
assert c.count(a) == 1
c = c.replace(a, a + '\n   sim_book(exPnl, exHg ? 1 : 0, exRiskAmt, exLots);')
c += '''
#line 1 "<sim-wrapper>"
extern "C" int sim_init() { return OnInit(); }
extern "C" void sim_ontick() { OnTick(); }
extern "C" void sim_deinit(int r) { OnDeinit(r); }
extern "C" int sim_exstate() { return gEA0.exState != 0 ? gEA0.exState : gEA1.exState; }
extern "C" double sim_crkl() { return gEA0.crkL; }
extern "C" double sim_vwap() { return ArraySize(gEA0.vwHist) > 0 ? gEA0.vwHist[0] : 0.0; }
'''
import re as _re
c = _re.sub(r'extern "C" void rt_reset\(\) \{[^\n]*', 'extern "C" void rt_reset() { gEA0.PresetApply(); gEA0.ResetEngine(); }', c)
c = _re.sub(r'extern "C" int rt_look\(\) \{[^\n]*', 'extern "C" int rt_look() { return 0; }', c)
c = _re.sub(r'extern "C" void rt_step\(int s, RtEv\* e\) \{[^\n]*', 'extern "C" void rt_step(int s, RtEv* e) {}', c)
c = _re.sub(r'extern "C" void rt_stats\(double\* o\) \{[^\n]*', 'extern "C" void rt_stats(double* o) {}', c)
open(cpp, 'w').write(c)
EOP
echo 'extern "C" void rec_fresh() {}' >> "$HERE/ea_$NAME.cpp"
clang++ -std=c++17 -O1 -w -c "$HERE/ea_$NAME.cpp" -o "$HERE/ea_$NAME.o"
clang++ -std=c++17 -O1 -c "$HERE/sim_driver.cpp" -o "$HERE/sim_driver.o"
clang++ -O1 "$HERE/sim_driver.o" "$HERE/ea_$NAME.o" -o "$HERE/$NAME"
echo "built $HERE/$NAME"
