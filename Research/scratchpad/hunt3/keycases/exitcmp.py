import sys, json, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit'); sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/xl')
from load_xl import load
from engine2 import prepare
from engine import rma
inp = next((json.loads(x) for x in sys.argv[1:] if x.startswith('{')), {"dayStopR":0})
spec = importlib.util.spec_from_file_location('m', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/keycases/kc.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
for sym in ('SENSEX','CRUDE'):
    P = prepare(sym); T = P['T']; idx = {t:i for i,t in enumerate(T)}; H=P['H']; L=P['L']
    tr = M.run(sym, inp)
    for x in load():
        if x['sym']!=sym: continue
        f = idx.get(x['date']+' '+x['tin']); e = idx.get(x['date']+' '+x['tout']) if x['tout'] else None
        m = next((m for m in tr if m['dir']==x['d'] and f is not None and abs(m['fill']-f)<=1), None)
        # where does logged TP4 / SL get hit from f on
        d=x['d']; risk=abs(x['entry']-x['stop']); t4=x['entry']+d*2*risk
        hit=None
        if f is not None:
            for j in range(f, min(f+300,len(T))):
                sl = L[j]<=x['stop'] if d>0 else H[j]>=x['stop']
                tp = H[j]>=t4 if d>0 else L[j]<=t4
                if (sl and j>f) or tp: hit=(T[j][5:], 'SL' if sl and j>f else 'TP4'); break
        print(sym, x['n'], x['date'][5:], x['tin'], x['tout'], x['maxtp'], '| logged-levels first hit', hit, '| model', (T[m['exit']][5:] if m and m['exit'] is not None else None, m['res'] if m else None) if m else 'none')
