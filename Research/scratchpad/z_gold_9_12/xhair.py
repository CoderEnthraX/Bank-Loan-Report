import sys
from PIL import Image
im=Image.open('/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/%s-image.png'%sys.argv[1]).convert('RGB')
best=[]
for x in range(80,1400):
    n=0
    for y in range(300,1000,2):
        r,g,b=im.getpixel((x,y))
        if abs(r-g)<15 and abs(g-b)<15 and 90<r<200: n+=1
    best.append((n,x))
best.sort(reverse=True); print(best[:5])
