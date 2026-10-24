import sys, datetime as dt
sys.path.insert(0, D := '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
rows, out = table(True)
def wk(P, i):
    ds = i - P['sinceStart'][i]; return dt.datetime.strptime(P['T'][ds][:10], '%Y-%m-%d').isocalendar()[:2]
for t, f in rows:
    if not f: continue
    s = t['sym']; P = prepare(s); i = t['arm_i']; w = wk(P, i)
    cl = [x for x in out[s] if x['exit'] is not None and x['exit'] <= i]
    wtr = [x for x in cl if wk(P, x['exit']) == w]
    f['weekR'] = sum(x['res'] for x in wtr); f['weekN'] = len(wtr); f['weekL'] = sum(1 for x in wtr if x['res'] < 0); f['weekW'] = f['weekN'] - f['weekL']
    days = sorted({P['T'][x['exit']][:10] for x in cl})
    f['dow'] = dt.datetime.strptime(P['T'][i][:10], '%Y-%m-%d').weekday()
    # previous day R
    ds = i - P['sinceStart'][i]; pds = ds - 1 - P['sinceStart'][ds - 1]
    f['prevDayR'] = sum(x['res'] for x in cl if pds <= x['exit'] < ds); f['prevDayN'] = sum(1 for x in cl if pds <= x['exit'] < ds)
res, n = sep(rows)
seen = set()
for r in res:
    if r[2] in seen: continue
    seen.add(r[2]); print(r)
    if len(seen) > 10: break
for t, f in rows:
    if f and (t['tight'] or t['sym'] in ('NIFTY', 'SENSEX')): print(t['sym'], t['fill'], 'T' if t['tight'] else ' ', {k: f[k] for k in ('weekR', 'weekN', 'weekL', 'dow', 'prevDayR', 'prevDayN')})
