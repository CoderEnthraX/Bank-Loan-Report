import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB'); W,H=im.size
x0,x1,y0,y1=map(int,sys.argv[2:6])
px=im.load()
from collections import Counter
# print color histogram in region
c=Counter()
for x in range(x0,x1):
  for y in range(y0,y1):
    p=px[x,y]; c[(p[0]//16*16,p[1]//16*16,p[2]//16*16)]+=1
for k,v in c.most_common(30): print(k,v)
