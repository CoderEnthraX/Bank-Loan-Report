import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/data'); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import dm
from engine2 import prepare
from engine import rma
import json
syms=['NIFTY','SENSEX','CRUDE','ETH','BTC','NATGAS','GOLD','BANKNIFTY']
import os
for s in syms:
    try: P=prepare(s)
    except Exception as e: continue
    T=P['T']; A=rma(P['tr'],14)
    base=dm.run(s,{}); fb=dm.run(s,{'minOpenBars':0})
    bs={(t['arm'],t['dir']) for t in base}
    new=[t for t in fb if (t['arm'],t['dir']) not in bs]
    old=[t for t in base if (t['arm'],t['dir']) not in {(x['arm'],x['dir']) for x in fb}]
    print(s,len(base),len(fb),'new:',[(T[t['arm']],t['dir'],T[t['fill']]) for t in new],'lost:',[(T[t['arm']],t['dir']) for t in old])
