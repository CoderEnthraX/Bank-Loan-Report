#!/bin/bash
cd "$(dirname "$0")"
export OBVOL=$PWD/vol_m5_full.txt OBVOL1=$PWD/vol_m1_full.txt
A="m1_full.csv 2024-01-02 2026-10-03 JIT=0.6"
./snsimF $A InpSetups=1 InpRec=0 > ea_def_norec.log 2>&1 &
./snsimF $A InpSetups=1 InpRec=0 InpSnVolLen=80 InpSnSlBuf=0.3 > ea_rec_norec.log 2>&1 &
wait
echo EACHECK2DONE
