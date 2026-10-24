import sys
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pfeat import *
from nearsig import conds
from sub import search
VAR = {'E1': None, 'E2': ('dir','rng','body','clos','brk','vw','mom','vsl'), 'E3': ('dir','rng','body','clos','brk','vw','vsl'),
       'E4': ('dir','rng','body','clos','brk','vw'), 'E5': ('dir','rng','body','clos','brk'), 'E6': ('dir','rng','body','clos','brk','vw','mom')}
for name, need in VAR.items():
    rows = []
    for t in TRADES:
        P = prepare(t['sym']); i = t['arm_i']; d = t['d']; ds = i - P['sinceStart'][i]; f = pf(t)
        if need is None: first = f['sameSigDay'] == 0
        else:
            first = True
            for j in range(ds, i):
                r = conds(P, j, d)
                if r and all(r[k] for k in need): first = False; break
        rows.append((t, f, first))
    tp = sum(1 for t, f, x in rows if x and t['tight']); fp = sum(1 for t, f, x in rows if x and not t['tight'])
    print(name, need, 'tight kept', tp, 'normal kept', fp, 'FPs:', [f"{t['sym']} {t['fill'][5:]}" for t, f, x in rows if x and not t['tight']])
    sub = [(t, f) for t, f, x in rows if x]
    for r in search(sub, 5): print('    ', r)
