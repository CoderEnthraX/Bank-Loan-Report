#!/bin/bash
W=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/stops
NEW='"slopeCross":true,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":true,"erMin":0.2'
J="{$NEW${1:+,$1}}"
cd $W/../../xl && r=$(timeout 900 python3 -I score_all.py ${MOD:-$W/combo.py} "$J" $2); printf '%s => %s\n' "$1" "$(echo "$r" | head -1)"; [ -n "$2" ] && echo "$r" | tail -n +2; true
