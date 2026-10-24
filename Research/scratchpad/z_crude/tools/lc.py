# precise line center: lc.py IMG x1,x2,.. yc halfwin  -> weighted center using |pixel - local background| (bg = median of window edges)
import sys, glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB')
xs=[int(v) for v in sys.argv[2].split(',')]
for spec in sys.argv[3:]:
    yc,h=map(int,spec.split(':'))
    res=[]
    for x in xs:
        ys=list(range(yc-h,yc+h+1))
        px=[im.getpixel((x,y)) for y in ys]
        edge=px[:2]+px[-2:]
        bg=[sorted(p[k] for p in edge)[len(edge)//2] for k in range(3)]
        w=[max(0,sum(abs(p[k]-bg[k]) for k in range(3))-20) for p in px]
        if sum(w)==0: res.append(None); continue
        res.append(round(sum(y*wi for y,wi in zip(ys,w))/sum(w),2))
    vals=[r for r in res if r is not None]
    print(spec, res, 'avg', round(sum(vals)/len(vals),2) if vals else None)
