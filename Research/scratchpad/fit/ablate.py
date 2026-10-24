import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt, score
def diffrows(a, b):
    sa = {(x[1], x[2], x[0]) for x in a}; sb = {(x[1], x[2], x[0]) for x in b}
    return sorted(sa - sb), sorted(sb - sa)
if __name__ == '__main__':
    tr, win = load_gt(os.path.join(os.path.dirname(__file__), '..', 'gt', 'final'))
    best = json.loads(sys.argv[1]); alt = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    rb, rowsb = score(best, tr, win, detail=True)
    print('BEST', rb)
    tests = [alt] if alt else [dict(best, **{k: v}) for k, v in [('vwap', 'close'), ('closePct', 30), ('bodyPct', 60), ('maxDayR', 0), ('brkLen', 6), ('roundLevels', True)]]
    for cfg in tests:
        r, rows = score(cfg, tr, win, detail=True)
        gone, new = diffrows(rowsb, rows)
        ch = {k: v for k, v in cfg.items() if best.get(k) != v}
        print(f'\nCHANGE {ch}: {r}')
        print('  only in BEST :', [g for g in gone if g[2] != 'ok' or True][:14])
        print('  only in ALT  :', new[:14])
