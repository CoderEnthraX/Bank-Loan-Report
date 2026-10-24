"""Coordinate-descent search of rule options against the original's trades."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt, score
SPACE = dict(
    brkLen=[6, 8, 9, 10, 11, 12, 15, 20], entryLen=[6, 8, 10, 12, 15, 20], retest=[3, 4, 5, 6, 8, 10],
    dispAtr=[0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], bodyPct=[0, 40, 50, 55, 60, 65, 70], closePct=[20, 25, 30, 35, 40, 50, 100],
    bodyAtr=[0.0, 0.3, 0.4, 0.5, 0.6, 0.7], brkMin=[0.0, 0.02, 0.05, 0.1], cooldown=[0, 1, 2, 3, 4, 5],
    coolWin=[None, 0, 2, 3, 4, 5, 6], coolLoss=[None, 0, 1, 2, 3, 4], rearm=['replace', 'samedir', 'ignore'], rearmBetter=[False, True],
    maxLossDay=[0, 2, 3], consecLoss=[0, 2, 3], maxDayR=[0, 2, 3], minBars=[0, 1, 2, 3, 4, 6], vwap=['close', 'open', 'none'],
    armOnExitBar=[False, True], vsLag=[0, 2, 3, 4], vsMin=[0.0, 0.01, 0.02, 0.05], zMin=[0, 0.2, 0.3, 0.4, 0.5], momMin=[0, 0.5, 0.7, 0.8, 0.85, 0.9, 1.0], momN=[8, 10, 12], noSunUTC=[0, 1])
def obj(r): return 3 * r['exact'] + 1 * r['near'] - 2 * r['miss'] - 2 * r['extra'] - 0.5 * r['entry_err']
def search(start, tr, win, rounds=3, verbose=True):
    cur = dict(start); best = score(cur, tr, win); bo = obj(best)
    for rd in range(rounds):
        improved = False
        for k, vals in SPACE.items():
            for v in vals:
                if cur.get(k, None) == v: continue
                cfg = dict(cur); cfg[k] = v
                r = score(cfg, tr, win); o = obj(r)
                if o > bo + 1e-9:
                    bo, best, cur = o, r, cfg; improved = True
                    if verbose: print(f'  r{rd} {k}={v!r:8} obj {o:6.1f} {r}', flush=True)
        if not improved: break
    return cur, best
if __name__ == '__main__':
    tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
    print(len(tr), 'trades', len(win), 'windows')
    t0 = time.time(); start = json.loads(sys.argv[1]) if len(sys.argv) > 1 else dict(brkLen=10, roundLevels=False)
    r = score(start, tr, win); print('start', obj(r), r, f'{time.time()-t0:.2f}s/eval')
    cur, best = search(start, tr, win)
    print('BEST', json.dumps(cur), best)
