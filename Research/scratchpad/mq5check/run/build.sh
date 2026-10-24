#!/bin/bash
# build.sh [EA.mq5]  -> run/ea_harness  (executable harness of the EA engine)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
EA="${1:-/home/user/Bank-Loan-Report/MetaTrader5/AuctionRetestEA.mq5}"
python3 -I "$HERE/create_rt.py" >/dev/null
cp "$EA" "$HERE/EA_copy.mq5"   # the source is only ever READ; everything below works on the copy
python3 -I "$HERE/mq5rt.py" "$HERE/EA_copy.mq5" "$HERE/ea_rt.cpp" >/dev/null
clang++ -std=c++17 -O1 -w -c "$HERE/ea_rt.cpp" -o "$HERE/ea_rt.o"
clang++ -std=c++17 -O1 -c "$HERE/driver.cpp" -o "$HERE/driver.o"
clang++ -O1 "$HERE/driver.o" "$HERE/ea_rt.o" -o "$HERE/ea_harness"
