"""vscan.py img x y0 y1 : print pixel colours down a column where they change"""
import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB')
x=int(sys.argv[2]);y0,y1=int(sys.argv[3]),int(sys.argv[4])
prev=None
for y in range(y0,y1):
    p=im.getpixel((x,y))
    if prev is None or max(abs(a-b) for a,b in zip(p,prev))>12:
        print(y,p)
    prev=p
