"""What the TP HIT / BREAKEVEN rows show: STATS block logic applied to ref.py trades (shown trades, all instruments)."""
import sys; S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/build'); sys.path.insert(0,S+'/fit')
import ref
from engine import prepare as eprep
SY=['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH','NSE_NIFTY1','MCX_NATURALGAS']
def stats(opts, syms=SY):
    p=dict(ref.IN); p.update(opts); tpR=(p['tp1R'],p['tp2R'],p['tp3R'],p['tp4R']); xk=p['exitAt']
    tot=w=0; hit=[0]*4; be=lk=0; R=0.0
    for s in syms:
        P=eprep(s); H=[r['h'] for r in P['rows']]; L=[r['l'] for r in P['rows']]; mt=P['mt']
        for x in ref.shown(s,opts):
            if x['exit'] is None: continue
            d=x['dir']; e=x['entry']; st=x['stop']; risk=d*(e-st); win=x['res'] is not None and x['res']>0 and x['exit']>x['fill'] and False
            # engine result: win = exited at the final target
            res=x['res']; tot+=1; R+=res
            # final stop level of the trade is unknown here when moved; recompute via a stop-hit scan is not needed: use res sign
            isWin = abs(res - tpR[xk-1]) < 1e-9 and not (p['mv1On'] or p['mv2On'] or p['mv3On']) or (abs(res - tpR[xk-1]) < 1e-9)
            w+=isWin
            best=e
            for k in range(x['fill']+1, x['exit']+1):
                stopHit = L[k] <= st + mt*0.001 if d>0 else H[k] >= st - mt*0.001
                if not stopHit: best = max(best,H[k]) if d>0 else min(best,L[k])
            for k in range(1,5):
                lv=e+d*tpR[k-1]*risk
                if (k<=xk) if isWin else (k<xk and d*(best-lv) >= -mt*0.001): hit[k-1]+=1
            if not isWin and res==0.0: be+=1
            elif not isWin and res>0: lk+=1
    return tot,w,R,hit,be,lk
for nm,o in (('defaults',{}),('BE at TP2 (mv2On, 0R)',{"mv2On":True,"mv2R":0.0}),('natural gas only',{})):
    t,w,R,hit,be,lk=stats(o, ['MCX_NATURALGAS'] if 'natural' in nm else SY)
    print('%-24s trades %d  win %.0f%%  R %+.0f | TP1 %.0f%% (%d) TP2 %.0f%% (%d) TP3 %.0f%% (%d) TP4 %.0f%% (%d) | BE %d locked %d'%(nm,t,100*w/t,R,*[v for k in range(4) for v in (100*hit[k]/t,hit[k])],be,lk))
