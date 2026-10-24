import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit')
import engine
from engine import run, tr_series, day_starts, MINTICK
from arp_data import load
mode = sys.argv[1] if len(sys.argv)>1 else 'none'
def prep(sym, mode):
    rows = load(sym); mt = MINTICK[sym]
    if mode != 'none':
        for r in rows:
            for k in ('o','h','l','c'):
                n = round(r[k]/mt)
                if mode == 'mul': r[k] = n*mt
                elif mode == 'div': r[k] = n/round(1/mt)
    return dict(sym=sym, rows=rows, mt=mt, tr=tr_series(rows), daystart=day_starts(rows))
for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P = prep(sym, mode); rows = P['rows']
    tr = run(P)
    mine = {(t['fill'], t['dir']) for t in tr}
    csv = {(r['i'], 1 if r['lf'] else -1) for r in rows if r['lf'] or r['sf']}
    skip = 1500
    a = {x for x in mine if x[0] >= skip}; b = {x for x in csv if x[0] >= skip}
    print(f"{mode} {sym:7s} port={len(a)} csv={len(b)} both={len(a&b)} only_port={len(a-b)} only_csv={len(b-a)}", sorted(a^b)[:4])
