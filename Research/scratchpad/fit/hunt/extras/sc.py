import sys, json; sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/extras')
import pf
BASE_OK = None
inp = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
r0, rows0 = pf.score({}, True); ok0 = {x[1:4] for x in rows0 if x[0] == 'ok'}
r, rows = pf.score(inp, True); ok = {x[1:4] for x in rows if x[0] == 'ok'}
print(inp, {k: r[k] for k in ('exact', 'miss', 'extra', 'near')}, 'lost:', sorted(ok0 - ok), 'gained:', sorted(ok - ok0))
print('  non-ok:', [' '.join(x[:4]) for x in rows if x[0] != 'ok'])
