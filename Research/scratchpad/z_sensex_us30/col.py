import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB'); px=im.load()
x=int(sys.argv[2]); y0,y1=int(sys.argv[3]),int(sys.argv[4])
prev=None
for y in range(y0,y1):
    p=px[x,y]
    if prev is None or max(abs(a-b) for a,b in zip(p,prev))>25: print(y,p)
    prev=p
