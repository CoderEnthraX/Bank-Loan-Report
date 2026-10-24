# usage: lines.py IMG x y0 y1  -> classify each pixel row: G(green line) R(red line) W(white/pink line) C(cyan) . other; prints runs with weighted centers
import sys, glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB')
x=int(sys.argv[2]); y0=int(sys.argv[3]); y1=int(sys.argv[4])
def cls(p):
    r,g,b=p
    if r>150 and g>110 and b>110: return 'W'
    if g>120 and r<120 and b<170 and g-r>60: return 'G'
    if r>150 and g<100: return 'R'
    if b>150 and g>150 and r<120: return 'C'
    return '.'
runs=[]; cur=None
for y in range(y0,y1+1):
    c=cls(im.getpixel((x,y)))
    if cur and cur[0]==c and y==cur[2]+1: cur[2]=y; cur[3].append(y)
    else:
        if cur: runs.append(cur)
        cur=[c,y,y,[y]]
runs.append(cur)
for c,a,b,ys in runs:
    if c!='.': print(c, a, b, 'mid', (a+b)/2)
