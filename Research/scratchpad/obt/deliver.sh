#!/bin/bash
# v6.0: copy the four files to the repository (+ .txt copies) and the build / check scripts to Research/scratchpad
set -e
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; R=/home/user/Bank-Loan-Report
cp $S/build/out/OrderBlock_Strategy.pine $S/build/out/Auction_Retest_OB_Strategy.pine $R/TradingView/
cp $S/build/out/OrderBlock_Strategy.pine $R/Research/scratchpad/OrderBlock_Strategy.txt
cp $S/build/out/Auction_Retest_OB_Strategy.pine $R/Research/scratchpad/Auction_Retest_OB_Strategy.txt
cp $S/build/out/OrderBlockEA.mq5 $S/build/out/AuctionRetestGridEA.mq5 $R/MetaTrader5/
mkdir -p $R/Research/scratchpad/build $R/Research/scratchpad/ob $R/Research/scratchpad/obt $R/Research/scratchpad/pinecheck
cp $S/build/build_ob_ea.py $S/build/ob_ea_parts.py $S/build/classwrap.py $S/build/build_ob_pine.py $S/build/grid_pine.py $R/Research/scratchpad/build/
cp $S/ob/ob_stream.py $R/Research/scratchpad/ob/
cp $S/obt/prep.py $S/obt/mk.py $S/obt/build_v.sh $S/obt/build_g.sh $S/obt/build_gr.sh $S/obt/runall.sh $S/obt/cmp.py $S/obt/pine_mirror.py $S/obt/deliver.sh $R/Research/scratchpad/obt/
cp $S/pinecheck/loop_audit.py $R/Research/scratchpad/pinecheck/
echo delivered
