import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import prepare, run
def show(sym, a, b, cfg=None):
    P = prepare(sym); rows = P['rows']
    for t in run(P, cfg):
        if a <= rows[t['fill']]['t'] <= b:
            print(f"  {sym:6s} {'L' if t['dir']>0 else 'S'} arm {rows[t['arm']]['t'][5:]} fill {rows[t['fill']]['t'][5:]} entry {t['entry']:.5g} stop {t['stop']:.5g} exit {rows[t['exit']]['t'][5:] if t['exit'] is not None else 'open'} {t['res']}")
if __name__ == '__main__':
    show(sys.argv[1], sys.argv[2], sys.argv[3])
