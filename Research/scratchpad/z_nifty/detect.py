"""Detect candles in a screenshot: python3 -I detect.py image x0 y0 x1 y1"""
import sys, glob
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
src=sys.argv[1]
src=glob.glob(U+src+'*')[0]
x0,y0,x1,y1=map(int,sys.argv[2:6])
im=np.asarray(Image.open(src).convert('RGB')).astype(int)
R,G,B=im[:,:,0],im[:,:,1],im[:,:,2]
red=(R>170)&(G<90)&(B<110)
grn=(G>110)&(R<80)&(B>70)&(B<150)&(G-B>15)
m=(red|grn)
sub=m[y0:y1,x0:x1].copy()
# remove long horizontal runs (box borders)
H,W=sub.shape
for y in range(H):
    row=sub[y]
    x=0
    while x<W:
        if row[x]:
            s=x
            while x<W and row[x]: x+=1
            if x-s>14: row[s:x]=False
        else: x+=1
col=sub.sum(axis=0)
# group columns
groups=[];x=0
while x<W:
    if col[x]>=2:
        s=x
        while x<W and col[x]>=2: x+=1
        groups.append((s,x-1))
    else: x+=1
for s,e in groups:
    ys=np.where(sub[:,s:e+1].any(axis=1))[0]
    # color of body
    r=red[y0:y1,x0+s:x0+e+1].sum(); g=grn[y0:y1,x0+s:x0+e+1].sum()
    # wick center: column with the longest extent
    ext=[(np.where(sub[:,c])[0]) for c in range(s,e+1)]
    print(f"{x0+(s+e)/2:7.1f} w{e-s+1:02d} top {y0+ys.min():4d} bot {y0+ys.max():4d} {'R' if r>g else 'G'}")
