"""axis.py img x0 x1 y0 y1: find text rows (label centres) in the price axis column"""
import sys,glob
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=np.asarray(Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('L')).astype(int)
x0,x1,y0,y1=map(int,sys.argv[2:6])
sub=im[y0:y1,x0:x1]
rows=(sub>110).sum(axis=1)
y=0;H=len(rows)
while y<H:
    if rows[y]>0:
        s=y
        while y<H and rows[y]>0: y+=1
        w=rows[s:y]; c=(np.arange(s,y)*w).sum()/w.sum()
        print('text rows %d-%d centre %.1f  (mid %.1f)'%(y0+s,y0+y-1,y0+c,y0+(s+y-1)/2))
    else: y+=1
