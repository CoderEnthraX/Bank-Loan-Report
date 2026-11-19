#!/bin/bash
# v5.1 checks, normal mode: the v4.9 Risk suites (regression), the v5.0 rec / pr sections without a stop distance (D = the R: v5.0 kept),
# the v5.1 Profit-with-costs suites (rec / pr / size / month / tp1), the old monthly and position-size suites. Progress: v51/progress.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; P=$S/v51/progress.txt; cd $S/mq5check/rec
unset REC_RESTART
echo "normal start $(date +%T) EA md5 $(md5sum $S/build/safe/AuctionRetestEA.mq5 | cut -c1-12) harness $(date -r rec_harness +%T)" >> $P
python3 -I parity_rec.py > parity_rec_v51_normal.log 2>&1 &
python3 -I parity_tp1.py > parity_tp1_v51_normal.log 2>&1 &
REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_v51_normal.log 2>&1 &
wait
echo "normal old rec $(tail -1 parity_rec_v51_normal.log) $(date +%T)" >> $P
echo "normal old tp1 $(grep '^p = 50' parity_tp1_v51_normal.log) | $(tail -1 parity_tp1_v51_normal.log) $(date +%T)" >> $P
echo "normal old crkpr $(tail -1 parity_crkpr_v51_normal.log) $(date +%T)" >> $P
python3 -I parity_v50.py rec 4 > parity_v50sec_rec_v51_normal.log 2>&1
echo "normal v50 rec (no stop distance: D = R) $(tail -1 parity_v50sec_rec_v51_normal.log) $(date +%T)" >> $P
for sec in rec pr size; do
  python3 -I parity_v51.py $sec 4 > parity_v51_${sec}_normal.log 2>&1
  echo "normal v51 $sec $(tail -1 parity_v51_${sec}_normal.log) $(date +%T)" >> $P
done
python3 -I parity_month_v51.py 2 > parity_month_v51_normal.log 2>&1 &
python3 -I parity_tp1_v51.py > parity_tp1_v51x_normal.log 2>&1 &
python3 -I parity_month.py > parity_month_old_v51_normal.log 2>&1 &
wait
python3 -I parity_size_ea.py > parity_size_old_v51_normal.log 2>&1
echo "normal v51 month $(tail -1 parity_month_v51_normal.log) $(date +%T)" >> $P
echo "normal v51 tp1 $(tail -1 parity_tp1_v51x_normal.log) $(date +%T)" >> $P
echo "normal old month $(tail -1 parity_month_old_v51_normal.log) $(date +%T)" >> $P
echo "normal old size $(tail -1 parity_size_old_v51_normal.log) $(date +%T)" >> $P
echo "normal done $(date +%T)" >> $P
