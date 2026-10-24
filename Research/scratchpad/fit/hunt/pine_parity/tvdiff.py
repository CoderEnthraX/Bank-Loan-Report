import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/pine_parity')
import gtscore, eng_eps
from engine2 import prepare, run as run2
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
tr, win = gtscore.load_gt('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/gt/final')
TV = dict(BEST, epsR=float(sys.argv[1]), epsF=float(sys.argv[2]))
for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P = prepare(s); T = P['T']
    f = lambda ts: {(T[t['arm']], T[t['fill']], 'L' if t['dir'] > 0 else 'S', round(t['entry'], 6), T[t['exit']] if t['exit'] is not None else None, t['res']) for t in ts}
    a = f(run2(P, BEST)); b = f(eng_eps.run(P, TV))
    for x in sorted(a - b):
        if x[1] >= '2026-10-04': print(s, 'python-only', x, 'covered' if gtscore.covered(win, s, x[1]) else 'not-covered')
    for x in sorted(b - a):
        if x[1] >= '2026-10-04': print(s, 'TV-only    ', x, 'covered' if gtscore.covered(win, s, x[1]) else 'not-covered')
gtscore.run = eng_eps.run
r, rows = gtscore.score(TV, tr, [dict(w) for w in win], detail=True)
print('TV-faithful score', {k: r[k] for k in ('exact','miss','extra')})
