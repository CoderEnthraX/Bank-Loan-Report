#!/bin/bash
# v4.3: money-management parity without and with a restart (save, fresh load, reload) at every step; progress in parity_progress_v43.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v40/parity_progress_v43.txt
cd $S/mq5check/rec
echo "start $(date +%T)" > $P
for mode in normal restart; do
  if [ $mode = restart ]; then export REC_RESTART=1; else unset REC_RESTART; fi
  python3 -I parity_rec.py > parity_rec_v43_$mode.log 2>&1; echo "$mode rec $(tail -1 parity_rec_v43_$mode.log) $(date +%T)" >> $P
  python3 -I parity_tp1.py > parity_tp1_v43_$mode.log 2>&1; echo "$mode tp1 $(tail -1 parity_tp1_v43_$mode.log) $(date +%T)" >> $P
  REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_v43_$mode.log 2>&1; echo "$mode crkpr $(tail -1 parity_crkpr_v43_$mode.log) $(date +%T)" >> $P
done
echo "done $(date +%T)" >> $P
