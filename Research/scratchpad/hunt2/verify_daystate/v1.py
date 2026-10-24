import sys, os, importlib.util, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/xl')
from load_xl import load
from engine2 import prepare
from engine import rma
spec=importlib.util.spec_from_file_location('m',S+'/hunt2/daystate/ds.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sym=sys.argv[1]; d1,d2=sys.argv[2],sys.argv[3]
opt=json.loads(sys.argv[4]) if len(sys.argv)>4 else {}
P=prepare(sym); T=P['T']; A=rma(P['tr'],14)
for tag,o in (('NODS',dict(opt,dsMode='none')),('BASE',opt)):
    print('---',tag)
    for m in M.run(sym,o):
        if d1<=T[m['fill']][:10]<=d2:
            print(' arm',T[m['arm']][5:],'fill',T[m['fill']][5:],'L' if m['dir']>0 else 'S','e %.6g s %.6g'%(m['entry'],m['stop']),'exit',T[m['exit']][5:] if m['exit'] else None,m['res'])
print('--- LOG')
for x in load():
    if x['sym']==sym and d1<=x['date']<=d2: print(' #%d'%x['n'],x['date'],x['tin'],'L' if x['d']>0 else 'S',x['entry'],x['stop'],x['maxtp'],x.get('tout'))
