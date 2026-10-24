import sys
N=int(sys.argv[1]); K=int(sys.argv[2]) if len(sys.argv)>2 else 4
B=[]
for l in open('ball.txt'):
    f=l.split()
    if len(f)>12 and f[0].isdigit():
        B.append(dict(t=f[1][5:]+' '+f[2],o=float(f[4]),h=float(f[6]),l=float(f[8]),c=float(f[10]),v=float(f[14]),my=('MY' in l)))
orig={'10-07 21:25','10-08 05:40','10-08 08:05','10-08 08:50','10-08 14:30','10-08 15:50','10-09 05:00','10-09 06:05','10-09 09:45','10-09 11:10','10-09 12:55','10-12 06:20','10-12 11:15'}
found=set()
for i in range(N,len(B)-1):
    b=B[i]; hh=max(x['h'] for x in B[i-N:i]); ll=min(x['l'] for x in B[i-N:i]); mid=(b['o']+b['c'])/2
    for d in ('L','S'):
        if d=='L' and b['c']>hh and b['c']>b['o']: e=max(mid,hh)
        elif d=='S' and b['c']<ll and b['c']<b['o']: e=min(mid,ll)
        else: continue
        fill=None
        for j in range(i+1,min(i+1+K,len(B))):
            if (d=='L' and B[j]['l']<=e) or (d=='S' and B[j]['h']>=e): fill=j;break
        if fill is None: continue
        ft=B[fill]['t']; tag='ORIG' if ft in orig else ''
        if tag: found.add(ft)
        vw='abv' if b['c']>b['v'] else 'blw'; ov='abv' if b['o']>b['v'] else 'blw'
        print(d,b['t'],'e=%.2f'%e,'fill',ft,tag,'MY' if B[fill]['my'] else '','body %.1f'%abs(b['c']-b['o']),'O',ov,'C',vw)
print('orig not found:',sorted(orig-found))
