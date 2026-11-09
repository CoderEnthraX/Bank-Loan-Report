#!/bin/bash
# negative control: an EA copy that does NOT save one recovery value must fail the restart parity (proves the test catches omissions)
S=/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad; N=$S/v43neg
for fld in 'IoD("kl", crkL); ' 'IoD("tn", totalNet); ' 'IoI("kt", crkSkipLeft); '; do
  python3 -I - "$S/build/safe/AuctionRetestEA.mq5" "$N/EA_broken.mq5" "$fld" <<'EOP'
import sys
s = open(sys.argv[1]).read(); f = sys.argv[3]
assert s.count(f) == 1, f
open(sys.argv[2], 'w').write(s.replace(f, ''))
EOP
  (cd $S/mq5check/rec && bash build.sh "$N/EA_broken.mq5" > /dev/null 2>&1)
  if [ "$fld" = 'IoI("kt", crkSkipLeft); ' ]; then r=$(cd $S/mq5check/rec && REC_RESTART=1 REC_DAYS=1 python3 -I parity_crkpr.py 2>&1 | tail -1)
  else r=$(cd $S/mq5check/rec && REC_RESTART=1 python3 -I parity_rec.py 2>&1 | tail -1); fi
  echo "without $fld-> $r" | cut -c1-200 >> $N/neg.log
done
(cd $S/mq5check/rec && bash build.sh > /dev/null 2>&1)   # back to the real EA
echo "done" >> $N/neg.log
