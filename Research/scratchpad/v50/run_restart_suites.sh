#!/bin/bash
# v5.0: every money suite with a restart (save, fresh load = OnInit's PresetApply, reload) after every step, plus the v4.9 monthly and
# position-size suites (normal). Harness rebuilt with rec_restart = OnInit order (build_v50b.log). Progress: v50/restart_progress.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v50/restart_progress.txt; cd $S/mq5check/rec
echo "start $(date +%T) EA md5 $(md5sum $S/build/safe/AuctionRetestEA.mq5 | cut -c1-12)" >> $P
export REC_RESTART=1
python3 -I parity_rec.py > parity_rec_v50_restart.log 2>&1 &
python3 -I parity_tp1.py > parity_tp1_v50_restart.log 2>&1 &
REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_v50_restart.log 2>&1 &
wait
echo "restart rec $(tail -1 parity_rec_v50_restart.log) $(date +%T)" >> $P
echo "restart tp1 $(grep '^p = 50' parity_tp1_v50_restart.log) | $(tail -1 parity_tp1_v50_restart.log) $(date +%T)" >> $P
echo "restart crkpr $(tail -1 parity_crkpr_v50_restart.log) $(date +%T)" >> $P
python3 -I parity_v50.py rec 2 > parity_v50_rec_restart.log 2>&1 &
python3 -I parity_v50.py pr 2 > parity_v50_pr_restart.log 2>&1 &
wait
echo "restart v50 rec $(tail -1 parity_v50_rec_restart.log) $(date +%T)" >> $P
echo "restart v50 pr $(tail -1 parity_v50_pr_restart.log) $(date +%T)" >> $P
python3 -I parity_month_v50.py 2 > parity_month_v50_restart.log 2>&1 &
python3 -I parity_tp1_v50.py > parity_tp1_v50_restart.log 2>&1 &
python3 -I parity_month.py > parity_month_v50_old_restart.log 2>&1 &
wait
echo "restart v50 month $(tail -1 parity_month_v50_restart.log) $(date +%T)" >> $P
echo "restart v50 tp1 $(tail -1 parity_tp1_v50_restart.log) $(date +%T)" >> $P
echo "restart old month $(tail -1 parity_month_v50_old_restart.log) $(date +%T)" >> $P
unset REC_RESTART
python3 -I parity_month.py > parity_month_v50_old_normal.log 2>&1 &
python3 -I parity_size_ea.py > parity_size_v50_old_normal.log 2>&1 &
wait
echo "normal old month $(tail -1 parity_month_v50_old_normal.log) $(date +%T)" >> $P
echo "normal old size $(tail -1 parity_size_v50_old_normal.log) $(date +%T)" >> $P
echo "done $(date +%T)" >> $P
