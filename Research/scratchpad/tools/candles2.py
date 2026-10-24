import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); minw=int(sys.argv[6]) if len(sys.argv)>6 else 12
cfg=sys.argv[7] if len(sys.argv)>7 else 'a'
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)[y0:y1,x0:x1]
R,G,B=im[...,0],im[...,1],im[...,2]
if cfg=='a':
    cyan=(G>185)&(B>170)&(R<170)&(R<G-50)
    red=(R>215)&(G<185)&(R>G+50)
else:
    exec(open(cfg).read())
out=[]
for name,m in (('CYAN',cyan),('RED',red)):
    # for each column: longest vertical run
    H,W=m.shape
    best=np.zeros(W,int)
    for x in range(W):
        c=m[:,x]; r=0;b=0
        for v in c:
            r=r+1 if v else 0
            if r>b: b=r
        best[x]=b
    isb=best>=6
    runs=[];s=None
    for i,v in enumerate(isb):
        if v and s is None: s=i
        if not v and s is not None: runs.append((s,i-1)); s=None
    if s is not None: runs.append((s,W-1))
    for a,b in runs:
        if b-a+1<minw: continue
        xc=(a+b)//2
        inner=m[:,a+2:b-1]
        frac=inner.mean(axis=1)
        rows=np.where(frac>0.5)[0]
        if len(rows)==0: continue
        segs=[];ss=rows[0];pp=rows[0]
        for r in rows[1:]:
            if r-pp>3: segs.append((ss,pp)); ss=r
            pp=r
        segs.append((ss,pp))
        bt,bb=max(segs,key=lambda t:t[1]-t[0])
        # wick: thin colored line at any column within body x-range
        wc=m[:,a:b+1].any(axis=1)
        t=bt
        while t>1 and (wc[t-1] or wc[t-2]): t-=1
        bo=bb
        while bo<H-2 and (wc[bo+1] or wc[bo+2]): bo+=1
        out.append((x0+xc,name,x0+a,x0+b,y0+bt,y0+bb,y0+t,y0+bo))
for o in sorted(out):
    print("c%d %-4s x%d-%d body %d-%d wick %d-%d"%o)
