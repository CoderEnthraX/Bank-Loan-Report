#!/bin/sh
# usage: sc.sh '<json>' tag  -> score line + A stops into res_<tag>.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad
cd $S/xl && timeout 900 python3 -I score_all.py $S/halfstop3/sc3.py "$1" d > $S/halfstop3/d_$2.txt 2>&1
cd $S/halfstop3 && timeout 900 python3 -I astops3.py "$1" > as_$2.txt 2>&1
echo "$2 $1 :: $(head -1 $S/halfstop3/d_$2.txt) :: $(tail -1 as_$2.txt)"
