"""log every displacement the best model detects (armFn called) and the trades, for a symbol and date range"""
import sys, json; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare, run
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
sym, a, b = sys.argv[1], sys.argv[2], sys.argv[3]
P = prepare(sym); T = P['T']; log = []
def af(P, i, d, ctx):
    if a <= T[i] <= b: log.append((T[i], d, ctx['st'], ctx['dayR'], ctx['dayFills']))
    return True
tr = run(P, dict(BEST, armFn=af))
for x in log: print('DISP', *x)
for t in tr:
    if a <= T[t['fill']] <= b: print('TRADE', T[t['arm']], T[t['fill']], t['dir'], round(t['entry'], 5), round(t['stop'], 5), T[t['exit']] if t['exit'] else None, t['res'])
