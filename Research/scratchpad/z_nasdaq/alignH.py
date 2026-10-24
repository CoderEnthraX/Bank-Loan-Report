import sys
cf,bf=sys.argv[1],sys.argv[2]; ax=float(sys.argv[3]); ai=int(sys.argv[4])
y1,p1,y2,p2=map(float,sys.argv[5:9]); show=sys.argv[9] if len(sys.argv)>9 else ''
k=(p2-p1)/(y2-y1); P=lambda y:p1+(y-y1)*k
C=[]
for l in open(cf).read().split('\n')[1:]:
    f=l.split()
    if len(f)>=6: C.append((float(f[0]),int(f[1]),int(f[2])))
B={}
for l in open(bf):
    f=l.split()
    if len(f)>10 and f[0].isdigit(): B[int(f[0])]=(f[2],float(f[6]),float(f[8]),'MY' if 'MY' in l else '')
best=None
for da in range(-3,4):
  for s100 in range(700,1500):
    s=s100/100; e=0;n=0
    for x,t,b in C:
        i=ai+da+round((x-ax)/s)
        if i in B: e+=min(abs(P(t)-B[i][1]),30); n+=1
    if n>20 and (best is None or e/n<best[0]): best=(e/n,s,n,da)
print('err %.2f spacing %.2f n %d shift %d'%best)
s=best[1];da=best[3]
if show:
    lo,hi=map(float,show.split(','))
    for x,t,b in C:
        i=ai+da+round((x-ax)/s)
        if i in B and lo<=x<=hi: print('%7.1f %s mH %.1f aH %.1f mL %.1f aL %.1f %s'%(x,B[i][0],P(t),B[i][1],P(b),B[i][2],B[i][3]))
