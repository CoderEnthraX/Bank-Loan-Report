import sys,json; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/data'); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import dm
from engine2 import prepare
sym=sys.argv[1]; d=sys.argv[2]; inp=json.loads(sys.argv[3]) if len(sys.argv)>3 else {}
P=prepare(sym); T=P['T']
for t in dm.run(sym,inp):
    if T[t['arm']][:10]==d: print(T[t['arm']][11:],'->',T[t['fill']][11:],'exit',T[t['exit']][11:] if t['exit'] is not None else None,t['dir'],round(t['entry'],1),round(t['stop'],1),t['res'])
