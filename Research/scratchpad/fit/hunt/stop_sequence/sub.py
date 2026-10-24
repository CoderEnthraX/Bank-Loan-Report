import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from pfeat import *
if __name__ == '__main__':
  rows = [(t, pf(t)) for t in TRADES]
  sub = [(t, f) for t, f in rows if f['sameSigDay'] == 0]
  print(len(sub), sum(t['tight'] for t, _ in sub))
def search(rs, top=25):
    y = [t['tight'] for t, _ in rs]; res = []
    for k in rs[0][1]:
        vals = sorted({f[k] for _, f in rs})
        for th in vals:
            for sgn in (1, -1):
                p = [sgn * f[k] >= sgn * th for _, f in rs]
                tp = sum(a and b for a, b in zip(p, y)); fp = sum(a and not b for a, b in zip(p, y))
                res.append((sum(y) - tp + fp, fp, k, '>=' if sgn > 0 else '<=', round(th, 3), tp))
    res.sort(); seen = set(); out = []
    for r in res:
        if r[2] in seen: continue
        seen.add(r[2]); out.append(r)
    return out[:top]
if __name__ == '__main__':
  for r in search(sub): print(r)
  print('--- all 80')
  for r in search(rows, 12): print(r)
