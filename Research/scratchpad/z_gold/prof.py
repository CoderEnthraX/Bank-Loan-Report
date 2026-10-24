import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: prof.py file xa xb y0 y1 [thresh] -> prints rows (frame coords) where mean brightness peaks
f=sys.argv[1]; xa,xb,y0,y1=map(float,sys.argv[2:6]); th=float(sys.argv[6]) if len(sys.argv)>6 else 0
im=np.asarray(Image.open(U+f).convert('RGB')).astype(float); s=im.shape[1]/2000.0
reg=im[int(y0*s):int(y1*s), int(xa*s):int(xb*s)]
br=reg.mean(axis=(1,2)); r=reg[:,:,0].mean(1); g=reg[:,:,1].mean(1); b=reg[:,:,2].mean(1)
for i,v in enumerate(br):
    if v>=th: print('%.1f  br=%.0f rgb=(%.0f,%.0f,%.0f)'%(y0+i/s, v, r[i],g[i],b[i]))
