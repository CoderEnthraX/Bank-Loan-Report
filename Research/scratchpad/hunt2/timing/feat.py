import sys, importlib.util, json
spec = importlib.util.spec_from_file_location('m', sys.argv[1]); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
inp = json.loads(sys.argv[2]); inp['dbg'] = True
from engine2 import prepare
from engine import rma
out = []
for sym in ['CRUDE','ETH','EURUSD','GC','NASDAQ','NIFTY','SENSEX','US30']:
    M.DBG.clear(); tr = M.run(sym, inp); D = {d['i']: d for d in M.DBG}
    P = prepare(sym); T = P['T']; C = P['C']; H=P['H']; L=P['L']; O=P['O']; A = rma(P['tr'], 14)
    for t in tr:
        j = t['arm']; d = D[j]; s = t['dir']
        mom = d['mom']*s
        # alt momentum measures
        m5 = s*(C[j]-C[j-5])/A[j]; m10o = s*(C[j]-O[j-9])/A[j]
        lo10 = min(L[j-10:j]) if s>0 else max(H[j-10:j]); mext = s*(C[j]-lo10)/A[j]
        out.append((sym, T[t['fill']], 'L' if s>0 else 'S', round(mom,2), round(m5,2), round(m10o,2), round(mext,2), round(d['brkL'] if s>0 else d['brkS'],2), round(d['cv']*s,2)))
for o in sorted(out, key=lambda x: x[3]):
    if o[3] < 1.3: print(*o)
