#!/bin/bash
# v4.0 parity suites, one after the other (4 cores); each log ends with its verdict. Progress: /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
cd /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/run
echo "start $(date +%T)" > /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
python3 -I parity.py > parity_v42.log 2>&1; echo "engine $(tail -1 parity_v42.log) $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
PARITY_SHIFT_DAYS=49 python3 -I parity.py > parity_v42_w49.log 2>&1; echo "engine +49 $(tail -1 parity_v42_w49.log) $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
PARITY_SHIFT_DAYS=-189 python3 -I parity.py > parity_v42_m189.log 2>&1; echo "engine -189 $(tail -1 parity_v42_m189.log) $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
cd /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/mq5check/rec
python3 -I parity_rec.py > parity_rec_v42.log 2>&1; echo "rec $(tail -1 parity_rec_v42.log) $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
python3 -I parity_tp1.py > parity_tp1_v42.log 2>&1; echo "tp1 $(tail -1 parity_tp1_v42.log) $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
REC_DAYS=1 python3 -I parity_crkpr.py > parity_crkpr_v42.log 2>&1; echo "crkpr $(tail -1 parity_crkpr_v42.log) $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
echo "done $(date +%T)" >> /tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/v40/parity_progress_v42.txt
