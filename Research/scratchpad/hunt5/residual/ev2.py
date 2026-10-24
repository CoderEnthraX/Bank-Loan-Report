import sys, os
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'; sys.path.insert(0,F)
import gtscore
from engine import prepare, rma
tr, win = gtscore.load_gt(os.path.join(F,'..','gt','final'))
k=6; erm=0.2
for Fd in (1.0,1.5,2.0,2.5):
    tot=inA=0; lst=[]
    for sym in ['CRUDE','GC','NASDAQ','NIFTY','US30','SENSEX','EURUSD','ETH']:
        P=prepare(sym); R=P['rows']; atr=rma(P['tr'],14)
        O=[r['o'] for r in R];H=[r['h'] for r in R];L=[r['l'] for r in R];C=[r['c'] for r in R];V=[r['vwap'] for r in R]
        for i in range(12,len(R)):
            A=atr[i]; 
            if not A: continue
            rng=H[i]-L[i]
            if rng<=0 or rng<0.8*A or abs(C[i]-O[i])/rng*100<55-1e-7: continue
            for d in (1,-1):
                if d==1:
                    ok = C[i]>O[i] and (H[i]-C[i])/rng*100<=25+1e-7 and C[i]>max(H[i-k:i]) and V[i]-V[i-3]>0 and C[i]>V[i] and max(H[i-10:i])-C[i]>=Fd*A
                else:
                    ok = C[i]<O[i] and (C[i]-L[i])/rng*100<=25+1e-7 and C[i]<min(L[i-k:i]) and V[i]-V[i-3]<0 and C[i]<V[i] and C[i]-min(L[i-10:i])>=Fd*A
                if not ok: continue
                m=d*(C[i]-C[i-k]); pth=sum(abs(C[j]-C[j-1]) for j in range(i-k+1,i+1))
                if m<0.85*A or m/pth<erm: continue
                tot+=1
                if gtscore.covered(win,sym,R[i]['t']) or gtscore.covered(win,sym,R[min(i+5,len(R)-1)]['t']): inA+=1; lst.append((sym,R[i]['t'],d))
    print('F',Fd,'events',tot,'in/near A windows',inA,lst)
