import numpy as np, itertools
# all in px of each image converted to ticks via scale
# name, scale(px/tick), R_px, ATR10_px, body_px, range_px, entry-to-extreme px, entry-to-open px, close-to-entry px
T={
'A':(4.12,161,94.5,206,243,112,104,102),
'B':(4.15,193,108.6,124,178,79,61,63),
'C':(5.436,357,221.3,318,358,173,159,159),
'D':(3.53,122.5,64.8,85,100,54.5,42.5,42.5),
'E':(3.25,111.5,101.5,98,129,93,66,32),
'F':(3.25,205.5,109.4,142,182,136.5,111.5,30.5),
}
names=['ATR','body','range','d_ext','d_open','d_close']
X=[];y=[]
for k,v in T.items():
    s=v[0]; R=v[1]/s; f=[x/s for x in v[2:]]
    X.append(f); y.append(R)
    print(k, 'R=%.1f'%R, ' '.join('%s=%.1f'%(n,x) for n,x in zip(names,f)), ' R/ATR=%.2f'%(R/f[0]))
X=np.array(X); y=np.array(y)
for i,j in itertools.combinations(range(len(names)),2):
    A=X[:,[i,j]]
    c,res,_,_=np.linalg.lstsq(A,y,rcond=None)
    pred=A@c; err=np.abs(pred-y).max()
    print(names[i],names[j],np.round(c,3),'maxerr %.1f'%err)
for i in range(len(names)):
    A=X[:,[i]]; c,_,_,_=np.linalg.lstsq(A,y,rcond=None); print(names[i],np.round(c,3),'maxerr %.1f'%np.abs(A@c-y).max())
