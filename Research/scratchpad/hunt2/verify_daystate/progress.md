# verify_daystate progress
- re-ran score2 on ds.py: none 79/1/3 | B 36/6 33/36; pine_final dayStopR=0 identical; maxFills 3/4/6/7/99 A 60/20/2, 72/8/3, 79/1/8, 78/2/11, 71/9/16 (B 29,34,36,36,36) all match analyst
- eodFlat true: A 77/3/5 matches; B is 34 matched, 31/34 stops (analyst wrote "B 31" = stops only)
- dsStrict, loss4, netR: A 79/1/3 B 36 33/36; lossDir3 and eve17: B 35 32/35 -> match
- v2.py: all trades differ between base and no-daily-stop on many outside-window days (~100), 0 inside any A window -> A has no evidence either way
- CRUDE 10-13: #51,#52,#53 three clean SL (-1R each) then #54 8841/8809, #55 8910/8872 -> model entries 8840.5/8910, stops 8808.33/8871.38, exits 19:30/22:25 match: strong evidence against -3R block
- CRUDE 10-16 #62 recovered (9259.5/9230.11 vs 9260/9231) but only if carry-over 09:00 exit counts; extra test ds_v.py carryPrev (exit on first session bar counted to previous day): with lossDir3 or eveReset17 -> B 36 33/36, A 79/1/3 (ties with no stop)
- CRUDE #48 10-09: model entry 8878.5 vs log 8880 (1.5 pts), stop 8833.69 vs 8833; weak match, and log shows #45 TP2/#46 TP3 not full losses so the 3-loss count there is ambiguous
- SENSEX 10-09 L carries to 10-12 09:15 gap TP4 (high 72884.2), then arms 09:35 -> fill 09:40 S matches #72 log
