#!/bin/bash
# build.sh: EA (read only) -> rec/ea_rt.cpp + the rec_* entry points -> rec/rec_harness
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; RUN="$HERE/../run"
EA="${1:-/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/build/safe/AuctionRetestEA.mq5}"
python3 -I "$RUN/create_rt.py" >/dev/null
cp "$EA" "$HERE/EA_copy.mq5"
python3 -I "$RUN/mq5rt.py" "$HERE/EA_copy.mq5" "$HERE/ea_rt.cpp" >/dev/null
cat >> "$HERE/ea_rt.cpp" <<'EOW'
#line 1 "<rec-wrapper>"
// what TakeSetup / the per-bar P&L update / BookClosed do with the money-management state (no broker calls)
extern "C" void rec_init() { LabReset(); }
extern "C" double rec_next(double exitR) { return NextRisk(exitR); }
extern "C" void rec_take() { crkRec = CrkRecNext(); }
extern "C" void rec_part(double np) { exPnl += np; totalNet += np; if(np != 0) carried = MathMax(0.0, carried - np); }
extern "C" void rec_close() { BookClosed(); }
extern "C" int rec_capstop() { return capStop ? 1 : 0; }
EOW
clang++ -std=c++17 -O1 -w -c "$HERE/ea_rt.cpp" -o "$HERE/ea_rt.o"
clang++ -std=c++17 -O1 -c "$HERE/rec_driver.cpp" -o "$HERE/rec_driver.o"
clang++ -O1 "$HERE/rec_driver.o" "$HERE/ea_rt.o" -o "$HERE/rec_harness"
