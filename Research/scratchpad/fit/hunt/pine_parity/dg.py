import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, run, rma
sym=sys.argv[1]; a=int(sys.argv[2]); b=int(sys.argv[3]); L=int(sys.argv[4]) if len(sys.argv)>4 else 6
P=prepare(sym); R=P['rows']; A=rma(P['tr'],14)
for i in range(a,b+1):
    r=R[i]; rng=r['h']-r['l']; body=abs(r['c']-r['o'])
    ph=max(x['h'] for x in R[i-L:i]); pl=min(x['l'] for x in R[i-L:i])
    print(i, r['t'], 'O',r['o'],'H',r['h'],'L',r['l'],'C',r['c'],'vw',round(r['vwap'],6),'atr',round(A[i],6),'rng/atr',round(rng/A[i],3),'body%',round(100*body/rng,1) if rng else None,
          'up%',round(100*(r['h']-r['c'])/rng,1) if rng else None,'dn%',round(100*(r['c']-r['l'])/rng,1) if rng else None,'ph',ph,'pl',pl,'ds',P['daystart'][i], 'LF' if r['lf'] else '', 'SF' if r['sf'] else '')
