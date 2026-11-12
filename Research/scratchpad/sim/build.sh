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
open(dst, 'w').write(h)
c = open(cpp).read()
inc = '#include "%s"' % src
assert c.count(inc) == 1
c = c.replace(inc, '#include "%s"' % dst)
a = '\nvoid BookClosed()\n{'
assert c.count(a) == 1
c = c.replace(a, '\nvoid BookClosed_ea();\nvoid BookClosed() { sim_book(exPnl, exHg ? 1 : 0, exRiskAmt, exLots); BookClosed_ea(); }\nvoid BookClosed_ea()\n{')
c += '''
#line 1 "<sim-wrapper>"
extern "C" int sim_init() { return OnInit(); }
extern "C" void sim_ontick() { OnTick(); }
extern "C" void sim_deinit(int r) { OnDeinit(r); }
extern "C" int sim_exstate() { return exState; }
extern "C" double sim_crkl() { return crkL; }
extern "C" double sim_vwap() { return ArraySize(vwHist) > 0 ? vwHist[0] : 0.0; }
'''
open(cpp, 'w').write(c)
EOP
python3 -I "$REC/gen_fresh.py" "$HERE/EA_$NAME.mq5" >> "$HERE/ea_$NAME.cpp"
clang++ -std=c++17 -O1 -w -c "$HERE/ea_$NAME.cpp" -o "$HERE/ea_$NAME.o"
clang++ -std=c++17 -O1 -c "$HERE/sim_driver.cpp" -o "$HERE/sim_driver.o"
clang++ -O1 "$HERE/sim_driver.o" "$HERE/ea_$NAME.o" -o "$HERE/$NAME"
echo "built $HERE/$NAME"
