import sys
from PIL import Image
import numpy as np
def uniform_filter1d(a,n):
    k=np.ones(n)/n; return np.convolve(np.pad(a,(n//2,n-1-n//2),mode="edge"),k,mode="valid")
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; y0,y1=map(int,sys.argv[2:4]); xs=[int(v) for v in sys.argv[4].split(',')]; w=int(sys.argv[5]) if len(sys.argv)>5 else 20
im=np.asarray(Image.open(U+f).convert('L')).astype(float)
for x in xs:
    prof=np.median(im[y0:y1,x-w//2:x+w//2],axis=1)
    hp=prof-uniform_filter1d(prof,25)
    # peaks
    pk=[i for i in range(2,len(hp)-2) if hp[i]>=hp[i-1] and hp[i]>=hp[i+1] and hp[i]>2.0 and hp[i]==max(hp[max(0,i-20):i+20])]
    print(x, [(y0+i, round(hp[i],1)) for i in pk])
