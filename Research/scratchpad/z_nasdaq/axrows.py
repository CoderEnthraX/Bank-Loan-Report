import sys
from PIL import Image
im=Image.open(sys.argv[1]).convert('RGB'); x0,x1=int(sys.argv[2]),int(sys.argv[3])
TH=int(sys.argv[4]) if len(sys.argv)>4 else 450
W,H=im.size; rows=[]
for y in range(H):
    n=sum(1 for x in range(x0,x1) if sum(im.getpixel((x,y)))>TH)
    rows.append(n)
y=0;out=[]
while y<H:
    if rows[y]>0:
        s=y
        while y<H and rows[y]>0: y+=1
        if y-s>=5: out.append((s,y-1,(s+y-1)/2))
    y+=1
print(out)
