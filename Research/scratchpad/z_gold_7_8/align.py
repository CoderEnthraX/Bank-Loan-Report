import sys, os, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from arp_data import load, find
# args: img x0 y0 x1 y1 yA pA yB pB anchor_time anchor_x(optional guess) 
img=sys.argv[1]; box=sys.argv[2:6]; yA,pA,yB,pB=map(float,sys.argv[6:10]); sym=sys.argv[10]; day=sys.argv[11]
out=subprocess.run(['python3','-I','candles.py',img]+box,capture_output=True,text=True,cwd='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit').stdout.split('\n')
C=[]
for l in out[1:]:
    p=l.split()
    if len(p)>=7 and int(p[6])>=4: C.append((float(p[0]),float(p[1]),float(p[2])))
pr=lambda y: pA+(y-yA)*(pB-pA)/(yB-yA)
R=load(sym)
# spacing via median diff
xs=[c[0] for c in C]; d=sorted(xs[i+1]-xs[i] for i in range(len(xs)-1)); sp=float(sys.argv[12]) if len(sys.argv)>12 else d[len(d)//2]
best=[]
idx0=[r['i'] for r in R if r['t'].startswith(day)][0]
for k in range(idx0-400, idx0+300):
  for off in [0]:
    err=[];n=0
    for x,yt,yb in C:
        j=k+round((x-C[0][0])/sp)
        if j>=len(R): break
        e=abs(pr(yt)-R[j]['h'])+abs(pr(yb)-R[j]['l']); err.append(e)
    if len(err)>len(C)*0.9:
        err.sort(); m=sum(err[:int(len(err)*0.8)])/int(len(err)*0.8)
        best.append((m,k))
best.sort()
print('sp',sp)
for m,k in best[:5]: print(round(m,3), R[k]['t'], 'first candle x', C[0][0])
