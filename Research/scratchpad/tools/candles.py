import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: candles.py file x0 x1 y0 y1 [minw]
f=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); minw=int(sys.argv[6]) if len(sys.argv)>6 else 12
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)[y0:y1,x0:x1]
R,G,B=im[...,0],im[...,1],im[...,2]
cyan=(G>185)&(B>170)&(R<170)&(R<G-50)
red=(R>215)&(G<185)&(R>G+50)
col=cyan|red
# body columns: column has a vertical run of >=8 colored px
cnt=col.sum(axis=0)
isb=cnt>=8
runs=[];s=None
for i,v in enumerate(isb):
    if v and s is None: s=i
    if not v and s is not None: runs.append((s,i-1)); s=None
if s is not None: runs.append((s,len(isb)-1))
for a,b in runs:
    if b-a+1<minw: continue
    xc=(a+b)//2
    inner=col[:,a+3:b-2] if b-a>8 else col[:,a:b+1]
    frac=inner.mean(axis=1)
    rows=np.where(frac>0.5)[0]
    if len(rows)==0: continue
    # largest contiguous body run
    segs=[];ss=rows[0];pp=rows[0]
    for r in rows[1:]:
        if r-pp>3: segs.append((ss,pp)); ss=r
        pp=r
    segs.append((ss,pp))
    bt,bb=max(segs,key=lambda t:t[1]-t[0])
    isc=cyan[bt:bb+1,a:b+1].sum()>red[bt:bb+1,a:b+1].sum()
    # wick: search at columns near center for colored pixels contiguous with body
    cmask=(cyan if isc else red)
    wc=cmask[:,max(0,xc-4):xc+5].any(axis=1)
    t=bt
    while t>0 and (wc[t-1] or (t>2 and wc[t-2]) ): t-=1
    bo=bb
    while bo<len(wc)-1 and (wc[bo+1] or (bo<len(wc)-2 and wc[bo+2])): bo+=1
    print(f"x {x0+a}-{x0+b} c{x0+xc} {'CYAN' if isc else 'RED '} body {y0+bt}-{y0+bb} wick {y0+t}-{y0+bo}")
