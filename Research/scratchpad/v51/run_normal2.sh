#!/bin/bash
# v5.1 checks, normal mode, part 2 (the first run was stopped after rec / pr / size): the tie-aware v5.1 suites, then the monthly, TP1,
# old monthly and old position-size suites. Progress: v51/progress.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v51/progress.txt; cd $S/mq5check/rec
unset REC_RESTART
echo "normal part 2 start $(date +%T) (tie-aware v5.1 suites)" >> $P
for sec in rec pr size; do
  python3 -I parity_v51.py $sec 4 > parity_v51_${sec}_normal.log 2>&1
  echo "normal v51 $sec $(tail -1 parity_v51_${sec}_normal.log) $(date +%T)" >> $P
done
python3 -I parity_month_v51.py 2 > parity_month_v51_normal.log 2>&1 &
python3 -I parity_tp1_v51.py > parity_tp1_v51x_normal.log 2>&1 &
python3 -I parity_month.py > parity_month_old_v51_normal.log 2>&1 &
wait
echo "normal v51 month $(tail -1 parity_month_v51_normal.log) $(date +%T)" >> $P
echo "normal v51 tp1 $(tail -1 parity_tp1_v51x_normal.log) $(date +%T)" >> $P
echo "normal old month $(tail -1 parity_month_old_v51_normal.log) $(date +%T)" >> $P
python3 -I parity_size_ea.py > parity_size_old_v51_normal.log 2>&1
echo "normal old size $(tail -1 parity_size_old_v51_normal.log) $(date +%T)" >> $P
echo "normal part 2 done $(date +%T)" >> $P
