"""print model trades: python3 -I mt.py SYM from to ['{json}'] [module]"""
import sys, json, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
from engine import rma
sym, a, b = sys.argv[1:4]
inp = next((json.loads(x) for x in sys.argv[4:] if x.startswith('{')), {})
modp = next((x for x in sys.argv[4:] if x.endswith('.py')), '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/keycases/kc.py')
spec = importlib.util.spec_from_file_location('m', modp); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
P = prepare(sym); T = P['T']; A = rma(P['tr'], 14)
for m in M.run(sym, inp):
    if a <= T[m['arm']] <= b:
        print(T[m['arm']], '->', T[m['fill']][11:], 'L' if m['dir'] > 0 else 'S', f"e {m['entry']:.6g} s {m['stop']:.6g} R/A {abs(m['entry']-m['stop'])/A[m['arm']]:.2f} t4 {m['entry']+2*(m['entry']-m['stop']):.6g}", 'exit', T[m['exit']][5:] if m['exit'] is not None else None, m['res'], 'tight' if m.get('tight') else '', m.get('info'))
