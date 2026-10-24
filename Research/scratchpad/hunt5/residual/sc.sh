#!/bin/sh
# usage: sc.sh '<extra json merged into CANDIDATE>'
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad
J=$(python3 -I -c "import json,sys; c={'slopeCross':True,'minOpenBars':0,'cooldownBars':1,'dayStopR':0,'tightOut':True,'erMin':0.2}; c.update(json.loads(sys.argv[1])); print(json.dumps(c))" "$1")
cd $S/xl && timeout 900 python3 -I score2.py $S/hunt5/residual/rc.py "$J" d 2>&1 | grep -v "^   B STOP CRUDE 5[28]\|^   B STOP CRUDE 60"
