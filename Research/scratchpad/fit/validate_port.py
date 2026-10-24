import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import prepare, run
for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P = prepare(sym); rows = P['rows']
    tr = run(P)
    mine = {(t['fill'], t['dir']) for t in tr}
    csv = {(r['i'], 1 if r['lf'] else -1) for r in rows if r['lf'] or r['sf']}
    skip = 1500  # warm-up: the exported indicator had more history
    a = {x for x in mine if x[0] >= skip}; b = {x for x in csv if x[0] >= skip}
    print(f"{sym:7s} mintick={P['mt']:<8g} days={sum(P['daystart'])} port={len(a)} csv={len(b)} both={len(a&b)} only_port={len(a-b)} only_csv={len(b-a)}",
          ' first diffs:', sorted(list((a ^ b)))[:4])
