import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt2/halfstop')
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import m
from engine import prepare
for sym in ['SENSEX','CRUDE','NIFTY','ETH','US30','GC1','EURUSD','NASDAQ','GOLD']:
    try: P=prepare(sym)
    except Exception as e: continue
    R=P['rows']
    a=m.run(sym,{}); b=m.run(sym,eval(sys.argv[1]))
    ka={(t['fill'],t['dir']):t for t in a}
    print(sym,len(a),len(b))
    for t in b:
        o=ka.get((t['fill'],t['dir']))
        if o is None or o['tight']!=t['tight'] or o['stop']!=t['stop']:
            print('  DIFF',R[t['fill']]['t'],t['dir'],'tight',t['tight'],'old',None if o is None else (o['tight'],o['res']),'new res',t['res'])
    for t in a:
        if (t['fill'],t['dir']) not in {(x['fill'],x['dir']) for x in b}: print('  GONE',R[t['fill']]['t'],t['dir'])
