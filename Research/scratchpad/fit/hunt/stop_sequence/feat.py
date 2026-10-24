"""Sequence features at every GT trade arm (oracle-tight full-engine history)."""
import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from rec import *
def feats(P, i, d, snap, arms):
    A = P[('atr',14)]; T = P['T']
    tr = snap['trades']; f = {}
    def tg(x): return x['dir']*(x['entry']-x['stop'])/A[x['arm']] < 1.4
    R = [x['res'] for x in tr]
    for N in range(1, 13):
        f[f'sumR{N}'] = sum(R[-N:]); f[f'wins{N}'] = sum(1 for r in R[-N:] if r > 0)
    cum = 0; peak = 0; eq = [0]
    for r in R: cum += r; peak = max(peak, cum); eq.append(cum)
    f['cumR'] = cum; f['dd'] = peak - cum; f['n'] = len(R); f['winpct'] = (sum(1 for r in R if r > 0) / len(R)) if R else 0
    for N in (3, 5, 10, 20):
        m = sum(eq[-N:]) / len(eq[-N:]); f[f'eqMA{N}'] = cum - m
    ls = 0
    for r in reversed(R):
        if r < 0: ls += 1
        else: break
    ws = 0
    for r in reversed(R):
        if r > 0: ws += 1
        else: break
    f['lstreak'] = ls; f['wstreak'] = ws
    f['dayFills'] = snap['dayFills']; f['dayR'] = snap['dayR']; f['dayLoss'] = snap['dayLoss']
    f['gap'] = (i - snap['lastExit']) if snap['lastExit'] is not None else 9999
    p = tr[-1] if tr else None
    f['prevTight'] = int(tg(p)) if p else 0
    f['prevSame'] = int(p['dir'] == d) if p else 0
    f['prevRes'] = p['res'] if p else 0
    f['sinceFill'] = (i - p['fill']) if p else 9999
    # same-direction consecutive trades before
    k = 0
    for x in reversed(tr):
        if x['dir'] == d: k += 1
        else: break
    f['sameRun'] = k
    # arms: list of (i, d, filled_bool) for this sym before i
    lastx = snap['lastExit'] if snap['lastExit'] is not None else -1
    lastf = p['fill'] if p else -1
    prior = [a for a in arms if a[0] < i]
    f['cancSinceExit'] = sum(1 for a in prior if a[0] > lastx and not a[2])
    f['armsSinceExit'] = sum(1 for a in prior if a[0] > lastx)
    f['cancSameSinceExit'] = sum(1 for a in prior if a[0] > lastx and not a[2] and a[1] == d)
    ds = i - P['sinceStart'][i]
    f['armsToday'] = sum(1 for a in prior if a[0] >= ds)
    f['cancToday'] = sum(1 for a in prior if a[0] >= ds and not a[2])
    f['cancN20'] = sum(1 for a in prior if a[0] >= i - 20 and not a[2])
    f['prevArmFilled'] = int(prior[-1][2]) if prior else 1
    f['prevArmSame'] = int(prior[-1][1] == d) if prior else 0
    f['barsPrevArm'] = (i - prior[-1][0]) if prior else 9999
    f['st'] = snap['st']
    f['replacing'] = int(snap['st'] != 0)
    # trades in last N bars
    for B in (12, 24, 48, 96, 288):
        f[f'tr{B}'] = sum(1 for x in tr if x['fill'] >= i - B)
    return f
def table(oracle=True):
    out = runall(oracle); rows = []
    ARMS = {}
    for s in out:
        filled = {t['arm'] for t in out[s]}
        ARMS[s] = [(a[0], a[1], a[0] in filled) for a in REC[s]]
    for t in TRADES:
        s = t['sym']; P = prepare(s)
        recs = [r for r in REC[s] if r[0] == t['arm_i'] and r[1] == t['d']]
        if not recs: rows.append((t, None)); continue
        rows.append((t, feats(P, t['arm_i'], t['d'], recs[-1][2], ARMS[s])))
    return rows, out
def sep(rows):
    rows = [(t, f) for t, f in rows if f]
    keys = rows[0][1].keys(); res = []
    for k in keys:
        vals = sorted({f[k] for _, f in rows})
        for th in vals:
            for sgn in (1, -1):
                pred = [(sgn * f[k] >= sgn * th) for _, f in rows]
                err = sum(p != t['tight'] for p, (t, _) in zip(pred, rows))
                fn = sum((not p) and t['tight'] for p, (t, _) in zip(pred, rows))
                res.append((err, fn, k, ('>=' if sgn > 0 else '<='), th))
    res.sort(key=lambda x: x[:2])
    return res, len(rows)
if __name__ == '__main__':
    rows, _ = table(True)
    res, n = sep(rows)
    print('rows with features', n)
    seen = set()
    for r in res:
        if r[2] in seen: continue
        seen.add(r[2]); print(r)
        if len(seen) > 30: break
