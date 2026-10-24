import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma
P=prepare('NIFTY'); rows=P['rows']; atr=rma(P['tr'],14)
ts=[r['t'] for r in rows]
# simple ADX(14)
def adx(n=14):
    pdm=[0];ndm=[0]
    for a,b in zip(rows,rows[1:]):
        up=b['h']-a['h']; dn=a['l']-b['l']
        pdm.append(up if up>dn and up>0 else 0); ndm.append(dn if dn>up and dn>0 else 0)
    tr=P['tr']; atrn=rma(tr,n); sp=rma(pdm,n); sn=rma(ndm,n)
    dx=[]
    for i in range(len(rows)):
        if atrn[i] is None or sp[i] is None: dx.append(0); continue
        p=100*sp[i]/atrn[i]; m=100*sn[i]/atrn[i]
        dx.append(0 if p+m==0 else 100*abs(p-m)/(p+m))
    return rma(dx,n)
ADX=adx()
cases=[('ORIG',  '2026-10-05 09:25',1),('ORIG','2026-10-05 10:35',-1),('ORIG','2026-10-06 09:45',1),('ORIG','2026-10-07 10:25',1),('ORIG','2026-10-07 10:55',1),
('ORIG','2026-10-08 10:35',-1),('ORIG','2026-10-08 13:15',-1),('ORIG','2026-10-09 10:05',1),('ORIG','2026-10-09 13:40',1),('ORIG','2026-10-12 09:50',-1),
('MINEonly','2026-10-07 09:35',-1),('MINEonly','2026-10-07 13:05',-1),('MINEonly','2026-10-07 13:10',-1),('MINEonly','2026-10-08 12:15',-1),('MINEonly','2026-10-08 14:00',-1),('MINEonly','2026-10-12 13:10',-1)]
for who,t,d in cases:
    i=ts.index(t); r=rows[i]
    for L in (6,):
        ph=max(x['h'] for x in rows[i-L:i]); pl=min(x['l'] for x in rows[i-L:i])
    rng=r['h']-r['l']; body=abs(r['c']-r['o'])
    clp=((r['h']-r['c']) if d>0 else (r['c']-r['l']))/rng*100
    lvl=ph if d>0 else pl
    mid=(r['o']+r['c'])/2
    ent=max(mid,ph) if d>0 else min(mid,pl)
    print(f"{who:8s} {t} d{d:+d} rng/atr {rng/atr[i]:.2f} body% {body/rng*100:.0f} closeOff% {clp:.0f} atr {atr[i]:.2f} c-vwap {r['c']-r['vwap']:+.1f} brk {d*(r['c']-lvl):+.1f} entry {ent:.2f} 1.8atr {1.8*atr[i]:.2f} adx {ADX[i]:.1f}")
