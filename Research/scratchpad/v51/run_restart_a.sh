#!/bin/bash
# v5.1 checks with a restart (save, fresh load = OnInit, reload) after every step: the v5.1 rec and pr sections (the new saved value "xw",
# Oscar's goal with Profit). Progress: v51/progress.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v51/progress.txt; cd $S/mq5check/rec
export REC_RESTART=1
echo "restart A start $(date +%T)" >> $P
python3 -I parity_v51.py rec 2 > parity_v51_rec_restart.log 2>&1 &
python3 -I parity_v51.py pr 2 > parity_v51_pr_restart.log 2>&1 &
wait
echo "restart v51 rec $(tail -1 parity_v51_rec_restart.log) $(date +%T)" >> $P
echo "restart v51 pr $(tail -1 parity_v51_pr_restart.log) $(date +%T)" >> $P
echo "restart A done $(date +%T)" >> $P
