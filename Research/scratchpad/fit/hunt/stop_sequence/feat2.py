import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-Bank-Loan-Report/21ed2550-acec-5cf1-bf01-a24cbf22fe18/scratchpad/fit/hunt/stop_sequence')
from feat import *
def tradeinfo(P, x):
    H, L, O = P['H'], P['L'], P['O']; d = x['dir']; R = d * (x['entry'] - x['stop'])
    mfe = 0; mae = 0
    for j in range(x['fill'], x['exit'] + 1):
        fav = (H[j] - x['entry']) if d > 0 else (x['entry'] - L[j]); adv = (x['entry'] - L[j]) if d > 0 else (H[j] - x['entry'])
        if j == x['exit'] and x['res'] < 0: fav = max(0, ((O[j] - x['entry']) if d > 0 else (x['entry'] - O[j])))
        mfe = max(mfe, fav / R); mae = max(mae, adv / R)
    hit = sum(1 for t in (0.6, 1.0, 1.5) if mfe >= t)
    gapx = int(P['daystart'][x['exit']]) if x['exit'] is not None else 0
    return dict(mfe=mfe, mae=mae, hit=hit, dur=x['exit'] - x['fill'], gapx=gapx)
if __name__ == '__main__':
    rows, out = table(True)
    for t, f in rows:
        if not f: continue
        s = t['sym']; P = prepare(s)
        prev = [x for x in out[s] if x['exit'] is not None and x['exit'] <= t['arm_i']]
        p = prev[-1]; ti = tradeinfo(P, p)
        f.update({'p_' + k: v for k, v in ti.items()})
        if len(prev) > 1:
            ti2 = tradeinfo(P, prev[-2]); f.update({'p2_' + k: v for k, v in ti2.items()})
    res, n = sep(rows)
    seen = set()
    for r in res:
        if r[2] in seen: continue
        seen.add(r[2]); print(r)
        if len(seen) > 12: break
    for t, f in rows:
        if f and (t['tight'] or (t['sym'] in ('SENSEX','NIFTY'))):
            print(t['sym'], t['fill'], 'T' if t['tight'] else ' ', {k: round(v, 2) for k, v in f.items() if k.startswith('p_') or k.startswith('p2_')})
