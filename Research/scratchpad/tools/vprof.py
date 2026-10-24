import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# print rows where a thin horizontal line exists: compare with rows +-6 ; column band x0..x1
f=sys.argv[1]; x0,x1,y0,y1=map(int,sys.argv[2:6]); thr=float(sys.argv[6]) if len(sys.argv)>6 else 15
im=np.asarray(Image.open(U+f).convert('RGB')).astype(float)
reg=im[y0:y1,x0:x1]
L=reg.mean(axis=2)
p=np.median(L,axis=1)
G=np.median(reg[...,1],axis=1); R=np.median(reg[...,0],axis=1); B=np.median(reg[...,2],axis=1)
for i in range(6,len(p)-6):
    d=p[i]-0.5*(p[i-6]+p[i+6])
    if d>thr and p[i]==max(p[i-3:i+4]):
        print(y0+i, round(d,1), 'RGB',int(R[i]),int(G[i]),int(B[i]))
