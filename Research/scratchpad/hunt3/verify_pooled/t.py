import sys,json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/pooled')
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import pf
from arp_data import load
R=load('CRUDE')
for opt in ({'erMin':0.2},{'erMin':0.2,'dayStopR':0}):
    print(opt)
    for t in pf.run('CRUDE',dict(opt)):
        a=R[t['arm']]['t']
        if a[:10] in('2026-10-15',):
            print(t['dir'],'arm',a[5:],'fill',R[t['fill']]['t'][5:],'exit',R[t['exit']]['t'][5:] if t['exit'] is not None else None,round(t['res'],2) if t.get('res') is not None else None)
