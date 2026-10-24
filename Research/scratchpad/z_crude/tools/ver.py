# ver.py dir arm fill entry R  (times 'YYYY-MM-DD_HH:MM')
import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('CRUDE'); idx={r['t']:r['i'] for r in rows}
d=1 if sys.argv[1]=='L' else -1; a=idx[sys.argv[2].replace('_',' ')]; f=idx[sys.argv[3].replace('_',' ')]
E=float(sys.argv[4]); R=float(sys.argv[5]); S=E-d*R; T=E+2*d*R
touch=lambda r: r['l']<=E if d>0 else r['h']>=E
pre=[rows[i]['t'][11:] for i in range(a+1,f) if touch(rows[i])]
print('entry',E,'stop %.2f tp4 %.2f'%(S,T),'| fill bar touches:',touch(rows[f]),'| earlier touches after arm:',pre)
for i in range(f,len(rows)):
    r=rows[i]; hs = r['l']<=S if d>0 else r['h']>=S; ht = r['h']>=T if d>0 else r['l']<=T
    if hs or ht:
        print('exit',r['t'],'STOP' if hs else '', 'TP4' if ht else '', 'H%g L%g'%(r['h'],r['l'])); break
