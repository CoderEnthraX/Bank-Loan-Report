import sys, importlib.util
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
spec=importlib.util.spec_from_file_location('m','/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/keycases/kc.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
for s in ('CRUDE','ETH','EURUSD','GC','NASDAQ','NIFTY','SENSEX','US30'):
    T=prepare(s)['T']; tr=sorted(M.run(s,{"dayStopR":0}),key=lambda t:t['fill'])
    for p,c in zip(tr,tr[1:]):
        if p['dir']==c['dir'] and p['exit'] is not None:
            sig=c['arm']  # arm bar index
            if 0<sig-p['exit']<=10 and sig-p['fill']>=10:
                print(s,T[p['fill']],'exit',T[p['exit']],'next arm',T[c['arm']],'fill',T[c['fill']],'dirs',c['dir'],'res',c['res'])
