import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: colrun.py file xa xb y0 y1 color(c/r)   -> for band xa..xb, rows where >50% px colored; and any-colored
f=sys.argv[1]; xa,xb,y0,y1=map(int,sys.argv[2:6]); cc=sys.argv[6]
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int)[y0:y1,xa:xb]
R,G,B=im[...,0],im[...,1],im[...,2]
if cc=='c': m=(G>175)&(B>160)&(R<G-45)
elif cc=='r': m=(R>205)&(R>G+45)
elif cc=='w': m=(R>200)&(G>200)&(B>200)
fr=m.mean(axis=1)
def runs(idx):
    if len(idx)==0: return []
    s=idx[0];p=idx[0];o=[]
    for r in idx[1:]:
        if r-p>2: o.append((y0+s,y0+p)); s=r
        p=r
    o.append((y0+s,y0+p)); return o
print('>50%:',runs(np.where(fr>0.5)[0]))
print('>0  :',runs(np.where(fr>0)[0]))
