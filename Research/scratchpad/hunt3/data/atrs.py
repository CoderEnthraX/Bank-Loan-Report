"""RMS deviation of logged risk/1.8 from ATR variants (normal-stop matched trades only) + SENSEX/CRUDE entry offset stats."""
import sys, statistics as stt
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S+'/fit'); sys.path.insert(0, S+'/xl'); sys.path.insert(0, S+'/hunt3/data')
from load_xl import load
from engine2 import prepare
from engine import rma
import dm
fixT = {66: '09:40'}; BAD = {49, 52, 56}  # stop-rule mismatches (not ATR)
def sma(x, n): return [None if i < n-1 else sum(x[i-n+1:i+1])/n for i in range(len(x))]
def ema(x, n):
    o=[None]*len(x); a=2/(n+1); s=None
    for i,v in enumerate(x):
        if i<n-1: continue
        s = sum(x[:n])/n if s is None else a*v+(1-a)*s; o[i]=s
    return o
for sym in ('SENSEX', 'CRUDE'):
    P = prepare(sym); T=P['T']; idx={t:i for i,t in enumerate(T)}; tr=P['tr']
    H,L=P['H'],P['L']; hl=[h-l for h,l in zip(H,L)]
    V = {}
    for n in (7,10,12,14,16,20,28): V[f'rma{n}'] = rma(tr,n)
    V['sma14']=sma(tr,14); V['ema14']=ema(tr,14); V['rmaHL14']=rma(hl,14)
    trades = dm.run(sym, {"dayStopR":0}); res={k:[] for k in V}; resf=[]; resp=[]; dE=[]
    for x in load():
        if x['sym']!=sym: continue
        f = idx.get(x['date']+' '+fixT.get(x['n'],x['tin'])); m=None
        for t in trades:
            if t['dir']==x['d'] and f is not None and abs(t['fill']-f)<=1 and (m is None or abs(t['fill']-f)<abs(m['fill']-f)): m=t
        if m is None: continue
        dE.append(x['entry']-m['entry'])
        if m['tight'] or x['n'] in BAD: continue
        lr=abs(x['entry']-x['stop'])/1.8; a=m['arm']
        for k in V: res[k].append(lr/V[k][a]-1)
        resf.append(lr/V['rma14'][m['fill']]-1); resp.append(lr/V['rma14'][a-1]-1)
    rms=lambda v:(sum(e*e for e in v)/len(v))**.5
    print(sym, 'n normal-stop', len(resp), ' RMS rel. error of logR/1.8 vs ATR:', ' '.join(f'{k} {rms(v)*100:.1f}%' for k,v in res.items()), f'| rma14@fill {rms(resf)*100:.1f}% rma14@sig-1 {rms(resp)*100:.1f}%', f"| mean bias rma14 {stt.mean(res['rma14'])*100:+.1f}%")
    print('   entry log-model: n', len(dE), 'mean %+.2f sd %.2f min %+.2f max %+.2f' % (stt.mean(dE), stt.pstdev(dE), min(dE), max(dE)), 'exact(|d|<=0.5):', sum(abs(d)<=0.5 for d in dE))
