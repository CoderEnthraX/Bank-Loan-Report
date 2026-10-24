import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt, covered
from engine2 import prepare, run
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
cfg = json.loads(sys.argv[1]); sym = sys.argv[2]; a = sys.argv[3] if len(sys.argv) > 3 else ''; b = sys.argv[4] if len(sys.argv) > 4 else 'z'
P = prepare(sym); T = P['T']
ev = []
for t in tr:
    if t['sym'] == sym and a <= t['fill'] <= b: ev.append((t['fill'], 'ORIG', 'L' if t['d'] > 0 else 'S', t['entry'], t['stop'], t['exit'], t['out']))
for m in run(P, cfg):
    tf = T[m['fill']]
    if a <= tf <= b and covered(win, sym, tf): ev.append((tf, 'mine', 'L' if m['dir'] > 0 else 'S', round(m['entry'], 5), round(m['stop'], 5), T[m['exit']] if m['exit'] is not None else None, m['res']))
for e in sorted(ev): print(*e)
