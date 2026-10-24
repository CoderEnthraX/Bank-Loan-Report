# detect trade triangles: blobs of saturated pink (short) or teal/green (long) of triangle size
import sys
from PIL import Image
im=Image.open('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'+sys.argv[1]+'-image.png').convert('RGB');px=im.load()
x0,y0,x1,y1=map(int,sys.argv[2:6])
def k(p):
    r,g,b=p
    if r>200 and 40<g<100 and 85<b<125 and r-g>120: return "S"
    if g>170 and r<100 and 90<b<180 and g-r>100: return "L"
    return None
seen=set();out=[]
for y in range(y0,y1):
  for x in range(x0,x1):
    if (x,y) in seen: continue
    c=k(px[x,y])
    if not c: continue
    st=[(x,y)];seen.add((x,y));pts=[]
    while st:
      a,b=st.pop();pts.append((a,b))
      for da,db in((1,0),(-1,0),(0,1),(0,-1)):
        q=(a+da,b+db)
        if x0<=q[0]<x1 and y0<=q[1]<y1 and q not in seen and k(px[q])==c: seen.add(q);st.append(q)
    if 8<=len(pts)<=200:
      xs=[p[0] for p in pts];ys=[p[1] for p in pts]
      w=max(xs)-min(xs)+1;h=max(ys)-min(ys)+1
      if 3<=w<=16 and 3<=h<=14: out.append((c,(min(xs)+max(xs))/2,(min(ys)+max(ys))/2,w,h,len(pts)))
for o in out: print(o)
