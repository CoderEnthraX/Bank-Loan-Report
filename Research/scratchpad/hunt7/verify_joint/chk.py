import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
sym,a,b=sys.argv[1:4]
R=load(sym); n=len(R)
O=[r['o'] for r in R];H=[r['h'] for r in R];L=[r['l'] for r in R];C=[r['c'] for r in R];V=[r['vwap'] for r in R]
tr=[H[0]-L[0]]+[max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])) for i in range(1,n)]
atr=[None]*n; s=sum(tr[:14])/14; atr[13]=s
for i in range(14,n): atr[i]=(atr[i-1]*13+tr[i])/14
for i,r in enumerate(R):
    if a<=r['t']<=b and i>=11:
        A=atr[i]; rng=H[i]-L[i]; body=abs(C[i]-O[i])/rng*100 if rng else 0
        ph10=max(H[i-10:i]);pl10=min(L[i-10:i]);ph6=max(H[i-6:i]);pl6=min(L[i-6:i])
        er10=(C[i]-C[i-10])/sum(abs(C[j]-C[j-1]) for j in range(i-9,i+1))
        er6=(C[i]-C[i-6])/sum(abs(C[j]-C[j-1]) for j in range(i-5,i+1))
        print(i,r['t'],f"O{O[i]} H{H[i]} L{L[i]} C{C[i]} V{V[i]:.2f} atr{A:.2f} rng/atr{rng/A:.2f} body{body:.0f} clsHi{(H[i]-C[i])/rng*100:.0f} clsLo{(C[i]-L[i])/rng*100:.0f} brk10up{(C[i]-ph10)/A:.2f} brk10dn{(pl10-C[i])/A:.2f} brk6up{(C[i]-ph6)/A:.2f} brk6dn{(pl6-C[i])/A:.2f} mom10{(C[i]-C[i-10])/A:.2f} er10 {er10:.3f} er6 {er6:.3f} farUp{(ph10-C[i])/A:.2f} farDn{(C[i]-pl10)/A:.2f} fills{r['lf']}{r['sf']}")
