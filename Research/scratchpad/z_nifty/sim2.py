import sys, math
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine import prepare, rma, rtick, DEFAULT
P=prepare('NIFTY'); rows=P['rows']; ts=[r['t'] for r in rows]
# HTF 60m EMA20 confirmed bias
def htf_ema(mins=60,n=20):
    keys=[];closes=[];last={}
    for i,r in enumerate(rows):
        h,m=int(r['t'][11:13]),int(r['t'][14:16]); b=r['t'][:10]+'-%03d'%((h*60+m-555)//mins)
        if not keys or keys[-1]!=b: keys.append(b); closes.append(r['c'])
        else: closes[-1]=r['c']
        last[i]=len(keys)-1
    k=2/(n+1); e=[];s=None
    for c in closes: s=c if s is None else s+k*(c-s); e.append(s)
    return [e[last[i]-1] if last[i]>0 else None for i in range(len(rows))]
HE=htf_ema()
def run(rearm=True, half_ctr=False, maxloss=None, log=False):
    c=dict(DEFAULT); mt=P['mt']; atr=rma(P['tr'],14); L=c['structLen']
    st=0; armBar=fillBar=lastExit=None; lim=stp=t4=None; dayFills=0; dayLoss=0; trades=[]; cur=None
    for i,r in enumerate(rows):
        if P['daystart'][i]: dayFills=0; dayLoss=0
        if abs(st)==2 and i>fillBar:
            isL=st==2; sh=r['l']<=stp if isL else r['h']>=stp; th=r['h']>=t4 if isL else r['l']<=t4
            if sh or th:
                cur.update(exit=i,res=-1.0 if sh else 2.0); lastExit=i; st=0
                if sh: dayLoss+=1
        if abs(st)==1 and i>armBar:
            isL=st==1; touched=r['l']<=lim if isL else r['h']>=lim
            if touched and dayFills<c['maxFills']:
                st=2 if isL else -2; fillBar=i; dayFills+=1
                cur=dict(dir=1 if isL else -1,arm=armBar,fill=i,entry=lim,stop=stp,t4=t4,exit=None,res=None); trades.append(cur)
                if (r['l']<=stp if isL else r['h']>=stp): cur.update(exit=i,res=-1.0); lastExit=i; st=0; dayLoss+=1
            elif i-armBar>=c['retest']: st=0
        if i<L+1 or atr[i] is None: continue
        cooled=lastExit is None or i-lastExit>=c['cooldown']
        if not (abs(st)!=2 and cooled and dayFills<c['maxFills']): continue
        if not rearm and abs(st)==1: continue
        if maxloss is not None and dayLoss>=maxloss: continue
        ph=max(x['h'] for x in rows[i-L:i]); pl=min(x['l'] for x in rows[i-L:i])
        rng=r['h']-r['l']; body=abs(r['c']-r['o']); mid=(r['o']+r['c'])/2; vw=r['vwap']
        big=rng>0 and rng>=c['dispAtr']*atr[i] and body/rng*100>=c['bodyPct']
        bull=r['c']>r['o'] and r['c']>ph and big and (r['h']-r['c'])/rng*100<=c['closePct'] and r['c']>vw
        bear=r['c']<r['o'] and r['c']<pl and big and (r['c']-r['l'])/rng*100<=c['closePct'] and r['c']<vw
        if not(bull or bear): continue
        d=1 if bull else -1
        entry=max(mid,ph) if bull else min(mid,pl)
        mult=c['stopAtr']
        if half_ctr and HE[i] is not None and d*(r['c']-HE[i])<0: mult/=2
        stop=entry-d*mult*atr[i]; rk=d*(entry-stop)
        if log and '2026-10-01'<=r['t']<='2026-10-12 23:59': print('   arm',r['t'],'L' if d>0 else 'S','entry %.2f'%entry, 'replacing' if abs(st)==1 else '')
        st=d; armBar=i; lim=rtick(entry,mt); stp=rtick(stop,mt); t4=rtick(lim+d*2*rk,mt)
    return trades
def show(tr,label):
    print('==',label)
    for t in tr:
        if '2026-10-01'<=rows[t['fill']]['t']<='2026-10-12 23:59':
            print('  %s fill %s entry %.2f stop %.2f exit %s res %s'%('L' if t['dir']>0 else 'S',rows[t['fill']]['t'][5:],t['entry'],t['stop'],rows[t['exit']]['t'][5:] if t['exit'] is not None else None,t['res']))
args=sys.argv[1:]
show(run(rearm='norearm' not in args, half_ctr='half' in args, maxloss=2 if 'maxloss2' in args else None, log='log' in args),' '.join(args))
