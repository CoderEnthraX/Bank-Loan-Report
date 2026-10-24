import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_author')
from alib import *
from engine2 import run
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
P = get('US30'); T = P['T']; tr = run(P, BEST)
for t in tr:
    if T[t['fill']] >= '2026-10-08':
        print(T[t['arm']], T[t['fill']], t['dir'], T[t['exit']] if t['exit'] is not None else None, t['res'])
dip, dim, adx = P['dmi']
# candidate snapshot bars: after last exit on a day with 2 fills 1W1L last stop
for i in range(len(T)):
    if T[i] < '2026-10-08' : continue
    if round(adx[i]) == 29:
        f = feats(P, i); print(T[i], f"adx {f['adx']:.1f} ch14 {f['chop14']:.1f} spr {f['spr']:+.1f} cv {f['cv']:+.2f}")
