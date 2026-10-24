import sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/hunt3/data')
from vwalt import weights
P,w,bad,err=weights('NASDAQ'); R=P['rows']; D=P['daystart']
from collections import Counter
c=Counter(); W=0; ex=[]
for i,r in enumerate(R):
    if D[i]: W=1; continue
    if r['vwap'] is None or R[i-1]['vwap'] is None: continue
    hl=(r['h']+r['l']+r['c'])/3; den=hl-R[i-1]['vwap']; num=r['vwap']-R[i-1]['vwap']
    rr=num/den if abs(den)>1e-7*abs(hl) else None
    if rr is None or not (0<rr<1):
        c[r['t'][:10]]+=1
        if len(ex)<15: ex.append((i,r['t'],round(hl,2),R[i-1]['vwap'],r['vwap'],rr))
print(c.most_common(20)); [print(e) for e in ex]
print(sum(1 for d in D if d))
