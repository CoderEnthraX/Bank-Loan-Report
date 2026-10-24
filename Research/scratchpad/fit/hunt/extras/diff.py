import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/extras')
import pf
from engine import prepare
inp = json.loads(sys.argv[1])
for s in ('CRUDE','ETH','EURUSD','GC','NASDAQ','NIFTY','SENSEX','US30'):
    T = [r['t'] for r in prepare(s)['rows']]
    a = {(T[m['fill']], m['dir'], round(m['entry'],4), round(m['stop'],4)) for m in pf.run(s, {})}
    b = {(T[m['fill']], m['dir'], round(m['entry'],4), round(m['stop'],4)) for m in pf.run(s, inp)}
    print(s, 'base', len(a), 'new', len(b), 'removed', sorted(a-b), 'added', sorted(b-a))
r0, _ = pf.score({}, True); r1, _ = pf.score(inp, True)
print('entry_err/stop_err base %.3f/%.3f new %.3f/%.3f' % (r0['entry_err'], r0['stop_err'], r1['entry_err'], r1['stop_err']))
