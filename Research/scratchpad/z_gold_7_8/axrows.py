import sys
from PIL import Image
im=Image.open('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'+sys.argv[1]+'-image.png').convert('RGB');px=im.load()
x0,x1=int(sys.argv[2]),int(sys.argv[3])
rows=[]
for y in range(90,1040):
  n=sum(1 for x in range(x0,x1) if sum(px[x,y])>450)
  rows.append((y,n))
grp=[];cur=[]
for y,n in rows:
  if n>0: cur.append(y)
  elif cur: grp.append(cur);cur=[]
for g in grp:
  if 6<=len(g)<=16: print((g[0]+g[-1])/2, len(g))
