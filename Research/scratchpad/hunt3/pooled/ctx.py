import sys, json
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/xl'); sys.path.insert(0,'.')
import pf
from engine2 import prepare
from load_xl import load
D=json.load(open('feat.json'))
print([ (o['sym'],o['t'],o['lab'],round(o['f']['brk10'],3)) for o in D if o['f']['brk10']<0.02])
X=load()
for o in D:
    if not (o['lab'].startswith('extra') or o['lab']=='must'): continue
    sym=o['sym']; P=prepare(sym); T=P['T']; i=o['i']
    tr=pf.run(sym,{"dayStopR":0}); sig=pf.SIGS[sym]
    print('====',sym,o['t'],o['lab'])
    for m in tr:
        if i-80<=m['fill']<=i+30: print('   model', 'L' if m['dir']>0 else 'S','arm',T[m['arm']],'fill',T[m['fill']][11:],'exit',T[m['exit']][11:] if m['exit'] else None,m['res'], 'e %.6g s %.6g'%(m['entry'],m['stop']))
    print('   sigs', [(T[s][11:], 'L' if d>0 else 'S') for s,d in sig if i-60<=s<=i+20])
    for x in X:
        if x['sym']==sym and x['date']==T[i][:10]: print('   log #%s %s-%s %s e %s s %s %s'%(x['n'],x['tin'],x['tout'],'L' if x['d']>0 else 'S',x['entry'],x['stop'],x['maxtp']))
