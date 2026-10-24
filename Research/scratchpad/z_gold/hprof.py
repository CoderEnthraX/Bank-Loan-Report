import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: hprof.py file ya yb x0 x1 [thresh]  -> column means in band ya..yb (frame coords)
f=sys.argv[1]; ya,yb,x0,x1=map(float,sys.argv[2:6]); th=float(sys.argv[6]) if len(sys.argv)>6 else 0
im=np.asarray(Image.open(U+f).convert('RGB')).astype(float); s=im.shape[1]/2000.0
reg=im[int(ya*s):int(yb*s), int(x0*s):int(x1*s)]
r=reg[:,:,0].mean(0); g=reg[:,:,1].mean(0); b=reg[:,:,2].mean(0); br=(r+g+b)/3
for i,v in enumerate(br):
    if v>=th: print('%.1f  br=%.0f rgb=(%.0f,%.0f,%.0f)'%(x0+i/s, v, r[i],g[i],b[i]))
