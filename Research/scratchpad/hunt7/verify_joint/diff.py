import sys,json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/joint')
import j
from arp_data import load
B=dict(slopeCross=True,minOpenBars=0,cooldownBars=1,dayStopR=0,tightOut=True,erMin=0.2)
def mod(**k): d=dict(B); d.update(k); return d
cfgs={'NEW':mod(),'s2':mod(s2Len=6,s2Far=2.0),'er21':mod(erMin=0.21),'er22cb':mod(erMin=0.22,cancelBlock=1),'best':mod(erMin=0.22,s2Len=6,s2Far=2.0,cancelBlock=1)}
base=sys.argv[1]; oth=sys.argv[2]
for sym in ['SENSEX','CRUDE','NSE_NIFTY1','MCX_NATURALGAS','NIFTY','GC','EURUSD','NASDAQ','US30','ETH']:
    try:
        R=load(sym); t={}
        for k in (base,oth):
            try: tr=j.run(sym,cfgs[k])
            except Exception as e: print(sym,'ERR',e); tr=[]
            t[k]={(x['fill'],x['dir']):x for x in tr}
    except Exception as e: print(sym,'load err',e); continue
    for key in sorted(set(t[base])|set(t[oth])):
        a=t[base].get(key);b=t[oth].get(key)
        if (a is None)!=(b is None) or (a and b and (a['res'],a['stop'],a['exit'])!=(b['res'],b['stop'],b['exit'])):
            x=a or b; print(sym,R[key[0]]['t'],'dir',key[1],'only in '+(base if a and not b else oth if b and not a else 'both-differ'),'res',x['res'], (a or {}).get('res'),(b or {}).get('res'))
