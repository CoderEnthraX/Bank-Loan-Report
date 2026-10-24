import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB'); x0,x1=int(sys.argv[2]),int(sys.argv[3])
rows=[]
for y in range(im.size[1]):
    n=sum(1 for x in range(x0,x1) if sum(im.getpixel((x,y)))>450)
    rows.append(n>0)
s=None
for y,v in enumerate(rows+[False]):
    if v and s is None: s=y
    if not v and s is not None:
        if y-s>=5: print(s,y-1,(s+y-1)/2)
        s=None
