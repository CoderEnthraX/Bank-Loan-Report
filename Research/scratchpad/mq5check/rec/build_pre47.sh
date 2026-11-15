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
h = h.replace(a, 'double rec_tv = 0, rec_ask = 0, rec_bid = 0, rec_vstep = 0.01, rec_vmin = 0.01, rec_vmax = 100.0, rec_eq = 0;\n' + a + '\n   if(id == SYMBOL_TRADE_TICK_VALUE) return rec_tv;\n   if(id == SYMBOL_ASK) return rec_ask;\n   if(id == SYMBOL_BID) return rec_bid;'
              '\n   if(id == SYMBOL_VOLUME_STEP) return rec_vstep;\n   if(id == SYMBOL_VOLUME_MIN) return rec_vmin;\n   if(id == SYMBOL_VOLUME_MAX) return rec_vmax;')
b = 'double AccountInfoDouble(ENUM_ACCOUNT_INFO_DOUBLE) { return 0; }'
assert h.count(b) == 1
h = h.replace(b, 'double AccountInfoDouble(ENUM_ACCOUNT_INFO_DOUBLE id) { return (id == ACCOUNT_EQUITY || id == ACCOUNT_MARGIN_FREE) ? rec_eq : 0; }   // 0 unless a lot test sets it')
h += '\nbool OrderCalcMargin(ENUM_ORDER_TYPE, const string&, double, double, double& margin) { margin = 0; return true; }   // harness stub\n'
open(dst, 'w').write(h)
c = open(cpp).read(); inc = '#include "%s"' % src
assert c.count(inc) == 1
open(cpp, 'w').write(c.replace(inc, '#include "%s"' % dst))
EOP
cat >> "$HERE/ea_rt.cpp" <<'EOW'
#line 1 "<rec-wrapper>"
// what TakeSetup / the per-bar P&L update / BookClosed do with the money-management state (no broker calls)
extern "C" void rec_init() { LabReset(); gCrkPrPrev = (int)InpCrkPr; }   // as after the first OnInit
extern "C" double rec_next(double exitR) { return NextRisk(exitR); }
// v4.5: the $ risk with the Crooks E / I small-lot risk of this trade and the equity (Crooks H); T1 mode: the EA's own MinLotRisk() of the set stop
extern "C" double rec_next_m(double exitR, double minRisk, double eq) { rec_eq = eq; return NextRisk(exitR, true, minRisk); }
extern "C" double rec_next_t1(double exitR, double eq) { rec_eq = eq; return NextRisk(exitR, true, (InpRec == REC_CRE || InpRec == REC_CRI || LadOn()) ? MinLotRisk(trRisk) : 0); }
extern "C" void rec_take() { crkRec = CrkRecNext(); }
extern "C" void rec_part(double np) { exPnl += np; totalNet += np; if(np != 0) carried = MathMax(0.0, carried - np); }
extern "C" void rec_close() { BookClosed(); }
extern "C" int rec_capstop() { return capStop ? 1 : 0; }
// TP1 rule: the engine's stop distance and the spread of the next setup, then whether the EA uses the TP1 rule for it
extern "C" void rec_setup(double risk, double spread) { trRisk = risk; rec_tv = 1.0; rec_bid = 1000.0; rec_ask = 1000.0 + spread; }
extern "C" int rec_t1() { return CrkT1Dist() > 0 ? 1 : 0; }
// Crooks C skip rule: a new day (counted or not) while trading is paused, and whether the next signal is skipped by the pause
extern "C" void rec_day(int counted) { CrkDayCount(counted != 0); }
extern "C" int rec_paused() { return CrkPause() ? 1 : 0; }
// v4.1 hedge rule: hedging account on/off, close the pair (lastOut = profit of the trade that closed last), state getters
extern "C" void rec_hgok(int on) { gHedgeOk = on != 0; }
extern "C" void rec_hgclose(double lastOut) { exHg = true; gLastOutProfit = lastOut; BookClosed(); }
extern "C" int rec_hgnow() { return CrkHedgeNow() ? 1 : 0; }
extern "C" double rec_owed() { return crkL; }
// v4.2 monthly profit lock: a month tick (your time zone), closed P&L, the checks, the restart once flat
extern "C" void rec_mtick(long long t) { MonthTick((datetime)t); }
extern "C" void rec_mpnl(double p) { monPnl += p; }
extern "C" int rec_mcheck() { MonthCheck(); return monStop ? 1 : 0; }
extern "C" int rec_mrestart() { if(monRestPend && exState == 0) { monRestPend = false; RecoveryRestart(); return 1; } return 0; }
extern "C" double rec_mpeak() { return monPeak; }
// lot sizing test: the EA's own LotsFor() with a set lot step / minimum / maximum, equity, tick value and spread
extern "C" double rec_lots(double risk, double sd, double entry, int isL, double ld, double tv, double spread, double vstep, double vmin, double eq)
{ rec_tv = tv; rec_bid = entry; rec_ask = entry + spread; rec_vstep = vstep; rec_vmin = vmin; rec_vmax = 100.0; rec_eq = eq; return LotsFor(risk, sd, entry, isL != 0, ld); }
// v4.3 restart memory: save, a fresh program load (every global back to its initial value), then what OnInit does with the saved state
extern "C" void rec_fresh();
extern "C" void rec_restart()
{
   bool hgOk = gHedgeOk;                                  // from the account in OnInit, not saved
   gPersist = true; gSvBase = "T|"; if(gLastDone <= 0) gLastDone = 1;   // as if a bar was processed (the harness has no bars)
   StateSave(true);
   rec_fresh();
   gPersist = true; gSvBase = "T|"; gHedgeOk = hgOk;
   if(ArraySize(labSeq) == 0) LabReset();
   if(!StateLoad()) Print("restart memory: nothing saved");
   if(gCrkPrPrev != (int)InpCrkPr || !CrkCFam()) { crkF = 0; crkWait = false; crkWW = 0; crkNeedL = false; crkSkip = false; crkSkipLeft = 0; crkHg = false; }
   gCrkPrPrev = (int)InpCrkPr;
}
EOW
python3 -I "$HERE/gen_fresh.py" "$HERE/EA_copy.mq5" >> "$HERE/ea_rt.cpp"
clang++ -std=c++17 -O1 -w -c "$HERE/ea_rt.cpp" -o "$HERE/ea_rt.o"
clang++ -std=c++17 -O1 -c "$HERE/rec_driver.cpp" -o "$HERE/rec_driver.o"
clang++ -O1 "$HERE/rec_driver.o" "$HERE/ea_rt.o" -o "$HERE/rec_harness"
clang++ -std=c++17 -O1 -c "$HERE/lots_driver.cpp" -o "$HERE/lots_driver.o"
clang++ -O1 "$HERE/lots_driver.o" "$HERE/ea_rt.o" -o "$HERE/lots_harness"
