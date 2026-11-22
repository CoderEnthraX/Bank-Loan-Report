"""obt/EA_obt.mq5: an EA from build/out with an OBSIG log line at each order block signal. Run: python3 -I mk.py SRC.mq5"""
import sys
S = '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
s = open(sys.argv[1]).read()
a = "   else         { for(int j = obPHN - 1; j >= 0; j--) if(obPH[j] > c) { obStopS = obPH[j] + buf; break; } }\n}"
assert s.count(a) == 1
s = s.replace(a, a[:-1] + '   Print("OBSIG ", (long)t, " ", sig, " ", DoubleToString(c, 2), " ", DoubleToString(obStopC, 2), " ", DoubleToString(obStopS, 2));\n}')
open(S + '/obt/EA_obt.mq5', 'w').write(s)
