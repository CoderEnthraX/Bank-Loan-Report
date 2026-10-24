B=[]
for l in open('ball.txt'):
    f=l.split()
    if len(f)>12 and f[0].isdigit():
        B.append(dict(t=f[1][5:]+' '+f[2],o=float(f[4]),h=float(f[6]),l=float(f[8]),c=float(f[10]),v=float(f[14])))
T={b['t']:i for i,b in enumerate(B)}
# orig: impulse bar, dir, exact entry
O=[('10-07 21:10','L',31088.2),('10-08 05:35','S',31171.5),('10-08 08:00','L',31208.1),('10-08 08:40','S',31154.75),('10-08 14:25','S',30975.5),('10-08 15:45','S',30964.5),('10-09 04:55','S',30781.75),('10-09 06:00','L',30780.2),('10-09 09:40','L',30896.7),('10-09 11:05','L',30928.35),('10-09 12:50','L',31000.2),('10-12 06:15','S',31006.7),('10-12 11:10','S',30984.1)]
X=[('10-08 13:25','S'),('10-09 07:05','L'),('10-12 05:00','L'),('10-12 08:45','S')]
for N in range(3,13):
    ok=0; bad=[]
    for t,d,e in O:
        i=T[t]; b=B[i]; hh=max(x['h'] for x in B[i-N:i]); ll=min(x['l'] for x in B[i-N:i]); mid=(b['o']+b['c'])/2
        brk = b['c']>hh if d=='L' else b['c']<ll
        r = max(mid,hh) if d=='L' else min(mid,ll)
        if brk and abs(r-e)<0.06: ok+=1
        else: bad.append(t+('' if brk else '(nobrk)'))
    xs=[]
    for t,d in X:
        i=T[t]; b=B[i]; hh=max(x['h'] for x in B[i-N:i]); ll=min(x['l'] for x in B[i-N:i])
        xs.append(t+':'+('brk' if (b['c']>hh if d=='L' else b['c']<ll) else 'no'))
    print(N,ok,bad,xs)
