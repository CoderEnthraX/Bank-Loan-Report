"""vertical profile: vprof.py img x y0 y1 pa ya pb yb [thr]"""
import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB')
x,y0,y1=map(int,sys.argv[2:5]); pa,ya,pb,yb=map(float,sys.argv[5:9]); thr=int(sys.argv[9]) if len(sys.argv)>9 else 90
for y in range(y0,y1):
    c=im.getpixel((x,y))
    if max(c)>thr: print(y, c, f"{pa+(y-ya)*(pb-pa)/(yb-ya):.2f}")
