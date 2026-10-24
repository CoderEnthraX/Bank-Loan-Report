# horizontal extent of a colored line at row y: hx.py IMG y x0 x1
import sys, glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB')
y=int(sys.argv[2]); x0=int(sys.argv[3]); x1=int(sys.argv[4])
def colored(p):
    r,g,b=p; return max(r,g,b)-min(r,g,b)>60 or (r>150 and g>110)
xs=[x for x in range(x0,x1+1) if colored(im.getpixel((x,y)))]
# print runs
runs=[];
for x in xs:
    if runs and x==runs[-1][1]+1: runs[-1][1]=x
    else: runs.append([x,x])
print(runs)
