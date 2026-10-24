"""Crop a screenshot in NATIVE pixel coordinates and upscale.
Usage: python3 -I crop2.py <image-id e.g. 37da0475 | full path> x0 y0 x1 y1 out.png [scale=2]
1920x1080 PNG screenshots: use pixel coords as seen.  4096x3072 photos (*.jpg): coords are native too."""
import sys, os, glob
from PIL import Image, ImageEnhance
U = '/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
src = sys.argv[1]
if not os.path.exists(src):
    m = glob.glob(U + src + '*')
    src = m[0]
x0, y0, x1, y1 = map(int, sys.argv[2:6]); out = sys.argv[6]; sc = float(sys.argv[7]) if len(sys.argv) > 7 else 2.0
im = Image.open(src).convert('RGB'); c = im.crop((x0, y0, x1, y1))
c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
ImageEnhance.Contrast(c).enhance(1.25).save(out); print(out, im.size, '->', c.size)
