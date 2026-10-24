import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: candle.py file xc halfbody y0 y1
f=sys.argv[1]; xc=int(sys.argv[2]); hb=int(sys.argv[3]); y0,y1=map(int,sys.argv[4:6])
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)
R,G,B=im[...,0],im[...,1],im[...,2]
cyan=(G>150)&(B>150)&(R<G-40)
red=(R>170)&(R>G+40)
col=cyan|red
def ext(mask,x0,x1,minfrac):
    sub=mask[y0:y1,x0:x1].mean(axis=1)
    rows=np.where(sub>=minfrac)[0]
    if len(rows)==0: return None
    return y0+rows.min(), y0+rows.max()
body=ext(col,xc-hb,xc+hb,0.6)
wick=ext(col,xc-3,xc+4,0.3)
c='cyan' if cyan[y0:y1,xc-hb:xc+hb].sum()>red[y0:y1,xc-hb:xc+hb].sum() else 'red'
print(f"x={xc} {c} body {body} wick {wick}")
