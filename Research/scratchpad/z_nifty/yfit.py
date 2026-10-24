"""fit y calibration from candle bodies.
usage: yfit.py img ax ai sp i_from i_to y0 y1 [exclude ranges i:i,...]
ax = x of bar index ai, sp = px/bar. Body rows detected at columns xc-2..xc+2."""
import sys,glob,csv
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB'); px=im.load()
ax,ai,sp=float(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]); i0,i1,y0,y1=map(int,sys.argv[5:9])
F='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/data/NSE_DLY_NIFTY.csv'
rows=list(csv.DictReader(open(F)))
def isG(c): r,g,b=c; return r<60 and g>110 and 80<b<150 and g-b>10
def isR(c): r,g,b=c; return r>190 and g<100 and b<120
pts=[]
for i in range(i0,i1+1):
    r=rows[i]; o,h,l,c=(float(r[k]) for k in ('open','high','low','close'))
    xc=round(ax+(i-ai)*sp); f=isG if c>=o else isR
    body=[y for y in range(y0,y1) if sum(1 for dx in (-2,-1,0,1,2) if f(px[xc+dx,y]))>=4]
    if not body: print(i,r['time'][5:16],'no body'); continue
    # take the longest contiguous run
    runs=[];s=body[0];p=body[0]
    for y in body[1:]:
        if y!=p+1: runs.append((s,p)); s=y
        p=y
    runs.append((s,p)); s,e=max(runs,key=lambda t:t[1]-t[0])
    pts.append((i,r['time'][5:16],max(o,c),min(o,c),s,e+1))
# least squares on both edges: y = a + b*price
X=[];Y=[]
for i,t,hi,lo,s,e in pts:
    if abs(hi-lo)<1.0: continue
    X+= [hi,lo]; Y+=[s,e]
def lsq(X,Y):
    n=len(X); mx=sum(X)/n; my=sum(Y)/n
    b=sum((x-mx)*(y-my) for x,y in zip(X,Y))/sum((x-mx)**2 for x in X); return my-b*mx,b
a,b=lsq(X,Y)
for it in range(6):
    keep=[(x,y) for x,y in zip(X,Y) if abs(y-(a+b*x))< (6 if it<2 else 2.0)]
    a,b=lsq([k[0] for k in keep],[k[1] for k in keep])
n=len(keep)
print(f"fit: y = {a:.3f} + {b:.6f}*p  -> px/pt {-b:.4f}; n={n}")
res=[]
for i,t,hi,lo,s,e in pts:
    r1=s-(a+b*hi); r2=e-(a+b*lo); res+= [r1,r2]
    print(f"{i} {t} body {hi:.2f}/{lo:.2f} y {s}-{e}  resid {r1:+.2f} {r2:+.2f}")
import statistics
rr=[x for x in res if abs(x)<2]; print('inlier resid mean %.3f sd %.3f n %d'%(statistics.mean(rr),statistics.pstdev(rr),len(rr)))
print(f"price(y) = {-a/b:.3f} + y*{1/b:.6f}")
