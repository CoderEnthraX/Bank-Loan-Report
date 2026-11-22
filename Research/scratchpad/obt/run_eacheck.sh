#!/bin/bash
cd "$(dirname "$0")"
export OBVOL=$PWD/vol_m5_full.txt OBVOL1=$PWD/vol_m1_full.txt
A="m1_full.csv 2024-01-02 2026-10-03 JIT=0.6"
NOF="InpDayOn=0 InpHoursOn=0 InpKzOn=0 InpDNewsOn=0 InpFcOn=0"
./snsimF $A InpSetups=1 > ea_def.log 2>&1 &
./snsimF $A InpSetups=1 InpSnVolLen=80 InpSnSlBuf=0.3 > ea_rec.log 2>&1 &
./snsimF $A InpSetups=1 $NOF > ea_def_nof.log 2>&1 &
./snsimF $A InpSetups=1 InpSnVolLen=80 InpSnSlBuf=0.3 $NOF > ea_rec_nof.log 2>&1 &
wait
echo EACHECKDONE
