import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB'); W,H=im.size
x0,x1,y0,y1=map(int,sys.argv[2:6])
px=im.load()
def cls(p):
    r,g,b=p
    if g>110 and r<110 and b>80 and g>r+50: return 'G'
    if r>180 and g<110 and b<120 and r>g+90: return 'R'
    return None
cols={}
for x in range(x0,x1):
    runs=[];cur=None
    for y in range(y0,y1):
        c=cls(px[x,y])
        if c and cur and cur[0]==c and cur[2]==y-1: cur[2]=y
        else:
            if c: cur=[c,y,y]; runs.append(cur)
            else: cur=None
    runs=[r for r in runs if r[2]-r[1]>=2]
    if runs: cols[x]=runs
# group columns
xs=sorted(cols)
groups=[];g=[]
for x in xs:
    if g and x-g[-1]>1: groups.append(g); g=[]
    g.append(x)
if g: groups.append(g)
for g in groups:
    allr=[r for x in g for r in cols[x]]
    col=max(set(r[0] for r in allr), key=lambda c: sum(r[2]-r[1] for r in allr if r[0]==c))
    rr=[r for r in allr if r[0]==col]
    top=min(r[1] for r in rr); bot=max(r[2] for r in rr)
    # body: columns widest
    print(f"x {g[0]}-{g[-1]} c{(g[0]+g[-1])/2:.1f} {col} top {top} bot {bot} w{len(g)}")
