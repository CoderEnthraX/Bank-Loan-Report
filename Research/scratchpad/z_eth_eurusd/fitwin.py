"""fitwin.py IMG SYMBOL x0 y0 x1 y1 'start' 'end'  -> fit candle bodies to data: best (index offset, spacing, price scale)"""
import sys, os, subprocess
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'
sys.path.insert(0,F)
from arp_data import load
import numpy as np
img,sym=sys.argv[1],sys.argv[2]; box=sys.argv[3:7]; a,b=sys.argv[7],sys.argv[8]
out=subprocess.run(['python3','-I',F+'/candles.py',img]+box,capture_output=True,text=True).stdout.split('\n')[1:]
C=[]
for l in out:
    p=l.split()
    if len(p)<7: continue
    x,wt,wb,bt,bb=map(float,p[:5]); C.append((x,wt,wb,bt,bb,p[5],int(p[6])))
D=[r for r in load(sym) if a<=r['t']<=b]
best=None
SL=float(os.environ.get('SL','0'))
xs=np.array([c[0] for c in C])
for sp in np.arange(float(sys.argv[9]) if len(sys.argv)>9 else 7.0, float(sys.argv[10]) if len(sys.argv)>10 else 20.0, 0.02):
    for off in range(len(D)):
        # candle k -> data index off + round((x-x_first)/sp)
        idx=off+np.round((xs-xs[0])/sp).astype(int)
        if idx[-1]>=len(D): break
        Y=[];P=[]
        for c,i in zip(C,idx):
            if c[6]<4: continue
            r=D[i]; Y+= [c[3],c[4]]; P+=[max(r['o'],r['c']),min(r['o'],r['c'])]
        Y=np.array(Y);P=np.array(P)
        A=np.vstack([Y,np.ones_like(Y)]).T
        co,res,_,_=np.linalg.lstsq(A,P,rcond=None)
        if SL: co=np.array([SL,np.median(P-SL*Y)])
        e=np.median(np.abs(A@co-P))
        if co[0]<0 and (best is None or e<best[0]): best=(e,sp,off,co)
e,sp,off,co=best
print('err',e,'spacing',sp,'first candle x',xs[0],'=',D[off]['t'],'price=y*%.8g+%.8g'%tuple(co))
for c in C:
    i=off+int(round((c[0]-xs[0])/sp)); r=D[i]
    print(f"x{c[0]:7.1f} {r['t'][5:]} wt {c[1]*co[0]+co[1]:.5f} wb {c[2]*co[0]+co[1]:.5f} | H {r['h']} L {r['l']}")
