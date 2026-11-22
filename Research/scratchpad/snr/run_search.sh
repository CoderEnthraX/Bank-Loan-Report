#!/bin/bash
cd "$(dirname "$0")"
python3 -I search.py 5 12000 1 > s5_1.log 2>&1 &
python3 -I search.py 5 12000 2 > s5_2.log 2>&1 &
python3 -I search.py 15 15000 3 > s15_3.log 2>&1 &
(python3 -I search.py 60 10000 4 > s60_4.log 2>&1; python3 -I search.py 120 10000 5 > s120_5.log 2>&1; python3 -I search.py 180 10000 6 > s180_6.log 2>&1) &
wait
echo ALLDONE
