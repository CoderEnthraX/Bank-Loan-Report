import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: bars.py file x0 x1 y0 y1 minw maxw [bright]
f=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); minw=int(sys.argv[6]); maxw=int(sys.argv[7]); bt=int(sys.argv[8]) if len(sys.argv)>8 else 165
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)[y0:y1,x0:x1]
R,G,B=im[...,0],im[...,1],im[...,2]
mx=im.max(axis=2); mn=im.min(axis=2)
cyan=(G>175)&(B>160)&(R<175)&(G-R>45)
red=(R>200)&(R-G>50)&(R-B>30)
body=cyan|red
H,W=body.shape
# per column longest run
best=np.zeros(W,int)
for x in range(W):
    c=body[:,x]; r=b=0
    for v in c:
        r=r+1 if v else 0
        b=max(b,r)
    best[x]=b
isb=best>=4
runs=[];s=None
for i,v in enumerate(isb):
    if v and s is None: s=i
    if not v and s is not None: runs.append((s,i-1)); s=None
if s is not None: runs.append((s,W-1))
bright=(mx>bt)&((mx-mn)>18)
res=[]
for a,b in runs:
    w=b-a+1
    if w<minw: continue
    pieces=[(a,b)]
    if w>maxw:
        n=int(round(w/ (maxw*0.9)))
        pieces=[(a+int(i*w/n),a+int((i+1)*w/n)-1) for i in range(n)]
    for a2,b2 in pieces:
        xc=(a2+b2)//2
        inner=body[:,a2+2:b2-1] if b2-a2>5 else body[:,a2:b2+1]
        fr=inner.mean(axis=1)
        rows=np.where(fr>0.5)[0]
        if len(rows)==0: continue
        segs=[];ss=rows[0];pp=rows[0]
        for r in rows[1:]:
            if r-pp>2: segs.append((ss,pp)); ss=r
            pp=r
        segs.append((ss,pp))
        tb,bb=max(segs,key=lambda t:t[1]-t[0])
        col=cyan[tb:bb+1,a2:b2+1].sum()>red[tb:bb+1,a2:b2+1].sum()
        wc=bright[:,max(0,xc-2):xc+3].any(axis=1)
        t=tb
        while t>2 and (wc[t-1] or wc[t-2] or wc[t-3]): t-=1
        bo=bb
        while bo<H-3 and (wc[bo+1] or wc[bo+2] or wc[bo+3]): bo+=1
        res.append((x0+xc,'C' if col else 'R',y0+tb,y0+bb,y0+t,y0+bo))
for r in res: print("x%d %s body %d-%d wick %d-%d range %d"%(r+(r[5]-r[4],)))
