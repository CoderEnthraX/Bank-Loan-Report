"""Diff the model trade lists of two option sets for all symbols (tight flags, presence)."""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/hunt7/stops')
import combo_f as M
from engine2 import prepare
BASE = {"slopeCross":True,"minOpenBars":0,"cooldownBars":1,"dayStopR":0,"tightOut":True,"erMin":0.2}
a = dict(BASE, **json.loads(sys.argv[1])); b = dict(BASE, **json.loads(sys.argv[2]))
lo = sys.argv[3] if len(sys.argv) > 3 else '2026-09-01'
for sym in ('CRUDE','SENSEX','NIFTY','NSE_NIFTY1','MCX_NATURALGAS','GC','EURUSD','NASDAQ','US30','ETH'):
    P = prepare(sym); T = P['T']
    ta = {(t['fill'], t['dir']): t for t in M.run(sym, a)}; tb = {(t['fill'], t['dir']): t for t in M.run(sym, b)}
    for k in sorted(set(ta) | set(tb)):
        x, y = ta.get(k), tb.get(k)
        if T[k[0]] < lo: continue
        if x and y and x['tight'] == y['tight'] and x['res'] == y['res']: continue
        def s(t):
            if not t: return '-'
            F = t['feat']; pn = F['prevNet'] or 0
            return f"{'T' if t['tight'] else 'n'} res{t['res']} pn{t['dir']*pn:+d} cur{t['dir']*(F['bullN']-F['bearN']):+d} same{F['bullN'] if t['dir']>0 else F['bearN']}"
        print(sym, T[k[0]], 'L' if k[1] > 0 else 'S', '|', s(x), '|', s(y))
