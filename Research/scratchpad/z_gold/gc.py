import sys, math
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: gc.py file x0 y0 x1 y1 out scale gridstep  (coords in 2000-wide frame; scale = out px per frame unit)
f,x0,y0,x1,y1,out=sys.argv[1:7]; k=float(sys.argv[7]); gs=float(sys.argv[8])
x0,y0,x1,y1=map(float,(x0,y0,x1,y1))
im=Image.open(U+f).convert('RGB'); W,H=im.size; s=W/2000.0
c=im.crop((int(x0*s),int(y0*s),int(x1*s),int(y1*s)))
c=c.resize((int((x1-x0)*k),int((y1-y0)*k)),Image.LANCZOS)
c=ImageEnhance.Contrast(c).enhance(1.3)
d=ImageDraw.Draw(c)
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
except: font=ImageFont.load_default()
g=math.ceil(x0/gs)*gs
while g<x1:
    X=(g-x0)*k; d.line([(X,0),(X,c.height)],fill=(255,255,0),width=1); d.text((X+2,2),('%g'%g),fill=(255,255,0),font=font); g+=gs
g=math.ceil(y0/gs)*gs
while g<y1:
    Y=(g-y0)*k; d.line([(0,Y),(c.width,Y)],fill=(255,160,0),width=1); d.text((2,Y+1),('%g'%g),fill=(255,160,0),font=font); g+=gs
c.save(out); print(out,c.size)
