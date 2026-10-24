"""Record model state (ctx) at every arm call in the full engine; join with the 80 GT trades."""
import sys, os, json
FIT='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0, FIT)
from gtscore import load_gt, score
from engine2 import prepare, run
from tightdata import TRADES
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
TIGHT = {(t['sym'], t['arm']) for t in TRADES if t['tight']}
REC = {}
def mk(oracle=True, extra=None):
    def fn(P, i, d, entry, stop, A, ctx):
        tr = ctx['trades']
        snap = dict(trades=[dict(x) for x in tr], dayFills=ctx['dayFills'], dayLoss=ctx['dayLoss'], dayR=ctx['dayR'], streak=ctx['streak'],
                    lastExit=ctx['lastExit'], lastRes=ctx['lastRes'], st=ctx['st'], armBar=ctx['armBar'], lim=ctx['lim'])
        REC.setdefault(P['sym'], []).append((i, d, snap))
        return stop
    cfg = dict(BEST); cfg['stopFn'] = fn
    if oracle: cfg['tightSet'] = TIGHT
    if extra: cfg.update(extra)
    return cfg
def runall(oracle=True):
    REC.clear(); out = {}
    for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
        P = prepare(s); out[s] = run(P, mk(oracle))
    return out
if __name__ == '__main__':
    out = runall(True)
    for t in TRADES:
        s = t['sym']; P = prepare(s); A = P[('atr',14)]
        recs = [r for r in REC[s] if r[0] == t['arm_i'] and r[1] == t['d']]
        if not recs: print(s, t['fill'], 'NO ARM CALL'); continue
        snap = recs[-1][2]; tr = snap['trades']
        prev = tr[-1] if tr else None
        def tg(x): return x['dir']*(x['entry']-x['stop'])/A[x['arm']] < 1.4
        ps = ''
        for x in tr[-4:]:
            ps += f" [{P['T'][x['fill']][5:]} {'L' if x['dir']>0 else 'S'} {x['res']:+.0f}{' T' if tg(x) else ''}]"
        print(f"{s:6s} {t['fill']} {'L' if t['d']>0 else 'S'} {'TIGHT' if t['tight'] else '     '} n={len(tr):3d} dF={snap['dayFills']} dR={snap['dayR']:+.0f} stk={snap['streak']} st={snap['st']:+d} gap={(t['arm_i']-snap['lastExit']) if snap['lastExit'] is not None else -1:4d} |{ps}")
