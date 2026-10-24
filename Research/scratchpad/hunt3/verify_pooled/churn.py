import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/pooled')
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import pf
syms=['CRUDE','ETH','NIFTY','SENSEX','GC','US30','NASDAQ','EURUSD']
tot=[0,0,0,0]
for s in syms:
    try:
        a={(t['fill'],t['dir']) for t in pf.run(s,{'dayStopR':0})}; b={(t['fill'],t['dir']) for t in pf.run(s,{'dayStopR':0,'erMin':0.2})}
    except Exception as e: print(s,e); continue
    print(s,len(a),len(b),'removed',len(a-b),'added',len(b-a)); tot[0]+=len(a);tot[1]+=len(b);tot[2]+=len(a-b);tot[3]+=len(b-a)
print(tot)
