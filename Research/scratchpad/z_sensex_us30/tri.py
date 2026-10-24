import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB'); px=im.load()
x0,y0,x1,y1=map(int,sys.argv[2:6])
def pk(p): r,g,b=p; return r>200 and g<110 and b>85
def gr(p): r,g,b=p; return g>150 and r<120 and b>100 and g-b<70 and g-b>10
seen=set(); out=[]
for kind,f in (('pinkTri',pk),('greenTri',gr)):
  for y in range(y0,y1):
    for x in range(x0,x1):
      if (x,y) in seen or not f(px[x,y]): continue
      st=[(x,y)]; seen.add((x,y)); pts=[]
      while st:
        a,b=st.pop(); pts.append((a,b))
        for da,db in ((1,0),(-1,0),(0,1),(0,-1)):
          q=(a+da,b+db)
          if x0<=q[0]<x1 and y0<=q[1]<y1 and q not in seen and f(px[q]): seen.add(q); st.append(q)
      xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
      w=max(xs)-min(xs)+1; h=max(ys)-min(ys)+1
      if 15<=len(pts)<=200 and 5<=w<=16 and 4<=h<=14: out.append((kind,round(sum(xs)/len(xs),1),min(ys),max(ys),len(pts)))
for o in out: print(o)
