import sys, os, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0,S+'/fit'); sys.path.insert(0,S+'/xl')
from engine2 import prepare
spec=importlib.util.spec_from_file_location('m',S+'/hunt2/daystate/ds.py'); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
import glob,json
syms=["ETH","US30","GC","EURUSD","NASDAQ"]
print(syms)
for sym in syms+['NIFTY','SENSEX','CRUDE']:
    try: P=prepare(sym)
    except Exception as e: print(sym,'ERR',e); continue
    T=P['T']
    a=[(T[m['fill']],m['dir'],m['res']) for m in M.run(sym,{})]
    b=[(T[m['fill']],m['dir'],m['res']) for m in M.run(sym,{'dsMode':'none'})]
    sa,sb=set(a),set(b)
    print(sym,len(a),len(b),'only base',sorted(sa-sb)[:8],'only nods',len(sb-sa), sorted(sb-sa)[:6])
print('=== window overlap')
import gtscore
tr,win=gtscore.load_gt(S+'/gt/final')
print(win[:2]); print(tr[:2])
cnt=0
for sym in ["ETH","US30","GC","EURUSD","NASDAQ","NIFTY","SENSEX","CRUDE"]:
    P=prepare(sym);T=P['T']
    a={(T[m['fill']],m['dir']) for m in M.run(sym,{})}
    b={(T[m['fill']],m['dir']) for m in M.run(sym,{'dsMode':'none'})}
    for t,d in sorted(a^b):
        for w in win:
            if w['sym']==sym and w['a']<=t<=w['b']:
                print('IN WINDOW',sym,t,d,'base' if (t,d) in a else 'nods',w['a'],w['b']); cnt+=1
print('in-window diffs',cnt)
from collections import Counter
print(Counter(w['sym'] for w in win))
for w in win:
    if w['sym']=='US30' and '10-13'<=w['a'][5:10]<='10-14' or (w['sym']=='US30' and w['b'][5:10]>='10-13'): print(w)
