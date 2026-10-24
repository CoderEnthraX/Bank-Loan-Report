"""detect candles in an image region. usage: cand.py img x0 x1 y0 y1 p_a y_a p_b y_b"""
import sys, glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
src=glob.glob(U+sys.argv[1]+'*')[0]
x0,x1,y0,y1=map(int,sys.argv[2:6]); pa,ya,pb,yb=map(float,sys.argv[6:10])
im=Image.open(src).convert('RGB'); px=im.load()
def p2(y): return pa+(y-ya)*(pb-pa)/(yb-ya)
def cls(c):
    r,g,b=c
    if r<48 and g>118 and 85<b<145 and g-b>12: return 'G'
    if r>195 and g<90 and b<110: return 'R'
    return None
W=x1-x0; H=y1-y0
m=[[cls(px[x,y]) for x in range(x0,x1)] for y in range(y0,y1)]
# remove horizontal line rows: runs of >=25 same-class px in a row
for yy in range(H):
    row=m[yy]; xx=0
    while xx<W:
        if row[xx]:
            c=row[xx]; s=xx
            while xx<W and row[xx]==c: xx+=1
            if xx-s>=14:
                for k in range(s,xx): row[k]=None
        else: xx+=1
# column profiles
cols=[]
for xx in range(W):
    ys=[yy for yy in range(H) if m[yy][xx]]
    cols.append(ys)
# group columns
groups=[];xx=0
while xx<W:
    if len(cols[xx])>=2:
        s=xx
        while xx<W and len(cols[xx])>=2: xx+=1
        groups.append((s,xx-1))
    else: xx+=1
for s,e in groups:
    ys=[y for k in range(s,e+1) for y in cols[k]]
    gs=sum(1 for k in range(s,e+1) for y in cols[k] if m[y][k]=='G'); rs=len(ys)-gs
    # body: columns with max count
    cnt=[len(cols[k]) for k in range(s,e+1)]
    wsum=sum(cnt); xc=sum((s+i)*c for i,c in enumerate(cnt))/wsum
    top=min(ys)+y0; bot=max(ys)+y0
    print(f"x {x0+s:4d}-{x0+e:4d} c {x0+xc:7.1f} w {e-s+1:2d} {'G' if gs>rs else 'R'} ytop {top} ybot {bot}  hi {p2(top-0.5):9.2f} lo {p2(bot+0.5):9.2f}")
