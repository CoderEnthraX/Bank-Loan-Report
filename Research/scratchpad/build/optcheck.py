import sys, importlib.util
S='/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad'
sys.path.insert(0, S + '/build'); import ref
def mod(p):
    spec = importlib.util.spec_from_file_location(p.replace('/', '_'), S + '/' + p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
SY = ['GC', 'EURUSD', 'NASDAQ', 'US30', 'CRUDE', 'NIFTY', 'SENSEX', 'ETH', 'NSE_NIFTY1', 'MCX_NATURALGAS']
key = lambda x: (x['dir'], x['arm'], x['fill'], x['exit'], round(x['entry'], 6), round(x['stop'], 6), round(x['res'], 6) if x['res'] is not None else None)
OLD = {"impBodyPct": 55.0, "brkLen": 10}   # research modules were built on the pre-impBody/brkLen engine
NEWC = {"slopeCross": True, "minOpenBars": 0, "cooldownBars": 1, "dayStopR": 0, "tightOut": True, "erMin": 0.2}
FIN = dict(NEWC, impBody=50, brkLen=6)
cases = [
  ('noChase vs research ghost z<=2.4', 'research/orderflow/combo_of.py', dict(NEWC, of_phantom=True, of_gate=[["z", "le", 2.4]]), dict(OLD, noChase=True, _skipFirstSess=True), True),
  ('lossBlock vs research skipLossDir', 'research/location/combo_loc.py', dict(NEWC, skipLossDir=1000), dict(OLD, lossBlock=True), False),
  ('BE at TP2 vs research beR=1', 'research/entry/combo_entry.py', dict(NEWC, beR=1.0), dict(OLD, mv2On=True, mv2R=0.0), False),
  ('deepOn vs final.py s2(6,2.0)', 'hunt8/final.py', dict(FIN, s2Len=6, s2Far=2.0), dict(deepOn=True), False),
  ('halfStrict vs final.py netHi rule', 'hunt8/final.py', dict(FIN, netCurMin=1, netHi=5, curOppMin=1), dict(halfStrict=True), False),
]
for name, path, ro, eo, ghost in cases:
    M = mod(path); diff = 0; tot = 0
    for s in SY:
        a = [key(x) for x in M.run(s, ro) if not x.get('phantom')]
        b = [key(x) for x in (ref.shown(s, eo))]
        tot += len(b)
        if a != b:
            diff += 1
            for k, (u, v) in enumerate(zip(a, b)):
                if u != v: print('   ', s, 'first diff', k, u, v); break
            else: print('   ', s, 'len', len(a), len(b))
    print(f'{name:40s} trades {tot:5d}  instruments differing: {diff}')
