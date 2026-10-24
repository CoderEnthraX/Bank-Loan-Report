import sys, os, subprocess, re
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
# usage: fit.py candles.txt SYMBOL xref iref spacing
lines=open(sys.argv[1]).read().split('\n')
sym=sys.argv[2]; xref=float(sys.argv[3]); iref=int(sys.argv[4]); s=float(sys.argv[5])
bars={r['i']:r for r in load(sym)}
pts=[]
for l in lines:
    m=re.match(r'x (\d+)-(\d+) c([\d.]+) (\w) top (\d+) bot (\d+) w(\d+)',l)
    if not m: continue
    c=float(m.group(3)); col=m.group(4); top=int(m.group(5)); bot=int(m.group(6)); w=int(m.group(7))
    fi=iref+(c-xref)/s; i=round(fi)
    if i not in bars: continue
    b=bars[i]; bc='G' if b['c']>=b['o'] else 'R'
    pts.append((c,fi-i,i,b['t'],col,bc,top,bot,max(b['o'],b['c']),min(b['o'],b['c']),b['h'],b['l'],w))
# regression on body top/bot for matched colors with w>=3
import statistics
X=[];Y=[]
for p in pts:
    if p[4]==p[5] and 3<=p[12]<=5:
        X+= [p[8],p[9]]; Y+=[p[6],p[7]]
n=len(X); mx=sum(X)/n; my=sum(Y)/n
b=sum((x-mx)*(y-my) for x,y in zip(X,Y))/sum((x-mx)**2 for x in X); a=my-b*mx
print('y = %.3f + %.5f*price  (px/unit %.4f)'%(a,b,-b))
for p in pts:
    ptop=(p[6]-a)/b; pbot=(p[7]-a)/b
    print(f"x{p[0]:7.1f} frac{p[1]:+.2f} {p[3]} img{p[4]} dat{p[5]} imgTop {ptop:8.1f} imgBot {pbot:8.1f} | bodyT {p[8]} bodyB {p[9]} H {p[10]} L {p[11]} w{p[12]}")
