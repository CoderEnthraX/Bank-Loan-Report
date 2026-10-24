import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt, score
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
cfg = json.loads(sys.argv[1]); det = len(sys.argv) > 2
r, rows = score(cfg, tr, [dict(w) for w in win], detail=True); print(r)
if det: [print(' ', *x) for x in rows if x[0] != 'ok']
