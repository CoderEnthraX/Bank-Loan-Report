import sys, json, importlib.util; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare; from engine import rma
spec=importlib.util.spec_from_file_location('m',sys.argv[1]); M=importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sym=sys.argv[2]; o=json.loads(sys.argv[3]); days=sys.argv[4:]
P=prepare(sym); T=P['T']; A=rma(P['tr'],14)
for m in M.run(sym,o):
    if T[m['fill']][:10] in days:
        print(T[m['arm']], T[m['fill']], 'L' if m['dir']>0 else 'S', 'e=%.1f s=%.1f r=%.2fATR'%(m['entry'],m['stop'],abs(m['entry']-m['stop'])/A[m['arm']]), 'exit', T[m['exit']] if m['exit'] is not None else None, m['res'], 'T' if m.get('tight') else '', m.get('info'))
