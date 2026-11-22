#!/bin/bash
cd "$(dirname "$0")"; export OBVOL=$PWD/vol_m5.txt
A="../sim/m1_2026q3.csv 2026-06-10 2026-10-03 JIT=0.6 InpWarmBars=100000"
./obbase $A > r_base.log 2>&1 &
./obob $A > r_ob.log 2>&1 &
./obgrid $A InpSetups=0 > r_g0.log 2>&1 &
./obgrid $A InpSetups=1 > r_g1.log 2>&1 &
./obgrid $A InpSetups=2 > r_g2.log 2>&1 &
./obgrid $A InpSetups=3 > r_g3.log 2>&1 &
wait; echo done
