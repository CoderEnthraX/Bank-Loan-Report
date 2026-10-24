import sys,glob
from PIL import Image
p=glob.glob('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'+sys.argv[1]+'-image.*')[0]
im=Image.open(p).convert('RGB'); px=im.load()
x0,y0,x1,y1=map(int,sys.argv[2:6])
cols=[]
for x in range(x0,x1):
    r_=g_=0
    for y in range(y0,y1):
        r,g,b=px[x,y]
        if 28<r<70 and r-g>=10 and r-b>=6 and g<45: r_+=1
        if 25<g<70 and g-r>=12 and g-b>=4 and r<40: g_+=1
    cols.append((x,r_,g_))
# print runs of columns with r_>=8 or g_>=8
def runs(idx):
    out=[];s=None
    for x,r_,g_ in cols:
        v=(r_ if idx==1 else g_)>=8
        if v and s is None: s=x
        if not v and s is not None: out.append((s,x-1)); s=None
    if s is not None: out.append((s,cols[-1][0]))
    return out
print('redfill',runs(1)); print('greenfill',runs(2))
