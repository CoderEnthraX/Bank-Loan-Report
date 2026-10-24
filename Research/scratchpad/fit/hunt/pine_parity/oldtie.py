import sys, math; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import engine
from engine import prepare, run
EPS = float(sys.argv[1]); RT = sys.argv[2] if len(sys.argv) > 2 else 'old'
if RT == 'dec':
    engine.rtick = lambda x, mt: math.floor(x / mt + 0.5) / round(1 / mt) if mt < 1 else math.floor(x / mt + 0.5) * mt
if RT == 'scale':
    engine.rtick = lambda x, mt: math.floor(x * round(1 / mt) + 0.5) / round(1 / mt) if mt < 1 else math.floor(x / mt + 0.5) * mt
if RT == 'half':  # x/mt with a tiny relative nudge, then half away from zero
    engine.rtick = lambda x, mt: math.floor(x / mt * (1 + 1e-12) + 0.5) / round(1 / mt) if mt < 1 else math.floor(x / mt + 0.5) * mt
def disp(P, i, c, atr, bull, bear, ph, pl):
    r = P['rows'][i]; rng = r['h'] - r['l']
    if rng <= 0: return False, False
    body = abs(r['c'] - r['o']); vw = r['vwap']
    big = rng >= c['dispAtr'] * atr[i] and body / rng * 100 >= c['bodyPct'] - EPS
    b1 = r['c'] > r['o'] and r['c'] > ph and big and (r['h'] - r['c']) / rng * 100 <= c['closePct'] + EPS and r['c'] > vw
    b2 = r['c'] < r['o'] and r['c'] < pl and big and (r['c'] - r['l']) / rng * 100 <= c['closePct'] + EPS and r['c'] < vw
    return b1, b2
for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P = prepare(sym); rows = P['rows']
    tr = run(P, hooks={'disp': disp})
    mine = {(t['fill'], t['dir']) for t in tr}
    csv = {(r['i'], 1 if r['lf'] else -1) for r in rows if r['lf'] or r['sf']}
    a = {x for x in mine if x[0] >= 1500}; b = {x for x in csv if x[0] >= 1500}
    print(f"eps={EPS} rt={RT} {sym:7s} both={len(a&b)} only_port={len(a-b)} only_csv={len(b-a)}", [(rows[x[0]]['t'], x[1]) for x in sorted(a ^ b)[:6]])
