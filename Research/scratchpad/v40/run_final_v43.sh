#!/bin/bash
# EA v4.3 final verification on the final EA. Progress: v40/final_v43.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v40/final_v43.txt; R=/home/user/Bank-Loan-Report
echo "start $(date +%T)" > $P
cp $S/build/safe/AuctionRetestEA.mq5 $R/MetaTrader5/AuctionRetestEA.mq5
cd $S/mq5check/rec && bash build.sh > build_v43.log 2>&1 || { echo "BUILD FAILED" >> $P; exit 1; }
for d in hg month; do clang++ -std=c++17 -O1 -c ${d}_driver.cpp -o ${d}_driver.o && clang++ -O1 ${d}_driver.o ea_rt.o -o ${d}_harness; done
for mode in normal restart; do
  if [ $mode = restart ]; then export REC_RESTART=1; else unset REC_RESTART; fi
  python3 -I parity_rec.py > parity_rec_v43f_$mode.log 2>&1; echo "$mode rec $(tail -1 parity_rec_v43f_$mode.log) $(date +%T)" >> $P
  python3 -I parity_tp1.py > parity_tp1_v43f_$mode.log 2>&1; echo "$mode tp1 $(tail -1 parity_tp1_v43f_$mode.log) $(date +%T)" >> $P
  REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_v43f_$mode.log 2>&1; echo "$mode crkpr $(tail -1 parity_crkpr_v43f_$mode.log) $(date +%T)" >> $P
done
unset REC_RESTART
{ for a in "1 1" "0 1 -1" "0 1 0.6" "1 0"; do echo "== hedge forget/ok/lastLeg: $a"; ./hg_harness $a; done; echo "== month"; ./month_harness; } > $S/v40/hg_month_v43.log 2>&1
echo "scripted hedge + month tests: $(grep -c '' $S/v40/hg_month_v43.log) lines, see hg_month_v43.log $(date +%T)" >> $P
rm -f $S/v43neg/neg.log; bash $S/v43neg/run_neg.sh; echo "negative control: $(tr '\n' ' ' < $S/v43neg/neg.log | cut -c1-600) $(date +%T)" >> $P
cd $S/mq5check/run && bash build.sh > build_v43.log 2>&1 || { echo "RUN BUILD FAILED" >> $P; exit 1; }
python3 -I parity.py > parity_v43f.log 2>&1; echo "engine $(tail -1 parity_v43f.log) $(date +%T)" >> $P
PARITY_SHIFT_DAYS=49 python3 -I parity.py > parity_v43f_w49.log 2>&1; echo "engine +49 $(tail -1 parity_v43f_w49.log) $(date +%T)" >> $P
PARITY_SHIFT_DAYS=-189 python3 -I parity.py > parity_v43f_m189.log 2>&1; echo "engine -189 $(tail -1 parity_v43f_m189.log) $(date +%T)" >> $P
python3 -I parity.py > parity_v43f_final.log 2>&1; echo "engine (data files restored) $(tail -1 parity_v43f_final.log) $(date +%T)" >> $P
echo "done $(date +%T)" >> $P
