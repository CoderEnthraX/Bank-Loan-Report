import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare
for sym in ['SENSEX','CRUDE','NIFTY','ETH','US30','GC1','EURUSD','NASDAQ']:
    try:P=prepare(sym)
    except Exception: continue
    R=P['rows'];ds=[i for i in range(len(R)) if P['daystart'][i]]+[len(R)]
    out=[]
    for k in range(1,len(ds)-1):
        a,b,c=ds[k-1],ds[k],ds[k+1]
        pH=max(r['h'] for r in R[a:b]);pL=min(r['l'] for r in R[a:b]);o=R[b]['o']
        if o>pH or o<pL: out.append((R[b]['t'][:10],'above' if o>pH else 'below'))
    print(sym,len(ds)-2,'sessions; open outside prev range:',len(out),out[-12:] if sym in('SENSEX','CRUDE') else out[-6:])
