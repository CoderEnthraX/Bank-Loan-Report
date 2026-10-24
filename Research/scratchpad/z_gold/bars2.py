import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: bars2.py file x0 x1 y0 y1 spacing [bgthr]
f=sys.argv[1]; x0,x1,y0,y1,sp=map(float,sys.argv[2:7]); bgthr=float(sys.argv[7]) if len(sys.argv)>7 else 150
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int); s=im.shape[1]/2000.0
X0,X1,Y0,Y1=int(x0*s),int(x1*s),int(y0*s),int(y1*s)
reg=im[Y0:Y1,X0:X1]
R,G,B=reg[:,:,0],reg[:,:,1],reg[:,:,2]
cyan=(G-R>90)&(B>200)&(G>200)
red=(R>215)&(R-G>50)
body=cyan|red
col=body.sum(0).astype(float)
k=max(3,int(sp*s*0.4))
sm=np.convolve(col,np.ones(k)/k,mode='same')
md=int(sp*s*0.55)
peaks=[]
for i in range(len(sm)):
    lo=max(0,i-md); hi=min(len(sm),i+md+1)
    if sm[i]>2 and sm[i]==sm[lo:hi].max():
        if not peaks or i-peaks[-1]>md: peaks.append(i)
bright=(R+G+B)/3>bgthr
out=[]
for p in peaks:
    xc=x0+p/s
    bw=max(2,int(2.0*s))
    band=body[:,max(0,p-bw):p+bw+1]
    frac=band.mean(1)
    rows=np.where(frac>0.7)[0]
    if len(rows)==0: continue
    # choose largest contiguous run
    runs=[];st=rows[0];pr=rows[0]
    for r in rows[1:]:
        if r!=pr+1: runs.append((st,pr)); st=r
        pr=r
    runs.append((st,pr))
    bt,bb=max(runs,key=lambda t:t[1]-t[0])
    cc=cyan[bt:bb+1,max(0,p-bw):p+bw+1].sum(); rr=red[bt:bb+1,max(0,p-bw):p+bw+1].sum()
    color='C' if cc>rr else 'R'
    # wick: find column within +-1.5px with brightest/colored continuity
    best=None
    for dx in range(-int(1.5*s),int(1.5*s)+1):
        c=p+dx
        colm=(bright[:,c]|body[:,c])
        t=bt
        while t>0 and colm[t-1]: t-=1
        b=bb
        while b<len(colm)-1 and colm[b+1]: b+=1
        if best is None or (b-t)>(best[1]-best[0]): best=(t,b)
    t,b=best
    print('x=%.1f %s body %.1f-%.1f wick %.1f-%.1f'%(xc,color,y0+bt/s,y0+bb/s,y0+t/s,y0+b/s))
