import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load
sym,cf,x0,i0,yref,pref,k=sys.argv[1],sys.argv[2],float(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),float(sys.argv[6]),float(sys.argv[7])
D={r['i']:r for r in load(sym)}
C=[]
for l in open(cf).read().split('\n')[1:]:
  f=l.split()
  if len(f)>=7 and int(f[6])>=3: C.append((float(f[0]),int(f[1]),int(f[2])))
P=lambda y: pref-(y-yref)/k
res=[]
for s100 in range(400,800):
  s=s100/100; e=[]
  for x,yt,yb in C:
    i=round(i0+(x-x0)/s)
    if i in D: e.append(min(abs(P(yt)-D[i]['h']),30)+min(abs(P(yb)-D[i]['l']),30))
  res.append((sum(e)/len(e),s))
res.sort(); print(res[:5])
