# find faint horizontal grid lines in a column: local maxima of brightness above background
import sys, glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('L')
xs=[int(v) for v in sys.argv[2].split(',')]; y0=int(sys.argv[3]); y1=int(sys.argv[4])
vals=[sum(im.getpixel((x,y)) for x in xs)/len(xs) for y in range(y0,y1+1)]
import statistics
bg=statistics.median(vals)
out=[]
y=0
while y<len(vals):
    if vals[y]>bg+2.5:
        a=y
        while y<len(vals) and vals[y]>bg+1.5: y+=1
        seg=range(a,y); w=[vals[k]-bg for k in seg]
        c=sum((y0+k)*wk for k,wk in zip(seg,w))/sum(w)
        out.append(round(c,2))
    y+=1
print('bg',bg); print(out)
