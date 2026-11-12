#!/bin/bash
# final simulator suite on the current EA: the 17 scenarios (v4.3 vs v4.4, results.txt) + 16 extra v4.4 runs; summary in final_summary.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; cd $S/sim
bash run_all.sh > /dev/null 2>&1 || { echo "run_all failed"; exit 1; }
A="m1_2026q3.csv 2026-08-03 2026-11-01 JIT=0.6"; B="m1_2025q4.csv 2025-09-15 2026-01-20 JIT=0.6"
declare -A X=([t1]="$A InpCrkT1=1" [t1r]="$A InpCrkT1=1 RESTART=1499 OFF=60" [t1tf]="$A InpCrkT1=1 TFSW=41 TFLEN=9" [t1d]="$A InpCrkT1=1 RESTART=397 OFF=150 DISC=1 EXT=6" [hg]="$A InpCrkPr=5 InpCrkPrN=1" [hgr]="$A InpCrkPr=5 InpCrkPrN=1 RESTART=1499 OFF=60" [hg2]="$A InpCrkPr=5 InpCrkPrN=1 InpCrkHgSl=3 InpCrkHgTp=3" [part]="$A InpExitAt=2 InpP1=50" [partr]="$A InpExitAt=2 InpP1=50 RESTART=1499 OFF=60 EXT=5" [mkt]="$A InpEntryMode=2" [mkttf]="$A InpEntryMode=2 TFSW=41 TFLEN=9 EXT=4" [mktr]="$A InpEntryMode=2 RESTART=997 OFF=0" [ybase]="$B" [ymix]="$B RESTART=3331 OFF=150 EXT=5 HOLD=35 TFSW=2777 TFLEN=50 REINIT=6007" [ymv]="$B InpExitAt=2 InpMv1On=1 InpMv1R=0 RESTART=797 OFF=150 DISC=1" [ymkt]="$B InpEntryMode=2 RESTART=397 OFF=150")
for k in "${!X[@]}"; do ./sim44 ${X[$k]} > x_${k}_44.log 2>&1 & done; wait
for f in sc_*_44.log x_*_44.log; do r=$(python3 -I analyze.py $f); echo "$f | noTP $(echo "$r" | grep -o 'broker: [0-9]*' | grep -o '[0-9]*$') | dup $(echo "$r" | grep -o 'before): [0-9]*' | grep -o '[0-9]*$') | stale $(echo "$r" | grep -o 'restart: [0-9]*' | grep -o '[0-9]*$') | bookings $(echo "$r" | grep -o 'P&L: [0-9]* of [0-9]*') | rejects $(grep -c '^SIM REJECT' $f) | initfail $(grep -c 'INIT FAILED' $f) | EA closes: $(echo "$r" | grep 'closed by EA' | sed 's/  */ /g;s/closed by EA: //;s/ (avg.*//;s/ trades, P&L.*//' | tr '\n' ';') | $(grep -h '^VWLINE' $f | sed 's/ (created [0-9]*, deleted [0-9]*)//;s/ | first [^|]*| last [^|]*|/ |/')"; done > final_summary.txt
echo "runs: $(wc -l < final_summary.txt), trades: $(cat sc_*_44.log x_*_44.log | grep -c '^SIM OPEN')"
awk -F'|' '{ if ($2 !~ /noTP 0 / || $3 !~ /dup 0 / || $4 !~ /stale 0 / || $6 !~ /rejects 0 / || $7 !~ /initfail 0 /) print "PROBLEM: " $0 }' final_summary.txt
awk -F'|' '{ split($5, a, " "); if (a[3] != a[5]) print "BOOKING MISMATCH: " $0 }' final_summary.txt
grep -v "gaps 0 | backwards 0" final_summary.txt | sed 's/^/VWAP LINE CHECK: /'
python3 -I - final_summary.txt <<'EOPY'
import sys, re
for l in open(sys.argv[1]):
    m = re.search(r'last point ([0-9.]+) \| engine VWAP ([0-9.]+)', l)
    if m and abs(float(m.group(1)) - float(m.group(2))) > 1e-6: print('VWAP LAST POINT MISMATCH:', l.strip())
EOPY
echo "checks done"
