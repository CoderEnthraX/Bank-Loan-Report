import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
f=sys.argv[1]; xa,xb,y0,y1=map(float,sys.argv[2:6])
im=np.asarray(Image.open(U+f).convert('L')).astype(float); s=im.shape[1]/2000.0
reg=im[int(y0*s):int(y1*s), int(xa*s):int(xb*s)]
p=reg.mean(1)
# detrend
from numpy import convolve
k=31; sm=np.convolve(p,np.ones(k)/k,mode='same')
d=p-sm
# local maxima above threshold
th=float(sys.argv[6]) if len(sys.argv)>6 else 1.5
for i in range(2,len(d)-2):
    if d[i]>th and d[i]==max(d[i-2:i+3]):
        print('%.1f  %.2f'%(y0+i/s, d[i]))
