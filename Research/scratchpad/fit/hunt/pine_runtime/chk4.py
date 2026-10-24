import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/pine_runtime')
from rt import run
from engine import rtick
tr, ev, P = run('CRUDE'); mt = P['mt']
for t in tr:
    if t['res'] is not None and t['res'] < 0 and t.get('best') is not None:
        d = t['dir']; lv = t['entry'] + d * 1.5 * t['risk']
        r = rtick(lv, mt)
        if d * (t['best'] - r) >= 0 and d * (t['best'] - lv) < 0:
            print(t['t'], 'dir', d, 'entry', t['entry'], 'risk', t['risk'], '1.5R level', lv, 'rounded', r, 'best', t['best'])
# entryLen > structLen: how often would the long limit sit beyond the close?
import rt
for sym in ['GC','NASDAQ','ETH']:
    tr2, ev2, P2 = run(sym, dict(structLen=3, entryLen=10)); R = P2['rows']
    beyond = sum(1 for t in tr2 if t['dir'] * (t['entry'] - R[t['arm']]['c']) > 0)
    notraded = sum(1 for t in tr2 if not (R[t['fill']]['l'] <= t['entry'] <= R[t['fill']]['h']))
    print(sym, 'structLen=3 entryLen=10: trades', len(tr2), 'limit beyond displacement close', beyond, 'fill price outside fill-bar range', notraded)
