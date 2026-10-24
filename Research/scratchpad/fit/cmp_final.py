import sys, os, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pine_final import run
from engine2 import prepare, run as run2
from engine import rma
spec = importlib.util.spec_from_file_location('r', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hunt/stop_sequence/rule_firstday_prevday.py')); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
cfg = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1,"stopFn":m.stop_fn}
for sym in ['GC','EURUSD','NASDAQ','US30','CRUDE','NIFTY','SENSEX','ETH']:
    P = prepare(sym)
    if ('atr', 14) not in P: P[('atr', 14)] = rma(P['tr'], 14)
    a = [(t['fill'], t['dir'], t['exit'], round(t['entry'], 6), round(t['stop'], 6)) for t in run(sym, {"eps": False})]
    b = [(t['fill'], t['dir'], t['exit'], round(t['entry'], 6), round(t['stop'], 6)) for t in run2(P, cfg)]
    sa, sb = set(a), set(b)
    T = P['T']
    print(f"{sym:7s} pine={len(a)} engine2+rule={len(b)} same={len(sa & sb)} diff={[ (T[x[0]], x[1], x[4]) for x in sorted(sa ^ sb)[:4]]}")
