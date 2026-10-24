import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); thr=int(sys.argv[6]) if len(sys.argv)>6 else 200
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)
reg=im[y0:y1,x0:x1]
# white: all channels high and similar
w=(reg.min(axis=2)>thr)
prof=w.sum(axis=1)
rows=np.where(prof>3)[0]
# cluster
cl=[];start=None;prev=None
for r in rows:
    if start is None: start=r;prev=r;continue
    if r-prev>4: cl.append((start,prev)); start=r
    prev=r
if start is not None: cl.append((start,prev))
for a,b in cl:
    if b-a<8: continue
    seg=w[a:b+1]
    cols=np.where(seg.any(axis=0))[0]
    wts=prof[a:b+1]; cy=(np.arange(a,b+1)*wts).sum()/wts.sum()
    print(f"rows {y0+a}-{y0+b} center {y0+(a+b)/2:.1f} wcenter {y0+cy:.1f} cols {x0+cols.min()}-{x0+cols.max()}")
