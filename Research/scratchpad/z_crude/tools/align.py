# align.py candles.txt "p:y,p:y,..." anchor_x 'YYYY-MM-DD HH:MM' [s_lo s_hi]
import sys, re
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
rows=load('CRUDE'); idx={r['t']:r['i'] for r in rows}
C=[]
for l in open(sys.argv[1]):
    m=re.search(r'c([\d.]+) \w top (\d+) bot (\d+)',l)
    if m: C.append(tuple(float(v) for v in m.groups())); continue
    f=l.split()
    if len(f)>=6 and f[5] in ('bull','bear'): C.append((float(f[0]),float(f[1]),float(f[2])))
pts=[tuple(map(float,s.split(':'))) for s in sys.argv[2].split(',')]
n=len(pts); mp=sum(p for p,_ in pts)/n; my=sum(y for _,y in pts)/n
b=sum((p-mp)*(y-my) for p,y in pts)/sum((p-mp)**2 for p,_ in pts); a=my-b*mp
pr=lambda y:(y-a)/b
ax=float(sys.argv[3]); ai=idx[sys.argv[4]]
lo,hi=(float(sys.argv[5]),float(sys.argv[6])) if len(sys.argv)>6 else (4.0,9.0)
best=None
s=lo
while s<=hi:
    err=0;cnt=0
    for x,t,bt in C:
        k=ai+round((x-ax)/s)
        if 0<=k<len(rows):
            e=abs(pr(t)-rows[k]['h'])+abs(pr(bt)-rows[k]['l']); err+=min(e,60);cnt+=1
    if best is None or err/cnt<best[0]: best=(err/cnt,s)
    s+=0.002
print('best s %.3f meanerr %.2f'%(best[1],best[0])); s=best[1]
for x,t,bt in C:
    k=ai+round((x-ax)/s); r=rows[k]
    print('%7.1f %s  H %.1f/%g  L %.1f/%g  off %.2f'%(x,r['t'],pr(t),r['h'],pr(bt),r['l'],(x-ax)/s-round((x-ax)/s)))
