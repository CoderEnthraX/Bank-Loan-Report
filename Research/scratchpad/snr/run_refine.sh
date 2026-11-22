#!/bin/bash
cd "$(dirname "$0")"
python3 -I refine.py 5 1.0 11 > r5_1.log 2>&1 &
python3 -I refine.py 5 0.5 12 > r5_05.log 2>&1 &
(python3 -I refine.py 15 1.0 13 > r15_1.log 2>&1; python3 -I refine.py 15 0.5 14 > r15_05.log 2>&1) &
(python3 -I refine.py 60 1.0 15 > r60_1.log 2>&1; python3 -I refine.py 120 1.0 16 > r120_1.log 2>&1; python3 -I refine.py 180 1.0 17 > r180_1.log 2>&1) &
wait
echo REFINEDONE
