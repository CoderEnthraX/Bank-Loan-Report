import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/final_review')
from pine_sim import sim
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from pine_final import run
key = lambda t: (t['dir'], t['arm'], t['fill'], t['entry'], t['stop'], t['exit'], t['res'])
# (sim override, pine_final override)
V = [({'keep':False},{'rearmKeep':False}), ({'cooldown':0},{'cooldownBars':0}), ({'cooldown':1},{'cooldownBars':1}), ({'cooldown':4},{'cooldownBars':4}),
     ({'maxFills':1},{'maxFills':1}), ({'maxFills':2},{'maxFills':2}), ({'dayStopR':0},{'dayStopR':0}), ({'dayStopR':1.5},{'dayStopR':1.5}),
     ({'halfOn':False},{'tightOn':False}), ({'biasNet':2},{'netMin':2}), ({'halfAtr':1.2},{'tightAtr':1.2}), ({'tp4R':1.5},{'tp4R':1.5}),
     ({'minOpenBars':0},{'minOpenBars':0}), ({'minOpenBars':3},{'minOpenBars':3}), ({'slopeBars':0},{'slopeBars':0}), ({'vwapFilter':False},{'vwapFilter':False}),
     ({'momAtr':0},{'momAtr':0}), ({'skipSunday':False},{'skipSunday':False}), ({'retestBars':3},{'retestBars':3}), ({'structLen':8,'entryLen':8},{'structLen':8,'entryLen':8})]
for so, po in V:
    tot = bad = 0
    for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
        a = [key(t) for t in sim(s, True, **so)]; b = [key(t) for t in run(s, po)]
        tot += len(b); bad += len([x for x in a if x not in b]) + len([x for x in b if x not in a])
    print(so, 'trades', tot, 'diffs', bad, flush=True)
