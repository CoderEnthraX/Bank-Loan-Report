# print pixel RGB down a column (x) between y0..y1, or along a row
import sys, glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
src=glob.glob(U+sys.argv[1]+'*')[0]
im=Image.open(src).convert('RGB')
mode=sys.argv[2]
if mode=='col':
    x=int(sys.argv[3]); y0=int(sys.argv[4]); y1=int(sys.argv[5])
    for y in range(y0,y1+1): print(y, im.getpixel((x,y)))
else:
    y=int(sys.argv[3]); x0=int(sys.argv[4]); x1=int(sys.argv[5])
    for x in range(x0,x1+1): print(x, im.getpixel((x,y)))
