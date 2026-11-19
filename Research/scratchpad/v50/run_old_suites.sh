#!/bin/bash
# v5.0 regression: the v4.9 money suites on the v5.0 EA (harness already built from build/safe/AuctionRetestEA.mq5), normal and with a
# restart after every step; then the monthly restart and the position-size suites. Progress: v50/regress_progress.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v50/regress_progress.txt; R=$S/mq5check/rec
echo "start $(date +%T) EA md5 $(md5sum $S/build/safe/AuctionRetestEA.mq5 | cut -c1-12)" >> $P
cd $R
for mode in normal restart; do
  if [ $mode = restart ]; then export REC_RESTART=1; else unset REC_RESTART; fi
  python3 -I parity_rec.py > parity_rec_v50_$mode.log 2>&1 &
  python3 -I parity_tp1.py > parity_tp1_v50_$mode.log 2>&1 &
  REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_v50_$mode.log 2>&1 &
  wait
  echo "$mode rec $(tail -1 parity_rec_v50_$mode.log) $(date +%T)" >> $P
  echo "$mode tp1 $(grep '^p = 50' parity_tp1_v50_$mode.log) | $(tail -1 parity_tp1_v50_$mode.log) $(date +%T)" >> $P
  echo "$mode crkpr $(tail -1 parity_crkpr_v50_$mode.log) $(date +%T)" >> $P
done
unset REC_RESTART
python3 -I parity_month.py > parity_month_v50_normal.log 2>&1 &
REC_RESTART=1 python3 -I parity_month.py > parity_month_v50_restart.log 2>&1 &
python3 -I parity_size_ea.py > parity_size_v50_normal.log 2>&1 &
wait
echo "month normal $(tail -1 parity_month_v50_normal.log) $(date +%T)" >> $P
echo "month restart $(tail -1 parity_month_v50_restart.log) $(date +%T)" >> $P
echo "size normal $(tail -1 parity_size_v50_normal.log) $(date +%T)" >> $P
echo "done $(date +%T)" >> $P
