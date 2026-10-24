"""horizontal profile: hprof.py img y x0 x1 [thr]"""
import sys,glob
from PIL import Image
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
im=Image.open(glob.glob(U+sys.argv[1]+'*')[0]).convert('RGB')
y,x0,x1=map(int,sys.argv[2:5]); thr=int(sys.argv[5]) if len(sys.argv)>5 else 80
print(' '.join(f"{x}:{im.getpixel((x,y))}" for x in range(x0,x1) if max(im.getpixel((x,y)))>thr))
