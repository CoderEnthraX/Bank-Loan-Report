import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); thr=int(sys.argv[6]) if len(sys.argv)>6 else 200; gap=int(sys.argv[7]) if len(sys.argv)>7 else 25
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)
reg=im[y0:y1,x0:x1]
w=(reg.min(axis=2)>thr)
prof=w.sum(axis=0)
cols=np.where(prof>1)[0]
cl=[];start=None;prev=None
for r in cols:
    if start is None: start=r;prev=r;continue
    if r-prev>gap: cl.append((start,prev)); start=r
    prev=r
if start is not None: cl.append((start,prev))
for a,b in cl:
    rr=np.where(w[:,a:b+1].any(axis=1))[0]
    print(f"cols {x0+a}-{x0+b} center {x0+(a+b)/2:.1f} rows {y0+rr.min()}-{y0+rr.max()}")
