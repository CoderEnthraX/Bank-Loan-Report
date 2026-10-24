import sys,json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/hunt2/timing'); sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/xl')
import importlib; sys.path.insert(0,"."); m=importlib.import_module(sys.argv[5] if len(sys.argv)>5 else "m")
from engine2 import prepare
sym=sys.argv[1]; inp=json.loads(sys.argv[2]); d0=sys.argv[3]; d1=sys.argv[4]
T=prepare(sym)['T']
for t in m.run(sym,inp):
    if d0<=T[t['fill']][:10]<=d1:
        print(T[t['arm']][5:],'fill',T[t['fill']][5:],'L' if t['dir']>0 else 'S',round(t['entry'],1),round(t['stop'],1),'exit',T[t['exit']][5:] if t['exit'] else None,t['res'],'tight' if t['tight'] else '')
