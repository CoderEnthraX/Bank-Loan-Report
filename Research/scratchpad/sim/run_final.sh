#!/bin/bash
# final simulator suite on the current EA: the 17 scenarios (v4.3 vs v4.4, results.txt) + 16 extra v4.4 runs + 4 runs with the restart
# memory off; summary in final_summary.txt (bookings checked with unbooked.py: gaps allowed only for trades closed while the EA was off
# with the memory off)
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; cd $S/sim
bash run_all.sh > /dev/null 2>&1 || { echo "run_all failed"; exit 1; }
A="m1_2026q3.csv 2026-08-03 2026-11-01 JIT=0.6"; B="m1_2025q4.csv 2025-09-15 2026-01-20 JIT=0.6"
declare -A X=([t1]="$A InpCrkT1=1" [t1r]="$A InpCrkT1=1 RESTART=1499 OFF=60" [t1tf]="$A InpCrkT1=1 TFSW=41 TFLEN=9" [t1d]="$A InpCrkT1=1 RESTART=397 OFF=150 DISC=1 EXT=6" [hg]="$A InpCrkPr=5 InpCrkPrN=1" [hgr]="$A InpCrkPr=5 InpCrkPrN=1 RESTART=1499 OFF=60" [hg2]="$A InpCrkPr=5 InpCrkPrN=1 InpCrkHgSl=3 InpCrkHgTp=3" [part]="$A InpExitAt=2 InpP1=50" [partr]="$A InpExitAt=2 InpP1=50 RESTART=1499 OFF=60 EXT=5" [mkt]="$A InpEntryMode=2" [mkttf]="$A InpEntryMode=2 TFSW=41 TFLEN=9 EXT=4" [mktr]="$A InpEntryMode=2 RESTART=997 OFF=0" [ybase]="$B" [ymix]="$B RESTART=3331 OFF=150 EXT=5 HOLD=35 TFSW=2777 TFLEN=50 REINIT=6007" [ymv]="$B InpExitAt=2 InpMv1On=1 InpMv1R=0 RESTART=797 OFF=150 DISC=1" [ymkt]="$B InpEntryMode=2 RESTART=397 OFF=150")
declare -A Z=([norem]="$A InpRemember=0 TFSW=37 TFLEN=11" [noremri]="$A InpRemember=0 REINIT=23" [noremrs]="$A InpRemember=0 RESTART=2999 OFF=100" [noremmix]="$A InpRemember=0 RESTART=4999 OFF=100 EXT=4 HOLD=30 TFSW=3001 TFLEN=40 REINIT=7001")
for k in "${!X[@]}"; do ./sim44 ${X[$k]} > x_${k}_44.log 2>&1 & done; wait
for k in "${!Z[@]}"; do ./sim44 ${Z[$k]} > z_${k}_44.log 2>&1 & done; wait
bash summarize.sh
echo "checks done"
