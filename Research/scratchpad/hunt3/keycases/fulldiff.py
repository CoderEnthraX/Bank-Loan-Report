"""full-data trade diff between two option sets: python3 -I fulldiff.py '{base}' '{new}'"""
import sys, json, importlib.util
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
from engine2 import prepare
spec = importlib.util.spec_from_file_location('m', '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt3/keycases/kc.py'); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
a, b = json.loads(sys.argv[1]), json.loads(sys.argv[2])
for s in ('CRUDE','ETH','EURUSD','GC','NASDAQ','NIFTY','SENSEX','US30'):
    T = prepare(s)['T']
    k = lambda m: (T[m['fill']], m['dir'], round(m['entry'], 4), round(m['stop'], 4), m['res'])
    A = set(map(k, M.run(s, a))); B = set(map(k, M.run(s, b)))
    print(s, 'base', len(A), 'new', len(B), 'sumR base %.1f new %.1f' % (sum(x[4] or 0 for x in A), sum(x[4] or 0 for x in B)))
    for x in sorted(A - B): print('   - ', *x)
    for x in sorted(B - A): print('   + ', *x)
