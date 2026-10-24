import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from forced import evaluate
from gtscore import load_gt
SPACE = dict(
    brkLen=[8, 9, 10, 11, 12, 15], entryLen=[5, 6, 7, 8, 10], retest=[3, 4, 5, 6, 8, 10, 12],
    dispAtr=[0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], bodyPct=[0, 40, 45, 50, 55, 60, 65, 70], closePct=[15, 20, 22, 25, 30, 35, 40, 100],
    bodyAtr=[0.0, 0.3, 0.4, 0.5, 0.55, 0.6, 0.7], brkMin=[0.0, 0.02, 0.05, 0.1], cooldown=[0, 1, 2, 3, 4, 5, 6],
    coolWin=[None, 0, 2, 3, 4, 5, 6, 8], coolLoss=[None, 0, 1, 2, 3, 4], rearm=['replace', 'samedir', 'ignore'], rearmBetter=[False, True],
    maxLossDay=[0, 2, 3], maxDayR=[0, 2, 3], minBars=[0, 1, 2, 3, 4, 6], vwap=['close', 'open', 'mid', 'none'], zMin=[0, 0.25, 0.4, 0.45, 0.5, 0.55, 0.6, 0.75],
    diAlign=[False, True], reTP=[False, True], sameDirLoss=[0, 2, 3], vsLag=[0, 2, 3, 4], vsMin=[0.0, 0.01, 0.02, 0.05])
def search(start, tr, win, rounds=4):
    cur = dict(start); best = evaluate(cur, tr, win); print('start', best, flush=True)
    for rd in range(rounds):
        imp = False
        for k, vals in SPACE.items():
            for v in vals:
                if cur.get(k, '__') == v: continue
                cfg = dict(cur); cfg[k] = v; r = evaluate(cfg, tr, win)
                if r['obj'] > best['obj'] + 1e-9:
                    best, cur, imp = r, cfg, True; print(f'  r{rd} {k}={v!r} {r}', flush=True)
        if not imp: break
    return cur, best
if __name__ == '__main__':
    tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
    start = json.loads(sys.argv[1]) if len(sys.argv) > 1 else dict(brkLen=10)
    cur, best = search(start, tr, win)
    print('BEST', json.dumps(cur), best)
