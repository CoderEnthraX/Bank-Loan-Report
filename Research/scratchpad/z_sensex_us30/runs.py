import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB'); px=im.load()
x0,y0,x1,y1=map(int,sys.argv[2:6]); minlen=int(sys.argv[6]) if len(sys.argv)>6 else 6
def kind(p):
    r,g,b=p
    if r>170 and g<130 and b>70 and r-g>90: return 'P'
    if g>150 and r<140 and g-r>70 and g-b>20: return 'G'
    if r>200 and g>200 and b>200: return 'W'
    return None
# vertical runs (box sides)
res=[]
for x in range(x0,x1):
    cur=None; s=0
    for y in range(y0,y1+1):
        k=kind(px[x,y]) if y<y1 else None
        if k!=cur:
            if cur in('P','G') and y-s>=minlen: res.append((x,cur,s,y-1))
            cur=k; s=y
for r in res: print(r)
