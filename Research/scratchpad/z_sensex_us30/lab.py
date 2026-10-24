import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB'); px=im.load()
x0,x1,y0,y1=map(int,sys.argv[2:6])
rows=[y for y in range(y0,y1) if sum(1 for x in range(x0,x1) if sum(px[x,y])>450)>2]
grp=[];
for y in rows:
    if grp and y-grp[-1][-1]<=1: grp[-1].append(y)
    else: grp.append([y])
print([ (g[0]+g[-1])/2 for g in grp])
