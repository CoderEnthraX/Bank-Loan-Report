import sys
from PIL import Image
import numpy as np
U='/root/.claude/uploads/21ed2550-acec-5cf1-bf01-a24cbf22fe18/'
# usage: bars.py file x0 x1 y0 y1 spacing
f=sys.argv[1]; x0,x1,y0,y1,sp=map(float,sys.argv[2:7])
im=np.asarray(Image.open(U+f).convert('RGB')).astype(int); s=im.shape[1]/2000.0
X0,X1,Y0,Y1=int(x0*s),int(x1*s),int(y0*s),int(y1*s)
reg=im[Y0:Y1,X0:X1]
R,G,B=reg[:,:,0],reg[:,:,1],reg[:,:,2]
br=(R+G+B)/3
cyan=(G-R>60)&(B>170)&(G>180)
red=(R>200)&(R-G>35)&(R-B>25)
body=cyan|red
col=body.sum(0).astype(float)
# smooth
k=max(3,int(sp*s*0.5)); 
sm=np.convolve(col,np.ones(k)/k,mode='same')
# peaks
md=int(sp*s*0.6)
peaks=[]
for i in range(len(sm)):
    lo=max(0,i-md); hi=min(len(sm),i+md+1)
    if sm[i]>3 and sm[i]==sm[lo:hi].max():
        if not peaks or i-peaks[-1]>md: peaks.append(i)
for p in peaks:
    xc=x0+p/s
    # body: rows where >=60% of band +-2.5px is colored
    bw=int(2.5*s)
    band=body[:,max(0,p-bw):p+bw+1]
    frac=band.mean(1)
    rows=np.where(frac>0.6)[0]
    color='C' if cyan[:,max(0,p-bw):p+bw+1].sum()>red[:,max(0,p-bw):p+bw+1].sum() else 'R'
    # wick: bright or colored pixels in narrow band +-1px
    nb=max(1,int(0.8*s))
    nband=(body|(br>165))[:,p-nb:p+nb+1].mean(1)>0.5
    # find contiguous segment containing body
    if len(rows)==0:
        print('%.1f %s no body'%(xc,color)); continue
    bt,bb=rows.min(),rows.max()
    # extend up
    t=bt
    while t>0 and nband[t-1]: t-=1
    b=bb
    while b<len(nband)-1 and nband[b+1]: b+=1
    print('x=%.1f %s body %.1f-%.1f  wick %.1f-%.1f'%(xc,color,y0+bt/s,y0+bb/s,y0+t/s,y0+b/s))
