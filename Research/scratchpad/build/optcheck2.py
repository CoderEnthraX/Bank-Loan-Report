"""v3.1 options in ref.py vs the research modules they came from (shown trades, every instrument)."""
import sys, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/build'); import ref
def mod(p):
    spec = importlib.util.spec_from_file_location(p.replace('/', '_'), S + '/' + p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
SY = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
key = lambda x: (x['dir'], x['arm'], x['fill'], x['exit'], round(x['entry'], 6), round(x['stop'], 6), round(x['res'], 6) if x['res'] is not None else None)
cases = [
  ('halfCap vs halfstop3/r3.py', 'halfstop3/r3.py', 'shown', {"halfCap": True}, {"halfCap": True}),
  ('chop 11.8 vs research/chop ghost xR2', 'research/chop/ref_chop.py', 'shown', {"chopRules": [["xR2", "le", 11.8]], "chopMode": "ghost"}, {"chopOn": True, "chopMax": 11.8}),
  ('chop 9.73 vs research/chop ghost xR2', 'research/chop/ref_chop.py', 'shown', {"chopRules": [["xR2", "le", 9.73]], "chopMode": "ghost"}, {"chopOn": True, "chopMax": 9.73}),
  ('ema 1.65 vs research/ema h6s ghost', 'research/ema/ref_ema.py', 'shown', {"emaGate": [["h6s_asl_E20_3", "le", 1.65]], "emaGhost": True}, {"emaOn": True, "emaMax": 1.65}),
  ('ema 2.0 vs research/ema h6s ghost', 'research/ema/ref_ema.py', 'shown', {"emaGate": [["h6s_asl_E20_3", "le", 2.0]], "emaGhost": True}, {"emaOn": True, "emaMax": 2.0}),
]
for name, path, fn, ro, eo in cases:
    M = mod(path); diff = 0; tot = 0; nd = 0
    for s in SY:
        a = [key(x) for x in getattr(M, fn)(s, ro)]
        b = [key(x) for x in ref.shown(s, eo)]
        tot += len(b)
        if a != b:
            diff += 1; sa, sb = set(a), set(b); nd += len(sa ^ sb)
            print('   ', s, 'research', len(a), 'ref', len(b), 'only research', sorted(sa - sb)[:3], 'only ref', sorted(sb - sa)[:3])
    print(f'{name:40s} trades {tot:5d}  instruments differing: {diff}  differing trades: {nd}')
