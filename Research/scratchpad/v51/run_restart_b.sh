#!/bin/bash
# v5.1 checks with a restart after every step: the monthly restart suite, the TP1-rule suite and the size section. Progress: v51/progress.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v51/progress.txt; cd $S/mq5check/rec
export REC_RESTART=1
echo "restart B start $(date +%T)" >> $P
python3 -I parity_month_v51.py 1 > parity_month_v51_restart.log 2>&1 &
python3 -I parity_tp1_v51.py > parity_tp1_v51x_restart.log 2>&1 &
wait
echo "restart v51 month $(tail -1 parity_month_v51_restart.log) $(date +%T)" >> $P
echo "restart v51 tp1 $(tail -1 parity_tp1_v51x_restart.log) $(date +%T)" >> $P
python3 -I parity_v51.py size 2 > parity_v51_size_restart.log 2>&1
echo "restart v51 size $(tail -1 parity_v51_size_restart.log) $(date +%T)" >> $P
echo "restart B done $(date +%T)" >> $P
