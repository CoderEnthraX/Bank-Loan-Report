"""px.py img  y=..  x=..  -> convert"""
import sys,numpy as np
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
byi={r['i']:r for r in load('NIFTY')}
x0,s,iref,a,c=np.load('/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/z_nifty/fit_%s.npy'%sys.argv[1])
for arg in sys.argv[2:]:
    t,v=arg.split('='); v=float(v)
    if t=='y': print('y',v,'-> price %.2f'%((v-c)/a))
    elif t=='dy': print('dy',v,'-> points %.2f'%(-v/a))
    elif t=='x':
        fi=(v-x0)/s+iref; i=int(round(fi)); print('x',v,'-> index %.2f'%fi, i, byi[i]['t'] if i in byi else '')
    elif t=='p': print('price',v,'-> y %.2f'%(a*v+c))
    elif t=='i': print('index',int(v),byi[int(v)]['t'],'-> x %.2f'%(x0+(v-iref)*s))
