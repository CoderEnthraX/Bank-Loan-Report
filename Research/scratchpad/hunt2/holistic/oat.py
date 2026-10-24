"""One-at-a-time: every grid value vs a base config; prints gains (fixed bad items) and losses (new bad items)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ev import ev, fmt
from grid import GRID
import m as M
base = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
b = ev(base); print('BASE', json.dumps(base), fmt(b))
for k, vals in GRID.items():
    for v in vals:
        if v == base.get(k, M.IN[k]): continue
        c = dict(base); c[k] = v; r = ev(c)
        g = sorted(b['bad'] - r['bad']); l = sorted(r['bad'] - b['bad'])
        if g or l: print(f"{k}={v}: {fmt(r)} d{r['obj']-b['obj']:+d} | GAIN {g} | LOSE {l}", flush=True)
