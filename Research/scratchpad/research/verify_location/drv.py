import sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research')
import lib
from multiprocessing import Pool
MP='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/research/verify_location/combo_v.py'
def ev(o):
    tr=lib.run_all(MP,o); a,b=lib.split(tr)
    out=dict(opts=o, ALL=lib.stats(tr), TRAIN=lib.stats(a), TEST=lib.stats(b),
      sym={s:lib.stats([x for x in tr if x['sym']==s]) for s in lib.SYMS},
      tr=[(x['sym'],x['fill'],x['t'],x['res'],x['hit1'],x['hit15']) for x in tr])
    return out
def pmap(opts, procs=4):
    with Pool(procs) as p: return p.map(ev, opts)
