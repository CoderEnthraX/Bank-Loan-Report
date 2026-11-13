#!/bin/bash
# EA v4.5 regression (Crooks E - J in rec / tp1 / crkpr): money-management parity (normal + restart after every step), scripted hedge/month, engine parity x3. Progress: v40/final_v45.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v40/final_v45.txt; EA=$S/build/safe/AuctionRetestEA.mq5
TAG=${1:-v45}
echo "start $TAG $(date +%T) EA md5 $(md5sum $EA | cut -c1-12)" >> $P
cd $S/mq5check/rec && bash build.sh $EA > build_$TAG.log 2>&1 || { echo "BUILD FAILED" >> $P; exit 1; }
for d in hg month; do clang++ -std=c++17 -O1 -c ${d}_driver.cpp -o ${d}_driver.o && clang++ -O1 ${d}_driver.o ea_rt.o -o ${d}_harness; done
{ for a in "1 1" "0 1 -1" "0 1 0.6" "1 0"; do echo "== hedge forget/ok/lastLeg: $a"; ./hg_harness $a; done; echo "== month"; ./month_harness; } > $S/v40/hg_month_$TAG.log 2>&1
echo "scripted hedge + month vs v4.3: $(diff -q $S/v40/hg_month_v43.log $S/v40/hg_month_$TAG.log > /dev/null && echo IDENTICAL || echo DIFFERENT) $(date +%T)" >> $P
for mode in normal restart; do
  if [ $mode = restart ]; then export REC_RESTART=1; else unset REC_RESTART; fi
  python3 -I parity_rec.py > parity_rec_${TAG}_$mode.log 2>&1; echo "$mode rec $(tail -1 parity_rec_${TAG}_$mode.log) $(date +%T)" >> $P
  python3 -I parity_tp1.py > parity_tp1_${TAG}_$mode.log 2>&1; echo "$mode tp1 $(tail -1 parity_tp1_${TAG}_$mode.log) $(date +%T)" >> $P
  REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_${TAG}_$mode.log 2>&1; echo "$mode crkpr $(tail -1 parity_crkpr_${TAG}_$mode.log) $(date +%T)" >> $P
done
unset REC_RESTART
cd $S/mq5check/run && bash build.sh $EA > build_$TAG.log 2>&1 || { echo "RUN BUILD FAILED" >> $P; exit 1; }
python3 -I parity.py > parity_$TAG.log 2>&1; echo "engine $(tail -1 parity_$TAG.log) $(date +%T)" >> $P
PARITY_SHIFT_DAYS=49 python3 -I parity.py > parity_${TAG}_w49.log 2>&1; echo "engine +49 $(tail -1 parity_${TAG}_w49.log) $(date +%T)" >> $P
PARITY_SHIFT_DAYS=-189 python3 -I parity.py > parity_${TAG}_m189.log 2>&1; echo "engine -189 $(tail -1 parity_${TAG}_m189.log) $(date +%T)" >> $P
python3 -I parity.py > parity_${TAG}_final.log 2>&1; echo "engine (data files restored) $(tail -1 parity_${TAG}_final.log) $(date +%T)" >> $P
echo "done $TAG $(date +%T)" >> $P
