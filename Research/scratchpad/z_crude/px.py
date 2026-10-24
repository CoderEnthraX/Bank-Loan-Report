import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB'); px=im.load()
mode=sys.argv[2]
if mode=='col':  # print column x from y0..y1
    x=int(sys.argv[3]); y0,y1=int(sys.argv[4]),int(sys.argv[5])
    for y in range(y0,y1): print(y, px[x,y])
else:
    y=int(sys.argv[3]); x0,x1=int(sys.argv[4]),int(sys.argv[5])
    for x in range(x0,x1): print(x, px[x,y])
