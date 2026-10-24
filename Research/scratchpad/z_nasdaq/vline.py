import sys
from PIL import Image
p=sys.argv[1]
if '/' not in p:
    import glob; p=glob.glob('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'+p+'-image.*')[0]
im=Image.open(p).convert('RGB'); W,H=im.size
y0,y1=int(sys.argv[2]),int(sys.argv[3]); x1=int(sys.argv[4]) if len(sys.argv)>4 else W-140
px=im.load()
res=[]
for x in range(x1):
    n=0
    for y in range(y0,y1):
        r,g,b=px[x,y]
        if abs(r-g)<12 and abs(g-b)<12 and 70<r<200: n+=1
    res.append((n,x))
res.sort(reverse=True); print(res[:12])
