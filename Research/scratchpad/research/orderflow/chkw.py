import sys
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/hunt3/data')
from vwalt import weights
from engine2 import prepare
import statistics as st
for s in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH','NSE_NIFTY1','MCX_NATURALGAS']:
    P,w,bad,err=weights(s); P2=prepare(s); R=P['rows']; D=P['daystart']
    n=len(R); first=[i for i in range(n) if D[i]]
    s1=first[1] if len(first)>1 else 0
    # err after first session
    sp=sw=0; e=0; ee=[]
    for i,r in enumerate(R):
        if D[i]: sp=sw=0
        sp+=w[i]*(r['h']+r['l']+r['c'])/3; sw+=w[i]
        if i>=s1 and r['vwap'] is not None: d=abs(sp/sw-r['vwap']); ee.append(d/ (P2['tr'][i] or 1))
    badafter=0
    # dispersion of w within sessions normalised by session median
    rel=[]; 
    for a,b in zip(first,first[1:]+[n]):
        ws=w[a:b]; m=st.median(ws) if ws else 1
        rel+= [x/m for x in ws[1:]] if m>0 else []
    rel.sort()
    print(f"{s:15s} n={n} sessions={len(first)} same_len={len(P2['H'])==n} bad={bad} maxerr/TR={max(ee):.4f} relw p10={rel[len(rel)//10]:.2f} p50={rel[len(rel)//2]:.2f} p90={rel[9*len(rel)//10]:.2f} p99={rel[99*len(rel)//100]:.2f}")
