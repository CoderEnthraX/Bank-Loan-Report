import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt5/residual')
import importlib
mod = importlib.import_module(sys.argv[1]); inp = json.loads(sys.argv[2]); sym=sys.argv[3]; a,b=sys.argv[4],sys.argv[5]
from engine import prepare
R = prepare(sym)['rows']
for t in mod.run(sym, inp):
    ta = R[t['arm']]['t']
    if a <= ta <= b:
        print('arm',ta,'fill',R[t['fill']]['t'],'D',t['dir'],'e',round(t['entry'],2),'s',round(t['stop'],2),'exit',R[t['exit']]['t'] if t['exit'] is not None else None,t['res'],'tight',t['tight'])
