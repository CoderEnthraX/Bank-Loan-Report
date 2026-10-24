import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; x0,x1,y0,y1=map(float,sys.argv[2:6])
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int); s=im.shape[1]/2000.0
reg=im[int(y0*s):int(y1*s), int(x0*s):int(x1*s)]
R,G,B=reg[:,:,0],reg[:,:,1],reg[:,:,2]
cyan=(G-R>90)&(B>190)&(G>190)
red=(R>200)&(R-G>45)&(R-B>30)
body=(cyan|red)
col=body.sum(0).astype(float)
# print compact column profile: x, count
out=[]
for i in range(0,len(col)):
    out.append((x0+i/s,int(col[i])))
# find runs where col>th
th=float(sys.argv[6]) if len(sys.argv)>6 else 6
runs=[];inrun=False
for x,c in out:
    if c>th and not inrun: st=x; inrun=True; mx=c
    elif c>th: mx=max(mx,c)
    elif inrun: runs.append((st,x,mx)); inrun=False
if inrun: runs.append((st,out[-1][0],mx))
for r in runs: print('%.1f-%.1f center %.1f width %.1f max %d'%(r[0],r[1],(r[0]+r[1])/2,r[1]-r[0],r[2]))
print('n=',len(runs))
