B=[]
for l in open('ball.txt'):
    f=l.split()
    if len(f)>12 and f[0].isdigit():
        B.append(dict(t=f[1][5:]+' '+f[2],o=float(f[4]),h=float(f[6]),l=float(f[8]),c=float(f[10]),v=float(f[14])))
T={b['t']:i for i,b in enumerate(B)}
tr=[0]+[max(B[i]['h'],B[i-1]['c'])-min(B[i]['l'],B[i-1]['c']) for i in range(1,len(B))]
atr=[0]*len(B); a=tr[1]
for i in range(1,len(B)): a=(a*13+tr[i])/14; atr[i]=a
R={'10-07 21:10':57.7,'10-08 05:35':22.6,'10-08 08:00':29.9,'10-08 08:40':31.1,'10-08 14:25':44.7,'10-08 15:45':41.0,'10-09 04:55':26.4,'10-09 06:00':19.5,'10-09 09:40':28.4,'10-09 11:05':28.1,'10-09 12:50':36.4,'10-12 06:15':29.2,'10-12 11:10':30.1}
for t in list(R)+['10-08 13:25','10-09 07:05','10-12 05:00','10-12 08:45']:
    i=T[t]; b=B[i]; body=abs(b['c']-b['o']); rng=b['h']-b['l']
    print(t,'body %.1f rng %.1f atr %.1f body/atr %.2f rng/atr %.2f'%(body,rng,atr[i],body/atr[i],rng/atr[i]), 'R %s R/atr %.2f'%(R.get(t,'-'),R[t]/atr[i] if t in R else 0), 'c-vwap %.1f'%(b['c']-b['v']), 'o-vwap %.1f'%(b['o']-b['v']))
