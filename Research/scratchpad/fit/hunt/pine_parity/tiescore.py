import sys, os, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/pine_parity')
import gtscore, eng_eps
from engine2 import prepare, run as run2
gtscore.run = eng_eps.run
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
tr, win = gtscore.load_gt('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/final')
SY=['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']
def key(ts, P): return {(P['T'][t['fill']], t['dir'], round(t['entry'],7), P['T'][t['exit']] if t['exit'] is not None else None) for t in ts}
base = {s: key(run2(prepare(s), BEST), prepare(s)) for s in SY}
for extra in [dict(), dict(epsR=1e-7), dict(epsR=-1e-7), dict(epsF=1e-6), dict(epsF=-1e-6), dict(epsR=1e-7, epsF=1e-6), dict(epsR=-1e-7, epsF=-1e-6)]:
    cfg = dict(BEST); cfg.update(extra)
    eng_eps.TIES.clear()
    r, rows = gtscore.score(cfg, tr, [dict(w) for w in win], detail=True)
    ch = {}
    for s in SY:
        P = prepare(s); k = key(eng_eps.run(P, cfg), P); d = k ^ base[s]
        win_d = [x for x in d if '2026-10-05' <= x[0] <= '2026-10-12 23:59']
        ch[s] = (len(d), len(win_d))
    print(extra, {k: r[k] for k in ('exact','miss','extra')}, 'changed trades (all, Oct5-12) per sym:', ch)
    if not extra:
        ties = eng_eps.TIES[:]
# list ties in base run
from collections import Counter
print('tie events in base run:', Counter((t[0], t[1]) for t in ties))
for t in ties:
    if '2026-10-04' <= t[2] <= '2026-10-12 23:59': print('  window tie', t)
