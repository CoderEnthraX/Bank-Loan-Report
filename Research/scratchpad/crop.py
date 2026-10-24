import sys
from PIL import Image, ImageEnhance, ImageFilter
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
def crop(fname, box, out, scale=1.0, sharpen=True):
    im=Image.open(U+fname)
    W,H=im.size; s=W/2000.0
    b=tuple(int(v*s) for v in box)
    c=im.crop(b)
    if scale!=1.0: c=c.resize((int(c.width*scale),int(c.height*scale)),Image.LANCZOS)
    if sharpen:
        c=ImageEnhance.Contrast(c).enhance(1.4); c=c.filter(ImageFilter.SHARPEN)
    c.save(out); print(out, im.size, c.size)
if __name__=='__main__':
    f,x0,y0,x1,y1,out=sys.argv[1:7]; sc=float(sys.argv[7]) if len(sys.argv)>7 else 1.0
    crop(f,(float(x0),float(y0),float(x1),float(y1)),out,sc)
