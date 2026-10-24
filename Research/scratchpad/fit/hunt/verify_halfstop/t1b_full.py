import sys, os, importlib.util
H = os.path.dirname(os.path.abspath(__file__)); FIT = os.path.abspath(os.path.join(H, '..', '..'))
sys.path.insert(0, H); sys.path.insert(0, FIT)
from own_impl import *
from gtscore import load_gt, score
from engine import rma
BEST = {"brkLen":10,"entryLen":6,"bodyPct":55,"closePct":25,"maxDayR":3,"vsLag":3,"noSunUTC":1,"momMin":0.85,"roundLevels":False,"rearm":"samedir","minBars":1}
spec = importlib.util.spec_from_file_location('rule', os.path.join(FIT, 'hunt/stop_author/rule_counter_net.py')); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
# signal equality
tot = 0
for s in SYMS:
    D = data(s); D['P'].setdefault(('atr', 14), rma(D['P']['tr'], 14)); sg = impulses(D); ref = mod._sig(D['P'])
    diff = int((sg != np.array(ref)).sum()); tot += diff
    print(s, 'n_imp', int((sg != 0).sum()), 'diff vs module', diff)
print('total signal diffs', tot)
# own stop_fn into the engine
def own_stop(P, i, d, entry, stop, A, ctx):
    D = data(P['sym']); sg = impulses(D) if ('s', P['sym']) not in own_stop.__dict__ else own_stop.__dict__[('s', P['sym'])]
    own_stop.__dict__[('s', P['sym'])] = sg
    net = sess_nets(D, sg)
    tg = is_tight(D, sg, net, i, d)
    return entry - d * stop_dist(D, i, d, entry, tg)
tr, win = load_gt(os.path.join(FIT, '..', 'gt', 'final'))
for name, fn in [('own', own_stop), ('module', mod.stop_fn), ('baseline(no rule)', None)]:
    cfg = dict(BEST)
    if fn: cfg['stopFn'] = fn
    r = score(cfg, tr, [dict(w) for w in win])
    print(name, {k: r[k] for k in ('exact', 'near', 'miss', 'extra')})
