import sys,glob
from PIL import Image
p=glob.glob('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'+sys.argv[1]+'-image.*')[0]
im=Image.open(p).convert('RGB'); px=im.load()
x=int(sys.argv[2]); y0,y1=int(sys.argv[3]),int(sys.argv[4])
prev=None
for y in range(y0,y1):
    c=px[x,y]
    if prev is None or max(abs(c[i]-prev[i]) for i in range(3))>25: print(y,c)
    prev=c
