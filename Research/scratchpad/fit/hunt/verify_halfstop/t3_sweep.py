import sys, os, importlib.util
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from own_impl import *
from gtscore import load_gt, score
from tightdata import TRADES
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
spec = importlib.util.spec_from_file_location('rule', os.path.join(FIT, 'hunt/stop_author/rule_counter_net.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
tr, win = load_gt(os.path.join(FIT, '..', 'gt', 'final'))
from engine import rma
for s in SYMS: data(s)['P'].setdefault(('atr', 14), rma(data(s)['P']['tr'], 14))
def classify(NET, wick):
    ok = 0; bad = []
    for t in TRADES:
        D = data(t['sym']); sg = impulses(D, wick=wick); net = sess_nets(D, sg); i = t['arm_i']
        tg = is_tight(D, sg, net, i, t['d'], NET); pred = stop_dist(D, i, t['d'], t['entry'], tg) / D['atr'][i] < 1.4
        if pred == t['tight']: ok += 1
        else: bad.append(f"{t['sym']} {t['fill'][5:]} {'FN' if t['tight'] else 'FP'}")
    return ok, bad
print('NET WICK | classif(own) | FULL engine(module) exact/miss/extra')
for wick in (True, False):
    for NET in range(1, 8):
        ok, bad = classify(NET, wick)
        mod.NET = NET; mod.WICK = wick
        cfg = dict(BEST); cfg['stopFn'] = mod.stop_fn
        r = score(cfg, tr, [dict(w) for w in win])
        print(NET, 'wick' if wick else 'close', '|', f'{ok}/80', bad, '|', f"{r['exact']}/{r['miss']}/{r['extra']}")
