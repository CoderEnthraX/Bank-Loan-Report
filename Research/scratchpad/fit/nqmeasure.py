import sys, re
sys.path.insert(0,'.')
from arp_data import load, find
import numpy as np
# calib from analyst alignment file: x -> time, wick y -> actual H/L
A=[];Y=[];P=[]
cf='../z_nasdaq/c_f5f38768.txt'; af='../z_nasdaq/a_f5.txt'
C={}
for l in open(cf).read().split('\n')[1:]:
    f=l.split()
    if len(f)>=6: C[float(f[0])]=(int(f[1]),int(f[2]))
for l in open(af):
    m=re.match(r'\s*([\d.]+) (\S+ \S+)\s+mH \S+ aH (\S+)\s+mL \S+ aL (\S+)',l)
    if m:
        x=float(m.group(1)); A.append((x,'2026-'+m.group(2)))
        if x in C: Y+= [C[x][0],C[x][1]]; P+=[float(m.group(3)),float(m.group(4))]
Y=np.array(Y);P=np.array(P)
for it in range(3):
    k,b=np.polyfit(Y,P,1); r=np.abs(P-(k*Y+b)); keep=r<np.percentile(r,70); Y,P=Y[keep],P[keep]
print('price = %.5f*y + %.2f'%(k,b))
pr=lambda y:k*y+b
xs=np.array([a[0] for a in A])
def tm(x): return A[int(np.argmin(np.abs(xs-x)))][1]
rows=load('NASDAQ')
for name,x0,x1,top,ent,bot,d in [('t1',324,389,702,760,881,-1),('t2',469,513,676,765,809,1),('t3',959,1036,372,500,565,1),('t4',1148,1293,302,429,493,1),('t5',1383,1527,102,266,348,1)]:
    e=pr(ent); s=pr(bot) if d==1 else pr(top); t4=pr(top) if d==1 else pr(bot)
    print(name,'dir',d,'fill',tm(x0),'end',tm(x1),'entry %.1f stop %.1f tp4 %.1f R %.1f  R(tp4) %.1f'%(e,s,t4,abs(e-s),abs(t4-e)/2))
