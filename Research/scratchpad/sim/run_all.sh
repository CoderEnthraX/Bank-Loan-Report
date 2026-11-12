#!/bin/bash
# all broker-simulator scenarios, v4.3 vs v4.4 (FxPro gold M1 ticks, 3 Aug - 2 Oct 2026). Results: sim/results.txt
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; cd $S/sim
bash build.sh $S/build/safe/AuctionRetestEA.mq5 sim44 > build44.log 2>&1 || { echo "BUILD 44 FAILED"; exit 1; }
bash build.sh $S/bak/v43_final/AuctionRetestEA_v43.mq5 sim43 v43 > build43.log 2>&1 || { echo "BUILD 43 FAILED"; exit 1; }
A="m1_2026q3.csv 2026-08-03 2026-11-01"
declare -A SC=(
 [01_base]="JIT=0" [02_spread]="JIT=0.6" [03_restart]="JIT=0.6 RESTART=2999" [04_restart_off]="JIT=0.6 RESTART=2999 OFF=200"
 [05_newinputs_same]="JIT=0.6 REINIT=3001" [06_newinputs_stress]="JIT=0.6 REINIT=23 InpDispAtr=1.0 ALT=InpDispAtr:0.8"
 [07_tfswitch]="JIT=0.6 TFSW=1999 TFLEN=60" [08_tfswitch_stress]="JIT=0.6 TFSW=37 TFLEN=11" [09_hand_close]="JIT=0.6 EXT=3 HOLD=40"
 [10_other_ea_close]="JIT=0.6 EXT=3 HOLD=40 EXTMAGIC=777" [11_stops_level]="JIT=0.6 STOPS=30" [12_commission]="JIT=0.6 COMM=3.5"
 [13_combined]="JIT=0.6 RESTART=4999 OFF=100 EXT=4 HOLD=30 TFSW=3001 TFLEN=40 REINIT=7001"
 [14_market_restart_off]="JIT=0.6 InpEntryMode=2 RESTART=397 OFF=150" [15_stopmove_restart_off]="JIT=0.6 InpExitAt=2 InpMv1On=1 InpMv1R=0 RESTART=331 OFF=120"
 [16_offline_start]="JIT=0.6 RESTART=397 OFF=150 DISC=1" [17_tp1rule_offline_hand]="JIT=0.6 InpCrkT1=1 RESTART=397 OFF=150 DISC=1 EXT=6")
for k in $(echo ${!SC[@]} | tr ' ' '\n' | sort); do
  for v in 43 44; do ./sim$v $A ${SC[$k]} > sc_${k}_$v.log 2>&1 & done
done; wait
{
echo "Broker simulator, FxPro gold ticks from M1 bars, 3 Aug - 2 Oct 2026, EA defaults; $(date)"
for k in $(echo ${!SC[@]} | tr ' ' '\n' | sort); do
  echo; echo "################ $k: ${SC[$k]}"
  python3 -I analyze.py sc_${k}_43.log sc_${k}_44.log | grep -v "^   bookings [0-9]* vs"
  for v in 43 44; do echo "   v$v rejects: $(grep -c '^SIM REJECT' sc_${k}_$v.log), early-close tags: $(grep -c 'SIMTAG close: engine wins' sc_${k}_$v.log), trades opened while on M1: $(awk '/DRIVER timeframe switch to M1/{m=1} /DRIVER timeframe switch to M5/{m=0} /^SIM OPEN/{if(m)n++} END{print n+0}' sc_${k}_$v.log), INIT FAILED: $(grep -c 'INIT FAILED' sc_${k}_$v.log)"; done
done
echo; echo "################ continuity: restarts / same new inputs against no restart (v4.4, same ticks)"
for k in 03_restart 05_newinputs_same; do python3 -I analyze.py sc_02_spread_44.log sc_${k}_44.log | grep "compare\|bookings [0-9]* vs"; done
for k in 03_restart 05_newinputs_same; do python3 -I analyze.py sc_02_spread_43.log sc_${k}_43.log | grep "compare\|bookings [0-9]* vs"; done
} > results.txt 2>&1
echo done
