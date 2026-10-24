import sys, json; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/joint'); sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import j
from engine2 import prepare
NEW={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
sym, lo, hi = sys.argv[1:4]
for a in sys.argv[4:]:
    c=dict(NEW); c.update(json.loads(a)); T=prepare(sym)['T']; print(a)
    for t in j.run(sym,c):
        if lo<=T[t['fill']]<=hi: print('  arm',T[t['arm']][5:],'fill',T[t['fill']][5:],'L' if t['dir']>0 else 'S',round(t['entry'],2),round(t['stop'],2),'exit',T[t['exit']][5:] if t['exit'] is not None else None,t['res'],'T' if t['tight'] else '')
