import sys, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/hunt7/stops')
import combo as M
from engine2 import prepare
B={"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
cfgs={'base':B,'ib':dict(B,impBody=50),'full':dict(B,impBody=50,netCurMin=1,netHi=5,curOppMin=1)}
for sym in ['NSE_NIFTY1','MCX_NATURALGAS','CRUDE','SENSEX','NIFTY','GC','EURUSD','NASDAQ','US30','ETH']:
    P=prepare(sym); T=P['T']
    R={k:M.run(sym,v) for k,v in cfgs.items()}
    for a,b in (('base','ib'),('ib','full')):
        ka={(z['fill'],z['dir']):z for z in R[a]}; kb={(z['fill'],z['dir']):z for z in R[b]}
        only_a=[k for k in ka if k not in kb]; only_b=[k for k in kb if k not in ka]
        tdiff=[k for k in ka if k in kb and ka[k]['tight']!=kb[k]['tight']]
        n=len(R[a]);
        print(f"{sym:15s} {a}->{b}: trades {len(R[a])}->{len(R[b])} lost {len(only_a)} new {len(only_b)} tightflip {len(tdiff)}", [T[k[0]][5:]+('L' if k[1]>0 else 'S')+('T' if ka[k]['tight'] else 'n')+'>'+('T' if kb[k]['tight'] else 'n') for k in tdiff][:8])
