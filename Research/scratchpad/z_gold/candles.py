import sys, json
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: candles.py file x0 x1 y0 y1  -> find bar columns & extents
f=sys.argv[1]; x0,x1,y0,y1=map(float,sys.argv[2:6])
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int); s=im.shape[1]/2000.0
X0,X1,Y0,Y1=int(x0*s),int(x1*s),int(y0*s),int(y1*s)
reg=im[Y0:Y1,X0:X1]
R,G,B=reg[:,:,0],reg[:,:,1],reg[:,:,2]
cyan=(G>170)&(B>150)&(R<170)&(G-R>50)
red=(R>190)&(G<160)&(R-G>60)
cnt_c=cyan.sum(0); cnt_r=red.sum(0)
# print per frame-x column counts
for i in range(0,X1-X0):
    xc=x0+i/s
    print('%.1f c=%d r=%d'%(xc,cnt_c[i],cnt_r[i]))
