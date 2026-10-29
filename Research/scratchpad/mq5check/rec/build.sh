#!/bin/bash
# build.sh: EA (read only) -> rec/ea_rt.cpp + the rec_* entry points -> rec/rec_harness
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; RUN="$(cd "$HERE/../run" && pwd)"
EA="${1:-/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5}"
python3 -I "$RUN/create_rt.py" >/dev/null
cp "$EA" "$HERE/EA_copy.mq5"
python3 -I "$RUN/mq5rt.py" "$HERE/EA_copy.mq5" "$HERE/ea_rt.cpp" >/dev/null
# harness-only copy of the runtime header: tick value, bid and ask can be set (the shared run/ header returns 0 for them)
python3 -I - "$RUN/mql5rt.h" "$HERE/mql5rt_rec.h" "$HERE/ea_rt.cpp" <<'EOP'
import sys
src, dst, cpp = sys.argv[1:4]
h = open(src).read()
a = 'double SymbolInfoDouble(const string&, ENUM_SYMBOL_INFO_DOUBLE id)\n{\n   if(id == SYMBOL_POINT || id == SYMBOL_TRADE_TICK_SIZE) return rt_tick;'
assert h.count(a) == 1
h = h.replace(a, 'double rec_tv = 0, rec_ask = 0, rec_bid = 0;\n' + a + '\n   if(id == SYMBOL_TRADE_TICK_VALUE) return rec_tv;\n   if(id == SYMBOL_ASK) return rec_ask;\n   if(id == SYMBOL_BID) return rec_bid;')
h += '\nbool OrderCalcMargin(ENUM_ORDER_TYPE, const string&, double, double, double& margin) { margin = 0; return true; }   // harness stub\n'
open(dst, 'w').write(h)
c = open(cpp).read(); inc = '#include "%s"' % src
assert c.count(inc) == 1
open(cpp, 'w').write(c.replace(inc, '#include "%s"' % dst))
EOP
cat >> "$HERE/ea_rt.cpp" <<'EOW'
#line 1 "<rec-wrapper>"
// what TakeSetup / the per-bar P&L update / BookClosed do with the money-management state (no broker calls)
extern "C" void rec_init() { LabReset(); }
extern "C" double rec_next(double exitR) { return NextRisk(exitR); }
extern "C" void rec_take() { crkRec = CrkRecNext(); }
extern "C" void rec_part(double np) { exPnl += np; totalNet += np; if(np != 0) carried = MathMax(0.0, carried - np); }
extern "C" void rec_close() { BookClosed(); }
extern "C" int rec_capstop() { return capStop ? 1 : 0; }
// TP1 rule: the engine's stop distance and the spread of the next setup, then whether the EA uses the TP1 rule for it
extern "C" void rec_setup(double risk, double spread) { trRisk = risk; rec_tv = 1.0; rec_bid = 1000.0; rec_ask = 1000.0 + spread; }
extern "C" int rec_t1() { return CrkT1Dist() > 0 ? 1 : 0; }
EOW
clang++ -std=c++17 -O1 -w -c "$HERE/ea_rt.cpp" -o "$HERE/ea_rt.o"
clang++ -std=c++17 -O1 -c "$HERE/rec_driver.cpp" -o "$HERE/rec_driver.o"
clang++ -O1 "$HERE/rec_driver.o" "$HERE/ea_rt.o" -o "$HERE/rec_harness"
