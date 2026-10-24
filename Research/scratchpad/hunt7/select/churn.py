"""churn.py '{base}' '{alt}' [v] : trades removed/added over all symbols"""
import sys, json, importlib.util, os
d=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location('m',os.path.join(d,'sel.py')); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
a=json.loads(sys.argv[1]); b=json.loads(sys.argv[2]); v='v' in sys.argv[3:]
tot=[0,0,0,0,0.0,0.0]
for sym in ('NSE_NIFTY1','MCX_NATURALGAS','CRUDE','SENSEX','NIFTY','GC','EURUSD','NASDAQ','US30','ETH'):
    R=M.eprep(sym)['rows']
    ta=M.run(sym,a); tb=M.run(sym,b)
    ka={(t['fill'],t['dir']):t for t in ta}; kb={(t['fill'],t['dir']):t for t in tb}
    rem=[k for k in ka if k not in kb]; add=[k for k in kb if k not in ka]
    ra=sum(t['res'] or 0 for t in ta); rb=sum(t['res'] or 0 for t in tb)
    print(f"{sym:15s} base {len(ta)} ({ra:+.0f}R) alt {len(tb)} ({rb:+.0f}R) removed {len(rem)} added {len(add)}")
    if v:
        for k in rem: print('    -', R[k[0]]['t'], 'L' if k[1]>0 else 'S', ka[k]['res'])
        for k in add: print('    +', R[k[0]]['t'], 'L' if k[1]>0 else 'S', kb[k]['res'])
    tot=[tot[0]+len(ta),tot[1]+len(tb),tot[2]+len(rem),tot[3]+len(add),tot[4]+ra,tot[5]+rb]
print('TOTAL base %d alt %d removed %d added %d  R %+.0f -> %+.0f'%tuple(tot))
