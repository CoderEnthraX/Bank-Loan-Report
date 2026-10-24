import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: gcrop.py file x0 y0 x1 y1 out scale gridstep  (coords in FULL-RES pixels)
f=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6]); out=sys.argv[6]; sc=float(sys.argv[7]); gs=int(sys.argv[8])
im=Image.open(U+f).convert('RGB')
c=im.crop((x0,y0,x1,y1))
c=ImageEnhance.Contrast(c).enhance(1.3)
c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS)
d=ImageDraw.Draw(c)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14)
except: font=ImageFont.load_default()
gx=(x0//gs+1)*gs
while gx<x1:
    X=(gx-x0)*sc; d.line([(X,0),(X,c.height)],fill=(255,255,0),width=1); d.text((X+2,2),str(gx),fill=(255,255,0),font=font); gx+=gs
gy=(y0//gs+1)*gs
while gy<y1:
    Y=(gy-y0)*sc; d.line([(0,Y),(c.width,Y)],fill=(255,0,255),width=1); d.text((2,Y+1),str(gy),fill=(255,0,255),font=font); gy+=gs
c.save(out); print(out,c.size)
