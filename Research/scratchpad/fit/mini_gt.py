import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine2 import prepare, run
# provisional ground truth (exact or near-exact) and the windows it fully covers
GT = {('GC','2026-10-09 03:30','2026-10-10 02:25'): ['L04:40','L07:30','L11:20','S18:25','L20:55'],
      ('GC','2026-10-12 03:30','2026-10-12 13:00'): ['L05:55','S10:35'],
      ('EURUSD','2026-10-09 03:30','2026-10-09 19:00'): ['L05:45','L07:05','L12:55','S15:30','S17:40'],
      ('NASDAQ','2026-10-12 03:30','2026-10-12 13:00'): ['S06:20','S11:15'],
      ('SENSEX','2026-10-12 09:15','2026-10-12 13:00'): ['S09:40','S11:20']}
def score(cfg, verbose=False):
    tot = dict(hit=0, miss=0, extra=0)
    for (sym, a, b), want in GT.items():
        P = prepare(sym); T = P['T']
        got = [('L' if t['dir'] > 0 else 'S') + T[t['fill']][11:] for t in run(P, cfg) if a <= T[t['fill']] <= b]
        h = len(set(got) & set(want)); tot['hit'] += h; tot['miss'] += len(want) - h; tot['extra'] += len(set(got) - set(want))
        if verbose: print(f"  {sym} {a[:10]}  got {got}  want {want}")
    return tot
if __name__ == '__main__':
    for cfg in [{}, dict(brkLen=10), dict(brkLen=10, rearm='ignore'), dict(brkLen=10, minBars=1), dict(brkLen=10, rearm='ignore', minBars=1)]:
        print(cfg, score(cfg, verbose=True))
