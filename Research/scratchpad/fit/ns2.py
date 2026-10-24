import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gtscore import load_gt, score
tr, win = load_gt(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'gt', 'final'))
cfg = json.loads(sys.argv[1])
cfg['tightSet'] = {('CRUDE','2026-10-09 10:25'),('EURUSD','2026-10-09 15:25'),('GC','2026-10-07 05:55'),('GC','2026-10-08 04:45'),('GC','2026-10-09 18:20'),('NASDAQ','2026-10-09 06:00'),('NIFTY','2026-10-05 09:25'),('NIFTY','2026-10-09 10:05')}
r, rows = score(cfg, tr, [dict(w) for w in win], detail=True); print(r)
[print(' ', *x) for x in rows if x[0] != 'ok']
