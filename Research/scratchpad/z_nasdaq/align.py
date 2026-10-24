import sys
# align.py candles.txt bars.txt anchor_x anchor_idx y1 p1 y2 p2 [show]
cf,bf=sys.argv[1],sys.argv[2]; ax=float(sys.argv[3]); ai=int(sys.argv[4])
y1,p1,y2,p2=map(float,sys.argv[5:9]); show=len(sys.argv)>9
k=(p2-p1)/(y2-y1); P=lambda y:p1+(y-y1)*k
C=[]
for l in open(cf).read().split('\n')[1:]:
    f=l.split()
    if len(f)>=6: C.append((float(f[0]),int(f[1]),int(f[2]),f[5]))
B={}
for l in open(bf):
    f=l.split()
    if len(f)>10 and f[0].isdigit(): B[int(f[0])]=(f[1]+' '+f[2],float(f[4]),float(f[6]),float(f[8]),float(f[10]),l.strip()[-14:] if 'MY' in l else '')
best=None
for s100 in range(900,1400):
    s=s100/100; e=0;n=0
    for x,t,b,c in C:
        i=ai+round((x-ax)/s)
        if i in B and t>95:
            e+=min(abs(P(t)-B[i][2]),30)+min(abs(P(b)-B[i][3]),30); n+=1
    if n and (best is None or e/n<best[0]): best=(e/n,s,n)
print('best err/bar %.2f spacing %.2f n %d'%best)
s=best[1]
if show:
    for x,t,b,c in C:
        i=ai+round((x-ax)/s)
        if i in B: print('%7.1f %s  mH %.1f aH %.1f  mL %.1f aL %.1f %s'%(x,B[i][0][5:],P(t),B[i][2],P(b),B[i][3],B[i][5]))
